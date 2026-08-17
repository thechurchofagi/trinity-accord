#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

const ADDRESS = (process.env.CHRONICLE_ADDRESS || '0xbc63566A41cBfDB9C266a5941CBe47894DaA54A8').toLowerCase();
const OUT = process.env.CHRONICLE_OUT || 'artifacts/chronicle-sidechain-scan';
const CHAINS = {
  polygon: { id: 137, explorer: 'https://polygon.blockscout.com', rpc: process.env.POLYGON_RPC_URL || 'https://polygon.drpc.org' },
  base: { id: 8453, explorer: 'https://base.blockscout.com', rpc: process.env.BASE_RPC_URL || 'https://mainnet.base.org' },
};

const MAX_BYTES = Number(process.env.CHRONICLE_MIRROR_MAX_BYTES || 104857600);
const HTTP_TIMEOUT_MS = boundedInt(process.env.CHRONICLE_HTTP_TIMEOUT_MS, 20_000, 5_000, 120_000);
const MEDIA_TIMEOUT_MS = boundedInt(process.env.CHRONICLE_MEDIA_TIMEOUT_MS, 15_000, 5_000, 120_000);
const HTTP_RETRIES = boundedInt(process.env.CHRONICLE_HTTP_RETRIES, 2, 0, 5);
const RECOVERY_CONCURRENCY = boundedInt(process.env.CHRONICLE_RECOVERY_CONCURRENCY, 4, 1, 8);

if (!/^0x[a-f0-9]{40}$/.test(ADDRESS)) throw new Error(`invalid address ${ADDRESS}`);
if (!Number.isFinite(MAX_BYTES) || MAX_BYTES < 1) throw new Error(`invalid CHRONICLE_MIRROR_MAX_BYTES=${MAX_BYTES}`);

function boundedInt(value, fallback, min, max) {
  const n = Number(value ?? fallback);
  return Number.isInteger(n) ? Math.max(min, Math.min(max, n)) : fallback;
}

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const sha256 = buf => crypto.createHash('sha256').update(buf).digest('hex');
const safe = value => String(value).replace(/[^A-Za-z0-9._-]/g, '_').slice(0, 180);
const nowIso = () => new Date().toISOString();
const elapsedMs = start => Date.now() - start;
const redactUrl = value => String(value).replace(/([?&]apikey=)[^&]+/gi, '$1REDACTED');

function writeJson(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(value, null, 2) + '\n');
}

function cleanOutputPreserveRuntime() {
  fs.mkdirSync(OUT, { recursive: true });
  for (const entry of fs.readdirSync(OUT, { withFileTypes: true })) {
    if (entry.name === 'runtime') continue;
    fs.rmSync(path.join(OUT, entry.name), { recursive: true, force: true });
  }
}

async function requestBuffer(url, options = {}) {
  const {
    timeoutMs = HTTP_TIMEOUT_MS,
    retries = HTTP_RETRIES,
    maxBytes = 20 * 1024 * 1024,
    label = redactUrl(url),
    headers = {},
    ...fetchOptions
  } = options;
  const attempts = [];
  let lastError;

  for (let attempt = 0; attempt <= retries; attempt++) {
    const controller = new AbortController();
    const started = Date.now();
    const timer = setTimeout(() => controller.abort(new Error(`timeout after ${timeoutMs}ms`)), timeoutMs);
    try {
      const response = await fetch(url, {
        ...fetchOptions,
        signal: controller.signal,
        headers: { 'user-agent': 'trinity-accord-sidechain-mirror/1.2', ...headers },
      });
      const declared = Number(response.headers.get('content-length') || 0);
      if (declared > maxBytes) throw new Error(`content-length ${declared} exceeds max ${maxBytes}`);
      if (!response.ok) {
        const body = Buffer.from(await response.arrayBuffer());
        throw new Error(`HTTP ${response.status}: ${body.toString('utf8', 0, Math.min(body.length, 300))}`);
      }
      const buf = Buffer.from(await response.arrayBuffer());
      if (buf.length > maxBytes) throw new Error(`body ${buf.length} exceeds max ${maxBytes}`);
      clearTimeout(timer);
      attempts.push({ attempt: attempt + 1, ok: true, elapsed_ms: elapsedMs(started), status: response.status });
      return { buf, status: response.status, resolvedUrl: response.url, contentType: response.headers.get('content-type') || '', attempts };
    } catch (error) {
      clearTimeout(timer);
      lastError = error;
      const message = error?.name === 'AbortError' ? `timeout after ${timeoutMs}ms` : String(error?.message || error);
      attempts.push({ attempt: attempt + 1, ok: false, elapsed_ms: elapsedMs(started), error: message });
      console.warn(`[REQUEST RETRY] ${label} attempt=${attempt + 1}/${retries + 1} elapsed=${elapsedMs(started)}ms error=${message}`);
      if (attempt < retries) await sleep(500 * (2 ** attempt));
    }
  }

  const error = new Error(`${label}: ${lastError?.message || lastError || 'request failed'}`);
  error.attempts = attempts;
  throw error;
}

async function requestJson(url, options = {}) {
  const result = await requestBuffer(url, options);
  try {
    return { data: JSON.parse(result.buf.toString('utf8')), request: { ...result, buf: undefined } };
  } catch (error) {
    throw new Error(`${options.label || redactUrl(url)}: invalid JSON: ${error.message}`);
  }
}

function normalizeV2Transfer(chain, standard, row) {
  const config = CHAINS[chain];
  const contract = String(row?.token?.address_hash || row?.token?.address || row?.contract_address || '').toLowerCase();
  const rawTokenId = row?.total?.token_id ?? row?.token_id ?? row?.tokenID ?? row?.token?.token_id ?? row?.token?.tokenId;
  if (!/^0x[a-f0-9]{40}$/.test(contract) || rawTokenId === undefined || rawTokenId === null) return null;
  const tokenId = String(rawTokenId);
  if (!/^\d+$/.test(tokenId)) return null;
  const timestamp = typeof row.timestamp === 'string' ? row.timestamp : null;
  const timestampMs = timestamp ? Date.parse(timestamp) : NaN;
  return {
    chain, chain_id: config.id, standard, discovery_source: 'blockscout_v2',
    block_number: Number(row.block_number || 0), block_hash: row.block_hash || null,
    log_index: Number.isFinite(Number(row.log_index)) ? Number(row.log_index) : null,
    timestamp, timestamp_unix: Number.isFinite(timestampMs) ? Math.floor(timestampMs / 1000) : 0,
    transaction_hash: row.transaction_hash || row.hash || null, contract, token_id: tokenId,
    from: String(row?.from?.hash || row.from || '').toLowerCase(),
    to: String(row?.to?.hash || row.to || '').toLowerCase(), quantity: String(row?.total?.value ?? row?.value ?? '1'),
  };
}

async function historyV2(chain, standard) {
  const config = CHAINS[chain];
  const rows = [];
  let cursor = null;
  for (let page = 1; page <= 10000; page++) {
    const url = new URL(`/api/v2/addresses/${ADDRESS}/token-transfers`, config.explorer);
    url.searchParams.set('type', standard);
    if (cursor) for (const [key, value] of Object.entries(cursor)) if (value !== null && value !== undefined) url.searchParams.set(key, String(value));
    const started = Date.now();
    const { data, request } = await requestJson(url, { label: `${chain}/${standard} Blockscout v2 page ${page}`, timeoutMs: HTTP_TIMEOUT_MS, retries: HTTP_RETRIES });
    writeJson(path.join(OUT, 'discovery', `${chain}-${standard.toLowerCase()}-v2-page-${String(page).padStart(4, '0')}.json`), {
      url: url.toString(), elapsed_ms: elapsedMs(started), request, response: data,
    });
    if (!Array.isArray(data.items)) throw new Error(`${chain}/${standard} v2 returned no items array`);
    for (const row of data.items) { const normalized = normalizeV2Transfer(chain, standard, row); if (normalized) rows.push(normalized); }
    console.log(`[DISCOVERY PAGE] ${chain}/${standard} page=${page} items=${data.items.length} normalized_total=${rows.length} elapsed=${elapsedMs(started)}ms`);
    if (!data.next_page_params) break;
    cursor = data.next_page_params;
    if (page === 10000) throw new Error(`${chain}/${standard} v2 pagination safety stop`);
  }
  return rows;
}

async function historyLegacy(chain, action, standard) {
  const config = CHAINS[chain];
  const rows = [];
  for (let page = 1; ; page++) {
    const url = new URL('/api', config.explorer);
    for (const [key, value] of Object.entries({ module: 'account', action, address: ADDRESS, page, offset: 1000, sort: 'asc' })) url.searchParams.set(key, value);
    if (process.env.BLOCKSCOUT_API_KEY) url.searchParams.set('apikey', process.env.BLOCKSCOUT_API_KEY);
    const started = Date.now();
    const { data, request } = await requestJson(url, { label: `${chain}/${standard} Blockscout legacy page ${page}`, timeoutMs: HTTP_TIMEOUT_MS, retries: HTTP_RETRIES });
    const items = Array.isArray(data.result) ? data.result : [];
    writeJson(path.join(OUT, 'discovery', `${chain}-${standard.toLowerCase()}-legacy-page-${String(page).padStart(4, '0')}.json`), {
      url: redactUrl(url.toString()), elapsed_ms: elapsedMs(started), request, response: data,
    });
    if (data.status === '0' && /no transactions/i.test(`${data.message || ''} ${data.result || ''}`)) break;
    if (!Array.isArray(data.result)) throw new Error(`${chain}/${action}: ${JSON.stringify(data).slice(0, 400)}`);
    for (const row of items) {
      const contract = String(row.contractAddress || '').toLowerCase();
      const tokenId = String(row.tokenID ?? row.tokenId ?? '');
      if (!/^0x[a-f0-9]{40}$/.test(contract) || !/^\d+$/.test(tokenId)) continue;
      rows.push({
        chain, chain_id: config.id, standard, discovery_source: 'blockscout_legacy',
        block_number: Number(row.blockNumber) || 0, block_hash: row.blockHash || null,
        log_index: Number.isFinite(Number(row.logIndex)) ? Number(row.logIndex) : null,
        timestamp: row.timeStamp ? new Date(Number(row.timeStamp) * 1000).toISOString() : null,
        timestamp_unix: Number(row.timeStamp) || 0, transaction_hash: row.hash || null, contract, token_id: tokenId,
        from: String(row.from || '').toLowerCase(), to: String(row.to || '').toLowerCase(), quantity: String(row.tokenValue ?? '1'),
      });
    }
    console.log(`[DISCOVERY PAGE] ${chain}/${standard} legacy page=${page} items=${items.length} normalized_total=${rows.length} elapsed=${elapsedMs(started)}ms`);
    if (items.length < 1000) break;
    if (page > 1000) throw new Error('legacy pagination safety stop');
  }
  return rows;
}

async function history(chain, standard) {
  try { return await historyV2(chain, standard); }
  catch (v2Error) {
    console.warn(`[DISCOVERY FALLBACK] ${chain}/${standard} v2 failed: ${v2Error.message}; trying legacy`);
    const action = standard === 'ERC-1155' ? 'token1155tx' : 'tokennfttx';
    try { return await historyLegacy(chain, action, standard); }
    catch (legacyError) { throw new Error(`${chain}/${standard} discovery failed: v2=${v2Error.message}; legacy=${legacyError.message}`); }
  }
}

async function rpc(chain, method, params) {
  const started = Date.now();
  const { data, request } = await requestJson(CHAINS[chain].rpc, {
    method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ jsonrpc: '2.0', id: 1, method, params }), label: `${chain} RPC ${method}`,
    timeoutMs: HTTP_TIMEOUT_MS, retries: HTTP_RETRIES, maxBytes: 2 * 1024 * 1024,
  });
  if (data.error) throw new Error(`${chain} RPC ${method}: ${JSON.stringify(data.error)}`);
  return { result: data.result, diagnostic: { elapsed_ms: elapsedMs(started), request } };
}

const idHex = id => BigInt(id).toString(16).padStart(64, '0');
function abiString(hex) {
  try {
    const raw = hex.slice(2), offset = Number(BigInt('0x' + raw.slice(0, 64))) * 2;
    const length = Number(BigInt('0x' + raw.slice(offset, offset + 64)));
    return Buffer.from(raw.slice(offset + 64, offset + 64 + length * 2), 'hex').toString();
  } catch { return null; }
}

async function tokenURI(token) {
  const started = Date.now();
  try {
    const selector = token.standard === 'ERC-1155' ? '0x0e89341c' : '0xc87b56dd';
    const { result, diagnostic } = await rpc(token.chain, 'eth_call', [{ to: token.contract, data: selector + idHex(token.token_id) }, 'latest']);
    let uri = abiString(result);
    if (uri && token.standard === 'ERC-1155') uri = uri.replaceAll('{id}', idHex(token.token_id));
    return { uri, rpc: CHAINS[token.chain].rpc, error: null, elapsed_ms: elapsedMs(started), request: diagnostic.request };
  } catch (error) { return { uri: null, rpc: CHAINS[token.chain].rpc, error: error.message, elapsed_ms: elapsedMs(started) }; }
}

function candidates(uri) {
  if (!uri) return [];
  if (uri.startsWith('ipfs://')) {
    const suffix = uri.slice(7).replace(/^ipfs\//, '');
    return [`https://dweb.link/ipfs/${suffix}`, `https://ipfs.io/ipfs/${suffix}`];
  }
  if (uri.startsWith('ar://')) return [`https://arweave.net/${uri.slice(5)}`];
  if (/^https?:\/\//i.test(uri)) return [uri];
  return [];
}

async function mirror(uri, base, role = 'payload') {
  const started = Date.now();
  if (!uri) return { status: 'missing', role, elapsed_ms: 0 };
  if (uri.startsWith('data:')) {
    try {
      const comma = uri.indexOf(',');
      if (comma < 0) throw new Error('malformed data URI');
      const head = uri.slice(5, comma), payload = uri.slice(comma + 1);
      const buf = Buffer.from(head.includes(';base64') ? payload : decodeURIComponent(payload), head.includes(';base64') ? 'base64' : 'utf8');
      if (buf.length > MAX_BYTES) throw new Error(`data URI ${buf.length} exceeds max ${MAX_BYTES}`);
      const file = `${base}.bin`;
      fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, buf);
      return { status: 'ok', role, original_uri: uri.slice(0, 200), file, bytes: buf.length, sha256: sha256(buf), elapsed_ms: elapsedMs(started), attempts: [{ source: 'data:', ok: true }] };
    } catch (error) { return { status: 'failed', role, original_uri: uri.slice(0, 200), elapsed_ms: elapsedMs(started), errors: [error.message] }; }
  }
  const attempts = [];
  for (const candidate of candidates(uri)) {
    const candidateStart = Date.now();
    try {
      const response = await requestBuffer(candidate, { label: `${role} ${redactUrl(candidate)}`, timeoutMs: MEDIA_TIMEOUT_MS, retries: HTTP_RETRIES, maxBytes: MAX_BYTES });
      const extension = response.contentType.includes('json') ? '.json' : (path.extname(new URL(response.resolvedUrl).pathname).slice(0, 12) || '.bin');
      const file = base + extension;
      fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, response.buf);
      attempts.push({ url: redactUrl(candidate), ok: true, elapsed_ms: elapsedMs(candidateStart), request_attempts: response.attempts });
      return { status: 'ok', role, original_uri: uri, resolved_url: response.resolvedUrl, file, bytes: response.buf.length, sha256: sha256(response.buf), content_type: response.contentType, elapsed_ms: elapsedMs(started), attempts };
    } catch (error) { attempts.push({ url: redactUrl(candidate), ok: false, elapsed_ms: elapsedMs(candidateStart), error: error.message, request_attempts: error.attempts || [] }); }
  }
  return { status: 'failed', role, original_uri: uri, elapsed_ms: elapsedMs(started), errors: attempts.map(item => `${item.url}: ${item.error || 'failed'}`), attempts };
}

async function recover(token, ordinal, total) {
  const started = Date.now(), dir = path.join(OUT, token.chain, token.contract, token.token_id);
  fs.mkdirSync(dir, { recursive: true });
  const diagnostic = { schema: 'trinity-accord/chronicle-sidechain-recovery-diagnostic/v1', started_at: nowIso(), ordinal, total, chain: token.chain, contract: token.contract, token_id: token.token_id, stages: {} };
  console.log(`[RECOVER START] ${ordinal}/${total} ${token.chain} ${token.contract} #${token.token_id}`);

  const uriStart = Date.now(), uri = await tokenURI(token);
  diagnostic.stages.token_uri = { status: uri.uri ? 'ok' : (uri.error ? 'error' : 'missing'), elapsed_ms: elapsedMs(uriStart), error: uri.error || null };
  console.log(`[STAGE] ${ordinal}/${total} token_uri status=${diagnostic.stages.token_uri.status} elapsed=${diagnostic.stages.token_uri.elapsed_ms}ms`);

  const instanceStart = Date.now(), instanceUrl = `${CHAINS[token.chain].explorer}/api/v2/tokens/${token.contract}/instances/${encodeURIComponent(token.token_id)}`;
  let instance = null, instanceError = null, instanceRequest = null;
  try {
    const result = await requestJson(instanceUrl, { label: `${token.chain} Blockscout NFT instance ${token.contract}#${token.token_id}`, timeoutMs: HTTP_TIMEOUT_MS, retries: HTTP_RETRIES });
    instance = result.data; instanceRequest = result.request;
  } catch (error) { instanceError = error.message; }
  diagnostic.stages.blockscout_instance = { status: instance ? 'ok' : 'error', elapsed_ms: elapsedMs(instanceStart), error: instanceError, request: instanceRequest };
  writeJson(path.join(dir, 'blockscout-instance.json'), { url: instanceUrl, data: instance, error: instanceError, diagnostic: diagnostic.stages.blockscout_instance });
  console.log(`[STAGE] ${ordinal}/${total} blockscout_instance status=${diagnostic.stages.blockscout_instance.status} elapsed=${diagnostic.stages.blockscout_instance.elapsed_ms}ms`);

  const metadataStart = Date.now();
  let metadata = null, metadataMirror = null;
  if (uri.uri) {
    metadataMirror = await mirror(uri.uri, path.join(dir, 'metadata'), 'metadata');
    if (metadataMirror.status === 'ok') try { metadata = JSON.parse(fs.readFileSync(metadataMirror.file, 'utf8')); } catch (error) { metadataMirror.json_parse_error = error.message; }
  }
  if (!metadata && instance?.metadata) metadata = instance.metadata;
  if (metadata) writeJson(path.join(dir, 'metadata.normalized.json'), metadata);
  diagnostic.stages.metadata = {
    status: metadata ? 'ok' : (metadataMirror?.status || 'missing'), elapsed_ms: elapsedMs(metadataStart),
    source: metadataMirror?.status === 'ok' && !metadataMirror?.json_parse_error ? 'token_uri' : (instance?.metadata ? 'blockscout_instance' : null), mirror: metadataMirror,
  };
  console.log(`[STAGE] ${ordinal}/${total} metadata status=${diagnostic.stages.metadata.status} source=${diagnostic.stages.metadata.source || 'none'} elapsed=${diagnostic.stages.metadata.elapsed_ms}ms`);

  const mediaStart = Date.now(), media = [];
  for (const key of ['image', 'image_url', 'animation_url', 'animation', 'video', 'audio']) if (typeof metadata?.[key] === 'string') {
    const result = await mirror(metadata[key], path.join(dir, `media-${safe(key)}`), `media:${key}`);
    media.push({ role: key, ...result });
    console.log(`[MEDIA] ${ordinal}/${total} role=${key} status=${result.status} elapsed=${result.elapsed_ms}ms bytes=${result.bytes || 0}`);
  }
  diagnostic.stages.media = {
    status: media.every(item => item.status === 'ok') ? 'ok' : (media.some(item => item.status === 'ok') ? 'partial' : (media.length ? 'failed' : 'none')),
    elapsed_ms: elapsedMs(mediaStart), total: media.length, ok: media.filter(item => item.status === 'ok').length, failed: media.filter(item => item.status === 'failed').length,
  };
  diagnostic.completed_at = nowIso(); diagnostic.elapsed_ms = elapsedMs(started);
  writeJson(path.join(dir, 'recovery-diagnostic.json'), diagnostic);
  const record = { ...token, token_uri: uri, metadata_mirror: metadataMirror, metadata, media, recovery_diagnostic: diagnostic };
  writeJson(path.join(dir, 'record.json'), record);
  console.log(`[RECOVER DONE] ${ordinal}/${total} ${token.chain} ${token.contract} #${token.token_id} elapsed=${diagnostic.elapsed_ms}ms metadata=${metadata ? 'yes' : 'no'} media_ok=${diagnostic.stages.media.ok}/${diagnostic.stages.media.total}`);
  return record;
}

async function recoverAll(tokens) {
  const results = new Array(tokens.length);
  let nextIndex = 0, completed = 0;
  const started = Date.now(), runtimeDir = path.join(OUT, 'runtime');
  fs.mkdirSync(runtimeDir, { recursive: true });
  async function worker(workerId) {
    while (true) {
      const index = nextIndex++;
      if (index >= tokens.length) return;
      const token = tokens[index];
      try { results[index] = await recover(token, index + 1, tokens.length); }
      catch (error) {
        const failure = { ...token, recovery_error: error.message, recovery_error_at: nowIso() };
        results[index] = failure;
        const dir = path.join(OUT, token.chain, token.contract, token.token_id); fs.mkdirSync(dir, { recursive: true }); writeJson(path.join(dir, 'record.json'), failure);
        console.error(`[RECOVER ERROR] ${index + 1}/${tokens.length} worker=${workerId} ${token.chain} ${token.contract} #${token.token_id}: ${error.stack || error.message}`);
      }
      completed += 1;
      writeJson(path.join(runtimeDir, 'scanner-progress.json'), {
        timestamp: nowIso(), completed, total: tokens.length, remaining: tokens.length - completed, concurrency: RECOVERY_CONCURRENCY,
        elapsed_ms: elapsedMs(started), last_completed: { ordinal: index + 1, chain: token.chain, contract: token.contract, token_id: token.token_id, error: results[index]?.recovery_error || null },
      });
      console.log(`[PROGRESS] completed=${completed}/${tokens.length} remaining=${tokens.length - completed} worker=${workerId} elapsed=${elapsedMs(started)}ms`);
    }
  }
  await Promise.all(Array.from({ length: Math.min(RECOVERY_CONCURRENCY, tokens.length) }, (_, i) => worker(i + 1)));
  return { results, elapsed_ms: elapsedMs(started) };
}

function existingIndex() {
  try {
    const index = JSON.parse(fs.readFileSync('token_index.json', 'utf8')), set = new Set();
    for (const [contract, tokens] of Object.entries(index)) for (const id of Object.keys(tokens || {})) set.add(`${contract.toLowerCase()}|${id}`);
    return { contracts: Object.keys(index).length, tokens: set.size, set };
  } catch (error) { return { contracts: 0, tokens: 0, set: new Set(), error: error.message }; }
}

function buildManifest() {
  const manifest = [];
  function walk(dir) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const file = path.join(dir, entry.name), relative = path.relative(OUT, file).replaceAll('\\', '/');
      if (entry.isDirectory()) {
        if (relative === 'runtime') continue;
        walk(file);
      } else if (entry.name !== 'MANIFEST.sha256' && entry.name !== 'MANIFEST.sha256.json') {
        const buf = fs.readFileSync(file); manifest.push({ path: relative, bytes: buf.length, sha256: sha256(buf) });
      }
    }
  }
  walk(OUT); manifest.sort((a, b) => a.path.localeCompare(b.path)); return manifest;
}

cleanOutputPreserveRuntime();
console.log(`[CONFIG] address=${ADDRESS} concurrency=${RECOVERY_CONCURRENCY} http_timeout_ms=${HTTP_TIMEOUT_MS} media_timeout_ms=${MEDIA_TIMEOUT_MS} retries=${HTTP_RETRIES} max_bytes=${MAX_BYTES}`);

const occurrences = [];
for (const chain of Object.keys(CHAINS)) {
  console.log(`[DISCOVERY START] ${chain} ${ADDRESS}`);
  for (const standard of ['ERC-721', 'ERC-1155']) {
    const rows = await history(chain, standard); console.log(`[DISCOVERY DONE] ${chain}/${standard}: ${rows.length} historical transfer occurrences`); occurrences.push(...rows);
  }
}
const uniqueOccurrences = new Map();
for (const row of occurrences) {
  const key = [row.chain, row.transaction_hash || '', row.log_index ?? '', row.contract, row.token_id, row.from, row.to, row.quantity].join('|');
  if (!uniqueOccurrences.has(key)) uniqueOccurrences.set(key, row);
}
const deduped = [...uniqueOccurrences.values()]; deduped.sort((a, b) => a.timestamp_unix - b.timestamp_unix || a.chain.localeCompare(b.chain));
writeJson(path.join(OUT, 'transfer-occurrences.json'), deduped);

const tokenMap = new Map();
for (const row of deduped) {
  const key = `${row.chain}|${row.contract}|${row.token_id}`;
  if (!tokenMap.has(key)) tokenMap.set(key, { chain: row.chain, chain_id: row.chain_id, standard: row.standard, contract: row.contract, token_id: row.token_id, first_seen: row.timestamp, first_seen_unix: row.timestamp_unix, first_seen_block: row.block_number, transfers: [] });
  const token = tokenMap.get(key); token.transfers.push(row);
  if (row.timestamp_unix && (!token.first_seen_unix || row.timestamp_unix < token.first_seen_unix)) { token.first_seen = row.timestamp; token.first_seen_unix = row.timestamp_unix; token.first_seen_block = row.block_number; }
}
const tokens = [...tokenMap.values()].sort((a, b) => a.first_seen_unix - b.first_seen_unix);
console.log(`[RECOVERY PLAN] unique_coordinates=${tokens.length} concurrency=${RECOVERY_CONCURRENCY}`);
const recovery = await recoverAll(tokens), recovered = recovery.results;
writeJson(path.join(OUT, 'recovered-tokens.json'), recovered);

const old = existingIndex();
const comparison = recovered.map(token => ({ chain: token.chain, contract: token.contract, token_id: token.token_id, first_seen: token.first_seen, same_contract_token_coordinate_in_existing_index: old.set.has(`${token.contract}|${token.token_id}`), name: token.metadata?.name || null, recovery_error: token.recovery_error || null }));
writeJson(path.join(OUT, 'comparison-with-token-index.json'), comparison);

const byChain = {};
for (const chain of Object.keys(CHAINS)) {
  const chainOccurrences = deduped.filter(item => item.chain === chain), chainRecovered = recovered.filter(item => item.chain === chain), chainComparison = comparison.filter(item => item.chain === chain), media = chainRecovered.flatMap(item => item.media || []);
  byChain[chain] = {
    transfer_occurrences: chainOccurrences.length, unique_coordinates: chainRecovered.length, metadata_recovered: chainRecovered.filter(item => item.metadata).length,
    recovery_errors: chainRecovered.filter(item => item.recovery_error).length, media_total: media.length, media_recovered: media.filter(item => item.status === 'ok').length, media_failed: media.filter(item => item.status === 'failed').length,
    same_contract_token_coordinate_in_existing_index: chainComparison.filter(item => item.same_contract_token_coordinate_in_existing_index).length,
    not_same_contract_token_coordinate_in_existing_index: chainComparison.filter(item => !item.same_contract_token_coordinate_in_existing_index).length,
    earliest_observed_transfer: chainOccurrences[0] ? { timestamp: chainOccurrences[0].timestamp, block_number: chainOccurrences[0].block_number, transaction_hash: chainOccurrences[0].transaction_hash, contract: chainOccurrences[0].contract, token_id: chainOccurrences[0].token_id, standard: chainOccurrences[0].standard } : null,
  };
}
const dated = deduped.filter(item => item.timestamp_unix > 0), earliest = dated[0] || deduped[0] || null, allMedia = recovered.flatMap(item => item.media || []);
const summary = {
  schema: 'trinity-accord/chronicle-sidechain-scan/v3', generated_at: nowIso(), target_address: ADDRESS,
  chains: Object.entries(CHAINS).map(([name, config]) => ({ name, chain_id: config.id, explorer: config.explorer, rpc: config.rpc })),
  runtime: { recovery_concurrency: RECOVERY_CONCURRENCY, http_timeout_ms: HTTP_TIMEOUT_MS, media_timeout_ms: MEDIA_TIMEOUT_MS, http_retries: HTTP_RETRIES, recovery_elapsed_ms: recovery.elapsed_ms },
  per_chain: byChain, existing_token_index: { contracts: old.contracts, tokens: old.tokens, error: old.error || null },
  transfer_occurrences: deduped.length, unique_sidechain_coordinates: recovered.length,
  same_contract_token_coordinate_in_existing_index: comparison.filter(item => item.same_contract_token_coordinate_in_existing_index).length,
  not_same_contract_token_coordinate_in_existing_index: comparison.filter(item => !item.same_contract_token_coordinate_in_existing_index).length,
  metadata_recovered: recovered.filter(item => item.metadata).length, recovery_errors: recovered.filter(item => item.recovery_error).length,
  media_total: allMedia.length, media_recovered: allMedia.filter(item => item.status === 'ok').length, media_failed: allMedia.filter(item => item.status === 'failed').length,
  earliest_observed_sidechain_nft_transfer: earliest ? { chain: earliest.chain, timestamp: earliest.timestamp, block_number: earliest.block_number, transaction_hash: earliest.transaction_hash, contract: earliest.contract, token_id: earliest.token_id, standard: earliest.standard } : null,
  comparison_note: 'The existing token_index.json does not encode chain identity in this comparison. Matching contract+token coordinates across chains is a heuristic overlap signal, not proof that two NFT occurrences are the same logical Chronicle record.',
  evidence_boundary: 'An observed sidechain occurrence is evidence input only. Cross-chain remints require semantic deduplication; this workflow does not amend Canon or automatically redefine Chronicle membership, record count, or formation time.',
};
writeJson(path.join(OUT, 'SUMMARY.json'), summary);
const manifest = buildManifest(); writeJson(path.join(OUT, 'MANIFEST.sha256.json'), manifest);
fs.writeFileSync(path.join(OUT, 'MANIFEST.sha256'), manifest.map(item => `${item.sha256}  ${item.path}`).join('\n') + '\n');
console.log('[SCAN COMPLETE]'); console.log(JSON.stringify(summary, null, 2));
