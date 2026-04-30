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
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { execSync } from 'child_process';

// --------------- Config ---------------
const CONCURRENCY = Number(process.env.CONCURRENCY || getArg('--concurrency') || 10);
const MAX_RETRIES = Number(process.env.MAX_RETRIES || 3);
const DRY_RUN = process.env.DRY_RUN === '1';
const CAR_FILE = process.env.CAR_FILE || 'archive/evidence/nft-recovery-package/recovery-package.bin';
const RELEASE_TAG = process.env.RELEASE_TAG || 'nft-backup-v1';
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO = 'thechurchofagi/trinity-accord';

const GATEWAYS = [
  'https://arweave.net',
  'https://ar-io.net',
];

const TMP_DIR = '/tmp/nft-cars';
const PART_SIZE = 50; // files per archive part

// --------------- Helpers ---------------
function getArg(name) {
  const idx = process.argv.indexOf(name);
  return idx >= 0 && process.argv[idx + 1] ? process.argv[idx + 1] : null;
}

function sha256hex(buf) {
  return crypto.createHash('sha256').update(buf).digest('hex');
}

function parseCarHeader(data) {
  let pos = 0, shift = 0, headerLen = 0;
  while (true) {
    const b = data[pos];
    headerLen |= (b & 0x7f) << shift;
    pos++; shift += 7;
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
      const b = data[pos];
      blockLen |= (b & 0x7f) << shift;
      pos++; shift += 7;
      if (b < 0x80) break;
    }
    if (blockLen === 0 || pos + blockLen > data.length) break;
    yield { data: data.slice(pos, pos + blockLen), index: idx };
    pos += blockLen;
    idx++;
  }
}

function extractTokenIndex(carPath) {
  const raw = fs.readFileSync(carPath);
  for (const block of iterCarBlocks(raw)) {
    const jsonStart = block.data.indexOf(0x7b);
    if (jsonStart < 0) continue;
    let depth = 0;
    for (let i = jsonStart; i < block.data.length; i++) {
      if (block.data[i] === 0x7b) depth++;
      else if (block.data[i] === 0x7d) depth--;
      if (depth === 0) {
        try { return JSON.parse(block.data.slice(jsonStart, i + 1).toString()); }
        catch { break; }
      }
    }
  }
  throw new Error('token_index.json not found in CAR');
}

function collectTxids(index) {
  const txids = new Map();
  for (const [contract, tokens] of Object.entries(index)) {
    for (const [token_id, entry] of Object.entries(tokens)) {
      const meta = entry.metadata;
      if (meta?.txid) txids.set(meta.txid, { role: 'metadata', contract, token_id, cid: meta.root_cid, sha256: meta.car_sha256 });
      for (const m of entry.media || []) {
        if (m.txid) txids.set(m.txid, { role: 'media', contract, token_id, cid: m.root_cid, leaf: m.leaf_path, sha256: m.car_sha256 });
      }
    }
  }
  return txids;
}

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

  // Check if release exists
  const res = await fetch(`https://api.github.com/repos/${REPO}/releases/tags/${RELEASE_TAG}`, {
    headers: { Authorization: `Bearer ${GITHUB_TOKEN}`, Accept: 'application/vnd.github+json' },
  });

  if (res.ok) {
    const data = await res.json();
    console.log(`   Release ${RELEASE_TAG} exists (id: ${data.id})`);
    return data;
  }

  // Create release
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
      prerelease: false,
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

  if (!res.ok) throw new Error(`Upload ${filename} failed: ${res.status}`);
  const data = await res.json();
  console.log(`   ✅ Uploaded: ${filename} (${(stat.size / 1024 / 1024).toFixed(1)}MB)`);
  return data;
}

// --------------- Main ---------------
async function main() {
  console.log(`📦 NFT CAR Downloader → GitHub Release`);
  console.log(`   Source: ${CAR_FILE}`);
  console.log(`   Release: ${RELEASE_TAG}`);
  console.log(`   Concurrency: ${CONCURRENCY}`);
  console.log();

  // 1. Extract token index
  console.log('📖 Extracting token_index.json...');
  const index = extractTokenIndex(CAR_FILE);
  const contracts = Object.keys(index);
  const totalTokens = contracts.reduce((n, c) => n + Object.keys(index[c]).length, 0);
  console.log(`   ${totalTokens} NFTs, ${contracts.length} contracts`);

  // 2. Collect txids
  const txids = collectTxids(index);
  console.log(`   ${txids.size} unique txids`);
  console.log();

  if (DRY_RUN) {
    console.log('🔍 DRY RUN — would download:');
    for (const [txid, info] of txids) {
      console.log(`   ${txid}  ${info.role}  ${info.contract.slice(0, 10)}...`);
    }
    console.log(`\nTotal: ${txids.size} files`);
    return;
  }

  // 3. Download all CARs
  fs.mkdirSync(TMP_DIR, { recursive: true });
  const manifest = [];
  const txidList = [...txids.entries()];
  let done = 0, pass = 0, fail = 0;

  const tasks = txidList.map(([txid, info]) => async () => {
    const dest = path.join(TMP_DIR, `${txid}.car`);

    if (fs.existsSync(dest) && fs.statSync(dest).size > 0) {
      const hash = sha256hex(fs.readFileSync(dest));
      manifest.push({ ...info, txid, sha256: hash, size: fs.statSync(dest).size, cached: true });
      done++; pass++;
      return;
    }

    try {
      const buf = await downloadTxid(txid);
      const hash = sha256hex(buf);
      fs.writeFileSync(dest, buf);
      manifest.push({ ...info, txid, sha256: hash, size: buf.length });
      done++; pass++;
      if (done % 10 === 0) process.stdout.write(`\r   ${done}/${txids.size} downloaded`);
    } catch (err) {
      done++; fail++;
      manifest.push({ ...info, txid, error: err.message });
    }
  });

  await pool(tasks, CONCURRENCY);
  console.log(`\n   ✅ ${pass} downloaded, ❌ ${fail} failed`);

  // 4. Write manifest
  const manifestPath = path.join(TMP_DIR, 'manifest.json');
  fs.writeFileSync(manifestPath, JSON.stringify({
    timestamp: new Date().toISOString(),
    total: txids.size,
    downloaded: pass,
    failed: fail,
    contracts: contracts.length,
    nfts: totalTokens,
    files: manifest,
  }, null, 2));

  // 5. Package into tar.gz parts
  console.log('\n📦 Packaging into archives...');
  const carFiles = fs.readdirSync(TMP_DIR).filter(f => f.endsWith('.car')).sort();
  const parts = [];
  for (let i = 0; i < carFiles.length; i += PART_SIZE) {
    const batch = carFiles.slice(i, i + PART_SIZE);
    const partNum = Math.floor(i / PART_SIZE) + 1;
    const partName = `nft-cars-part${String(partNum).padStart(2, '0')}.tar.gz`;
    const partPath = path.join(TMP_DIR, partName);

    console.log(`   Part ${partNum}: ${batch.length} files → ${partName}`);
    execSync(`tar czf "${partPath}" -C "${TMP_DIR}" ${batch.join(' ')}`, { stdio: 'pipe' });
    parts.push({ name: partName, path: partPath, count: batch.length });
  }

  // Also package manifest
  const manifestTar = path.join(TMP_DIR, 'nft-cars-manifest.tar.gz');
  execSync(`tar czf "${manifestTar}" -C "${TMP_DIR}" manifest.json`, { stdio: 'pipe' });
  parts.push({ name: 'nft-cars-manifest.tar.gz', path: manifestTar, count: 1 });

  console.log(`\n   ${parts.length} archives created`);

  // 6. Upload to GitHub Release
  console.log('\n📤 Uploading to GitHub Release...');
  const release = await ensureRelease();

  for (const part of parts) {
    try {
      await uploadAsset(release.id, part.path, part.name);
    } catch (err) {
      console.error(`   ❌ Failed to upload ${part.name}: ${err.message}`);
    }
  }

  console.log('\n=========================================');
  console.log(`  ✅ Done! ${pass} CARs backed up to release ${RELEASE_TAG}`);
  console.log(`  📦 ${parts.length} archives uploaded`);
  console.log(`  📋 manifest.json included`);
  console.log('=========================================');
}

main().catch(err => {
  console.error('Fatal:', err);
  process.exit(1);
});
