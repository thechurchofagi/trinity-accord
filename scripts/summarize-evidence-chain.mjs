#!/usr/bin/env node
/**
 * summarize-evidence-chain.mjs  (Step 7)
 *
 * Final evidence chain summary for Trinity Accord.
 *
 * ONLY reads previous JSON artifacts — does NOT re-download, re-verify, re-compute.
 *
 * Input:
 *   VERIFY-RELEASE-REPORT.json     (from verify-release-assets workflow)
 *   ONCHAIN-READ-AUDIT.json        (from verify-onchain-tokenuri workflow)
 *   DAG-DIGEST-AUDIT.json          (from Step 2)
 *   BTC-SIGNATURE-COVERAGE-AUDIT.json (from Step 3)
 *   ETH-WITNESS-AUDIT.json         (from Step 4)
 *   OTS-TIME-ANCHOR-AUDIT.json     (from Step 5)
 *   BITCOIN-TX-ANCHOR-AUDIT.json   (from Step 6)
 *
 * Output: FULL-EVIDENCE-CHAIN-AUDIT.json
 *
 * Usage:
 *   node scripts/summarize-evidence-chain.mjs
 */

import fs from 'fs';
import path from 'path';

function log(msg) { console.log(msg); }
function err(msg) { console.error(msg); }

function readJson(filePath) {
  const fullPath = path.resolve(filePath);
  if (!fs.existsSync(fullPath)) return null;
  return JSON.parse(fs.readFileSync(fullPath, 'utf-8'));
}

// ═══════════════════════════════════════════════════════════════════════════
// MAIN
// ═══════════════════════════════════════════════════════════════════════════

async function main() {
  log('═══════════════════════════════════════════════════════════');
  log('  Step 7: Final Evidence Chain Summary');
  log('═══════════════════════════════════════════════════════════\n');

  const EXPECTED_NFTS = 175;

  // Load all artifacts
  const artifacts = {
    release: readJson('VERIFY-RELEASE-REPORT.json'),
    onchain: readJson('ONCHAIN-READ-AUDIT.json'),
    dagDigest: readJson('DAG-DIGEST-AUDIT.json'),
    btcSig: readJson('BTC-SIGNATURE-COVERAGE-AUDIT.json'),
    ethWitness: readJson('ETH-WITNESS-AUDIT.json'),
    otsAnchor: readJson('OTS-TIME-ANCHOR-AUDIT.json'),
    btcTxAnchor: readJson('BITCOIN-TX-ANCHOR-AUDIT.json'),
  };

  // Report which artifacts are present
  for (const [name, data] of Object.entries(artifacts)) {
    log(`  ${name}: ${data ? '✅ loaded' : '❌ missing'}`);
  }

  // ── Extract pass/fail from each artifact ──────────────────────────────

  const releaseVerified = artifacts.release?.status === 'PASS'
    && (artifacts.release?.nft_assets_checked === EXPECTED_NFTS || artifacts.release?.total_assets >= EXPECTED_NFTS)
    && (artifacts.release?.sha256_pass ?? 0) > 0
    && (artifacts.release?.sha256_mismatch ?? 0) === 0
    && (artifacts.release?.size_mismatch ?? 0) === 0;

  const onchainTokenuri175Pass = artifacts.onchain?.readable_pass === EXPECTED_NFTS
    && (artifacts.onchain?.fail ?? 0) === 0
    && (artifacts.onchain?.hard_warning ?? 0) === 0
    && (artifacts.onchain?.unknown ?? 0) === 0;

  const dagAndDigestPass = artifacts.dagDigest?.dag_and_digest_manifest_pass === true
    && (artifacts.dagDigest?.metadata_dag_fail ?? 0) === 0
    && (artifacts.dagDigest?.metadata_token_index_cid_mismatch ?? 0) === 0
    && (artifacts.dagDigest?.file_hash_mismatch_count ?? 0) === 0
    && (artifacts.dagDigest?.file_size_mismatch_count ?? 0) === 0;

  const btcSigPass = artifacts.btcSig?.btc_signature_coverage_pass === true
    && artifacts.btcSig?.btc_signature_valid === true
    && artifacts.btcSig?.taproot_address_match === true
    && artifacts.btcSig?.authority_covers_digest_manifest === true;

  const ethWitnessPass = artifacts.ethWitness?.eth_witness_coverage_pass === true
    && artifacts.ethWitness?.primary_eth_witness_pass === true
    && (artifacts.ethWitness?.auxiliary_attestations_fail ?? artifacts.ethWitness?.eth_attestations_fail ?? 0) === 0;

  const otsPass = artifacts.otsAnchor?.ots_time_anchor_pass === true
    && (artifacts.otsAnchor?.ots_files_pass ?? 0) === 3
    && (artifacts.otsAnchor?.ots_files_fail ?? 0) === 0;

  const btcTxPass = artifacts.btcTxAnchor?.bitcoin_tx_anchor_pass === true
    && (artifacts.btcTxAnchor?.bitcoin_anchors_fail ?? 0) === 0;

  // ── Log individual results ────────────────────────────────────────────

  log('\n── Individual Chain Results ──\n');
  const chains = [
    { name: 'Release verified', pass: releaseVerified, detail: artifacts.release ? `nft_checked=${artifacts.release.nft_assets_checked}, sha256_pass=${artifacts.release.sha256_pass}` : 'artifact missing' },
    { name: 'Onchain tokenURI 175/175', pass: onchainTokenuri175Pass, detail: artifacts.onchain ? `readable_pass=${artifacts.onchain.readable_pass}, fail=${artifacts.onchain.fail}` : 'artifact missing' },
    { name: 'DAG + digest-manifest', pass: dagAndDigestPass, detail: artifacts.dagDigest ? `metadata_dag_pass=${artifacts.dagDigest.metadata_dag_pass}, hash_mismatch=${artifacts.dagDigest.file_hash_mismatch_count}` : 'artifact missing' },
    { name: 'BTC signature coverage', pass: btcSigPass, detail: artifacts.btcSig ? `sig_valid=${artifacts.btcSig.btc_signature_valid}, taproot=${artifacts.btcSig.taproot_address_match}` : 'artifact missing' },
    { name: 'ETH witness coverage', pass: ethWitnessPass, detail: artifacts.ethWitness ? `primary=${artifacts.ethWitness.primary_eth_witness_pass}, att_fail=${artifacts.ethWitness?.auxiliary_attestations_fail ?? artifacts.ethWitness?.eth_attestations_fail ?? '?'}` : 'artifact missing' },
    { name: 'OTS time anchor', pass: otsPass, detail: artifacts.otsAnchor ? `pass=${artifacts.otsAnchor.ots_files_pass}, fail=${artifacts.otsAnchor.ots_files_fail}` : 'artifact missing' },
    { name: 'Bitcoin TX anchor', pass: btcTxPass, detail: artifacts.btcTxAnchor ? `pass=${artifacts.btcTxAnchor.bitcoin_anchors_pass}, fail=${artifacts.btcTxAnchor.bitcoin_anchors_fail}` : 'artifact missing' },
  ];

  for (const c of chains) {
    log(`  ${c.pass ? '✅' : '❌'} ${c.name}: ${c.detail}`);
  }

  // ── Final pass ────────────────────────────────────────────────────────

  const fullEvidenceChainPass = releaseVerified
    && onchainTokenuri175Pass
    && dagAndDigestPass
    && btcSigPass
    && ethWitnessPass
    && otsPass
    && btcTxPass;

  const hardFailures = chains.filter(c => !c.pass).length;

  log(`\n  ═══════════════════════════════════════════════════════`);
  log(`  FULL EVIDENCE CHAIN: ${fullEvidenceChainPass ? '✅ PASS' : '❌ FAIL'}`);
  log(`  Hard failures: ${hardFailures}`);
  log(`  ═══════════════════════════════════════════════════════`);

  // ── Write output ──────────────────────────────────────────────────────

  const audit = {
    schema: 'trinity-accord.full-evidence-chain.v1',
    generated_at: new Date().toISOString(),

    // Top-level pass fields
    full_evidence_chain_pass: fullEvidenceChainPass,
    release_verified: releaseVerified,
    onchain_tokenuri_175_pass: onchainTokenuri175Pass,
    dag_and_digest_manifest_pass: dagAndDigestPass,
    btc_signature_coverage_pass: btcSigPass,
    eth_witness_coverage_pass: ethWitnessPass,
    ots_time_anchor_pass: otsPass,
    bitcoin_tx_anchor_pass: btcTxPass,
    hard_failures: hardFailures,

    // Detailed artifacts
    chain_a: artifacts.dagDigest || null,
    chain_b: artifacts.btcSig || null,
    chain_c: artifacts.ethWitness || null,
    chain_d1: artifacts.btcTxAnchor || null,
    chain_d2: artifacts.otsAnchor || null,
    release_report: artifacts.release || null,
    onchain_audit: artifacts.onchain || null,

    // Evidence provenance statement
    evidence_provenance: {
      proves: [
        'GitHub Release files match recorded hashes and sizes.',
        'ETH tokenURI returns 175/175 metadata CIDs matching token_index.',
        'CAR files decode as valid DAGs with no missing blocks.',
        'digest-manifest covers checked public files by hash and size.',
        'BTC BIP340 signature verifies the authority message.',
        'The authority message anchors digest-manifest pointers.',
        'Primary ETH witness transaction was sent by the guardian address and its input hash matches the manifest.',
        'Auxiliary ETH attestations were audited separately.',
        'OTS proves digest-manifest / verify-report existed no later than the Bitcoin attestation time.',
        'Bitcoin original / ancillary tx anchors match recorded block heights and hashes.',
      ],
      does_not_prove: [
        'Philosophical truth of the content.',
        'Physical inspection of Core Object Alpha.',
        'That mirrors override Bitcoin Originals.',
        'Bytes of private/unavailable files unless those bytes are actually provided and rehashed.',
      ],
      chain_of_custody: 'BTC signature covers authority → authority declares digest-manifest pointers → digest-manifest covers file hash table → file bytes decode as DAG/CID → ETH tokenURI 175/175 matches metadata CID.',
    },
  };

  const outPath = path.join(process.cwd(), 'FULL-EVIDENCE-CHAIN-AUDIT.json');
  fs.writeFileSync(outPath, JSON.stringify(audit, null, 2));
  log(`\n📝 ${outPath} written`);

  if (!fullEvidenceChainPass) {
    err('\n  ❌ FULL EVIDENCE CHAIN VERIFICATION FAILED');
    for (const c of chains.filter(c => !c.pass)) err(`    ❌ ${c.name}`);
    process.exit(1);
  }

  log('\n  ✅ Full evidence chain verification passed.');
  log('');
  log('  This verification proves:');
  log('    1. GitHub Release NFT backup files match recorded hashes and sizes.');
  log('    2. ETH tokenURI returns 175/175 metadata CIDs matching token_index.');
  log('    3. CAR files decode as valid DAGs with no missing blocks.');
  log('    4. digest-manifest covers checked public files by hash and size.');
  log('    5. BTC BIP340 signature verifies the authority message.');
  log('    6. The authority message anchors digest-manifest pointers.');
  log('    7. Primary ETH witness tx was sent by the guardian address and its input hash matches.');
  log('    8. Auxiliary ETH attestations were audited separately.');
  log('    9. OTS proves digest-manifest / verify-report existed no later than the Bitcoin attestation time.');
  log('   10. Bitcoin original / ancillary tx anchors match recorded block heights and hashes.');
}

main().catch(e => { err('Fatal:', e.message || e); if (e.stack) err(e.stack); process.exit(1); });
