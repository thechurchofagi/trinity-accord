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

function ipfsRef(uri) {
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

function historicalFile(out, payload) {
  if (!payload || payload.status !== 'ok' || typeof payload.file !== 'string') return null;
  const root = path.resolve(out);
  const file = path.resolve(payload.file);
  if (file !== root && !file.startsWith(`${root}${path.sep}`)) return null;
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) return null;
  return file;
}

function refsFromSnapshot(out, records) {
  const byRoot = new Map();
  const add = (asset, role, uri, payload) => {
    const ref = ipfsRef(uri);
    const file = historicalFile(out, payload);
    if (!ref?.root_cid || !file) return;
    const row = {
      asset_id: asset,
      role,
      root_cid: ref.root_cid,
      leaf_path: ref.leaf_path,
      file,
      file_relative: path.relative(out, file).replaceAll('\\', '/'),
    };
    const rows = byRoot.get(ref.root_cid) || [];
    if (!rows.some(existing => existing.file === row.file && existing.leaf_path === row.leaf_path)) rows.push(row);
    byRoot.set(ref.root_cid, rows);
  };
  for (const token of records) {
    const asset = `eip155:${token.chain_id}/${String(token.standard || '').toLowerCase().replace('-', '')}:${token.contract}/${token.token_id}`;
    add(asset, 'metadata', token.token_uri?.uri || null, token.metadata_mirror);
    for (const media of token.media || []) {
      add(asset, media.role || 'media', media.original_uri || token.metadata?.[media.role] || null, media);
    }
  }
  return byRoot;
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
    schema: 'trinity-accord/chronicle-sidechain-historical-car-rebuild/v1',
    started_at: new Date().toISOString(),
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
  summary.roots_considered = refs.size;
  fs.mkdirSync(carDir, { recursive: true });

  for (const [rootCid, candidates] of refs) {
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
      const row = { root_cid: rootCid, method, bytes: rebuilt.length, file: used.file_relative, leaf_path: used.leaf_path };
      summary.recovered.push(row);
      console.log(`[CAR HISTORICAL REBUILD COMPLETE] cid=${rootCid} method=${method} bytes=${rebuilt.length}`);
    } else {
      summary.unrecovered.push({ root_cid: rootCid, candidates: candidates.map(x => ({ asset_id: x.asset_id, role: x.role, file: x.file_relative, leaf_path: x.leaf_path })) });
      console.warn(`[CAR HISTORICAL REBUILD MISS] cid=${rootCid} candidates=${candidates.length}`);
    }
  }
  summary.finished_at = new Date().toISOString();
  const report = path.join(out, 'runtime', 'HISTORICAL-CAR-REBUILD.json');
  fs.mkdirSync(path.dirname(report), { recursive: true });
  fs.writeFileSync(report, JSON.stringify(summary, null, 2) + '\n');
  console.log(`[CAR HISTORICAL REBUILD SUMMARY] roots=${summary.roots_considered} valid=${summary.already_valid} invalid_removed=${summary.invalid_removed} direct=${summary.direct_raw_rebuilt} kubo=${summary.kubo_rebuilt} unrecovered=${summary.unrecovered.length}`);
  return summary;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  rebuildCarsFromHistoricalPayloads().catch(error => {
    console.error(error?.stack || error);
    process.exitCode = 1;
  });
}
