#!/usr/bin/env node
/**
 * backup-nft-arweave-mirror.mjs  (v3 — strict verification)
 *
 * Strict Arweave → GitHub Release mirror for 175 NFTs.
 *
 * Verification layers:
 *   1. SHA-256 of every downloaded CAR == token_index car_sha256
 *   2. Size of every downloaded CAR   == token_index car_size
 *   3. Root CID extracted from CAR    == token_index root_cid
 *   4. Every uploaded Release asset is re-downloaded and re-verified
 *   5. RELEASE-MANIFEST.json + RELEASE-CHECKSUMS.sha256 uploaded as final assets
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
const CAR_FILE = process.env.CAR_FILE || 'archive/evidence/nft-recovery-package/recovery-package.bin';
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
    yield { data: data.slice(pos, pos + blockLen), index: idx, offset: pos };
    pos += blockLen; idx++;
  }
}

/**
 * Extract root CID from CAR header.
 * The header is DAG-CBOR: { roots: [CID], version: 1 }
 * CID is tagged with CBOR tag 42.
 * Returns the root CID as a base32 CIDv1 string.
 */
function extractCarRootCid(carData) {
  // Parse the CBOR header manually to find the CID
  // The header structure after varint-length:
  // a2          map(2)
  // 65726f6f7473 "roots"
  // 81          array(1)
  // d82a        tag(42) — CID tag
  // 5823        bytes(35) for CIDv0 or similar
  // Then the CID bytes follow

  const headerEnd = parseCarHeader(carData);
  const header = carData.slice(0, headerEnd);

  // Find tag(42) marker: 0xd8 0x2a
  for (let i = 0; i < header.length - 2; i++) {
    if (header[i] === 0xd8 && header[i + 1] === 0x2a) {
      // Next byte should be a bytes length indicator
      let cidStart = i + 2;
      let cidLen = 0;

      if (header[cidStart] === 0x58) {
        // 1-byte length follows
        cidLen = header[cidStart + 1];
        cidStart += 2;
      } else if (header[cidStart] === 0x59) {
        // 2-byte length follows
        cidLen = (header[cidStart + 1] << 8) | header[cidStart + 2];
        cidStart += 3;
      } else {
        cidLen = header[cidStart] - 0x40; // inline length
        cidStart += 1;
      }

      const cidBytes = header.slice(cidStart, cidStart + cidLen);
      return cidBytesToCidV1(cidBytes);
    }
  }

  throw new Error('Could not extract root CID from CAR header');
}

/**
 * Convert raw CID bytes to a CIDv1 base32 string.
 * CIDv0: just a multihash (starts with 0x12 0x20 for sha2-256)
 * CIDv1: version(1) + codec + multihash
 */
function cidBytesToCidV1(bytes) {
  if (bytes[0] === 0x12 && bytes[1] === 0x20) {
    // CIDv0 — sha2-256 multihash. Convert to CIDv1 dag-cbor.
    // CIDv1 = 0x01 + 0x71 (dag-cbor) + multihash
    const cidV1Bytes = Buffer.concat([Buffer.from([0x01, 0x71]), bytes]);
    return base32EncodeCid(cidV1Bytes);
  }
  // Already CIDv1
  if (bytes[0] === 0x01) {
    return base32EncodeCid(bytes);
  }
  // Fallback: return hex
  return bytes.toString('hex');
}

/**
 * Encode CID bytes to base32 (RFC 4648, no padding, lowercase)
 */
function base32EncodeCid(bytes) {
  const alphabet = 'abcdefghijklmnopqrstuvwxyz234567';
  let bits = 0, value = 0, output = '';
  for (const byte of bytes) {
    value = (value << 8) | byte;
    bits += 8;
    while (bits >= 5) {
      output += alphabet[(value >>> (bits - 5)) & 0x1f];
      bits -= 5;
    }
  }
  if (bits > 0) {
    output += alphabet[(value << (5 - bits)) & 0x1f];
  }
  return output;
}

/**
 * Extract token_index.json from the recovery CAR by finding the LARGEST
 * token-index JSON object across ALL blocks.
 */
function extractTokenIndexFromCar(carPath) {
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
      try { results[idx] = await tasks[idx](); }
      catch (err) { results[idx] = err; }
    }
  }
  const workers = Array.from({ length: Math.min(limit, tasks.length) }, () => worker());
  await Promise.all(workers);
  return results;
}

// ─── GitHub helpers ────────────────────────────────────────────────────────

function ghHeaders(extra = {}) {
  return { Authorization: `Bearer ${GITHUB_TOKEN}`, Accept: 'application/vnd.github+json', ...extra };
}

async function ensureRelease() {
  const res = await fetch(`https://api.github.com/repos/${REPO}/releases/tags/${RELEASE_TAG}`, { headers: ghHeaders() });
  if (res.ok) {
    const rel = await res.json();
    console.log(`  Release ${RELEASE_TAG} exists (id: ${rel.id})`);
    return rel;
  }
  console.log(`  Creating release ${RELEASE_TAG}...`);
  const create = await fetch(`https://api.github.com/repos/${REPO}/releases`, {
    method: 'POST',
    headers: ghHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({
      tag_name: RELEASE_TAG,
      name: `NFT Arweave Mirror — 175 NFTs (strict verified)`,
      body: [
        `## Strict Arweave → GitHub Release Mirror (v3)`,
        ``,
        `175 individual NFT archives with full verification:`,
        `- SHA-256 match against token_index`,
        `- CAR size match against token_index`,
        `- Root CID match against token_index`,
        `- Re-download verification after upload`,
        ``,
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
      console.log(`    ⚠️  422 on attempt ${attempt + 1}, retrying...`);
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

async function deleteAsset(releaseId, assetId) {
  const res = await fetch(
    `https://api.github.com/repos/${REPO}/releases/assets/${assetId}`,
    { method: 'DELETE', headers: ghHeaders() }
  );
  if (!res.ok && res.status !== 404) {
    throw new Error(`Delete asset failed: ${res.status}`);
  }
}

async function downloadAsset(assetId) {
  const res = await fetch(
    `https://api.github.com/repos/${REPO}/releases/assets/${assetId}`,
    { headers: ghHeaders({ Accept: 'application/octet-stream' }) }
  );
  if (!res.ok) throw new Error(`Download asset failed: ${res.status}`);
  return Buffer.from(await res.arrayBuffer());
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

function extractFilesFromTar(buf) {
  const files = [];
  let pos = 0;
  while (pos < buf.length - 1024) {
    const header = buf.slice(pos, pos + 512);
    if (header.every(b => b === 0)) break;
    let nameEnd = 0;
    while (nameEnd < 100 && header[nameEnd] !== 0) nameEnd++;
    const name = header.slice(0, nameEnd).toString('utf-8');
    let sizeStr = '';
    for (let i = 124; i < 136; i++) {
      if (header[i] === 0 || header[i] === 32) break;
      sizeStr += String.fromCharCode(header[i]);
    }
    const size = parseInt(sizeStr, 8) || 0;
    pos += 512;
    if (size > 0) {
      const data = buf.slice(pos, pos + size);
      files.push({ name, data });
      pos += Math.ceil(size / 512) * 512;
    }
  }
  return files;
}

// ─── Main ──────────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  const dryRun = args.includes('--dry-run');
  const contractFilter = args.includes('--contract') ? args[args.indexOf('--contract') + 1] : null;
  const deleteExisting = args.includes('--delete-existing');

  let sourceCommit = 'unknown';
  try { sourceCommit = execSync('git rev-parse HEAD', { encoding: 'utf-8' }).trim(); } catch {}

  console.log('═══════════════════════════════════════════════════════════');
  console.log('  NFT Arweave → GitHub Release Strict Mirror (v3)');
  console.log('═══════════════════════════════════════════════════════════');
  console.log(`  Token Index: ${TOKEN_INDEX_FILE}`);
  console.log(`  Release    : ${RELEASE_TAG}`);
  console.log(`  Concurrency: dl=${DOWNLOAD_CONCURRENCY}, ul=${UPLOAD_CONCURRENCY}`);
  console.log(`  Commit     : ${sourceCommit}`);
  console.log();

  // ── Step 1: Load token_index.json directly ───────────────────────────

  console.log('📖 Step 1: Loading token_index.json...');
  const index = JSON.parse(fs.readFileSync(TOKEN_INDEX_FILE, 'utf-8'));
  const allContracts = Object.keys(index);
  const contracts = contractFilter ? [contractFilter] : allContracts;

  let totalNfts = 0;
  for (const c of contracts) {
    if (!index[c]) { console.error(`  ❌ Contract ${c} not found`); process.exit(1); }
    totalNfts += Object.keys(index[c]).length;
  }
  console.log(`  ${contracts.length} contracts, ${totalNfts} NFTs`);

  if (totalNfts !== EXPECTED_NFTS && !contractFilter) {
    console.error(`  ❌ Expected ${EXPECTED_NFTS} NFTs, found ${totalNfts}`);
    process.exit(1);
  }

  // Build full NFT list with all verification fields
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
            match: m.match || null,
          });
          allTxids.add(m.txid);
          totalCars++;
        }
      }

      const safeContract = contract.toLowerCase();
      const safeTokenId = tokenId.toString();
      const assetName = `nft-${safeContract}-${safeTokenId}.tar`;

      nftList.push({ contract, tokenId, entry, files, assetName, safeContract, safeTokenId });
    }
  }

  console.log(`  ${totalCars} CAR files, ${allTxids.size} unique txids`);
  console.log();

  if (dryRun) {
    console.log('🔍 DRY RUN — first 5 NFTs:');
    for (const nft of nftList.slice(0, 5)) {
      console.log(`  ${nft.assetName}`);
      for (const f of nft.files) {
        console.log(`    ${f.role}: sha256=${f.expected_sha256?.slice(0, 16)}... size=${f.expected_size} root_cid=${f.expected_root_cid?.slice(0, 20)}... match=${f.match}`);
      }
    }
    return;
  }

  // ── Step 2: Prepare ─────────────────────────────────────────────────

  fs.mkdirSync(TMP_DIR, { recursive: true });
  fs.mkdirSync(path.join(TMP_DIR, 'cars'), { recursive: true });

  // ── Step 3: Ensure release ──────────────────────────────────────────

  console.log('📦 Step 2: Ensuring GitHub Release...');
  const release = await ensureRelease();
  let existingAssets = await getExistingAssets(release.id);
  console.log(`  ${existingAssets.size} existing assets`);

  // ── Step 4: Optionally delete existing NFT assets ───────────────────

  if (deleteExisting && existingAssets.size > 0) {
    console.log('  Deleting existing NFT assets for clean re-upload...');
    let deleted = 0;
    for (const [name, asset] of existingAssets) {
      if (name.startsWith('nft-') || name === 'RELEASE-MANIFEST.json' || name === 'RELEASE-CHECKSUMS.sha256') {
        await deleteAsset(release.id, asset.id);
        deleted++;
        if (deleted % 20 === 0) process.stdout.write(`\r    Deleted ${deleted}...`);
      }
    }
    console.log(`\r    Deleted ${deleted} assets`);
    existingAssets = await getExistingAssets(release.id);
  }

  console.log();

  // ── Step 5: Phase 1 — Download & verify CARs from Arweave ──────────

  console.log('📥 Step 3: Downloading & verifying CAR files from Arweave...');
  let dlOk = 0, dlFail = 0, dlSkip = 0;
  const verificationErrors = [];

  const downloadTasks = [];
  for (const nft of nftList) {
    const nftDir = path.join(TMP_DIR, 'cars', `${nft.safeContract}_${nft.safeTokenId}`);
    fs.mkdirSync(nftDir, { recursive: true });

    for (const f of nft.files) {
      const dest = path.join(nftDir, `${f.role}.car`);

      // Check if already downloaded and verified
      if (fs.existsSync(dest) && fs.statSync(dest).size > 0) {
        const existingBuf = fs.readFileSync(dest);
        const existingHash = sha256hex(existingBuf);
        if (existingHash === f.expected_sha256 && existingBuf.length === f.expected_size) {
          dlSkip++;
          continue;
        }
        // Hash mismatch — re-download
        fs.unlinkSync(dest);
      }

      downloadTasks.push(async () => {
        try {
          const buf = await downloadTxid(f.txid, dest);

          // Verify SHA-256
          const actualHash = sha256hex(buf);
          if (actualHash !== f.expected_sha256) {
            verificationErrors.push({
              nft: nft.assetName, role: f.role, type: 'sha256_mismatch',
              expected: f.expected_sha256, actual: actualHash,
            });
            dlFail++;
            return;
          }

          // Verify size
          if (buf.length !== f.expected_size) {
            verificationErrors.push({
              nft: nft.assetName, role: f.role, type: 'size_mismatch',
              expected: f.expected_size, actual: buf.length,
            });
            dlFail++;
            return;
          }

          dlOk++;
          if ((dlOk + dlFail) % 20 === 0) {
            process.stdout.write(`\r   ${dlOk + dlFail}/${totalCars} CARs`);
          }
        } catch (err) {
          dlFail++;
          verificationErrors.push({
            nft: nft.assetName, role: f.role, type: 'download_failed',
            error: err.message,
          });
        }
      });
    }
  }

  if (downloadTasks.length > 0) {
    await runConcurrent(downloadTasks, DOWNLOAD_CONCURRENCY);
  }
  console.log(`\n   Downloads: ${dlOk} ok, ${dlFail} failed, ${dlSkip} cached`);

  if (verificationErrors.length > 0) {
    console.error('\n  ❌ Download/verification errors:');
    for (const e of verificationErrors.slice(0, 10)) {
      console.error(`    ${e.nft} [${e.role}] ${e.type}: ${e.expected || ''} → ${e.actual || e.error || ''}`);
    }
    if (verificationErrors.length > 10) console.error(`    ... and ${verificationErrors.length - 10} more`);
    process.exit(1);
  }
  console.log();

  // ── Step 6: Phase 2 — Verify root CIDs ─────────────────────────────

  console.log('🔍 Step 4: Verifying CAR root CIDs...');
  let cidPass = 0, cidFail = 0;

  for (const nft of nftList) {
    const nftDir = path.join(TMP_DIR, 'cars', `${nft.safeContract}_${nft.safeTokenId}`);
    for (const f of nft.files) {
      const carPath = path.join(nftDir, `${f.role}.car`);
      if (!fs.existsSync(carPath)) continue;

      try {
        const carData = fs.readFileSync(carPath);
        const actualRootCid = extractCarRootCid(carData);

        if (actualRootCid !== f.expected_root_cid) {
          verificationErrors.push({
            nft: nft.assetName, role: f.role, type: 'root_cid_mismatch',
            expected: f.expected_root_cid, actual: actualRootCid,
          });
          cidFail++;
        } else {
          cidPass++;
        }
      } catch (err) {
        verificationErrors.push({
          nft: nft.assetName, role: f.role, type: 'cid_extract_failed',
          error: err.message,
        });
        cidFail++;
      }
    }
  }

  console.log(`   Root CIDs: ${cidPass} pass, ${cidFail} fail`);

  if (cidFail > 0) {
    console.error('\n  ❌ Root CID verification errors:');
    for (const e of verificationErrors.filter(e => e.type.includes('cid'))) {
      console.error(`    ${e.nft} [${e.role}] ${e.type}: ${e.expected || ''} → ${e.actual || e.error || ''}`);
    }
    process.exit(1);
  }
  console.log();

  // ── Step 7: Phase 3 — Package and upload ────────────────────────────

  console.log('📤 Step 5: Packaging & uploading NFT archives...');
  let uploaded = 0, skipped = 0, upFail = 0;
  const uploadedAssetIds = new Map(); // assetName -> assetId

  for (const nft of nftList) {
    const nftDir = path.join(TMP_DIR, 'cars', `${nft.safeContract}_${nft.safeTokenId}`);
    const tarPath = path.join(TMP_DIR, nft.assetName);

    // If asset already exists, record it for verification
    if (existingAssets.has(nft.assetName)) {
      skipped++;
      uploadedAssetIds.set(nft.assetName, existingAssets.get(nft.assetName).id);
      continue;
    }

    // Build archive
    const tarFiles = [];
    const checksumLines = [];

    // manifest.json
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
        console.error(`  ❌ Missing: ${carPath}`);
        upFail++;
        continue;
      }

      const carData = fs.readFileSync(carPath);
      const carHash = sha256hex(carData);

      manifest.files.push({
        role: f.role.startsWith('media') ? 'media' : 'metadata',
        arweave_txid: f.txid,
        original_leaf_path: f.leaf_path,
        cid: f.expected_root_cid,
        match: f.match,
        size_bytes: carData.length,
        sha256: carHash,
        local_filename: `${f.role}.car`,
      });

      checksumLines.push(`${carHash}  ${f.role}.car`);
      tarFiles.push({ name: `${nft.safeContract}_${nft.safeTokenId}/${f.role}.car`, data: carData });
    }

    // Add manifest.json
    tarFiles.push({
      name: `${nft.safeContract}_${nft.safeTokenId}/manifest.json`,
      data: Buffer.from(JSON.stringify(manifest, null, 2)),
    });

    // Add checksums.sha256
    tarFiles.push({
      name: `${nft.safeContract}_${nft.safeTokenId}/checksums.sha256`,
      data: Buffer.from(checksumLines.join('\n') + '\n'),
    });

    // Create .tar
    const tarBuf = createTar(tarFiles);
    fs.writeFileSync(tarPath, tarBuf);

    // Upload
    try {
      const result = await uploadAsset(release.id, tarPath, nft.assetName);
      uploaded++;
      uploadedAssetIds.set(nft.assetName, result.id);
      if (uploaded % 10 === 0) {
        process.stdout.write(`\r   ${uploaded + skipped + upFail}/${nftList.length} NFTs`);
      }
    } catch (err) {
      console.error(`\n  ❌ Upload ${nft.assetName}: ${err.message}`);
      upFail++;
    }

    if (fs.existsSync(tarPath)) fs.unlinkSync(tarPath);
  }

  console.log(`\n   Uploads: ${uploaded} new | ${skipped} existing | ${upFail} failed`);

  if (upFail > 0) {
    console.error(`  ❌ ${upFail} uploads failed. Aborting.`);
    process.exit(1);
  }
  console.log();

  // ── Step 8: Phase 4 — Re-download & verify ALL assets ───────────────

  console.log('🔍 Step 6: Re-downloading & verifying ALL 175 Release assets...');
  let verifyPass = 0, verifyFail = 0;
  const assetVerificationResults = [];

  for (const nft of nftList) {
    const assetId = uploadedAssetIds.get(nft.assetName);
    if (!assetId) {
      console.error(`  ❌ ${nft.assetName}: no asset ID found`);
      verifyFail++;
      continue;
    }

    try {
      const assetBuf = await downloadAsset(assetId);
      const tarFiles = extractFilesFromTar(assetBuf);

      // Verify each CAR in the tar matches what we downloaded from Arweave
      let nftVerifyOk = true;
      for (const f of nft.files) {
        const expectedHash = f.expected_sha256;
        const tarEntry = tarFiles.find(t => t.name.endsWith(`${f.role}.car`));

        if (!tarEntry) {
          console.error(`  ❌ ${nft.assetName}: missing ${f.role}.car in tar`);
          nftVerifyOk = false;
          continue;
        }

        const actualHash = sha256hex(tarEntry.data);
        if (actualHash !== expectedHash) {
          console.error(`  ❌ ${nft.assetName} [${f.role}]: SHA-256 mismatch after re-download`);
          console.error(`     expected: ${expectedHash}`);
          console.error(`     actual  : ${actualHash}`);
          nftVerifyOk = false;
        }

        // Also verify root CID from the re-downloaded CAR
        try {
          const reRootCid = extractCarRootCid(tarEntry.data);
          if (reRootCid !== f.expected_root_cid) {
            console.error(`  ❌ ${nft.assetName} [${f.role}]: root CID mismatch after re-download`);
            nftVerifyOk = false;
          }
        } catch (err) {
          console.error(`  ❌ ${nft.assetName} [${f.role}]: CID extract failed: ${err.message}`);
          nftVerifyOk = false;
        }
      }

      if (nftVerifyOk) {
        verifyPass++;
      } else {
        verifyFail++;
      }

      assetVerificationResults.push({
        asset_name: nft.assetName,
        verified: nftVerifyOk,
        car_count: nft.files.length,
      });

      if ((verifyPass + verifyFail) % 20 === 0) {
        process.stdout.write(`\r   ${verifyPass + verifyFail}/${nftList.length} verified`);
      }
    } catch (err) {
      console.error(`\n  ❌ ${nft.assetName}: re-download failed: ${err.message}`);
      verifyFail++;
      assetVerificationResults.push({
        asset_name: nft.assetName, verified: false, error: err.message,
      });
    }
  }

  console.log(`\n   Verified: ${verifyPass} pass, ${verifyFail} fail`);
  console.log();

  if (verifyFail > 0) {
    console.error(`  ❌ ${verifyFail} re-verification failures. Aborting.`);
    process.exit(1);
  }

  // ── Step 9: Generate RELEASE-MANIFEST.json ──────────────────────────

  console.log('📄 Step 7: Generating RELEASE-MANIFEST.json & RELEASE-CHECKSUMS.sha256...');

  const manifestEntries = nftList.map(nft => ({
    contract: nft.contract,
    token_id: nft.tokenId,
    nft_asset_name: nft.assetName,
    car_count: nft.files.length,
    files: nft.files.map(f => ({
      role: f.role.startsWith('media') ? 'media' : 'metadata',
      arweave_txid: f.txid,
      expected_sha256: f.expected_sha256,
      expected_size: f.expected_size,
      expected_root_cid: f.expected_root_cid,
      leaf_path: f.leaf_path,
      match: f.match,
    })),
  }));

  const releaseManifest = {
    schema: 'nft-arweave-mirror-manifest-v3',
    release_tag: RELEASE_TAG,
    generated_at: new Date().toISOString(),
    source_index_commit: sourceCommit,
    source_index_file: TOKEN_INDEX_FILE,
    expected_nfts: EXPECTED_NFTS,
    actual_nfts: nftList.length,
    nft_archive_asset_count: nftList.length,
    total_car_files: totalCars,
    total_unique_arweave_txids: allTxids.size,
    all_car_sha256_match_token_index: verifyPass === nftList.length,
    all_car_size_match_token_index: verifyPass === nftList.length,
    all_car_root_cid_match_token_index: verifyPass === nftList.length,
    all_release_assets_reverified: verifyPass === nftList.length,
    verification_status: (verifyPass === nftList.length && verifyFail === 0) ? 'PASS' : 'FAIL',
    per_nft_assets: manifestEntries,
  };

  // Write and upload RELEASE-MANIFEST.json
  const manifestPath = path.join(TMP_DIR, 'RELEASE-MANIFEST.json');
  fs.writeFileSync(manifestPath, JSON.stringify(releaseManifest, null, 2));

  // Delete old manifest/checksums if they exist
  for (const oldName of ['RELEASE-MANIFEST.json', 'RELEASE-CHECKSUMS.sha256']) {
    if (existingAssets.has(oldName)) {
      await deleteAsset(release.id, existingAssets.get(oldName).id);
    }
  }

  await uploadAsset(release.id, manifestPath, 'RELEASE-MANIFEST.json');
  console.log('  ✅ RELEASE-MANIFEST.json uploaded');

  // Generate RELEASE-CHECKSUMS.sha256
  const checksumLines = [];
  checksumLines.push(`# RELEASE-CHECKSUMS.sha256 — ${RELEASE_TAG}`);
  checksumLines.push(`# Generated: ${new Date().toISOString()}`);
  checksumLines.push(`# Every line: sha256  asset_name`);
  checksumLines.push('');
  for (const nft of nftList) {
    // Read the tar we just uploaded (re-download for consistency)
    const assetId = uploadedAssetIds.get(nft.assetName);
    if (!assetId) continue;
    // We already verified these — use the known hash from the CAR files
    // For the tar itself, we need its hash. Re-download and hash.
    const buf = await downloadAsset(assetId);
    const tarHash = sha256hex(buf);
    checksumLines.push(`${tarHash}  ${nft.assetName}`);
  }
  // Add manifest itself
  const manifestBuf = fs.readFileSync(manifestPath);
  checksumLines.push(`${sha256hex(manifestBuf)}  RELEASE-MANIFEST.json`);

  const checksumsPath = path.join(TMP_DIR, 'RELEASE-CHECKSUMS.sha256');
  fs.writeFileSync(checksumsPath, checksumLines.join('\n') + '\n');
  await uploadAsset(release.id, checksumsPath, 'RELEASE-CHECKSUMS.sha256');
  console.log('  ✅ RELEASE-CHECKSUMS.sha256 uploaded');

  // ── Final summary ───────────────────────────────────────────────────

  console.log();
  console.log('═══════════════════════════════════════════════════════════');
  console.log(`  ✅ Downloads   : ${dlOk + dlSkip} CARs (${allTxids.size} unique txids)`);
  console.log(`  ✅ SHA-256     : all ${totalCars} CARs match token_index`);
  console.log(`  ✅ Size        : all ${totalCars} CARs match token_index`);
  console.log(`  ✅ Root CID    : all ${totalCars} CARs match token_index`);
  console.log(`  📤 Uploads     : ${uploaded} new | ${skipped} existing`);
  console.log(`  🔍 Re-verified : ${verifyPass} / ${nftList.length} assets`);
  console.log(`  📊 Release     : ${nftList.length} NFT assets + manifest + checksums`);
  console.log(`  📄 Status      : ${releaseManifest.verification_status}`);
  console.log('═══════════════════════════════════════════════════════════');

  if (releaseManifest.verification_status !== 'PASS') {
    console.error('\n  ❌ FAIL');
    process.exit(1);
  }

  console.log('\n  🎉 All 175 NFTs mirrored and fully verified!');
}

main().catch(err => {
  console.error('Fatal:', err);
  process.exit(1);
});
