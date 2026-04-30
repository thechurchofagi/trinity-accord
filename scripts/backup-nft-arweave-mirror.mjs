#!/usr/bin/env node
/**
 * backup-nft-arweave-mirror.mjs  (v4 — strict verification, no shortcuts)
 *
 * Strict Arweave → GitHub Release mirror for 175 NFTs.
 *
 * Verification layers:
 *   1. SHA-256 of every downloaded CAR == token_index car_sha256
 *   2. Size of every downloaded CAR   == token_index car_size
 *   3. Root CID extracted from CAR    == token_index root_cid
 *   4. Every uploaded Release asset is re-downloaded and re-verified (ALL 175, no skip)
 *   5. RELEASE-MANIFEST.json + RELEASE-CHECKSUMS.sha256 uploaded as final assets
 *   6. Optional: onchain tokenURI CID == token_index metadata.root_cid
 *
 * Re-run behavior: ALL old nft-*.tar assets are deleted before upload.
 * Every asset is freshly uploaded and fully re-verified. No silent reuse.
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
const ETH_RPC_URL = process.env.ETH_RPC_URL || '';
const REPO = process.env.REPO || 'thechurchofagi/trinity-accord';
const RELEASE_TAG = process.env.RELEASE_TAG || 'nft-arweave-mirror-175-v1';
const TOKEN_INDEX_FILE = 'token_index.json';
const TMP_DIR = '/tmp/nft-arweave-mirror';
const GATEWAYS = ['https://arweave.net', 'https://ar-io.net'];
const EXPECTED_NFTS = 175;
const MAX_RETRIES = 3;
const DOWNLOAD_CONCURRENCY = 5;
const UPLOAD_CONCURRENCY = 2;

// ERC-721 tokenURI(uint256) selector
const ERC721_TOKENURI_SELECTOR = '0xc87b56dd';
// ERC-1155 uri(uint256) selector
const ERC1155_URI_SELECTOR = '0x0e89341c';

// ─── Helpers ───────────────────────────────────────────────────────────────

function sha256hex(buf) {
  return crypto.createHash('sha256').update(buf).digest('hex');
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function log(msg) { console.log(msg); }
function err(msg) { console.error(msg); }

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

function extractCarRootCid(carData) {
  const headerEnd = parseCarHeader(carData);
  const header = carData.slice(0, headerEnd);

  for (let i = 0; i < header.length - 2; i++) {
    if (header[i] === 0xd8 && header[i + 1] === 0x2a) {
      let cidStart = i + 2;
      let cidLen = 0;

      if (header[cidStart] === 0x58) {
        cidLen = header[cidStart + 1];
        cidStart += 2;
      } else if (header[cidStart] === 0x59) {
        cidLen = (header[cidStart + 1] << 8) | header[cidStart + 2];
        cidStart += 3;
      } else {
        cidLen = header[cidStart] - 0x40;
        cidStart += 1;
      }

      const cidBytes = header.slice(cidStart, cidStart + cidLen);
      return cidBytesToCidV1(cidBytes);
    }
  }

  throw new Error('Could not extract root CID from CAR header — no CBOR tag(42) found. Header hex: ' + header.slice(0, Math.min(header.length, 64)).toString('hex'));
}

function cidBytesToCidV1(bytes) {
  // Strip leading zero bytes (some CAR packagers prefix 0x00)
  while (bytes.length > 0 && bytes[0] === 0x00) {
    bytes = bytes.slice(1);
  }
  if (bytes.length === 0) throw new Error('Empty CID bytes after stripping zeros');

  if (bytes[0] === 0x12 && bytes[1] === 0x20) {
    // CIDv0 — sha2-256 multihash. Convert to CIDv1 dag-cbor.
    const cidV1Bytes = Buffer.concat([Buffer.from([0x01, 0x71]), bytes]);
    return base32EncodeCid(cidV1Bytes);
  }
  if (bytes[0] === 0x01) {
    return base32EncodeCid(bytes);
  }
  return 'b' + bytes.toString('hex');
}

function base32EncodeCid(bytes) {
  const alphabet = 'abcdefghijklmnopqrstuvwxyz234567';
  let bits = 0, value = 0, output = 'b'; // 'b' = multibase prefix for base32-lower
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

// ─── GitHub helpers ────────────────────────────────────────────────────────

function ghHeaders(extra = {}) {
  return { Authorization: `Bearer ${GITHUB_TOKEN}`, Accept: 'application/vnd.github+json', ...extra };
}

async function ghFetch(url, opts = {}) {
  const res = await fetch(url, opts);
  return res;
}

async function ensureRelease() {
  const res = await ghFetch(
    `https://api.github.com/repos/${REPO}/releases/tags/${RELEASE_TAG}`,
    { headers: ghHeaders() }
  );
  if (res.ok) {
    const rel = await res.json();
    log(`  Release ${RELEASE_TAG} exists (id: ${rel.id})`);
    return rel;
  }
  log(`  Creating release ${RELEASE_TAG}...`);
  const create = await ghFetch(`https://api.github.com/repos/${REPO}/releases`, {
    method: 'POST',
    headers: ghHeaders({ 'Content-Type': 'application/json' }),
    body: JSON.stringify({
      tag_name: RELEASE_TAG,
      name: `NFT Arweave Mirror — 175 NFTs (strict verified v4)`,
      body: [
        `## Strict Arweave → GitHub Release Mirror (v4)`,
        ``,
        `175 individual NFT archives with full verification:`,
        `- SHA-256 match against token_index`,
        `- CAR size match against token_index`,
        `- Root CID match against token_index`,
        `- Re-download verification after upload (ALL assets, no skip)`,
        `- Optional: onchain tokenURI CID verification`,
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

async function getAllAssets(releaseId) {
  const assets = new Map();
  let page = 1;
  while (true) {
    const res = await ghFetch(
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
    const res = await ghFetch(url, {
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
  const res = await ghFetch(
    `https://api.github.com/repos/${REPO}/releases/assets/${assetId}`,
    { method: 'DELETE', headers: ghHeaders() }
  );
  if (!res.ok && res.status !== 404) {
    throw new Error(`Delete asset failed: ${res.status}`);
  }
}

async function downloadAsset(assetId) {
  const res = await ghFetch(
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

// ─── ETH on-chain verification ─────────────────────────────────────────────

/**
 * Try calling a function on-chain. Returns the decoded string or null.
 */
async function tryEthCall(rpcUrl, contractAddr, tokenId, selector) {
  try {
    const paddedId = BigInt(tokenId).toString(16).padStart(64, '0');
    const callData = selector + paddedId;

    const res = await fetch(rpcUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0', id: 1,
        method: 'eth_call',
        params: [{ to: contractAddr, data: callData }, 'latest'],
      }),
    });

    const json = await res.json();
    if (json.error) return null;

    const hex = json.result;
    if (!hex || hex === '0x' || hex.length < 130) return null;

    // ABI decode dynamic bytes/string: offset(32) + length(32) + data
    const offset = parseInt(hex.slice(2, 66), 16) * 2 + 2;
    const len = parseInt(hex.slice(66, 130), 16) * 2;
    const strHex = hex.slice(130, 130 + len);

    let uri = '';
    for (let i = 0; i < strHex.length; i += 2) {
      uri += String.fromCharCode(parseInt(strHex.slice(i, i + 2), 16));
    }
    return uri || null;
  } catch {
    return null;
  }
}

/**
 * Fetch on-chain tokenURI. Tries ERC-721 tokenURI first, then ERC-1155 uri.
 * Returns the decoded URI string, or null if neither succeeds.
 */
async function fetchOnchainTokenURI(contractAddr, tokenId, rpcUrl) {
  // Try ERC-721 tokenURI(uint256) first
  const erc721Uri = await tryEthCall(rpcUrl, contractAddr, tokenId, ERC721_TOKENURI_SELECTOR);
  if (erc721Uri) return erc721Uri;

  // Fallback: ERC-1155 uri(uint256)
  const erc1155Uri = await tryEthCall(rpcUrl, contractAddr, tokenId, ERC1155_URI_SELECTOR);
  return erc1155Uri;
}

/**
 * Extract CID from a tokenURI string.
 * Handles:
 *   ipfs://CID, ipfs://ipfs/CID, ipfs://CID/path
 *   ar://CID
 *   https://arweave.net/TXID
 *   https://.../ipfs/CID, https://.../ipfs/CID/path
 * Also handles ERC-1155 {id} replacement.
 */
function extractCidFromUri(uri) {
  if (!uri) return null;

  // ipfs://CID or ipfs://ipfs/CID or ipfs://CID/path
  const ipfsMatch = uri.match(/ipfs:\/\/(?:ipfs\/)?([a-zA-Z0-9]+)/);
  if (ipfsMatch) return ipfsMatch[1];

  // https://.../ipfs/CID or https://.../ipfs/CID/path
  const httpsIpfsMatch = uri.match(/\/ipfs\/([a-zA-Z0-9]+)/);
  if (httpsIpfsMatch) return httpsIpfsMatch[1];

  // ar://CID
  const arMatch = uri.match(/ar:\/\/([a-zA-Z0-9_-]+)/);
  if (arMatch) return arMatch[1];

  // https://arweave.net/TXID
  const arHttpMatch = uri.match(/arweave\.net\/([a-zA-Z0-9_-]+)/);
  if (arHttpMatch) return arHttpMatch[1];

  return null;
}

/**
 * Replace ERC-1155 {id} placeholder in URI with hex-padded tokenId.
 */
function expandErc1155Id(uri, tokenId) {
  if (!uri || !uri.includes('{id}')) return uri;
  const hexId = BigInt(tokenId).toString(16).padStart(64, '0');
  return uri.replace('{id}', hexId);
}

// ─── Main ──────────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  const dryRun = args.includes('--dry-run');
  const contractFilter = args.includes('--contract') ? args[args.indexOf('--contract') + 1] : null;

  let sourceCommit = 'unknown';
  try { sourceCommit = execSync('git rev-parse HEAD', { encoding: 'utf-8' }).trim(); } catch {}

  log('═══════════════════════════════════════════════════════════');
  log('  NFT Arweave → GitHub Release Strict Mirror (v4)');
  log('═══════════════════════════════════════════════════════════');
  log(`  Token Index: ${TOKEN_INDEX_FILE}`);
  log(`  Release    : ${RELEASE_TAG}`);
  log(`  Concurrency: dl=${DOWNLOAD_CONCURRENCY}, ul=${UPLOAD_CONCURRENCY}`);
  log(`  ETH RPC    : ${ETH_RPC_URL ? 'configured' : 'not set (skipping onchain check)'}`);
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
            // Preserve original match value exactly (exact, cid_only, etc.)
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
        metadataRootCid: meta.root_cid || null,
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
        log(`    ${f.role}: sha256=${f.expected_sha256?.slice(0, 16)}... size=${f.expected_size} root_cid=${f.expected_root_cid?.slice(0, 20)}... match=${f.match}`);
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

  // ── Step 4: ALWAYS delete old nft-*.tar + manifest + checksums ─────
  // No silent reuse. Every run is a clean rebuild with full verification.

  log('  Cleaning old NFT assets for mandatory full re-verification...');
  let deleted = 0;
  for (const [name, asset] of existingAssets) {
    if (name.startsWith('nft-') || name === 'RELEASE-MANIFEST.json' || name === 'RELEASE-CHECKSUMS.sha256') {
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

      // Check if already downloaded and verified (from a previous partial run)
      if (fs.existsSync(dest) && fs.statSync(dest).size > 0) {
        const existingBuf = fs.readFileSync(dest);
        const existingHash = sha256hex(existingBuf);
        if (existingHash === f.expected_sha256 && existingBuf.length === f.expected_size) {
          dlSkip++;
          sha256MatchCount++;
          sizeMatchCount++;
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
          sha256MatchCount++;

          // Verify size
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

  // ── Step 6: Verify root CIDs ───────────────────────────────────────

  log('🔍 Step 4: Verifying CAR root CIDs...');
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
      } catch (e) {
        verificationErrors.push({
          nft: nft.assetName, role: f.role, type: 'cid_extract_failed',
          error: e.message,
        });
        cidFail++;
      }
    }
  }

  log(`   Root CIDs: ${cidPass} pass, ${cidFail} fail`);

  if (cidFail > 0) {
    err('\n  ❌ Root CID verification errors:');
    for (const e of verificationErrors.filter(e => e.type.includes('cid'))) {
      err(`    ${e.nft} [${e.role}] ${e.type}: ${e.expected || ''} → ${e.actual || e.error || ''}`);
    }
    process.exit(1);
  }
  log('');

  // ── Step 7 (optional): ETH on-chain tokenURI verification ──────────

  let onchainPass = 0, onchainFail = 0, onchainSkip = 0;
  const onchainErrors = [];

  if (ETH_RPC_URL) {
    log('🔗 Step 4b: Verifying on-chain tokenURI CIDs...');
    const ethTasks = [];

    for (const nft of nftList) {
      ethTasks.push(async () => {
        try {
          let uri = await fetchOnchainTokenURI(nft.contract, nft.tokenId, ETH_RPC_URL);
          if (!uri) {
            onchainErrors.push({
              nft: nft.assetName, type: 'onchain_no_uri',
              error: 'Neither tokenURI nor uri returned a value',
            });
            onchainSkip++;
            return;
          }

          // Handle ERC-1155 {id} placeholder
          uri = expandErc1155Id(uri, nft.tokenId);

          const onchainCid = extractCidFromUri(uri);
          if (!onchainCid) {
            onchainErrors.push({
              nft: nft.assetName, type: 'onchain_cid_parse_failed',
              error: `Could not extract CID from URI: ${uri}`,
            });
            onchainSkip++;
            return;
          }

          // Compare: onchain CID == token_index metadata.root_cid
          if (onchainCid !== nft.metadataRootCid) {
            onchainErrors.push({
              nft: nft.assetName, type: 'onchain_cid_mismatch',
              onchain: onchainCid, token_index: nft.metadataRootCid,
            });
            onchainFail++;
          } else {
            onchainPass++;
          }
        } catch (e) {
          onchainErrors.push({
            nft: nft.assetName, type: 'onchain_error',
            error: e.message,
          });
          onchainFail++;
        }
      });
    }

    await runConcurrent(ethTasks, DOWNLOAD_CONCURRENCY);
    log(`   On-chain: ${onchainPass} pass, ${onchainFail} fail, ${onchainSkip} skipped`);

    // When ETH_RPC_URL is set, ALL 175 must pass. No skip allowed.
    if (onchainFail > 0 || onchainSkip > 0) {
      err('\n  ❌ On-chain verification failed:');
      if (onchainFail > 0) err(`    ${onchainFail} CID mismatches`);
      if (onchainSkip > 0) err(`    ${onchainSkip} could not read/parse on-chain URI`);
      for (const e of onchainErrors.slice(0, 10)) {
        err(`    ${e.nft}: ${e.type} — ${e.onchain || e.error || ''}`);
      }
      if (onchainErrors.length > 10) err(`    ... and ${onchainErrors.length - 10} more`);
      process.exit(1);
    }
    log('');
  } else {
    log('⏭️  Step 4b: ETH_RPC_URL not set, skipping on-chain verification');
    log('');
  }

  // ── Step 8: Package and upload ─────────────────────────────────────

  log('📤 Step 5: Packaging & uploading NFT archives...');
  let uploaded = 0, upFail = 0;
  const uploadedAssetIds = new Map();

  for (const nft of nftList) {
    const nftDir = path.join(TMP_DIR, 'cars', `${nft.safeContract}_${nft.safeTokenId}`);
    const tarPath = path.join(TMP_DIR, nft.assetName);

    // Build archive
    const tarFiles = [];
    const checksumLines = [];

    // manifest.json — preserve original match values from token_index
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
        err(`  ❌ Missing: ${carPath}`);
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
        // Preserve original match value: exact, cid_only, or whatever token_index has
        match: f.match,
        size_bytes: carData.length,
        sha256: carHash,
        local_filename: `${f.role}.car`,
      });

      checksumLines.push(`${carHash}  ${f.role}.car`);
      tarFiles.push({
        name: `nft/${f.role}.car`,
        data: carData,
      });
    }

    // Add manifest.json
    tarFiles.push({
      name: `nft/manifest.json`,
      data: Buffer.from(JSON.stringify(manifest, null, 2)),
    });

    // Add checksums.sha256
    tarFiles.push({
      name: `nft/checksums.sha256`,
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
        process.stdout.write(`\r   ${uploaded + upFail}/${nftList.length} NFTs`);
      }
    } catch (e) {
      err(`\n  ❌ Upload ${nft.assetName}: ${e.message}`);
      upFail++;
    }

    if (fs.existsSync(tarPath)) fs.unlinkSync(tarPath);
  }

  log(`\n   Uploads: ${uploaded} uploaded, ${upFail} failed`);

  if (upFail > 0) {
    err(`  ❌ ${upFail} uploads failed. Aborting.`);
    process.exit(1);
  }
  log('');

  // ── Step 9: Re-download & verify ALL 175 Release assets ────────────
  // No skipped-existing bypass. Every single asset is downloaded and verified.

  log('🔍 Step 6: Re-downloading & verifying ALL 175 Release assets...');
  let reVerifySha256Pass = 0, reVerifySizePass = 0, reVerifyCidPass = 0;
  let reVerifyFail = 0;
  const reVerifyErrors = [];

  for (const nft of nftList) {
    const assetId = uploadedAssetIds.get(nft.assetName);
    if (!assetId) {
      err(`  ❌ ${nft.assetName}: no asset ID found`);
      reVerifyFail++;
      continue;
    }

    try {
      const assetBuf = await downloadAsset(assetId);
      const tarFiles = extractFilesFromTar(assetBuf);

      let nftSha256Ok = true, nftSizeOk = true, nftCidOk = true;

      for (const f of nft.files) {
        const tarEntry = tarFiles.find(t => t.name === `nft/${f.role}.car`);

        if (!tarEntry) {
          err(`  ❌ ${nft.assetName}: missing ${f.role}.car in tar`);
          nftSha256Ok = false;
          nftSizeOk = false;
          nftCidOk = false;
          continue;
        }

        // SHA-256 check
        const actualHash = sha256hex(tarEntry.data);
        if (actualHash !== f.expected_sha256) {
          err(`  ❌ ${nft.assetName} [${f.role}]: SHA-256 mismatch after re-download`);
          nftSha256Ok = false;
        }

        // Size check
        if (tarEntry.data.length !== f.expected_size) {
          err(`  ❌ ${nft.assetName} [${f.role}]: size mismatch after re-download`);
          nftSizeOk = false;
        }

        // Root CID check
        try {
          const reRootCid = extractCarRootCid(tarEntry.data);
          if (reRootCid !== f.expected_root_cid) {
            err(`  ❌ ${nft.assetName} [${f.role}]: root CID mismatch after re-download`);
            nftCidOk = false;
          }
        } catch (e) {
          err(`  ❌ ${nft.assetName} [${f.role}]: CID extract failed: ${e.message}`);
          nftCidOk = false;
        }
      }

      if (nftSha256Ok) reVerifySha256Pass++;
      if (nftSizeOk) reVerifySizePass++;
      if (nftCidOk) reVerifyCidPass++;
      if (!nftSha256Ok || !nftSizeOk || !nftCidOk) reVerifyFail++;

      if ((reVerifySha256Pass + reVerifyFail) % 20 === 0) {
        process.stdout.write(`\r   ${reVerifySha256Pass + reVerifyFail}/${nftList.length} verified`);
      }
    } catch (e) {
      err(`\n  ❌ ${nft.assetName}: re-download failed: ${e.message}`);
      reVerifyFail++;
    }
  }

  log(`\n   Re-verified SHA-256 : ${reVerifySha256Pass} / ${nftList.length}`);
  log(`   Re-verified Size    : ${reVerifySizePass} / ${nftList.length}`);
  log(`   Re-verified Root CID: ${reVerifyCidPass} / ${nftList.length}`);
  log('');

  if (reVerifyFail > 0) {
    err(`  ❌ ${reVerifyFail} re-verification failures. Aborting.`);
    process.exit(1);
  }

  // ── Step 10: Generate RELEASE-MANIFEST.json ────────────────────────

  log('📄 Step 7: Generating RELEASE-MANIFEST.json & RELEASE-CHECKSUMS.sha256...');

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

  const allSha256Match = sha256MatchCount === totalCars;
  const allSizeMatch = sizeMatchCount === totalCars;
  const allCidMatch = cidPass === totalCars;
  const allReVerified = reVerifyFail === 0 && reVerifySha256Pass === nftList.length;
  // When ETH_RPC_URL is set: all 175 must pass, 0 fail, 0 skip
  const allOnchainOk = ETH_RPC_URL
    ? (onchainPass === EXPECTED_NFTS && onchainFail === 0 && onchainSkip === 0)
    : true;

  const overallPass = allSha256Match && allSizeMatch && allCidMatch && allReVerified && allOnchainOk;

  const releaseManifest = {
    schema: 'nft-arweave-mirror-manifest-v4',
    release_tag: RELEASE_TAG,
    generated_at: new Date().toISOString(),
    source_index_commit: sourceCommit,
    source_index_file: TOKEN_INDEX_FILE,
    expected_nfts: EXPECTED_NFTS,
    actual_nfts: nftList.length,
    nft_archive_asset_count: nftList.length,
    total_car_files: totalCars,
    total_unique_arweave_txids: allTxids.size,
    all_car_sha256_match_token_index: allSha256Match,
    all_car_size_match_token_index: allSizeMatch,
    all_car_root_cid_match_token_index: allCidMatch,
    all_release_assets_reverified: allReVerified,
    onchain_tokenuri_verified: ETH_RPC_URL ? true : false,
    onchain_all_match: allOnchainOk,
    verification_status: overallPass ? 'PASS' : 'FAIL',
    verification_details: {
      arweave_download: { ok: dlOk + dlSkip, fail: dlFail },
      sha256_check: { pass: sha256MatchCount, total: totalCars },
      size_check: { pass: sizeMatchCount, total: totalCars },
      root_cid_check: { pass: cidPass, total: totalCars },
      release_reverify_sha256: { pass: reVerifySha256Pass, total: nftList.length },
      release_reverify_size: { pass: reVerifySizePass, total: nftList.length },
      release_reverify_cid: { pass: reVerifyCidPass, total: nftList.length },
      onchain_check: ETH_RPC_URL
        ? { pass: onchainPass, fail: onchainFail, skip: onchainSkip }
        : { skipped: true, reason: 'ETH_RPC_URL not set' },
    },
    per_nft_assets: manifestEntries,
  };

  // Write and upload RELEASE-MANIFEST.json
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
    const assetId = uploadedAssetIds.get(nft.assetName);
    if (!assetId) continue;
    const buf = await downloadAsset(assetId);
    checksumLines.push(`${sha256hex(buf)}  ${nft.assetName}`);
  }
  const manifestBuf = fs.readFileSync(manifestPath);
  checksumLines.push(`${sha256hex(manifestBuf)}  RELEASE-MANIFEST.json`);

  const checksumsPath = path.join(TMP_DIR, 'RELEASE-CHECKSUMS.sha256');
  fs.writeFileSync(checksumsPath, checksumLines.join('\n') + '\n');
  await uploadAsset(release.id, checksumsPath, 'RELEASE-CHECKSUMS.sha256');
  log('  ✅ RELEASE-CHECKSUMS.sha256 uploaded');

  // ── Final summary ──────────────────────────────────────────────────

  log('');
  log('═══════════════════════════════════════════════════════════');
  log(`  ✅ Downloads      : ${dlOk + dlSkip} CARs (${allTxids.size} unique txids)`);
  log(`  ✅ SHA-256        : ${sha256MatchCount}/${totalCars} CARs match token_index`);
  log(`  ✅ Size           : ${sizeMatchCount}/${totalCars} CARs match token_index`);
  log(`  ✅ Root CID       : ${cidPass}/${totalCars} CARs match token_index`);
  log(`  📤 Uploads        : ${uploaded} uploaded`);
  log(`  🔍 Re-verified    : SHA256=${reVerifySha256Pass} Size=${reVerifySizePass} CID=${reVerifyCidPass} / ${nftList.length}`);
  if (ETH_RPC_URL) {
    log(`  🔗 On-chain       : ${onchainPass} pass, ${onchainFail} fail, ${onchainSkip} skip`);
  }
  log(`  📊 Release        : ${nftList.length} NFT assets + manifest + checksums`);
  log(`  📄 Status         : ${releaseManifest.verification_status}`);
  log('═══════════════════════════════════════════════════════════');

  if (!overallPass) {
    err('\n  ❌ FAIL — one or more verification checks did not pass');
    process.exit(1);
  }

  log('\n  🎉 All 175 NFTs mirrored and fully verified!');
}

main().catch(e => {
  err('Fatal:', e);
  process.exit(1);
});
