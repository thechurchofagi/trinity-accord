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
 *   CONCURRENCY                        - max parallel downloads (default 10)
 *   MAX_RETRIES                        - retry count per file (default 3)
 *   GITHUB_TOKEN                       - GitHub PAT for release upload
 *   RELEASE_TAG                        - release tag (default: nft-backup-v1)
 *   DRY_RUN                            - set to "1" to only list txids without downloading
 *   CAR_FILE                           - path to recovery-package.bin
 *   NFT_CARS_TMP_DIR                   - explicit tmp directory (will be cleaned on start)
 *   MAX_CAR_BYTES                      - per-file size cap (default 500MB)
 *   MAX_TOTAL_BYTES                    - total verified size cap (default 10GB)
 *   EXPECTED_NFTS                      - expected NFT count (default 175)
 *   EXPECTED_RECOVERY_PACKAGE_SHA256   - required recovery package sha256 (64hex)
 *   RECOVERY_PACKAGE_SHA256_FILE       - file containing expected sha256
 */

import fs from 'fs';
import path from 'path';
import os from 'os';
import crypto from 'crypto';
import { execFileSync } from 'child_process';
import { fileURLToPath } from 'url';

// --------------- Config ---------------
function getArg(name) {
  const idx = process.argv.indexOf(name);
  return idx >= 0 && process.argv[idx + 1] ? process.argv[idx + 1] : null;
}

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
const PART_SIZE = 50;
const EXPECTED_NFTS = parsePositiveIntEnv('EXPECTED_NFTS', 175, 1, 100000);

const RECOVERY_PACKAGE_SHA256_FILE =
  process.env.RECOVERY_PACKAGE_SHA256_FILE ||
  'archive/evidence/nft-recovery-package/recovery-package.sha256';

// --------------- Resource limits ---------------
const MAX_CAR_BYTES = parsePositiveIntEnv('MAX_CAR_BYTES', 500 * 1024 * 1024, 1, 5 * 1024 * 1024 * 1024);
const MAX_TOTAL_BYTES = parsePositiveIntEnv('MAX_TOTAL_BYTES', 10 * 1024 * 1024 * 1024, 1, 100 * 1024 * 1024 * 1024);

// --------------- TMP_DIR: unique or cleaned ---------------
const TMP_DIR = process.env.NFT_CARS_TMP_DIR
  ? (() => {
      fs.rmSync(process.env.NFT_CARS_TMP_DIR, { recursive: true, force: true });
      fs.mkdirSync(process.env.NFT_CARS_TMP_DIR, { recursive: true });
      return process.env.NFT_CARS_TMP_DIR;
    })()
  : fs.mkdtempSync(path.join(os.tmpdir(), 'nft-cars-'));

// --------------- Constants ---------------
const SHA256_RE = /^[a-f0-9]{64}$/i;
const ARWEAVE_TXID_RE = /^[A-Za-z0-9_-]{43}$/;
const ETH_CONTRACT_RE = /^0x[a-fA-F0-9]{40}$/;
const CID_LIKE_RE = /^(bafy|bafk|bafz|Qm)[A-Za-z0-9]+$/;

// --------------- Helpers ---------------
function sha256hex(buf) {
  return crypto.createHash('sha256').update(buf).digest('hex');
}

function normalizeExpectedSize(value) {
  if (typeof value === 'number' && Number.isSafeInteger(value) && value >= 0) return value;
  if (typeof value === 'string' && /^[0-9]+$/.test(value)) {
    const n = Number(value);
    if (Number.isSafeInteger(n) && n >= 0) return n;
  }
  return null;
}

function validateExpectedInfo(txid, info) {
  if (!txid || typeof txid !== 'string') throw new Error(`Invalid txid: ${txid}`);
  if (!info || typeof info !== 'object') throw new Error(`Missing info for txid=${txid}`);
  if (!SHA256_RE.test(info.sha256 || '')) throw new Error(`Missing or invalid expected sha256 for txid=${txid}`);
  const expectedSize = normalizeExpectedSize(info.size);
  if (expectedSize === null) throw new Error(`Missing or invalid expected size for txid=${txid}`);
  return { expected_sha256: String(info.sha256).toLowerCase(), expected_size: expectedSize, expected_cid: info.cid || null };
}

function stableStringify(value) {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(stableStringify).join(',')}]`;
  return `{${Object.keys(value).sort().map(k => `${JSON.stringify(k)}:${stableStringify(value[k])}`).join(',')}}`;
}

// --------------- Strict CAR Parser (TA-REDTEAM-2026-007 SRC-CAR-001) ---------------
function readVarintStrict(data, offset, label = 'varint') {
  let value = 0;
  let shift = 0;
  let pos = offset;
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

function parseCarHeaderStrict(data) {
  const { value: headerLen, bytesRead } = readVarintStrict(data, 0, 'CAR header length');
  if (headerLen <= 0) throw new Error(`Invalid CAR header length: ${headerLen}`);
  const headerEnd = bytesRead + headerLen;
  if (headerEnd > data.length) throw new Error(`CAR header length exceeds buffer: headerEnd=${headerEnd} len=${data.length}`);
  return headerEnd;
}

function parseCarHeader(data) {
  return parseCarHeaderStrict(data);
}

function* iterCarBlocksStrict(data) {
  let pos = parseCarHeaderStrict(data);
  let idx = 0;
  while (pos < data.length) {
    const { value: blockLen, bytesRead } = readVarintStrict(data, pos, `CAR block ${idx} length`);
    pos += bytesRead;
    if (blockLen <= 0) throw new Error(`Invalid CAR block length at index=${idx}: ${blockLen}`);
    const blockEnd = pos + blockLen;
    if (blockEnd > data.length) throw new Error(`CAR block length exceeds buffer at index=${idx}: blockEnd=${blockEnd} len=${data.length}`);
    yield { data: data.slice(pos, blockEnd), index: idx, offset: pos, length: blockLen };
    pos = blockEnd;
    idx++;
  }
}

function iterCarBlocks(data) {
  return iterCarBlocksStrict(data);
}

// --------------- token_index Schema Validator (TA-REDTEAM-2026-007 SRC-SCHEMA-001) ---------------
function normalizeTokenId(tokenId) {
  const s = String(tokenId);
  if (!/^[0-9]+$/.test(s)) throw new Error(`Invalid token_id: ${tokenId}`);
  return s;
}

function validateCarRef(ref, pathLabel) {
  if (!ref || typeof ref !== 'object' || Array.isArray(ref)) throw new Error(`${pathLabel} must be object`);
  if (!ARWEAVE_TXID_RE.test(ref.txid || '')) throw new Error(`${pathLabel}.txid invalid: ${ref.txid}`);
  if (!ref.root_cid || typeof ref.root_cid !== 'string' || ref.root_cid.length < 10) throw new Error(`${pathLabel}.root_cid missing or invalid`);
  if (!SHA256_RE.test(ref.car_sha256 || '')) throw new Error(`${pathLabel}.car_sha256 invalid`);
  const size = normalizeExpectedSize(ref.car_size);
  if (size === null || size <= 0) throw new Error(`${pathLabel}.car_size invalid`);
  return { txid: ref.txid, root_cid: ref.root_cid, car_sha256: String(ref.car_sha256).toLowerCase(), car_size: size, leaf_path: ref.leaf_path || null };
}

function validateTokenIndex(index) {
  if (!index || typeof index !== 'object' || Array.isArray(index)) throw new Error('token_index must be object');
  const contracts = Object.keys(index);
  if (contracts.length === 0) throw new Error('token_index has no contracts');
  const normalized = {};
  for (const contract of contracts) {
    if (!ETH_CONTRACT_RE.test(contract)) throw new Error(`Invalid contract address: ${contract}`);
    const tokens = index[contract];
    if (!tokens || typeof tokens !== 'object' || Array.isArray(tokens)) throw new Error(`Contract ${contract} must map to token object`);
    normalized[contract] = {};
    for (const [tokenIdRaw, entry] of Object.entries(tokens)) {
      const token_id = normalizeTokenId(tokenIdRaw);
      if (!entry || typeof entry !== 'object' || Array.isArray(entry)) throw new Error(`${contract}/${token_id} entry must be object`);
      if (!entry.metadata) throw new Error(`${contract}/${token_id}.metadata missing`);
      const metadata = validateCarRef(entry.metadata, `${contract}/${token_id}.metadata`);
      const media = [];
      if (entry.media !== undefined) {
        if (!Array.isArray(entry.media)) throw new Error(`${contract}/${token_id}.media must be array`);
        for (let i = 0; i < entry.media.length; i++) {
          media.push(validateCarRef(entry.media[i], `${contract}/${token_id}.media[${i}]`));
        }
      }
      normalized[contract][token_id] = { metadata, media };
    }
  }
  return normalized;
}

function countTokenIndexNfts(index) {
  return Object.values(index).reduce((n, tokens) => n + Object.keys(tokens).length, 0);
}

function countMetadataEntries(index) {
  let count = 0;
  for (const tokens of Object.values(index)) {
    for (const entry of Object.values(tokens)) {
      if (entry.metadata) count++;
    }
  }
  return count;
}

// --------------- token_index Extraction (TA-REDTEAM-2026-007 SRC-TOKEN-001) ---------------
function looksLikeTokenIndexObject(obj) {
  if (!obj || typeof obj !== 'object' || Array.isArray(obj)) return false;
  const contractKeys = Object.keys(obj);
  if (contractKeys.length === 0) return false;
  return contractKeys.some(contract => {
    const tokens = obj[contract];
    if (!tokens || typeof tokens !== 'object' || Array.isArray(tokens)) return false;
    return Object.values(tokens).some(entry =>
      entry && typeof entry === 'object' && !Array.isArray(entry) && (entry.metadata || entry.media)
    );
  });
}

function extractJsonObjectsFromBlock(blockData, blockIndex) {
  const candidates = [];
  const errors = [];
  let searchPos = 0;
  while (searchPos < blockData.length) {
    const jsonStart = blockData.indexOf(0x7b, searchPos);
    if (jsonStart < 0) break;

    let depth = 0, inString = false, escaped = false, endPos = -1;
    for (let i = jsonStart; i < blockData.length; i++) {
      const ch = blockData[i];
      if (inString) {
        if (escaped) { escaped = false; }
        else if (ch === 0x5c) { escaped = true; }
        else if (ch === 0x22) { inString = false; }
        continue;
      }
      if (ch === 0x22) { inString = true; }
      else if (ch === 0x7b) { depth++; }
      else if (ch === 0x7d) { depth--; if (depth === 0) { endPos = i; break; } }
    }

    if (endPos > jsonStart) {
      const raw = blockData.slice(jsonStart, endPos + 1).toString('utf8');
      try {
        const obj = JSON.parse(raw);
        candidates.push({ obj, blockIndex, jsonStart, jsonEnd: endPos, raw });
      } catch (e) {
        errors.push(`Malformed JSON candidate at block=${blockIndex} offset=${jsonStart}: ${e.message}`);
      }
      searchPos = endPos + 1;
    } else {
      errors.push(`Unclosed JSON candidate at block=${blockIndex} offset=${jsonStart}`);
      break;
    }
  }
  return { candidates, errors };
}

function extractTokenIndex(carPath) {
  const raw = fs.readFileSync(carPath);
  const candidates = [];
  const allErrors = [];

  for (const block of iterCarBlocksStrict(raw)) {
    const result = extractJsonObjectsFromBlock(block.data, block.index);
    allErrors.push(...result.errors);
    for (const c of result.candidates) {
      if (looksLikeTokenIndexObject(c.obj)) candidates.push(c);
    }
  }

  if (allErrors.length > 0) {
    throw new Error(`Malformed JSON while scanning token_index candidates: ${allErrors.join('; ')}`);
  }
  if (candidates.length === 0) throw new Error('token_index.json not found in recovery CAR');
  if (candidates.length > 1) {
    const locations = candidates.map(c => `block=${c.blockIndex} offset=${c.jsonStart}`).join(', ');
    throw new Error(`Ambiguous token_index candidates: found ${candidates.length} candidates (${locations})`);
  }

  const normalized = validateTokenIndex(candidates[0].obj);
  return normalized;
}

// --------------- Duplicate txid Handling (TA-REDTEAM-2026-007 SRC-DUPTXID-001) ---------------
function sameExpectedCar(a, b) {
  return (
    String(a.sha256 || '').toLowerCase() === String(b.sha256 || '').toLowerCase() &&
    normalizeExpectedSize(a.size) === normalizeExpectedSize(b.size) &&
    String(a.cid || '') === String(b.cid || '')
  );
}

function addTxidRef(txids, txid, ref) {
  validateExpectedInfo(txid, ref);
  const normalizedRef = {
    role: ref.role,
    contract: ref.contract,
    token_id: String(ref.token_id),
    cid: ref.cid || null,
    leaf: ref.leaf || null,
    sha256: String(ref.sha256).toLowerCase(),
    size: normalizeExpectedSize(ref.size),
  };

  const existing = txids.get(txid);
  if (!existing) {
    txids.set(txid, {
      txid,
      role: normalizedRef.role,
      contract: normalizedRef.contract,
      token_id: normalizedRef.token_id,
      cid: normalizedRef.cid,
      leaf: normalizedRef.leaf,
      sha256: normalizedRef.sha256,
      size: normalizedRef.size,
      all_references: [normalizedRef],
    });
    return;
  }

  if (!sameExpectedCar(existing, normalizedRef)) {
    throw new Error(
      `Conflicting duplicate txid=${txid}: existing sha256=${existing.sha256} size=${existing.size} cid=${existing.cid}; ` +
      `new sha256=${normalizedRef.sha256} size=${normalizedRef.size} cid=${normalizedRef.cid}`
    );
  }
  existing.all_references.push(normalizedRef);
}

function collectTxids(index) {
  const txids = new Map();
  for (const [contract, tokens] of Object.entries(index)) {
    for (const [token_id, entry] of Object.entries(tokens)) {
      const meta = entry.metadata;
      addTxidRef(txids, meta.txid, {
        role: 'metadata', contract, token_id,
        cid: meta.root_cid, sha256: meta.car_sha256, size: meta.car_size,
      });
      for (const m of entry.media || []) {
        addTxidRef(txids, m.txid, {
          role: 'media', contract, token_id,
          cid: m.root_cid, leaf: m.leaf_path, sha256: m.car_sha256, size: m.car_size,
        });
      }
    }
  }
  return txids;
}

// --------------- Recovery Package Source Binding (TA-REDTEAM-2026-007 SRC-BIND-001) ---------------
function readExpectedRecoveryPackageSha256() {
  const cli = process.env.EXPECTED_RECOVERY_PACKAGE_SHA256 || getArg('--expected-recovery-package-sha256');
  if (cli) return cli;
  if (fs.existsSync(RECOVERY_PACKAGE_SHA256_FILE)) {
    const text = fs.readFileSync(RECOVERY_PACKAGE_SHA256_FILE, 'utf8').trim();
    const match = text.match(/[a-fA-F0-9]{64}/);
    if (match) return match[0];
  }
  return null;
}

function verifyRecoveryPackageSource(carPath) {
  const buf = fs.readFileSync(carPath);
  const actual = sha256hex(buf);
  const expectedHash = readExpectedRecoveryPackageSha256();

  if (expectedHash) {
    if (!SHA256_RE.test(expectedHash)) throw new Error(`Invalid expected recovery package sha256: ${expectedHash}`);
    if (actual.toLowerCase() !== expectedHash.toLowerCase()) {
      throw new Error(`Recovery package sha256 mismatch: expected=${expectedHash} actual=${actual}`);
    }
    console.log(`   ✅ Recovery package digest matches expected`);
  } else if (!DRY_RUN) {
    throw new Error(
      'EXPECTED_RECOVERY_PACKAGE_SHA256 (env) or recovery-package.sha256 (file) required unless DRY_RUN=1; ' +
      'refusing to use unauthenticated recovery package'
    );
  }

  return { sha256: actual, size: buf.length, expected_sha256: expectedHash || actual };
}

// --------------- Downloaded CAR Verification ---------------
function verifyDownloadedCarBuffer(txid, info, buf, source = 'download') {
  const expected = validateExpectedInfo(txid, info);
  const actualSha256 = sha256hex(buf);
  const actualSize = buf.length;

  if (actualSize > MAX_CAR_BYTES) throw new Error(`CAR too large for txid=${txid}: ${actualSize} > ${MAX_CAR_BYTES}`);
  if (expected.expected_size > MAX_CAR_BYTES) throw new Error(`Expected size exceeds per-file cap for txid=${txid}: ${expected.expected_size}`);
  if (actualSha256 !== expected.expected_sha256) throw new Error(`SHA256 mismatch for txid=${txid} source=${source}: expected=${expected.expected_sha256} actual=${actualSha256}`);
  if (actualSize !== expected.expected_size) throw new Error(`Size mismatch for txid=${txid} source=${source}: expected=${expected.expected_size} actual=${actualSize}`);

  return {
    txid, role: info.role, contract: info.contract, token_id: info.token_id,
    cid: expected.expected_cid, leaf: info.leaf || null,
    expected_sha256: expected.expected_sha256, actual_sha256: actualSha256, sha256_match: true,
    expected_size: expected.expected_size, actual_size: actualSize, size_match: true,
    verified: true, cached: source === 'cache',
    all_references: info.all_references || [{ role: info.role, contract: info.contract, token_id: info.token_id, cid: expected.expected_cid, leaf: info.leaf || null }],
    reference_count: (info.all_references || [{ role: info.role }]).length,
  };
}

// --------------- Download ---------------
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
    headers: { Authorization: `Bearer ${GITHUB_TOKEN}`, Accept: 'application/vnd.github+json', 'Content-Type': 'application/json' },
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
    headers: { Authorization: `Bearer ${GITHUB_TOKEN}`, 'Content-Type': 'application/gzip', 'Content-Length': buf.length.toString() },
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
  console.log(`   EXPECTED_NFTS: ${EXPECTED_NFTS}`);
  console.log(`   TMP_DIR: ${TMP_DIR}`);
  console.log(`   MAX_CAR_BYTES: ${(MAX_CAR_BYTES / 1024 / 1024).toFixed(0)}MB`);
  console.log(`   MAX_TOTAL_BYTES: ${(MAX_TOTAL_BYTES / 1024 / 1024 / 1024).toFixed(1)}GB`);
  console.log();

  // 0. Verify recovery package source (SRC-BIND-001)
  console.log('🔐 Verifying recovery package source...');
  const recoverySource = verifyRecoveryPackageSource(CAR_FILE);
  console.log(`   SHA-256: ${recoverySource.sha256}`);
  console.log(`   Size: ${recoverySource.size} bytes`);

  // Also cross-check hash-manifest.json if available
  const hashManifestPath = 'archive/hash-manifest.json';
  if (fs.existsSync(hashManifestPath)) {
    try {
      const hm = JSON.parse(fs.readFileSync(hashManifestPath, 'utf8'));
      const hmEntry = (hm.files || hm.arweave_assets || []).find(e => (e.path || '').includes('recovery-package.bin'));
      if (hmEntry && hmEntry.sha256) {
        if (hmEntry.sha256.toLowerCase() !== recoverySource.sha256.toLowerCase()) {
          throw new Error(`Recovery package digest mismatch vs hash-manifest.json! Expected ${hmEntry.sha256}, got ${recoverySource.sha256}`);
        }
        console.log(`   ✅ Also matches hash-manifest.json`);
      }
    } catch (err) {
      if (err.message.includes('mismatch')) throw err;
      console.warn(`   ⚠️  hash-manifest.json check skipped: ${err.message}`);
    }
  }

  // 1. Extract token index (SRC-TOKEN-001 + SRC-SCHEMA-001)
  console.log('\n📖 Extracting and validating token_index.json...');
  const index = extractTokenIndex(CAR_FILE);
  const contracts = Object.keys(index);
  const totalTokens = countTokenIndexNfts(index);
  const metadataCount = countMetadataEntries(index);
  console.log(`   ${totalTokens} NFTs, ${contracts.length} contracts, ${metadataCount} metadata entries`);

  // 2. Expected count gate (SRC-COUNT-001)
  if (totalTokens !== EXPECTED_NFTS) {
    throw new Error(`token_index NFT count mismatch: expected=${EXPECTED_NFTS} actual=${totalTokens}`);
  }
  if (metadataCount !== EXPECTED_NFTS) {
    throw new Error(`metadata count mismatch: expected=${EXPECTED_NFTS} actual=${metadataCount}`);
  }
  console.log(`   ✅ NFT count matches ${EXPECTED_NFTS}`);

  // 3. Canonical token_index digest (SRC-TRACE-001)
  const tokenIndexCanonical = stableStringify(index);
  const tokenIndexSha256 = sha256hex(Buffer.from(tokenIndexCanonical, 'utf8'));
  console.log(`   Token index canonical SHA-256: ${tokenIndexSha256}`);

  // 4. Collect txids (SRC-DUPTXID-001)
  const txids = collectTxids(index);
  const logicalFileReferences = [...txids.values()].reduce((sum, t) => sum + t.all_references.length, 0);
  console.log(`   ${txids.size} unique txids, ${logicalFileReferences} logical file references`);
  console.log();

  if (DRY_RUN) {
    console.log('🔍 DRY RUN — listing txids:');
    for (const [txid, info] of txids) {
      const refs = info.all_references.length > 1 ? ` (${info.all_references.length} refs)` : '';
      console.log(`   ${txid}  ${info.role}  ${info.contract.slice(0, 10)}.../${info.token_id.slice(0, 20)}...${refs}`);
    }
    console.log(`\nTotal: ${txids.size} unique files, ${logicalFileReferences} references`);
    return;
  }

  // 5. Download all CARs
  fs.mkdirSync(TMP_DIR, { recursive: true });
  const manifest = [];
  const verifiedCarFiles = [];
  const txidList = [...txids.entries()];
  let done = 0, pass = 0, fail = 0;
  let totalVerifiedBytes = 0;

  const tasks = txidList.map(([txid, info]) => async () => {
    const dest = path.join(TMP_DIR, `${txid}.car`);
    if (fs.existsSync(dest) && fs.statSync(dest).size > 0) {
      try {
        const cachedBuf = fs.readFileSync(dest);
        const verified = verifyDownloadedCarBuffer(txid, info, cachedBuf, 'cache');
        totalVerifiedBytes += verified.actual_size;
        if (totalVerifiedBytes > MAX_TOTAL_BYTES) throw new Error(`Total CAR verified size exceeds cap: ${totalVerifiedBytes} > ${MAX_TOTAL_BYTES}`);
        manifest.push(verified);
        verifiedCarFiles.push({ txid, path: dest, manifest_item: verified });
        done++; pass++;
        if (done % 50 === 0) process.stdout.write(`\r   ${done}/${txids.size}`);
        return;
      } catch (err) { fs.rmSync(dest, { force: true }); }
    }
    try {
      const buf = await downloadTxid(txid);
      const verified = verifyDownloadedCarBuffer(txid, info, buf, 'download');
      totalVerifiedBytes += verified.actual_size;
      if (totalVerifiedBytes > MAX_TOTAL_BYTES) throw new Error(`Total CAR verified size exceeds cap: ${totalVerifiedBytes} > ${MAX_TOTAL_BYTES}`);
      fs.writeFileSync(dest, buf);
      manifest.push(verified);
      verifiedCarFiles.push({ txid, path: dest, manifest_item: verified });
      done++; pass++;
      if (done % 10 === 0) process.stdout.write(`\r   ${done}/${txids.size} downloaded`);
    } catch (err) {
      done++; fail++;
      manifest.push({ txid, role: info.role, contract: info.contract, token_id: info.token_id, expected_sha256: info.sha256 || null, expected_size: info.size ?? null, error: err.message, verified: false });
    }
  });

  await pool(tasks, CONCURRENCY);
  console.log(`\n   ✅ ${pass} downloaded, ❌ ${fail} failed`);

  if (fail > 0) throw new Error(`${fail} CAR downloads failed; refusing to package or upload incomplete backup`);

  // 6. Aggregate manifest checks
  const sha256Pass = manifest.filter(x => x.sha256_match === true).length;
  const sizePass = manifest.filter(x => x.size_match === true).length;
  const allVerified = fail === 0 && pass === txids.size && sha256Pass === txids.size && sizePass === txids.size;
  if (!allVerified) throw new Error(`Not all files verified: sha256_pass=${sha256Pass}/${txids.size} size_pass=${sizePass}/${txids.size}`);

  // 7. Write manifest
  const manifestPath = path.join(TMP_DIR, 'manifest.json');
  fs.writeFileSync(manifestPath, JSON.stringify({
    timestamp: new Date().toISOString(),
    expected_nfts: EXPECTED_NFTS, actual_nfts: totalTokens, nft_count_match: totalTokens === EXPECTED_NFTS,
    total_txids: txids.size, logical_file_references: logicalFileReferences,
    downloaded: pass, failed: fail, verified: pass,
    sha256_check: { pass: sha256Pass, total: txids.size },
    size_check: { pass: sizePass, total: txids.size },
    all_expected_sha256_matched: sha256Pass === txids.size,
    all_expected_size_matched: sizePass === txids.size,
    all_verified: allVerified,
    contracts: contracts.length, nfts: totalTokens, files: manifest,
  }, null, 2));

  // 8. Package into tar.gz parts
  console.log('\n📦 Packaging into archives...');
  if (verifiedCarFiles.length !== txids.size) throw new Error(`Verified CAR count mismatch: expected=${txids.size} actual=${verifiedCarFiles.length}`);

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
    parts.push({ name: partName, path: partPath, count: batch.length, files: batch.map(x => ({ txid: x.txid, tar_path: path.basename(x.path), manifest_item: x.manifest_item })) });
  }

  const manifestTar = path.join(TMP_DIR, 'nft-cars-manifest.tar.gz');
  execFileSync('tar', ['czf', manifestTar, '-C', TMP_DIR, 'manifest.json'], { stdio: 'pipe' });
  parts.push({ name: 'nft-cars-manifest.tar.gz', path: manifestTar, count: 1 });
  console.log(`   ${parts.length} archives created`);

  // 9. Build RELEASE-MANIFEST.json (SRC-TRACE-001 + SRC-H1)
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
        root_cid_verified: false,
        cid_check_required: false,
        all_references: f.manifest_item.all_references || [],
        reference_count: f.manifest_item.reference_count || 1,
      })),
    }));

  const totalCarFiles = releaseAssets.reduce((sum, a) => sum + a.files.length, 0);

  const releaseManifest = {
    schema: 'trinity-release-manifest-v1',
    release_kind: 'nft-car-backup-parts',
    verification_basis: 'expected_sha256_and_expected_size',
    actual_nfts: totalTokens,
    expected_nfts: EXPECTED_NFTS,
    nft_count_match: totalTokens === EXPECTED_NFTS,
    total_car_files: totalCarFiles,
    logical_file_references: logicalFileReferences,
    contracts: contracts.length,
    source_recovery_package: {
      path: CAR_FILE,
      sha256: recoverySource.sha256,
      size: recoverySource.size,
      expected_sha256: recoverySource.expected_sha256,
      sha256_match: true,
    },
    source_token_index: {
      sha256: tokenIndexSha256,
      canonicalization: 'stable-json-v1',
      contracts: contracts.length,
      nfts: totalTokens,
    },
    source_expectations: {
      expected_nfts: EXPECTED_NFTS,
      actual_nfts: totalTokens,
      nft_count_match: totalTokens === EXPECTED_NFTS,
    },
    source_binding: {
      recovery_package_sha256_enforced: true,
      digest_manifest_crosscheck_performed: fs.existsSync(hashManifestPath),
      authority_manifest_crosscheck_performed: false,
    },
    cid_policy: {
      producer_verifies_root_cid: false,
      root_cid_recorded_as_expected_metadata: true,
      verifier_command: 'node scripts/verify-release-assets.mjs --cid-check',
    },
    source_manifest: { generator: 'scripts/download-nft-cars.mjs' },
    release_assets: releaseAssets,
    auxiliary_assets: ['nft-cars-manifest.tar.gz', 'RELEASE-MANIFEST.json'],
    does_not_prove: [
      'independent attestation',
      'on-chain ownership or tokenURI correctness',
      'physical authorship or provenance',
      'CID/root/DAG correctness — root_cid is metadata from token_index, NOT verified by this producer; run verify-release-assets.mjs --cid-check to verify',
      'full evidence chain verification',
    ],
  };

  const releaseManifestPath = path.join(TMP_DIR, 'RELEASE-MANIFEST.json');
  fs.writeFileSync(releaseManifestPath, JSON.stringify(releaseManifest, null, 2));
  console.log(`   ✅ RELEASE-MANIFEST.json written (${releaseAssets.length} parts, ${totalCarFiles} CARs, ${logicalFileReferences} refs)`);

  // 10. Upload to GitHub Release
  console.log('\n📤 Uploading to GitHub Release...');
  const release = await ensureRelease();
  let uploadFail = 0;

  try { await uploadAsset(release.id, releaseManifestPath, 'RELEASE-MANIFEST.json'); }
  catch (err) { uploadFail++; console.error(`   ❌ Failed to upload RELEASE-MANIFEST.json: ${err.message}`); }

  for (const part of parts) {
    try { await uploadAsset(release.id, part.path, part.name); }
    catch (err) { uploadFail++; console.error(`   ❌ Failed to upload ${part.name}: ${err.message}`); }
  }

  if (uploadFail > 0) throw new Error(`${uploadFail} release asset uploads failed`);

  console.log('\n=========================================');
  console.log(`  ✅ Done! ${pass} CARs backed up to release ${RELEASE_TAG}`);
  console.log(`  📦 ${parts.length} archives uploaded`);
  console.log(`  📋 RELEASE-MANIFEST.json uploaded`);
  console.log('=========================================');
}

const isMain = process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1]);

if (isMain) {
  main().catch(err => { console.error('Fatal:', err); process.exit(1); });
}

export {
  normalizeExpectedSize,
  validateExpectedInfo,
  verifyDownloadedCarBuffer,
  sha256hex,
  readVarintStrict,
  parseCarHeaderStrict,
  iterCarBlocksStrict,
  extractTokenIndex,
  looksLikeTokenIndexObject,
  validateTokenIndex,
  validateCarRef,
  normalizeTokenId,
  countTokenIndexNfts,
  countMetadataEntries,
  collectTxids,
  addTxidRef,
  sameExpectedCar,
  stableStringify,
  readExpectedRecoveryPackageSha256,
  verifyRecoveryPackageSource,
};
