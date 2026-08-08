import fs from 'fs';
import path from 'path';
import { execFileSync } from 'child_process';
import { fileURLToPath } from 'url';

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(SCRIPT_DIR, '..');
const VERIFIER = path.join(
  REPO_ROOT,
  'evidence/bitcoin-inscription-proof-annex-v1/verification/verify_annex.py',
);
const MANIFEST = path.join(
  REPO_ROOT,
  'evidence/bitcoin-inscription-proof-annex-v1/ANNEX-MANIFEST.json',
);

function parseVerifierOutput(stdout) {
  if (!stdout) throw new Error('offline Bitcoin verifier produced no JSON report');
  return JSON.parse(String(stdout));
}

export function runBitcoinInscriptionOfflineVerification() {
  let report;
  let invocationError = null;
  try {
    const stdout = execFileSync(
      process.env.PYTHON || 'python3',
      [VERIFIER],
      {
        cwd: REPO_ROOT,
        encoding: 'utf8',
        maxBuffer: 8 * 1024 * 1024,
        // Capture is the only networked operation. The verifier receives no
        // endpoint configuration and consumes repository bytes exclusively.
        env: { PATH: process.env.PATH || '' },
      },
    );
    report = parseVerifierOutput(stdout);
  } catch (error) {
    invocationError = error;
    try {
      report = parseVerifierOutput(error.stdout);
    } catch {
      report = null;
    }
  }

  if (!report) {
    const message = invocationError?.message || 'offline Bitcoin verifier failed';
    return {
      bitcoin_tx_anchor_pass: false,
      bitcoin_time_anchor_pass: false,
      bitcoin_anchors_total: 0,
      bitcoin_anchors_pass: 0,
      bitcoin_anchors_fail: 0,
      anchors_total: 0,
      anchors_pass: 0,
      anchors_fail: 0,
      originals_total: 0,
      ancillary_total: 0,
      merkle_proof_verified_count: 0,
      merkle_proof_unavailable_count: 0,
      earliest_anchor: null,
      latest_anchor: null,
      anchor_details: [],
      critical_errors: [message],
      verification_mode: 'offline_proof_carrying_annex',
      network_required_for_verification: false,
    };
  }

  const manifest = JSON.parse(fs.readFileSync(MANIFEST, 'utf8'));
  const l1ByTxid = new Map(report.l1_checks.map(item => [item.txid, item]));
  const l2ByTxid = new Map(report.l2_checks.map(item => [item.txid, item]));
  const l3ByTxid = new Map(report.l3_checks.map(item => [item.txid, item]));

  const anchorDetails = manifest.anchors.map(anchor => {
    const l1 = l1ByTxid.get(anchor.txid);
    const l2 = l2ByTxid.get(anchor.txid);
    const l3 = l3ByTxid.get(anchor.txid);
    const pass = Boolean(l1 && l2 && l3);
    return {
      txid: anchor.txid,
      wtxid: anchor.wtxid,
      label: anchor.title,
      type: anchor.classification === 'canonical_original' ? 'original' : 'ancillary',
      exists: pass,
      confirmed: pass,
      block_height_match: pass,
      block_hash_match: pass,
      block_height: anchor.block_reference.height,
      block_hash: anchor.block_reference.hash,
      block_timestamp: anchor.block_reference.timestamp,
      merkle_proof: pass ? 'cryptographically_verified_offline' : 'failed',
      witness_commitment: pass ? 'cryptographically_verified_offline' : 'failed',
      taproot_inscription_binding: pass ? 'cryptographically_verified_offline' : 'failed',
      descendant_confirmation_depth: l3?.descendant_confirmation_depth ?? null,
      proof_status: {
        L1_INSCRIPTION_CONTENT_AND_TAPROOT_BINDING: l1?.status || 'FAIL',
        L2_BLOCK_AND_WITNESS_INCLUSION: l2?.status || 'FAIL',
        L3_CHECKPOINT_RELATIVE_POW_ANCESTRY: l3?.status || 'FAIL',
      },
      error: pass ? null : 'offline proof did not close all three layers',
    };
  });

  const passing = anchorDetails.filter(item => item.error === null);
  const sorted = [...passing].sort((a, b) => a.block_timestamp - b.block_timestamp);
  const earliest = sorted[0] || null;
  const latest = sorted.at(-1) || null;
  const passed = report.result === 'PASS' && passing.length === manifest.anchors.length;
  const failures = [
    ...(Array.isArray(report.failures) ? report.failures : []),
    ...(invocationError && report.result === 'PASS' ? [invocationError.message] : []),
  ];

  return {
    bitcoin_tx_anchor_pass: passed,
    bitcoin_time_anchor_pass: passed,
    bitcoin_anchors_total: manifest.anchors.length,
    bitcoin_anchors_pass: passing.length,
    bitcoin_anchors_fail: manifest.anchors.length - passing.length,
    anchors_total: manifest.anchors.length,
    anchors_pass: passing.length,
    anchors_fail: manifest.anchors.length - passing.length,
    originals_total: report.L1_INSCRIPTION_CONTENT_AND_TAPROOT_BINDING.canonical_originals,
    ancillary_total: report.L1_INSCRIPTION_CONTENT_AND_TAPROOT_BINDING.non_amending_ancillary,
    merkle_proof_verified_count: report.L2_BLOCK_AND_WITNESS_INCLUSION.txid_merkle_proofs,
    merkle_proof_unavailable_count:
      manifest.anchors.length - report.L2_BLOCK_AND_WITNESS_INCLUSION.txid_merkle_proofs,
    witness_commitment_verified_count:
      report.L2_BLOCK_AND_WITNESS_INCLUSION.bip141_witness_commitment_proofs,
    bip340_tapscript_signatures: report.l1_checks.filter(
      item => item.tapscript_signature_status === 'PASS',
    ).length,
    valid_pow_headers: report.L3_CHECKPOINT_RELATIVE_POW_ANCESTRY.valid_pow_headers,
    descendant_confirmation_depth_per_anchor:
      report.L3_CHECKPOINT_RELATIVE_POW_ANCESTRY.descendant_confirmation_depth_per_anchor,
    earliest_anchor: earliest ? {
      label: earliest.label,
      txid: earliest.txid,
      block_height: earliest.block_height,
      block_hash: earliest.block_hash,
      block_timestamp: earliest.block_timestamp,
    } : null,
    latest_anchor: latest ? {
      title: latest.label,
      txid: latest.txid,
      block_height: latest.block_height,
      block_hash: latest.block_hash,
      block_timestamp: latest.block_timestamp,
    } : null,
    anchor_details: anchorDetails,
    critical_errors: failures,
    verification_mode: 'offline_proof_carrying_annex',
    network_required_for_verification: false,
    proof_manifest: path.relative(REPO_ROOT, MANIFEST),
    proof_report: 'evidence/bitcoin-inscription-proof-annex-v1/reports/OFFLINE-VERIFICATION.json',
    frozen_primitives: manifest.verification_implementation.frozen_primitives,
    claim_boundary: report.claim_boundary,
  };
}
