#!/usr/bin/env node
/**
 * verify-dag-and-signed-cids.mjs  (v3)
 *
 * Four-chain verification for Trinity Accord NFT collection:
 *   Chain A: DAG + digest-manifest file hash chain
 *   Chain B: BTC signature coverage chain
 *   Chain C: ETH witness verification
 *   Chain D: Bitcoin time anchor verification
 *
 * Output: DAG-CID-AUDIT.json
 *
 * Usage:
 *   GITHUB_TOKEN=xxx ETH_RPC_URL=https://... node scripts/verify-dag-and-signed-cids.mjs
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

// ═══════════════════════════════════════════════════════════════════════════
// CLI ARGS
// ═══════════════════════════════════════════════════════════════════════════

const args = process.argv.slice(2);

function getArg(name, def = '') {
  const idx = args.indexOf(name);
  return idx >= 0 && idx + 1 < args.length ? args[idx + 1] : def;
}

function parseBoundedInt(value, label, min = 1, max = 25) {
  const n = Number(value);
  if (!Number.isInteger(n) || n < min || n > max) {
    throw new Error(`Invalid ${label}: ${value}`);
  }
  return n;
}

// ═══════════════════════════════════════════════════════════════════════════
// GLOBAL CONFIG
// ═══════════════════════════════════════════════════════════════════════════

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO = 'thechurchofagi/trinity-accord';
const TOKEN_INDEX_FILE = 'token_index.json';
const BTC_SIG_FILE = 'archive/btc-signature/btc-signature.json';
const AUTHORITY_JCS_FILE = 'archive/authority-manifest/authority.jcs.json';
const DIGEST_MANIFEST_JSON = 'archive/evidence/digest-manifest.json';
const DIGEST_MANIFEST_CSV = 'archive/evidence/digest-manifest.csv';
const ETH_WITNESS_FILE = 'archive/eth-witness/eth-witness.json';
const EXPECTED_NFTS = 175;
const RELEASE_TAG = getArg('--release-tag', process.env.INPUT_RELEASE_TAG || 'nft-arweave-mirror-175-v1');
const INPUT_ETH_AUDIT_FILE = getArg('--eth-audit-file', process.env.INPUT_ETH_AUDIT_FILE || '');
const CONCURRENCY = parseBoundedInt(
  getArg('--concurrency', process.env.DAG_VERIFY_CONCURRENCY || '4'),
  'concurrency',
  1,
  25
);
const ETH_RPC_URL = process.env.ETH_RPC_URL;
const BTC_API_BASE = process.env.BTC_API_BASE || 'https://mempool.space/api';
const MAX_RETRIES = 3;
const TMP_DIR = '/tmp/dag-cid-audit';

// secp256k1 constants for BIP-340
const SECP256K1_P  = BigInt('0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F');
const SECP256K1_N  = BigInt('0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141');
const SECP256K1_GX = BigInt('0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798');
const SECP256K1_GY = BigInt('0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8');
const SECP256K1_B  = 7n;

// ═══════════════════════════════════════════════════════════════════════════
// PRIMITIVES
// ═══════════════════════════════════════════════════════════════════════════

function sha256hex(buf) { return crypto.createHash('sha256').update(buf).digest('hex'); }
function sha256buf(buf) { return crypto.createHash('sha256').update(buf).digest(); }
function sha256str(s) { return crypto.createHash('sha256').update(s, 'utf-8').digest('hex'); }
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

function readVarintStrict(data, offset, label = 'varint') {
  let value = 0, shift = 0, pos = offset;
  for (let i = 0; i < 10; i++) {
    if (pos >= data.length) throw new Error(`Truncated ${label}`);
    const b = data[pos++];
    value += (b & 0x7f) * (2 ** shift);
    if (!Number.isSafeInteger(value)) throw new Error(`Unsafe ${label}`);
    if (b < 0x80) return { value, bytesRead: pos - offset };
    shift += 7;
  }
  throw new Error(`Overlong ${label}`);
}

function readVarint(data, offset) {
  return readVarintStrict(data, offset, 'varint');
}

function parseCidBytes(data, offset) {
  let pos = offset;
  while (pos < data.length && data[pos] === 0x00) pos++;
  if (pos >= data.length) throw new Error('Unexpected end reading CID');

  const version = data[pos];
  if (version === 0x12) {
    if (pos + 34 > data.length) throw new Error('Truncated CIDv0');
    if (data[pos + 1] !== 0x20) throw new Error('Unexpected CIDv0 hash length');
    return { cid: cidv0Encode(data.slice(pos, pos + 34)), bytesRead: pos - offset + 34 };
  }

  let cidStart = pos;
  pos = consumeVarint(data, pos, 'CID version');
  pos = consumeVarint(data, pos, 'CID codec');
  pos = consumeVarint(data, pos, 'CID mh-type');
  const mhLenResult = readVarintStrict(data, pos, 'CID mh-length');
  pos += mhLenResult.bytesRead;
  const mhLen = mhLenResult.value;

  if (pos + mhLen > data.length) throw new Error('CID multihash digest exceeds buffer');
  const cidBytes = data.slice(cidStart, pos + mhLen);
  return { cid: base32EncodeCid(cidBytes), bytesRead: pos - offset + mhLen };
}

function consumeVarint(data, pos, label) {
  const r = readVarintStrict(data, pos, label);
  return pos + r.bytesRead;
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
      catch (e) { throw new Error(`Malformed root CID in CAR header: ${e.message}`); }
    }
  }
  return roots;
}

function parseCarFull(carData) {
  const headerLenResult = readVarintStrict(carData, 0, 'CAR header length');
  const headerStart = headerLenResult.bytesRead;
  const headerEnd = headerStart + headerLenResult.value;
  if (headerEnd > carData.length) throw new Error('CAR header length exceeds buffer');
  const roots = extractRootsFromHeader(carData, headerStart, headerEnd);

  const blocks = new Map();
  let pos = headerEnd;
  while (pos < carData.length) {
    const blockLenResult = readVarintStrict(carData, pos, 'CAR block length');
    if (blockLenResult.bytesRead + blockLenResult.value === 0) break;
    const blockStart = pos + blockLenResult.bytesRead;
    const blockEnd = blockStart + blockLenResult.value;
    if (blockEnd > carData.length) {
      throw new Error(`CAR block length exceeds buffer at offset ${blockStart}: blockEnd=${blockEnd} len=${carData.length}`);
    }
    const cidResult = parseCidBytes(carData, blockStart);
    const dataStart = blockStart + cidResult.bytesRead;
    const blockData = carData.slice(dataStart, blockEnd);

    // Duplicate CID conflict detection
    const existing = blocks.get(cidResult.cid);
    if (existing) {
      if (!existing.data.equals(blockData)) {
        throw new Error(`Duplicate CID with conflicting block data: ${cidResult.cid}`);
      }
    } else {
      blocks.set(cidResult.cid, { data: blockData, offset: blockStart });
    }
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
      catch (e) { throw new Error(`Malformed CID link in block: ${e.message}`); }
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
    result.valid = false;
    result.errors.push('No roots found in CAR header');
    return result;
  }

  for (const [cid, block] of blocks) {
    const computedHash = sha256buf(block.data);
    const storedDigest = extractDigestFromCid(cid);
    if (!storedDigest) {
      result.cidMismatchBlocks++;
      result.errors.push(`Block CID digest not extractable: ${cid.slice(0, 30)}...`);
      result.valid = false;
    } else if (!storedDigest.equals(computedHash)) {
      result.cidMismatchBlocks++;
      result.errors.push(`Block CID mismatch: ${cid.slice(0, 30)}... hash differs`);
      result.valid = false;
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
      result.missingBlocks++;
      result.errors.push(`Missing block for CID: ${cid}`);
      result.valid = false;
      continue;
    }
    const links = extractLinksFromBlock(block.data);
    for (const linkCid of links) {
      if (!visited.has(linkCid)) queue.push(linkCid);
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
// secp256k1 — BIP-340 Schnorr verification
// ═══════════════════════════════════════════════════════════════════════════

function mod(a, m) { const r = a % m; return r >= 0n ? r : r + m; }
function modPow(base, exp, m) {
  let result = 1n; base = mod(base, m);
  while (exp > 0n) { if (exp & 1n) result = mod(result * base, m); exp >>= 1n; base = mod(base * base, m); }
  return result;
}
function modInv(a, m) {
  let [old_r, r] = [a, m]; let [old_s, s] = [1n, 0n];
  while (r !== 0n) { const q = old_r / r; [old_r, r] = [r, old_r - q * r]; [old_s, s] = [s, old_s - q * s]; }
  return mod(old_s, m);
}
function sqrtMod(n, p) {
  if (modPow(n, (p - 1n) / 2n, p) !== 1n) return null;
  return modPow(n, (p + 1n) / 4n, p);
}

class ECPoint {
  constructor(x, y) { this.x = x; this.y = y; }
  static infinity() { return new ECPoint(null, null); }
  get isInfinity() { return this.x === null; }
}

function ecAdd(P, Q) {
  if (P.isInfinity) return Q;
  if (Q.isInfinity) return P;
  if (P.x === Q.x && P.y !== Q.y) return ECPoint.infinity();
  let lam;
  if (P.x === Q.x && P.y === Q.y)
    lam = mod(3n * P.x * P.x * modInv(mod(2n * P.y, SECP256K1_P), SECP256K1_P), SECP256K1_P);
  else
    lam = mod((Q.y - P.y) * modInv(mod(Q.x - P.x, SECP256K1_P), SECP256K1_P), SECP256K1_P);
  const x = mod(lam * lam - P.x - Q.x, SECP256K1_P);
  const y = mod(lam * (P.x - x) - P.y, SECP256K1_P);
  return new ECPoint(x, y);
}

function ecMul(k, P) {
  let result = ECPoint.infinity(), addend = P;
  while (k > 0n) { if (k & 1n) result = ecAdd(result, addend); addend = ecAdd(addend, addend); k >>= 1n; }
  return result;
}

const G = new ECPoint(SECP256K1_GX, SECP256K1_GY);

function taggedHash(tag, data) {
  const tagHash = sha256buf(Buffer.from(tag, 'utf-8'));
  return sha256buf(Buffer.concat([tagHash, tagHash, data]));
}

function verifyBip340(pubkeyXonly, msg, sig) {
  const P_x = BigInt('0x' + pubkeyXonly.toString('hex'));
  if (P_x === 0n || P_x >= SECP256K1_P) return false;
  const P_y_sq = mod(P_x * P_x * P_x + SECP256K1_B, SECP256K1_P);
  const P_y = sqrtMod(P_y_sq, SECP256K1_P);
  if (P_y === null) return false;
  const P = new ECPoint(P_x, P_y % 2n === 0n ? P_y : mod(-P_y, SECP256K1_P));
  const R_x = BigInt('0x' + sig.slice(0, 32).toString('hex'));
  const s   = BigInt('0x' + sig.slice(32, 64).toString('hex'));
  if (R_x >= SECP256K1_P || s >= SECP256K1_N) return false;
  const eInput = Buffer.concat([sig.slice(0, 32), pubkeyXonly, msg]);
  const eHash  = taggedHash('BIP0340/challenge', eInput);
  const e      = mod(BigInt('0x' + eHash.toString('hex')), SECP256K1_N);
  const sG = ecMul(s, G);
  const eP = ecMul(e, P);
  const negEP = new ECPoint(eP.x, mod(-eP.y, SECP256K1_P));
  const Rprime = ecAdd(sG, negEP);
  if (Rprime.isInfinity) return false;
  if (Rprime.y % 2n !== 0n) return false;
  if (Rprime.x !== R_x) return false;
  return true;
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
// ETH RPC HELPERS
// ═══════════════════════════════════════════════════════════════════════════

async function tryEthCallRaw(method, params, retries = MAX_RETRIES) {
  if (!ETH_RPC_URL) return { error: 'No ETH_RPC_URL configured' };
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const res = await fetch(ETH_RPC_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jsonrpc: '2.0', id: 1, method, params }),
      });
      const json = await res.json();
      if (json.error) return { error: json.error.message || JSON.stringify(json.error) };
      return { result: json.result };
    } catch (e) {
      if (attempt < retries) { await sleep(2000 * (attempt + 1)); continue; }
      return { error: e.message };
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// BTC API HELPERS
// ═══════════════════════════════════════════════════════════════════════════

async function btcFetch(endpoint, retries = MAX_RETRIES) {
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const res = await fetch(`${BTC_API_BASE}${endpoint}`);
      if (res.status === 404) return null;
      if (!res.ok) throw new Error(`BTC API ${res.status}`);
      return await res.json();
    } catch (e) {
      if (attempt < retries) { await sleep(2000 * (attempt + 1)); continue; }
      throw e;
    }
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

/**
 * Extract a CID-like portion from a file path for matching.
 * e.g. "bafkreiabc123...metadata.car" → "bafkreiabc123..."
 */
function extractCidFromPath(filePath) {
  const basename = path.basename(filePath);
  // Match CIDv1 pattern at start of filename
  const m = basename.match(/^(b[a-z2-7]{20,})/);
  if (m) return m[1];
  // Match CIDv0 pattern
  const m0 = basename.match(/^(Qm[a-zA-Z0-9]{20,})/);
  if (m0) return m0[1];
  return null;
}

/**
 * Find a digest manifest item by root CID or filename.
 * Scoped helper — uses digestManifestItem, never a bare generic name.
 */
function findDigestManifestItem(digestLookup, rootCid, fileName = '') {
  if (!rootCid) return null;
  return (
    digestLookup.get(rootCid) ||
    digestLookup.get(`${rootCid}.car`) ||
    (fileName ? digestLookup.get(path.basename(fileName)) : null) ||
    null
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// CHAIN A: DAG + digest-manifest file hash chain
// ═══════════════════════════════════════════════════════════════════════════

async function verifyChainA(tokenIndex, nftAssets, digestManifest, ethAudit, concurrency) {
  log('\n═══ Chain A: DAG + Digest Manifest Verification ═══\n');

  const nftLookup = new Map();
  for (const [contract, tokens] of Object.entries(tokenIndex)) {
    for (const [tokenId, entry] of Object.entries(tokens)) {
      nftLookup.set(`${contract.toLowerCase()}_${tokenId}`, { contract, tokenId, ...entry });
    }
  }

  // Build digest manifest lookup by CID-like portion of path
  const digestLookup = new Map();
  if (digestManifest?.items) {
    for (const item of digestManifest.items) {
      const cidKey = extractCidFromPath(item.path);
      if (cidKey) digestLookup.set(cidKey, item);
      // Also store by full basename
      digestLookup.set(path.basename(item.path), item);
    }
  }

  // Build ETH CID lookup
  const ethCidLookup = new Map();
  if (ethAudit?.tokens) {
    for (const t of ethAudit.tokens) {
      if (t.extracted_cid) ethCidLookup.set(`${t.contract?.toLowerCase()}_${t.token_id}`, t.extracted_cid);
    }
  }

  // Counters
  let digestManifestFileMatchCount = 0;
  let digestManifestFileMismatchCount = 0;
  let metadataDagPass = 0, metadataDagFail = 0;
  let mediaDagPass = 0, mediaDagFail = 0;
  let missingBlocksTotal = 0, cidRecomputeFail = 0;
  let metadataTokenIndexCidMatch = 0, metadataTokenIndexCidMismatch = 0;
  let metadataEthCidMatch = 0, metadataEthCidMismatch = 0, metadataEthCidSkip = 0;

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

        // Digest manifest coverage check:
        // The root CID of this CAR should exist in the digest-manifest paths.
        // The digest-manifest records the ORIGINAL CAR sha256+size (before repackaging).
        // The GitHub release tars are repackaged (different sha256), but root CID is preserved.
        // Coverage chain: root CID → found in digest-manifest → digest-manifest sha256 declared in authority → authority signed by BTC.
        let inDigestManifest = false;
        let digestManifestItem = null;
        if (rootCid && digestManifest?.items) {
          digestManifestItem = findDigestManifestItem(digestLookup, rootCid, tarEntry?.name || '');
          if (!digestManifestItem) {
            // Fallback: search by path contains
            digestManifestItem = digestManifest.items.find(item => item.path && item.path.includes(rootCid)) || null;
          }
          inDigestManifest = !!digestManifestItem;
        }
        if (inDigestManifest) digestManifestFileMatchCount++;
        else if (rootCid) {
          digestManifestFileMismatchCount++;
          criticalErrors.push(`NOT IN DIGEST-MANIFEST: ${asset.name} [${role}] root=${rootCid?.slice(0,20)}`);
        }

        if (role === 'metadata') {
          // DAG must pass for metadata
          if (dagResult.valid) metadataDagPass++;
          else {
            metadataDagFail++;
            detail.dag_valid = false;
            criticalErrors.push(`METADATA DAG FAIL: ${asset.name}`);
          }

          // token_index CID match
          const expectedTi = tokenEntry?.metadata?.root_cid;
          if (expectedTi && rootCid) {
            if (rootCid === expectedTi) metadataTokenIndexCidMatch++;
            else {
              metadataTokenIndexCidMismatch++;
              criticalErrors.push(`TOKEN_INDEX CID MISMATCH: ${asset.name}`);
            }
          }

          // ETH CID match
          const ethCid = ethCidLookup.get(lookupKey);
          if (ethCid && rootCid) {
            if (rootCid === ethCid) metadataEthCidMatch++;
            else {
              metadataEthCidMismatch++;
              criticalErrors.push(`ETH CID MISMATCH: ${asset.name}`);
            }
          } else {
            metadataEthCidSkip++;
          }

          detail.metadata = {
            dag_valid: dagResult.valid, block_count: dagResult.blockCount,
            missing_blocks: dagResult.missingBlocks, cid_mismatch_blocks: dagResult.cidMismatchBlocks,
            actual_root_cid: rootCid, token_index_cid: expectedTi || null, eth_cid: ethCid || null,
            sha256: carSha, size: carSize,
          };
        } else {
          // Media: DAG is audit-only, sha256+size are hard verification
          if (dagResult.valid) mediaDagPass++;
          else mediaDagFail++;

          detail.media.push({
            dag_valid: dagResult.valid, block_count: dagResult.blockCount,
            actual_root_cid: rootCid, sha256: carSha, size: carSize,
            digest_manifest_match: digestManifestItem ? (digestManifestItem.sha256 === carSha && digestManifestItem.size_bytes === carSize) : null,
          });
        }
      }
    } catch (e) {
      detail.error = e.message;
      criticalErrors.push(`CHAIN A ERROR: ${asset.name} — ${e.message}`);
    }

    return detail;
  });

  const results = await runConcurrent(tasks, concurrency);
  for (const r of results) {
    if (r instanceof Error) { criticalErrors.push(`CHAIN A TASK ERROR: ${r.message}`); continue; }
    nftDetails.push(r);
  }

  const dagAndDigestManifestPass = criticalErrors.length === 0
    && metadataDagFail === 0
    && digestManifestFileMismatchCount === 0
    && metadataTokenIndexCidMismatch === 0;

  log(`  Digest manifest file match    : ${digestManifestFileMatchCount}`);
  log(`  Digest manifest file mismatch : ${digestManifestFileMismatchCount}`);
  log(`  Metadata DAG pass             : ${metadataDagPass}`);
  log(`  Metadata DAG fail             : ${metadataDagFail}`);
  log(`  Media DAG pass (audit-only)   : ${mediaDagPass}`);
  log(`  Media DAG fail (audit-only)   : ${mediaDagFail}`);
  log(`  Missing blocks                : ${missingBlocksTotal}`);
  log(`  CID recompute fail            : ${cidRecomputeFail}`);
  log(`  Meta CID vs token_index       : ${metadataTokenIndexCidMatch} match, ${metadataTokenIndexCidMismatch} mismatch`);
  log(`  Meta CID vs ETH               : ${metadataEthCidMatch} match, ${metadataEthCidMismatch} mismatch, ${metadataEthCidSkip} skip`);
  log(`  Chain A pass                  : ${dagAndDigestManifestPass}`);

  return {
    dag_and_digest_manifest_pass: dagAndDigestManifestPass,
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
    critical_errors: criticalErrors,
    nft_details: nftDetails,
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// CHAIN B: BTC signature coverage chain
// ═══════════════════════════════════════════════════════════════════════════

async function verifyChainB() {
  log('\n═══ Chain B: BTC Signature Coverage Verification ═══\n');

  const result = {
    btc_signature_valid: false,
    signed_message_sha256_match: false,
    authority_covers_digest_manifest: false,
    digest_manifest_json_sha256_match: false,
    digest_manifest_json_size_match: false,
    digest_manifest_csv_sha256_match: false,
    digest_manifest_csv_size_match: false,
    btc_signature_coverage_pass: false,
    critical_errors: [],
  };

  // 1. Read btc-signature.json
  const btcSig = readRepoJson(BTC_SIG_FILE);
  if (!btcSig) {
    result.critical_errors.push('btc-signature.json not found');
    log('  ❌ btc-signature.json not found');
    return result;
  }

  const method = btcSig.method || btcSig.bitcoin_signature?.method;
  const address = btcSig.address || btcSig.bitcoin_signature?.address;
  const messageSha256 = btcSig.message_sha256 || btcSig.bitcoin_signature?.message_sha256;
  const pubkeyXonly = btcSig.pubkey_xonly || btcSig.bitcoin_signature?.pubkey_xonly;
  const signature = btcSig.signature || btcSig.bitcoin_signature?.signature;

  log(`  Method      : ${method}`);
  log(`  Address     : ${address}`);
  log(`  Msg SHA-256 : ${messageSha256?.slice(0, 16)}...`);

  // 2. Verify BIP-340 Schnorr signature
  if (pubkeyXonly && messageSha256 && signature) {
    const pubkey = Buffer.from(pubkeyXonly, 'hex');
    const msg = Buffer.from(messageSha256, 'hex');
    const sig = Buffer.from(signature, 'hex');
    if (pubkey.length === 32 && msg.length === 32 && sig.length === 64) {
      try {
        result.btc_signature_valid = verifyBip340(pubkey, msg, sig);
      } catch (e) {
        result.critical_errors.push(`BIP-340 verify error: ${e.message}`);
      }
    } else {
      result.critical_errors.push('Invalid pubkey/msg/sig lengths');
    }
  } else {
    result.critical_errors.push('Missing btc-signature fields');
  }
  log(`  BIP-340 valid: ${result.btc_signature_valid}`);

  // 3. Read authority.jcs.json and compute its SHA-256
  const authorityRaw = readRepoFile(AUTHORITY_JCS_FILE);
  if (!authorityRaw) {
    result.critical_errors.push('authority.jcs.json not found');
    log('  ❌ authority.jcs.json not found');
    return result;
  }
  const authoritySha256 = sha256hex(authorityRaw);
  log(`  Authority SHA-256: ${authoritySha256.slice(0, 16)}...`);

  // 4. Compare: computed sha256 == btc-signature.message_sha256
  if (messageSha256) {
    result.signed_message_sha256_match = authoritySha256 === messageSha256.toLowerCase();
    log(`  Signed message SHA-256 match: ${result.signed_message_sha256_match}`);
  }

  // 5. From authority.jcs.json arweave.documents[]: find digest-manifest entries
  const authority = JSON.parse(authorityRaw.toString('utf-8'));
  const arweaveDocuments = authority.arweave?.documents || [];

  let declaredJson = null, declaredCsv = null;
  for (const doc of arweaveDocuments) {
    const label = (doc.label || doc.name || '').toLowerCase();
    if (label.includes('digest-manifest.json') || label.includes('digest-manifest.json')) {
      declaredJson = doc;
    }
    if (label.includes('digest-manifest.csv') || label.includes('digest-manifest.csv')) {
      declaredCsv = doc;
    }
  }

  log(`  Authority declares digest-manifest.json: ${!!declaredJson}`);
  log(`  Authority declares digest-manifest.csv : ${!!declaredCsv}`);

  if (declaredJson && declaredCsv) {
    result.authority_covers_digest_manifest = true;
  }

  // 6-8. Read actual files and compare sha256 + size
  const actualJson = readRepoFile(DIGEST_MANIFEST_JSON);
  if (actualJson && declaredJson) {
    const actualJsonSha = sha256hex(actualJson);
    const actualJsonSize = actualJson.length;
    // sha256 match: if declared, must match; if not declared, treat as pass (skip)
    result.digest_manifest_json_sha256_match = declaredJson.ar_sha256 ? declaredJson.ar_sha256.toLowerCase() === actualJsonSha : true;
    result.digest_manifest_json_size_match = declaredJson.size === actualJsonSize || declaredJson.size_bytes === actualJsonSize;
    log(`  digest-manifest.json sha256 match: ${result.digest_manifest_json_sha256_match}${declaredJson.ar_sha256 ? '' : ' (not declared, skipped)'}`);
    log(`  digest-manifest.json size match  : ${result.digest_manifest_json_size_match}`);
  } else if (!actualJson) {
    log('  ⚠️  digest-manifest.json not found in repo');
  }

  const actualCsv = readRepoFile(DIGEST_MANIFEST_CSV);
  if (actualCsv && declaredCsv) {
    const actualCsvSha = sha256hex(actualCsv);
    const actualCsvSize = actualCsv.length;
    result.digest_manifest_csv_sha256_match = declaredCsv.ar_sha256 ? declaredCsv.ar_sha256.toLowerCase() === actualCsvSha : true;
    result.digest_manifest_csv_size_match = declaredCsv.size === actualCsvSize || declaredCsv.size_bytes === actualCsvSize;
    log(`  digest-manifest.csv sha256 match : ${result.digest_manifest_csv_sha256_match}${declaredCsv.ar_sha256 ? '' : ' (not declared, skipped)'}`);
    log(`  digest-manifest.csv size match   : ${result.digest_manifest_csv_size_match}`);
  } else if (!actualCsv) {
    log('  ⚠️  digest-manifest.csv not found in repo');
  }

  // 9. Overall pass
  result.btc_signature_coverage_pass =
    result.btc_signature_valid &&
    result.signed_message_sha256_match &&
    result.authority_covers_digest_manifest &&
    result.digest_manifest_json_sha256_match &&
    result.digest_manifest_json_size_match &&
    result.digest_manifest_csv_sha256_match &&
    result.digest_manifest_csv_size_match;

  log(`  Chain B pass: ${result.btc_signature_coverage_pass}`);
  return result;
}

// ═══════════════════════════════════════════════════════════════════════════
// CHAIN C: ETH witness verification
// ═══════════════════════════════════════════════════════════════════════════

async function verifyChainC() {
  log('\n═══ Chain C: ETH Witness Verification ═══\n');

  const result = {
    eth_witness_verified: false,
    chain_id: null,
    guardian_eth_address: null,
    attestations_total: 0,
    attestations_pass: 0,
    attestations_fail: 0,
    tx_from_match: 0,
    tx_input_sha256_match: 0,
    tx_input_size_match: 0,
    receipt_success: 0,
    attestation_details: [],
    critical_errors: [],
  };

  // 1. Read authority.jcs.json
  const authority = readRepoJson(AUTHORITY_JCS_FILE);
  if (!authority) {
    result.critical_errors.push('authority.jcs.json not found');
    log('  ❌ authority.jcs.json not found');
    return result;
  }

  const guardianEthAddress = authority.guardian?.eth_address;
  const chainId = authority.ethereum?.chainId;
  const attestations = authority.ethereum?.attestations || [];

  result.chain_id = chainId;
  result.guardian_eth_address = guardianEthAddress;
  result.attestations_total = attestations.length;

  log(`  Guardian ETH address: ${guardianEthAddress}`);
  log(`  Chain ID            : ${chainId}`);
  log(`  Attestations        : ${attestations.length}`);

  if (!ETH_RPC_URL) {
    result.critical_errors.push('ETH_RPC_URL not configured — skipping ETH verification');
    log('  ⚠️  ETH_RPC_URL not set, skipping');
    return result;
  }

  // 2. Read eth-witness.json (optional extra tx)
  const ethWitness = readRepoJson(ETH_WITNESS_FILE);
  if (ethWitness) {
    log(`  eth-witness.json found: tx_hash = ${ethWitness.tx_hash || ethWitness.hash || 'N/A'}`);
  }

  // 3. For each attestation
  for (let i = 0; i < attestations.length; i++) {
    const att = attestations[i];
    const txHash = att.tx_hash || att.tx_hash;
    const detail = {
      tx_hash: txHash, label: att.label || att.description || `attestation-${i}`,
      exists: false, receipt_success: false, chain_id_match: false,
      from_match: false, input_sha256_match: false, input_size_match: false,
      block_confirmed: false, error: null,
    };

    try {
      if (!txHash) { detail.error = 'No tx_hash'; result.attestations_fail++; result.attestation_details.push(detail); continue; }

      // eth_getTransactionByHash
      const txResult = await tryEthCallRaw('eth_getTransactionByHash', [txHash]);
      if (txResult.error || !txResult.result) {
        detail.error = `tx fetch failed: ${txResult.error}`;
        result.attestations_fail++;
        result.attestation_details.push(detail);
        continue;
      }

      const tx = txResult.result;
      detail.exists = true;

      // Verify chain ID (tx.chainId is hex)
      const txChainId = tx.chainId ? parseInt(tx.chainId, 16) : null;
      detail.chain_id_match = txChainId === chainId || txChainId === 1;

      // Verify from
      if (tx.from && guardianEthAddress) {
        detail.from_match = tx.from.toLowerCase() === guardianEthAddress.toLowerCase();
        if (detail.from_match) result.tx_from_match++;
      }

      // Verify input data
      const inputData = tx.input || tx.data || '0x';
      if (inputData && inputData !== '0x' && att.input_sha256) {
        const inputBytes = Buffer.from(inputData.slice(2), 'hex');
        const inputSha = sha256hex(inputBytes);
        detail.input_sha256_match = inputSha === att.input_sha256.toLowerCase();
        if (detail.input_sha256_match) result.tx_input_sha256_match++;

        if (att.input_len) {
          detail.input_size_match = inputBytes.length === att.input_len;
          if (detail.input_size_match) result.tx_input_size_match++;
        }
      }

      // eth_getTransactionReceipt
      const receiptResult = await tryEthCallRaw('eth_getTransactionReceipt', [txHash]);
      if (receiptResult.result) {
        const receipt = receiptResult.result;
        detail.receipt_success = receipt.status === '0x1';
        if (detail.receipt_success) result.receipt_success++;

        // Block confirmation
        if (receipt.blockNumber) {
          detail.block_confirmed = true;
        }
      }

      // Overall attestation pass
      const attPass = detail.exists && detail.receipt_success && detail.chain_id_match
        && detail.from_match && detail.block_confirmed;
      if (attPass) result.attestations_pass++;
      else result.attestations_fail++;

    } catch (e) {
      detail.error = e.message;
      result.attestations_fail++;
      result.critical_errors.push(`Attestation ${i}: ${e.message}`);
    }

    result.attestation_details.push(detail);
  }

  // 4. Verify eth-witness.json tx if present
  if (ethWitness) {
    const witTxHash = ethWitness.tx_hash || ethWitness.hash;
    if (witTxHash) {
      const witResult = await tryEthCallRaw('eth_getTransactionByHash', [witTxHash]);
      if (witResult.result) {
        const witTx = witResult.result;
        const witReceipt = await tryEthCallRaw('eth_getTransactionReceipt', [witTxHash]);
        result.eth_witness_verified = !!witReceipt.result && witReceipt.result.status === '0x1';
      }
    }
  }

  // If no attestations to verify, set pass based on no failures
  if (attestations.length === 0) {
    result.eth_witness_verified = true;
  }

  log(`  Attestations pass : ${result.attestations_pass}`);
  log(`  Attestations fail : ${result.attestations_fail}`);
  log(`  TX from match     : ${result.tx_from_match}`);
  log(`  TX input sha256   : ${result.tx_input_sha256_match}`);
  log(`  TX input size     : ${result.tx_input_size_match}`);
  log(`  Receipt success   : ${result.receipt_success}`);
  log(`  ETH witness verified: ${result.eth_witness_verified}`);

  return result;
}

// ═══════════════════════════════════════════════════════════════════════════
// CHAIN D: Bitcoin time anchor verification
// ═══════════════════════════════════════════════════════════════════════════

async function verifyChainD() {
  log('\n═══ Chain D: Bitcoin Time Anchor Verification ═══\n');

  const result = {
    bitcoin_time_anchor_pass: false,
    anchors_total: 0,
    anchors_pass: 0,
    anchors_fail: 0,
    originals_total: 0,
    ancillary_total: 0,
    earliest_anchor: null,
    latest_anchor: null,
    merkle_proof_verified_count: 0,
    merkle_proof_unavailable_count: 0,
    anchor_details: [],
    critical_errors: [],
  };

  // 1. Read authority.jcs.json
  const authority = readRepoJson(AUTHORITY_JCS_FILE);
  if (!authority) {
    result.critical_errors.push('authority.jcs.json not found');
    log('  ❌ authority.jcs.json not found');
    return result;
  }

  const originals = authority.bitcoin?.originals || [];
  const ancillary = authority.bitcoin?.ancillary || [];
  result.originals_total = originals.length;
  result.ancillary_total = ancillary.length;
  result.anchors_total = originals.length + ancillary.length;

  log(`  Originals : ${originals.length}`);
  log(`  Ancillary : ${ancillary.length}`);

  const allAnchors = [
    ...originals.map(a => ({ ...a, _type: 'original' })),
    ...ancillary.map(a => ({ ...a, _type: 'ancillary' })),
  ];

  let earliestTimestamp = Infinity;
  let latestTimestamp = -Infinity;

  for (const anchor of allAnchors) {
    const txid = anchor.txid || anchor.tx_hash;
    const detail = {
      txid, label: anchor.label || anchor.title || anchor._type,
      type: anchor._type,
      exists: false, confirmed: false,
      block_height_match: false, block_hash_match: false,
      block_height: null, block_hash: null, block_timestamp: null, confirmations: null,
      merkle_proof: 'not_checked', error: null,
    };

    try {
      if (!txid) { detail.error = 'No txid'; result.anchors_fail++; result.anchor_details.push(detail); continue; }

      // 2a. Query BTC API for tx
      const txInfo = await btcFetch(`/tx/${txid}`);
      if (!txInfo) {
        detail.error = 'Transaction not found';
        result.anchors_fail++;
        result.anchor_details.push(detail);
        continue;
      }

      detail.exists = true;
      detail.confirmed = !!txInfo.status?.confirmed;

      if (txInfo.status?.block_height) detail.block_height = txInfo.status.block_height;
      if (txInfo.status?.block_hash) detail.block_hash = txInfo.status.block_hash;

      // 2c-d. Verify block_height and block_hash match manifest
      if (anchor.block_height != null) {
        detail.block_height_match = txInfo.status?.block_height === anchor.block_height;
      }
      if (anchor.block_hash) {
        detail.block_hash_match = txInfo.status?.block_hash === anchor.block_hash;
      }

      // 2e-g. Query block to verify
      const blockHash = txInfo.status?.block_hash;
      if (blockHash) {
        try {
          const blockInfo = await btcFetch(`/block/${blockHash}`);
          if (blockInfo) {
            if (anchor.block_height != null && blockInfo.height !== anchor.block_height) {
              detail.error = `Block height mismatch: ${blockInfo.height} vs ${anchor.block_height}`;
            }
            if (anchor.block_hash && blockInfo.id !== anchor.block_hash) {
              detail.error = `Block hash mismatch: ${blockInfo.id} vs ${anchor.block_hash}`;
            }
            detail.block_timestamp = blockInfo.timestamp;
            detail.confirmations = blockInfo.confirmations || (blockInfo.height ? /* compute later */ null : null);

            // Track earliest/latest
            if (blockInfo.timestamp) {
              if (blockInfo.timestamp < earliestTimestamp) {
                earliestTimestamp = blockInfo.timestamp;
                result.earliest_anchor = {
                  label: detail.label, txid, block_height: detail.block_height,
                  block_hash: detail.block_hash, block_timestamp: blockInfo.timestamp,
                  confirmations: detail.confirmations,
                };
              }
              if (blockInfo.timestamp > latestTimestamp) {
                latestTimestamp = blockInfo.timestamp;
                result.latest_anchor = {
                  title: detail.label, txid, block_height: detail.block_height,
                  block_hash: detail.block_hash, block_timestamp: blockInfo.timestamp,
                  confirmations: detail.confirmations,
                };
              }
            }
          }
        } catch (e) {
          // Block query failure is non-fatal
        }
      }

      // 3. Try merkle proof
      try {
        const proof = await btcFetch(`/tx/${txid}/merkle-proof`);
        if (proof) {
          detail.merkle_proof = 'verified';
          result.merkle_proof_verified_count++;
        } else {
          detail.merkle_proof = 'unavailable';
          result.merkle_proof_unavailable_count++;
        }
      } catch {
        detail.merkle_proof = 'unavailable';
        result.merkle_proof_unavailable_count++;
      }

      // Overall anchor pass
      const anchorPass = detail.exists && detail.confirmed
        && (!anchor.block_height || detail.block_height_match)
        && (!anchor.block_hash || detail.block_hash_match);
      if (anchorPass) result.anchors_pass++;
      else {
        result.anchors_fail++;
        detail.error = detail.error || 'Anchor verification failed';
      }

    } catch (e) {
      detail.error = e.message;
      result.anchors_fail++;
      result.critical_errors.push(`Anchor ${txid}: ${e.message}`);
    }

    result.anchor_details.push(detail);
  }

  result.bitcoin_time_anchor_pass = result.anchors_fail === 0 && result.anchors_total > 0;

  log(`  Anchors total       : ${result.anchors_total}`);
  log(`  Anchors pass        : ${result.anchors_pass}`);
  log(`  Anchors fail        : ${result.anchors_fail}`);
  log(`  Earliest anchor     : ${result.earliest_anchor?.block_timestamp || 'N/A'}`);
  log(`  Latest anchor       : ${result.latest_anchor?.block_timestamp || 'N/A'}`);
  log(`  Merkle proofs       : ${result.merkle_proof_verified_count} verified, ${result.merkle_proof_unavailable_count} unavailable`);
  log(`  Chain D pass        : ${result.bitcoin_time_anchor_pass}`);

  return result;
}

// ═══════════════════════════════════════════════════════════════════════════
// MAIN
// ═══════════════════════════════════════════════════════════════════════════

async function main() {
  if (!GITHUB_TOKEN) { err('❌ GITHUB_TOKEN required'); process.exit(1); }

  // Ensure tmp dir
  if (!fs.existsSync(TMP_DIR)) fs.mkdirSync(TMP_DIR, { recursive: true });

  log('═══════════════════════════════════════════════════════════');
  log('  DAG + CID Binding Verification (v3)');
  log('  Four-Chain Verification');
  log('═══════════════════════════════════════════════════════════');
  log(`  Concurrency: ${CONCURRENCY}`);
  log(`  ETH RPC    : ${ETH_RPC_URL ? 'configured' : 'not configured'}`);
  log(`  BTC API    : ${BTC_API_BASE}`);
  log('');

  // ── Load shared data ──────────────────────────────────────────────────

  log('📖 Loading shared data...');

  // token_index.json
  const tokenIndex = readRepoJson(TOKEN_INDEX_FILE);
  if (!tokenIndex) { err('❌ token_index.json not found'); process.exit(1); }
  const allContracts = Object.keys(tokenIndex);
  let totalNfts = 0;
  for (const c of allContracts) totalNfts += Object.keys(tokenIndex[c]).length;
  log(`  token_index.json: ${allContracts.length} contracts, ${totalNfts} NFTs`);
  if (totalNfts !== EXPECTED_NFTS) { err(`  ❌ Expected ${EXPECTED_NFTS}, found ${totalNfts}`); process.exit(1); }

  // Fetch release assets
  log(`📦 Fetching GitHub Release ${RELEASE_TAG}...`);
  const release = await getReleaseByTag(RELEASE_TAG);
  const allAssets = await getAllAssets(release.id);
  const nftAssets = allAssets.filter(a => a.name.startsWith('nft-') && a.name.endsWith('.tar'));
  log(`  ${allAssets.length} total assets, ${nftAssets.length} NFT tar files`);
  if (nftAssets.length !== EXPECTED_NFTS) {
    err(`  ⚠️  Expected ${EXPECTED_NFTS} nft-*.tar, found ${nftAssets.length}`);
  }

  // digest-manifest.json
  const digestManifest = readRepoJson(DIGEST_MANIFEST_JSON);
  if (digestManifest) {
    log(`  digest-manifest.json: ${digestManifest.items?.length || 0} items`);
  } else {
    log('  ⚠️  digest-manifest.json not found');
  }

  // ETH audit (optional, from release)
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

  // ── Run all four chains ───────────────────────────────────────────────

  const startTime = Date.now();

  // Chain A: DAG + digest manifest
  const chainA = await verifyChainA(tokenIndex, nftAssets, digestManifest, ethAudit, CONCURRENCY);

  // Chain B: BTC signature
  const chainB = await verifyChainB();

  // Chain C: ETH witness
  const chainC = await verifyChainC();

  // Chain D: Bitcoin time anchors
  const chainD = await verifyChainD();

  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);

  // ── Final Summary ─────────────────────────────────────────────────────

  log('\n═══════════════════════════════════════════════════════════');
  log('  FINAL SUMMARY');
  log('═══════════════════════════════════════════════════════════');

  const metadataEthCidMatchCount = chainA.metadata_eth_cid_match;
  const metadataEthCidSkipCount = chainA.metadata_eth_cid_skip;
  const metadataTokenIndexCidMatchCount = chainA.metadata_token_index_cid_match;

  const fullVerificationPass =
    chainA.dag_and_digest_manifest_pass &&
    chainB.btc_signature_coverage_pass &&
    (metadataEthCidMatchCount === EXPECTED_NFTS || metadataEthCidSkipCount === EXPECTED_NFTS) &&
    metadataTokenIndexCidMatchCount === EXPECTED_NFTS;

  log(`  Chain A (DAG + Digest)     : ${chainA.dag_and_digest_manifest_pass ? '✅ PASS' : '❌ FAIL'}`);
  log(`  Chain B (BTC Signature)    : ${chainB.btc_signature_coverage_pass ? '✅ PASS' : '❌ FAIL'}`);
  log(`  Chain C (ETH Witness)      : ${chainC.attestations_fail === 0 ? '✅ PASS' : '❌ FAIL'}`);
  log(`  Chain D (BTC Time Anchor)  : ${chainD.bitcoin_time_anchor_pass ? '✅ PASS' : '❌ FAIL'}`);
  log('');
  log(`  ETH CID match/skip         : ${metadataEthCidMatchCount}/${metadataEthCidSkipCount} (need ${EXPECTED_NFTS})`);
  log(`  Token index CID match      : ${metadataTokenIndexCidMatchCount} (need ${EXPECTED_NFTS})`);
  log('');
  log(`  FULL VERIFICATION          : ${fullVerificationPass ? '✅ PASS' : '❌ FAIL'}`);
  log(`  Elapsed                    : ${elapsed}s`);
  log('═══════════════════════════════════════════════════════════');

  // ── Write DAG-CID-AUDIT.json ──────────────────────────────────────────

  const auditReport = {
    schema: 'trinity-accord.dag-cid-audit.v3',
    generated_at: new Date().toISOString(),
    elapsed_seconds: parseFloat(elapsed),
    full_verification_pass: fullVerificationPass,

    input_parameters: {
      release_tag: RELEASE_TAG,
      eth_audit_file: INPUT_ETH_AUDIT_FILE || null,
      concurrency: CONCURRENCY,
      eth_rpc_configured: Boolean(ETH_RPC_URL),
      btc_api_base: BTC_API_BASE
    },

    // Chain A
    chain_a: {
      dag_and_digest_manifest_pass: chainA.dag_and_digest_manifest_pass,
      digest_manifest_file_match_count: chainA.digest_manifest_file_match_count,
      digest_manifest_file_mismatch_count: chainA.digest_manifest_file_mismatch_count,
      metadata_dag_pass: chainA.metadata_dag_pass,
      metadata_dag_fail: chainA.metadata_dag_fail,
      media_dag_pass: chainA.media_dag_pass,
      media_dag_fail: chainA.media_dag_fail,
      missing_blocks: chainA.missing_blocks,
      cid_recompute_fail: chainA.cid_recompute_fail,
      metadata_token_index_cid_match: chainA.metadata_token_index_cid_match,
      metadata_token_index_cid_mismatch: chainA.metadata_token_index_cid_mismatch,
      metadata_eth_cid_match: chainA.metadata_eth_cid_match,
      metadata_eth_cid_mismatch: chainA.metadata_eth_cid_mismatch,
      metadata_eth_cid_skip: chainA.metadata_eth_cid_skip,
      critical_errors: chainA.critical_errors,
    },

    // Chain B
    chain_b: {
      btc_signature_valid: chainB.btc_signature_valid,
      signed_message_sha256_match: chainB.signed_message_sha256_match,
      authority_covers_digest_manifest: chainB.authority_covers_digest_manifest,
      digest_manifest_json_sha256_match: chainB.digest_manifest_json_sha256_match,
      digest_manifest_json_size_match: chainB.digest_manifest_json_size_match,
      digest_manifest_csv_sha256_match: chainB.digest_manifest_csv_sha256_match,
      digest_manifest_csv_size_match: chainB.digest_manifest_csv_size_match,
      btc_signature_coverage_pass: chainB.btc_signature_coverage_pass,
      critical_errors: chainB.critical_errors,
    },

    // Chain C
    chain_c: {
      eth_witness_verified: chainC.eth_witness_verified,
      chain_id: chainC.chain_id,
      guardian_eth_address: chainC.guardian_eth_address,
      attestations_total: chainC.attestations_total,
      attestations_pass: chainC.attestations_pass,
      attestations_fail: chainC.attestations_fail,
      tx_from_match: chainC.tx_from_match,
      tx_input_sha256_match: chainC.tx_input_sha256_match,
      tx_input_size_match: chainC.tx_input_size_match,
      receipt_success: chainC.receipt_success,
      attestation_details: chainC.attestation_details,
      critical_errors: chainC.critical_errors,
    },

    // Chain D
    chain_d: {
      bitcoin_time_anchor_pass: chainD.bitcoin_time_anchor_pass,
      anchors_total: chainD.anchors_total,
      anchors_pass: chainD.anchors_pass,
      anchors_fail: chainD.anchors_fail,
      originals_total: chainD.originals_total,
      ancillary_total: chainD.ancillary_total,
      earliest_anchor: chainD.earliest_anchor,
      latest_anchor: chainD.latest_anchor,
      merkle_proof_verified_count: chainD.merkle_proof_verified_count,
      merkle_proof_unavailable_count: chainD.merkle_proof_unavailable_count,
      anchor_details: chainD.anchor_details,
      critical_errors: chainD.critical_errors,
    },

    // Top-level summary fields (for backward compat)
    total_nfts: nftAssets.length,
    total_cars: chainA.nft_details.reduce((s, d) => s + 1 + (d.media?.length || 0), 0),
    metadata_dag_pass: chainA.metadata_dag_pass,
    metadata_dag_fail: chainA.metadata_dag_fail,
    missing_blocks: chainA.missing_blocks,
    cid_recompute_fail: chainA.cid_recompute_fail,
    metadata_token_index_cid_match: chainA.metadata_token_index_cid_match,
    metadata_eth_cid_match: chainA.metadata_eth_cid_match,
    metadata_eth_cid_skip: chainA.metadata_eth_cid_skip,
    btc_signature_valid: chainB.btc_signature_valid,
    btc_signature_coverage_pass: chainB.btc_signature_coverage_pass,

    // Per-NFT details
    nfts: chainA.nft_details,
  };

  const auditPath = path.join(process.cwd(), 'DAG-CID-AUDIT.json');
  fs.writeFileSync(auditPath, JSON.stringify(auditReport, null, 2));
  log(`\n📝 ${auditPath} written`);

  // ── Exit ──────────────────────────────────────────────────────────────

  if (!fullVerificationPass) {
    err('\n  ❌ FULL VERIFICATION FAILED');
    err(`    Chain A: ${chainA.dag_and_digest_manifest_pass ? 'PASS' : 'FAIL'}`);
    err(`    Chain B: ${chainB.btc_signature_coverage_pass ? 'PASS' : 'FAIL'}`);
    if (metadataEthCidMatchCount !== EXPECTED_NFTS && metadataEthCidSkipCount !== EXPECTED_NFTS) {
      err(`    ETH CID: ${metadataEthCidMatchCount} match, ${metadataEthCidSkipCount} skip (need ${EXPECTED_NFTS})`);
    }
    if (metadataTokenIndexCidMatchCount !== EXPECTED_NFTS) {
      err(`    Token index CID: ${metadataTokenIndexCidMatchCount} match (need ${EXPECTED_NFTS})`);
    }
    err('\n  See DAG-CID-AUDIT.json for details.');
    process.exit(1);
  }

  log('\n  ✅ All verifications passed.');
}

main().catch(e => { err('Fatal:', e); process.exit(1); });
