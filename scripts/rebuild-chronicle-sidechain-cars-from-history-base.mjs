#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import os from 'os';
import crypto from 'crypto';
import { execFile } from 'child_process';
import { promisify } from 'util';
import { cidSha256Digest, singleBlockCar } from './ipfs-car-blockwise.mjs';
import { verifyCompleteCar } from './chronicle-sidechain-car-integrity.mjs';

const execFileAsync = promisify(execFile);
const MAX = Number(process.env.CHRONICLE_CAR_MAX_BYTES || 157286400);

function sha256(buffer) {
  return crypto.createHash('sha256').update(buffer).digest();
}

function sha256Hex(buffer) {
  return crypto.createHash('sha256').update(buffer).digest('hex');
}

export function ipfsRef(uri) {
  if (typeof uri !== 'string' || !uri) return null;
  if (uri.startsWith('ipfs://')) {
    const parts = uri.slice(7).replace(/^ipfs\//, '').split('/');
    return { root_cid: parts.shift(), leaf_path: parts.join('/') || null };
  }
  try {
    const url = new URL(uri);
    const pathMatch = url.pathname.match(/\/ipfs\/([^/]+)(?:\/(.*))?$/);
    const subdomain = url.hostname.match(/^([^.]*)\.ipfs\./);
    if (pathMatch) return { root_cid: pathMatch[1], leaf_path: pathMatch[2] || null };
    if (subdomain) return { root_cid: subdomain[1], leaf_path: url.pathname.replace(/^\//, '') || null };
  } catch {}
  return null;
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

function safeName(value) {
  return String(value).replace(/[^A-Za-z0-9._-]/g, '_').slice(0, 180);
}

function safeExistingFile(out, declaredFile) {
  if (typeof declaredFile !== 'string' || !declaredFile) return null;
  const root = path.resolve(out);
  const file = path.resolve(declaredFile);
  if (file !== root && !file.startsWith(`${root}${path.sep}`)) return null;
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) return null;
  return file;
}

function addCandidate(out, list, file, source, details = {}) {
  const resolved = safeExistingFile(out, file);
  if (!resolved) return;
  const relative = path.relative(out, resolved).replaceAll('\\', '/');
  if (list.some(item => item.file === resolved)) return;
  list.push({ file: resolved, file_relative: relative, source, ...details });
}

function writeRuntimeCandidate(out, asset, role, variant, buffer) {
  const name = `${safeName(asset)}--${safeName(role)}--${safeName(variant)}--${sha256Hex(buffer).slice(0, 16)}.bin`;
  const file = path.join(out, 'runtime', 'historical-candidates', name);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  if (!fs.existsSync(file) || !fs.readFileSync(file).equals(buffer)) fs.writeFileSync(file, buffer);
  return file;
}

function localCandidates(out, token, asset, role, payload) {
  const candidates = [];
  const tokenDir = path.join(out, token.chain, token.contract, token.token_id);

  // Keep historical bytes whenever they actually exist, even if the old mirror
  // status field says failed/partial. The bytes themselves are still subjected
  // to exact-CID reconstruction and strict CAR verification below.
  addCandidate(out, candidates, payload?.file, 'declared_mirror_file', { payload_status: payload?.status || null });

  if (role === 'metadata') {
    addCandidate(out, candidates, path.join(tokenDir, 'metadata.bin'), 'deterministic_metadata_mirror');
    addCandidate(out, candidates, path.join(tokenDir, 'metadata.normalized.json'), 'normalized_metadata_file');
    if (token.metadata && typeof token.metadata === 'object') {
      const variants = [
        ['json_compact', Buffer.from(JSON.stringify(token.metadata), 'utf8')],
        ['json_compact_newline', Buffer.from(JSON.stringify(token.metadata) + '\n', 'utf8')],
        ['json_pretty2', Buffer.from(JSON.stringify(token.metadata, null, 2), 'utf8')],
        ['json_pretty2_newline', Buffer.from(JSON.stringify(token.metadata, null, 2) + '\n', 'utf8')],
      ];
      for (const [variant, buffer] of variants) {
        const file = writeRuntimeCandidate(out, asset, role, variant, buffer);
        addCandidate(out, candidates, file, 'synthesized_metadata', { variant });
      }
    }
  } else {
    addCandidate(out, candidates, path.join(tokenDir, `media-${safeName(role)}.bin`), 'deterministic_media_mirror');
  }
  return candidates;
}

export function refsFromSnapshot(out, records) {
  const byRoot = new Map();
  const add = (token, asset, role, uri, payload) => {
    const ref = ipfsRef(uri);
    if (!ref?.root_cid) return;
    const candidates = localCandidates(out, token, asset, role, payload);
    const row = {
      asset_id: asset,
      role,
      root_cid: ref.root_cid,
      leaf_path: ref.leaf_path,
      original_uri: uri,
      payload_status: payload?.status || null,
      declared_file: typeof payload?.file === 'string' ? payload.file : null,
      declared_file_exists: Boolean(safeExistingFile(out, payload?.file)),
      candidates,
    };
    const rows = byRoot.get(ref.root_cid) || [];
    const key = `${row.asset_id}|${row.role}|${row.leaf_path || ''}|${row.original_uri || ''}`;
    if (!rows.some(existing => `${existing.asset_id}|${existing.role}|${existing.leaf_path || ''}|${existing.original_uri || ''}` === key)) rows.push(row);
    byRoot.set(ref.root_cid, rows);
  };
  for (const token of records) {
    const asset = `eip155:${token.chain_id}/${String(token.standard || '').toLowerCase().replace('-', '')}:${token.contract}/${token.token_id}`;
    add(token, asset, 'metadata', token.token_uri?.uri || null, token.metadata_mirror);
    for (const media of token.media || []) {
      add(token, asset, media.role || 'media', media.original_uri || token.metadata?.[media.role] || null, media);
    }
  }
  return byRoot;
}

function flattenCandidates(refRows) {
  const out = [];
  const seen = new Set();
  for (const ref of refRows) {
    for (const candidate of ref.candidates || []) {
      const key = `${candidate.file}|${ref.leaf_path || ''}`;
      if (seen.has(key)) continue;
      seen.add(key);
      out.push({
        asset_id: ref.asset_id,
        role: ref.role,
        root_cid: ref.root_cid,
        leaf_path: ref.leaf_path,
        original_uri: ref.original_uri,
        payload_status: ref.payload_status,
        ...candidate,
      });
    }
  }
  return out;
}

function importerVariants(rootCid) {
  if (String(rootCid).startsWith('Qm')) {
    return [
      { cidVersion: 0, rawLeaves: false, chunker: 'size-262144', layout: 'balanced' },
      { cidVersion: 0, rawLeaves: false, chunker: 'size-1048576', layout: 'balanced' },
      { cidVersion: 0, rawLeaves: false, chunker: 'size-262144', layout: 'trickle' },
      { cidVersion: 0, rawLeaves: false, chunker: 'size-1048576', layout: 'trickle' },
    ];
  }
  return [
    { cidVersion: 1, rawLeaves: true, chunker: 'size-262144', layout: 'balanced' },
    { cidVersion: 1, rawLeaves: false, chunker: 'size-262144', layout: 'balanced' },
    { cidVersion: 1, rawLeaves: true, chunker: 'size-1048576', layout: 'balanced' },
    { cidVersion: 1, rawLeaves: false, chunker: 'size-1048576', layout: 'balanced' },
    { cidVersion: 1, rawLeaves: true, chunker: 'size-262144', layout: 'trickle' },
    { cidVersion: 1, rawLeaves: false, chunker: 'size-262144', layout: 'trickle' },
  ];
}

function addArgs(input, recursive, variant, onlyHash) {
  const args = ['add', '-Q', '--pin=false', `--cid-version=${variant.cidVersion}`, `--raw-leaves=${variant.rawLeaves ? 'true' : 'false'}`, `--chunker=${variant.chunker}`];
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
  const lines = String(stdout || '').trim().split(/\s+/).filter(Boolean);
  return lines.at(-1) || null;
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

function writeAtomic(file, buffer) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const tmp = `${file}.${process.pid}.${crypto.randomBytes(6).toString('hex')}.tmp`;
  fs.writeFileSync(tmp, buffer);
  fs.renameSync(tmp, file);
}

async function tryDirectRaw(rootCid, candidate) {
  if (candidate.leaf_path) return null;
  const data = fs.readFileSync(candidate.file);
  let digest;
  try { digest = cidSha256Digest(rootCid); } catch { return null; }
  if (!sha256(data).equals(digest)) return null;
  const car = singleBlockCar(rootCid, data);
  verifyCompleteCar(car, rootCid);
  return car;
}

async function tryKuboRebuild(kubo, rootCid, candidate) {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'chronicle-history-rebuild-'));
  try {
    let input = candidate.file;
    let recursive = false;
    const segments = safeLeafSegments(candidate.leaf_path);
    if (segments.length) {
      const tree = path.join(tmp, 'root');
      const target = path.join(tree, ...segments);
      fs.mkdirSync(path.dirname(target), { recursive: true });
      fs.copyFileSync(candidate.file, target);
      input = tree;
      recursive = true;
    }
    for (const variant of importerVariants(rootCid)) {
      let computed;
      try {
        computed = await kuboAddCid(kubo, input, recursive, variant, true);
      } catch (error) {
        console.warn(`[CAR HISTORICAL REBUILD HASH FAILED] cid=${rootCid} mode=v${variant.cidVersion}/raw=${variant.rawLeaves}/${variant.chunker}/${variant.layout} error=${String(error.message || error).replace(/\s+/g, ' ').slice(0, 300)}`);
        continue;
      }
      console.log(`[CAR HISTORICAL REBUILD HASH] cid=${rootCid} computed=${computed || 'none'} mode=v${variant.cidVersion}/raw=${variant.rawLeaves}/${variant.chunker}/${variant.layout} file=${candidate.file_relative} leaf=${candidate.leaf_path || '(root)'}`);
      if (computed !== rootCid) continue;
      const imported = await kuboAddCid(kubo, input, recursive, variant, false);
      if (imported !== rootCid) throw Error(`Kubo import drift expected=${rootCid} actual=${imported}`);
      const car = await exportCar(kubo, rootCid);
      console.log(`[CAR HISTORICAL ROOT REBUILT] cid=${rootCid} bytes=${car.length} mode=v${variant.cidVersion}/raw=${variant.rawLeaves}/${variant.chunker}/${variant.layout} file=${candidate.file_relative} leaf=${candidate.leaf_path || '(root)'}`);
      return car;
    }
    return null;
  } finally {
    fs.rmSync(tmp, { recursive: true, force: true });
  }
}

export async function rebuildCarsFromHistoricalPayloads({ out = process.env.CHRONICLE_OUT || 'artifacts/chronicle-sidechain-scan', kubo = process.env.CHRONICLE_KUBO_BIN || '' } = {}) {
  const snapshotFile = path.join(out, 'recovered-tokens.json');
  const carDir = path.join(out, 'evidence-v2', 'cars');
  const summary = {
    schema: 'trinity-accord/chronicle-sidechain-historical-car-rebuild/v2',
    started_at: new Date().toISOString(),
    roots_mapped: 0,
    refs_mapped: 0,
    roots_with_candidates: 0,
    roots_without_candidates: 0,
    roots_considered: 0,
    already_valid: 0,
    invalid_removed: 0,
    direct_raw_rebuilt: 0,
    kubo_rebuilt: 0,
    unrecovered: [],
    recovered: [],
  };
  if (!fs.existsSync(snapshotFile)) return summary;
  const records = JSON.parse(fs.readFileSync(snapshotFile, 'utf8'));
  const refs = refsFromSnapshot(out, records);
  summary.roots_mapped = refs.size;
  summary.refs_mapped = [...refs.values()].reduce((n, rows) => n + rows.length, 0);
  summary.roots_with_candidates = [...refs.values()].filter(rows => flattenCandidates(rows).length > 0).length;
  summary.roots_without_candidates = refs.size - summary.roots_with_candidates;
  summary.roots_considered = refs.size;
  fs.mkdirSync(carDir, { recursive: true });

  const rootMap = [...refs.entries()].map(([rootCid, rows]) => {
    const candidates = flattenCandidates(rows);
    return {
      root_cid: rootCid,
      ref_count: rows.length,
      candidate_count: candidates.length,
      refs: rows.map(row => ({
        asset_id: row.asset_id,
        role: row.role,
        leaf_path: row.leaf_path,
        original_uri: row.original_uri,
        payload_status: row.payload_status,
        declared_file: row.declared_file,
        declared_file_exists: row.declared_file_exists,
        candidates: row.candidates.map(candidate => ({
          source: candidate.source,
          file: candidate.file_relative,
          variant: candidate.variant || null,
          payload_status: candidate.payload_status || null,
        })),
      })),
    };
  });
  const rootMapFile = path.join(out, 'runtime', 'HISTORICAL-CAR-ROOT-MAP.json');
  fs.mkdirSync(path.dirname(rootMapFile), { recursive: true });
  fs.writeFileSync(rootMapFile, JSON.stringify({
    schema: 'trinity-accord/chronicle-sidechain-historical-car-root-map/v1',
    generated_at: new Date().toISOString(),
    roots: rootMap,
  }, null, 2) + '\n');
  console.log(`[CAR HISTORICAL ROOT MAP] roots=${summary.roots_mapped} refs=${summary.refs_mapped} with_candidates=${summary.roots_with_candidates} without_candidates=${summary.roots_without_candidates}`);

  for (const [rootCid, refRows] of refs) {
    const candidates = flattenCandidates(refRows);
    const carFile = path.join(carDir, `${rootCid}.car`);
    if (fs.existsSync(carFile)) {
      try {
        verifyCompleteCar(fs.readFileSync(carFile), rootCid);
        summary.already_valid++;
        continue;
      } catch (error) {
        fs.rmSync(carFile, { force: true });
        summary.invalid_removed++;
        console.warn(`[CAR HISTORICAL REBUILD INVALID CACHE] cid=${rootCid} error=${error.message || error}`);
      }
    }

    let rebuilt = null;
    let method = null;
    let used = null;
    for (const candidate of candidates) {
      try {
        rebuilt = await tryDirectRaw(rootCid, candidate);
        if (rebuilt) {
          method = 'direct_raw_payload';
          used = candidate;
          break;
        }
        if (kubo) {
          rebuilt = await tryKuboRebuild(kubo, rootCid, candidate);
          if (rebuilt) {
            method = 'kubo_unixfs_exact_root_match';
            used = candidate;
            break;
          }
        }
      } catch (error) {
        console.warn(`[CAR HISTORICAL REBUILD CANDIDATE FAILED] cid=${rootCid} file=${candidate.file_relative} leaf=${candidate.leaf_path || '(root)'} error=${String(error.message || error).replace(/\s+/g, ' ').slice(0, 500)}`);
      }
    }
    if (rebuilt) {
      verifyCompleteCar(rebuilt, rootCid);
      writeAtomic(carFile, rebuilt);
      if (method === 'direct_raw_payload') summary.direct_raw_rebuilt++;
      else summary.kubo_rebuilt++;
      const row = { root_cid: rootCid, method, bytes: rebuilt.length, file: used.file_relative, leaf_path: used.leaf_path, source: used.source };
      summary.recovered.push(row);
      console.log(`[CAR HISTORICAL REBUILD COMPLETE] cid=${rootCid} method=${method} bytes=${rebuilt.length}`);
    } else {
      summary.unrecovered.push({
        root_cid: rootCid,
        refs: refRows.map(ref => ({ asset_id: ref.asset_id, role: ref.role, leaf_path: ref.leaf_path, original_uri: ref.original_uri, payload_status: ref.payload_status })),
        candidates: candidates.map(x => ({ asset_id: x.asset_id, role: x.role, source: x.source, file: x.file_relative, leaf_path: x.leaf_path, variant: x.variant || null })),
      });
      console.warn(`[CAR HISTORICAL REBUILD MISS] cid=${rootCid} refs=${refRows.length} candidates=${candidates.length}`);
    }
  }
  summary.finished_at = new Date().toISOString();
  const report = path.join(out, 'runtime', 'HISTORICAL-CAR-REBUILD.json');
  fs.mkdirSync(path.dirname(report), { recursive: true });
  fs.writeFileSync(report, JSON.stringify(summary, null, 2) + '\n');
  console.log(`[CAR HISTORICAL REBUILD SUMMARY] mapped=${summary.roots_mapped} refs=${summary.refs_mapped} with_candidates=${summary.roots_with_candidates} without_candidates=${summary.roots_without_candidates} valid=${summary.already_valid} invalid_removed=${summary.invalid_removed} direct=${summary.direct_raw_rebuilt} kubo=${summary.kubo_rebuilt} unrecovered=${summary.unrecovered.length}`);
  return summary;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  rebuildCarsFromHistoricalPayloads().catch(error => {
    console.error(error?.stack || error);
    process.exitCode = 1;
  });
}
