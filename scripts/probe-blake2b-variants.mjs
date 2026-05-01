#!/usr/bin/env node
/**
 * probe-blake2b-variants.mjs
 *
 * Probes all plausible blake2b generation variants against digest-manifest
 * to discover the historical generation口径 for blake2b_256.
 *
 * The manifest stores blake2b_256 as 128-hex-char strings (512-bit output),
 * despite the field name suggesting 256-bit. This script tests 8 variants
 * to find which one matches.
 *
 * Usage:
 *   node scripts/probe-blake2b-variants.mjs [--release-tag TAG] [--concurrency N]
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { blake2b, blake2s } from '@noble/hashes/blake2.js';
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
const DIGEST_MANIFEST_JSON = 'archive/evidence/digest-manifest.json';
const DIGEST_MANIFEST_CSV = 'archive/evidence/digest-manifest.csv';
const EXPECTED_NFTS = 175;
const TMP_DIR = '/tmp/blake2b-probe';

// ═══════════════════════════════════════════════════════════════════════════
// HELPERS
// ═══════════════════════════════════════════════════════════════════════════

function sha256hex(buf) { return crypto.createHash('sha256').update(buf).digest('hex'); }
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
function log(msg) { console.log(msg); }
function err(msg) { console.error(msg); }

function normalizeKey(k) {
  return String(k || '').trim().toLowerCase().replace(/[-\s]/g, '_');
}

function normPath(p) {
  return String(p || '').replace(/\\/g, '/').replace(/^\.?\//, '').replace(/\/+/g, '/').trim();
}

function normalizeHashValue(v) {
  return String(v || '').trim().toLowerCase().replace(/^0x/, '');
}

function isNonEmptyHash(v) {
  return typeof v === 'string' && v.trim().length > 0;
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
// MANIFEST NORMALIZATION (from verify-dag-digest.mjs)
// ═══════════════════════════════════════════════════════════════════════════

const PATH_ALIASES = ['path', 'file', 'filename', 'relative_path', 'name'];
const SIZE_ALIASES = ['size', 'size_bytes', 'bytes', 'length'];
const SHA256_ALIASES = ['sha256', 'sha_256', 'digest_sha256'];
const BLAKE2B_ALIASES = ['blake2b_256', 'blake2b-256'];

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
    blake2b_256: String(resolveField(raw, BLAKE2B_ALIASES) || '').toLowerCase(),
    _raw: raw,
  };
}

function normalizeDigestManifest(digestManifest) {
  const items = digestManifest.items || digestManifest;
  if (!Array.isArray(items)) return [];
  return items.map(normalizeManifestItem);
}

// ═══════════════════════════════════════════════════════════════════════════
// BLAKE2B VARIANT COMPUTATION
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Compute all 8 blake2b variants for a buffer.
 * Returns hex strings for comparison.
 */
function computeBlake2bVariants(buf) {
  const u8 = buf instanceof Uint8Array ? buf : new Uint8Array(buf.buffer, buf.byteOffset, buf.byteLength);
  const sha256Hex = sha256hex(buf);

  // 1. blake2b with dkLen=32 (canonical 256-bit)
  const v1 = bytesToHex(blake2b(u8, { dkLen: 32 }));

  // 2. blake2b with dkLen=64, take first 32 bytes
  const v2full = blake2b(u8, { dkLen: 64 });
  const v2 = bytesToHex(v2full.slice(0, 32));

  // 3. blake2b with dkLen=64, take last 32 bytes
  const v3 = bytesToHex(v2full.slice(32, 64));

  // 4. Node crypto blake2b512, take first 32 bytes
  const v4full = crypto.createHash('blake2b512').update(buf).digest();
  const v4 = v4full.slice(0, 32).toString('hex');

  // 5. Node crypto blake2b512, full 64 bytes
  const v5 = v4full.toString('hex');

  // 6. blake2b of sha256 hex string (UTF-8 bytes of the hex text)
  const v6 = bytesToHex(blake2b(Buffer.from(sha256Hex, 'utf8'), { dkLen: 32 }));

  // 7. blake2b of sha256 raw bytes (32 bytes)
  const v7 = bytesToHex(blake2b(Buffer.from(sha256Hex, 'hex'), { dkLen: 32 }));

  // 8. blake2s_256 (if supported)
  let v8 = null;
  try {
    v8 = bytesToHex(blake2s(u8, { dkLen: 32 }));
  } catch { /* not available */ }

  return {
    blake2b_256_dklen32: v1,
    blake2b_512_first32: v2,
    blake2b_512_last32: v3,
    node_blake2b512_first32: v4,
    node_blake2b512_full: v5,
    blake2b_256_of_sha256_hex_utf8: v6,
    blake2b_256_of_sha256_raw: v7,
    blake2s_256: v8,
  };
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
    attempts = 5,
    baseDelayMs = 1000,
    maxDelayMs = 15000,
    headers = {}
  } = options;

  let lastError = null;
  for (let i = 1; i <= attempts; i++) {
    try {
      const res = await fetch(url, { headers });
      if (res.ok) return Buffer.from(await res.arrayBuffer());
      const body = await res.text().catch(() => '');
      lastError = new Error(`${label}: HTTP ${res.status} ${res.statusText} ${body.slice(0, 300)}`);
      const retryable = res.status === 408 || res.status === 429 || res.status >= 500;
      if (!retryable || i === attempts) throw lastError;
    } catch (e) {
      lastError = e;
      if (!isRetryableFetchError(e) || i === attempts) throw e;
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
    { label: `asset-${assetId}`, headers: ghHeaders({ Accept: 'application/octet-stream' }) }
  );
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
// BUILD SHA256 INDEX FROM MANIFEST
// ═══════════════════════════════════════════════════════════════════════════

function buildManifestIndexes(items) {
  const bySha256 = new Map();
  const byPath = new Map();
  for (const item of items) {
    if (item.sha256) bySha256.set(item.sha256.toLowerCase(), item);
    const np = normPath(item.path);
    if (np) byPath.set(np, item);
  }
  return { bySha256, byPath };
}

function findManifestEntry(fileSha256, filePath, indexes) {
  if (fileSha256 && indexes.bySha256.has(fileSha256.toLowerCase())) {
    return indexes.bySha256.get(fileSha256.toLowerCase());
  }
  const np = normPath(filePath);
  if (np && indexes.byPath.has(np)) {
    return indexes.byPath.get(np);
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
  log('  BLAKE2B Variant Probe — find historical generation口径');
  log('═══════════════════════════════════════════════════════════\n');

  // ── Load manifest ─────────────────────────────────────────────────
  const rawDigestManifest = readRepoJson(DIGEST_MANIFEST_JSON);
  const manifestItems = normalizeDigestManifest(rawDigestManifest);
  const indexes = buildManifestIndexes(manifestItems);
  log(`  digest-manifest: ${manifestItems.length} items`);

  // Filter to items with non-empty blake2b_256
  const itemsWithBlake2b = manifestItems.filter(item => isNonEmptyHash(item.blake2b_256));
  log(`  items with blake2b_256 declared: ${itemsWithBlake2b.length}`);

  // ── Load token index & fetch release ──────────────────────────────
  const tokenIndex = readRepoJson(TOKEN_INDEX_FILE);
  if (!tokenIndex) { err('❌ token_index.json not found'); process.exit(1); }
  let totalNfts = 0;
  for (const c of Object.keys(tokenIndex)) totalNfts += Object.keys(tokenIndex[c]).length;
  log(`  token_index: ${totalNfts} NFTs`);

  log(`\n📦 Fetching release ${RELEASE_TAG}...`);
  const release = await getReleaseByTag(RELEASE_TAG);
  const allAssets = await getAllAssets(release.id);
  const nftAssets = allAssets.filter(a => a.name.startsWith('nft-') && a.name.endsWith('.tar'));
  log(`  ${allAssets.length} total assets, ${nftAssets.length} NFT tars`);

  // ── Variant match counters ────────────────────────────────────────
  const VARIANT_NAMES = [
    'blake2b_256_dklen32',
    'blake2b_512_first32',
    'blake2b_512_last32',
    'node_blake2b512_first32',
    'node_blake2b512_full',
    'blake2b_256_of_sha256_hex_utf8',
    'blake2b_256_of_sha256_raw',
    'blake2s_256',
  ];

  const matchCounts = {};
  for (const v of VARIANT_NAMES) matchCounts[v] = 0;

  let filesChecked = 0;
  let manifestBlake2bRecords = 0;
  const mismatchSamples = []; // first few files for debugging

  // ── Process NFT tars ──────────────────────────────────────────────
  const tasks = nftAssets.map(asset => async () => {
    let tarBuf;
    try {
      tarBuf = await downloadAsset(asset.id);
    } catch (e) {
      err(`  ⚠ Download failed: ${asset.name} — ${e.message}`);
      return;
    }

    const tarFiles = extractFilesFromTar(tarBuf);

    for (const tarFile of tarFiles) {
      if (!tarFile.name.endsWith('.car')) continue;

      const carData = tarFile.data;
      const carSha = sha256hex(carData);

      const matchedItem = findManifestEntry(carSha, tarFile.name, indexes);
      if (!matchedItem) continue;
      if (!isNonEmptyHash(matchedItem.blake2b_256)) continue;

      manifestBlake2bRecords++;
      filesChecked++;

      const expected = normalizeHashValue(matchedItem.blake2b_256);
      const variants = computeBlake2bVariants(carData);

      for (const vname of VARIANT_NAMES) {
        const computed = variants[vname];
        if (computed && normalizeHashValue(computed) === expected) {
          matchCounts[vname]++;
        }
      }

      // Collect a mismatch sample for debugging (first 3)
      if (mismatchSamples.length < 3) {
        const sample = { file: tarFile.name, expected_blake2b_256: expected.slice(0, 32) + '...' };
        for (const vname of VARIANT_NAMES) {
          const computed = variants[vname];
          sample[vname] = computed ? (normalizeHashValue(computed) === expected ? 'MATCH' : computed.slice(0, 16) + '...') : 'N/A';
        }
        mismatchSamples.push(sample);
      }
    }
  });

  const results = await runConcurrent(tasks, CONCURRENCY);
  for (const r of results) {
    if (r instanceof Error) err(`  ❌ Task error: ${r.message}`);
  }

  // ── Determine winning variant ─────────────────────────────────────
  let winningVariant = null;
  let allFilesMatched = false;

  for (const vname of VARIANT_NAMES) {
    if (matchCounts[vname] === filesChecked && filesChecked > 0) {
      winningVariant = vname;
      allFilesMatched = true;
      break;
    }
  }

  // ── Build output ──────────────────────────────────────────────────
  const variantsOutput = {};
  for (const vname of VARIANT_NAMES) {
    variantsOutput[vname] = { match: matchCounts[vname] };
  }

  const output = {
    schema: 'trinity-accord.blake2b-variant-probe.v1',
    generated_at: new Date().toISOString(),
    files_checked: filesChecked,
    manifest_blake2b_records: manifestBlake2bRecords,
    variants: variantsOutput,
    winning_variant: winningVariant,
    all_files_matched_by_variant: allFilesMatched,
    mismatch_samples: mismatchSamples,
  };

  const outPath = path.join(process.cwd(), 'BLAKE2B-VARIANT-PROBE.json');
  fs.writeFileSync(outPath, JSON.stringify(output, null, 2));
  log(`\n📝 ${outPath} written`);

  // ── Report ────────────────────────────────────────────────────────
  log('\n═══════════════════════════════════════════════════════════');
  log('  RESULTS');
  log('═══════════════════════════════════════════════════════════');
  log(`  Files checked           : ${filesChecked}`);
  log(`  Manifest blake2b records: ${manifestBlake2bRecords}`);
  log('');
  for (const vname of VARIANT_NAMES) {
    const pct = filesChecked > 0 ? ((matchCounts[vname] / filesChecked) * 100).toFixed(1) : '0.0';
    const marker = matchCounts[vname] === filesChecked && filesChecked > 0 ? ' ← WINNER' : '';
    log(`  ${vname.padEnd(35)} : ${matchCounts[vname]}/${filesChecked} (${pct}%)${marker}`);
  }
  log('');
  if (winningVariant) {
    log(`  ✅ WINNING VARIANT: ${winningVariant}`);
    log(`  All ${filesChecked} files matched.`);
  } else {
    log(`  ❌ No single variant matched all ${filesChecked} files.`);
    log(`  Check mismatch_samples in output for debugging.`);
  }
  log('');

  // ── Exit code ─────────────────────────────────────────────────────
  if (!winningVariant) process.exit(1);
}

main().catch(e => { err(`\n❌ Fatal: ${e.message}\n${e.stack}`); process.exit(1); });
