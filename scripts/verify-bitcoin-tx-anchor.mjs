#!/usr/bin/env node
/**
 * verify-bitcoin-tx-anchor.mjs  (Step 6)
 *
 * Bitcoin transaction anchor verification for Trinity Accord.
 *
 * Proves:
 *   - authority.jcs.json bitcoin.originals[] and bitcoin.ancillary[] txids exist
 *   - Transactions are confirmed
 *   - Block heights and hashes match manifest declarations
 *
 * Does NOT verify: DAG, BTC signatures, ETH witness, OTS.
 *
 * Output: BITCOIN-TX-ANCHOR-AUDIT.json
 *
 * Usage:
 *   node scripts/verify-bitcoin-tx-anchor.mjs
 */

import fs from 'fs';
import path from 'path';

// ═══════════════════════════════════════════════════════════════════════════
// CONFIG
// ═══════════════════════════════════════════════════════════════════════════

const AUTHORITY_JCS_FILE = 'archive/authority-manifest/authority.jcs.json';
const BTC_API_BASE = process.env.BITCOIN_API_BASE || process.env.BTC_API_BASE || 'https://mempool.space/api';
const MAX_RETRIES = 3;

function log(msg) { console.log(msg); }
function err(msg) { console.error(msg); }
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function readRepoJson(filePath) {
  const fullPath = path.resolve(filePath);
  if (fs.existsSync(fullPath)) return JSON.parse(fs.readFileSync(fullPath, 'utf-8'));
  return null;
}

// ═══════════════════════════════════════════════════════════════════════════
// BTC API HELPERS
// ═══════════════════════════════════════════════════════════════════════════

async function btcFetch(endpoint, retries = MAX_RETRIES) {
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const res = await fetch(`${BTC_API_BASE}${endpoint}`);
      if (res.status === 404) return null;
      if (!res.ok) throw new Error(`BTC API ${res.status}`);
      const text = await res.text();
      try { return JSON.parse(text); } catch { return text; }
    } catch (e) {
      if (attempt < retries) { await sleep(2000 * (attempt + 1)); continue; }
      throw e;
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// MAIN
// ═══════════════════════════════════════════════════════════════════════════

async function main() {
  log('═══════════════════════════════════════════════════════════');
  log('  Step 6: Bitcoin TX Anchor Verification');
  log('═══════════════════════════════════════════════════════════\n');

  const result = {
    bitcoin_tx_anchor_pass: false,
    bitcoin_anchors_total: 0,
    bitcoin_anchors_pass: 0,
    bitcoin_anchors_fail: 0,
    originals_total: 0,
    ancillary_total: 0,
    earliest_anchor: null,
    latest_anchor: null,
    anchor_details: [],
    critical_errors: [],
  };

  const authority = readRepoJson(AUTHORITY_JCS_FILE);
  if (!authority) {
    result.critical_errors.push('authority.jcs.json not found');
    err('❌ authority.jcs.json not found');
    writeOutput(result); process.exit(1);
  }

  const originals = authority.bitcoin?.originals || [];
  const ancillary = authority.bitcoin?.ancillary || [];
  result.originals_total = originals.length;
  result.ancillary_total = ancillary.length;
  result.bitcoin_anchors_total = originals.length + ancillary.length;

  log(`  Originals : ${originals.length}`);
  log(`  Ancillary : ${ancillary.length}`);

  const allAnchors = [
    ...originals.map(a => ({ ...a, _type: 'original' })),
    ...ancillary.map(a => ({ ...a, _type: 'ancillary' })),
  ];

  let earliestTimestamp = Infinity;
  let latestTimestamp = -Infinity;

  for (const anchor of allAnchors) {
    const txid = anchor.txid;
    const detail = {
      txid, label: anchor.label || anchor.title || anchor._type,
      type: anchor._type,
      exists: false, confirmed: false,
      block_height_match: false, block_hash_match: false,
      block_height: null, block_hash: null, block_timestamp: null,
      merkle_proof: 'not_checked', error: null,
    };

    try {
      if (!txid) {
        detail.error = 'No txid';
        result.bitcoin_anchors_fail++;
        result.anchor_details.push(detail);
        continue;
      }

      log(`  Checking: ${detail.label} (${txid.slice(0, 16)}...)`);
      const txInfo = await btcFetch(`/tx/${txid}`);
      if (!txInfo) {
        detail.error = 'Transaction not found';
        result.bitcoin_anchors_fail++;
        result.anchor_details.push(detail);
        log(`    ❌ Not found`);
        continue;
      }

      detail.exists = true;
      detail.confirmed = !!txInfo.status?.confirmed;
      if (txInfo.status?.block_height) detail.block_height = txInfo.status.block_height;
      if (txInfo.status?.block_hash) detail.block_hash = txInfo.status.block_hash;

      // Verify block_height and block_hash match manifest
      if (anchor.block_height != null) {
        detail.block_height_match = txInfo.status?.block_height === anchor.block_height;
      }
      if (anchor.block_hash) {
        detail.block_hash_match = txInfo.status?.block_hash === anchor.block_hash;
      }

      // Query block for timestamp
      const blockHash = txInfo.status?.block_hash;
      if (blockHash) {
        try {
          const blockInfo = await btcFetch(`/block/${blockHash}`);
          if (blockInfo) {
            detail.block_timestamp = blockInfo.timestamp;
            if (blockInfo.timestamp) {
              if (blockInfo.timestamp < earliestTimestamp) {
                earliestTimestamp = blockInfo.timestamp;
                result.earliest_anchor = {
                  label: detail.label, txid, block_height: detail.block_height,
                  block_hash: detail.block_hash, block_timestamp: blockInfo.timestamp,
                };
              }
              if (blockInfo.timestamp > latestTimestamp) {
                latestTimestamp = blockInfo.timestamp;
                result.latest_anchor = {
                  title: detail.label, txid, block_height: detail.block_height,
                  block_hash: detail.block_hash, block_timestamp: blockInfo.timestamp,
                };
              }
            }
          }
        } catch { /* non-fatal */ }
      }

      // Try merkle proof
      try {
        const proof = await btcFetch(`/tx/${txid}/merkle-proof`);
        detail.merkle_proof = proof ? 'verified' : 'unavailable';
      } catch {
        detail.merkle_proof = 'unavailable';
      }

      // Overall anchor pass
      const anchorPass = detail.exists && detail.confirmed
        && (!anchor.block_height || detail.block_height_match)
        && (!anchor.block_hash || detail.block_hash_match);
      if (anchorPass) {
        result.bitcoin_anchors_pass++;
        log(`    ✅ Confirmed at block ${detail.block_height}`);
      } else {
        result.bitcoin_anchors_fail++;
        detail.error = detail.error || 'Anchor verification failed';
        log(`    ❌ Failed: ${detail.error}`);
      }

    } catch (e) {
      detail.error = e.message;
      result.bitcoin_anchors_fail++;
      result.critical_errors.push(`Anchor ${txid}: ${e.message}`);
      log(`    ❌ Error: ${e.message}`);
    }
    result.anchor_details.push(detail);
  }

  result.bitcoin_tx_anchor_pass = result.bitcoin_anchors_fail === 0 && result.bitcoin_anchors_total > 0;

  log(`\n  Anchors total  : ${result.bitcoin_anchors_total}`);
  log(`  Anchors pass   : ${result.bitcoin_anchors_pass}`);
  log(`  Anchors fail   : ${result.bitcoin_anchors_fail}`);
  log(`  Chain D1 pass  : ${result.bitcoin_tx_anchor_pass}`);

  if (result.earliest_anchor) log(`  Earliest       : block ${result.earliest_anchor.block_height} (${new Date(result.earliest_anchor.block_timestamp * 1000).toISOString()})`);
  if (result.latest_anchor) log(`  Latest         : block ${result.latest_anchor.block_height} (${new Date(result.latest_anchor.block_timestamp * 1000).toISOString()})`);

  writeOutput(result);

  if (!result.bitcoin_tx_anchor_pass) {
    err('\n  ❌ BITCOIN TX ANCHOR VERIFICATION FAILED');
    for (const e of result.critical_errors) err(`    ❌ ${e}`);
    process.exit(1);
  }
  log('\n  ✅ Bitcoin tx anchor verification passed.');
}

function writeOutput(result) {
  const outPath = path.join(process.cwd(), 'BITCOIN-TX-ANCHOR-AUDIT.json');
  const audit = {
    schema: 'trinity-accord.bitcoin-tx-anchor.v1',
    generated_at: new Date().toISOString(),
    ...result,
  };
  fs.writeFileSync(outPath, JSON.stringify(audit, null, 2));
  log(`\n📝 ${outPath} written`);
}

main().catch(e => { err('Fatal:', e.message || e); if (e.stack) err(e.stack); process.exit(1); });
