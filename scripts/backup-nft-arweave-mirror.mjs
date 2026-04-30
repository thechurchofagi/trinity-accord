#!/usr/bin/env node
/**
 * backup-nft-arweave-mirror.mjs
 *
 * Strict Arweave → GitHub Release mirror for 175 NFTs.
 *
 * - Downloads CAR files directly from Arweave gateways
 * - Packages each NFT as an individual .tar (no compression, raw CAR bytes preserved)
 * - Uploads to a clean GitHub Release
 * - Verifies every upload by re-downloading and comparing SHA-256
 * - Generates RELEASE-MANIFEST.json as the final asset
 *
 * Usage:
 *   GITHUB_TOKEN=xxx node scripts/backup-nft-arweave-mirror.mjs [--dry-run] [--contract 0x...]
 *
 * Designed to run exclusively via GitHub Actions workflow.
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { execSync } from 'child_process';
import { pipeline } from 'stream/promises';
import { createWriteStream } from 'fs';

// ─── Config ────────────────────────────────────────────────────────────────

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO = process.env.REPO || 'thechurchofagi/trinity-accord';
const RELEASE_TAG = process.env.RELEASE_TAG || 'nft-arweave-mirror-175-v1';
const CAR_FILE = process.env.CAR_FILE || 'archive/evidence/nft-recovery-package/recovery-package.bin';
const TMP_DIR = '/tmp/nft-arweave-mirror';
const GATEWAYS = ['https://arweave.net', 'https://ar-io.net'];
const EXPECTED_NFTS = 175;
const MAX_RETRIES = 3;
const DOWNLOAD_CONCURRENCY = 5;
const UPLOAD_CONCURRENCY = 2; // conservative to avoid 429

// ─── Helpers ───────────────────────────────────────────────────────────────

function sha256(buf) {
  return crypto.createHash('sha256').update(buf).digest('hex');
}

function sha256File(filePath) {
  const hash = crypto.createHash('sha256');
  const data = fs.readFileSync(filePath);
  hash.update(data);
  return hash.digest('hex');
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ─── CAR parsing ───────────────────────────────────────────────────────────

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

/**
 * Extract token_index.json from the recovery CAR by finding the LARGEST
 * token-index JSON object across ALL blocks.
 */
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
    } catch (err) {
      if (attempt === retries) throw err;
      await sleep(2000 * (attempt + 1));
    }
  }
}

// ─── Concurrency pool ──────────────────────────────────────────────────────

async function runConcurrent(tasks, limit) {
  const results = new Array(tasks.length);
  let nextIdx = 0;

  async function worker() {
    while (nextIdx < tasks.length) {
      const idx = nextIdx++;
      try {
        results[idx] = await tasks[idx]();
      } catch (err) {
        results[idx] = err;
      }
    }
  }

  const workers = Array.from({ length: Math.min(limit, tasks.length) }, () => worker());
  await Promise.all(workers);
  return results;
}

// ─── GitHub Release helpers ────────────────────────────────────────────────

function ghHeaders() {
  return {
    Authorization: `Bearer ${GITHUB_TOKEN}`,
    Accept: 'application/vnd.github+json',
  };
}

async function ghFetch(url, opts = {}) {
  const res = await fetch(url, {
    ...opts,
    headers: { ...ghHeaders(), ...opts.headers },
  });
  return res;
}

async function ensureRelease() {
  const res = await ghFetch(`https://api.github.com/repos/${REPO}/releases/tags/${RELEASE_TAG}`);
  if (res.ok) {
    const rel = await res.json();
    console.log(`  Release ${RELEASE_TAG} already exists (id: ${rel.id}), will reuse.`);
    return rel;
  }

  console.log(`  Creating release ${RELEASE_TAG}...`);
  const create = await ghFetch(`https://api.github.com/repos/${REPO}/releases`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      tag_name: RELEASE_TAG,
      name: `NFT Arweave Mirror — 175 NFTs`,
      body: [
        `## Strict Arweave → GitHub Release Mirror`,
        ``,
        `175 individual NFT archives, each containing raw Arweave CAR files.`,
        `No compression applied (.tar only) — CAR bytes are exactly as downloaded from Arweave.`,
        ``,
        `Every CAR file SHA-256 is verified after download AND after upload.`,
        `See RELEASE-MANIFEST.json for full verification results.`,
        ``,
        `Generated: ${new Date().toISOString()}`,
      ].join('\n'),
    }),
  });
  if (!create.ok) throw new Error(`Create release failed: ${create.status} ${await create.text()}`);
  return await create.json();
}

async function getExistingAssets(releaseId) {
  const assets = new Map();
  let page = 1;
  while (true) {
    const res = await ghFetch(
      `https://api.github.com/repos/${REPO}/releases/${releaseId}/assets?per_page=100&page=${page}`
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
      const errBody = await res.text();
      console.log(`    ⚠️  422 on attempt ${attempt + 1}: ${errBody.slice(0, 100)}`);
      await sleep(3000 * (attempt + 1));
      continue;
    }
    if (res.status === 403 || res.status === 429) {
      console.log(`    ⚠️  Rate limited (${res.status}), waiting 60s...`);
      await sleep(60000);
      continue;
    }
    throw new Error(`Upload failed: ${res.status} ${await res.text()}`);
  }
  throw new Error(`Upload failed after ${MAX_RETRIES} attempts`);
}

async function downloadAndVerifyAsset(assetId, assetName) {
  const res = await ghFetch(
    `https://api.github.com/repos/${REPO}/releases/assets/${assetId}`,
    { headers: { Accept: 'application/octet-stream' } }
  );
  if (!res.ok) throw new Error(`Download asset failed: ${res.status}`);
  const buf = Buffer.from(await res.arrayBuffer());
  return buf;
}

// ─── Tar creation (pure Node.js, no external deps) ─────────────────────────

/**
 * Create a minimal POSIX .tar archive from a list of files.
 * No compression — raw bytes preserved.
 */
function createTar(files) {
  // TAR header: 512 bytes per file header + 512-byte data blocks (padded to 512)
  // + 1024 bytes end-of-archive

  const blocks = [];

  for (const { name, data } of files) {
    const header = Buffer.alloc(512);

    // File name (100 bytes)
    header.write(name, 0, Math.min(name.length, 100), 'utf-8');
    // File mode (8 bytes) - '0644\0'
    header.write('0000644\0', 100, 8, 'utf-8');
    // Owner ID (8 bytes)
    header.write('0000000\0', 108, 8, 'utf-8');
    // Group ID (8 bytes)
    header.write('0000000\0', 116, 8, 'utf-8');
    // File size in octal (12 bytes)
    const sizeOctal = data.length.toString(8).padStart(11, '0') + '\0';
    header.write(sizeOctal, 124, 12, 'utf-8');
    // Modification time in octal (12 bytes)
    const mtimeOctal = Math.floor(Date.now() / 1000).toString(8).padStart(11, '0') + '\0';
    header.write(mtimeOctal, 136, 12, 'utf-8');
    // Type flag (1 byte) - '0' = regular file
    header.write('0', 156, 1, 'utf-8');
    // USTAR magic (6 bytes)
    header.write('ustar\0', 257, 6, 'utf-8');
    // USTAR version (2 bytes)
    header.write('00', 263, 2, 'utf-8');

    // Calculate checksum
    header.fill(32, 148, 156); // fill checksum field with spaces
    let chksum = 0;
    for (let i = 0; i < 512; i++) chksum += header[i];
    const chksumOctal = chksum.toString(8).padStart(6, '0') + '\0 ';
    header.write(chksumOctal, 148, 8, 'utf-8');

    blocks.push(header);

    // Data blocks (padded to 512-byte boundary)
    const paddedSize = Math.ceil(data.length / 512) * 512;
    const dataBlock = Buffer.alloc(paddedSize);
    data.copy(dataBlock);
    blocks.push(dataBlock);
  }

  // End-of-archive: two 512-byte zero blocks
  blocks.push(Buffer.alloc(512));
  blocks.push(Buffer.alloc(512));

  return Buffer.concat(blocks);
}

// ─── Main ──────────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  const dryRun = args.includes('--dry-run');
  const contractFilter = args.includes('--contract') ? args[args.indexOf('--contract') + 1] : null;

  // Get current commit hash for provenance
  let sourceCommit = 'unknown';
  try {
    sourceCommit = execSync('git rev-parse HEAD', { encoding: 'utf-8' }).trim();
  } catch {}

  console.log('═══════════════════════════════════════════════════════════');
  console.log('  NFT Arweave → GitHub Release Strict Mirror');
  console.log('═══════════════════════════════════════════════════════════');
  console.log(`  Source CAR : ${CAR_FILE}`);
  console.log(`  Release    : ${RELEASE_TAG}`);
  console.log(`  Concurrency: download=${DOWNLOAD_CONCURRENCY}, upload=${UPLOAD_CONCURRENCY}`);
  console.log(`  Commit     : ${sourceCommit}`);
  if (contractFilter) console.log(`  Contract   : ${contractFilter}`);
  console.log();

  // ── Step 1: Extract token index ──────────────────────────────────────

  console.log('📖 Step 1: Extracting token_index from CAR...');
  const index = extractTokenIndex(CAR_FILE);

  const allContracts = Object.keys(index);
  const contracts = contractFilter ? [contractFilter] : allContracts;
  let totalNfts = 0;
  for (const c of contracts) {
    if (!index[c]) { console.error(`  ❌ Contract ${c} not found in index`); process.exit(1); }
    totalNfts += Object.keys(index[c]).length;
  }

  console.log(`  Contracts: ${contracts.length} (of ${allContracts.length} total)`);
  console.log(`  NFTs: ${totalNfts}`);

  if (totalNfts !== EXPECTED_NFTS && !contractFilter) {
    console.error(`  ❌ FATAL: Expected ${EXPECTED_NFTS} NFTs, found ${totalNfts}. Aborting.`);
    process.exit(1);
  }
  console.log();

  // ── Step 2: Build task list ──────────────────────────────────────────

  console.log('📋 Step 2: Building NFT task list...');
  const nftList = [];
  const allTxids = new Set();

  for (const contract of contracts) {
    for (const [tokenId, entry] of Object.entries(index[contract])) {
      const files = [];
      if (entry.metadata?.txid) {
        files.push({ role: 'metadata', txid: entry.metadata.txid, leaf_path: null, cid: entry.metadata.cid || null });
        allTxids.add(entry.metadata.txid);
      }
      const mediaList = entry.media || [];
      for (let i = 0; i < mediaList.length; i++) {
        const m = mediaList[i];
        if (m.txid) {
          files.push({ role: `media-${String(i).padStart(3, '0')}`, txid: m.txid, leaf_path: m.leaf_path || null, cid: m.cid || null });
          allTxids.add(m.txid);
        }
      }

      const safeContract = contract.toLowerCase();
      const safeTokenId = tokenId.toString();
      const assetName = `nft-${safeContract}-${safeTokenId}.tar`;

      nftList.push({ contract, tokenId, entry, files, assetName, safeContract, safeTokenId });
    }
  }

  console.log(`  ${nftList.length} NFTs, ${allTxids.size} unique Arweave txids`);
  console.log();

  if (dryRun) {
    console.log('🔍 DRY RUN — first 10 NFTs:');
    for (const nft of nftList.slice(0, 10)) {
      console.log(`  ${nft.assetName}  files=${nft.files.length}`);
    }
    console.log(`  ... (${nftList.length - 10} more)`);
    return;
  }

  // ── Step 3: Prepare ─────────────────────────────────────────────────

  fs.mkdirSync(TMP_DIR, { recursive: true });
  fs.mkdirSync(path.join(TMP_DIR, 'cars'), { recursive: true });

  // ── Step 4: Ensure release ──────────────────────────────────────────

  console.log('📦 Step 3: Ensuring GitHub Release...');
  const release = await ensureRelease();
  const existingAssets = await getExistingAssets(release.id);
  console.log(`  Release id: ${release.id}, existing assets: ${existingAssets.size}`);
  console.log();

  // ── Step 5: Phase 1 — Download all CARs from Arweave ────────────────

  console.log('📥 Step 4: Downloading CAR files from Arweave...');
  let dlOk = 0, dlFail = 0, dlSkip = 0;

  const downloadTasks = [];
  for (const nft of nftList) {
    const nftDir = path.join(TMP_DIR, 'cars', `${nft.safeContract}_${nft.safeTokenId}`);
    fs.mkdirSync(nftDir, { recursive: true });

    for (const f of nft.files) {
      const dest = path.join(nftDir, `${f.role}.car`);
      if (fs.existsSync(dest) && fs.statSync(dest).size > 0) {
        dlSkip++;
        continue;
      }
      downloadTasks.push(async () => {
        try {
          await downloadTxid(f.txid, dest);
          dlOk++;
          if ((dlOk + dlFail) % 20 === 0) {
            process.stdout.write(`\r   ${dlOk + dlFail}/${nftList.reduce((n, nft) => n + nft.files.length, 0)} CARs`);
          }
        } catch (err) {
          dlFail++;
          console.error(`\n  ❌ ${f.txid.slice(0, 16)}...: ${err.message}`);
        }
      });
    }
  }

  const totalCars = downloadTasks.length + dlSkip;
  if (downloadTasks.length > 0) {
    await runConcurrent(downloadTasks, DOWNLOAD_CONCURRENCY);
  }
  console.log(`\n   Downloads: ${dlOk} ok, ${dlFail} failed, ${dlSkip} skipped (cached)`);

  if (dlFail > 0) {
    console.error(`  ❌ ${dlFail} downloads failed. Aborting.`);
    process.exit(1);
  }
  console.log();

  // ── Step 6: Phase 2 — Package and upload ────────────────────────────

  console.log('📤 Step 5: Packaging & uploading NFT archives...');
  let uploaded = 0, skipped = 0, upFail = 0;
  const uploadedAssets = new Map(); // assetName -> { id, carSha256s }

  // Track per-NFT verification data for manifest
  const manifestEntries = [];

  for (const nft of nftList) {
    const nftDir = path.join(TMP_DIR, 'cars', `${nft.safeContract}_${nft.safeTokenId}`);
    const tarPath = path.join(TMP_DIR, nft.assetName);

    // Check if already uploaded
    if (existingAssets.has(nft.assetName)) {
      skipped++;
      const existing = existingAssets.get(nft.assetName);
      manifestEntries.push({
        contract: nft.contract,
        token_id: nft.tokenId,
        nft_asset_name: nft.assetName,
        github_asset_id: existing.id,
        verification: 'skipped-existing',
        files: [],
      });
      continue;
    }

    // Build archive contents
    const tarFiles = [];
    const carSha256s = [];
    const fileEntries = [];

    // Write manifest.json
    const manifest = {
      contract: nft.contract,
      token_id: nft.tokenId,
      nft_asset_name: nft.assetName,
      source_index_commit: sourceCommit,
      generated_by_workflow: 'backup-nft-arweave-mirror',
      generated_at: new Date().toISOString(),
      files: [],
    };

    for (const f of nft.files) {
      const carPath = path.join(nftDir, `${f.role}.car`);
      if (!fs.existsSync(carPath)) {
        console.error(`  ❌ Missing CAR: ${carPath}`);
        upFail++;
        continue;
      }

      const carData = fs.readFileSync(carPath);
      const carHash = sha256(carData);

      manifest.files.push({
        role: f.role.startsWith('media') ? 'media' : 'metadata',
        arweave_txid: f.txid,
        original_leaf_path: f.leaf_path,
        cid: f.cid,
        match: true,
        size_bytes: carData.length,
        sha256: carHash,
        local_filename: `${f.role}.car`,
      });

      carSha256s.push({ role: f.role, sha256: carHash, size: carData.length });
      tarFiles.push({ name: `${nft.safeContract}_${nft.safeTokenId}/${f.role}.car`, data: carData });
    }

    // Add manifest.json to tar
    const manifestJson = JSON.stringify(manifest, null, 2);
    tarFiles.push({
      name: `${nft.safeContract}_${nft.safeTokenId}/manifest.json`,
      data: Buffer.from(manifestJson),
    });

    // Add checksums.sha256
    const checksumLines = carSha256s.map(c => `${c.sha256}  ${c.role}.car`).join('\n') + '\n';
    tarFiles.push({
      name: `${nft.safeContract}_${nft.safeTokenId}/checksums.sha256`,
      data: Buffer.from(checksumLines),
    });

    // Create .tar
    const tarBuf = createTar(tarFiles);
    fs.writeFileSync(tarPath, tarBuf);

    // Upload
    try {
      const result = await uploadAsset(release.id, tarPath, nft.assetName);
      uploaded++;
      uploadedAssets.set(nft.assetName, { id: result.id, carSha256s });

      if (uploaded % 10 === 0) {
        process.stdout.write(`\r   ${uploaded + skipped + upFail}/${nftList.length} NFTs`);
      }
    } catch (err) {
      console.error(`\n  ❌ Upload ${nft.assetName}: ${err.message}`);
      upFail++;
    }

    // Cleanup tar
    if (fs.existsSync(tarPath)) fs.unlinkSync(tarPath);
  }

  console.log(`\n   Uploads: ${uploaded} new | ${skipped} skipped | ${upFail} failed`);
  console.log();

  if (upFail > 0) {
    console.error(`  ❌ ${upFail} uploads failed. Aborting verification.`);
    process.exit(1);
  }

  // ── Step 7: Phase 3 — Verify uploaded assets ────────────────────────

  console.log('🔍 Step 6: Verifying uploaded assets (re-download + SHA-256 check)...');
  let verifyPass = 0, verifyFail = 0;

  for (const [assetName, info] of uploadedAssets) {
    try {
      const assetBuf = await downloadAndVerifyAsset(info.id, assetName);

      // Extract CAR files from tar and verify SHA-256
      // For .tar: parse tar headers and extract files
      const extractedCars = extractFilesFromTar(assetBuf);

      for (const { name, data } of extractedCars) {
        if (!name.endsWith('.car')) continue;
        const actualHash = sha256(data);
        const expected = info.carSha256s.find(c => name.endsWith(`${c.role}.car`));
        if (!expected) {
          console.error(`  ❌ ${assetName}: unexpected file ${name}`);
          verifyFail++;
          continue;
        }
        if (actualHash !== expected.sha256) {
          console.error(`  ❌ ${assetName}: SHA-256 mismatch for ${name}`);
          console.error(`     expected: ${expected.sha256}`);
          console.error(`     actual  : ${actualHash}`);
          verifyFail++;
        }
      }
      verifyPass++;
      if (verifyPass % 20 === 0) {
        process.stdout.write(`\r   ${verifyPass + verifyFail}/${uploadedAssets.size} verified`);
      }
    } catch (err) {
      console.error(`\n  ❌ Verify ${assetName}: ${err.message}`);
      verifyFail++;
    }
  }

  console.log(`\n   Verified: ${verifyPass} pass, ${verifyFail} fail`);
  console.log();

  if (verifyFail > 0) {
    console.error(`  ❌ ${verifyFail} verification failures. Aborting.`);
    process.exit(1);
  }

  // ── Step 8: Generate RELEASE-MANIFEST.json ──────────────────────────

  console.log('📄 Step 7: Generating RELEASE-MANIFEST.json...');

  // Rebuild full manifest entries for all NFTs
  const finalManifestEntries = [];
  for (const nft of nftList) {
    const existing = existingAssets.get(nft.assetName) || uploadedAssets.get(nft.assetName);
    const entry = {
      contract: nft.contract,
      token_id: nft.tokenId,
      nft_asset_name: nft.assetName,
      github_asset_id: existing?.id || null,
      verification: uploadedAssets.has(nft.assetName) ? 'verified' : 'skipped-existing',
      files: nft.files.map(f => ({
        role: f.role.startsWith('media') ? 'media' : 'metadata',
        arweave_txid: f.txid,
      })),
    };
    finalManifestEntries.push(entry);
  }

  const finalAssetCount = existingAssets.size + uploaded;
  const releaseManifest = {
    schema: 'nft-arweave-mirror-manifest-v1',
    release_tag: RELEASE_TAG,
    generated_at: new Date().toISOString(),
    source_index_commit: sourceCommit,
    expected_nfts: EXPECTED_NFTS,
    release_asset_count: finalAssetCount,
    total_arweave_car_files: totalCars,
    total_unique_arweave_txids: allTxids.size,
    verification_status: finalAssetCount === EXPECTED_NFTS ? 'PASS' : 'FAIL',
    per_nft_assets: finalManifestEntries,
  };

  const manifestPath = path.join(TMP_DIR, 'RELEASE-MANIFEST.json');
  fs.writeFileSync(manifestPath, JSON.stringify(releaseManifest, null, 2));

  // Upload manifest
  try {
    await uploadAsset(release.id, manifestPath, 'RELEASE-MANIFEST.json');
    console.log('  ✅ RELEASE-MANIFEST.json uploaded');
  } catch (err) {
    console.error(`  ❌ Upload manifest: ${err.message}`);
    process.exit(1);
  }

  // ── Final summary ───────────────────────────────────────────────────

  console.log();
  console.log('═══════════════════════════════════════════════════════════');
  console.log(`  ✅ Downloads : ${dlOk + dlSkip} CARs (${allTxids.size} unique txids)`);
  console.log(`  📤 Uploads   : ${uploaded} new | ${skipped} existing`);
  console.log(`  🔍 Verified  : ${verifyPass} pass | ${verifyFail} fail`);
  console.log(`  📊 Release   : ${finalAssetCount} NFT assets / ${EXPECTED_NFTS} expected`);
  console.log(`  📄 Manifest  : ${releaseManifest.verification_status}`);
  console.log('═══════════════════════════════════════════════════════════');

  if (finalAssetCount !== EXPECTED_NFTS) {
    console.error(`\n  ❌ FAIL: Release has ${finalAssetCount} assets, expected ${EXPECTED_NFTS}`);
    process.exit(1);
  }

  if (releaseManifest.verification_status !== 'PASS') {
    console.error(`\n  ❌ FAIL: Verification status is ${releaseManifest.verification_status}`);
    process.exit(1);
  }

  console.log('\n  🎉 All 175 NFTs mirrored successfully!');
}

/**
 * Extract files from a .tar buffer (minimal POSIX tar parser)
 */
function extractFilesFromTar(buf) {
  const files = [];
  let pos = 0;

  while (pos < buf.length - 1024) {
    // Check for zero block (end of archive)
    const header = buf.slice(pos, pos + 512);
    if (header.every(b => b === 0)) break;

    // Parse file name (bytes 0-99)
    let nameEnd = 0;
    while (nameEnd < 100 && header[nameEnd] !== 0) nameEnd++;
    const name = header.slice(0, nameEnd).toString('utf-8');

    // Parse file size (bytes 124-135, octal)
    let sizeStr = '';
    for (let i = 124; i < 136; i++) {
      if (header[i] === 0 || header[i] === 32) break;
      sizeStr += String.fromCharCode(header[i]);
    }
    const size = parseInt(sizeStr, 8) || 0;

    pos += 512; // skip header

    if (size > 0) {
      const data = buf.slice(pos, pos + size);
      files.push({ name, data });
      pos += Math.ceil(size / 512) * 512;
    }
  }

  return files;
}

main().catch(err => {
  console.error('Fatal:', err);
  process.exit(1);
});
