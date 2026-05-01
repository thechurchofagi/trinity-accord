#!/usr/bin/env node
/**
 * verify-eth-witness.mjs  (Step B — strict version)
 *
 * ETH guardian witness verification.
 * Primary witness + auxiliary attestations must ALL hard pass.
 * input_sha256 + input_len must be declared and verified for every tx.
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

const AUTHORITY_JCS_FILE = 'archive/authority-manifest/authority.jcs.json';
const EVIDENCE_MANIFEST_FILE = 'api/evidence-manifest.json';
const ETH_RPC_URL = process.env.ETH_RPC_URL;
const MAX_RETRIES = 3;

function log(msg) { console.log(msg); }
function err(msg) { console.error(msg); }
function sha256hex(buf) { return crypto.createHash('sha256').update(buf).digest('hex'); }
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function readRepoJson(filePath) {
  const fullPath = path.resolve(filePath);
  if (fs.existsSync(fullPath)) return JSON.parse(fs.readFileSync(fullPath, 'utf-8'));
  return null;
}

function hexDataToBytes(hex) {
  const s = String(hex || '');
  if (!s.startsWith('0x')) throw new Error('tx.input is not 0x-prefixed hex');
  const clean = s.slice(2);
  if (!/^[0-9a-fA-F]*$/.test(clean)) throw new Error('tx.input contains non-hex characters');
  if (clean.length % 2 !== 0) throw new Error('tx.input hex has odd length');
  return Buffer.from(clean, 'hex');
}

async function tryEthCallRaw(method, params, retries = MAX_RETRIES) {
  if (!ETH_RPC_URL) return { error: 'No ETH_RPC_URL configured' };
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const res = await fetch(ETH_RPC_URL, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
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

/**
 * Verify a single ETH transaction against declared attestation.
 * Returns detailed result with all fields explicitly set.
 */
async function verifyOneTx(txHash, expectedFrom, declaredInputSha256, declaredInputLen, label) {
  const detail = {
    label, tx_hash: txHash,
    expected_from: expectedFrom,
    observed_from: null,
    exists: false, receipt_success: false, from_match: false, block_confirmed: false,
    input_len_declared: declaredInputLen != null ? Number(declaredInputLen) : null,
    input_len_observed: null,
    input_size_match: null,
    input_sha256_declared: declaredInputSha256 ? String(declaredInputSha256).toLowerCase() : null,
    input_sha256_observed: null,
    input_sha256_match: null,
    pass: false,
    failure_reason: null,
  };

  try {
    if (!txHash) { detail.failure_reason = 'no_tx_hash'; return detail; }

    // eth_getTransactionByHash
    const txResult = await tryEthCallRaw('eth_getTransactionByHash', [txHash]);
    if (txResult.error || !txResult.result) {
      detail.failure_reason = `tx_fetch_failed: ${txResult.error}`;
      return detail;
    }

    const tx = txResult.result;
    detail.exists = true;
    detail.observed_from = tx.from?.toLowerCase() || null;

    // from match
    if (expectedFrom && tx.from) {
      detail.from_match = tx.from.toLowerCase() === expectedFrom.toLowerCase();
      if (!detail.from_match) { detail.failure_reason = 'from_mismatch'; }
    }

    // input parsing
    const inputData = tx.input || tx.data || '0x';
    if (!inputData || inputData === '0x') {
      detail.failure_reason = 'empty_input';
      return detail;
    }

    const inputBytes = hexDataToBytes(inputData);
    detail.input_len_observed = inputBytes.length;
    detail.input_sha256_observed = sha256hex(inputBytes);

    // input_len match
    if (declaredInputLen != null) {
      detail.input_size_match = detail.input_len_observed === Number(declaredInputLen);
      if (!detail.input_size_match) {
        detail.failure_reason = `input_len_mismatch: declared=${declaredInputLen} observed=${detail.input_len_observed}`;
      }
    } else {
      detail.failure_reason = 'missing_declared_input_len';
    }

    // input_sha256 match
    if (declaredInputSha256) {
      detail.input_sha256_match = detail.input_sha256_observed === String(declaredInputSha256).toLowerCase();
      if (!detail.input_sha256_match) {
        detail.failure_reason = `input_sha256_mismatch`;
      }
    } else {
      detail.failure_reason = 'missing_declared_input_sha256';
    }

    // receipt
    const receiptResult = await tryEthCallRaw('eth_getTransactionReceipt', [txHash]);
    if (receiptResult.result) {
      detail.receipt_success = receiptResult.result.status === '0x1';
      detail.block_confirmed = !!receiptResult.result.blockNumber;
      if (!detail.receipt_success) detail.failure_reason = 'receipt_failed';
      if (!detail.block_confirmed) detail.failure_reason = 'not_confirmed';
    } else {
      detail.failure_reason = 'receipt_fetch_failed';
    }

    // overall pass
    detail.pass = detail.exists && detail.receipt_success && detail.from_match
      && detail.block_confirmed && detail.input_sha256_match === true && detail.input_size_match === true;

  } catch (e) {
    detail.failure_reason = `exception: ${e.message}`;
  }

  return detail;
}

async function main() {
  log('═══════════════════════════════════════════════════════════');
  log('  Step B: ETH Witness Verification (strict)');
  log('═══════════════════════════════════════════════════════════\n');

  if (!ETH_RPC_URL) {
    err('❌ ETH_RPC_URL not set — cannot verify ETH witness');
    const result = { eth_witness_coverage_pass: false, fatal_error: 'ETH_RPC_URL not set' };
    fs.writeFileSync(path.join(process.cwd(), 'ETH-WITNESS-AUDIT.json'), JSON.stringify({ schema: 'trinity-accord.eth-witness-audit.v1', generated_at: new Date().toISOString(), ...result }, null, 2));
    process.exit(1);
  }

  const authority = readRepoJson(AUTHORITY_JCS_FILE);
  if (!authority) { err('❌ authority.jcs.json not found'); process.exit(1); }

  const guardianEthAddress = authority.guardian?.eth_address;
  const chainId = authority.ethereum?.chainId;
  const attestations = authority.ethereum?.attestations || [];

  log(`  Guardian ETH: ${guardianEthAddress}`);
  log(`  Chain ID    : ${chainId}`);
  log(`  Attestations: ${attestations.length}\n`);

  // ── Primary witness ────────────────────────────────────────────────
  log('── Primary ETH Witness ──\n');
  const evidenceManifest = readRepoJson(EVIDENCE_MANIFEST_FILE);
  const primaryTxHash = evidenceManifest?.eth_mirror_tx;

  // Find declared hash/size for primary tx from authority attestations
  const primaryAttInAuthority = attestations.find(a => a.tx_hash?.toLowerCase() === primaryTxHash?.toLowerCase());
  const primaryDeclaredSha256 = evidenceManifest?.input_sha256 || primaryAttInAuthority?.input_sha256 || null;
  const primaryDeclaredLen = evidenceManifest?.input_len || primaryAttInAuthority?.input_len || null;

  const primaryDetail = await verifyOneTx(primaryTxHash, guardianEthAddress, primaryDeclaredSha256, primaryDeclaredLen, 'primary-eth-witness');
  primaryDetail.source = 'evidence-manifest.json';

  log(`  tx: ${primaryTxHash?.slice(0, 20)}...`);
  log(`  exists: ${primaryDetail.exists}, receipt: ${primaryDetail.receipt_success}, from: ${primaryDetail.from_match}`);
  log(`  input_sha256: ${primaryDetail.input_sha256_match}, input_size: ${primaryDetail.input_size_match}`);
  log(`  Primary pass: ${primaryDetail.pass}`);
  if (!primaryDetail.pass) log(`  Failure: ${primaryDetail.failure_reason}`);

  // ── Auxiliary attestations ──────────────────────────────────────────
  log('\n── Auxiliary ETH Attestations ──\n');
  const auxDetails = [];
  let auxPass = 0, auxFail = 0;
  let txFromMatch = 0, txInputSha256Match = 0, txInputSizeMatch = 0, receiptSuccess = 0;

  for (let i = 0; i < attestations.length; i++) {
    const att = attestations[i];
    // Skip if this is the same as primary witness
    if (att.tx_hash?.toLowerCase() === primaryTxHash?.toLowerCase()) {
      log(`  [${i}] ${att.label}: skipped (same as primary witness)`);
      continue;
    }

    const detail = await verifyOneTx(att.tx_hash, guardianEthAddress, att.input_sha256, att.input_len, att.label || `attestation-${i}`);

    if (detail.pass) { auxPass++; } else { auxFail++; }
    if (detail.from_match) txFromMatch++;
    if (detail.input_sha256_match === true) txInputSha256Match++;
    if (detail.input_size_match === true) txInputSizeMatch++;
    if (detail.receipt_success) receiptSuccess++;

    log(`  [${i}] ${detail.label}: pass=${detail.pass} ${detail.pass ? '' : `reason=${detail.failure_reason}`}`);
    auxDetails.push(detail);
  }

  // ── Overall ────────────────────────────────────────────────────────
  const primaryPass = primaryDetail.pass;
  const hardFailures = (primaryPass ? 0 : 1) + auxFail;
  const ethWitnessCoveragePass = primaryPass && auxFail === 0 && hardFailures === 0;

  log(`\n  Primary witness pass          : ${primaryPass}`);
  log(`  Auxiliary attestations total  : ${auxDetails.length}`);
  log(`  Auxiliary attestations pass   : ${auxPass}`);
  log(`  Auxiliary attestations fail   : ${auxFail}`);
  log(`  Hard failures                 : ${hardFailures}`);
  log(`  Chain B pass                  : ${ethWitnessCoveragePass}`);

  const audit = {
    schema: 'trinity-accord.eth-witness-audit.v1',
    generated_at: new Date().toISOString(),
    eth_witness_coverage_pass: ethWitnessCoveragePass,
    guardian_eth_address: guardianEthAddress,
    eth_chain_id_expected: chainId,
    primary_eth_witness_pass: primaryPass,
    primary_eth_witness: primaryDetail,
    auxiliary_attestations_total: auxDetails.length,
    auxiliary_attestations_pass: auxPass,
    auxiliary_attestations_fail: auxFail,
    auxiliary_attestations: auxDetails,
    tx_from_match: txFromMatch + (primaryDetail.from_match ? 1 : 0),
    tx_input_sha256_match: txInputSha256Match + (primaryDetail.input_sha256_match ? 1 : 0),
    tx_input_size_match: txInputSizeMatch + (primaryDetail.input_size_match ? 1 : 0),
    receipt_success: receiptSuccess + (primaryDetail.receipt_success ? 1 : 0),
    hard_failures: hardFailures,
  };

  const outPath = path.join(process.cwd(), 'ETH-WITNESS-AUDIT.json');
  fs.writeFileSync(outPath, JSON.stringify(audit, null, 2));
  log(`\n📝 ${outPath} written`);

  if (!ethWitnessCoveragePass) {
    err('\n  ❌ ETH WITNESS VERIFICATION FAILED');
    process.exit(1);
  }
  log('\n  ✅ ETH witness verification passed.');
}

main().catch(e => { err('Fatal:', e.message || e); if (e.stack) err(e.stack); process.exit(1); });
