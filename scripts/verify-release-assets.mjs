#!/usr/bin/env node
/**
 * verify-release-assets.mjs  (v3 — strict, manifest-driven, fail-closed)
 *
 * Downloads ALL NFT .tar assets from a GitHub Release and re-verifies:
 *   1. Release manifest schema recognized
 *   2. ALL manifest-declared NFT assets present (complete set proof)
 *   3. No extra/duplicate release assets
 *   4. TAR entries strict: no duplicates, no path traversal, no truncation
 *   5. SHA-256 of every CAR inside the tar == expected_sha256
 *   6. Size of every CAR == expected_size
 *   7. Root CID (metadata=strict, media=audit) — ONLY when --cid-check is passed
 *   8. Report includes verification_scope, does_not_prove, limitations
 *
 * Usage:
 *   GITHUB_TOKEN=xxx node scripts/verify-release-assets.mjs \
 *     [--release-tag nft-arweave-mirror-175-v1] \
 *     [--cid-check] \
 *     [--concurrency 8]
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { fileURLToPath } from 'url';
import { collectToolchainProvenance } from './toolchain_provenance.mjs';

// ─── Config ────────────────────────────────────────────────────────────────

function parseBoundedInt(value, label, min, max) {
  const n = Number(value);
  if (!Number.isInteger(n) || n < min || n > max) {
    throw new Error(`Invalid ${label}: ${value}. Must be integer ${min}-${max}.`);
  }
  return n;
}

function parseBoundedIntEnv(name, fallback, min, max) {
  const raw = process.env[name] || String(fallback);
  return parseBoundedInt(raw, name, min, max);
}

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO = process.env.REPO || 'thechurchofagi/trinity-accord';
const MAX_RETRIES = 3;
const VERIFY_CONCURRENCY = parseBoundedIntEnv('VERIFY_CONCURRENCY', 8, 1, 25);

// ─── Resource limits ──────────────────────────────────────────────────────

const MAX_RELEASE_ASSET_BYTES = parseBoundedIntEnv(
  'MAX_RELEASE_ASSET_BYTES', 1024 * 1024 * 1024, 1, 10 * 1024 * 1024 * 1024
);
const MAX_TOTAL_RELEASE_BYTES = parseBoundedIntEnv(
  'MAX_TOTAL_RELEASE_BYTES', 20 * 1024 * 1024 * 1024, 1, 200 * 1024 * 1024 * 1024
);
let totalDownloadedBytes = 0;

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

// ─── Manifest schema normalization ─────────────────────────────────────────

function normalizeTarPath(name) {
  return name.replace(/^\.\//, '');
}

function normalizeReleaseManifest(manifest) {
  if (!manifest || typeof manifest !== 'object') {
    throw new Error('Release manifest must be a JSON object');
  }

  // v1 explicit schema
  if (manifest.schema === 'trinity-release-manifest-v1') {
    return normalizeTrinityReleaseManifestV1(manifest);
  }

  // Legacy: has per_nft_assets array
  if (Array.isArray(manifest.per_nft_assets)) {
    return normalizeLegacyPerNftManifest(manifest);
  }

  throw new Error(`Unsupported release manifest schema: ${manifest.schema || 'missing'}`);
}

function normalizeTrinityReleaseManifestV1(m) {
  // Part-based manifest takes priority
  if (Array.isArray(m.release_assets)) {
    return normalizePartBasedManifestV1(m);
  }

  // Legacy per_nft_assets (only for backward compat)
  if (Array.isArray(m.per_nft_assets)) {
    return normalizePerNftManifestV1(m);
  }

  throw new Error('trinity-release-manifest-v1 requires release_assets array or per_nft_assets array');
}

function normalizePerNftManifestV1(m) {
  const expected = m.per_nft_assets.map(entry => {
    if (!entry.nft_asset_name) throw new Error('Missing nft_asset_name in manifest entry');
    return {
      name: entry.nft_asset_name,
      contract: entry.contract || null,
      token_id: entry.token_id || null,
      files: (entry.files || []).map(f => ({
        role: f.role,
        expected_path: f.expected_path || `nft/${f.role}.car`,
        expected_sha256: (f.expected_sha256 || '').toLowerCase(),
        expected_size: f.expected_size,
        expected_root_cid: f.expected_root_cid || null,
        cid_required: f.cid_check_required || false,
      })),
    };
  });

  return {
    schema: m.schema,
    verification_basis: m.verification_basis || 'expected_sha256_and_expected_size',
    expected_release_assets: expected,
    expected_asset_count: m.actual_nfts ?? expected.length,
    expected_nft_count: m.actual_nfts ?? expected.length,
    expected_car_count: m.total_car_files ?? expected.reduce((s, e) => s + e.files.length, 0),
    does_not_prove: m.does_not_prove || [],
  };
}

function normalizePartBasedManifestV1(m) {
  const expected = m.release_assets.map(asset => {
    if (!asset.asset_name) throw new Error('Missing asset_name in release_assets entry');
    if (!Array.isArray(asset.files)) throw new Error(`Missing files for ${asset.asset_name}`);
    return {
      name: asset.asset_name,
      contract: null,
      token_id: null,
      files: asset.files.map(f => ({
        role: f.role,
        contract: f.contract || null,
        token_id: f.token_id || null,
        txid: f.txid || null,
        expected_path: normalizeTarPath(f.expected_path || `${f.txid}.car`),
        expected_sha256: (f.expected_sha256 || '').toLowerCase(),
        expected_size: f.expected_size,
        expected_root_cid: f.expected_root_cid || null,
        cid_required: f.cid_check_required || false,
      })),
    };
  });

  return {
    schema: m.schema,
    verification_basis: m.verification_basis || 'expected_sha256_and_expected_size',
    expected_release_assets: expected,
    expected_asset_count: expected.length,
    expected_nft_count: m.actual_nfts ?? null,
    expected_car_count: m.total_car_files ?? expected.reduce((s, e) => s + e.files.length, 0),
    auxiliary_assets: m.auxiliary_assets || ['RELEASE-MANIFEST.json', 'nft-cars-manifest.tar.gz'],
    does_not_prove: m.does_not_prove || [],
  };
}

function normalizeLegacyPerNftManifest(m) {
  const expected = m.per_nft_assets.map(entry => {
    if (!entry.nft_asset_name) throw new Error('Missing nft_asset_name in legacy manifest');
    return {
      name: entry.nft_asset_name,
      contract: null,
      token_id: null,
      files: (entry.files || []).map(f => ({
        role: f.role,
        expected_path: `nft/${f.role}.car`,
        expected_sha256: (f.expected_sha256 || '').toLowerCase(),
        expected_size: f.expected_size,
        expected_root_cid: f.expected_root_cid || null,
        cid_required: false,
      })),
    };
  });

  return {
    schema: 'legacy-per-nft-assets',
    verification_basis: 'expected_sha256_and_expected_size',
    expected_nft_assets: expected,
    expected_nft_count: m.actual_nfts ?? expected.length,
    expected_car_count: m.total_car_files ?? expected.reduce((s, e) => s + e.files.length, 0),
    does_not_prove: [],
  };
}

// ─── Strict TAR extraction ─────────────────────────────────────────────────

function readTarString(header, start, len) {
  let end = start;
  while (end < start + len && header[end] !== 0) end++;
  return header.slice(start, end).toString('utf-8');
}

function parseTarOctal(header, start, len) {
  const s = readTarString(header, start, len).trim();
  if (!/^[0-7]*$/.test(s)) throw new Error(`Invalid TAR octal: "${s}"`);
  return s ? parseInt(s, 8) : 0;
}

function extractFilesFromTarStrict(buf) {
  const files = [];
  const seen = new Set();
  const errors = [];
  let pos = 0;

  while (pos + 512 <= buf.length) {
    const header = buf.slice(pos, pos + 512);
    if (header.every(b => b === 0)) break;

    const name = readTarString(header, 0, 100);
    const prefix = readTarString(header, 345, 155);
    const fullName = prefix ? `${prefix}/${name}` : name;
    const typeflag = String.fromCharCode(header[156] || 0) || '0';

    // Path safety
    if (!fullName || fullName.includes('\0')) {
      errors.push(`Invalid TAR name at offset ${pos}`);
      break;
    }
    if (fullName.startsWith('/') || fullName.includes('..')) {
      errors.push(`Unsafe TAR path: ${fullName}`);
      break;
    }

    // Duplicate detection
    if (seen.has(fullName)) {
      errors.push(`Duplicate TAR entry: ${fullName}`);
    }
    seen.add(fullName);

    // Only support regular files
    if (!['0', '\0'].includes(typeflag)) {
      errors.push(`Unsupported TAR entry type '${typeflag}' for ${fullName}`);
      break;
    }

    const size = parseTarOctal(header, 124, 12);
    pos += 512;

    if (!Number.isSafeInteger(size) || size < 0) {
      errors.push(`Invalid TAR size for ${fullName}`);
      break;
    }

    if (pos + size > buf.length) {
      errors.push(`Truncated TAR payload for ${fullName}: need ${size} bytes at offset ${pos}, only ${buf.length - pos} available`);
      break;
    }

    if (size > 0 && errors.length === 0) {
      files.push({ name: normalizeTarPath(fullName), data: buf.slice(pos, pos + size) });
    }

    pos += Math.ceil(size / 512) * 512;
  }

  if (errors.length > 0) {
    throw new Error(`Invalid TAR: ${errors.join('; ')}`);
  }

  return files;
}

// ─── CAR parsing (root CID extraction) ─────────────────────────────────────

function parseCarHeader(data) {
  let pos = 0, shift = 0, headerLen = 0;
  for (let i = 0; i < 10; i++) {
    if (pos >= data.length) throw new Error('Truncated CAR header varint');
    const b = data[pos]; headerLen += (b & 0x7f) * (2 ** shift); pos++; shift += 7;
    if (!Number.isSafeInteger(headerLen)) throw new Error('Unsafe CAR header varint');
    if (b < 0x80) break;
  }
  return pos + headerLen;
}

function cidBytesToCidV1(bytes) {
  while (bytes.length > 0 && bytes[0] === 0x00) bytes = bytes.slice(1);
  if (bytes.length === 0) throw new Error('Empty CID bytes');
  if (bytes[0] === 0x12 && bytes[1] === 0x20) {
    const cidV1Bytes = Buffer.concat([Buffer.from([0x01, 0x71]), bytes]);
    return base32EncodeCid(cidV1Bytes);
  }
  if (bytes[0] === 0x01) return base32EncodeCid(bytes);
  return 'b' + bytes.toString('hex');
}

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

function extractCarRootCid(carData) {
  const headerEnd = parseCarHeader(carData);
  const header = carData.slice(0, headerEnd);
  for (let i = 0; i < header.length - 2; i++) {
    if (header[i] === 0xd8 && header[i + 1] === 0x2a) {
      let cidStart = i + 2, cidLen = 0;
      if (header[cidStart] === 0x58) { cidLen = header[cidStart + 1]; cidStart += 2; }
      else if (header[cidStart] === 0x59) { cidLen = (header[cidStart + 1] << 8) | header[cidStart + 2]; cidStart += 3; }
      else { cidLen = header[cidStart] - 0x40; cidStart += 1; }
      return cidBytesToCidV1(header.slice(cidStart, cidStart + cidLen));
    }
  }
  throw new Error('No CBOR tag(42) found in CAR header');
}

// ─── GitHub helpers ────────────────────────────────────────────────────────

function ghHeaders(extra = {}) {
  return { Authorization: `Bearer ${GITHUB_TOKEN}`, Accept: 'application/vnd.github+json', ...extra };
}

async function getReleaseByTag(tag) {
  const res = await fetch(
    `https://api.github.com/repos/${REPO}/releases/tags/${tag}`,
    { headers: ghHeaders() }
  );
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
    if (res.ok) {
      // Content-Length cap
      const len = Number(res.headers.get('content-length') || 0);
      if (len && len > MAX_RELEASE_ASSET_BYTES) {
        throw new Error(`Release asset too large by Content-Length: ${len} > ${MAX_RELEASE_ASSET_BYTES}`);
      }

      const ab = await res.arrayBuffer();
      const buf = Buffer.from(ab);

      // Actual size cap
      if (buf.length > MAX_RELEASE_ASSET_BYTES) {
        throw new Error(`Release asset too large: ${buf.length} > ${MAX_RELEASE_ASSET_BYTES}`);
      }

      // Total bytes cap
      totalDownloadedBytes += buf.length;
      if (totalDownloadedBytes > MAX_TOTAL_RELEASE_BYTES) {
        throw new Error(`Total release download bytes exceed cap: ${totalDownloadedBytes} > ${MAX_TOTAL_RELEASE_BYTES}`);
      }

      return buf;
    }
    if ((res.status >= 500 || res.status === 403 || res.status === 429) && attempt < retries) {
      await sleep(5000 * (attempt + 1));
      continue;
    }
    throw new Error(`Download failed: ${res.status}`);
  }
}

// ─── Main ──────────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  const releaseTag = args.includes('--release-tag') ? args[args.indexOf('--release-tag') + 1] : 'nft-arweave-mirror-175-v1';
  const cidCheck = args.includes('--cid-check');
  const concurrencyArg = args.includes('--concurrency') ? Number(args[args.indexOf('--concurrency') + 1]) : null;
  const concurrency = concurrencyArg || VERIFY_CONCURRENCY;

  if (!GITHUB_TOKEN) { err('❌ GITHUB_TOKEN required'); process.exit(1); }

  log('═══════════════════════════════════════════════════════════');
  log('  Release Asset Re-Verification (v3 — strict, manifest-driven)');
  log('═══════════════════════════════════════════════════════════');
  log(`  Repo       : ${REPO}`);
  log(`  Release    : ${releaseTag}`);
  log(`  CID check  : ${cidCheck ? 'enabled (metadata=strict, media=audit)' : 'disabled'}`);
  log(`  Concurrency: ${concurrency}`);
  log(`  Max asset  : ${(MAX_RELEASE_ASSET_BYTES / 1024 / 1024).toFixed(0)}MB`);
  log(`  Max total  : ${(MAX_TOTAL_RELEASE_BYTES / 1024 / 1024 / 1024).toFixed(1)}GB`);
  log('');

  // ── 1. Get release + manifest ────────────────────────────────────────

  log('📦 Fetching release...');
  const release = await getReleaseByTag(releaseTag);
  log(`  Release ID: ${release.id}`);

  const allAssets = await getAllAssets(release.id);
  log(`  ${allAssets.length} assets total`);

  const manifestAsset = allAssets.find(a => a.name === 'RELEASE-MANIFEST.json');
  if (!manifestAsset) { err('❌ RELEASE-MANIFEST.json not found in release'); process.exit(1); }

  log('  Downloading RELEASE-MANIFEST.json...');
  const manifestBuf = await downloadAsset(manifestAsset.id);
  let rawManifest;
  try {
    rawManifest = JSON.parse(manifestBuf.toString('utf-8'));
  } catch (e) {
    err(`❌ RELEASE-MANIFEST.json is not valid JSON: ${e.message}`);
    process.exit(1);
  }

  // ── 2. Normalize manifest (schema gate) ──────────────────────────────

  let normalized;
  try {
    normalized = normalizeReleaseManifest(rawManifest);
  } catch (e) {
    err(`❌ Release manifest schema error: ${e.message}`);
    process.exit(1);
  }

  log(`  Manifest schema: ${normalized.schema}`);
  log(`  Expected NFTs  : ${normalized.expected_asset_count}`);
  log(`  Expected CARs  : ${normalized.expected_car_count}`);
  log('');

  // ── 3. Build lookup maps ─────────────────────────────────────────────

  const releaseAssetByName = new Map();
  const duplicateAssets = [];
  for (const asset of allAssets) {
    if (releaseAssetByName.has(asset.name)) {
      duplicateAssets.push(asset.name);
    }
    releaseAssetByName.set(asset.name, asset);
  }

  const expectedAssets = normalized.expected_release_assets || normalized.expected_nft_assets;
  const expectedNames = new Set(expectedAssets.map(x => x.name));

  // ── 4. Completeness checks ───────────────────────────────────────────

  const errors = [];
  let fail = 0;

  // Duplicate release assets
  for (const dup of duplicateAssets) {
    errors.push({ type: 'duplicate_release_asset', asset: dup });
    fail++;
  }

  // Missing expected assets
  const missingAssets = [];
  for (const expected of expectedAssets) {
    if (!releaseAssetByName.has(expected.name)) {
      errors.push({ type: 'missing_release_asset', asset: expected.name });
      missingAssets.push(expected.name);
      fail++;
    }
  }

  // Extra unexpected assets (ignore auxiliary assets)
  const auxiliaryAssets = new Set(normalized.auxiliary_assets || ['RELEASE-MANIFEST.json', 'nft-cars-manifest.tar.gz']);
  const extraAssets = [];
  for (const asset of allAssets) {
    if (auxiliaryAssets.has(asset.name)) continue;
    const looksVerifiable = asset.name.endsWith('.tar.gz') || asset.name.startsWith('nft-');
    if (looksVerifiable && !expectedNames.has(asset.name)) {
      errors.push({ type: 'unexpected_release_asset', asset: asset.name });
      extraAssets.push(asset.name);
      fail++;
    }
  }

  // Manifest count invariants
  if (expectedAssets.length !== normalized.expected_asset_count) {
    errors.push({ type: 'manifest_count_mismatch', field: 'expected_asset_count', expected: normalized.expected_asset_count, actual: expectedAssets.length });
    fail++;
  }

  log('🔍 Completeness checks...');
  log(`  Expected assets : ${expectedAssets.length}`);
  log(`  Missing assets  : ${missingAssets.length}`);
  log(`  Extra assets    : ${extraAssets.length}`);
  log(`  Duplicates      : ${duplicateAssets.length}`);
  log('');

  // ── 5. Verify each expected asset ────────────────────────────────────

  log('🔍 Re-verifying all expected NFT assets...');

  let totalChecks = 0;
  let sha256Pass = 0, sizePass = 0;
  let metaCidPass = 0, metaCidFail = 0, mediaCidPass = 0, mediaCidAudit = 0;
  let pass = 0;

  const tasks = expectedAssets
    .filter(expected => releaseAssetByName.has(expected.name))
    .map(expected => async () => {
      const asset = releaseAssetByName.get(expected.name);
      let assetOk = true;

      try {
        const tarBuf = await downloadAsset(asset.id);

        // Strict TAR extraction
        let tarFiles;
        try {
          tarFiles = extractFilesFromTarStrict(tarBuf);
        } catch (e) {
          errors.push({ asset: asset.name, type: 'tar_parse_error', error: e.message });
          fail++;
          return;
        }

        // Build TAR file lookup
        const tarFilesByName = new Map();
        for (const f of tarFiles) {
          if (tarFilesByName.has(f.name)) {
            errors.push({ asset: asset.name, type: 'duplicate_tar_entry', path: f.name });
            assetOk = false;
          }
          tarFilesByName.set(f.name, f);
        }

        // Check for unexpected TAR entries
        const expectedPaths = new Set(expected.files.map(f => f.expected_path));
        for (const tarEntry of tarFiles) {
          if (!expectedPaths.has(tarEntry.name)) {
            errors.push({ asset: asset.name, type: 'unexpected_tar_entry', path: tarEntry.name });
            assetOk = false;
          }
        }

        // Verify each expected file
        for (const f of expected.files) {
          totalChecks++;
          const tarEntry = tarFilesByName.get(f.expected_path);
          if (!tarEntry) {
            errors.push({ asset: asset.name, role: f.role, type: 'missing_tar_entry', expected_path: f.expected_path });
            assetOk = false;
            continue;
          }

          // SHA-256
          const hash = sha256hex(tarEntry.data);
          if (hash !== f.expected_sha256) {
            errors.push({ asset: asset.name, role: f.role, type: 'sha256_mismatch', expected: f.expected_sha256, actual: hash });
            assetOk = false;
          } else {
            sha256Pass++;
          }

          // Size
          if (tarEntry.data.length !== f.expected_size) {
            errors.push({ asset: asset.name, role: f.role, type: 'size_mismatch', expected: f.expected_size, actual: tarEntry.data.length });
            assetOk = false;
          } else {
            sizePass++;
          }

          // Root CID (only when --cid-check enabled)
          if (cidCheck) {
            try {
              const rootCid = extractCarRootCid(tarEntry.data);
              if (f.role === 'metadata') {
                if (rootCid !== f.expected_root_cid) {
                  errors.push({ asset: asset.name, role: f.role, type: 'cid_mismatch', expected: f.expected_root_cid, actual: rootCid });
                  metaCidFail++;
                  assetOk = false;
                } else {
                  metaCidPass++;
                }
              } else {
                // media: audit only
                if (rootCid === f.expected_root_cid) mediaCidPass++;
                else mediaCidAudit++;
              }
            } catch (e) {
              if (f.role === 'metadata') {
                errors.push({ asset: asset.name, role: f.role, type: 'cid_extract_failed', error: e.message });
                metaCidFail++;
                assetOk = false;
              } else {
                mediaCidAudit++;
              }
            }
          }
        }

        if (assetOk) pass++;

      } catch (e) {
        errors.push({ asset: asset.name, error: e.message });
      }
    });

  await runConcurrent(tasks, concurrency);
  const verifiedAssetCount = pass;
  log(`\r   Verified: ${pass} pass, ${fail} fail / ${expectedAssets.length}`);

  if (errors.length > 0) {
    log('');
    log(`  ❌ ${errors.length} errors:`);
    for (const e of errors.slice(0, 20)) {
      log(`    ${e.asset || ''} [${e.role || ''}] ${e.type || e.error}`);
    }
    if (errors.length > 20) log(`    ... and ${errors.length - 20} more`);
  }

  // ── 6. Compute status with invariants ────────────────────────────────

  const expectedCarCount = normalized.expected_car_count;
  const status = computeStatus({
    errors,
    sha256Pass,
    sizePass,
    carFilesExpected: expectedCarCount,
    assetsVerified: verifiedAssetCount,
    assetsExpected: normalized.expected_asset_count,
    cidCheckEnabled: cidCheck,
    metadataCidFail: metaCidFail,
  });

  // ── 7. Build report ──────────────────────────────────────────────────

  const verificationScope = cidCheck
    ? 'hash_size_and_metadata_cid'
    : 'hash_size_only';

  const doesNotProve = [
    'independent attestation',
    'on-chain ownership or tokenURI correctness',
    'physical authorship or provenance',
    'full DAG completeness unless full_dag_check_enabled is true',
    'that the release contains all declared NFTs beyond what the manifest declares and the verifier checks',
  ];

  if (!cidCheck) {
    doesNotProve.push('CID/root/DAG correctness');
    doesNotProve.push('on-chain evidence or full evidence chain');
  }

  const report = {
    schema: 'verify-release-report-v3',
    release_tag: releaseTag,
    generated_at: new Date().toISOString(),
    verification_scope: verificationScope,
    cid_check_enabled: cidCheck,
    full_dag_check_enabled: false,
    supported_manifest_schema: normalized.schema,

    required_checks: [
      'release manifest schema recognized',
      'manifest-declared asset set complete',
      'no duplicate release assets',
      'no extra unexpected nft-* assets',
      'TAR entries strict and non-duplicate',
      'expected SHA-256 matched for every expected CAR',
      'expected size matched for every expected CAR',
    ],
    optional_checks: cidCheck ? ['metadata root CID strict', 'media root CID audit'] : [],

    total_assets: allAssets.length,
    assets_expected: normalized.expected_asset_count,
    assets_verified: verifiedAssetCount,
    car_files_expected: expectedCarCount,
    car_files_checked: totalChecks,
    sha256_pass: sha256Pass,
    size_pass: sizePass,

    cid_check_enabled: cidCheck,
    metadata_cid_pass: cidCheck ? metaCidPass : null,
    metadata_cid_fail: cidCheck ? metaCidFail : null,
    media_cid_audit_pass: cidCheck ? mediaCidPass : null,
    media_cid_audit_warning: cidCheck ? mediaCidAudit : null,

    does_not_prove: doesNotProve,
    limitations: [
      'GitHub Release asset availability is checked through GitHub API at verification time.',
      'Hash and size verification do not by themselves prove on-chain tokenURI correctness.',
      'Media CID mismatches are audit warnings unless policy is changed to strict.',
      'TAR strict mode rejects duplicate entries, symlinks, and path traversal.',
    ],

    status,
    errors: errors.slice(0, 100),
    toolchain_provenance: collectToolchainProvenance(),
  };

  // ── 8. Write report ──────────────────────────────────────────────────

  const reportPath = path.join(process.cwd(), 'VERIFY-RELEASE-REPORT.json');
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  log(`\n  📝 VERIFY-RELEASE-REPORT.json written`);

  // ── 9. Summary ───────────────────────────────────────────────────────

  log('');
  log('═══════════════════════════════════════════════════════════');
  log(`  ${status === 'PASS' ? '✅ PASS' : '❌ FAIL'}: ${verifiedAssetCount}/${normalized.expected_asset_count} assets verified`);
  log(`  SHA-256 : ${sha256Pass}/${totalChecks} pass`);
  log(`  Size    : ${sizePass}/${totalChecks} pass`);
  log(`  Scope   : ${verificationScope}`);
  if (cidCheck) {
    log(`  Meta CID: ${metaCidPass} pass, ${metaCidFail} fail`);
    log(`  Media CID: ${mediaCidPass} match, ${mediaCidAudit} audit-warning`);
  }
  log('═══════════════════════════════════════════════════════════');

  if (status !== 'PASS') process.exit(1);
}

function computeStatus({ errors, sha256Pass, sizePass, carFilesExpected, assetsVerified, assetsExpected, cidCheckEnabled, metadataCidFail }) {
  if (errors.length > 0) return 'FAIL';
  if (assetsVerified !== assetsExpected) return 'FAIL';
  if (sha256Pass !== carFilesExpected) return 'FAIL';
  if (sizePass !== carFilesExpected) return 'FAIL';
  if (cidCheckEnabled && metadataCidFail !== 0) return 'FAIL';
  return 'PASS';
}

const isMain = process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1]);

if (isMain) {
  main().catch(e => { err('Fatal:', e); process.exit(1); });
}

export {
  normalizeReleaseManifest,
  extractFilesFromTarStrict,
  computeStatus,
  sha256hex,
};
