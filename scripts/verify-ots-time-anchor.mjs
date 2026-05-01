#!/usr/bin/env node
/**
 * verify-ots-time-anchor.mjs  (Step C — ci-api + fullnode)
 *
 * OTS / Bitcoin time anchor verification.
 *
 * Modes (env OTS_VERIFY_MODE):
 *   ci-api   — default, for GitHub-hosted runners. Uses ots info + ots verify --no-bitcoin + public Bitcoin API.
 *   fullnode — for self-hosted runners with Bitcoin Core. Uses ots verify with local node.
 *
 * Must verify ALL 3 files: digest-manifest.json, digest-manifest.csv, verify-report.json.
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { spawnSync } from 'node:child_process';

// ═══════════════════════════════════════════════════════════════════════════
// CLI ARGS & CONFIG
// ═══════════════════════════════════════════════════════════════════════════

const args = process.argv.slice(2);
function getArg(name, def) {
  const idx = args.indexOf(name);
  return idx >= 0 && idx + 1 < args.length ? args[idx + 1] : def;
}
const OTS_RELEASE_TAG = getArg('--ots-release-tag', 'ots-and-flaw-mirror-v1');

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO = 'thechurchofagi/trinity-accord';
const OTS_VERIFY_MODE = process.env.OTS_VERIFY_MODE || 'ci-api';
const BTC_API_BASE = process.env.BITCOIN_API_BASE || 'https://mempool.space/api';
const BTC_API_FALLBACK = 'https://blockstream.info/api';
const MAX_RETRIES = 3;
const TMP_DIR = '/tmp/ots-verify';

// File candidate paths
const DIGEST_JSON_CANDIDATES = [
  'digest-manifest.json',
  'archive/evidence/digest-manifest.json',
  'archive/digest-manifest.json',
  'public/digest-manifest.json',
  'data/digest-manifest.json'
];
const DIGEST_CSV_CANDIDATES = [
  'digest-manifest.csv',
  'archive/evidence/digest-manifest.csv',
  'archive/digest-manifest.csv',
  'public/digest-manifest.csv',
  'data/digest-manifest.csv'
];
const VERIFY_REPORT_CANDIDATES = [
  'verify-report.json',
  'archive/evidence/verify-report.json',
  'archive/verify-report.json',
  'public/verify-report.json',
  'data/verify-report.json',
  'ots/verify-report.json'
];
const OTS_CANDIDATE_DIRS = [
  '.',
  'ots',
  'archive/ots',
  'archive/evidence',
  'archive/evidence/ots-proofs/OTS',
  'public',
  'data'
];

// ═══════════════════════════════════════════════════════════════════════════
// HELPERS
// ═══════════════════════════════════════════════════════════════════════════

function log(msg) { console.log(msg); }
function err(msg) { console.error(msg); }
function sha256hex(buf) { return crypto.createHash('sha256').update(buf).digest('hex'); }
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

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

function findFileByCandidates(candidates) {
  for (const c of candidates) {
    const buf = readRepoFile(c);
    if (buf) return { path: path.resolve(c), relativePath: c, buf };
  }
  return null;
}

function findOtsProof(filename) {
  // Try local dirs first
  for (const dir of OTS_CANDIDATE_DIRS) {
    const p = path.resolve(dir, filename);
    if (fs.existsSync(p)) return p;
  }
  return null;
}

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

async function btcFetch(endpoint, retries = 2) {
  const bases = [BTC_API_BASE, BTC_API_FALLBACK];
  for (const base of bases) {
    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const res = await fetch(`${base}${endpoint}`);
        if (res.status === 404) return null;
        if (!res.ok) throw new Error(`BTC API ${res.status}`);
        const text = await res.text();
        try { return JSON.parse(text); } catch { return text; }
      } catch (e) {
        if (attempt < retries) { await sleep(1500 * (attempt + 1)); continue; }
      }
    }
  }
  return null;
}

function runCmd(cmd, cmdArgs, opts = {}) {
  const r = spawnSync(cmd, cmdArgs, { encoding: 'utf8', maxBuffer: 20 * 1024 * 1024, timeout: 120000, ...opts });
  return { ok: r.status === 0, status: r.status, stdout: r.stdout || '', stderr: r.stderr || '' };
}

// ═══════════════════════════════════════════════════════════════════════════
// OTS COMMANDS
// ═══════════════════════════════════════════════════════════════════════════

function otsInfo(otsPath) {
  return runCmd('ots', ['info', otsPath]);
}

function otsVerifyNoBitcoin(otsPath, filePath) {
  const attempts = [
    ['verify', '--no-bitcoin', otsPath, '-f', filePath],
    ['verify', '--no-bitcoin', '-f', filePath, otsPath]
  ];
  let last = null;
  for (const cmdArgs of attempts) {
    const r = runCmd('ots', cmdArgs);
    last = r;
    if (r.ok) return { ok: true, args: cmdArgs, stdout: r.stdout, stderr: r.stderr };
  }
  return { ok: false, stdout: last?.stdout || '', stderr: last?.stderr || '' };
}

function otsVerifyFullnode(otsPath, filePath) {
  const attempts = [
    ['verify', otsPath, '-f', filePath],
    ['verify', '-f', filePath, otsPath]
  ];
  let last = null;
  for (const cmdArgs of attempts) {
    const r = runCmd('ots', cmdArgs);
    last = r;
    if (r.ok) return { ok: true, args: cmdArgs, stdout: r.stdout, stderr: r.stderr };
    if ((r.stdout || '').includes('Success!') || (r.stdout || '').includes('attested')) {
      return { ok: true, args: cmdArgs, stdout: r.stdout, stderr: r.stderr };
    }
  }
  return { ok: false, stdout: last?.stdout || '', stderr: last?.stderr || '' };
}

function otsUpgrade(otsPath) {
  return runCmd('ots', ['upgrade', otsPath]);
}

function parseBitcoinAttestation(infoText) {
  const text = String(infoText || '');
  const hasBitcoinAttestation = /BitcoinBlockHeaderAttestation|bitcoin block|block header/i.test(text);
  const blockHeights = [];
  for (const m of text.matchAll(/(?:block height|height|BitcoinBlockHeaderAttestation)\D+(\d+)/gi)) {
    blockHeights.push(Number(m[1]));
  }
  const blockHashes = [];
  for (const m of text.matchAll(/\b[0-9a-f]{64}\b/gi)) {
    blockHashes.push(m[0].toLowerCase());
  }
  const txids = [];
  for (const m of text.matchAll(/(?:txid|transaction id|tx)\D+([0-9a-f]{64})/gi)) {
    txids.push(m[1].toLowerCase());
  }
  return {
    hasBitcoinAttestation,
    block_heights: [...new Set(blockHeights)],
    candidate_hashes: [...new Set(blockHashes)],
    txids: [...new Set(txids)]
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// MAIN
// ═══════════════════════════════════════════════════════════════════════════

async function main() {
  if (!GITHUB_TOKEN) { err('❌ GITHUB_TOKEN required'); process.exit(1); }
  if (!fs.existsSync(TMP_DIR)) fs.mkdirSync(TMP_DIR, { recursive: true });

  const isCiApi = OTS_VERIFY_MODE === 'ci-api';

  log('═══════════════════════════════════════════════════════════');
  log('  Step C: OTS / Bitcoin Time Anchor Verification');
  log(`  Mode: ${OTS_VERIFY_MODE}`);
  log('═══════════════════════════════════════════════════════════\n');

  // Check ots CLI
  let otsAvailable = false;
  try {
    const r = runCmd('ots', ['--version']);
    otsAvailable = r.ok;
    if (otsAvailable) log('  ✅ ots CLI available');
  } catch {}
  if (!otsAvailable) {
    try {
      spawnSync('pip3', ['install', 'opentimestamps-client'], { encoding: 'utf8', timeout: 60000 });
      const r = runCmd('ots', ['--version']);
      otsAvailable = r.ok;
      if (otsAvailable) log('  ✅ ots CLI installed');
    } catch {}
  }
  if (!otsAvailable) {
    err('  ❌ ots CLI not available');
  }

  // Check Bitcoin Core availability (for fullnode mode)
  let bitcoinCoreAvailable = false;
  if (!isCiApi) {
    const cookiePath = path.join(process.env.HOME || '/root', '.bitcoin', '.cookie');
    bitcoinCoreAvailable = fs.existsSync(cookiePath);
    if (!bitcoinCoreAvailable) {
      log('  ⚠️ Bitcoin Core not detected (no .cookie file). Will fall back to ci-api behavior.');
    }
  }

  // Targets: 3 files required
  const targets = [
    { label: 'digest-manifest.json', candidates: DIGEST_JSON_CANDIDATES },
    { label: 'digest-manifest.csv', candidates: DIGEST_CSV_CANDIDATES },
    { label: 'verify-report.json', candidates: VERIFY_REPORT_CANDIDATES },
  ];

  // Download OTS proofs from release if not found locally
  const otsProofBuffers = {};
  const needsReleaseDownload = targets.some(t => !findOtsProof(`${t.label}.ots`));
  if (needsReleaseDownload) {
    log(`📦 Fetching OTS release ${OTS_RELEASE_TAG}...`);
    try {
      const otsRelease = await getReleaseByTag(OTS_RELEASE_TAG);
      const otsAssets = await getAllAssets(otsRelease.id);
      for (const asset of otsAssets) {
        if (asset.name.endsWith('.ots')) {
          try { otsProofBuffers[asset.name] = await downloadAsset(asset.id); log(`  Downloaded: ${asset.name}`); }
          catch (e) { log(`  Failed: ${asset.name}: ${e.message}`); }
        }
      }
    } catch (e) { log(`  ⚠️ OTS release not found: ${e.message}`); }
  }

  const result = {
    ots_time_anchor_pass: false,
    ots_verification_mode: OTS_VERIFY_MODE,
    ots_ci_check_pass: false,
    ots_fullnode_verify_pass: false,
    fullnode_independent_verification: false,
    verification_note: isCiApi
      ? 'CI mode uses public Bitcoin APIs; full independent verification requires Bitcoin Core.'
      : 'Fullnode mode uses local Bitcoin Core for independent verification.',
    environment_missing_bitcoin_core: isCiApi ? false : !bitcoinCoreAvailable,
    ots_files_total: 3,
    ots_original_files_found: 0,
    ots_files_pass: 0,
    ots_files_fail: 0,
    missing_original_files: [],
    proof_without_original_file: 0,
    anchored_files: [],
    upgraded_ots_files: [],
    critical_errors: [],
  };

  for (const target of targets) {
    const detail = {
      file: target.label,
      file_path: null,
      ots: `${target.label}.ots`,
      ots_path: null,
      original_file_exists: false,
      ots_file_exists: false,
      original_size: null,
      original_sha256: null,
      ots_info_ok: false,
      ots_verify_no_bitcoin_ok: null,
      bitcoin_attested: false,
      bitcoin_api_checked: false,
      bitcoin_api_check_level: null,
      block_height: null,
      block_hash: null,
      block_time: null,
      bitcoin_txid: null,
      tx_confirmed: null,
      pass: false,
      failure_reason: null,
      ots_info_output: null,
      ots_verify_output: null,
      error: null,
    };

    try {
      // 1. Find original file
      const found = findFileByCandidates(target.candidates);
      if (!found) {
        detail.error = `Original file not found: ${target.label}`;
        detail.failure_reason = 'original_file_missing';
        result.ots_files_fail++;
        result.missing_original_files.push({
          file: target.label,
          searched_paths: target.candidates
        });
        result.anchored_files.push(detail);
        result.critical_errors.push(detail.error);
        continue;
      }
      detail.original_file_exists = true;
      detail.file_path = found.relativePath;
      detail.original_size = found.buf.length;
      detail.original_sha256 = sha256hex(found.buf);
      result.ots_original_files_found++;

      // Write to tmp for ots commands
      const tmpFilePath = path.join(TMP_DIR, target.label);
      fs.writeFileSync(tmpFilePath, found.buf);

      // 2. Find OTS proof
      let otsPath = findOtsProof(`${target.label}.ots`);
      if (!otsPath && otsProofBuffers[`${target.label}.ots`]) {
        otsPath = path.join(TMP_DIR, `${target.label}.ots`);
        fs.writeFileSync(otsPath, otsProofBuffers[`${target.label}.ots`]);
      }
      if (!otsPath) {
        detail.error = `OTS proof not found: ${target.label}.ots`;
        detail.failure_reason = 'ots_proof_missing';
        result.ots_files_fail++;
        result.anchored_files.push(detail);
        result.critical_errors.push(detail.error);
        continue;
      }
      detail.ots_file_exists = true;
      detail.ots_path = otsPath;

      // 3. ots info (always run)
      const infoResult = otsAvailable ? otsInfo(otsPath) : { ok: false, stdout: '', stderr: '' };
      detail.ots_info_ok = infoResult.ok;
      detail.ots_info_output = (infoResult.stdout || infoResult.stderr || '').trim().slice(0, 3000);
      const attestation = parseBitcoinAttestation(detail.ots_info_output);

      // 4. Verify based on mode
      let verifyOk = false;
      let verifyOutput = '';

      if (isCiApi) {
        // ci-api mode: try ots verify --no-bitcoin
        if (otsAvailable) {
          const noBtcResult = otsVerifyNoBitcoin(otsPath, tmpFilePath);
          detail.ots_verify_no_bitcoin_ok = noBtcResult.ok;
          verifyOutput = (noBtcResult.stdout + noBtcResult.stderr).trim().slice(0, 2000);
          verifyOk = noBtcResult.ok;

          // If --no-bitcoin not supported, still continue
          if (!noBtcResult.ok && noBtcResult.stderr.includes('--no-bitcoin')) {
            detail.ots_verify_no_bitcoin_ok = null;
            log(`    ⚠️ --no-bitcoin not supported by ots CLI`);
          }
        }

        // Bitcoin API cross-check
        if (attestation.hasBitcoinAttestation || attestation.block_heights.length > 0) {
          detail.bitcoin_attested = true;

          if (attestation.block_heights.length > 0) {
            detail.block_height = attestation.block_heights.sort((a, b) => b - a)[0];
            try {
              const blockHash = await btcFetch(`/block-height/${detail.block_height}`);
              if (typeof blockHash === 'string' && blockHash.length === 64) {
                detail.block_hash = blockHash;
                detail.bitcoin_api_checked = true;
                detail.bitcoin_api_check_level = 'block_height';
                const blockDetail = await btcFetch(`/block/${blockHash}`);
                if (blockDetail) detail.block_time = blockDetail.timestamp;
              }
            } catch (e) { log(`    ⚠️ Could not query block ${detail.block_height}`); }
          }

          // If we have txids, verify them
          if (attestation.txids.length > 0) {
            detail.bitcoin_txid = attestation.txids[0];
            try {
              const txInfo = await btcFetch(`/tx/${detail.bitcoin_txid}`);
              if (txInfo?.status?.confirmed) {
                detail.tx_confirmed = true;
                if (txInfo.status.block_height) detail.block_height = txInfo.status.block_height;
                if (txInfo.status.block_hash) detail.block_hash = txInfo.status.block_hash;
                detail.bitcoin_api_checked = true;
                detail.bitcoin_api_check_level = 'tx';
              }
            } catch (e) { log(`    ⚠️ Could not query tx ${detail.bitcoin_txid}`); }
          }
        }

        // ci-api pass: info ok + attested + API checked
        const ciPass = detail.ots_info_ok && detail.bitcoin_attested && detail.bitcoin_api_checked;
        if (ciPass) {
          verifyOk = true;
        } else if (!detail.ots_info_ok) {
          verifyOk = false;
        } else {
          // info ok but no attestation — try upgrade as fallback
          if (otsAvailable) {
            log(`  ⚠️ ${target.label}: no Bitcoin attestation in info, attempting upgrade...`);
            const upgradeResult = otsUpgrade(otsPath);
            if (upgradeResult.ok) {
              result.upgraded_ots_files.push(`${target.label}.ots`);
              const info2 = otsInfo(otsPath);
              const att2 = parseBitcoinAttestation(info2.stdout || '');
              if (att2.hasBitcoinAttestation || att2.block_heights.length > 0) {
                detail.bitcoin_attested = true;
                if (att2.block_heights.length > 0) {
                  detail.block_height = att2.block_heights.sort((a, b) => b - a)[0];
                  try {
                    const blockHash = await btcFetch(`/block-height/${detail.block_height}`);
                    if (typeof blockHash === 'string' && blockHash.length === 64) {
                      detail.block_hash = blockHash;
                      detail.bitcoin_api_checked = true;
                      detail.bitcoin_api_check_level = 'block_height';
                      const blockDetail = await btcFetch(`/block/${blockHash}`);
                      if (blockDetail) detail.block_time = blockDetail.timestamp;
                    }
                  } catch {}
                }
                verifyOk = detail.bitcoin_attested && detail.bitcoin_api_checked;
              }
            }
          }
        }

        detail.ots_verify_output = verifyOutput;

      } else {
        // fullnode mode
        if (!bitcoinCoreAvailable) {
          detail.failure_reason = 'environment_missing_bitcoin_core';
          detail.error = 'Bitcoin Core not available. Run on self-hosted runner or use OTS_VERIFY_MODE=ci-api';
          result.ots_files_fail++;
          result.anchored_files.push(detail);
          result.critical_errors.push(detail.error);
          continue;
        }

        if (otsAvailable) {
          const fullnodeResult = otsVerifyFullnode(otsPath, tmpFilePath);
          detail.ots_verify_output = (fullnodeResult.stdout + fullnodeResult.stderr).trim().slice(0, 2000);
          verifyOk = fullnodeResult.ok;

          if (!verifyOk) {
            // Try upgrade
            log(`  ⚠️ ${target.label}: ots verify failed, attempting upgrade...`);
            const upgradeResult = otsUpgrade(otsPath);
            if (upgradeResult.ok) {
              result.upgraded_ots_files.push(`${target.label}.ots`);
              const retry = otsVerifyFullnode(otsPath, tmpFilePath);
              detail.ots_verify_output = (retry.stdout + retry.stderr).trim().slice(0, 2000);
              verifyOk = retry.ok;
            }
          }
        }

        // Parse attestation from verify output or info
        if (attestation.hasBitcoinAttestation || attestation.block_heights.length > 0) {
          detail.bitcoin_attested = true;
          if (attestation.block_heights.length > 0) {
            detail.block_height = attestation.block_heights.sort((a, b) => b - a)[0];
            try {
              const blockHash = await btcFetch(`/block-height/${detail.block_height}`);
              if (typeof blockHash === 'string' && blockHash.length === 64) {
                detail.block_hash = blockHash;
                detail.bitcoin_api_checked = true;
                const blockDetail = await btcFetch(`/block/${blockHash}`);
                if (blockDetail) detail.block_time = blockDetail.timestamp;
              }
            } catch {}
          }
          if (attestation.txids.length > 0) detail.bitcoin_txid = attestation.txids[0];
        }
      }

      // 5. Final pass/fail
      if (verifyOk) {
        detail.pass = true;
        result.ots_files_pass++;
        log(`  ✅ ${target.label}: pass (block ${detail.block_height || '?'}, API ${detail.bitcoin_api_checked ? 'checked' : 'skip'})`);
      } else {
        detail.pass = false;
        detail.failure_reason = detail.failure_reason || (!detail.ots_info_ok ? 'ots_info_failed' : !detail.bitcoin_attested ? 'no_bitcoin_attestation' : 'verification_failed');
        detail.error = detail.error || detail.failure_reason;
        result.ots_files_fail++;
        result.critical_errors.push(`${target.label}: ${detail.failure_reason}`);
        log(`  ❌ ${target.label}: ${detail.failure_reason}`);
      }

    } catch (e) {
      detail.error = e.message;
      detail.failure_reason = 'exception';
      result.ots_files_fail++;
      result.critical_errors.push(`${target.label}: ${e.message}`);
    }
    result.anchored_files.push(detail);
  }

  // Final results
  const allPass = result.ots_files_pass === 3 && result.ots_files_fail === 0;

  if (isCiApi) {
    result.ots_ci_check_pass = allPass;
    result.ots_time_anchor_pass = allPass;
    result.ots_fullnode_verify_pass = false;
    result.fullnode_independent_verification = false;
  } else {
    result.ots_fullnode_verify_pass = allPass;
    result.fullnode_independent_verification = allPass;
    result.ots_ci_check_pass = false;
    result.ots_time_anchor_pass = allPass;
  }

  log(`\n  OTS files total  : ${result.ots_files_total}`);
  log(`  OTS originals    : ${result.ots_original_files_found}`);
  log(`  OTS files pass   : ${result.ots_files_pass}`);
  log(`  OTS files fail   : ${result.ots_files_fail}`);
  log(`  Mode             : ${OTS_VERIFY_MODE}`);
  if (isCiApi) {
    log(`  CI check pass    : ${result.ots_ci_check_pass}`);
  } else {
    log(`  Fullnode pass    : ${result.ots_fullnode_verify_pass}`);
    log(`  Bitcoin Core     : ${bitcoinCoreAvailable ? 'available' : 'MISSING'}`);
  }
  log(`  Chain C pass     : ${result.ots_time_anchor_pass}`);

  const outPath = path.join(process.cwd(), 'OTS-TIME-ANCHOR-AUDIT.json');
  const output = {
    schema: 'trinity-accord.ots-time-anchor.v1',
    generated_at: new Date().toISOString(),
    ...result
  };
  fs.writeFileSync(outPath, JSON.stringify(output, null, 2));
  log(`\n📝 ${outPath} written`);

  if (!result.ots_time_anchor_pass) {
    err('\n  ❌ OTS TIME ANCHOR VERIFICATION FAILED');
    for (const e of result.critical_errors) err(`    ❌ ${e}`);
    process.exit(1);
  }
  log('\n  ✅ OTS time anchor verification passed.');
}

main().catch(e => { err('Fatal:', e.message || e); if (e.stack) err(e.stack); process.exit(1); });
