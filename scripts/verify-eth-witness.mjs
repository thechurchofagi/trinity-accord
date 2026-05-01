#!/usr/bin/env node
/**
 * verify-eth-witness.mjs  (Step 4)
 *
 * ETH guardian witness verification for Trinity Accord.
 *
 * Proves:
 *   - Primary ETH witness tx (evidence-manifest.json eth_mirror_tx) exists and is valid
 *   - Auxiliary ETH attestations (authority.jcs.json ethereum.attestations[]) are valid
 *   - tx.from matches guardian ETH address
 *   - tx.input sha256 and size match manifest declarations
 *
 * Does NOT verify: DAG, BTC signatures, OTS, Bitcoin tx anchors.
 *
 * Output: ETH-WITNESS-AUDIT.json
 *
 * Usage:
 *   ETH_RPC_URL=https://... node scripts/verify-eth-witness.mjs
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

// ═══════════════════════════════════════════════════════════════════════════
// CONFIG
// ═══════════════════════════════════════════════════════════════════════════

const AUTHORITY_JCS_FILE = 'archive/authority-manifest/authority.jcs.json';
const EVIDENCE_MANIFEST_FILE = 'api/evidence-manifest.json';
const ETH_RPC_URL = process.env.ETH_RPC_URL;
const MAX_RETRIES = 3;

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
// MAIN
// ═══════════════════════════════════════════════════════════════════════════

async function main() {
  log('═══════════════════════════════════════════════════════════');
  log('  Step 4: ETH Witness Verification');
  log('═══════════════════════════════════════════════════════════\n');

  const result = {
    primary_eth_witness_pass: false,
    eth_witness_coverage_pass: false,
    guardian_eth_address: null,
    primary_witness: null,
    eth_attestations_total: 0,
    eth_attestations_pass: 0,
    eth_attestations_fail: 0,
    tx_from_match: 0,
    tx_input_sha256_match: 0,
    tx_input_size_match: 0,
    receipt_success: 0,
    attestation_details: [],
    critical_errors: [],
  };

  // 1. Read authority
  const authority = readRepoJson(AUTHORITY_JCS_FILE);
  if (!authority) {
    result.critical_errors.push('authority.jcs.json not found');
    err('❌ authority.jcs.json not found');
    writeOutput(result); process.exit(1);
  }

  const guardianEthAddress = authority.guardian?.eth_address;
  const chainId = authority.ethereum?.chainId;
  const attestations = authority.ethereum?.attestations || [];

  result.guardian_eth_address = guardianEthAddress;
  result.eth_attestations_total = attestations.length;

  log(`  Guardian ETH address: ${guardianEthAddress}`);
  log(`  Chain ID            : ${chainId}`);
  log(`  Attestations        : ${attestations.length}`);

  if (!ETH_RPC_URL) {
    result.critical_errors.push('ETH_RPC_URL not configured');
    err('❌ ETH_RPC_URL not set');
    writeOutput(result); process.exit(1);
  }

  // 2. Primary witness from evidence-manifest.json
  log('\n── Primary ETH Witness ──\n');
  const evidenceManifest = readRepoJson(EVIDENCE_MANIFEST_FILE);
  if (evidenceManifest?.eth_mirror_tx) {
    const primaryTxHash = evidenceManifest.eth_mirror_tx;
    const primaryDetail = {
      tx_hash: primaryTxHash, label: 'primary-eth-witness',
      source: 'evidence-manifest.json',
      exists: false, receipt_success: false, from_match: false,
      input_sha256_match: null, input_size_match: null,
      block_confirmed: false, error: null,
    };

    try {
      const txResult = await tryEthCallRaw('eth_getTransactionByHash', [primaryTxHash]);
      if (txResult.error || !txResult.result) {
        primaryDetail.error = `tx fetch failed: ${txResult.error}`;
      } else {
        const tx = txResult.result;
        primaryDetail.exists = true;

        if (tx.from && guardianEthAddress) {
          primaryDetail.from_match = tx.from.toLowerCase() === guardianEthAddress.toLowerCase();
        }

        const inputData = tx.input || tx.data || '0x';
        if (inputData && inputData !== '0x') {
          const inputBytes = Buffer.from(inputData.slice(2), 'hex');
          // Check if authority has matching attestation with sha256
          const matchingAtt = attestations.find(a => a.tx_hash?.toLowerCase() === primaryTxHash.toLowerCase());
          if (matchingAtt?.input_sha256) {
            const inputSha = sha256hex(inputBytes);
            primaryDetail.input_sha256_match = inputSha === matchingAtt.input_sha256.toLowerCase();
          }
          if (matchingAtt?.input_len) {
            primaryDetail.input_size_match = inputBytes.length === matchingAtt.input_len;
          }
        }

        const receiptResult = await tryEthCallRaw('eth_getTransactionReceipt', [primaryTxHash]);
        if (receiptResult.result) {
          primaryDetail.receipt_success = receiptResult.result.status === '0x1';
          primaryDetail.block_confirmed = !!receiptResult.result.blockNumber;
        }
      }

      primaryDetail.pass = primaryDetail.exists && primaryDetail.receipt_success
        && primaryDetail.from_match && primaryDetail.block_confirmed
        && (primaryDetail.input_sha256_match === true || primaryDetail.input_sha256_match === null)
        && (primaryDetail.input_size_match === true || primaryDetail.input_size_match === null);

      result.primary_eth_witness_pass = primaryDetail.pass;
      log(`  Primary witness tx: ${primaryTxHash.slice(0, 20)}...`);
      log(`  exists: ${primaryDetail.exists}, receipt: ${primaryDetail.receipt_success}, from: ${primaryDetail.from_match}`);
      log(`  input_sha256: ${primaryDetail.input_sha256_match}, input_size: ${primaryDetail.input_size_match}`);
      log(`  Primary witness pass: ${primaryDetail.pass}`);

    } catch (e) {
      primaryDetail.error = e.message;
      result.critical_errors.push(`Primary witness: ${e.message}`);
    }
    result.primary_witness = primaryDetail;
  } else {
    result.critical_errors.push('No eth_mirror_tx in evidence-manifest.json');
    log('  ⚠️ No primary witness tx found');
  }

  // 3. Auxiliary attestations
  log('\n── Auxiliary ETH Attestations ──\n');
  for (let i = 0; i < attestations.length; i++) {
    const att = attestations[i];
    const txHash = att.tx_hash;
    const detail = {
      tx_hash: txHash,
      label: att.label || `attestation-${i}`,
      exists: false, receipt_success: false, chain_id_match: false,
      from_match: false, input_sha256_match: false, input_size_match: false,
      block_confirmed: false, error: null,
    };

    try {
      if (!txHash) { detail.error = 'No tx_hash'; result.eth_attestations_fail++; result.attestation_details.push(detail); continue; }

      const txResult = await tryEthCallRaw('eth_getTransactionByHash', [txHash]);
      if (txResult.error || !txResult.result) {
        detail.error = `tx fetch failed: ${txResult.error}`;
        result.eth_attestations_fail++;
        result.attestation_details.push(detail);
        continue;
      }

      const tx = txResult.result;
      detail.exists = true;
      const txChainId = tx.chainId ? parseInt(tx.chainId, 16) : null;
      detail.chain_id_match = txChainId === chainId || txChainId === 1;

      if (tx.from && guardianEthAddress) {
        detail.from_match = tx.from.toLowerCase() === guardianEthAddress.toLowerCase();
        if (detail.from_match) result.tx_from_match++;
      }

      const inputData = tx.input || tx.data || '0x';
      if (inputData && inputData !== '0x') {
        const inputBytes = Buffer.from(inputData.slice(2), 'hex');
        if (att.input_sha256) {
          const inputSha = sha256hex(inputBytes);
          detail.input_sha256_match = inputSha === att.input_sha256.toLowerCase();
          if (detail.input_sha256_match) result.tx_input_sha256_match++;
        } else { detail.input_sha256_match = null; }
        if (att.input_len) {
          detail.input_size_match = inputBytes.length === att.input_len;
          if (detail.input_size_match) result.tx_input_size_match++;
        } else { detail.input_size_match = null; }
      }

      const receiptResult = await tryEthCallRaw('eth_getTransactionReceipt', [txHash]);
      if (receiptResult.result) {
        detail.receipt_success = receiptResult.result.status === '0x1';
        if (detail.receipt_success) result.receipt_success++;
        if (receiptResult.result.blockNumber) detail.block_confirmed = true;
      }

      const attPass = detail.exists && detail.receipt_success && detail.chain_id_match
        && detail.from_match && detail.block_confirmed
        && (detail.input_sha256_match === true || detail.input_sha256_match === null)
        && (detail.input_size_match === true || detail.input_size_match === null);

      if (attPass) result.eth_attestations_pass++;
      else result.eth_attestations_fail++;

      log(`  [${i}] ${detail.label}: exists=${detail.exists} receipt=${detail.receipt_success} from=${detail.from_match} sha256=${detail.input_sha256_match} size=${detail.input_size_match} → ${attPass ? 'PASS' : 'FAIL'}`);

    } catch (e) {
      detail.error = e.message;
      result.eth_attestations_fail++;
      result.critical_errors.push(`Attestation ${i}: ${e.message}`);
    }
    result.attestation_details.push(detail);
  }

  // 4. Overall pass
  result.eth_witness_coverage_pass =
    result.primary_eth_witness_pass &&
    result.eth_attestations_total > 0 &&
    result.eth_attestations_fail === 0;

  log(`\n  Primary witness pass  : ${result.primary_eth_witness_pass}`);
  log(`  Attestations pass     : ${result.eth_attestations_pass}`);
  log(`  Attestations fail     : ${result.eth_attestations_fail}`);
  log(`  Chain C pass          : ${result.eth_witness_coverage_pass}`);

  writeOutput(result);

  if (!result.eth_witness_coverage_pass) {
    err('\n  ❌ ETH WITNESS VERIFICATION FAILED');
    for (const e of result.critical_errors) err(`    ❌ ${e}`);
    process.exit(1);
  }
  log('\n  ✅ ETH witness verification passed.');
}

function writeOutput(result) {
  const outPath = path.join(process.cwd(), 'ETH-WITNESS-AUDIT.json');
  const audit = {
    schema: 'trinity-accord.eth-witness-audit.v1',
    generated_at: new Date().toISOString(),
    ...result,
  };
  fs.writeFileSync(outPath, JSON.stringify(audit, null, 2));
  log(`\n📝 ${outPath} written`);
}

main().catch(e => { err('Fatal:', e.message || e); if (e.stack) err(e.stack); process.exit(1); });
