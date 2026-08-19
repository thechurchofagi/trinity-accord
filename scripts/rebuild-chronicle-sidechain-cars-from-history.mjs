#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import os from 'os';
import crypto from 'crypto';
import { execFile } from 'child_process';
import { promisify } from 'util';
import {
  rebuildCarsFromHistoricalPayloads as baseRebuildCarsFromHistoricalPayloads,
  refsFromSnapshot,
} from './rebuild-chronicle-sidechain-cars-from-history-base.mjs';
import {
  cidSha256Digest,
  singleBlockCar,
} from './ipfs-car-blockwise.mjs';
import { verifyCompleteCar } from './chronicle-sidechain-car-integrity.mjs';

export * from './rebuild-chronicle-sidechain-cars-from-history-base.mjs';

const execFileAsync = promisify(execFile);
const MAX = Number(process.env.CHRONICLE_CAR_MAX_BYTES || 157286400);
const HTTP_TIMEOUT = Math.max(
  3000,
  Math.min(30000, Number(process.env.CHRONICLE_HISTORICAL_CONTENT_TIMEOUT_MS || 12000)),
);
const ROOT_CONCURRENCY = Math.max(
  1,
  Math.min(8, Number(process.env.CHRONICLE_HISTORICAL_CONTENT_CONCURRENCY || 4)),
);
const EXTRA_GATEWAYS = [
  'https://ipfs.io/ipfs/{cid}',
  'https://dweb.link/ipfs/{cid}',
  'https://w3s.link/ipfs/{cid}',
  'https://gateway.pinata.cloud/ipfs/{cid}',
  'https://nftstorage.link/ipfs/{cid}',
  'https://4everland.io/ipfs/{cid}',
];

function sha256(buffer) {
  return crypto.createHash('sha256').update(buffer).digest();
}

function sha256Hex(buffer) {
  return sha256(buffer).toString('hex');
}

function safeLeafSegments(value) {
  if (!value) return [];
  const out = [];
  for (const raw of String(value).split('/')) {
    if (!raw) continue;
    let segment;
    try { segment = decodeURIComponent(raw); } catch { segment = raw; }
    if (!segment || segment === '.' || segment === '..' || segment.includes('/') || segment.includes('\\') || segment.includes('\0')) {
      throw Error(`unsafe historical leaf path segment ${JSON.stringify(segment)}`);
    }
    out.push(segment);
  }
  return out;
}

function atomicWrite(file, buffer) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const tmp = `${file}.${process.pid}.${crypto.randomBytes(6).toString('hex')}.tmp`;
  fs.writeFileSync(tmp, buffer);
  fs.renameSync(tmp, file);
}

function appendTrace(out, event) {
  const file = path.join(out, 'runtime', 'HISTORICAL-CONTENT-RECOVERY.ndjson');
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.appendFileSync(file, JSON.stringify({ timestamp: new Date().toISOString(), ...event }) + '\n');
}

function rootCodecHint(rootCid) {
  if (String(rootCid).startsWith('Qm')) return 'cidv0-dag-pb';
  if (String(rootCid).startsWith('bafk')) return 'cidv1-raw-likely';
  if (String(rootCid).startsWith('bafy')) return 'cidv1-dag-pb-likely';
  return 'unknown';
}

function importerVariants(rootCid, bytes) {
  // For a single small file, chunk size/layout cannot change a one-block DAG.
  // Keep the matrix minimal there; expand only for larger payloads.
  if (String(rootCid).startsWith('Qm')) {
    if (bytes <= 262144) {
      return [{ cidVersion: 0, rawLeaves: false, chunker: 'size-262144', layout: 'balanced' }];
    }
    return [
      { cidVersion: 0, rawLeaves: false, chunker: 'size-262144', layout: 'balanced' },
      { cidVersion: 0, rawLeaves: false, chunker: 'size-524288', layout: 'balanced' },
      { cidVersion: 0, rawLeaves: false, chunker: 'size-1048576', layout: 'balanced' },
      { cidVersion: 0, rawLeaves: false, chunker: 'size-262144', layout: 'trickle' },
      { cidVersion: 0, rawLeaves: false, chunker: 'size-1048576', layout: 'trickle' },
    ];
  }
  if (bytes <= 262144) {
    return [{ cidVersion: 1, rawLeaves: false, chunker: 'size-262144', layout: 'balanced' }];
  }
  return [
    { cidVersion: 1, rawLeaves: true, chunker: 'size-262144', layout: 'balanced' },
    { cidVersion: 1, rawLeaves: false, chunker: 'size-262144', layout: 'balanced' },
    { cidVersion: 1, rawLeaves: true, chunker: 'size-524288', layout: 'balanced' },
    { cidVersion: 1, rawLeaves: false, chunker: 'size-524288', layout: 'balanced' },
    { cidVersion: 1, rawLeaves: true, chunker: 'size-1048576', layout: 'balanced' },
    { cidVersion: 1, rawLeaves: false, chunker: 'size-1048576', layout: 'balanced' },
    { cidVersion: 1, rawLeaves: true, chunker: 'size-262144', layout: 'trickle' },
    { cidVersion: 1, rawLeaves: false, chunker: 'size-262144', layout: 'trickle' },
  ];
}

function addArgs(input, recursive, variant, onlyHash) {
  const args = [
    'add',
    '-Q',
    '--pin=false',
    `--cid-version=${variant.cidVersion}`,
    `--raw-leaves=${variant.rawLeaves ? 'true' : 'false'}`,
    `--chunker=${variant.chunker}`,
  ];
  if (variant.layout === 'trickle') args.push('--trickle');
  if (onlyHash) args.push('--only-hash');
  if (recursive) args.push('-r');
  args.push(input);
  return args;
}

async function kuboAddCid(kubo, input, recursive, variant, onlyHash) {
  const { stdout } = await execFileAsync(kubo, addArgs(input, recursive, variant, onlyHash), {
    timeout: 60000,
    maxBuffer: 1024 * 1024,
    encoding: 'utf8',
    windowsHide: true,
  });
  return String(stdout || '').trim().split(/\s+/).filter(Boolean).at(-1) || null;
}

async function exportCar(kubo, rootCid) {
  const { stdout } = await execFileAsync(kubo, ['dag', 'export', rootCid], {
    timeout: 90000,
    maxBuffer: MAX,
    encoding: 'buffer',
    windowsHide: true,
  });
  const buffer = Buffer.from(stdout);
  if (!buffer.length) throw Error('Kubo dag export returned empty CAR');
  if (buffer.length > MAX) throw Error(`Kubo dag export bytes ${buffer.length}>${MAX}`);
  verifyCompleteCar(buffer, rootCid);
  return buffer;
}

function directRawCar(rootCid, data, leafPath) {
  if (leafPath) return null;
  let digest;
  try { digest = cidSha256Digest(rootCid); } catch { return null; }
  if (!sha256(data).equals(digest)) return null;
  const car = singleBlockCar(rootCid, data);
  verifyCompleteCar(car, rootCid);
  return car;
}

async function exactCarFromBytes({ kubo, rootCid, data, leafPath, out, source, variantLabel }) {
  const direct = directRawCar(rootCid, data, leafPath);
  if (direct) {
    appendTrace(out, {
      event: 'candidate_exact_match',
      root_cid: rootCid,
      source,
      candidate_variant: variantLabel || null,
      method: 'direct_raw_block',
      bytes: data.length,
      sha256: sha256Hex(data),
    });
    return { car: direct, method: 'direct_raw_block', importer: null };
  }
  if (!kubo) return null;

  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'chronicle-content-rebuild-'));
  try {
    let input = path.join(tmp, 'candidate.bin');
    let recursive = false;
    const segments = safeLeafSegments(leafPath);
    if (segments.length) {
      const tree = path.join(tmp, 'root');
      input = path.join(tree, ...segments);
      fs.mkdirSync(path.dirname(input), { recursive: true });
      recursive = true;
    }
    fs.writeFileSync(input, data);

    for (const importer of importerVariants(rootCid, data.length)) {
      const mode = `v${importer.cidVersion}/raw=${importer.rawLeaves}/${importer.chunker}/${importer.layout}`;
      let computed;
      try {
        computed = await kuboAddCid(kubo, recursive ? path.join(tmp, 'root') : input, recursive, importer, true);
      } catch (error) {
        appendTrace(out, {
          event: 'candidate_hash_error',
          root_cid: rootCid,
          source,
          candidate_variant: variantLabel || null,
          mode,
          error: String(error.message || error).replace(/\s+/g, ' ').slice(0, 600),
        });
        continue;
      }
      appendTrace(out, {
        event: 'candidate_hash',
        root_cid: rootCid,
        source,
        candidate_variant: variantLabel || null,
        mode,
        bytes: data.length,
        sha256: sha256Hex(data),
        computed_cid: computed,
        exact: computed === rootCid,
      });
      if (computed !== rootCid) continue;

      const imported = await kuboAddCid(kubo, recursive ? path.join(tmp, 'root') : input, recursive, importer, false);
      if (imported !== rootCid) throw Error(`Kubo import drift expected=${rootCid} actual=${imported}`);
      const car = await exportCar(kubo, rootCid);
      return { car, method: 'kubo_exact_content_rebuild', importer: mode };
    }
    return null;
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
}

function contentGateways() {
  const configured = String(process.env.CHRONICLE_HISTORICAL_CONTENT_GATEWAYS || '')
    .split(/[\n,]/)
    .map(x => x.trim())
    .filter(Boolean);
  const inherited = String(process.env.CHRONICLE_CAR_GATEWAYS || '')
    .split(/[\n,]/)
    .map(x => x.trim())
    .filter(Boolean)
    .map(value => {
      try {
        const cleaned = value.replaceAll('{cid}', '__CID__');
        const url = new URL(cleaned);
        url.searchParams.delete('format');
        url.searchParams.delete('dag-scope');
        url.searchParams.delete('entity-bytes');
        return url.toString().replaceAll('__CID__', '{cid}');
      } catch {
        return value.replace(/[?&](?:format|dag-scope|entity-bytes)=[^&]*/g, '').replace(/[?&]$/, '');
      }
    });
  return [...new Set([...configured, ...inherited, ...EXTRA_GATEWAYS])];
}

function gatewayUrl(template, rootCid, leafPath) {
  const raw = template.includes('{cid}')
    ? template.replaceAll('{cid}', encodeURIComponent(rootCid))
    : `${template.replace(/\/$/, '')}/ipfs/${encodeURIComponent(rootCid)}`;
  const url = new URL(raw);
  url.searchParams.delete('format');
  url.searchParams.delete('dag-scope');
  url.searchParams.delete('entity-bytes');
  if (leafPath) {
    const suffix = safeLeafSegments(leafPath).map(encodeURIComponent).join('/');
    url.pathname = `${url.pathname.replace(/\/$/, '')}/${suffix}`;
  }
  return url.toString();
}

async function fetchContent(url, rootCid, out, endpointIndex) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), HTTP_TIMEOUT);
  try {
    const response = await fetch(url, {
      signal: controller.signal,
      redirect: 'follow',
      headers: {
        accept: '*/*',
        'user-agent': 'trinity-accord-historical-content-recovery/1.0',
      },
    });
    if (!response.ok) throw Error(`HTTP ${response.status}`);
    const length = Number(response.headers.get('content-length') || 0);
    if (Number.isFinite(length) && length > MAX) throw Error(`content-length ${length}>${MAX}`);
    const data = Buffer.from(await response.arrayBuffer());
    if (!data.length) throw Error('empty body');
    if (data.length > MAX) throw Error(`body ${data.length}>${MAX}`);
    appendTrace(out, {
      event: 'http_content_received',
      root_cid: rootCid,
      endpoint_index: endpointIndex,
      url: response.url,
      content_type: response.headers.get('content-type') || null,
      bytes: data.length,
      sha256: sha256Hex(data),
    });
    return { data, finalUrl: response.url, contentType: response.headers.get('content-type') || null };
  } catch (error) {
    appendTrace(out, {
      event: 'http_content_failed',
      root_cid: rootCid,
      endpoint_index: endpointIndex,
      url,
      error: error?.name === 'AbortError' ? 'timeout' : String(error.message || error).slice(0, 500),
    });
    throw error;
  } finally {
    clearTimeout(timer);
  }
}

function orderedTopLevel(value, preferred) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return value;
  const out = {};
  for (const key of preferred) if (Object.prototype.hasOwnProperty.call(value, key)) out[key] = value[key];
  for (const key of Object.keys(value)) if (!Object.prototype.hasOwnProperty.call(out, key)) out[key] = value[key];
  return out;
}

function sortedKeys(value) {
  if (Array.isArray(value)) return value.map(sortedKeys);
  if (!value || typeof value !== 'object') return value;
  const out = {};
  for (const key of Object.keys(value).sort()) out[key] = sortedKeys(value[key]);
  return out;
}

function jsonAsciiString(value) {
  const quoted = JSON.stringify(String(value));
  let out = '"';
  for (const char of quoted.slice(1, -1)) {
    const cp = char.codePointAt(0);
    if (cp <= 0x7f) {
      out += char;
    } else if (cp <= 0xffff) {
      out += `\\u${cp.toString(16).padStart(4, '0')}`;
    } else {
      const n = cp - 0x10000;
      const hi = 0xd800 + (n >> 10);
      const lo = 0xdc00 + (n & 0x3ff);
      out += `\\u${hi.toString(16).padStart(4, '0')}\\u${lo.toString(16).padStart(4, '0')}`;
    }
  }
  return out + '"';
}

function jsonSpaced(value, ascii = false) {
  if (value === null) return 'null';
  if (typeof value === 'string') return ascii ? jsonAsciiString(value) : JSON.stringify(value);
  if (typeof value === 'number' || typeof value === 'boolean') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(item => jsonSpaced(item, ascii)).join(', ')}]`;
  if (value && typeof value === 'object') {
    return `{${Object.entries(value).map(([key, item]) =>
      `${ascii ? jsonAsciiString(key) : JSON.stringify(key)}: ${jsonSpaced(item, ascii)}`
    ).join(', ')}}`;
  }
  return JSON.stringify(value);
}

function asciiCompact(value) {
  if (value === null) return 'null';
  if (typeof value === 'string') return jsonAsciiString(value);
  if (typeof value === 'number' || typeof value === 'boolean') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(asciiCompact).join(',')}]`;
  if (value && typeof value === 'object') {
    return `{${Object.entries(value).map(([key, item]) =>
      `${jsonAsciiString(key)}:${asciiCompact(item)}`
    ).join(',')}}`;
  }
  return JSON.stringify(value);
}

function metadataCandidates(metadata) {
  if (!metadata || typeof metadata !== 'object') return [];
  const orderings = [
    ['snapshot_order', metadata],
    ['sorted_recursive', sortedKeys(metadata)],
    ['nft_common_name_description_image', orderedTopLevel(metadata, ['name', 'description', 'image', 'animation_url', 'external_url', 'attributes', 'properties'])],
    // Historical spam-airdrop metadata in the immutable v1 snapshot was serialized
    // by Python-style JSON with external_url before image. Preserve that exact
    // ordering as another candidate; acceptance still requires target CID equality.
    ['nft_common_name_description_external_image', orderedTopLevel(metadata, ['name', 'description', 'external_url', 'image', 'animation_url', 'attributes', 'properties'])],
    ['nft_common_name_image_description', orderedTopLevel(metadata, ['name', 'image', 'description', 'animation_url', 'external_url', 'attributes', 'properties'])],
  ];
  const out = [];
  const seen = new Set();
  const add = (label, text) => {
    const variants = [
      [label, text],
      [`${label}_lf`, `${text}\n`],
      [`${label}_crlf`, `${text}\r\n`],
    ];
    for (const [variant, body] of variants) {
      const data = Buffer.from(body, 'utf8');
      const key = sha256Hex(data);
      if (seen.has(key)) continue;
      seen.add(key);
      out.push({ variant, data });
    }
  };
  for (const [orderName, value] of orderings) {
    add(`${orderName}_compact`, JSON.stringify(value));
    add(`${orderName}_spaced`, jsonSpaced(value, false));
    add(`${orderName}_pretty2`, JSON.stringify(value, null, 2));
    add(`${orderName}_pretty4`, JSON.stringify(value, null, 4));
    add(`${orderName}_tabs`, JSON.stringify(value, null, '\t'));
    add(`${orderName}_ascii_compact`, asciiCompact(value));
    add(`${orderName}_ascii_spaced`, jsonSpaced(value, true));
  }
  return out;
}

function assetId(token) {
  return `eip155:${token.chain_id}/${String(token.standard || '').toLowerCase().replace('-', '')}:${token.contract}/${token.token_id}`;
}

async function mapLimit(items, limit, fn) {
  let next = 0;
  const workers = Array.from({ length: Math.min(limit, items.length) }, async () => {
    while (true) {
      const index = next++;
      if (index >= items.length) return;
      await fn(items[index], index);
    }
  });
  await Promise.all(workers);
}

async function recoverOneRoot({ out, kubo, rootCid, refRows, tokenByAsset, carDir }) {
  const carFile = path.join(carDir, `${rootCid}.car`);
  if (fs.existsSync(carFile)) {
    try {
      verifyCompleteCar(fs.readFileSync(carFile), rootCid);
      return { root_cid: rootCid, status: 'already_valid' };
    } catch {
      fs.rmSync(carFile, { force: true });
    }
  }

  const refs = [...refRows];
  const leafPaths = [...new Set(refs.map(ref => ref.leaf_path || null))];
  const gateways = contentGateways();
  const responseCandidates = [];
  const responseSeen = new Set();

  for (const leafPath of leafPaths) {
    const urls = gateways.map((gateway, i) => ({ url: gatewayUrl(gateway, rootCid, leafPath), i: i + 1, leafPath }));
    for (let start = 0; start < urls.length; start += 4) {
      const batch = urls.slice(start, start + 4);
      const results = await Promise.allSettled(batch.map(item =>
        fetchContent(item.url, rootCid, out, item.i).then(response => ({ ...item, ...response }))
      ));
      for (const result of results) {
        if (result.status !== 'fulfilled') continue;
        const key = `${result.value.leafPath || ''}:${sha256Hex(result.value.data)}`;
        if (responseSeen.has(key)) continue;
        responseSeen.add(key);
        responseCandidates.push(result.value);
      }
      // Try received bytes immediately before spending time on more gateways.
      for (const candidate of responseCandidates.splice(0)) {
        const exact = await exactCarFromBytes({
          kubo,
          rootCid,
          data: candidate.data,
          leafPath: candidate.leafPath,
          out,
          source: `http_gateway_${candidate.i}`,
          variantLabel: candidate.contentType || null,
        });
        if (!exact) continue;
        atomicWrite(carFile, exact.car);
        console.log(`[CAR HISTORICAL CONTENT RECOVERED] cid=${rootCid} method=${exact.method} endpoint=${candidate.i} bytes=${candidate.data.length} codec_hint=${rootCodecHint(rootCid)}`);
        appendTrace(out, {
          event: 'root_recovered',
          root_cid: rootCid,
          method: exact.method,
          importer: exact.importer,
          endpoint_index: candidate.i,
          source_url: candidate.finalUrl,
          bytes: candidate.data.length,
          sha256: sha256Hex(candidate.data),
        });
        return { root_cid: rootCid, status: 'recovered', source: 'http_gateway', method: exact.method, importer: exact.importer, endpoint_index: candidate.i };
      }
    }
  }

  // If the exact historical bytes are no longer available from gateways,
  // enumerate common historical JSON serializations. Acceptance still requires
  // exact root CID equality; this is reconstruction, not approximation.
  const metadataRefs = refs.filter(ref => ref.role === 'metadata');
  const metadataSeen = new Set();
  for (const ref of metadataRefs) {
    const token = tokenByAsset.get(ref.asset_id);
    for (const candidate of metadataCandidates(token?.metadata)) {
      const key = sha256Hex(candidate.data);
      if (metadataSeen.has(key)) continue;
      metadataSeen.add(key);
      const exact = await exactCarFromBytes({
        kubo,
        rootCid,
        data: candidate.data,
        leafPath: ref.leaf_path || null,
        out,
        source: 'metadata_serialization_matrix',
        variantLabel: candidate.variant,
      });
      if (!exact) continue;
      atomicWrite(carFile, exact.car);
      console.log(`[CAR HISTORICAL METADATA REBUILT] cid=${rootCid} method=${exact.method} variant=${candidate.variant} bytes=${candidate.data.length}`);
      appendTrace(out, {
        event: 'root_recovered',
        root_cid: rootCid,
        method: exact.method,
        importer: exact.importer,
        source: 'metadata_serialization_matrix',
        candidate_variant: candidate.variant,
        bytes: candidate.data.length,
        sha256: key,
      });
      return { root_cid: rootCid, status: 'recovered', source: 'metadata_serialization_matrix', method: exact.method, importer: exact.importer, variant: candidate.variant };
    }
  }

  appendTrace(out, {
    event: 'root_unrecovered',
    root_cid: rootCid,
    refs: refs.map(ref => ({ asset_id: ref.asset_id, role: ref.role, leaf_path: ref.leaf_path, original_uri: ref.original_uri })),
    http_gateway_count: gateways.length,
    metadata_candidate_count: metadataSeen.size,
  });
  return { root_cid: rootCid, status: 'unrecovered', http_gateway_count: gateways.length, metadata_candidate_count: metadataSeen.size };
}

async function extendedRecovery({ out, kubo, unrecovered }) {
  const snapshotFile = path.join(out, 'recovered-tokens.json');
  const carDir = path.join(out, 'evidence-v2', 'cars');
  if (!fs.existsSync(snapshotFile) || !unrecovered?.length) {
    return { attempted: 0, recovered: [], unrecovered: [] };
  }

  const records = JSON.parse(fs.readFileSync(snapshotFile, 'utf8'));
  const refs = refsFromSnapshot(out, records);
  const tokenByAsset = new Map(records.map(token => [assetId(token), token]));
  const targets = unrecovered
    .map(row => row?.root_cid)
    .filter(Boolean)
    .map(rootCid => ({ rootCid, refRows: refs.get(rootCid) || [] }));

  const results = new Array(targets.length);
  await mapLimit(targets, ROOT_CONCURRENCY, async (target, index) => {
    try {
      results[index] = await recoverOneRoot({
        out,
        kubo,
        rootCid: target.rootCid,
        refRows: target.refRows,
        tokenByAsset,
        carDir,
      });
    } catch (error) {
      console.warn(`[CAR HISTORICAL CONTENT ROOT FAILED] cid=${target.rootCid} error=${String(error.message || error).replace(/\s+/g, ' ').slice(0, 800)}`);
      appendTrace(out, {
        event: 'root_recovery_error',
        root_cid: target.rootCid,
        error: String(error.message || error).replace(/\s+/g, ' ').slice(0, 1200),
      });
      results[index] = { root_cid: target.rootCid, status: 'error', error: String(error.message || error).slice(0, 800) };
    }
  });

  const report = {
    schema: 'trinity-accord/chronicle-sidechain-historical-content-recovery/v1',
    generated_at: new Date().toISOString(),
    operational_only: true,
    acceptance_rule: 'exact target CID plus complete CAR verification only',
    attempted: targets.length,
    recovered: results.filter(row => row?.status === 'recovered'),
    unrecovered: results.filter(row => row?.status !== 'recovered' && row?.status !== 'already_valid'),
    results,
  };
  const reportFile = path.join(out, 'runtime', 'HISTORICAL-CONTENT-RECOVERY.json');
  atomicWrite(reportFile, Buffer.from(JSON.stringify(report, null, 2) + '\n'));
  console.log(`[CAR HISTORICAL CONTENT SUMMARY] attempted=${report.attempted} recovered=${report.recovered.length} unrecovered=${report.unrecovered.length}`);
  return report;
}

export async function rebuildCarsFromHistoricalPayloads(options = {}) {
  const out = options.out || process.env.CHRONICLE_OUT || 'artifacts/chronicle-sidechain-scan';
  const kubo = options.kubo || process.env.CHRONICLE_KUBO_BIN || '';
  const first = await baseRebuildCarsFromHistoricalPayloads({ ...options, out, kubo });
  if (!first.unrecovered?.length) return first;

  console.log(`[CAR HISTORICAL CONTENT START] unresolved=${first.unrecovered.length} strict=true`);
  const recovery = await extendedRecovery({ out, kubo, unrecovered: first.unrecovered });
  if (!recovery.recovered.length) return { ...first, extended_content_recovery: recovery };

  // Re-run the original strict scanner. Newly recovered CARs are accepted only
  // if the original verifier agrees they are complete and rooted at the exact CID.
  const second = await baseRebuildCarsFromHistoricalPayloads({ ...options, out, kubo });
  return { ...second, extended_content_recovery: recovery };
}

if (import.meta.url === `file://${process.argv[1]}`) {
  rebuildCarsFromHistoricalPayloads().catch(error => {
    console.error(error?.stack || error);
    process.exitCode = 1;
  });
}
