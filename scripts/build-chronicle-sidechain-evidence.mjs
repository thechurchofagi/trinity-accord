#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { fetchBlockwiseCar } from './ipfs-car-blockwise.mjs';

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
  return [...m.values()].sort((a, b) =>
    (a.timestamp_unix || 0) - (b.timestamp_unix || 0) ||
    (a.block_number || 0) - (b.block_number || 0) ||
    (a.log_index ?? 1e9) - (b.log_index ?? 1e9));
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
function carUrl(template, cid) {
  return template.includes('{cid}') ? template.replaceAll('{cid}', encodeURIComponent(cid)) : `${template.replace(/\/$/, '')}/ipfs/${encodeURIComponent(cid)}?format=car&dag-scope=all`;
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
          fetchCar: async (url, context) => {
            const r = await get(url, {
              headers: { accept: 'application/vnd.ipld.car' },
              max: MAX,
              label: `CAR block ${context.cid} gateway=${context.gatewayIndex}/${CAR_GATEWAYS.length}`,
              timeout: CAR_TIMEOUT,
              retries: CAR_RETRIES,
            });
            const type = r.type.toLowerCase();
            if (!type.includes('application/vnd.ipld.car') && !type.includes('application/octet-stream')) {
              throw Error(`unexpected content-type ${r.type || '(empty)'}`);
            }
            return r.b;
          },
        });
        fs.writeFileSync(f, recovered.buffer);
        console.log(`[CAR BLOCKWISE COMPLETE] cid=${ref.root_cid} blocks=${recovered.blocks} requests=${recovered.requests} bytes=${recovered.buffer.length}`);
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
const res = new Array(src.length);
let next = 0, done = 0;
async function worker(id) {
  while (true) {
    const i = next++;
    if (i >= src.length) return;
    const t = src[i];
    console.log(`[EVIDENCE START] ${i + 1}/${src.length} worker=${id} ${t.chain} ${t.contract} #${t.token_id}`);
    let xs, err = null;
    try {
      xs = await history(t);
    } catch (e) {
      err = e.message;
      xs = [...(t.transfers || [])].sort((a, b) => (a.timestamp_unix || 0) - (b.timestamp_unix || 0));
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
      origin_resolution: { full_instance_history: err ? 'fallback_address_history' : 'blockscout_instance_history', error: err },
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
  l1_merkle_root_sha256: commit.merkle_root_sha256,
  pass: !miss.length && !fail.length,
});
if (miss.length || fail.length) {
  console.error(`[EVIDENCE FAIL] missing=${miss.length} car_failures=${fail.length}`);
  process.exit(1);
}
console.log(`[EVIDENCE COMPLETE] records=${res.length} l1=${commit.merkle_root_sha256}`);
