#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import os from 'os';
import { execFile } from 'child_process';
import { promisify } from 'util';
import {
  cidSha256Digest,
  delegatedProviderMultiaddrs,
  fetchBlockwiseCar,
  singleBlockCar,
} from './ipfs-car-blockwise.mjs';

const execFileAsync = promisify(execFile);

const OUT = process.env.CHRONICLE_OUT || 'artifacts/chronicle-sidechain-scan';
const ZERO = '0x0000000000000000000000000000000000000000';
const CHAINS = {
  polygon: { id: 137, explorer: 'https://polygon.blockscout.com' },
  base: { id: 8453, explorer: 'https://base.blockscout.com' },
};
const TIMEOUT = Number(process.env.CHRONICLE_EVIDENCE_HTTP_TIMEOUT_MS || 30000);
const RETRIES = Number(process.env.CHRONICLE_EVIDENCE_HTTP_RETRIES || 2);
const CAR_TIMEOUT = Number(process.env.CHRONICLE_CAR_HTTP_TIMEOUT_MS || 25000);
const CAR_RETRIES = Number(process.env.CHRONICLE_CAR_HTTP_RETRIES || 1);
const MAX = Number(process.env.CHRONICLE_CAR_MAX_BYTES || 157286400);
const CAR_BLOCK_CONCURRENCY = Math.max(1, Math.min(16, Number(process.env.CHRONICLE_CAR_BLOCK_CONCURRENCY || 2)));
const CAR_BLOCK_MAX_COUNT = Math.max(1, Math.min(100000, Number(process.env.CHRONICLE_CAR_BLOCK_MAX_COUNT || 4096)));
const CAR_BLOCK_GATEWAY_RACE = Math.max(1, Math.min(16, Number(process.env.CHRONICLE_CAR_BLOCK_GATEWAY_RACE || 2)));
const CAR_BLOCK_TIMEOUT = Number(process.env.CHRONICLE_CAR_BLOCK_HTTP_TIMEOUT_MS || 20000);
const CAR_BLOCK_RAW_TIMEOUT = Number(process.env.CHRONICLE_CAR_BLOCK_RAW_HTTP_TIMEOUT_MS || 15000);
const CAR_BLOCK_RETRIES = Number(process.env.CHRONICLE_CAR_BLOCK_HTTP_RETRIES || 0);
const CAR_BLOCK_CACHE_DIR = process.env.CHRONICLE_CAR_BLOCK_CACHE_DIR || 'artifacts/chronicle-sidechain-car-block-cache';
const HISTORICAL_CHUNK_SIZES = [...new Set(String(process.env.CHRONICLE_HISTORICAL_CHUNK_SIZES || '1048576,262144')
  .split(',')
  .map(value => Number(value.trim()))
  .filter(value => Number.isSafeInteger(value) && value > 0 && value <= MAX))]
  .sort((a, b) => b - a);
const LASSIE_BIN = String(process.env.CHRONICLE_LASSIE_BIN || '').trim();
const LASSIE_GLOBAL_TIMEOUT = Math.max(10000, Math.min(600000, Number(process.env.CHRONICLE_LASSIE_GLOBAL_TIMEOUT_MS || 180000)));
const LASSIE_PROVIDER_TIMEOUT = Math.max(5000, Math.min(LASSIE_GLOBAL_TIMEOUT, Number(process.env.CHRONICLE_LASSIE_PROVIDER_TIMEOUT_MS || 45000)));
const LASSIE_DELEGATED_ROUTING_ENDPOINT = String(process.env.CHRONICLE_LASSIE_DELEGATED_ROUTING_ENDPOINT || '').trim().replace(/\/+$/, '');
const LASSIE_DELEGATED_ROUTING_TIMEOUT = Math.max(1000, Math.min(30000, Number(process.env.CHRONICLE_LASSIE_DELEGATED_ROUTING_TIMEOUT_MS || 10000)));
const LASSIE_VERSION = String(process.env.CHRONICLE_LASSIE_VERSION || '').trim() || null;
const LASSIE_ASSET_SHA256 = String(process.env.CHRONICLE_LASSIE_ASSET_SHA256 || '').trim() || null;
const KUBO_BIN = String(process.env.CHRONICLE_KUBO_BIN || '').trim();
const KUBO_VERSION = String(process.env.CHRONICLE_KUBO_VERSION || '').trim() || null;
const KUBO_ASSET_SHA512 = String(process.env.CHRONICLE_KUBO_ASSET_SHA512 || '').trim() || null;
const KUBO_CONNECT_TIMEOUT = Math.max(5000, Math.min(60000, Number(process.env.CHRONICLE_KUBO_CONNECT_TIMEOUT_MS || 15000)));
const KUBO_BLOCK_TIMEOUT = Math.max(10000, Math.min(180000, Number(process.env.CHRONICLE_KUBO_BLOCK_TIMEOUT_MS || 60000)));
const REFRESH_HISTORY = /^(1|true|yes)$/i.test(process.env.CHRONICLE_EVIDENCE_REFRESH_HISTORY || 'false');
const C = Math.max(1, Math.min(8, Number(process.env.CHRONICLE_EVIDENCE_CONCURRENCY || 4)));
const DEFAULT_CAR_GATEWAYS = [
  'https://trustless-gateway.link/ipfs/{cid}?format=car&dag-scope=all',
  'https://ipfs.io/ipfs/{cid}?format=car&dag-scope=all',
  'https://dweb.link/ipfs/{cid}?format=car&dag-scope=all',
  'https://w3s.link/ipfs/{cid}?format=car&dag-scope=all',
  'https://gateway.pinata.cloud/ipfs/{cid}?format=car&dag-scope=all',
];
const CAR_GATEWAYS = (process.env.CHRONICLE_CAR_GATEWAYS || DEFAULT_CAR_GATEWAYS.join(','))
  .split(/[\n,]/)
  .map(x => x.trim())
  .filter(Boolean);
const CAR_WHOLE_DAG_ENDPOINT_LIMIT = Math.max(1, Math.min(
  CAR_GATEWAYS.length,
  Number(process.env.CHRONICLE_CAR_WHOLE_DAG_ENDPOINT_LIMIT || CAR_GATEWAYS.length),
));

const sha = b => crypto.createHash('sha256').update(b).digest();
const sh = b => sha(b).toString('hex');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const read = f => JSON.parse(fs.readFileSync(f, 'utf8'));
function write(f, v) {
  fs.mkdirSync(path.dirname(f), { recursive: true });
  fs.writeFileSync(f, JSON.stringify(v, null, 2) + '\n');
}
function stable(v) {
  if (Array.isArray(v)) return '[' + v.map(stable).join(',') + ']';
  if (v && typeof v === 'object') return '{' + Object.keys(v).sort().map(k => JSON.stringify(k) + ':' + stable(v[k])).join(',') + '}';
  return JSON.stringify(v);
}

async function get(url, { headers = {}, max = 20 * 1024 * 1024, label = url, timeout = TIMEOUT, retries = RETRIES } = {}) {
  let last;
  for (let a = 0; a <= retries; a++) {
    const c = new AbortController();
    const t = setTimeout(() => c.abort(), timeout);
    try {
      const r = await fetch(url, {
        signal: c.signal,
        redirect: 'follow',
        headers: { 'user-agent': 'trinity-accord-sidechain-evidence/2.1', ...headers },
      });
      if (!r.ok) {
        const e = Error(`HTTP ${r.status}`);
        e.status = r.status;
        e.retryAfter = r.headers.get('retry-after');
        throw e;
      }
      const b = Buffer.from(await r.arrayBuffer());
      if (b.length > max) throw Error(`body ${b.length}>${max}`);
      clearTimeout(t);
      return { b, url: r.url, type: r.headers.get('content-type') || '' };
    } catch (e) {
      clearTimeout(t);
      last = e;
      console.warn(`[EVIDENCE RETRY] ${label} ${a + 1}/${retries + 1} ${e.name === 'AbortError' ? 'timeout' : e.message}`);
      if (a < retries) {
        const retryAfter = Number(e.retryAfter);
        const wait = Number.isFinite(retryAfter) && retryAfter > 0
          ? Math.min(retryAfter * 1000, 15000)
          : Math.min(500 * (2 ** a), 5000);
        await sleep(wait);
      }
    }
  }
  throw Error(`${label}: ${last?.message || last}`);
}
async function getJson(u, o = {}) {
  return JSON.parse((await get(u, o)).b.toString('utf8'));
}
function sortHistory(rows) {
  return [...rows].sort((a, b) =>
    (a.timestamp_unix || 0) - (b.timestamp_unix || 0) ||
    (a.block_number || 0) - (b.block_number || 0) ||
    (a.log_index ?? 1e9) - (b.log_index ?? 1e9));
}
function norm(token, row) {
  const id = row?.total?.token_id ?? row?.token_id ?? row?.tokenID ?? token.token_id;
  if (String(id) !== String(token.token_id)) return null;
  const ts = typeof row.timestamp === 'string' ? row.timestamp : null;
  return {
    chain: token.chain,
    chain_id: token.chain_id,
    standard: token.standard,
    block_number: Number(row.block_number || 0),
    block_hash: row.block_hash || null,
    log_index: Number.isFinite(Number(row.log_index)) ? Number(row.log_index) : null,
    transaction_hash: row.transaction_hash || row.hash || null,
    timestamp: ts,
    timestamp_unix: ts && Number.isFinite(Date.parse(ts)) ? Math.floor(Date.parse(ts) / 1000) : 0,
    contract: token.contract.toLowerCase(),
    token_id: String(token.token_id),
    from: String(row?.from?.hash || row.from || '').toLowerCase(),
    to: String(row?.to?.hash || row.to || '').toLowerCase(),
    quantity: String(row?.total?.value ?? row?.value ?? '1'),
    source: 'blockscout_nft_instance_transfers',
  };
}
async function history(token) {
  const rows = [];
  let cursor = null;
  for (let p = 1; p <= 1000; p++) {
    const u = new URL(`/api/v2/tokens/${token.contract}/instances/${encodeURIComponent(token.token_id)}/transfers`, CHAINS[token.chain].explorer);
    if (cursor) for (const [k, v] of Object.entries(cursor)) if (v != null) u.searchParams.set(k, String(v));
    const d = await getJson(u, { label: `${token.chain} ${token.contract}#${token.token_id} transfers` });
    if (!Array.isArray(d.items)) throw Error('no items array');
    for (const x of d.items) {
      const n = norm(token, x);
      if (n) rows.push(n);
    }
    if (!d.next_page_params) break;
    cursor = d.next_page_params;
  }
  const m = new Map();
  for (const x of [...(token.transfers || []), ...rows]) {
    const y = { ...x, chain: token.chain, chain_id: token.chain_id, contract: token.contract.toLowerCase(), token_id: String(token.token_id) };
    const k = [y.chain, y.transaction_hash || '', y.log_index ?? '', y.contract, y.token_id, y.from || '', y.to || '', y.quantity || '1'].join('|');
    if (!m.has(k)) m.set(k, y);
  }
  return sortHistory(m.values());
}
function snapshotHistory(token) {
  const rows = sortHistory(token.transfers || []);
  if (!rows.length) {
    throw Error(`verified snapshot has no transfer history for ${token.chain} ${token.contract} #${token.token_id}`);
  }
  return rows;
}
function origin(xs) {
  const ms = xs.filter(x => String(x.from || '').toLowerCase() === ZERO);
  const x = ms[0] || xs[0];
  return x ? { kind: ms.length ? 'mint' : 'first_observed', mint_observed: !!ms.length, ...x } : null;
}
function ipfs(uri) {
  if (typeof uri !== 'string') return null;
  if (uri.startsWith('ipfs://')) {
    const a = uri.slice(7).replace(/^ipfs\//, '').split('/');
    return { root_cid: a.shift(), leaf_path: a.join('/') || null };
  }
  try {
    const u = new URL(uri);
    const m = u.pathname.match(/\/ipfs\/([^/]+)(?:\/(.*))?$/);
    const s = u.hostname.match(/^([^.]*)\.ipfs\./);
    if (m) return { root_cid: m[1], leaf_path: m[2] || null };
    if (s) return { root_cid: s[1], leaf_path: u.pathname.replace(/^\//, '') || null };
  } catch {}
  return null;
}

const cache = new Map();
let historicalChunkIndex = null;
let historicalIndexedFiles = 0;
const historicalChunkRecoveries = new Map();
function blockCacheFile(key) {
  return path.join(CAR_BLOCK_CACHE_DIR, `${key}.car`);
}
function historicalPayloadFiles() {
  const root = path.resolve(OUT);
  const prefix = `${root}${path.sep}`;
  const files = new Set();
  for (const token of src) {
    for (const payload of [token.metadata_mirror, ...(token.media || [])]) {
      if (payload?.status !== 'ok' || typeof payload.file !== 'string') continue;
      const file = path.resolve(payload.file);
      if (!file.startsWith(prefix) || !fs.existsSync(file) || !fs.statSync(file).isFile()) continue;
      files.add(file);
    }
  }
  return [...files].sort();
}
function ensureHistoricalChunkIndex() {
  if (historicalChunkIndex) return historicalChunkIndex;
  const index = new Map();
  const files = historicalPayloadFiles();
  for (const file of files) {
    const buffer = fs.readFileSync(file);
    const sourceSha256 = sh(buffer);
    const ranges = new Map();
    ranges.set(`0:${buffer.length}`, { offset: 0, length: buffer.length });
    for (const size of HISTORICAL_CHUNK_SIZES) {
      for (let offset = 0; offset < buffer.length; offset += size) {
        const length = Math.min(size, buffer.length - offset);
        ranges.set(`${offset}:${length}`, { offset, length });
      }
    }
    for (const { offset, length } of ranges.values()) {
      const digest = sh(buffer.subarray(offset, offset + length));
      if (!index.has(digest)) index.set(digest, { file, offset, length, sourceSha256 });
    }
  }
  historicalChunkIndex = index;
  historicalIndexedFiles = files.length;
  console.log(`[HISTORICAL CHUNK INDEX] files=${files.length} chunks=${index.size} sizes=${HISTORICAL_CHUNK_SIZES.join(',')}`);
  return index;
}
function recoverHistoricalBlock({ cid, key }) {
  let digest;
  try {
    digest = cidSha256Digest(cid).toString('hex');
  } catch {
    return null;
  }
  const match = ensureHistoricalChunkIndex().get(digest);
  if (!match) return null;
  const fd = fs.openSync(match.file, 'r');
  const data = Buffer.alloc(match.length);
  try {
    const bytesRead = fs.readSync(fd, data, 0, data.length, match.offset);
    if (bytesRead !== data.length) throw Error(`historical chunk short read ${bytesRead}/${data.length}`);
  } finally {
    fs.closeSync(fd);
  }
  const buffer = singleBlockCar(cid, data);
  const recovery = {
    cid,
    source_file: path.relative(OUT, match.file).replaceAll('\\', '/'),
    source_file_sha256: match.sourceSha256,
    offset: match.offset,
    bytes: match.length,
  };
  historicalChunkRecoveries.set(cid, recovery);
  saveCachedBlock({ cid, key, buffer });
  console.log(`[CAR HISTORICAL CHUNK VERIFIED] cid=${cid} file=${recovery.source_file} offset=${match.offset} bytes=${match.length}`);
  return buffer;
}
function loadCachedBlock({ cid, key }) {
  const file = blockCacheFile(key);
  return fs.existsSync(file) ? fs.readFileSync(file) : recoverHistoricalBlock({ cid, key });
}
function saveCachedBlock({ cid, key, buffer }) {
  fs.mkdirSync(CAR_BLOCK_CACHE_DIR, { recursive: true });
  const file = blockCacheFile(key);
  const tmp = `${file}.${process.pid}.${crypto.randomBytes(6).toString('hex')}.tmp`;
  fs.writeFileSync(tmp, buffer);
  fs.renameSync(tmp, file);
  console.log(`[CAR BLOCK CACHED] cid=${cid} bytes=${buffer.length}`);
}
function carUrl(template, cid) {
  return template.includes('{cid}') ? template.replaceAll('{cid}', encodeURIComponent(cid)) : `${template.replace(/\/$/, '')}/ipfs/${encodeURIComponent(cid)}?format=car&dag-scope=all`;
}
function rawBlockUrl(value) {
  const url = new URL(value);
  url.searchParams.set('format', 'raw');
  url.searchParams.delete('dag-scope');
  url.searchParams.delete('entity-bytes');
  return url.toString();
}
const delegatedProviderCache = new Map();
const delegatedProviderObservations = new Map();
async function discoverDelegatedProviders(cid) {
  if (!LASSIE_DELEGATED_ROUTING_ENDPOINT) return [];
  let pending = delegatedProviderCache.get(cid);
  if (!pending) {
    pending = (async () => {
      const url = `${LASSIE_DELEGATED_ROUTING_ENDPOINT}/routing/v1/providers/${encodeURIComponent(cid)}`;
      const payload = await getJson(url, {
        headers: { accept: 'application/json' },
        max: 1024 * 1024,
        label: `delegated providers ${cid}`,
        timeout: LASSIE_DELEGATED_ROUTING_TIMEOUT,
        retries: 0,
      });
      const providers = delegatedProviderMultiaddrs(payload);
      delegatedProviderObservations.set(cid, providers.length);
      console.log(`[CAR DELEGATED PROVIDERS] cid=${cid} multiaddrs=${providers.length}`);
      return providers;
    })();
    delegatedProviderCache.set(cid, pending);
  }
  return pending;
}
async function discoverLassieProviders(cids) {
  const providers = [];
  const seen = new Set();
  for (const cid of [...new Set(cids.filter(Boolean))]) {
    try {
      for (const provider of await discoverDelegatedProviders(cid)) {
        if (seen.has(provider)) continue;
        seen.add(provider);
        providers.push(provider);
      }
    } catch (error) {
      console.warn(`[CAR DELEGATED PROVIDERS FAILED] cid=${cid} ${error.message}`);
    }
  }
  return providers;
}
function addressesByPeer(providers) {
  const groups = new Map();
  for (const provider of providers) {
    const match = provider.match(/\/p2p\/([^/]+)$/);
    if (!match) continue;
    const addresses = groups.get(match[1]) || [];
    addresses.push(provider);
    groups.set(match[1], addresses);
  }
  return [...groups.values()];
}
async function fetchKuboBlock({ cid, rootCid }) {
  if (!KUBO_BIN) throw Error('Kubo Bitswap fallback is not configured');
  const providers = await discoverLassieProviders([cid, rootCid]);
  const peerGroups = addressesByPeer(providers);
  const connections = await Promise.allSettled(peerGroups.map(addresses => execFileAsync(KUBO_BIN, [
    'swarm', 'connect', ...addresses,
  ], {
    timeout: KUBO_CONNECT_TIMEOUT,
    maxBuffer: 1024 * 1024,
    windowsHide: true,
  })));
  const connected = connections.filter(result => result.status === 'fulfilled').length;
  console.log(`[CAR KUBO CONNECT] cid=${cid} multiaddrs=${providers.length} peers=${peerGroups.length} connected=${connected}`);
  try {
    const { stdout } = await execFileAsync(KUBO_BIN, ['block', 'get', cid], {
      timeout: KUBO_BLOCK_TIMEOUT,
      maxBuffer: MAX,
      encoding: 'buffer',
      windowsHide: true,
    });
    const data = Buffer.from(stdout);
    if (!data.length) throw Error('returned an empty block');
    const buffer = singleBlockCar(cid, data);
    console.log(`[CAR KUBO BLOCK VERIFIED] cid=${cid} bytes=${data.length} connected=${connected}`);
    return buffer;
  } catch (error) {
    const detail = Buffer.isBuffer(error.stderr)
      ? error.stderr.toString('utf8')
      : String(error.stderr || error.stdout || error.message || error);
    throw Error(`Kubo block retrieval failed for ${cid} multiaddrs=${providers.length} peers=${peerGroups.length} connected=${connected}: ${detail.trim().replace(/\s+/g, ' ').slice(0, 800)}`);
  }
}
async function runLassieCar({ cid, scope, neededCid, providerCids = [] }) {
  if (!LASSIE_BIN) throw Error('Lassie fallback is not configured');
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'chronicle-lassie-'));
  const output = path.join(tmp, `${cid}-${scope}.car`);
  try {
    const providers = await discoverLassieProviders([cid, ...providerCids]);
    const args = [
      'fetch',
      '--output', output,
      '--tempdir', tmp,
      '--dag-scope', scope,
      '--protocols', 'bitswap,graphsync,http',
      '--global-timeout', `${LASSIE_GLOBAL_TIMEOUT}ms`,
      '--provider-timeout', `${LASSIE_PROVIDER_TIMEOUT}ms`,
    ];
    if (providers.length) args.push('--providers', providers.join(','));
    args.push(cid);
    console.log(`[CAR LASSIE START] cid=${cid} scope=${scope} needed=${neededCid} delegated_multiaddrs=${providers.length}`);
    const { stdout, stderr } = await execFileAsync(LASSIE_BIN, args, {
      timeout: LASSIE_GLOBAL_TIMEOUT + 15000,
      maxBuffer: 2 * 1024 * 1024,
      windowsHide: true,
    });
    if (!fs.existsSync(output)) throw Error('completed without a CAR output file');
    const buffer = fs.readFileSync(output);
    if (!buffer.length) throw Error('returned an empty CAR');
    if (buffer.length > MAX) throw Error(`CAR bytes ${buffer.length}>${MAX}`);
    const detail = String(stderr || stdout || '').trim().replace(/\s+/g, ' ').slice(0, 400);
    console.log(`[CAR LASSIE RECEIVED] cid=${cid} scope=${scope} needed=${neededCid} bytes=${buffer.length}${detail ? ` detail=${detail}` : ''}`);
    return buffer;
  } catch (error) {
    const detail = String(error.stderr || error.stdout || error.message || error).trim().replace(/\s+/g, ' ').slice(0, 800);
    throw Error(`Lassie ${scope} retrieval failed for ${cid}: ${detail || 'unknown error'}`);
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
}
const lassieRootCars = new Map();
function fetchLassieRootCar({ rootCid, neededCid }) {
  let pending = lassieRootCars.get(rootCid);
  if (!pending) {
    pending = runLassieCar({ cid: rootCid, scope: 'all', neededCid, providerCids: [neededCid] });
    lassieRootCars.set(rootCid, pending);
  } else {
    console.log(`[CAR LASSIE ROOT REUSE] cid=${rootCid} needed=${neededCid}`);
  }
  return pending;
}
async function fetchLassieBlock({ cid, rootCid }) {
  let blockError;
  try {
    return await runLassieCar({ cid, scope: 'block', neededCid: cid, providerCids: [rootCid] });
  } catch (error) {
    blockError = error;
  }
  if (rootCid && rootCid !== cid) {
    try {
      return await fetchLassieRootCar({ rootCid, neededCid: cid });
    } catch (rootError) {
      throw Error(`direct=${blockError.message}; root=${rootError.message}`);
    }
  }
  throw blockError;
}
async function fetchProviderBlock({ cid, rootCid }) {
  const errors = [];
  if (KUBO_BIN) {
    try {
      return await fetchKuboBlock({ cid, rootCid });
    } catch (error) {
      errors.push(error.message);
    }
  }
  if (LASSIE_BIN) {
    try {
      return await fetchLassieBlock({ cid, rootCid });
    } catch (error) {
      errors.push(error.message);
    }
  }
  throw Error(errors.join('; ') || 'provider fallback is not configured');
}
async function car(ref) {
  if (!ref) return { status: 'not_ipfs' };
  let base = cache.get(ref.root_cid);
  if (!base) {
    base = (async () => {
      const d = path.join(OUT, 'evidence-v2', 'cars');
      fs.mkdirSync(d, { recursive: true });
      const f = path.join(d, `${ref.root_cid}.car`);
      if (fs.existsSync(f)) {
        const b = fs.readFileSync(f);
        return {
          status: 'ok',
          root_cid: ref.root_cid,
          file: path.relative(OUT, f).replaceAll('\\', '/'),
          car_bytes: b.length,
          car_sha256: sh(b),
          retrieval: 'restored_cache',
        };
      }
      const errors = [];
      for (let i = 0; i < CAR_WHOLE_DAG_ENDPOINT_LIMIT; i++) {
        const u = carUrl(CAR_GATEWAYS[i], ref.root_cid);
        try {
          const r = await get(u, {
            headers: { accept: 'application/vnd.ipld.car' },
            max: MAX,
            label: `CAR ${ref.root_cid} endpoint=${i + 1}/${CAR_GATEWAYS.length}`,
            timeout: CAR_TIMEOUT,
            retries: CAR_RETRIES,
          });
          const type = r.type.toLowerCase();
          if (!type.includes('application/vnd.ipld.car') && !type.includes('application/octet-stream')) {
            throw Error(`unexpected content-type ${r.type || '(empty)'}`);
          }
          fs.writeFileSync(f, r.b);
          return {
            status: 'ok',
            root_cid: ref.root_cid,
            file: path.relative(OUT, f).replaceAll('\\', '/'),
            car_bytes: r.b.length,
            car_sha256: sh(r.b),
            content_type: r.type,
            retrieval: 'gateway_untrusted_offline_verification_required',
            retrieval_endpoint_index: i + 1,
          };
        } catch (e) {
          errors.push({ endpoint_index: i + 1, error: e.message });
        }
      }
      console.warn(`[CAR WHOLE-DAG FAILED] cid=${ref.root_cid} endpoints=${CAR_WHOLE_DAG_ENDPOINT_LIMIT}; trying blockwise recovery`);
      try {
        const recovered = await fetchBlockwiseCar({
          rootCid: ref.root_cid,
          gateways: CAR_GATEWAYS,
          maxBytes: MAX,
          concurrency: CAR_BLOCK_CONCURRENCY,
          maxBlocks: CAR_BLOCK_MAX_COUNT,
          gatewayRace: Math.min(CAR_BLOCK_GATEWAY_RACE, CAR_GATEWAYS.length),
          loadBlock: loadCachedBlock,
          saveBlock: saveCachedBlock,
          fetchFallback: LASSIE_BIN || KUBO_BIN
            ? context => fetchProviderBlock({ ...context, rootCid: ref.root_cid })
            : null,
          fetchCar: async (url, context) => {
            let carError;
            try {
              const r = await get(url, {
                headers: { accept: 'application/vnd.ipld.car' },
                max: MAX,
                label: `CAR block ${context.cid} gateway=${context.gatewayIndex}/${CAR_GATEWAYS.length}`,
                timeout: CAR_BLOCK_TIMEOUT,
                retries: CAR_BLOCK_RETRIES,
              });
              const type = r.type.toLowerCase();
              if (!type.includes('application/vnd.ipld.car') && !type.includes('application/octet-stream')) {
                throw Error(`unexpected content-type ${r.type || '(empty)'}`);
              }
              return r.b;
            } catch (error) {
              carError = error;
            }
            try {
              const rawUrl = rawBlockUrl(url);
              const r = await get(rawUrl, {
                headers: { accept: 'application/vnd.ipld.raw' },
                max: MAX,
                label: `raw block ${context.cid} gateway=${context.gatewayIndex}/${CAR_GATEWAYS.length}`,
                timeout: CAR_BLOCK_RAW_TIMEOUT,
                retries: CAR_BLOCK_RETRIES,
              });
              const wrapped = singleBlockCar(context.cid, r.b);
              console.log(`[CAR RAW BLOCK VERIFIED] cid=${context.cid} gateway=${context.gatewayIndex} bytes=${r.b.length}`);
              return wrapped;
            } catch (rawError) {
              throw Error(`CAR request failed: ${carError.message}; raw request failed: ${rawError.message}`);
            }
          },
        });
        fs.writeFileSync(f, recovered.buffer);
        console.log(`[CAR BLOCKWISE COMPLETE] cid=${ref.root_cid} blocks=${recovered.blocks} requests=${recovered.requests} lassie=${recovered.fallbackHits}/${recovered.fallbackRequests} bytes=${recovered.buffer.length}`);
        return {
          status: 'ok',
          root_cid: ref.root_cid,
          file: path.relative(OUT, f).replaceAll('\\', '/'),
          car_bytes: recovered.buffer.length,
          car_sha256: sh(recovered.buffer),
          content_type: 'application/vnd.ipld.car',
          retrieval: 'gateway_untrusted_blockwise_car_offline_verification_required',
          block_count: recovered.blocks,
          blockwise_request_count: recovered.requests,
          block_cache_hits: recovered.cacheHits,
          block_cache_writes: recovered.cacheWrites,
          lassie_fallback_requests: recovered.fallbackRequests,
          lassie_fallback_hits: recovered.fallbackHits,
        };
      } catch (e) {
        errors.push({ mode: 'blockwise', error: e.message });
        console.error(`[CAR FAILED] cid=${ref.root_cid} endpoints=${CAR_GATEWAYS.length} blockwise=${e.message}`);
        return { status: 'failed', root_cid: ref.root_cid, error: e.message, attempts: errors };
      }
    })();
    cache.set(ref.root_cid, base);
  }
  return { ...(await base), leaf_path: ref.leaf_path };
}
function payload(m) {
  if (!m || m.status !== 'ok' || !m.file || !fs.existsSync(m.file)) return null;
  const b = fs.readFileSync(m.file);
  return { file: path.relative(OUT, m.file).replaceAll('\\', '/'), bytes: b.length, sha256: sh(b) };
}
function mth(a) {
  if (!a.length) return sha(Buffer.alloc(0));
  if (a.length === 1) return sha(Buffer.concat([Buffer.from([0]), a[0]]));
  let k = 1;
  while ((k << 1) < a.length) k <<= 1;
  return sha(Buffer.concat([Buffer.from([1]), mth(a.slice(0, k)), mth(a.slice(k))]));
}

const src = read(path.join(OUT, 'recovered-tokens.json'));
console.log(`[HISTORY SOURCE] ${REFRESH_HISTORY ? 'live_blockscout_refresh' : 'verified_recovered_tokens_snapshot'} records=${src.length}`);
const res = new Array(src.length);
let next = 0, done = 0;
async function worker(id) {
  while (true) {
    const i = next++;
    if (i >= src.length) return;
    const t = src[i];
    console.log(`[EVIDENCE START] ${i + 1}/${src.length} worker=${id} ${t.chain} ${t.contract} #${t.token_id}`);
    let xs, err = null, historySource;
    if (!REFRESH_HISTORY) {
      xs = snapshotHistory(t);
      historySource = 'verified_recovered_tokens_snapshot';
    } else {
      try {
        xs = await history(t);
        historySource = 'blockscout_instance_history';
      } catch (e) {
        err = e.message;
        xs = snapshotHistory(t);
        historySource = 'verified_recovered_tokens_snapshot_fallback';
      }
    }
    const o = origin(xs);
    const mu = t.token_uri?.uri || null;
    const mr = ipfs(mu);
    const mc = await car(mr);
    const media = [];
    for (const m of t.media || []) {
      const u = m.original_uri || t.metadata?.[m.role] || null;
      const r = ipfs(u);
      media.push({ role: m.role, uri: u, ipfs: r, payload: payload(m), car: await car(r) });
    }
    res[i] = {
      asset_id: `eip155:${t.chain_id}/${String(t.standard || '').toLowerCase().replace('-', '')}:${t.contract}/${t.token_id}`,
      chain: { name: t.chain, namespace: 'eip155', chain_id: t.chain_id },
      standard: t.standard,
      contract: t.contract.toLowerCase(),
      token_id: String(t.token_id),
      origin: o,
      origin_resolution: { full_instance_history: historySource, error: err },
      transfers: xs,
      token_uri: mu,
      content: {
        metadata: {
          root_cid: mr?.root_cid || null,
          leaf_path: mr?.leaf_path || null,
          payload: payload(t.metadata_mirror),
          normalized_sha256: t.metadata ? sh(Buffer.from(stable(t.metadata))) : null,
          car: mc,
        },
        media,
      },
      recovery_error: t.recovery_error || null,
    };
    done++;
    console.log(`[EVIDENCE PROGRESS] ${done}/${src.length} origin=${o?.kind || 'missing'} car=${mc.status}`);
  }
}
await Promise.all(Array.from({ length: Math.min(C, src.length) }, (_, i) => worker(i + 1)));

res.sort((a, b) => {
  let x = (a.origin?.timestamp_unix || 0) - (b.origin?.timestamp_unix || 0);
  if (x) return x;
  x = a.chain.chain_id - b.chain.chain_id;
  if (x) return x;
  x = a.contract.localeCompare(b.contract);
  if (x) return x;
  const p = BigInt(a.token_id), q = BigInt(b.token_id);
  return p < q ? -1 : p > q ? 1 : 0;
});
const E = path.join(OUT, 'evidence-v2');
const index = {
  schema: 'trinity-accord/chronicle-sidechain-nft-identity-index/v2',
  generated_at: new Date().toISOString(),
  record_semantics: 'Every independently minted NFT coordinate (chain_id + contract + token_id) is one Chronicle record; transfer events are provenance and are never cross-chain-deduplicated.',
  records: res,
};
write(path.join(E, 'SIDECHAIN-NFT-IDENTITY-INDEX.json'), index);
const timeline = res.map(r => ({
  timestamp: r.origin?.timestamp || null,
  timestamp_unix: r.origin?.timestamp_unix || 0,
  chain: r.chain.name,
  chain_id: r.chain.chain_id,
  contract: r.contract,
  token_id: r.token_id,
  origin_kind: r.origin?.kind || null,
  transaction_hash: r.origin?.transaction_hash || null,
  block_number: r.origin?.block_number || null,
  block_hash: r.origin?.block_hash || null,
  log_index: r.origin?.log_index ?? null,
  asset_id: r.asset_id,
}));
write(path.join(E, 'TIMELINE.json'), timeline);
for (const c of Object.keys(CHAINS)) write(path.join(E, `${c.toUpperCase()}-TIMELINE.json`), timeline.filter(x => x.chain === c));
const proj = res.map(r => ({
  asset_id: r.asset_id,
  chain_id: r.chain.chain_id,
  standard: r.standard,
  contract: r.contract,
  token_id: r.token_id,
  origin: r.origin ? Object.fromEntries(['kind', 'mint_observed', 'transaction_hash', 'block_hash', 'block_number', 'log_index', 'timestamp', 'timestamp_unix', 'from', 'to', 'quantity'].map(k => [k, r.origin[k] ?? null])) : null,
  content: {
    metadata: {
      root_cid: r.content.metadata.root_cid,
      leaf_path: r.content.metadata.leaf_path,
      payload_sha256: r.content.metadata.payload?.sha256 || null,
      payload_bytes: r.content.metadata.payload?.bytes || null,
      normalized_sha256: r.content.metadata.normalized_sha256,
      car_sha256: r.content.metadata.car?.car_sha256 || null,
      car_bytes: r.content.metadata.car?.car_bytes || null,
    },
    media: r.content.media.map(m => ({
      role: m.role,
      root_cid: m.ipfs?.root_cid || null,
      leaf_path: m.ipfs?.leaf_path || null,
      payload_sha256: m.payload?.sha256 || null,
      payload_bytes: m.payload?.bytes || null,
      car_sha256: m.car?.car_sha256 || null,
      car_bytes: m.car?.car_bytes || null,
    })),
  },
})).sort((a, b) => a.asset_id.localeCompare(b.asset_id));
const leaf = proj.map(x => Buffer.from(stable(x)));
const leaves = proj.map((p, i) => ({ asset_id: p.asset_id, leaf_sha256: sha(Buffer.concat([Buffer.from([0]), leaf[i]])).toString('hex') }));
const raw = fs.readFileSync(path.join(E, 'SIDECHAIN-NFT-IDENTITY-INDEX.json'));
const commit = {
  schema: 'trinity-accord/chronicle-sidechain-nft-collection-commitment/v2',
  generated_at: new Date().toISOString(),
  algorithm: 'RFC6962-style SHA-256 domain separation',
  canonicalization: 'recursive lexicographic JSON keys; arrays preserved',
  record_count: proj.length,
  source_index_sha256: sh(raw),
  merkle_root_sha256: mth(leaf).toString('hex'),
  leaves,
};
write(path.join(E, 'SIDECHAIN-NFT-COLLECTION-COMMITMENT.json'), commit);
write(path.join(E, 'L3-SETTLEMENT-STATUS.json'), {
  schema: 'trinity-accord/chronicle-sidechain-l3-settlement-status/v1',
  generated_at: new Date().toISOString(),
  status: 'not_yet_captured',
  boundary: 'L1 identity/content and L2 execution inclusion are distinct from L3 settlement/finality. This is not an L3 PASS.',
  chains: {
    polygon: {
      mechanism: 'Bor/Heimdall checkpoint or milestone; Ethereum RootChainProxy anchoring',
      ethereum_root_chain_proxy: '0x86E4Dc95c7FBdBf52e33D563BbDB00823894C287',
      status: 'not_yet_captured',
    },
    base: { mechanism: 'OP Stack/Base output or proof system settled on Ethereum', status: 'not_yet_captured' },
  },
});
const refs = res.flatMap(r => [r.content.metadata.car, ...r.content.media.map(m => m.car)]).filter(Boolean);
const fail = refs.filter(x => x.status === 'failed');
const miss = res.filter(r => !r.origin);
const fallback = res.filter(r => r.origin && !r.origin.mint_observed);
const prior = read(path.join(OUT, 'SUMMARY.json'));
const earliest = timeline.filter(x => x.timestamp_unix > 0).sort((a, b) => a.timestamp_unix - b.timestamp_unix)[0] || null;
write(path.join(OUT, 'SUMMARY.json'), {
  ...prior,
  schema: 'trinity-accord/chronicle-sidechain-scan/v4',
  chronicle_record_semantics: 'one NFT coordinate per chain is one Chronicle record; no cross-chain record deduplication',
  sidechain_nft_records: res.length,
  origins: {
    mint_observed: res.length - fallback.length - miss.length,
    mint_not_observed_first_observed_used: fallback.length,
    missing: miss.length,
  },
  car_preservation: {
    references: refs.length,
    ok: refs.filter(x => x.status === 'ok').length,
    not_ipfs: refs.filter(x => x.status === 'not_ipfs').length,
    failed: fail.length,
    unique_car_files: new Set(refs.filter(x => x.file).map(x => x.file)).size,
  },
  earliest_sidechain_nft_origin: earliest,
  comparison_note: 'Cross-chain similarity is annotation only and never removes an NFT Chronicle record.',
  evidence_boundary: 'Each Polygon/Base NFT is preserved as an independent Chronicle record. This does not amend the three-inscription Bitcoin Canon.',
});
write(path.join(E, 'BUILD-REPORT.json'), {
  schema: 'trinity-accord/chronicle-sidechain-evidence-build/v2',
  records: res.length,
  mint_observed: res.length - fallback.length - miss.length,
  mint_not_observed: fallback.length,
  car_failures: fail,
  car_gateway_count: CAR_GATEWAYS.length,
  lassie_fallback: {
    enabled: Boolean(LASSIE_BIN),
    version: LASSIE_VERSION,
    asset_sha256: LASSIE_ASSET_SHA256,
    global_timeout_ms: LASSIE_GLOBAL_TIMEOUT,
    provider_timeout_ms: LASSIE_PROVIDER_TIMEOUT,
    delegated_routing_endpoint: LASSIE_DELEGATED_ROUTING_ENDPOINT || null,
    delegated_routing_timeout_ms: LASSIE_DELEGATED_ROUTING_TIMEOUT,
    delegated_provider_multiaddrs_by_cid: Object.fromEntries([...delegatedProviderObservations.entries()].sort(([a], [b]) => a.localeCompare(b))),
  },
  kubo_bitswap_fallback: {
    enabled: Boolean(KUBO_BIN),
    version: KUBO_VERSION,
    asset_sha512: KUBO_ASSET_SHA512,
    connect_timeout_ms: KUBO_CONNECT_TIMEOUT,
    block_timeout_ms: KUBO_BLOCK_TIMEOUT,
  },
  historical_chunk_fallback: {
    chunk_sizes: HISTORICAL_CHUNK_SIZES,
    indexed_files: historicalIndexedFiles,
    recoveries: [...historicalChunkRecoveries.values()].sort((a, b) => a.cid.localeCompare(b.cid)),
  },
  history_refresh_enabled: REFRESH_HISTORY,
  history_sources: Object.fromEntries([...new Set(res.map(r => r.origin_resolution.full_instance_history))]
    .sort()
    .map(source => [source, res.filter(r => r.origin_resolution.full_instance_history === source).length])),
  l1_merkle_root_sha256: commit.merkle_root_sha256,
  pass: !miss.length && !fail.length,
});
if (miss.length || fail.length) {
  console.error(`[EVIDENCE FAIL] missing=${miss.length} car_failures=${fail.length}`);
  process.exit(1);
}
console.log(`[EVIDENCE COMPLETE] records=${res.length} l1=${commit.merkle_root_sha256}`);
