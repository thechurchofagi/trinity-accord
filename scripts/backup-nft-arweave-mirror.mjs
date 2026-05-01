#!/usr/bin/env node
/**
 * backup-nft-arweave-mirror.mjs  (v5 — backup only, no onchain verification)
 *
 * Arweave → GitHub Release mirror for 175 NFTs.
 * Scope: download CARs from Arweave, verify sha256 + size against token_index,
 *        package into per-NFT tars, upload to GitHub Release.
 *
 * Does NOT verify root CIDs. Does NOT touch ETH chain.
 * For root CID / onchain verification, use separate scripts:
 *   - verify-release-assets.mjs   (release-level re-verification)
 *   - verify-onchain-tokenuri.mjs (ETH onchain tokenURI audit)
 *
 * Usage:
 *   GITHUB_TOKEN=xxx node scripts/backup-nft-arweave-mirror.mjs [--dry-run] [--contract 0x...]
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { execSync } from 'child_process';

// ─── Config ────────────────────────────────────────────────────────────────

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO = process.env.REPO || 'thechurchofagi/trinity-accord';
const RELEASE_TAG = process.env.RELEASE_TAG || 'nft-arweave-mirror-175-v1';
const TOKEN_INDEX_FILE = 'token_index.json';
const TMP_DIR = '/tmp/nft-arweave-mirror';
const GATEWAYS = ['https://arweave.net', 'https://ar-io.net'];
const EXPECTED_NFTS = 175;
const MAX_RETRIES = 3;
const DOWNLOAD_CONCURRENCY = 5;
const UPLOAD_CONCURRENCY = 2;

// ─── Helpers ───────────────────────────────────────────────────────────────

function sha256hex(buf) {
  return crypto.createHash('sha256').update(buf).digest('hex');
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
function log(msg) { console.log(msg); }
function err(msg) { console.error(msg); }

// ─── Concurrency pool ──────────────────────────────────────────────────────

async function runConcurrent(tasks, limit) {
  const results = new Array(tasks.length);
  let nextIdx = 0;
  async function worker() {
    while (nextIdx < tasks.length) {
      const idx = nextIdx++;
      try { results[idx] = await tasks[idx](); }
      catch (e) { results[idx] = e; }
    }
  }
  const workers = Array.from({ length: Math.min(limit, tasks.length) }, () => worker());
  await Promise.all(workers);
  return results;
}

// ─── Arweave download ──────────────────────────────────────────────────────

async function downloadTxid(txid, destPath, retries = MAX_RETRIES) {
  for (let attempt = 0; attempt <= retries; attempt++) {
    const gw = GATEWAYS[attempt % GATEWAYS.length];
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 180_000);
      const res = await fetch(`${gw}/${txid}`, { signal: controller.signal });
      clearTimeout(timeout);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const buf = Buffer.from(await res.arrayBuffer());
      fs.writeFileSync(destPath, buf);
      return buf;
    } catch (fetchErr) {
      if (attempt === retries) throw fetchErr;
      await sleep(2000 * (attempt + 1));
    }
  }
}

// ─── GitHub helpers ────────────────────────────────────────────────────────

function ghHeaders(extra = {}) {
  return { Authorization: `Bearer ${GITHUB_TOKEN}`, Accept: 'application/vnd.github+json', ...extra };
}

async function ensureRelease() {
  const res = await fetch(
    `https://api.github.com/repos/${REPO}/releases/tags/${RELEASE_TAG}`,
    { headers: ghHeaders() }
  );
  if (res.ok) {
    const rel = await res.json();
    log(`  Release ${RELEASE_TAG} exists (id: ${rel.id})`);
    return rel;
  }
  log(`  Creating release ${RELEASE_TAG}...`);
  const create = await fetch(`https://api.github.com/repos/${REPO}/releases`, {
    method: 'POST',
    headers: ghHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({
      tag_name: RELEASE_TAG,
      name: `NFT Arweave Mirror — 175 NFTs (v5, hash+size verified)`,
      body: [
        `## Arweave → GitHub Release Mirror (v5)`,
        ``,
        `175 individual NFT archives.`,
        `Verification scope: sha256 + size against token_index.json.`,
        `No root CID verification. No onchain verification.`,
        ``,
        `For root CID / onchain verification see separate release assets.`,
        ``,
        `Generated: ${new Date().toISOString()}`,
      ].join('\n'),
    }),
  });
  if (!create.ok) throw new Error(`Create release failed: ${create.status} ${await create.text()}`);
  return await create.json();
}

async function getAllAssets(releaseId) {
  const assets = new Map();
  let page = 1;
  while (true) {
    const res = await fetch(
      `https://api.github.com/repos/${REPO}/releases/${releaseId}/assets?per_page=100&page=${page}`,
      { headers: ghHeaders() }
    );
    if (!res.ok) break;
    const batch = await res.json();
    if (!batch.length) break;
    for (const a of batch) assets.set(a.name, a);
    page++;
  }
  return assets;
}

async function uploadAsset(releaseId, filePath, filename) {
  const buf = fs.readFileSync(filePath);
  const url = `https://uploads.github.com/repos/${REPO}/releases/${releaseId}/assets?name=${encodeURIComponent(filename)}`;
  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${GITHUB_TOKEN}`,
        'Content-Type': 'application/x-tar',
        'Content-Length': buf.length.toString(),
      },
      body: buf,
    });
    if (res.ok) {
      const asset = await res.json();
      return { status: 'uploaded', id: asset.id, size: asset.size };
    }
    if (res.status === 422) {
      log(`    ⚠️  422 on attempt ${attempt + 1}, retrying...`);
      await sleep(3000 * (attempt + 1));
      continue;
    }
    if (res.status === 403 || res.status === 429) {
      log(`    ⚠️  Rate limited (${res.status}), waiting 60s...`);
      await sleep(60000);
      continue;
    }
    throw new Error(`Upload failed: ${res.status} ${await res.text()}`);
  }
  throw new Error(`Upload failed after ${MAX_RETRIES} attempts`);
}

async function deleteAsset(releaseId, assetId) {
  const res = await fetch(
    `https://api.github.com/repos/${REPO}/releases/assets/${assetId}`,
    { method: 'DELETE', headers: ghHeaders() }
  );
  if (!res.ok && res.status !== 404) {
    throw new Error(`Delete asset failed: ${res.status}`);
  }
}

// ─── Tar creation (pure Node.js) ───────────────────────────────────────────

function createTar(files) {
  const blocks = [];
  for (const { name, data } of files) {
    const header = Buffer.alloc(512);
    header.write(name, 0, Math.min(name.length, 100), 'utf-8');
    header.write('0000644\0', 100, 8, 'utf-8');
    header.write('0000000\0', 108, 8, 'utf-8');
    header.write('0000000\0', 116, 8, 'utf-8');
    const sizeOctal = data.length.toString(8).padStart(11, '0') + '\0';
    header.write(sizeOctal, 124, 12, 'utf-8');
    const mtimeOctal = Math.floor(Date.now() / 1000).toString(8).padStart(11, '0') + '\0';
    header.write(mtimeOctal, 136, 12, 'utf-8');
    header.write('0', 156, 1, 'utf-8');
    header.write('ustar\0', 257, 6, 'utf-8');
    header.write('00', 263, 2, 'utf-8');
    header.fill(32, 148, 156);
    let chksum = 0;
    for (let i = 0; i < 512; i++) chksum += header[i];
    header.write(chksum.toString(8).padStart(6, '0') + '\0 ', 148, 8, 'utf-8');
    blocks.push(header);
    const paddedSize = Math.ceil(data.length / 512) * 512;
    const dataBlock = Buffer.alloc(paddedSize);
    data.copy(dataBlock);
    blocks.push(dataBlock);
  }
  blocks.push(Buffer.alloc(512));
  blocks.push(Buffer.alloc(512));
  return Buffer.concat(blocks);
}

// ─── Main ──────────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  const dryRun = args.includes('--dry-run');
  const contractFilter = args.includes('--contract') ? args[args.indexOf('--contract') + 1] : null;

  let sourceCommit = 'unknown';
  try { sourceCommit = execSync('git rev-parse HEAD', { encoding: 'utf-8' }).trim(); } catch {}

  log('═══════════════════════════════════════════════════════════');
  log('  NFT Arweave → GitHub Release Mirror (v5 — backup only)');
  log('═══════════════════════════════════════════════════════════');
  log(`  Token Index: ${TOKEN_INDEX_FILE}`);
  log(`  Release    : ${RELEASE_TAG}`);
  log(`  Concurrency: dl=${DOWNLOAD_CONCURRENCY}, ul=${UPLOAD_CONCURRENCY}`);
  log(`  Commit     : ${sourceCommit}`);
  log('');

  // ── Step 1: Load token_index.json ───────────────────────────────────

  log('📖 Step 1: Loading token_index.json...');
  const index = JSON.parse(fs.readFileSync(TOKEN_INDEX_FILE, 'utf-8'));
  const allContracts = Object.keys(index);
  const contracts = contractFilter ? [contractFilter] : allContracts;

  let totalNfts = 0;
  for (const c of contracts) {
    if (!index[c]) { err(`  ❌ Contract ${c} not found`); process.exit(1); }
    totalNfts += Object.keys(index[c]).length;
  }
  log(`  ${contracts.length} contracts, ${totalNfts} NFTs`);

  if (totalNfts !== EXPECTED_NFTS && !contractFilter) {
    err(`  ❌ Expected ${EXPECTED_NFTS} NFTs, found ${totalNfts}`);
    process.exit(1);
  }

  // Build NFT list
  const nftList = [];
  const allTxids = new Set();
  let totalCars = 0;

  for (const contract of contracts) {
    for (const [tokenId, entry] of Object.entries(index[contract])) {
      const files = [];
      const meta = entry.metadata || {};
      if (meta.txid) {
        files.push({
          role: 'metadata',
          txid: meta.txid,
          expected_sha256: meta.car_sha256,
          expected_size: meta.car_size,
          expected_root_cid: meta.root_cid,
          leaf_path: null,
          match: null,
        });
        allTxids.add(meta.txid);
        totalCars++;
      }
      for (let i = 0; i < (entry.media || []).length; i++) {
        const m = entry.media[i];
        if (m.txid) {
          files.push({
            role: `media-${String(i).padStart(3, '0')}`,
            txid: m.txid,
            expected_sha256: m.car_sha256,
            expected_size: m.car_size,
            expected_root_cid: m.root_cid,
            leaf_path: m.leaf_path || null,
            match: m.match ?? null,
          });
          allTxids.add(m.txid);
          totalCars++;
        }
      }

      const safeContract = contract.toLowerCase();
      const safeTokenId = tokenId.toString();
      const assetName = `nft-${safeContract}-${safeTokenId}.tar`;

      nftList.push({
        contract, tokenId, entry, files, assetName,
        safeContract, safeTokenId,
      });
    }
  }

  log(`  ${totalCars} CAR files, ${allTxids.size} unique txids`);
  log('');

  if (dryRun) {
    log('🔍 DRY RUN — first 5 NFTs:');
    for (const nft of nftList.slice(0, 5)) {
      log(`  ${nft.assetName}`);
      for (const f of nft.files) {
        log(`    ${f.role}: sha256=${f.expected_sha256?.slice(0, 16)}... size=${f.expected_size}`);
      }
    }
    return;
  }

  // ── Step 2: Prepare ─────────────────────────────────────────────────

  fs.mkdirSync(TMP_DIR, { recursive: true });
  fs.mkdirSync(path.join(TMP_DIR, 'cars'), { recursive: true });

  // ── Step 3: Ensure release ──────────────────────────────────────────

  log('📦 Step 2: Ensuring GitHub Release...');
  const release = await ensureRelease();
  let existingAssets = await getAllAssets(release.id);
  log(`  ${existingAssets.size} existing assets`);

  // ── Step 4: Clean old assets ────────────────────────────────────────

  log('  Cleaning old NFT assets for clean rebuild...');
  let deleted = 0;
  for (const [name, asset] of existingAssets) {
    if (name.startsWith('nft-') || name === 'RELEASE-MANIFEST.json' || name === 'RELEASE-CHECKSUMS.sha256'
        || name === 'ONCHAIN-READ-AUDIT.json' || name === 'verification_observed.json' || name === 'media-root-cid-mismatches.json') {
      await deleteAsset(release.id, asset.id);
      deleted++;
      if (deleted % 20 === 0) process.stdout.write(`\r    Deleted ${deleted}...`);
    }
  }
  if (deleted > 0) log(`\r    Deleted ${deleted} old assets`);
  existingAssets = await getAllAssets(release.id);
  log('');

  // ── Step 5: Download & verify CARs from Arweave ────────────────────

  log('📥 Step 3: Downloading & verifying CAR files from Arweave...');
  let dlOk = 0, dlFail = 0, dlSkip = 0;
  const verificationErrors = [];
  let sha256MatchCount = 0, sizeMatchCount = 0;

  const downloadTasks = [];
  for (const nft of nftList) {
    const nftDir = path.join(TMP_DIR, 'cars', `${nft.safeContract}_${nft.safeTokenId}`);
    fs.mkdirSync(nftDir, { recursive: true });

    for (const f of nft.files) {
      const dest = path.join(nftDir, `${f.role}.car`);

      if (fs.existsSync(dest) && fs.statSync(dest).size > 0) {
        const existingBuf = fs.readFileSync(dest);
        const existingHash = sha256hex(existingBuf);
        if (existingHash === f.expected_sha256 && existingBuf.length === f.expected_size) {
          dlSkip++;
          sha256MatchCount++;
          sizeMatchCount++;
          continue;
        }
        fs.unlinkSync(dest);
      }

      downloadTasks.push(async () => {
        try {
          const buf = await downloadTxid(f.txid, dest);

          const actualHash = sha256hex(buf);
          if (actualHash !== f.expected_sha256) {
            verificationErrors.push({
              nft: nft.assetName, role: f.role, type: 'sha256_mismatch',
              expected: f.expected_sha256, actual: actualHash,
            });
            dlFail++;
            return;
          }
          sha256MatchCount++;

          if (buf.length !== f.expected_size) {
            verificationErrors.push({
              nft: nft.assetName, role: f.role, type: 'size_mismatch',
              expected: f.expected_size, actual: buf.length,
            });
            dlFail++;
            return;
          }
          sizeMatchCount++;

          dlOk++;
          if ((dlOk + dlFail) % 20 === 0) {
            process.stdout.write(`\r   ${dlOk + dlFail}/${totalCars} CARs`);
          }
        } catch (e) {
          dlFail++;
          verificationErrors.push({
            nft: nft.assetName, role: f.role, type: 'download_failed',
            error: e.message,
          });
        }
      });
    }
  }

  if (downloadTasks.length > 0) {
    await runConcurrent(downloadTasks, DOWNLOAD_CONCURRENCY);
  }
  log(`\n   Downloads: ${dlOk} ok, ${dlFail} failed, ${dlSkip} cached`);

  if (verificationErrors.length > 0) {
    err('\n  ❌ Download/verification errors:');
    for (const e of verificationErrors.slice(0, 10)) {
      err(`    ${e.nft} [${e.role}] ${e.type}: ${e.expected || ''} → ${e.actual || e.error || ''}`);
    }
    if (verificationErrors.length > 10) err(`    ... and ${verificationErrors.length - 10} more`);
    process.exit(1);
  }
  log('');

  // ── Step 6: Package and upload ─────────────────────────────────────

  log('📤 Step 4: Packaging & uploading NFT archives...');
  let uploaded = 0, upFail = 0;

  for (const nft of nftList) {
    const nftDir = path.join(TMP_DIR, 'cars', `${nft.safeContract}_${nft.safeTokenId}`);
    const tarPath = path.join(TMP_DIR, nft.assetName);

    const tarFiles = [];
    const checksumLines = [];

    const manifest = {
      contract: nft.contract,
      token_id: nft.tokenId,
      nft_asset_name: nft.assetName,
      source_index_commit: sourceCommit,
      generated_by_workflow: 'backup-nft-arweave-mirror',
      generated_at: new Date().toISOString(),
      verification_scope: 'arweave_download_hash_size_only',
      files: [],
    };

    for (const f of nft.files) {
      const carPath = path.join(nftDir, `${f.role}.car`);
      if (!fs.existsSync(carPath)) {
        err(`  ❌ Missing: ${carPath}`);
        upFail++;
        continue;
      }

      const carData = fs.readFileSync(carPath);
      const carHash = sha256hex(carData);

      manifest.files.push({
        role: f.role,
        arweave_txid: f.txid,
        original_leaf_path: f.leaf_path,
        cid: f.expected_root_cid,
        match: f.match,
        size_bytes: carData.length,
        sha256: carHash,
        local_filename: `${f.role}.car`,
      });

      checksumLines.push(`${carHash}  ${f.role}.car`);
      tarFiles.push({ name: `nft/${f.role}.car`, data: carData });
    }

    tarFiles.push({
      name: `nft/manifest.json`,
      data: Buffer.from(JSON.stringify(manifest, null, 2)),
    });
    tarFiles.push({
      name: `nft/checksums.sha256`,
      data: Buffer.from(checksumLines.join('\n') + '\n'),
    });

    const tarBuf = createTar(tarFiles);
    fs.writeFileSync(tarPath, tarBuf);

    try {
      await uploadAsset(release.id, tarPath, nft.assetName);
      uploaded++;
      if (uploaded % 10 === 0) {
        process.stdout.write(`\r   ${uploaded + upFail}/${nftList.length} NFTs`);
      }
    } catch (e) {
      err(`\n  ❌ Upload ${nft.assetName}: ${e.message}`);
      upFail++;
    }
  }

  log(`\n   Uploads: ${uploaded} uploaded, ${upFail} failed`);
  if (upFail > 0) {
    err(`  ❌ ${upFail} uploads failed. Aborting.`);
    process.exit(1);
  }
  log('');

  // ── Step 7: Generate RELEASE-MANIFEST.json ─────────────────────────

  log('📄 Step 5: Generating RELEASE-MANIFEST.json & RELEASE-CHECKSUMS.sha256...');

  const manifestEntries = nftList.map(nft => ({
    contract: nft.contract,
    token_id: nft.tokenId,
    nft_asset_name: nft.assetName,
    car_count: nft.files.length,
    files: nft.files.map(f => ({
      role: f.role,
      arweave_txid: f.txid,
      expected_sha256: f.expected_sha256,
      expected_size: f.expected_size,
      expected_root_cid: f.expected_root_cid,
      leaf_path: f.leaf_path,
      match: f.match,
    })),
  }));

  const allSha256Match = sha256MatchCount === totalCars;
  const allSizeMatch = sizeMatchCount === totalCars;

  const releaseManifest = {
    schema: 'nft-arweave-mirror-manifest-v5',
    release_tag: RELEASE_TAG,
    generated_at: new Date().toISOString(),
    source_index_commit: sourceCommit,
    source_index_file: TOKEN_INDEX_FILE,
    expected_nfts: EXPECTED_NFTS,
    actual_nfts: nftList.length,
    nft_archive_asset_count: nftList.length,
    total_car_files: totalCars,
    total_unique_arweave_txids: allTxids.size,
    verification_scope: 'arweave_download_hash_size_only',
    verification_status: (allSha256Match && allSizeMatch) ? 'PASS' : 'FAIL',
    all_car_sha256_match_token_index: allSha256Match,
    all_car_size_match_token_index: allSizeMatch,
    root_cid_verified: false,
    onchain_verified: false,
    verification_details: {
      arweave_download: { ok: dlOk + dlSkip, fail: dlFail },
      sha256_check: { pass: sha256MatchCount, total: totalCars },
      size_check: { pass: sizeMatchCount, total: totalCars },
    },
    note: 'Verification is sha256+size only against token_index. Use verify-release-assets.mjs for release-level re-verification. Use verify-onchain-tokenuri.mjs for ETH onchain audit.',
    per_nft_assets: manifestEntries,
  };

  const manifestPath = path.join(TMP_DIR, 'RELEASE-MANIFEST.json');
  fs.writeFileSync(manifestPath, JSON.stringify(releaseManifest, null, 2));
  await uploadAsset(release.id, manifestPath, 'RELEASE-MANIFEST.json');
  log('  ✅ RELEASE-MANIFEST.json uploaded');

  // Generate RELEASE-CHECKSUMS.sha256
  const checksumLines = [];
  checksumLines.push(`# RELEASE-CHECKSUMS.sha256 — ${RELEASE_TAG}`);
  checksumLines.push(`# Generated: ${new Date().toISOString()}`);
  checksumLines.push(`# Every line: sha256  asset_name`);
  checksumLines.push('');
  for (const nft of nftList) {
    const tarPath = path.join(TMP_DIR, nft.assetName);
    if (!fs.existsSync(tarPath)) continue;
    const buf = fs.readFileSync(tarPath);
    checksumLines.push(`${sha256hex(buf)}  ${nft.assetName}`);
  }
  const manifestBuf = fs.readFileSync(manifestPath);
  checksumLines.push(`${sha256hex(manifestBuf)}  RELEASE-MANIFEST.json`);

  const checksumsPath = path.join(TMP_DIR, 'RELEASE-CHECKSUMS.sha256');
  fs.writeFileSync(checksumsPath, checksumLines.join('\n') + '\n');
  await uploadAsset(release.id, checksumsPath, 'RELEASE-CHECKSUMS.sha256');
  log('  ✅ RELEASE-CHECKSUMS.sha256 uploaded');

  // Cleanup local tar files
  for (const nft of nftList) {
    const tarPath = path.join(TMP_DIR, nft.assetName);
    if (fs.existsSync(tarPath)) fs.unlinkSync(tarPath);
  }

  // ── Final summary ──────────────────────────────────────────────────

  log('');
  log('═══════════════════════════════════════════════════════════');
  log(`  ✅ Downloads      : ${dlOk + dlSkip} CARs (${allTxids.size} unique txids)`);
  log(`  ✅ SHA-256        : ${sha256MatchCount}/${totalCars} CARs match token_index`);
  log(`  ✅ Size           : ${sizeMatchCount}/${totalCars} CARs match token_index`);
  log(`  📤 Uploads        : ${uploaded} uploaded`);
  log(`  📊 Release        : ${nftList.length} NFT assets + manifest + checksums`);
  log(`  📄 Status         : ${releaseManifest.verification_status}`);
  log(`  🔍 Scope          : arweave_download_hash_size_only (no CID, no onchain)`);
  log('═══════════════════════════════════════════════════════════');

  if (!(allSha256Match && allSizeMatch)) {
    err('\n  ❌ FAIL — sha256 or size verification failed');
    process.exit(1);
  }

  log('\n  🎉 All 175 NFTs mirrored (hash + size verified).');
}

main().catch(e => {
  err('Fatal:', e);
  process.exit(1);
});
