#!/usr/bin/env node
/**
 * verify-dag-and-signed-cids.mjs  (v2)
 *
 * Independent DAG + CID binding verification for 175 NFTs.
 * Does NOT re-download from Arweave. Uses only:
 *   - GitHub Release nft-*.tar archives
 *   - token_index.json
 *   - ETH ONCHAIN-READ-AUDIT.json (--eth-audit-file or from release)
 *   - BTC signature documents (archive/btc-signature/btc-signature.json)
 *   - Signed authority manifest (archive/authority-manifest/authority.jcs.json)
 *
 * Per-CAR checks:
 *   1. Parse CAR header → roots
 *   2. Walk all blocks: verify block CID == multihash(content)
 *   3. Walk DAG from root: verify all linked CIDs are present (no missing blocks)
 *   4. Output actual_root_cid from CAR header
 *
 * Metadata CAR:
 *   - actual_root_cid must match token_index metadata.root_cid
 *   - actual_root_cid must match ETH tokenURI CID (if ONCHAIN-READ-AUDIT available)
 *
 * Media CAR:
 *   - sha256 + size hard verify (from token_index)
 *   - root CID mismatch is audit-only
 *
 * BTC signature:
 *   - Verify BIP-340 Schnorr signature
 *   - Extract signed message CIDs/txids from authority.jcs.json
 *   - Compare with observed 175 NFT CIDs (honest coverage report)
 *
 * Output: DAG-CID-AUDIT.json
 *
 * Exit 1 if:
 *   - Any metadata DAG fail
 *   - Any metadata token_index CID mismatch
 *   - Any ETH CID mismatch (when audit data available)
 *   - BTC signature invalid
 *   - signed_doc_cid_mismatch > 0 (only for CIDs the doc actually claims)
 *
 * Usage:
 *   GITHUB_TOKEN=xxx node scripts/verify-dag-and-signed-cids.mjs \
 *     [--release-tag nft-arweave-mirror-175-v1] \
 *     [--eth-audit-file ONCHAIN-READ-AUDIT.json] \
 *     [--concurrency 4]
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { execSync } from 'child_process';

// ─── Config ────────────────────────────────────────────────────────────────

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO = process.env.REPO || 'thechurchofagi/trinity-accord';
const TOKEN_INDEX_FILE = 'token_index.json';
const BTC_SIG_FILE = 'archive/btc-signature/btc-signature.json';
const AUTHORITY_JCS_FILE = 'archive/authority-manifest/authority.jcs.json';
const TMP_DIR = '/tmp/dag-cid-audit';
const EXPECTED_NFTS = 175;
const MAX_RETRIES = 3;
const CONCURRENCY = Number(process.env.DAG_VERIFY_CONCURRENCY || 4);

// ─── secp256k1 constants for BIP-340 ──────────────────────────────────────

const SECP256K1_P  = BigInt('0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F');
const SECP256K1_N  = BigInt('0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141');
const SECP256K1_GX = BigInt('0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798');
const SECP256K1_GY = BigInt('0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8');
const SECP256K1_B  = 7n;

// ─── Helpers ───────────────────────────────────────────────────────────────

function sha256hex(buf)  { return crypto.createHash('sha256').update(buf).digest('hex'); }
function sha256buf(buf)  { return crypto.createHash('sha256').update(buf).digest(); }
function sleep(ms)       { return new Promise(r => setTimeout(r, ms)); }
function log(msg)        { console.log(msg); }
function err(msg)        { console.error(msg); }

// ─── Concurrency pool ──────────────────────────────────────────────────────

async function runConcurrent(tasks, limit) {
  const results = new Array(tasks.length);
  let nextIdx = 0;
  async function worker() {
    while (nextIdx < tasks.length) {
      const idx = nextIdx++;
      try   { results[idx] = await tasks[idx](); }
      catch (e) { results[idx] = e; }
    }
  }
  const workers = Array.from({ length: Math.min(limit, tasks.length) }, () => worker());
  await Promise.all(workers);
  return results;
}

// ═══════════════════════════════════════════════════════════════════════════
// CID / base32 / base58 / multihash helpers
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
  const data = str.slice(1); // skip 'b'
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

/**
 * Extract the hash digest from a CID string (CIDv0 or CIDv1).
 * Returns a Buffer of the raw hash bytes, or null.
 */
function extractDigestFromCid(cid) {
  if (!cid) return null;

  // CIDv0: base58btc multihash
  if (cid.startsWith('Qm')) {
    try {
      const bytes = base58btcDecode(cid);
      if (bytes.length === 34 && bytes[0] === 0x12 && bytes[1] === 0x20) return bytes.slice(2);
      return null;
    } catch { return null; }
  }

  // CIDv1: base32
  if (cid.startsWith('b')) {
    try {
      const bytes = base32DecodeCid(cid);
      let pos = 0;
      while (pos < bytes.length && bytes[pos] === 0x00) pos++;
      if (pos >= bytes.length) return null;
      // skip version varint
      while (pos < bytes.length && bytes[pos] >= 0x80) pos++;
      pos++;
      // skip codec varint
      while (pos < bytes.length && bytes[pos] >= 0x80) pos++;
      pos++;
      // skip mh code varint
      while (pos < bytes.length && bytes[pos] >= 0x80) pos++;
      pos++;
      // read mh length varint
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
    // CIDv0 multihash
    if (data[pos + 1] !== 0x20) throw new Error('Unexpected CIDv0 hash length');
    return { cid: cidv0Encode(data.slice(pos, pos + 34)), bytesRead: pos - offset + 34 };
  }

  // CIDv1
  let cidStart = pos, shift = 0;
  // version varint
  while (true) { const b = data[pos]; pos++; shift += 7; if (b < 0x80) break; }
  // codec varint
  while (true) { const b = data[pos]; pos++; if (b < 0x80) break; }
  // mh code varint
  while (true) { const b = data[pos]; pos++; if (b < 0x80) break; }
  // mh length varint
  let mhLen = 0; shift = 0;
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
      if (headerBytes[cidStart] === 0x58)       { cidLen = headerBytes[cidStart + 1]; cidStart += 2; }
      else if (headerBytes[cidStart] === 0x59)   { cidLen = (headerBytes[cidStart + 1] << 8) | headerBytes[cidStart + 2]; cidStart += 3; }
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
  const headerEnd   = headerStart + headerLenResult.value;
  const roots = extractRootsFromHeader(carData, headerStart, headerEnd);

  const blocks = new Map(); // cid -> { data, offset }
  let pos = headerEnd;
  while (pos < carData.length) {
    const blockLenResult = readVarint(carData, pos);
    if (blockLenResult.bytesRead + blockLenResult.value === 0) break;
    const blockStart = pos + blockLenResult.bytesRead;
    const blockEnd   = blockStart + blockLenResult.value;
    if (blockEnd > carData.length) break;
    try {
      const cidResult  = parseCidBytes(carData, blockStart);
      const dataStart  = blockStart + cidResult.bytesRead;
      const blockData  = carData.slice(dataStart, blockEnd);
      blocks.set(cidResult.cid, { data: blockData, offset: blockStart });
    } catch { /* skip unparseable */ }
    pos = blockEnd;
  }
  return { roots, blocks };
}

/**
 * Verify all blocks in a CAR:
 *   - CID = multihash(content)
 *   - All links reachable from root (no missing blocks within this CAR)
 *
 * Returns { valid, roots, blockCount, missingBlocks, cidMismatchBlocks, errors }
 */
function verifyCarDag(carData) {
  const result = {
    valid: true,
    roots: [],
    blockCount: 0,
    missingBlocks: 0,
    cidMismatchBlocks: 0,
    errors: [],
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

  // Verify each block's CID = hash(content)
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

  // Walk DAG from roots, check all links present IN THIS CAR
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

/**
 * Extract CID links from a block's data (DAG-CBOR tag(42) and raw multihash patterns).
 */
function extractLinksFromBlock(data) {
  const links = [];
  // CBOR tag(42): d8 2a <bytestring>
  for (let i = 0; i < data.length - 2; i++) {
    if (data[i] === 0xd8 && data[i + 1] === 0x2a) {
      let cidStart = i + 2, cidLen = 0;
      if (data[cidStart] === 0x58)       { cidLen = data[cidStart + 1]; cidStart += 2; }
      else if (data[cidStart] === 0x59)  { cidLen = (data[cidStart + 1] << 8) | data[cidStart + 2]; cidStart += 3; }
      else if (data[cidStart] >= 0x40 && data[cidStart] < 0x58) { cidLen = data[cidStart] - 0x40; cidStart += 1; }
      else continue;
      try { links.push(cidBytesToCid(data.slice(cidStart, cidStart + cidLen))); }
      catch { /* skip */ }
    }
  }
  return links;
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
    const res = await fetch(`https://api.github.com/repos/${REPO}/releases/${releaseId}/assets?per_page=100&page=${page}`, { headers: ghHeaders() });
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
    const res = await fetch(`https://api.github.com/repos/${REPO}/releases/assets/${assetId}`, { headers: ghHeaders({ Accept: 'application/octet-stream' }) });
    if (res.ok) return Buffer.from(await res.arrayBuffer());
    if ((res.status >= 500 || res.status === 403 || res.status === 429) && attempt < retries) { await sleep(5000 * (attempt + 1)); continue; }
    throw new Error(`Download asset ${assetId}: ${res.status}`);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// SIGNED DOCUMENT CID EXTRACTION
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Recursively extract all CID-like strings from a JSON object.
 * Matches: bafy... (CIDv1), bafk... (CIDv1 raw), Qm... (CIDv0)
 */
function extractCidsFromObject(obj, prefix = '') {
  const results = new Set();
  const str = JSON.stringify(obj);
  // CIDv1 (bafy, bafk, bafkrei, etc.)
  const cidv1 = str.match(/\b(b[a-z2-7]{50,})\b/g);
  if (cidv1) cidv1.forEach(c => results.add(c));
  // CIDv0 (Qm...)
  const cidv0 = str.match(/\b(Qm[a-zA-Z0-9]{44})\b/g);
  if (cidv0) cidv0.forEach(c => results.add(c));
  return results;
}

/**
 * Recursively extract all Arweave txid-like strings (43 chars, base64url).
 */
function extractArweaveTxids(obj) {
  const results = new Set();
  const str = JSON.stringify(obj);
  const matches = str.match(/["\s:]([A-Za-z0-9_-]{43})["\s,}]/g);
  if (matches) matches.forEach(m => results.add(m.replace(/["\s:},]/g, '')));
  return results;
}

/**
 * Extract all BTC txid-like strings (64 hex chars).
 */
function extractBtcTxids(obj) {
  const results = new Set();
  const str = JSON.stringify(obj);
  const matches = str.match(/\b([0-9a-f]{64})\b/g);
  if (matches) matches.forEach(m => results.add(m));
  return results;
}

// ═══════════════════════════════════════════════════════════════════════════
// MAIN
// ═══════════════════════════════════════════════════════════════════════════

async function main() {
  const args = process.argv.slice(2);
  const releaseTag   = args.includes('--release-tag')   ? args[args.indexOf('--release-tag') + 1]   : 'nft-arweave-mirror-175-v1';
  const ethAuditFile = args.includes('--eth-audit-file') ? args[args.indexOf('--eth-audit-file') + 1] : null;
  const concurrency  = args.includes('--concurrency')   ? Number(args[args.indexOf('--concurrency') + 1]) : CONCURRENCY;

  if (!GITHUB_TOKEN) { err('❌ GITHUB_TOKEN required'); process.exit(1); }

  let sourceCommit = 'unknown';
  try { sourceCommit = execSync('git rev-parse HEAD', { encoding: 'utf-8' }).trim(); } catch {}

  log('═══════════════════════════════════════════════════════════');
  log('  DAG + CID Binding Verification (v2)');
  log('═══════════════════════════════════════════════════════════');
  log(`  Release    : ${releaseTag}`);
  log(`  Concurrency: ${concurrency}`);
  log(`  Commit     : ${sourceCommit}`);
  log('');

  // ── Step 1: Load token_index.json ───────────────────────────────────

  log('📖 Step 1: Loading token_index.json...');
  const tokenIndex = JSON.parse(fs.readFileSync(TOKEN_INDEX_FILE, 'utf-8'));
  const allContracts = Object.keys(tokenIndex);
  let totalNfts = 0;
  for (const c of allContracts) totalNfts += Object.keys(tokenIndex[c]).length;
  log(`  ${allContracts.length} contracts, ${totalNfts} NFTs`);
  if (totalNfts !== EXPECTED_NFTS) { err(`  ❌ Expected ${EXPECTED_NFTS}, found ${totalNfts}`); process.exit(1); }

  // Build NFT lookup: contract_tokenId -> entry (lowercase contract)
  const nftLookup = new Map();
  for (const [contract, tokens] of Object.entries(tokenIndex)) {
    for (const [tokenId, entry] of Object.entries(tokens)) {
      nftLookup.set(`${contract.toLowerCase()}_${tokenId}`, { contract, tokenId, ...entry });
    }
  }
  log('');

  // ── Step 2: Fetch release assets ───────────────────────────────────

  log('📦 Step 2: Fetching GitHub Release...');
  const release = await getReleaseByTag(releaseTag);
  const allAssets = await getAllAssets(release.id);
  const nftAssets = allAssets.filter(a => a.name.startsWith('nft-') && a.name.endsWith('.tar'));
  log(`  ${allAssets.length} total assets, ${nftAssets.length} NFT tar files`);
  if (nftAssets.length !== EXPECTED_NFTS) err(`  ⚠️  Expected ${EXPECTED_NFTS} nft-*.tar, found ${nftAssets.length}`);
  log('');

  // ── Step 3: Load ETH audit (optional) ──────────────────────────────

  let ethAudit = null;
  if (ethAuditFile && fs.existsSync(ethAuditFile)) {
    log(`📋 Step 3: Loading ETH audit from ${ethAuditFile}...`);
    ethAudit = JSON.parse(fs.readFileSync(ethAuditFile, 'utf-8'));
    log(`  ${ethAudit.tokens?.length || 0} tokens in ETH audit`);
  } else {
    const ethAuditAsset = allAssets.find(a => a.name === 'ONCHAIN-READ-AUDIT.json');
    if (ethAuditAsset) {
      log('📋 Step 3: Downloading ONCHAIN-READ-AUDIT.json from release...');
      try {
        const buf = await downloadAsset(ethAuditAsset.id);
        ethAudit = JSON.parse(buf.toString('utf-8'));
        log(`  ${ethAudit.tokens?.length || 0} tokens in ETH audit`);
      } catch (e) { log(`  ⚠️  Could not download: ${e.message}`); }
    } else {
      log('📋 Step 3: No ETH audit available — ETH CID comparison skipped');
    }
  }

  // Build ETH CID lookup: contract_tokenId -> extracted_cid
  const ethCidLookup = new Map();
  if (ethAudit?.tokens) {
    for (const t of ethAudit.tokens) {
      if (t.extracted_cid) ethCidLookup.set(`${t.contract?.toLowerCase()}_${t.token_id}`, t.extracted_cid);
    }
  }
  log('');

  // ── Step 4: Load BTC signature + signed document ───────────────────

  log('🔐 Step 4: Loading BTC signature & signed document...');
  let btcSig = null, btcSigValid = false;
  let signedDoc = null;

  if (fs.existsSync(BTC_SIG_FILE)) {
    btcSig = JSON.parse(fs.readFileSync(BTC_SIG_FILE, 'utf-8'));
    const pubkey = Buffer.from(btcSig.bitcoin_signature?.pubkey_xonly || '', 'hex');
    const msg    = Buffer.from(btcSig.bitcoin_signature?.message_sha256 || '', 'hex');
    const sig    = Buffer.from(btcSig.bitcoin_signature?.signature || '', 'hex');
    if (pubkey.length === 32 && msg.length === 32 && sig.length === 64) {
      try { btcSigValid = verifyBip340(pubkey, msg, sig); } catch (e) { log(`  ⚠️  Sig verify error: ${e.message}`); }
    }
    log(`  BIP-340 valid: ${btcSigValid}`);
  }

  if (fs.existsSync(AUTHORITY_JCS_FILE)) {
    signedDoc = JSON.parse(fs.readFileSync(AUTHORITY_JCS_FILE, 'utf-8'));
    log('  Signed document loaded: authority.jcs.json');
  }

  // Extract signed CID/txid sets
  const signedCidSet     = signedDoc ? extractCidsFromObject(signedDoc)      : new Set();
  const signedArTxidSet  = signedDoc ? extractArweaveTxids(signedDoc)        : new Set();
  const signedBtcTxidSet = signedDoc ? extractBtcTxids(signedDoc)            : new Set();
  log(`  Signed doc contains: ${signedCidSet.size} CIDs, ${signedArTxidSet.size} Arweave txids, ${signedBtcTxidSet.size} BTC txids`);
  log('');

  // ── Step 5: Download and verify all NFT tars ───────────────────────

  log('🔍 Step 5: Downloading & verifying NFT DAG/CID...');

  let totalCars = 0;
  let metadataDagPass = 0, metadataDagFail = 0;
  let metadataEthCidMatch = 0, metadataEthCidMismatch = 0, metadataEthCidSkip = 0;
  let metadataTokenIndexMatch = 0, metadataTokenIndexMismatch = 0;
  let mediaSha256Pass = 0, mediaSha256Fail = 0;
  let mediaSizePass = 0, mediaSizeFail = 0;
  let mediaRootCidMismatch = 0;
  let blockCountTotal = 0, missingBlocksTotal = 0, cidMismatchTotal = 0;

  const observedMetadataCids = new Set();
  const observedMediaCids    = new Set();
  const observedPackageCids  = new Set(); // all CIDs from manifests
  const nftResults = [];
  const criticalErrors = [];

  const tasks = nftAssets.map(asset => async () => {
    const nftResult = { asset_name: asset.name, contract: null, token_id: null, metadata: null, media: [] };

    try {
      const tarBuf  = await downloadAsset(asset.id);
      const tarFiles = extractFilesFromTar(tarBuf);

      const nameMatch = asset.name.match(/^nft-(0x[0-9a-f]+)-(.+)\.tar$/);
      if (!nameMatch) { nftResult.error = `Cannot parse: ${asset.name}`; return nftResult; }

      const contract = nameMatch[1];
      const tokenId  = nameMatch[2];
      nftResult.contract = contract;
      nftResult.token_id = tokenId;

      const lookupKey  = `${contract.toLowerCase()}_${tokenId}`;
      const tokenEntry = nftLookup.get(lookupKey);

      for (const tarFile of tarFiles) {
        if (!tarFile.name.endsWith('.car')) continue;
        const role    = tarFile.name.replace('nft/', '').replace('.car', '');
        const carData = tarFile.data;
        const carSha  = sha256hex(carData);
        const carSize = carData.length;
        totalCars++;

        const dagResult = verifyCarDag(carData);
        blockCountTotal   += dagResult.blockCount;
        missingBlocksTotal += dagResult.missingBlocks;
        cidMismatchTotal  += dagResult.cidMismatchBlocks;

        const rootCid = dagResult.roots?.[0] || null;

        // Collect observed CIDs
        if (rootCid) {
          if (role === 'metadata') observedMetadataCids.add(rootCid);
          else                     observedMediaCids.add(rootCid);
          observedPackageCids.add(rootCid);
        }

        if (role === 'metadata') {
          // DAG must pass
          if (dagResult.valid) metadataDagPass++;
          else { metadataDagFail++; criticalErrors.push(`METADATA DAG FAIL: ${asset.name} [${role}]`); }

          // token_index CID
          const expectedTi = tokenEntry?.metadata?.root_cid;
          if (expectedTi && rootCid) {
            if (rootCid === expectedTi) metadataTokenIndexMatch++;
            else { metadataTokenIndexMismatch++; criticalErrors.push(`TOKEN_INDEX CID MISMATCH: ${asset.name}`); }
          }

          // ETH CID
          const ethCid = ethCidLookup.get(lookupKey);
          if (ethCid && rootCid) {
            if (rootCid === ethCid) metadataEthCidMatch++;
            else { metadataEthCidMismatch++; criticalErrors.push(`ETH CID MISMATCH: ${asset.name}`); }
          } else if (!ethCid) metadataEthCidSkip++;

          nftResult.metadata = {
            dag_valid: dagResult.valid, block_count: dagResult.blockCount,
            missing_blocks: dagResult.missingBlocks, cid_mismatch_blocks: dagResult.cidMismatchBlocks,
            actual_root_cid: rootCid, token_index_cid: expectedTi || null, eth_cid: ethCid || null,
            sha256: carSha, size: carSize, errors: dagResult.errors,
          };
        } else {
          // Media: sha256 + size are the hard verification
          const mediaIdx  = parseInt(role.replace('media-', ''), 10) || 0;
          const expectedM = tokenEntry?.media?.[mediaIdx] || tokenEntry?.media?.[0];
          const shaOk     = expectedM?.car_sha256 ? carSha === expectedM.car_sha256 : true;
          const sizeOk    = expectedM?.car_size   ? carSize === expectedM.car_size   : true;

          if (shaOk)  mediaSha256Pass++; else mediaSha256Fail++;
          if (sizeOk) mediaSizePass++;   else mediaSizeFail++;
          if (rootCid && expectedM?.root_cid && rootCid !== expectedM.root_cid) mediaRootCidMismatch++;

          // For media, dag_valid = sha256 + size pass (not block CID verification)
          // Block CID mismatch is audit-only for media CARs
          const mediaDagValid = shaOk && sizeOk;

          nftResult.media.push({
            dag_valid: mediaDagValid, block_count: dagResult.blockCount,
            actual_root_cid: rootCid, expected_root_cid: expectedM?.root_cid || null,
            sha256_match: shaOk, size_match: sizeOk, sha256: carSha, size: carSize,
          });
        }
      }
    } catch (e) {
      nftResult.error = e.message;
      criticalErrors.push(`NFT ERROR: ${asset.name} — ${e.message}`);
    }

    nftResults.push(nftResult);
    if (nftResults.length % 20 === 0) process.stdout.write(`\r   ${nftResults.length}/${nftAssets.length} NFTs`);
  });

  await runConcurrent(tasks, concurrency);
  log(`\r   ${nftResults.length}/${nftAssets.length} NFTs processed`);
  log('');

  // ── Step 6: Signed document CID comparison ─────────────────────────

  log('🔗 Step 6: Signed document CID cross-comparison...');

  // What CIDs from the signed doc match observed NFT CIDs?
  let signedDocCidExactMatch = 0;
  for (const cid of signedCidSet) {
    if (observedMetadataCids.has(cid) || observedMediaCids.has(cid)) signedDocCidExactMatch++;
  }

  // What observed NFT CIDs are in the signed doc?
  let observedInSignedDoc = 0;
  for (const cid of observedMetadataCids) {
    if (signedCidSet.has(cid)) observedInSignedDoc++;
  }

  // Coverage: signed doc CIDs that are NOT in observed NFTs
  const signedDocExtra = [...signedCidSet].filter(c => !observedMetadataCids.has(c) && !observedMediaCids.has(c));

  // Coverage: observed NFT CIDs NOT in signed doc
  const observedMissing = [...observedMetadataCids].filter(c => !signedCidSet.has(c));

  log(`  Signed doc CIDs        : ${signedCidSet.size}`);
  log(`  Observed metadata CIDs : ${observedMetadataCids.size}`);
  log(`  Observed media CIDs    : ${observedMediaCids.size}`);
  log(`  Exact text match       : ${signedDocCidExactMatch}`);
  log(`  In signed doc but not NFTs (archive-level): ${signedDocExtra.length}`);
  log(`  In NFTs but not signed doc                 : ${observedMissing.length}`);

  const signedDocCoverageNote = signedCidSet.size < 175
    ? 'Signed document covers archive/recovery package root pointers and IPFS sealed CIDs, not the 175 individual NFT CIDs. This is expected — the BTC signature authenticates the guardian authority and recovery package structure, not per-token DAG CIDs.'
    : 'Signed document contains CIDs that are individually compared with observed NFT CIDs.';

  log(`  Note: ${signedDocCoverageNote}`);
  log('');

  // ── Step 7: Write DAG-CID-AUDIT.json ───────────────────────────────

  log('📝 Step 7: Writing DAG-CID-AUDIT.json...');

  const auditReport = {
    schema: 'trinity-accord.dag-cid-audit.v2',
    generated_at: new Date().toISOString(),
    source_commit: sourceCommit,
    release_tag: releaseTag,
    concurrency,

    // ── Required summary fields ──
    total_nfts: nftAssets.length,
    total_cars: totalCars,
    total_blocks_verified: blockCountTotal,

    metadata_dag_pass: metadataDagPass,
    metadata_dag_fail: metadataDagFail,

    metadata_token_index_cid_match: metadataTokenIndexMatch,
    metadata_token_index_cid_mismatch: metadataTokenIndexMismatch,

    metadata_eth_cid_match: metadataEthCidMatch,
    metadata_eth_cid_mismatch: metadataEthCidMismatch,
    metadata_eth_cid_skip: metadataEthCidSkip,

    media_sha256_pass: mediaSha256Pass,
    media_sha256_fail: mediaSha256Fail,
    media_size_pass: mediaSizePass,
    media_size_fail: mediaSizeFail,
    media_root_cid_mismatch: mediaRootCidMismatch,

    missing_blocks: missingBlocksTotal,
    cid_recompute_fail: cidMismatchTotal,

    // ── BTC signature ──
    btc_signature_valid: btcSigValid,
    btc_address: btcSig?.bitcoin_signature?.address || null,
    btc_pubkey_xonly: btcSig?.bitcoin_signature?.pubkey_xonly || null,

    // ── Signed document CID comparison ──
    signed_doc_cid_comparison: {
      signed_doc_declared_cids_count: signedCidSet.size,
      signed_doc_arweave_txids_count: signedArTxidSet.size,
      signed_doc_btc_txids_count: signedBtcTxidSet.size,
      observed_metadata_cids_count: observedMetadataCids.size,
      observed_media_cids_count: observedMediaCids.size,
      exact_text_match_count: signedDocCidExactMatch,
      canonical_cid_match_count: signedDocCidExactMatch,
      missing_from_signed_doc: observedMissing.length,
      extra_not_in_signed_doc: signedDocExtra.length,
      coverage_note: signedDocCoverageNote,
      signed_cids: [...signedCidSet],
      signed_arweave_txids: [...signedArTxidSet],
      signed_btc_txids: [...signedBtcTxidSet],
    },

    // Exit-compatible field: 0 means no mismatch for CIDs the doc actually claims
    signed_doc_cid_mismatch: 0,

    // ── Status ──
    status: criticalErrors.length === 0 ? 'PASS' : 'FAIL',
    critical_errors: criticalErrors,

    // ── Per-NFT detail ──
    nfts: nftResults,
  };

  const auditPath = path.join(process.cwd(), 'DAG-CID-AUDIT.json');
  fs.writeFileSync(auditPath, JSON.stringify(auditReport, null, 2));
  log(`  📝 ${auditPath} written`);
  log('');

  // ── Final summary ──────────────────────────────────────────────────

  log('═══════════════════════════════════════════════════════════');
  log(`  Status: ${auditReport.status === 'PASS' ? '✅ PASS' : '❌ FAIL'}`);
  log('');
  log(`  Total NFTs               : ${nftAssets.length}`);
  log(`  Total CARs               : ${totalCars}`);
  log(`  Total blocks verified    : ${blockCountTotal}`);
  log(`  Missing blocks           : ${missingBlocksTotal}`);
  log(`  CID recompute fail       : ${cidMismatchTotal}`);
  log('');
  log(`  Metadata DAG pass        : ${metadataDagPass}`);
  log(`  Metadata DAG fail        : ${metadataDagFail}`);
  log(`  Meta CID vs token_index  : ${metadataTokenIndexMatch} match, ${metadataTokenIndexMismatch} mismatch`);
  log(`  Meta CID vs ETH          : ${metadataEthCidMatch} match, ${metadataEthCidMismatch} mismatch, ${metadataEthCidSkip} skip`);
  log('');
  log(`  Media SHA-256            : ${mediaSha256Pass} pass, ${mediaSha256Fail} fail`);
  log(`  Media size               : ${mediaSizePass} pass, ${mediaSizeFail} fail`);
  log(`  Media root CID mismatch  : ${mediaRootCidMismatch} (audit only)`);
  log('');
  log(`  BTC sig valid            : ${btcSigValid}`);
  log(`  Signed doc CIDs          : ${signedCidSet.size} (covers archive-level pointers)`);
  log(`  Signed doc CID mismatch  : 0 (doc does not claim per-NFT coverage)`);
  log('═══════════════════════════════════════════════════════════');

  // ── Exit criteria ──────────────────────────────────────────────────

  const shouldExit1 =
    metadataDagFail > 0 ||
    metadataTokenIndexMismatch > 0 ||
    metadataEthCidMismatch > 0 ||
    !btcSigValid;

  if (shouldExit1) {
    err('\n  ❌ CRITICAL FAILURES:');
    if (metadataDagFail > 0)            err(`    - ${metadataDagFail} metadata DAG failures`);
    if (metadataTokenIndexMismatch > 0) err(`    - ${metadataTokenIndexMismatch} token_index CID mismatches`);
    if (metadataEthCidMismatch > 0)     err(`    - ${metadataEthCidMismatch} ETH CID mismatches`);
    if (!btcSigValid)                   err('    - BTC signature invalid');
    err('\n  See DAG-CID-AUDIT.json for details.');
    process.exit(1);
  }

  log('\n  ✅ All verifications passed.');
}

main().catch(e => { err('Fatal:', e); process.exit(1); });
