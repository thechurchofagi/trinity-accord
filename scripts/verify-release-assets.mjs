#!/usr/bin/env node
/**
 * verify-release-assets.mjs  (v2 — concurrent, optional CID check)
 *
 * Downloads ALL NFT .tar assets from a GitHub Release and re-verifies:
 *   1. SHA-256 of every CAR inside the tar == RELEASE-MANIFEST.json expected_sha256
 *   2. Size of every CAR               == expected_size
 *   3. Root CID (metadata=strict, media=audit) — ONLY when --cid-check is passed
 *
 * This is a SEPARATE script from backup-nft-arweave-mirror.mjs.
 * Run it independently to verify an existing release without re-uploading.
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

// ─── Config ────────────────────────────────────────────────────────────────

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO = process.env.REPO || 'thechurchofagi/trinity-accord';
const MAX_RETRIES = 3;
const VERIFY_CONCURRENCY = Number(process.env.VERIFY_CONCURRENCY || 8);

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

// ─── CAR parsing (root CID extraction only) ────────────────────────────────

function parseCarHeader(data) {
  let pos = 0, shift = 0, headerLen = 0;
  while (true) {
    const b = data[pos]; headerLen |= (b & 0x7f) << shift; pos++; shift += 7;
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

// ─── Tar extraction ────────────────────────────────────────────────────────

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
    if (res.ok) return Buffer.from(await res.arrayBuffer());
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
  log('  Release Asset Re-Verification (v2 — concurrent)');
  log('═══════════════════════════════════════════════════════════');
  log(`  Repo       : ${REPO}`);
  log(`  Release    : ${releaseTag}`);
  log(`  CID check  : ${cidCheck ? 'enabled (metadata=strict, media=audit)' : 'disabled'}`);
  log(`  Concurrency: ${concurrency}`);
  log('');

  // 1. Get release + manifest
  log('📦 Fetching release...');
  const release = await getReleaseByTag(releaseTag);
  log(`  Release ID: ${release.id}`);

  const allAssets = await getAllAssets(release.id);
  log(`  ${allAssets.length} assets total`);

  const manifestAsset = allAssets.find(a => a.name === 'RELEASE-MANIFEST.json');
  if (!manifestAsset) { err('❌ RELEASE-MANIFEST.json not found in release'); process.exit(1); }

  log('  Downloading RELEASE-MANIFEST.json...');
  const manifestBuf = await downloadAsset(manifestAsset.id);
  const manifest = JSON.parse(manifestBuf.toString('utf-8'));
  log(`  Manifest: ${manifest.actual_nfts} NFTs, ${manifest.total_car_files} CARs`);
  log('');

  // 2. Build verification tasks
  log('🔍 Re-verifying all NFT assets...');
  const nftAssets = allAssets.filter(a => a.name.startsWith('nft-'));

  let totalChecks = 0;
  let sha256Pass = 0, sizePass = 0;
  let metaCidPass = 0, metaCidFail = 0, mediaCidPass = 0, mediaCidAudit = 0;
  const errors = [];
  let pass = 0, fail = 0;

  const tasks = nftAssets.map(asset => async () => {
    const manifestEntry = manifest.per_nft_assets?.find(m => m.nft_asset_name === asset.name);
    if (!manifestEntry) {
      errors.push({ asset: asset.name, error: 'not in manifest' });
      fail++;
      return;
    }

    try {
      const tarBuf = await downloadAsset(asset.id);
      const tarFiles = extractFilesFromTar(tarBuf);

      let assetOk = true;
      for (const f of manifestEntry.files) {
        totalChecks++;
        const carName = `${f.role}.car`;
        const tarEntry = tarFiles.find(t => t.name === `nft/${carName}`);
        if (!tarEntry) {
          errors.push({ asset: asset.name, role: f.role, error: 'missing in tar' });
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
      else fail++;

      if ((pass + fail) % 20 === 0) process.stdout.write(`\r   ${pass + fail}/${nftAssets.length}`);
    } catch (e) {
      errors.push({ asset: asset.name, error: e.message });
      fail++;
    }
  });

  await runConcurrent(tasks, concurrency);
  log(`\r   Verified: ${pass} pass, ${fail} fail / ${nftAssets.length}`);

  if (errors.length > 0) {
    log('');
    log(`  ❌ ${errors.length} errors:`);
    for (const e of errors.slice(0, 20)) {
      log(`    ${e.asset} [${e.role || ''}] ${e.type || e.error}`);
    }
    if (errors.length > 20) log(`    ... and ${errors.length - 20} more`);
  }

  // 3. Write VERIFY-RELEASE-REPORT.json
  const report = {
    schema: 'verify-release-report-v2',
    release_tag: releaseTag,
    generated_at: new Date().toISOString(),
    total_assets: allAssets.length,
    nft_assets_checked: nftAssets.length,
    car_files_checked: totalChecks,
    sha256_pass: sha256Pass,
    size_pass: sizePass,
    cid_check_enabled: cidCheck,
    metadata_cid_pass: cidCheck ? metaCidPass : null,
    metadata_cid_fail: cidCheck ? metaCidFail : null,
    media_cid_audit_pass: cidCheck ? mediaCidPass : null,
    media_cid_audit_warning: cidCheck ? mediaCidAudit : null,
    status: fail === 0 ? 'PASS' : 'FAIL',
    errors: errors.slice(0, 100),
  };

  const reportPath = path.join(process.cwd(), 'VERIFY-RELEASE-REPORT.json');
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  log(`\n  📝 VERIFY-RELEASE-REPORT.json written`);

  log('');
  log('═══════════════════════════════════════════════════════════');
  log(`  ${fail === 0 ? '✅ PASS' : '❌ FAIL'}: ${pass}/${nftAssets.length} assets verified`);
  log(`  SHA-256 : ${sha256Pass}/${totalChecks} pass`);
  log(`  Size    : ${sizePass}/${totalChecks} pass`);
  if (cidCheck) {
    log(`  Meta CID: ${metaCidPass} pass, ${metaCidFail} fail`);
    log(`  Media CID: ${mediaCidPass} match, ${mediaCidAudit} audit-warning`);
  }
  log('═══════════════════════════════════════════════════════════');

  if (fail > 0) process.exit(1);
}

main().catch(e => { err('Fatal:', e); process.exit(1); });
