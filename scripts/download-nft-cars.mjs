#!/usr/bin/env node
/**
 * download-nft-cars.mjs
 * 
 * Concurrent downloader for 175 NFT CAR files from Arweave.
 * Downloads all CARs, packages into tar.gz archives, uploads to GitHub Releases.
 * 
 * Usage:
 *   GITHUB_TOKEN=xxx node scripts/download-nft-cars.mjs [--concurrency 10]
 * 
 * Environment:
 *   CONCURRENCY    - max parallel downloads (default 10)
 *   MAX_RETRIES    - retry count per file (default 3)
 *   GITHUB_TOKEN   - GitHub PAT for release upload
 *   RELEASE_TAG    - release tag (default: nft-backup-v1)
 *   DRY_RUN        - set to "1" to only list txids without downloading
 *   CAR_FILE       - path to recovery-package.bin
 *   NFT_CARS_TMP_DIR - explicit tmp directory (will be cleaned on start)
 *   MAX_CAR_BYTES  - per-file size cap (default 500MB)
 *   MAX_TOTAL_BYTES - total verified size cap (default 10GB)
 */

import fs from 'fs';
import path from 'path';
import os from 'os';
import crypto from 'crypto';
import { execFileSync } from 'child_process';
import { fileURLToPath } from 'url';

// --------------- Config ---------------
function parsePositiveIntEnv(name, fallback, min, max) {
  const raw = process.env[name] || getArg(`--${name.toLowerCase()}`) || String(fallback);
  const n = Number(raw);
  if (!Number.isInteger(n) || n < min || n > max) {
    throw new Error(`Invalid ${name}: ${raw}. Must be integer ${min}-${max}.`);
  }
  return n;
}

const CONCURRENCY = parsePositiveIntEnv('CONCURRENCY', 10, 1, 25);
const MAX_RETRIES = parsePositiveIntEnv('MAX_RETRIES', 3, 0, 10);
const DRY_RUN = process.env.DRY_RUN === '1';
const CAR_FILE = process.env.CAR_FILE || 'archive/evidence/nft-recovery-package/recovery-package.bin';
const RELEASE_TAG = process.env.RELEASE_TAG || 'nft-backup-v1';
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO = 'thechurchofagi/trinity-accord';

const GATEWAYS = ['https://arweave.net', 'https://ar-io.net'];
const PART_SIZE = 50; // files per archive part

// --------------- Resource limits ---------------
const MAX_CAR_BYTES = parsePositiveIntEnv('MAX_CAR_BYTES', 500 * 1024 * 1024, 1, 5 * 1024 * 1024 * 1024);
const MAX_TOTAL_BYTES = parsePositiveIntEnv('MAX_TOTAL_BYTES', 10 * 1024 * 1024 * 1024, 1, 100 * 1024 * 1024 * 1024);

// --------------- TMP_DIR: unique or cleaned ---------------
const TMP_DIR = process.env.NFT_CARS_TMP_DIR
  ? (() => {
      // Explicit dir: clean and recreate
      fs.rmSync(process.env.NFT_CARS_TMP_DIR, { recursive: true, force: true });
      fs.mkdirSync(process.env.NFT_CARS_TMP_DIR, { recursive: true });
      return process.env.NFT_CARS_TMP_DIR;
    })()
  : fs.mkdtempSync(path.join(os.tmpdir(), 'nft-cars-'));

// --------------- Helpers ---------------
function getArg(name) {
  const idx = process.argv.indexOf(name);
  return idx >= 0 && process.argv[idx + 1] ? process.argv[idx + 1] : null;
}

function sha256hex(buf) {
  return crypto.createHash('sha256').update(buf).digest('hex');
}

const SHA256_RE = /^[a-f0-9]{64}$/i;

function normalizeExpectedSize(value) {
  if (typeof value === 'number' && Number.isSafeInteger(value) && value >= 0) return value;
  if (typeof value === 'string' && /^[0-9]+$/.test(value)) {
    const n = Number(value);
    if (Number.isSafeInteger(n) && n >= 0) return n;
  }
  return null;
}

function validateExpectedInfo(txid, info) {
  if (!txid || typeof txid !== 'string') {
    throw new Error(`Invalid txid: ${txid}`);
  }
  if (!info || typeof info !== 'object') {
    throw new Error(`Missing info for txid=${txid}`);
  }
  if (!SHA256_RE.test(info.sha256 || '')) {
    throw new Error(`Missing or invalid expected sha256 for txid=${txid}`);
  }

  const expectedSize = normalizeExpectedSize(info.size);
  if (expectedSize === null) {
    throw new Error(`Missing or invalid expected size for txid=${txid}`);
  }

  return {
    expected_sha256: String(info.sha256).toLowerCase(),
    expected_size: expectedSize,
    expected_cid: info.cid || null,
  };
}

function verifyDownloadedCarBuffer(txid, info, buf, source = 'download') {
  const expected = validateExpectedInfo(txid, info);
  const actualSha256 = sha256hex(buf);
  const actualSize = buf.length;

  // Per-file size cap
  if (actualSize > MAX_CAR_BYTES) {
    throw new Error(
      `CAR too large for txid=${txid}: ${actualSize} > ${MAX_CAR_BYTES}`
    );
  }

  // Expected size cap
  if (expected.expected_size > MAX_CAR_BYTES) {
    throw new Error(
      `Expected size exceeds per-file cap for txid=${txid}: ${expected.expected_size}`
    );
  }

  if (actualSha256 !== expected.expected_sha256) {
    throw new Error(
      `SHA256 mismatch for txid=${txid} source=${source}: expected=${expected.expected_sha256} actual=${actualSha256}`
    );
  }

  if (actualSize !== expected.expected_size) {
    throw new Error(
      `Size mismatch for txid=${txid} source=${source}: expected=${expected.expected_size} actual=${actualSize}`
    );
  }

  return {
    txid,
    role: info.role,
    contract: info.contract,
    token_id: info.token_id,
    cid: expected.expected_cid,
    leaf: info.leaf || null,

    expected_sha256: expected.expected_sha256,
    actual_sha256: actualSha256,
    sha256_match: true,

    expected_size: expected.expected_size,
    actual_size: actualSize,
    size_match: true,

    verified: true,
    cached: source === 'cache',
  };
}

function parseCarHeader(data) {
  let pos = 0, shift = 0, headerLen = 0;
  while (true) {
    const b = data[pos]; headerLen |= (b & 0x7f) << shift; pos++; shift += 7;
    if (b < 0x80) break;
  }
  return pos + headerLen;
}

function* iterCarBlocks(data) {
  let pos = parseCarHeader(data);
  let idx = 0;
  while (pos < data.length) {
    let shift = 0, blockLen = 0;
    while (pos < data.length) {
      const b = data[pos]; blockLen |= (b & 0x7f) << shift; pos++; shift += 7;
      if (b < 0x80) break;
    }
    if (blockLen === 0 || pos + blockLen > data.length) break;
    yield { data: data.slice(pos, pos + blockLen), index: idx };
    pos += blockLen; idx++;
  }
}

/** Extract token_index.json from the recovery CAR by finding the largest token-index JSON */
function extractTokenIndex(carPath) {
  const raw = fs.readFileSync(carPath);
  let bestObj = null;
  let bestKeyCount = 0;

  for (const block of iterCarBlocks(raw)) {
    let searchPos = 0;
    while (searchPos < block.data.length) {
      const jsonStart = block.data.indexOf(0x7b, searchPos);
      if (jsonStart < 0) break;

      let depth = 0, endPos = -1;
      for (let i = jsonStart; i < block.data.length; i++) {
        if (block.data[i] === 0x7b) depth++;
        else if (block.data[i] === 0x7d) depth--;
        if (depth === 0) { endPos = i; break; }
      }

      if (endPos > jsonStart) {
        try {
          const obj = JSON.parse(block.data.slice(jsonStart, endPos + 1).toString());
          if (typeof obj === 'object' && !Array.isArray(obj)) {
            const keys = Object.keys(obj);
            const isTokenIndex = keys.some(k => {
              const v = obj[k];
              if (typeof v !== 'object' || v === null || Array.isArray(v)) return false;
              return Object.values(v).some(t =>
                t && typeof t === 'object' && (t.metadata || t.media)
              );
            });
            if (isTokenIndex && keys.length > bestKeyCount) {
              bestObj = obj;
              bestKeyCount = keys.length;
            }
          }
        } catch {}
        searchPos = endPos + 1;
      } else {
        searchPos = jsonStart + 1;
      }
    }
  }

  if (bestObj) return bestObj;
  throw new Error('token_index.json not found in CAR');
}

/** Collect all unique txids from token_index */
function collectTxids(index) {
  const txids = new Map();
  for (const [contract, tokens] of Object.entries(index)) {
    for (const [token_id, entry] of Object.entries(tokens)) {
      const meta = entry.metadata;
      if (meta?.txid) {
        txids.set(meta.txid, {
          role: 'metadata', contract, token_id,
          cid: meta.root_cid, sha256: meta.car_sha256, size: meta.car_size,
        });
      }
      for (const m of entry.media || []) {
        if (m.txid) {
          txids.set(m.txid, {
            role: 'media', contract, token_id,
            cid: m.root_cid, leaf: m.leaf_path, sha256: m.car_sha256, size: m.car_size,
          });
        }
      }
    }
  }
  return txids;
}

/** Download with gateway rotation + retries */
async function downloadTxid(txid, retries = MAX_RETRIES) {
  for (let attempt = 0; attempt <= retries; attempt++) {
    const gw = GATEWAYS[attempt % GATEWAYS.length];
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 120_000);
      const res = await fetch(`${gw}/${txid}`, { signal: controller.signal });
      clearTimeout(timeout);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return Buffer.from(await res.arrayBuffer());
    } catch (err) {
      if (attempt === retries) throw err;
      await sleep(1000 * (attempt + 1));
    }
  }
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

/** Run async tasks with concurrency limit */
async function pool(tasks, limit) {
  const results = [];
  let i = 0;
  const workers = Array.from({ length: limit }, async () => {
    while (i < tasks.length) {
      const idx = i++;
      results[idx] = await tasks[idx]();
    }
  });
  await Promise.all(workers);
  return results;
}

// --------------- GitHub Release ---------------
async function ensureRelease() {
  if (!GITHUB_TOKEN) throw new Error('GITHUB_TOKEN required for release upload');

  const res = await fetch(`https://api.github.com/repos/${REPO}/releases/tags/${RELEASE_TAG}`, {
    headers: { Authorization: `Bearer ${GITHUB_TOKEN}`, Accept: 'application/vnd.github+json' },
  });

  if (res.ok) {
    const data = await res.json();
    console.log(`   Release ${RELEASE_TAG} exists (id: ${data.id})`);
    return data;
  }

  console.log(`   Creating release ${RELEASE_TAG}...`);
  const create = await fetch(`https://api.github.com/repos/${REPO}/releases`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${GITHUB_TOKEN}`,
      Accept: 'application/vnd.github+json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      tag_name: RELEASE_TAG,
      name: `NFT Backup - 175 NFTs (Arweave CAR Files)`,
      body: `## NFT Recovery CAR Files\n\nBackup of 175 Ethereum NFT metadata and media as IPFS CAR files from Arweave.\n\nSee \`token_index.json\` in the main repo for the mapping of contract+token_id → Arweave txid.\n\nGenerated: ${new Date().toISOString()}`,
    }),
  });

  if (!create.ok) throw new Error(`Create release failed: ${create.status} ${await create.text()}`);
  const data = await create.json();
  console.log(`   Release created (id: ${data.id})`);
  return data;
}

async function uploadAsset(releaseId, filePath, filename) {
  const buf = fs.readFileSync(filePath);
  const url = `https://uploads.github.com/repos/${REPO}/releases/${releaseId}/assets?name=${encodeURIComponent(filename)}`;

  const res = await fetch(url, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${GITHUB_TOKEN}`,
      'Content-Type': 'application/gzip',
      'Content-Length': buf.length.toString(),
    },
    body: buf,
  });

  if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
  console.log(`   ✅ Uploaded: ${filename} (${(buf.length / 1024 / 1024).toFixed(1)}MB)`);
}

// --------------- Main ---------------
async function main() {
  console.log(`📦 NFT CAR Downloader → GitHub Release`);
  console.log(`   Source: ${CAR_FILE}`);
  console.log(`   Release: ${RELEASE_TAG}`);
  console.log(`   Concurrency: ${CONCURRENCY}`);
  console.log(`   TMP_DIR: ${TMP_DIR}`);
  console.log(`   MAX_CAR_BYTES: ${(MAX_CAR_BYTES / 1024 / 1024).toFixed(0)}MB`);
  console.log(`   MAX_TOTAL_BYTES: ${(MAX_TOTAL_BYTES / 1024 / 1024 / 1024).toFixed(1)}GB`);
  console.log();

  // 1. Extract token index
  console.log('📖 Extracting token_index.json...');
  const index = extractTokenIndex(CAR_FILE);
  const contracts = Object.keys(index);
  const totalTokens = contracts.reduce((n, c) => n + Object.keys(index[c]).length, 0);
  console.log(`   ${totalTokens} NFTs, ${contracts.length} contracts`);

  // 2. Collect txids
  const txids = collectTxids(index);
  console.log(`   ${txids.size} unique txids to download`);
  console.log();

  if (DRY_RUN) {
    console.log('🔍 DRY RUN — listing txids:');
    for (const [txid, info] of txids) {
      console.log(`   ${txid}  ${info.role}  ${info.contract.slice(0, 10)}.../${info.token_id.slice(0, 20)}...`);
    }
    console.log(`\nTotal: ${txids.size} files`);
    return;
  }

  // 3. Download all CARs
  fs.mkdirSync(TMP_DIR, { recursive: true });
  const manifest = [];
  const verifiedCarFiles = [];
  const txidList = [...txids.entries()];
  let done = 0, pass = 0, fail = 0;
  let totalVerifiedBytes = 0;

  const tasks = txidList.map(([txid, info]) => async () => {
    const dest = path.join(TMP_DIR, `${txid}.car`);

    // Cache path: must verify expected hash/size before trusting
    if (fs.existsSync(dest) && fs.statSync(dest).size > 0) {
      try {
        const cachedBuf = fs.readFileSync(dest);
        const verified = verifyDownloadedCarBuffer(txid, info, cachedBuf, 'cache');

        // Total size cap check
        totalVerifiedBytes += verified.actual_size;
        if (totalVerifiedBytes > MAX_TOTAL_BYTES) {
          throw new Error(`Total CAR verified size exceeds cap: ${totalVerifiedBytes} > ${MAX_TOTAL_BYTES}`);
        }

        manifest.push(verified);
        verifiedCarFiles.push({ txid, path: dest, manifest_item: verified });
        done++; pass++;
        if (done % 50 === 0) process.stdout.write(`\r   ${done}/${txids.size}`);
        return;
      } catch (err) {
        // Stale or corrupted cache: delete and re-download
        fs.rmSync(dest, { force: true });
      }
    }

    try {
      const buf = await downloadTxid(txid);
      const verified = verifyDownloadedCarBuffer(txid, info, buf, 'download');

      // Total size cap check
      totalVerifiedBytes += verified.actual_size;
      if (totalVerifiedBytes > MAX_TOTAL_BYTES) {
        throw new Error(`Total CAR verified size exceeds cap: ${totalVerifiedBytes} > ${MAX_TOTAL_BYTES}`);
      }

      fs.writeFileSync(dest, buf);
      manifest.push(verified);
      verifiedCarFiles.push({ txid, path: dest, manifest_item: verified });

      done++; pass++;
      if (done % 10 === 0) process.stdout.write(`\r   ${done}/${txids.size} downloaded`);
    } catch (err) {
      done++; fail++;
      manifest.push({
        txid,
        role: info.role,
        contract: info.contract,
        token_id: info.token_id,
        expected_sha256: info.sha256 || null,
        expected_size: info.size ?? null,
        error: err.message,
        verified: false,
      });
    }
  });

  await pool(tasks, CONCURRENCY);
  console.log(`\n   ✅ ${pass} downloaded, ❌ ${fail} failed`);

  if (fail > 0) {
    throw new Error(`${fail} CAR downloads failed; refusing to package or upload incomplete backup`);
  }

  // 4. Aggregate manifest checks
  const sha256Pass = manifest.filter(x => x.sha256_match === true).length;
  const sizePass = manifest.filter(x => x.size_match === true).length;
  const allVerified = fail === 0 && pass === txids.size && sha256Pass === txids.size && sizePass === txids.size;

  if (!allVerified) {
    throw new Error(`Not all files verified: sha256_pass=${sha256Pass}/${txids.size} size_pass=${sizePass}/${txids.size}`);
  }

  // 5. Write manifest
  const manifestPath = path.join(TMP_DIR, 'manifest.json');
  fs.writeFileSync(manifestPath, JSON.stringify({
    timestamp: new Date().toISOString(),
    total_txids: txids.size,
    downloaded: pass,
    failed: fail,
    verified: pass,
    sha256_check: { pass: sha256Pass, total: txids.size },
    size_check: { pass: sizePass, total: txids.size },
    all_expected_sha256_matched: sha256Pass === txids.size,
    all_expected_size_matched: sizePass === txids.size,
    all_verified: allVerified,
    contracts: contracts.length,
    nfts: totalTokens,
    files: manifest,
  }, null, 2));

  // 6. Package into tar.gz parts — ONLY verified files
  console.log('\n📦 Packaging into archives...');

  if (verifiedCarFiles.length !== txids.size) {
    throw new Error(`Verified CAR count mismatch: expected=${txids.size} actual=${verifiedCarFiles.length}`);
  }

  const parts = [];
  for (let i = 0; i < verifiedCarFiles.length; i += PART_SIZE) {
    const batch = verifiedCarFiles.slice(i, i + PART_SIZE);
    const partNum = Math.floor(i / PART_SIZE) + 1;
    const partName = `nft-cars-part${String(partNum).padStart(2, '0')}.tar.gz`;
    const partPath = path.join(TMP_DIR, partName);

    console.log(`   Part ${partNum}: ${batch.length} files → ${partName}`);
    const listFile = path.join(TMP_DIR, `.part${partNum}.txt`);
    fs.writeFileSync(listFile, batch.map(x => `./${path.basename(x.path)}`).join('\n'));
    execFileSync('tar', ['czf', partPath, '-C', TMP_DIR, '-T', listFile], { stdio: 'pipe' });
    fs.unlinkSync(listFile);
    parts.push({
      name: partName,
      path: partPath,
      count: batch.length,
      files: batch.map(x => ({
        txid: x.txid,
        tar_path: path.basename(x.path),
        manifest_item: x.manifest_item,
      })),
    });
  }

  // Also package manifest
  const manifestTar = path.join(TMP_DIR, 'nft-cars-manifest.tar.gz');
  execFileSync('tar', ['czf', manifestTar, '-C', TMP_DIR, 'manifest.json'], { stdio: 'pipe' });
  parts.push({ name: 'nft-cars-manifest.tar.gz', path: manifestTar, count: 1 });

  console.log(`\n   ${parts.length} archives created`);

  // 7. Build and write RELEASE-MANIFEST.json (trinity-release-manifest-v1, part-based)
  console.log('\n📄 Building RELEASE-MANIFEST.json...');

  const releaseAssets = parts
    .filter(p => p.name !== 'nft-cars-manifest.tar.gz')
    .map(part => ({
      asset_name: part.name,
      files: part.files.map(f => ({
        role: f.manifest_item.role,
        contract: f.manifest_item.contract || null,
        token_id: f.manifest_item.token_id || null,
        txid: f.txid,
        expected_path: f.tar_path,
        expected_sha256: f.manifest_item.expected_sha256,
        expected_size: f.manifest_item.expected_size,
        expected_root_cid: f.manifest_item.cid || null,
        cid_check_required: false,
      })),
    }));

  const totalCarFiles = releaseAssets.reduce((sum, a) => sum + a.files.length, 0);

  const releaseManifest = {
    schema: 'trinity-release-manifest-v1',
    release_kind: 'nft-car-backup-parts',
    verification_basis: 'expected_sha256_and_expected_size',
    actual_nfts: totalTokens,
    total_car_files: totalCarFiles,
    contracts: contracts.length,
    source_manifest: { generator: 'scripts/download-nft-cars.mjs' },
    release_assets: releaseAssets,
    auxiliary_assets: ['nft-cars-manifest.tar.gz', 'RELEASE-MANIFEST.json'],
    does_not_prove: [
      'independent attestation',
      'on-chain ownership or tokenURI correctness',
      'physical authorship or provenance',
      'CID/root/DAG correctness unless verify-release-assets.mjs is run with --cid-check',
      'full evidence chain verification',
    ],
  };

  const releaseManifestPath = path.join(TMP_DIR, 'RELEASE-MANIFEST.json');
  fs.writeFileSync(releaseManifestPath, JSON.stringify(releaseManifest, null, 2));
  console.log(`   ✅ RELEASE-MANIFEST.json written (${releaseAssets.length} parts, ${totalCarFiles} CARs)`);

  // 8. Upload to GitHub Release
  console.log('\n📤 Uploading to GitHub Release...');
  const release = await ensureRelease();

  let uploadFail = 0;

  // Upload RELEASE-MANIFEST.json first
  try {
    await uploadAsset(release.id, releaseManifestPath, 'RELEASE-MANIFEST.json');
  } catch (err) {
    uploadFail++;
    console.error(`   ❌ Failed to upload RELEASE-MANIFEST.json: ${err.message}`);
  }

  for (const part of parts) {
    try {
      await uploadAsset(release.id, part.path, part.name);
    } catch (err) {
      uploadFail++;
      console.error(`   ❌ Failed to upload ${part.name}: ${err.message}`);
    }
  }

  if (uploadFail > 0) {
    throw new Error(`${uploadFail} release asset uploads failed`);
  }

  console.log('\n=========================================');
  console.log(`  ✅ Done! ${pass} CARs backed up to release ${RELEASE_TAG}`);
  console.log(`  📦 ${parts.length} archives uploaded`);
  console.log(`  📋 RELEASE-MANIFEST.json uploaded`);
  console.log('=========================================');
}

const isMain = process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1]);

if (isMain) {
  main().catch(err => {
    console.error('Fatal:', err);
    process.exit(1);
  });
}

export {
  normalizeExpectedSize,
  validateExpectedInfo,
  verifyDownloadedCarBuffer,
  sha256hex,
};
