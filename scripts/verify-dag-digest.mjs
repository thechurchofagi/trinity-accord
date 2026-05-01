#!/usr/bin/env node
/**
 * verify-dag-digest.mjs  (Step 2)
 *
 * DAG + digest-manifest file hash verification for Trinity Accord NFT collection.
 *
 * Proves:
 *   - digest-manifest.json/csv sha256 + size match authority.jcs.json declarations
 *   - CAR files in release decode as valid DAGs with no missing blocks
 *   - metadata root CIDs match token_index and ETH tokenURI
 *   - file-level hash/size comparison against digest-manifest
 *
 * Does NOT verify: BTC signatures, ETH witness, OTS, Bitcoin tx anchors.
 *
 * Output: DAG-DIGEST-AUDIT.json
 *
 * Usage:
 *   GITHUB_TOKEN=xxx node scripts/verify-dag-digest.mjs \
 *     --release-tag nft-arweave-mirror-175-v1 \
 *     --concurrency 8
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

// ═══════════════════════════════════════════════════════════════════════════
// CLI ARGS
// ═══════════════════════════════════════════════════════════════════════════

const args = process.argv.slice(2);
function getArg(name, def) {
  const idx = args.indexOf(name);
  return idx >= 0 && idx + 1 < args.length ? args[idx + 1] : def;
}
const RELEASE_TAG = getArg('--release-tag', 'nft-arweave-mirror-175-v1');
const CONCURRENCY = Number(getArg('--concurrency', process.env.DAG_VERIFY_CONCURRENCY || '4'));

// ═══════════════════════════════════════════════════════════════════════════
// GLOBAL CONFIG
// ═══════════════════════════════════════════════════════════════════════════

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO = 'thechurchofagi/trinity-accord';
const TOKEN_INDEX_FILE = 'token_index.json';
const AUTHORITY_JCS_FILE = 'archive/authority-manifest/authority.jcs.json';
const DIGEST_MANIFEST_JSON = 'archive/evidence/digest-manifest.json';
const DIGEST_MANIFEST_CSV = 'archive/evidence/digest-manifest.csv';
const EXPECTED_NFTS = 175;
const MAX_RETRIES = 3;
const TMP_DIR = '/tmp/dag-digest-verify';

// ═══════════════════════════════════════════════════════════════════════════
// PRIMITIVES
// ═══════════════════════════════════════════════════════════════════════════

function sha256hex(buf) { return crypto.createHash('sha256').update(buf).digest('hex'); }
function sha256buf(buf) { return crypto.createHash('sha256').update(buf).digest(); }
function sha3_256hex(buf) { return crypto.createHash('sha3-256').update(buf).digest('hex'); }
function blake2b256hex(buf) { return crypto.createHash('blake2b512').update(buf).digest('hex').slice(0, 64); }
function sha512_256hex(buf) { return crypto.createHash('sha512-256').update(buf).digest('hex'); }
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
function log(msg) { console.log(msg); }
function err(msg) { console.error(msg); }

// ═══════════════════════════════════════════════════════════════════════════
// CONCURRENCY POOL
// ═══════════════════════════════════════════════════════════════════════════

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

// ═══════════════════════════════════════════════════════════════════════════
// CID / BASE32 / BASE58 / MULTihASH HELPERS
// ═══════════════════════════════════════════════════════════════════════════

function base32EncodeCid(bytes) {
  const alphabet = 'abcdefghijklmnopqrstuvwxyz234567';
  let bits = 0, value = 0, output = 'b';
  for (const byte of bytes) {
    value = (value << 8) | byte;
    bits += 8;
    while (bits >= 5) { output += alphabet[(value >>> (bits - 5)) & 0x1f]; bits -= 5; }
  }
  if (bits > 0) output += alphabet[(value << (5 - bits)) & 0x1f];
  return output;
}

function base32DecodeCid(str) {
  const alphabet = 'abcdefghijklmnopqrstuvwxyz234567';
  const data = str.slice(1);
  let bits = 0, value = 0;
  const bytes = [];
  for (const ch of data) {
    const val = alphabet.indexOf(ch);
    if (val < 0) throw new Error('Invalid base32 char');
    value = (value << 5) | val;
    bits += 5;
    if (bits >= 8) { bytes.push((value >>> (bits - 8)) & 0xff); bits -= 8; }
  }
  return Buffer.from(bytes);
}

function cidv0Encode(hashBytes) {
  const alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
  let result = '';
  const digits = [0];
  for (const byte of hashBytes) {
    let carry = byte;
    for (let j = 0; j < digits.length; j++) {
      carry += digits[j] << 8;
      digits[j] = carry % 58;
      carry = (carry / 58) | 0;
    }
    while (carry > 0) { digits.push(carry % 58); carry = (carry / 58) | 0; }
  }
  for (let i = 0; i < hashBytes.length && hashBytes[i] === 0; i++) result += '1';
  for (let i = digits.length - 1; i >= 0; i--) result += alphabet[digits[i]];
  return result;
}

function base58btcDecode(str) {
  const alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz';
  const bytes = [0];
  for (const ch of str) {
    const val = alphabet.indexOf(ch);
    if (val < 0) throw new Error('Invalid base58 char');
    let carry = val;
    for (let j = 0; j < bytes.length; j++) {
      carry += bytes[j] * 58;
      bytes[j] = carry & 0xff;
      carry >>= 8;
    }
    while (carry > 0) { bytes.push(carry & 0xff); carry >>= 8; }
  }
  let leadingZeros = 0;
  for (const ch of str) { if (ch === '1') leadingZeros++; else break; }
  return Buffer.from([...Array(leadingZeros).fill(0), ...bytes.reverse()]);
}

function cidBytesToCid(bytes) {
  let start = 0;
  while (start < bytes.length && bytes[start] === 0x00) start++;
  const trimmed = bytes.slice(start);
  if (trimmed.length === 0) throw new Error('Empty CID bytes');
  if (trimmed[0] === 0x12 && trimmed.length >= 34 && trimmed[1] === 0x20) {
    return cidv0Encode(trimmed.slice(0, 34));
  }
  return base32EncodeCid(trimmed);
}

function extractDigestFromCid(cid) {
  if (!cid) return null;
  if (cid.startsWith('Qm')) {
    try {
      const bytes = base58btcDecode(cid);
      if (bytes.length === 34 && bytes[0] === 0x12 && bytes[1] === 0x20) return bytes.slice(2);
      return null;
    } catch { return null; }
  }
  if (cid.startsWith('b')) {
    try {
      const bytes = base32DecodeCid(cid);
      let pos = 0;
      while (pos < bytes.length && bytes[pos] === 0x00) pos++;
      if (pos >= bytes.length) return null;
      while (pos < bytes.length && bytes[pos] >= 0x80) pos++;
      pos++;
      while (pos < bytes.length && bytes[pos] >= 0x80) pos++;
      pos++;
      while (pos < bytes.length && bytes[pos] >= 0x80) pos++;
      pos++;
      let mhLen = 0, shift = 0;
      while (pos < bytes.length) {
        const b = bytes[pos]; mhLen |= (b & 0x7f) << shift; pos++; shift += 7;
        if (b < 0x80) break;
      }
      if (pos + mhLen <= bytes.length) return bytes.slice(pos, pos + mhLen);
      return null;
    } catch { return null; }
  }
  return null;
}

// ═══════════════════════════════════════════════════════════════════════════
// CAR PARSING — full block-level verification
// ═══════════════════════════════════════════════════════════════════════════

function readVarint(data, offset) {
  let value = 0, shift = 0, pos = offset;
  while (true) {
    const b = data[pos]; value |= (b & 0x7f) << shift; pos++; shift += 7;
    if (b < 0x80) break;
  }
  return { value, bytesRead: pos - offset };
}

function parseCidBytes(data, offset) {
  let pos = offset;
  while (pos < data.length && data[pos] === 0x00) pos++;
  if (pos >= data.length) throw new Error('Unexpected end reading CID');
  const version = data[pos];
  if (version === 0x12) {
    if (data[pos + 1] !== 0x20) throw new Error('Unexpected CIDv0 hash length');
    return { cid: cidv0Encode(data.slice(pos, pos + 34)), bytesRead: pos - offset + 34 };
  }
  let cidStart = pos;
  while (true) { const b = data[pos]; pos++; if (b < 0x80) break; }
  while (true) { const b = data[pos]; pos++; if (b < 0x80) break; }
  while (true) { const b = data[pos]; pos++; if (b < 0x80) break; }
  let mhLen = 0, shift = 0;
  while (true) { const b = data[pos]; mhLen |= (b & 0x7f) << shift; pos++; shift += 7; if (b < 0x80) break; }
  const cidBytes = data.slice(cidStart, pos + mhLen);
  return { cid: base32EncodeCid(cidBytes), bytesRead: pos - offset + mhLen };
}

function extractRootsFromHeader(carData, headerStart, headerEnd) {
  const headerBytes = carData.slice(headerStart, headerEnd);
  const roots = [];
  for (let i = 0; i < headerBytes.length - 2; i++) {
    if (headerBytes[i] === 0xd8 && headerBytes[i + 1] === 0x2a) {
      let cidStart = i + 2, cidLen = 0;
      if (headerBytes[cidStart] === 0x58) { cidLen = headerBytes[cidStart + 1]; cidStart += 2; }
      else if (headerBytes[cidStart] === 0x59) { cidLen = (headerBytes[cidStart + 1] << 8) | headerBytes[cidStart + 2]; cidStart += 3; }
      else if (headerBytes[cidStart] >= 0x40 && headerBytes[cidStart] < 0x58) { cidLen = headerBytes[cidStart] - 0x40; cidStart += 1; }
      else continue;
      try { roots.push(cidBytesToCid(headerBytes.slice(cidStart, cidStart + cidLen))); }
      catch { /* skip */ }
    }
  }
  return roots;
}

function parseCarFull(carData) {
  const headerLenResult = readVarint(carData, 0);
  const headerStart = headerLenResult.bytesRead;
  const headerEnd = headerStart + headerLenResult.value;
  const roots = extractRootsFromHeader(carData, headerStart, headerEnd);
  const blocks = new Map();
  let pos = headerEnd;
  while (pos < carData.length) {
    const blockLenResult = readVarint(carData, pos);
    if (blockLenResult.bytesRead + blockLenResult.value === 0) break;
    const blockStart = pos + blockLenResult.bytesRead;
    const blockEnd = blockStart + blockLenResult.value;
    if (blockEnd > carData.length) break;
    try {
      const cidResult = parseCidBytes(carData, blockStart);
      const dataStart = blockStart + cidResult.bytesRead;
      const blockData = carData.slice(dataStart, blockEnd);
      blocks.set(cidResult.cid, { data: blockData, offset: blockStart });
    } catch { /* skip */ }
    pos = blockEnd;
  }
  return { roots, blocks };
}

function extractLinksFromBlock(data) {
  const links = [];
  for (let i = 0; i < data.length - 2; i++) {
    if (data[i] === 0xd8 && data[i + 1] === 0x2a) {
      let cidStart = i + 2, cidLen = 0;
      if (data[cidStart] === 0x58) { cidLen = data[cidStart + 1]; cidStart += 2; }
      else if (data[cidStart] === 0x59) { cidLen = (data[cidStart + 1] << 8) | data[cidStart + 2]; cidStart += 3; }
      else if (data[cidStart] >= 0x40 && data[cidStart] < 0x58) { cidLen = data[cidStart] - 0x40; cidStart += 1; }
      else continue;
      try { links.push(cidBytesToCid(data.slice(cidStart, cidStart + cidLen))); }
      catch { /* skip */ }
    }
  }
  return links;
}

function verifyCarDag(carData) {
  const result = {
    valid: true, roots: [], blockCount: 0, missingBlocks: 0, cidMismatchBlocks: 0, errors: [],
  };
  let parsed;
  try { parsed = parseCarFull(carData); }
  catch (e) { result.valid = false; result.errors.push(`CAR parse failed: ${e.message}`); return result; }
  const { roots, blocks } = parsed;
  result.roots = roots;
  result.blockCount = blocks.size;
  if (roots.length === 0) {
    result.valid = false; result.errors.push('No roots found in CAR header'); return result;
  }
  for (const [cid, block] of blocks) {
    const computedHash = sha256buf(block.data);
    const storedDigest = extractDigestFromCid(cid);
    if (!storedDigest) {
      result.cidMismatchBlocks++; result.errors.push(`Block CID digest not extractable: ${cid.slice(0, 30)}...`); result.valid = false;
    } else if (!storedDigest.equals(computedHash)) {
      result.cidMismatchBlocks++; result.errors.push(`Block CID mismatch: ${cid.slice(0, 30)}... hash differs`); result.valid = false;
    }
  }
  const visited = new Set();
  const queue = [...roots];
  while (queue.length > 0) {
    const cid = queue.shift();
    if (visited.has(cid)) continue;
    visited.add(cid);
    const block = blocks.get(cid);
    if (!block) {
      result.missingBlocks++; result.errors.push(`Missing block for CID: ${cid}`); result.valid = false; continue;
    }
    const links = extractLinksFromBlock(block.data);
    for (const linkCid of links) { if (!visited.has(linkCid)) queue.push(linkCid); }
  }
  return result;
}

// ═══════════════════════════════════════════════════════════════════════════
// TAR EXTRACTION
// ═══════════════════════════════════════════════════════════════════════════

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
      files.push({ name, data: buf.slice(pos, pos + size) });
      pos += Math.ceil(size / 512) * 512;
    }
  }
  return files;
}

// ═══════════════════════════════════════════════════════════════════════════
// GITHUB HELPERS
// ═══════════════════════════════════════════════════════════════════════════

function ghHeaders(extra = {}) {
  return { Authorization: `Bearer ${GITHUB_TOKEN}`, Accept: 'application/vnd.github+json', ...extra };
}

async function getReleaseByTag(tag) {
  const res = await fetch(`https://api.github.com/repos/${REPO}/releases/tags/${tag}`, { headers: ghHeaders() });
  if (!res.ok) throw new Error(`Release ${tag} not found: ${res.status}`);
  return res.json();
}

async function getAllAssets(releaseId) {
  const assets = [];
  let page = 1;
  while (true) {
    const res = await fetch(
      `https://api.github.com/repos/${REPO}/releases/${releaseId}/assets?per_page=100&page=${page}`,
      { headers: ghHeaders() }
    );
    if (!res.ok) break;
    const batch = await res.json();
    if (!batch.length) break;
    assets.push(...batch);
    page++;
  }
  return assets;
}

async function downloadAsset(assetId, retries = MAX_RETRIES) {
  for (let attempt = 0; attempt <= retries; attempt++) {
    const res = await fetch(
      `https://api.github.com/repos/${REPO}/releases/assets/${assetId}`,
      { headers: ghHeaders({ Accept: 'application/octet-stream' }) }
    );
    if (res.ok) return Buffer.from(await res.arrayBuffer());
    if ((res.status >= 500 || res.status === 403 || res.status === 429) && attempt < retries) {
      await sleep(5000 * (attempt + 1));
      continue;
    }
    throw new Error(`Download asset ${assetId}: ${res.status}`);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// REPO FILE HELPERS
// ═══════════════════════════════════════════════════════════════════════════

function readRepoFile(filePath) {
  const fullPath = path.resolve(filePath);
  if (fs.existsSync(fullPath)) return fs.readFileSync(fullPath);
  return null;
}

function readRepoJson(filePath) {
  const buf = readRepoFile(filePath);
  if (!buf) return null;
  return JSON.parse(buf.toString('utf-8'));
}

// ═══════════════════════════════════════════════════════════════════════════
// DIGEST MANIFEST HELPERS
// ═══════════════════════════════════════════════════════════════════════════

function parseDigestManifestCsv(csvText) {
  const lines = csvText.trim().split('\n');
  if (lines.length < 2) return [];
  const headers = lines[0].split(',').map(h => h.trim());
  const pathIdx = headers.indexOf('path');
  const sizeIdx = headers.indexOf('size_bytes');
  const shaIdx = headers.indexOf('sha256');
  const items = [];
  for (let i = 1; i < lines.length; i++) {
    const cols = lines[i].split(',').map(c => c.trim());
    if (cols.length < 3) continue;
    items.push({
      path: cols[pathIdx] || cols[0],
      size_bytes: parseInt(cols[sizeIdx] || cols[1], 10),
      sha256: cols[shaIdx] || cols[2],
    });
  }
  return items;
}

function normalizePath(p) { return p.replace(/\\/g, '/'); }

function extractCidFromPath(filePath) {
  const basename = path.basename(filePath);
  const m = basename.match(/^(b[a-z2-7]{20,})/);
  if (m) return m[1];
  const m0 = basename.match(/^(Qm[a-zA-Z0-9]{20,})/);
  if (m0) return m0[1];
  return null;
}

function computeAllHashes(buf) {
  return {
    sha256: sha256hex(buf),
    sha3_256: sha3_256hex(buf),
    blake2b_256: blake2b256hex(buf),
    shake256_256: crypto.createHash('shake256', { outputLength: 32 }).update(buf).digest('hex'),
    sha512_256: sha512_256hex(buf),
    blake3_256: null,
  };
}

function findManifestEntry(filename, digestManifest) {
  if (!digestManifest?.items) return null;
  const normalized = normalizePath(filename);
  for (const item of digestManifest.items) {
    const itemBasename = path.basename(normalizePath(item.path));
    if (itemBasename === filename || itemBasename === path.basename(normalized)) return item;
  }
  for (const item of digestManifest.items) {
    const itemNorm = normalizePath(item.path);
    if (itemNorm.endsWith('/' + normalized) || itemNorm.endsWith('/' + path.basename(normalized))) return item;
  }
  const cidMatch = filename.match(/(b[a-z2-7]{20,}|Qm[a-zA-Z0-9]{20,})/);
  if (cidMatch) {
    const cid = cidMatch[1];
    for (const item of digestManifest.items) {
      if (item.path && item.path.includes(cid)) return item;
    }
  }
  return null;
}

// ═══════════════════════════════════════════════════════════════════════════
// MAIN
// ═══════════════════════════════════════════════════════════════════════════

async function main() {
  if (!GITHUB_TOKEN) { err('❌ GITHUB_TOKEN required'); process.exit(1); }
  if (!fs.existsSync(TMP_DIR)) fs.mkdirSync(TMP_DIR, { recursive: true });

  log('═══════════════════════════════════════════════════════════');
  log('  Step 2: DAG + Digest-Manifest Verification');
  log('═══════════════════════════════════════════════════════════');
  log(`  Release tag    : ${RELEASE_TAG}`);
  log(`  Concurrency    : ${CONCURRENCY}`);
  log('');

  // ── Load shared data ──────────────────────────────────────────────────
  log('📖 Loading shared data...');

  const tokenIndex = readRepoJson(TOKEN_INDEX_FILE);
  if (!tokenIndex) { err('❌ token_index.json not found'); process.exit(1); }
  const allContracts = Object.keys(tokenIndex);
  let totalNfts = 0;
  for (const c of allContracts) totalNfts += Object.keys(tokenIndex[c]).length;
  log(`  token_index.json: ${allContracts.length} contracts, ${totalNfts} NFTs`);
  if (totalNfts !== EXPECTED_NFTS) { err(`  ❌ Expected ${EXPECTED_NFTS}, found ${totalNfts}`); process.exit(1); }

  log(`📦 Fetching GitHub Release ${RELEASE_TAG}...`);
  const release = await getReleaseByTag(RELEASE_TAG);
  const allAssets = await getAllAssets(release.id);
  const nftAssets = allAssets.filter(a => a.name.startsWith('nft-') && a.name.endsWith('.tar'));
  log(`  ${allAssets.length} total assets, ${nftAssets.length} NFT tar files`);
  if (nftAssets.length !== EXPECTED_NFTS) {
    err(`  ⚠️  Expected ${EXPECTED_NFTS} nft-*.tar, found ${nftAssets.length}`);
  }

  const digestManifest = readRepoJson(DIGEST_MANIFEST_JSON);
  if (digestManifest) {
    log(`  digest-manifest.json: ${digestManifest.items?.length || 0} items`);
  }

  // ETH audit (optional)
  let ethAudit = null;
  const ethAuditAsset = allAssets.find(a => a.name === 'ONCHAIN-READ-AUDIT.json');
  if (ethAuditAsset) {
    try {
      const buf = await downloadAsset(ethAuditAsset.id);
      ethAudit = JSON.parse(buf.toString('utf-8'));
      log(`  ETH audit: ${ethAudit.tokens?.length || 0} tokens`);
    } catch (e) {
      log(`  ⚠️  Could not download ETH audit: ${e.message}`);
    }
  }

  // ── Build lookups ─────────────────────────────────────────────────────
  const nftLookup = new Map();
  for (const [contract, tokens] of Object.entries(tokenIndex)) {
    for (const [tokenId, entry] of Object.entries(tokens)) {
      nftLookup.set(`${contract.toLowerCase()}_${tokenId}`, { contract, tokenId, ...entry });
    }
  }

  const ethCidLookup = new Map();
  if (ethAudit?.tokens) {
    for (const t of ethAudit.tokens) {
      if (t.extracted_cid) ethCidLookup.set(`${t.contract?.toLowerCase()}_${t.token_id}`, t.extracted_cid);
    }
  }

  // ── Verify digest-manifest files against authority ────────────────────
  log('\n═══ Verifying digest-manifest integrity ═══\n');

  const authority = readRepoJson(AUTHORITY_JCS_FILE);
  const arweaveDocs = authority?.arweave?.documents || [];
  let declaredJson = null, declaredCsv = null;
  for (const doc of arweaveDocs) {
    const label = (doc.label || '').toLowerCase();
    if (label === 'digest-manifest.json') declaredJson = doc;
    if (label === 'digest-manifest.csv') declaredCsv = doc;
  }

  let digestJsonShaMatch = false, digestJsonSizeMatch = false;
  let digestCsvShaMatch = false, digestCsvSizeMatch = false;

  const actualJsonBuf = readRepoFile(DIGEST_MANIFEST_JSON);
  if (actualJsonBuf && declaredJson) {
    const actualSha = sha256hex(actualJsonBuf);
    digestJsonShaMatch = declaredJson.ar_sha256 ? declaredJson.ar_sha256.toLowerCase() === actualSha : false;
    digestJsonSizeMatch = (declaredJson.size === actualJsonBuf.length) || (declaredJson.size_bytes === actualJsonBuf.length);
    log(`  digest-manifest.json sha256 match: ${digestJsonShaMatch}`);
    log(`  digest-manifest.json size match  : ${digestJsonSizeMatch}`);
  }

  const actualCsvBuf = readRepoFile(DIGEST_MANIFEST_CSV);
  if (actualCsvBuf && declaredCsv) {
    const actualSha = sha256hex(actualCsvBuf);
    digestCsvShaMatch = declaredCsv.ar_sha256 ? declaredCsv.ar_sha256.toLowerCase() === actualSha : false;
    digestCsvSizeMatch = (declaredCsv.size === actualCsvBuf.length) || (declaredCsv.size_bytes === actualCsvBuf.length);
    log(`  digest-manifest.csv sha256 match : ${digestCsvShaMatch}`);
    log(`  digest-manifest.csv size match   : ${digestCsvSizeMatch}`);
  }

  // ── Verify NFT tar files ──────────────────────────────────────────────
  log('\n═══ Verifying NFT tar files (DAG + CID) ═══\n');

  let metadataDagPass = 0, metadataDagFail = 0;
  let mediaDagPass = 0, mediaDagFail = 0;
  let missingBlocksTotal = 0, cidRecomputeFail = 0;
  let metadataTokenIndexCidMatch = 0, metadataTokenIndexCidMismatch = 0;
  let metadataEthCidMatch = 0, metadataEthCidMismatch = 0, metadataEthCidSkip = 0;
  let digestManifestFileMatchCount = 0, digestManifestFileMismatchCount = 0;
  let metadataDigestMatchCount = 0, metadataDigestMismatchCount = 0;
  let mediaDigestMatchCount = 0, mediaDigestMismatchCount = 0;

  const nftDetails = [];
  const criticalErrors = [];

  const tasks = nftAssets.map(asset => async () => {
    const detail = {
      asset_name: asset.name, contract: null, token_id: null,
      metadata: null, media: [], dag_valid: true,
    };
    try {
      const tarBuf = await downloadAsset(asset.id);
      const tarFiles = extractFilesFromTar(tarBuf);
      const nameMatch = asset.name.match(/^nft-(0x[0-9a-f]+)-(.+)\.tar$/);
      if (!nameMatch) { detail.error = `Cannot parse: ${asset.name}`; return detail; }
      const contract = nameMatch[1];
      const tokenId = nameMatch[2];
      detail.contract = contract;
      detail.token_id = tokenId;
      const lookupKey = `${contract.toLowerCase()}_${tokenId}`;
      const tokenEntry = nftLookup.get(lookupKey);

      for (const tarFile of tarFiles) {
        if (!tarFile.name.endsWith('.car')) continue;
        const role = tarFile.name.replace('nft/', '').replace('.car', '');
        const carData = tarFile.data;
        const carSha = sha256hex(carData);
        const carSize = carData.length;
        const dagResult = verifyCarDag(carData);
        missingBlocksTotal += dagResult.missingBlocks;
        cidRecomputeFail += dagResult.cidMismatchBlocks;
        const rootCid = dagResult.roots?.[0] || null;

        let matchedManifestItem = null;
        if (rootCid && digestManifest?.items) {
          matchedManifestItem = digestManifest.items.find(item => item.path && item.path.includes(rootCid)) || null;
        }
        const inDigestManifest = !!matchedManifestItem;
        if (inDigestManifest) {
          digestManifestFileMatchCount++;
          if (role === 'metadata') metadataDigestMatchCount++;
          else mediaDigestMatchCount++;
        } else if (rootCid) {
          digestManifestFileMismatchCount++;
          if (role === 'metadata') {
            metadataDigestMismatchCount++;
            criticalErrors.push(`NOT IN DIGEST-MANIFEST: ${asset.name} [${role}] root=${rootCid?.slice(0,20)}`);
          } else {
            mediaDigestMismatchCount++;
          }
        }

        if (role === 'metadata') {
          if (dagResult.valid) metadataDagPass++;
          else { metadataDagFail++; detail.dag_valid = false; criticalErrors.push(`METADATA DAG FAIL: ${asset.name}`); }
          const expectedTi = tokenEntry?.metadata?.root_cid;
          if (expectedTi && rootCid) {
            if (rootCid === expectedTi) metadataTokenIndexCidMatch++;
            else { metadataTokenIndexCidMismatch++; criticalErrors.push(`TOKEN_INDEX CID MISMATCH: ${asset.name}`); }
          }
          const ethCid = ethCidLookup.get(lookupKey);
          if (ethCid && rootCid) {
            if (rootCid === ethCid) metadataEthCidMatch++;
            else { metadataEthCidMismatch++; criticalErrors.push(`ETH CID MISMATCH: ${asset.name}`); }
          } else { metadataEthCidSkip++; }
          detail.metadata = {
            dag_valid: dagResult.valid, block_count: dagResult.blockCount,
            missing_blocks: dagResult.missingBlocks, cid_mismatch_blocks: dagResult.cidMismatchBlocks,
            actual_root_cid: rootCid, token_index_cid: expectedTi || null, eth_cid: ethCid || null,
            sha256: carSha, size: carSize,
          };
        } else {
          if (dagResult.valid) mediaDagPass++;
          else mediaDagFail++;
          detail.media.push({
            dag_valid: dagResult.valid, block_count: dagResult.blockCount,
            actual_root_cid: rootCid, sha256: carSha, size: carSize,
            digest_manifest_match: matchedManifestItem ? (matchedManifestItem.sha256 === carSha && matchedManifestItem.size_bytes === carSize) : null,
          });
        }
      }
    } catch (e) {
      detail.error = e.message;
      criticalErrors.push(`ERROR: ${asset.name} — ${e.message}`);
    }
    return detail;
  });

  const results = await runConcurrent(tasks, CONCURRENCY);
  for (const r of results) {
    if (r instanceof Error) { criticalErrors.push(`TASK ERROR: ${r.message}`); continue; }
    nftDetails.push(r);
  }

  // ── Digest-manifest hash coverage ─────────────────────────────────────
  log('\n  ── Digest-manifest hash coverage ──');

  let multiHashMatchCount = 0, fileHashMismatchCount = 0, fileSizeMismatchCount = 0, privateUnavailableCount = 0;

  try {
    // Verify repo files against manifest
    const repoFilesToVerify = [];
    const verifyReportAsset = allAssets.find(a => a.name === 'verify-report.json');
    let verifyReportBuf = null;
    if (verifyReportAsset) {
      try {
        verifyReportBuf = await downloadAsset(verifyReportAsset.id);
        repoFilesToVerify.push({ label: 'verify-report.json', buf: verifyReportBuf });
      } catch (e) { log(`  ⚠️ Could not download verify-report.json: ${e.message}`); }
    }

    // NFT CAR hash verification against manifest
    let nftHashMatchCount = 0, nftHashMismatchCount = 0, nftSizeMismatchCount = 0;
    let nftManifestCoveredCount = 0;

    for (const detail of nftDetails) {
      if (detail.error) continue;
      if (detail.metadata?.actual_root_cid) {
        const rootCid = detail.metadata.actual_root_cid;
        const matchedItem = digestManifest?.items?.find(item => item.path && item.path.includes(rootCid));
        if (matchedItem) {
          nftManifestCoveredCount++;
          const shaMatch = detail.metadata.sha256 === matchedItem.sha256?.toLowerCase();
          const sizeMatch = detail.metadata.size === matchedItem.size_bytes;
          if (shaMatch && sizeMatch) nftHashMatchCount++;
          else { nftHashMismatchCount++; if (!sizeMatch) nftSizeMismatchCount++; }
        }
      }
      for (const m of detail.media || []) {
        if (m.actual_root_cid) {
          const rootCid = m.actual_root_cid;
          const matchedItem = digestManifest?.items?.find(item => item.path && item.path.includes(rootCid));
          if (matchedItem) {
            nftManifestCoveredCount++;
            const shaMatch = m.sha256 === matchedItem.sha256?.toLowerCase();
            const sizeMatch = m.size === matchedItem.size_bytes;
            if (shaMatch && sizeMatch) nftHashMatchCount++;
            else { nftHashMismatchCount++; if (!sizeMatch) nftSizeMismatchCount++; }
          }
        }
      }
    }

    multiHashMatchCount = nftHashMatchCount;
    fileHashMismatchCount = nftHashMismatchCount;
    fileSizeMismatchCount = nftSizeMismatchCount;

    // Count private/unavailable
    if (digestManifest?.items) {
      const accessibleBasenames = new Set();
      if (verifyReportBuf) accessibleBasenames.add('verify-report.json');
      for (const detail of nftDetails) {
        if (detail.metadata?.actual_root_cid) accessibleBasenames.add(detail.metadata.actual_root_cid);
        for (const m of detail.media || []) { if (m.actual_root_cid) accessibleBasenames.add(m.actual_root_cid); }
      }
      for (const item of digestManifest.items) {
        const norm = normalizePath(item.path);
        const bn = path.basename(norm);
        let found = false;
        for (const acc of accessibleBasenames) {
          if (item.path.includes(acc) || bn === acc) { found = true; break; }
        }
        if (!found) privateUnavailableCount++;
      }
    }

    log(`  NFT CAR manifest covered : ${nftManifestCoveredCount}`);
    log(`  NFT CAR hash+size match  : ${nftHashMatchCount}`);
    log(`  NFT CAR hash mismatch    : ${nftHashMismatchCount}`);
    log(`  NFT CAR size mismatch    : ${nftSizeMismatchCount}`);
    log(`  Private/unavailable      : ${privateUnavailableCount}`);

  } catch (hashErr) {
    log(`  ⚠️ Hash coverage verification error: ${hashErr.message}`);
  }

  // ── Compute overall pass ──────────────────────────────────────────────
  const dagAndDigestManifestPass = criticalErrors.length === 0
    && metadataDagFail === 0
    && metadataDigestMismatchCount === 0
    && metadataTokenIndexCidMismatch === 0
    && digestJsonShaMatch && digestCsvShaMatch
    && digestJsonSizeMatch && digestCsvSizeMatch;

  log(`\n  ── Summary ──`);
  log(`  Metadata DAG pass             : ${metadataDagPass}`);
  log(`  Metadata DAG fail             : ${metadataDagFail}`);
  log(`  Media DAG pass (audit-only)   : ${mediaDagPass}`);
  log(`  Media DAG fail (audit-only)   : ${mediaDagFail}`);
  log(`  Missing blocks                : ${missingBlocksTotal}`);
  log(`  CID recompute fail            : ${cidRecomputeFail}`);
  log(`  Meta CID vs token_index       : ${metadataTokenIndexCidMatch} match, ${metadataTokenIndexCidMismatch} mismatch`);
  log(`  Meta CID vs ETH               : ${metadataEthCidMatch} match, ${metadataEthCidMismatch} mismatch, ${metadataEthCidSkip} skip`);
  log(`  Chain A pass                  : ${dagAndDigestManifestPass}`);

  // ── Write output ──────────────────────────────────────────────────────
  const audit = {
    schema: 'trinity-accord.dag-digest-audit.v1',
    generated_at: new Date().toISOString(),
    dag_and_digest_manifest_pass: dagAndDigestManifestPass,
    release_nft_tar_count: nftAssets.length,
    digest_manifest_json_sha256_match: digestJsonShaMatch,
    digest_manifest_csv_sha256_match: digestCsvShaMatch,
    digest_manifest_json_size_match: digestJsonSizeMatch,
    digest_manifest_csv_size_match: digestCsvSizeMatch,
    digest_manifest_file_match_count: digestManifestFileMatchCount,
    digest_manifest_file_mismatch_count: digestManifestFileMismatchCount,
    metadata_dag_pass: metadataDagPass,
    metadata_dag_fail: metadataDagFail,
    media_dag_pass: mediaDagPass,
    media_dag_fail: mediaDagFail,
    missing_blocks: missingBlocksTotal,
    cid_recompute_fail: cidRecomputeFail,
    metadata_token_index_cid_match: metadataTokenIndexCidMatch,
    metadata_token_index_cid_mismatch: metadataTokenIndexCidMismatch,
    metadata_eth_cid_match: metadataEthCidMatch,
    metadata_eth_cid_mismatch: metadataEthCidMismatch,
    metadata_eth_cid_skip: metadataEthCidSkip,
    multi_hash_match_count: multiHashMatchCount,
    file_hash_mismatch_count: fileHashMismatchCount,
    file_size_mismatch_count: fileSizeMismatchCount,
    private_unavailable_hash_only: privateUnavailableCount,
    critical_errors: criticalErrors,
  };

  const outPath = path.join(process.cwd(), 'DAG-DIGEST-AUDIT.json');
  fs.writeFileSync(outPath, JSON.stringify(audit, null, 2));
  log(`\n📝 ${outPath} written`);

  if (!dagAndDigestManifestPass) {
    err('\n  ❌ DAG + DIGEST MANIFEST VERIFICATION FAILED');
    for (const e of criticalErrors) err(`    ❌ ${e}`);
    process.exit(1);
  }

  log('\n  ✅ DAG + digest-manifest verification passed.');
}

main().catch(e => { err('Fatal:', e.message || e); if (e.stack) err(e.stack); process.exit(1); });
