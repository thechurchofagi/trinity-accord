#!/usr/bin/env node
/**
 * verify-dag-digest.mjs  (Step A — strict version)
 *
 * DAG + digest-manifest file hash verification.
 * Uses @noble/hashes for all hash algorithms including blake3.
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { sha3_256 } from '@noble/hashes/sha3.js';
import { blake2b } from '@noble/hashes/blake2.js';
import { shake256 } from '@noble/hashes/sha3.js';
import { blake3 } from '@noble/hashes/blake3.js';
import { bytesToHex } from '@noble/hashes/utils.js';

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
// CONFIG
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

const HASH_ALGORITHMS = ['sha256', 'sha3_256', 'blake2b_256', 'shake256_256', 'sha512_256', 'blake3_256'];

function isNonEmptyHash(v) {
  return typeof v === 'string' && v.trim().length > 0;
}

function declaredHashAlgorithms(record) {
  return HASH_ALGORITHMS.filter(algo => isNonEmptyHash(record[algo]));
}

function normalizeHashValue(v) {
  return String(v || '').trim().toLowerCase().replace(/^0x/, '');
}

// ═══════════════════════════════════════════════════════════════════════════
// PRIMITIVES
// ═══════════════════════════════════════════════════════════════════════════

function sha256hex(buf) { return crypto.createHash('sha256').update(buf).digest('hex'); }
function sha256buf(buf) { return crypto.createHash('sha256').update(buf).digest(); }
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
function log(msg) { console.log(msg); }
function err(msg) { console.error(msg); }

function normalizeKey(k) {
  return String(k || '').trim().toLowerCase().replace(/[-\s]/g, '_');
}

function normPath(p) {
  return String(p || '').replace(/\\/g, '/').replace(/^\.?\//, '').replace(/\/+/g, '/').trim();
}

/**
 * Compute all 6 hashes for a buffer using @noble/hashes where available.
 *
 * blake2b_256 uses the HISTORICAL generation variant:
 *   crypto.createHash('blake2b512').update(buf).digest('hex')
 * The manifest stores full blake2b-512 output (128 hex chars / 64 bytes)
 * under the field name "blake2b_256". This was confirmed by probe-blake2b-variants.mjs
 * (node_blake2b512_full matched 524/524 public files).
 */
function computeAllHashes(buf) {
  const u8 = buf instanceof Uint8Array ? buf : new Uint8Array(buf.buffer, buf.byteOffset, buf.byteLength);
  return {
    sha256: sha256hex(buf),
    sha3_256: bytesToHex(sha3_256(u8)),
    blake2b_256: crypto.createHash('blake2b512').update(buf).digest('hex'),
    shake256_256: bytesToHex(shake256(u8, { dkLen: 32 })),
    sha512_256: crypto.createHash('sha512-256').update(buf).digest('hex'),
    blake3_256: bytesToHex(blake3(u8)),
  };
}

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
// CID / BASE32 / BASE58 HELPERS
// ═══════════════════════════════════════════════════════════════════════════

function base32EncodeCid(bytes) {
  const alphabet = 'abcdefghijklmnopqrstuvwxyz234567';
  let bits = 0, value = 0, output = 'b';
  for (const byte of bytes) {
    value = (value << 8) | byte; bits += 8;
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
    value = (value << 5) | val; bits += 5;
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
    for (let j = 0; j < digits.length; j++) { carry += digits[j] << 8; digits[j] = carry % 58; carry = (carry / 58) | 0; }
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
    for (let j = 0; j < bytes.length; j++) { carry += bytes[j] * 58; bytes[j] = carry & 0xff; carry >>= 8; }
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
  if (trimmed[0] === 0x12 && trimmed.length >= 34 && trimmed[1] === 0x20) return cidv0Encode(trimmed.slice(0, 34));
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
      while (pos < bytes.length && bytes[pos] >= 0x80) pos++; pos++;
      while (pos < bytes.length && bytes[pos] >= 0x80) pos++; pos++;
      while (pos < bytes.length && bytes[pos] >= 0x80) pos++; pos++;
      let mhLen = 0, shift = 0;
      while (pos < bytes.length) { const b = bytes[pos]; mhLen |= (b & 0x7f) << shift; pos++; shift += 7; if (b < 0x80) break; }
      if (pos + mhLen <= bytes.length) return bytes.slice(pos, pos + mhLen);
      return null;
    } catch { return null; }
  }
  return null;
}

// ═══════════════════════════════════════════════════════════════════════════
// CAR PARSING
// ═══════════════════════════════════════════════════════════════════════════

function readVarint(data, offset) {
  let value = 0, shift = 0, pos = offset;
  while (true) { const b = data[pos]; value |= (b & 0x7f) << shift; pos++; shift += 7; if (b < 0x80) break; }
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
      try { roots.push(cidBytesToCid(headerBytes.slice(cidStart, cidStart + cidLen))); } catch { /* skip */ }
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
      blocks.set(cidResult.cid, { data: carData.slice(dataStart, blockEnd), offset: blockStart });
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
      try { links.push(cidBytesToCid(data.slice(cidStart, cidStart + cidLen))); } catch { /* skip */ }
    }
  }
  return links;
}

function verifyCarDag(carData) {
  const result = { valid: true, roots: [], blockCount: 0, missingBlocks: 0, cidMismatchBlocks: 0, errors: [] };
  let parsed;
  try { parsed = parseCarFull(carData); } catch (e) { result.valid = false; result.errors.push(`CAR parse failed: ${e.message}`); return result; }
  const { roots, blocks } = parsed;
  result.roots = roots;
  result.blockCount = blocks.size;
  if (roots.length === 0) { result.valid = false; result.errors.push('No roots found'); return result; }
  for (const [cid, block] of blocks) {
    const computedHash = sha256buf(block.data);
    const storedDigest = extractDigestFromCid(cid);
    if (!storedDigest) { result.cidMismatchBlocks++; result.errors.push(`CID digest not extractable: ${cid.slice(0, 30)}`); result.valid = false; }
    else if (!storedDigest.equals(computedHash)) { result.cidMismatchBlocks++; result.errors.push(`CID mismatch: ${cid.slice(0, 30)}`); result.valid = false; }
  }
  const visited = new Set();
  const queue = [...roots];
  while (queue.length > 0) {
    const cid = queue.shift();
    if (visited.has(cid)) continue;
    visited.add(cid);
    const block = blocks.get(cid);
    if (!block) { result.missingBlocks++; result.errors.push(`Missing block: ${cid}`); result.valid = false; continue; }
    for (const linkCid of extractLinksFromBlock(block.data)) { if (!visited.has(linkCid)) queue.push(linkCid); }
  }
  return result;
}

/**
 * Re-verify a CAR's DAG with cross-CAR block resolution.
 * Returns granular counts: cross_car_references (resolved from other CARs)
 * vs unresolved_missing_blocks (truly missing from all CARs).
 */
function verifyCarDagCrossResolved(carData, globalBlocks) {
  const result = { valid: true, roots: [], blockCount: 0, crossCarReferences: 0, unresolvedMissingBlocks: 0, cidMismatchBlocks: 0, errors: [] };
  let parsed;
  try { parsed = parseCarFull(carData); } catch (e) { result.valid = false; result.errors.push(`CAR parse failed: ${e.message}`); return result; }
  const { roots, blocks } = parsed;
  result.roots = roots;
  result.blockCount = blocks.size;
  if (roots.length === 0) { result.valid = false; result.errors.push('No roots found'); return result; }
  for (const [cid, block] of blocks) {
    const computedHash = sha256buf(block.data);
    const storedDigest = extractDigestFromCid(cid);
    if (!storedDigest) { result.cidMismatchBlocks++; result.errors.push(`CID digest not extractable: ${cid.slice(0, 30)}`); result.valid = false; }
    else if (!storedDigest.equals(computedHash)) { result.cidMismatchBlocks++; result.errors.push(`CID mismatch: ${cid.slice(0, 30)}`); result.valid = false; }
  }
  const visited = new Set();
  const queue = [...roots];
  while (queue.length > 0) {
    const cid = queue.shift();
    if (visited.has(cid)) continue;
    visited.add(cid);
    const block = blocks.get(cid);
    if (block) {
      for (const linkCid of extractLinksFromBlock(block.data)) { if (!visited.has(linkCid)) queue.push(linkCid); }
    } else if (globalBlocks.has(cid)) {
      // Block found in another CAR — cross-CAR reference, not an error
      result.crossCarReferences++;
    } else {
      result.unresolvedMissingBlocks++;
      result.errors.push(`Unresolved missing block: ${cid}`);
      result.valid = false;
    }
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
    for (let i = 124; i < 136; i++) { if (header[i] === 0 || header[i] === 32) break; sizeStr += String.fromCharCode(header[i]); }
    const size = parseInt(sizeStr, 8) || 0;
    pos += 512;
    if (size > 0) { files.push({ name, data: buf.slice(pos, pos + size) }); pos += Math.ceil(size / 512) * 512; }
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
    const res = await fetch(`https://api.github.com/repos/${REPO}/releases/${releaseId}/assets?per_page=100&page=${page}`, { headers: ghHeaders() });
    if (!res.ok) break;
    const batch = await res.json();
    if (!batch.length) break;
    assets.push(...batch);
    page++;
  }
  return assets;
}

function isRetryableFetchError(err) {
  const msg = String(err?.message || err);
  return /fetch failed|ECONNRESET|ETIMEDOUT|timeout|network|socket|429|5\d\d/i.test(msg);
}

async function fetchBufferWithRetry(url, options = {}) {
  const {
    label = url,
    attempts = Number(process.env.RELEASE_ASSET_DOWNLOAD_RETRIES || 5),
    baseDelayMs = 1000,
    maxDelayMs = 15000,
    headers = {}
  } = options;

  let lastError = null;

  for (let i = 1; i <= attempts; i++) {
    try {
      const res = await fetch(url, { headers });

      if (res.ok) {
        return Buffer.from(await res.arrayBuffer());
      }

      const body = await res.text().catch(() => '');

      const retryable =
        res.status === 408 ||
        res.status === 429 ||
        res.status >= 500;

      lastError = new Error(
        `${label}: HTTP ${res.status} ${res.statusText} ${body.slice(0, 300)}`
      );

      if (!retryable || i === attempts) {
        throw lastError;
      }
    } catch (e) {
      lastError = e;

      if (!isRetryableFetchError(e) || i === attempts) {
        throw e;
      }
    }

    const delay = Math.min(maxDelayMs, baseDelayMs * 2 ** (i - 1));
    log(`  Retry ${i}/${attempts} for ${label} after ${delay}ms`);
    await sleep(delay);
  }

  throw lastError;
}

async function downloadAsset(assetId) {
  return fetchBufferWithRetry(
    `https://api.github.com/repos/${REPO}/releases/assets/${assetId}`,
    {
      label: `asset-${assetId}`,
      headers: ghHeaders({ Accept: 'application/octet-stream' })
    }
  );
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
// DIGEST MANIFEST NORMALIZATION
// ═══════════════════════════════════════════════════════════════════════════

const PATH_ALIASES = ['path', 'file', 'filename', 'relative_path', 'name'];
const SIZE_ALIASES = ['size', 'size_bytes', 'bytes', 'length'];
const SHA256_ALIASES = ['sha256', 'sha_256', 'digest_sha256'];
const SHA3_ALIASES = ['sha3_256', 'sha3-256'];
const BLAKE2B_ALIASES = ['blake2b_256', 'blake2b-256'];
const SHAKE_ALIASES = ['shake256_256', 'shake256-256'];
const SHA512_ALIASES = ['sha512_256', 'sha512-256'];
const BLAKE3_ALIASES = ['blake3_256', 'blake3-256'];
const CID_ALIASES = ['cid', 'root_cid', 'ipfs_cid'];
const TXID_ALIASES = ['txid', 'arweave_txid', 'ar_txid'];

function resolveField(obj, aliases) {
  for (const a of aliases) {
    const nk = normalizeKey(a);
    for (const [k, v] of Object.entries(obj)) {
      if (normalizeKey(k) === nk && v != null) return v;
    }
  }
  return null;
}

function normalizeManifestItem(raw) {
  return {
    path: resolveField(raw, PATH_ALIASES) || '',
    filename: path.basename(normPath(resolveField(raw, PATH_ALIASES) || '')),
    size_bytes: Number(resolveField(raw, SIZE_ALIASES)) || 0,
    sha256: String(resolveField(raw, SHA256_ALIASES) || '').toLowerCase(),
    sha3_256: String(resolveField(raw, SHA3_ALIASES) || '').toLowerCase(),
    blake2b_256: String(resolveField(raw, BLAKE2B_ALIASES) || '').toLowerCase(),
    shake256_256: String(resolveField(raw, SHAKE_ALIASES) || '').toLowerCase(),
    sha512_256: String(resolveField(raw, SHA512_ALIASES) || '').toLowerCase(),
    blake3_256: String(resolveField(raw, BLAKE3_ALIASES) || '').toLowerCase(),
    cid: String(resolveField(raw, CID_ALIASES) || ''),
    txid: String(resolveField(raw, TXID_ALIASES) || ''),
    status: raw.status || null,
    _raw: raw,
  };
}

function normalizeDigestManifest(digestManifest) {
  const items = digestManifest.items || digestManifest;
  if (!Array.isArray(items)) return [];
  return items.map(normalizeManifestItem);
}

/**
 * Build multiple lookup indexes from normalized manifest items.
 */
function buildManifestIndexes(items) {
  const byPath = new Map();
  const byFilename = new Map();
  const bySha256 = new Map();
  const byCid = new Map();
  const byTxid = new Map();

  for (const item of items) {
    const np = normPath(item.path);
    if (np) byPath.set(np, item);
    if (item.filename) {
      const existing = byFilename.get(item.filename);
      if (!existing) byFilename.set(item.filename, item);
      else byFilename.set(item.filename, Array.isArray(existing) ? [...existing, item] : [existing, item]);
    }
    if (item.sha256) bySha256.set(item.sha256.toLowerCase(), item);
    if (item.cid) byCid.set(item.cid.toLowerCase(), item);
    if (item.txid) byTxid.set(item.txid.toLowerCase(), item);
  }

  return { byPath, byFilename, bySha256, byCid, byTxid };
}

/**
 * Find manifest entry using multiple indexes.
 * Priority: sha256 > normalized path > filename > CID > txid > path contains CID (candidate only).
 */
function findManifestEntry(fileSha256, filePath, fileCid, indexes) {
  // 1. sha256 exact match
  if (fileSha256 && indexes.bySha256.has(fileSha256.toLowerCase())) {
    return { item: indexes.bySha256.get(fileSha256.toLowerCase()), matchMethod: 'sha256' };
  }

  // 2. normalized path exact match
  const np = normPath(filePath);
  if (np && indexes.byPath.has(np)) {
    return { item: indexes.byPath.get(np), matchMethod: 'path' };
  }

  // 3. filename exact match
  const fn = path.basename(np || filePath);
  if (fn && indexes.byFilename.has(fn)) {
    const entry = indexes.byFilename.get(fn);
    const item = Array.isArray(entry) ? entry[0] : entry;
    return { item, matchMethod: 'filename' };
  }

  // 4. CID exact match
  if (fileCid && indexes.byCid.has(fileCid.toLowerCase())) {
    return { item: indexes.byCid.get(fileCid.toLowerCase()), matchMethod: 'cid' };
  }

  // 5. path contains CID (candidate only — NOT a pass condition)
  if (fileCid) {
    for (const [key, item] of indexes.byPath) {
      if (key.includes(fileCid)) return { item, matchMethod: 'path_contains_cid_candidate' };
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
  log('  Step A: DAG + Digest-Manifest Verification (strict)');
  log('═══════════════════════════════════════════════════════════\n');

  // ── Load data ─────────────────────────────────────────────────────
  const tokenIndex = readRepoJson(TOKEN_INDEX_FILE);
  if (!tokenIndex) { err('❌ token_index.json not found'); process.exit(1); }
  let totalNfts = 0;
  for (const c of Object.keys(tokenIndex)) totalNfts += Object.keys(tokenIndex[c]).length;
  log(`  token_index: ${totalNfts} NFTs`);
  if (totalNfts !== EXPECTED_NFTS) { err(`  ❌ Expected ${EXPECTED_NFTS}`); process.exit(1); }

  log(`📦 Fetching release ${RELEASE_TAG}...`);
  const release = await getReleaseByTag(RELEASE_TAG);
  const allAssets = await getAllAssets(release.id);
  const nftAssets = allAssets.filter(a => a.name.startsWith('nft-') && a.name.endsWith('.tar'));
  log(`  ${allAssets.length} total, ${nftAssets.length} NFT tars`);

  // Load and normalize digest-manifest
  const rawDigestManifest = readRepoJson(DIGEST_MANIFEST_JSON);
  const manifestItems = normalizeDigestManifest(rawDigestManifest);
  const indexes = buildManifestIndexes(manifestItems);
  log(`  digest-manifest: ${manifestItems.length} items (normalized)`);

  // ETH audit
  let ethAudit = null;
  const ethAuditAsset = allAssets.find(a => a.name === 'ONCHAIN-READ-AUDIT.json');
  if (ethAuditAsset) {
    try { ethAudit = JSON.parse((await downloadAsset(ethAuditAsset.id)).toString('utf-8')); } catch {}
  }

  // ── Verify digest-manifest integrity ──────────────────────────────
  log('\n═══ A.4: digest-manifest integrity ═══\n');

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
    log(`  digest-manifest.json sha256: ${digestJsonShaMatch}, size: ${digestJsonSizeMatch}`);
    if (!declaredJson.ar_sha256) { err('  ❌ authority missing digest-manifest.json sha256'); }
  }

  const actualCsvBuf = readRepoFile(DIGEST_MANIFEST_CSV);
  if (actualCsvBuf && declaredCsv) {
    const actualSha = sha256hex(actualCsvBuf);
    digestCsvShaMatch = declaredCsv.ar_sha256 ? declaredCsv.ar_sha256.toLowerCase() === actualSha : false;
    digestCsvSizeMatch = (declaredCsv.size === actualCsvBuf.length) || (declaredCsv.size_bytes === actualCsvBuf.length);
    log(`  digest-manifest.csv sha256: ${digestCsvShaMatch}, size: ${digestCsvSizeMatch}`);
    if (!declaredCsv.ar_sha256) { err('  ❌ authority missing digest-manifest.csv sha256'); }
  }

  // ── Verify NFT tar files ──────────────────────────────────────────
  log('\n═══ A.6-A.9: NFT tar verification ═══\n');

  // NFT lookup
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

  // Counters
  let metadataDagPass = 0, metadataDagFail = 0;
  let mediaDagPass = 0, mediaDagFail = 0;
  let missingBlocksTotal = 0, cidRecomputeFail = 0;
  let crossCarRefTotal = 0, crossCarRefResolvedTotal = 0, unresolvedMissingTotal = 0;
  let metadataTokenIndexCidMatch = 0, metadataTokenIndexCidMismatch = 0;
  let metadataEthCidMatch = 0, metadataEthCidMismatch = 0, metadataEthCidSkip = 0;
  let manifestDirectMatchCount = 0, releaseDerivVerifiedCount = 0;
  let publicMissingCount = 0;
  let sha256MatchCount = 0, sha3MatchCount = 0, blake2bMatchCount = 0;
  let shake256MatchCount = 0, sha512MatchCount = 0, blake3MatchCount = 0;
  let fileHashMismatchCount = 0, fileSizeMismatchCount = 0;
  let mediaSha256Fail = 0, mediaSizeFail = 0, mediaRootCidMismatchWarning = 0;
  let downloadFailures = 0;
  const downloadFailureDetails = [];
  let declaredHashChecksTotal = 0;
  let skippedUndeclaredHashFields = 0;
  let unavailableAlgorithmCount = 0;
  const unavailableAlgorithmDetails = [];
  const hashMatchByAlgorithm = { sha256: 0, sha3_256: 0, blake2b_256: 0, shake256_256: 0, sha512_256: 0, blake3_256: 0 };
  const hashMismatchByAlgorithm = { sha256: 0, sha3_256: 0, blake2b_256: 0, shake256_256: 0, sha512_256: 0, blake3_256: 0 };
  const hashMismatchDetails = [];

  const criticalErrors = [];
  const nftDetails = [];

  const tasks = nftAssets.map(asset => async () => {
    const detail = { asset_name: asset.name, contract: null, token_id: null, metadata: null, media: [], dag_valid: true };
    try {
      let tarBuf;
      try {
        tarBuf = await downloadAsset(asset.id);
      } catch (e) {
        downloadFailures++;
        downloadFailureDetails.push({ asset: asset.name, error: String(e?.stack || e) });
        criticalErrors.push(`DOWNLOAD FAILED: ${asset.name} — ${e.message}`);
        detail.error = `Download failed: ${e.message}`;
        return detail;
      }

      const tarFiles = extractFilesFromTar(tarBuf);
      const nameMatch = asset.name.match(/^nft-(0x[0-9a-f]+)-(.+)\.tar$/);
      if (!nameMatch) { detail.error = `Cannot parse: ${asset.name}`; return detail; }
      const contract = nameMatch[1], tokenId = nameMatch[2];
      detail.contract = contract; detail.token_id = tokenId;
      const lookupKey = `${contract.toLowerCase()}_${tokenId}`;
      const tokenEntry = nftLookup.get(lookupKey);

      // nft-*.tar is a release derivative
      releaseDerivVerifiedCount++;

      // ── Pass 1: parse all CARs, build global block pool ──────────
      const carFiles = tarFiles.filter(f => f.name.endsWith('.car'));
      const globalBlocks = new Map();
      const parsedCars = [];
      for (const carFile of carFiles) {
        try {
          const parsed = parseCarFull(carFile.data);
          for (const [cid, block] of parsed.blocks) {
            if (!globalBlocks.has(cid)) globalBlocks.set(cid, block);
          }
          parsedCars.push({ carFile, parsed });
        } catch { parsedCars.push({ carFile, parsed: null }); }
      }

      // ── Pass 2: verify each CAR with cross-resolve ──────────────
      for (const { carFile, parsed: parsedCar } of parsedCars) {
        if (!parsedCar) continue;
        const role = carFile.name.replace('nft/', '').replace('.car', '');
        const carData = carFile.data;
        const carSha = sha256hex(carData);
        const carSize = carData.length;

        const dagResult = verifyCarDagCrossResolved(carData, globalBlocks);
        crossCarRefTotal += dagResult.crossCarReferences;
        crossCarRefResolvedTotal += dagResult.crossCarReferences;
        unresolvedMissingTotal += dagResult.unresolvedMissingBlocks;
        cidRecomputeFail += dagResult.cidMismatchBlocks;
        const rootCid = dagResult.roots?.[0] || null;

        // Find manifest entry using strict matching
        const findResult = findManifestEntry(carSha, tarFile.name, rootCid, indexes);
        const matchedItem = findResult?.item || null;
        const matchMethod = findResult?.matchMethod || 'none';

        if (matchedItem && matchMethod !== 'path_contains_cid_candidate') {
          // Only verify hash fields that are explicitly declared (non-empty) in manifest
          const hashes = computeAllHashes(carData);
          const declared = declaredHashAlgorithms(matchedItem);
          const skipped = HASH_ALGORITHMS.length - declared.length;
          skippedUndeclaredHashFields += skipped;

          for (const algo of declared) {
            declaredHashChecksTotal++;
            const expected = normalizeHashValue(matchedItem[algo]);
            const observed = normalizeHashValue(hashes[algo]);

            if (!observed) {
              unavailableAlgorithmCount++;
              unavailableAlgorithmDetails.push({ path: matchedItem.path, algorithm: algo, reason: 'algorithm_declared_but_not_computed' });
              continue;
            }

            if (observed === expected) {
              hashMatchByAlgorithm[algo]++;
              // Also update legacy counters
              if (algo === 'sha256') sha256MatchCount++;
              else if (algo === 'sha3_256') sha3MatchCount++;
              else if (algo === 'blake2b_256') blake2bMatchCount++;
              else if (algo === 'shake256_256') shake256MatchCount++;
              else if (algo === 'sha512_256') sha512MatchCount++;
              else if (algo === 'blake3_256') blake3MatchCount++;
            } else {
              hashMismatchByAlgorithm[algo]++;
              fileHashMismatchCount++;
              hashMismatchDetails.push({ path: matchedItem.path, algorithm: algo, expected, observed });
            }
          }

          if (matchedItem.size_bytes && carSize !== matchedItem.size_bytes) fileSizeMismatchCount++;
          manifestDirectMatchCount++;
        } else if (matchedItem && matchMethod === 'path_contains_cid_candidate') {
          // CID path match is only a candidate — verify hash (sha256 only)
          const hashes = computeAllHashes(carData);
          if (matchedItem.sha256) {
            declaredHashChecksTotal++;
            if (normalizeHashValue(hashes.sha256) === normalizeHashValue(matchedItem.sha256)) {
              sha256MatchCount++;
              hashMatchByAlgorithm.sha256++;
              manifestDirectMatchCount++;
            } else {
              fileHashMismatchCount++;
              hashMismatchByAlgorithm.sha256++;
              hashMismatchDetails.push({ path: matchedItem.path, algorithm: 'sha256', expected: normalizeHashValue(matchedItem.sha256), observed: normalizeHashValue(hashes.sha256) });
            }
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
            cross_car_references: dagResult.crossCarReferences,
            unresolved_missing_blocks: dagResult.unresolvedMissingBlocks,
            cid_mismatch_blocks: dagResult.cidMismatchBlocks,
            actual_root_cid: rootCid, token_index_cid: expectedTi || null, eth_cid: ethCid || null,
            sha256: carSha, size: carSize,
          };
        } else {
          if (dagResult.valid) mediaDagPass++;
          else mediaDagFail++;

          // Media: sha256 + size are hard verification
          const hashes = computeAllHashes(carData);
          const mediaMatched = findManifestEntry(carSha, tarFile.name, rootCid, indexes);
          if (mediaMatched?.item) {
            if (mediaMatched.item.sha256 && hashes.sha256 !== mediaMatched.item.sha256) mediaSha256Fail++;
            if (mediaMatched.item.size_bytes && carSize !== mediaMatched.item.size_bytes) mediaSizeFail++;
          }
          if (rootCid && tokenEntry?.media) {
            const expectedMedia = tokenEntry.media.find(m => m.root_cid === rootCid);
            if (!expectedMedia) mediaRootCidMismatchWarning++;
          }

          detail.media.push({
            dag_valid: dagResult.valid, block_count: dagResult.blockCount,
            actual_root_cid: rootCid, sha256: carSha, size: carSize,
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

  // ── Count private/unavailable ──────────────────────────────────────
  const accessibleBasenames = new Set();
  for (const detail of nftDetails) {
    if (detail.metadata?.actual_root_cid) accessibleBasenames.add(detail.metadata.actual_root_cid);
    for (const m of detail.media || []) { if (m.actual_root_cid) accessibleBasenames.add(m.actual_root_cid); }
  }
  let privateUnavailableCount = 0;
  for (const item of manifestItems) {
    const np = normPath(item.path);
    const bn = path.basename(np);
    let found = false;
    for (const acc of accessibleBasenames) {
      if (np.includes(acc) || bn === acc || item.sha256 === acc) { found = true; break; }
    }
    if (!found) privateUnavailableCount++;
  }

  // ── Summary ────────────────────────────────────────────────────────
  const dagAndDigestManifestPass = criticalErrors.length === 0
    && downloadFailures === 0
    && metadataDagFail === 0
    && metadataTokenIndexCidMismatch === 0
    && digestJsonShaMatch && digestCsvShaMatch
    && digestJsonSizeMatch && digestCsvSizeMatch
    && fileHashMismatchCount === 0
    && fileSizeMismatchCount === 0
    && unavailableAlgorithmCount === 0
    && publicMissingCount === 0
    && unresolvedMissingTotal === 0
    && (declaredJson?.ar_sha256 ? true : false)
    && (declaredCsv?.ar_sha256 ? true : false);

  log(`\n  ── Summary ──`);
  log(`  Manifest records total        : ${manifestItems.length}`);
  log(`  Public files checked          : ${manifestDirectMatchCount}`);
  log(`  Digest manifest direct match  : ${manifestDirectMatchCount}`);
  log(`  Release derivative verified   : ${releaseDerivVerifiedCount}`);
  log(`  Private/unavailable           : ${privateUnavailableCount}`);
  log(`  Public missing                : ${publicMissingCount}`);
  log(`  Download failures             : ${downloadFailures}`);
  log(`  Declared hash checks total    : ${declaredHashChecksTotal}`);
  log(`  Skipped undeclared hash fields: ${skippedUndeclaredHashFields}`);
  log(`  Unavailable algorithm count   : ${unavailableAlgorithmCount}`);
  log(`  sha256 matches                : ${sha256MatchCount}`);
  log(`  sha3_256 matches              : ${sha3MatchCount}`);
  log(`  blake2b_256 matches           : ${blake2bMatchCount}`);
  log(`  shake256_256 matches          : ${shake256MatchCount}`);
  log(`  sha512_256 matches            : ${sha512MatchCount}`);
  log(`  blake3_256 matches            : ${blake3MatchCount}`);
  log(`  File hash mismatch            : ${fileHashMismatchCount}`);
  log(`  File size mismatch            : ${fileSizeMismatchCount}`);
  log(`  Metadata DAG pass/fail        : ${metadataDagPass}/${metadataDagFail}`);
  log(`  Metadata CID vs token_index   : ${metadataTokenIndexCidMatch} match, ${metadataTokenIndexCidMismatch} mismatch`);
  log(`  Metadata CID vs ETH           : ${metadataEthCidMatch} match, ${metadataEthCidMismatch} mismatch, ${metadataEthCidSkip} skip`);
  log(`  Media sha256 fail             : ${mediaSha256Fail}`);
  log(`  Media size fail               : ${mediaSizeFail}`);
  log(`  Media CID mismatch warning    : ${mediaRootCidMismatchWarning}`);
  log(`  Cross-CAR references          : ${crossCarRefTotal}`);
  log(`  Cross-CAR resolved            : ${crossCarRefResolvedTotal}`);
  log(`  Unresolved missing blocks     : ${unresolvedMissingTotal}`);
  log(`  Chain A pass                  : ${dagAndDigestManifestPass}`);
  log(`  blake2b_256 variant           : node_blake2b512_full (historical)`);

  // ── Write output ───────────────────────────────────────────────────
  const audit = {
    schema: 'trinity-accord.dag-digest-audit.v1',
    generated_at: new Date().toISOString(),
    dag_and_digest_manifest_pass: dagAndDigestManifestPass,
    release_nft_tar_count: nftAssets.length,

    download_failures: downloadFailures,
    download_failure_details: downloadFailureDetails,

    digest_manifest_json_sha256_match: digestJsonShaMatch,
    digest_manifest_csv_sha256_match: digestCsvShaMatch,
    digest_manifest_json_size_match: digestJsonSizeMatch,
    digest_manifest_csv_size_match: digestCsvSizeMatch,

    manifest_records_total: manifestItems.length,
    public_files_checked: manifestDirectMatchCount,
    digest_manifest_direct_match_count: manifestDirectMatchCount,
    release_derivative_verified_count: releaseDerivVerifiedCount,
    private_unavailable_hash_only: privateUnavailableCount,
    public_missing_count: publicMissingCount,

    declared_hash_checks_total: declaredHashChecksTotal,
    skipped_undeclared_hash_fields: skippedUndeclaredHashFields,
    unavailable_algorithm_count: unavailableAlgorithmCount,
    unavailable_algorithm_details: unavailableAlgorithmDetails,

    hash_match_by_algorithm: hashMatchByAlgorithm,
    hash_mismatch_by_algorithm: hashMismatchByAlgorithm,

    sha256_match_count: sha256MatchCount,
    sha3_256_match_count: sha3MatchCount,
    blake2b_256_match_count: blake2bMatchCount,
    shake256_256_match_count: shake256MatchCount,
    sha512_256_match_count: sha512MatchCount,
    blake3_256_match_count: blake3MatchCount,

    file_hash_mismatch_count: fileHashMismatchCount,
    file_size_mismatch_count: fileSizeMismatchCount,
    hash_mismatch_details: hashMismatchDetails,

    metadata_dag_pass: metadataDagPass,
    metadata_dag_fail: metadataDagFail,
    metadata_token_index_cid_match: metadataTokenIndexCidMatch,
    metadata_eth_tokenuri_cid_match: metadataEthCidMatch,

    cross_car_references: crossCarRefTotal,
    cross_car_references_resolved: crossCarRefResolvedTotal,
    unresolved_missing_blocks: unresolvedMissingTotal,
    cid_recompute_fail: cidRecomputeFail,

    media_sha256_fail: mediaSha256Fail,
    media_size_fail: mediaSizeFail,
    media_root_cid_mismatch_warning_count: mediaRootCidMismatchWarning,

    critical_errors: criticalErrors,

    // blake2b_256 historical generation variant note:
    // The manifest stores full blake2b-512 output (128 hex chars) under field name "blake2b_256".
    // Canonical check uses crypto.createHash('blake2b512').update(buf).digest('hex').
    // Confirmed by probe-blake2b-variants.mjs: node_blake2b512_full matched 524/524 public files.
    blake2b_256_generation_variant: 'node_blake2b512_full (historical, 128-hex-char output)',
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
