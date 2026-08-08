#!/usr/bin/env node
/**
 * Offline Bitcoin inscription proof verification.
 *
 * This compatibility entrypoint now consumes the proof-carrying annex. It does
 * not infer verification from explorer/API responses and does not use a
 * network connection. Capture and provider cross-observation are handled by
 * the annex's separate capture_proofs.py program.
 *
 * Output: BITCOIN-TX-ANCHOR-AUDIT.json
 */

import fs from 'fs';
import path from 'path';
import { runBitcoinInscriptionOfflineVerification } from './bitcoin-inscription-offline-adapter.mjs';

function log(message) { console.log(message); }

function main() {
  log('═══════════════════════════════════════════════════════════');
  log('  Bitcoin Inscription Offline Cryptographic Verification');
  log('═══════════════════════════════════════════════════════════\n');

  const result = runBitcoinInscriptionOfflineVerification();
  const audit = {
    schema: 'trinity-accord.bitcoin-tx-anchor.v2',
    generated_at: new Date().toISOString(),
    ...result,
  };
  const outputPath = path.join(process.cwd(), 'BITCOIN-TX-ANCHOR-AUDIT.json');
  fs.writeFileSync(outputPath, `${JSON.stringify(audit, null, 2)}\n`);

  log(`  Verification mode : ${result.verification_mode}`);
  log(`  Network required  : ${result.network_required_for_verification}`);
  log(`  Anchors            : ${result.bitcoin_anchors_pass}/${result.bitcoin_anchors_total}`);
  log(`  BIP340 signatures  : ${result.bip340_tapscript_signatures || 0}`);
  log(`  BIP141 commitments : ${result.witness_commitment_verified_count || 0}`);
  log(`  Valid PoW headers  : ${result.valid_pow_headers || 0}`);
  log(`  Result             : ${result.bitcoin_tx_anchor_pass ? 'PASS' : 'FAIL'}`);
  log(`\n📝 ${outputPath} written`);

  if (!result.bitcoin_tx_anchor_pass) {
    for (const error of result.critical_errors) console.error(`  ❌ ${error}`);
    process.exit(1);
  }
  log('\n  ✅ Bitcoin inscription proof annex passed offline.');
}

try {
  main();
} catch (error) {
  console.error(`Fatal: ${error.message || error}`);
  process.exit(1);
}
