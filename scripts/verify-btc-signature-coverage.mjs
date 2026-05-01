#!/usr/bin/env node
/**
 * verify-btc-signature-coverage.mjs  (Step 3)
 *
 * BTC BIP340 / Taproot signature coverage verification for Trinity Accord.
 *
 * Proves:
 *   - btc-signature.json method == bip340-taproot-xonly
 *   - BIP340 Schnorr signature is valid
 *   - authority.jcs.json sha256 == btc-signature.message_sha256
 *   - x-only pubkey derives Taproot P2TR address matching declared address
 *   - authority declares digest-manifest.json/csv pointers with sha256 + size
 *   - actual digest-manifest files match authority declarations
 *
 * Does NOT verify: DAG, ETH witness, OTS, Bitcoin tx anchors.
 *
 * Output: BTC-SIGNATURE-COVERAGE-AUDIT.json
 *
 * Usage:
 *   node scripts/verify-btc-signature-coverage.mjs
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

// ═══════════════════════════════════════════════════════════════════════════
// CONFIG
// ═══════════════════════════════════════════════════════════════════════════

const BTC_SIG_FILE = 'archive/btc-signature/btc-signature.json';
const AUTHORITY_JCS_FILE = 'archive/authority-manifest/authority.jcs.json';
const DIGEST_MANIFEST_JSON = 'archive/evidence/digest-manifest.json';
const DIGEST_MANIFEST_CSV = 'archive/evidence/digest-manifest.csv';

// secp256k1 constants for BIP-340
const SECP256K1_P  = BigInt('0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F');
const SECP256K1_N  = BigInt('0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141');
const SECP256K1_GX = BigInt('0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798');
const SECP256K1_GY = BigInt('0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8');
const SECP256K1_B  = 7n;

function log(msg) { console.log(msg); }
function err(msg) { console.error(msg); }
function sha256hex(buf) { return crypto.createHash('sha256').update(buf).digest('hex'); }
function sha256buf(buf) { return crypto.createHash('sha256').update(buf).digest(); }

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
// secp256k1 — BIP-340 Schnorr verification
// ═══════════════════════════════════════════════════════════════════════════

function mod(a, m) { const r = a % m; return r >= 0n ? r : r + m; }
function modPow(base, exp, m) {
  let result = 1n; base = mod(base, m);
  while (exp > 0n) { if (exp & 1n) result = mod(result * base, m); exp >>= 1n; base = mod(base * base, m); }
  return result;
}
function modInv(a, m) {
  let [old_r, r] = [a, m]; let [old_s, s] = [1n, 0n];
  while (r !== 0n) { const q = old_r / r; [old_r, r] = [r, old_r - q * r]; [old_s, s] = [s, old_s - q * s]; }
  return mod(old_s, m);
}
function sqrtMod(n, p) {
  if (modPow(n, (p - 1n) / 2n, p) !== 1n) return null;
  return modPow(n, (p + 1n) / 4n, p);
}

class ECPoint {
  constructor(x, y) { this.x = x; this.y = y; }
  static infinity() { return new ECPoint(null, null); }
  get isInfinity() { return this.x === null; }
}

function ecAdd(P, Q) {
  if (P.isInfinity) return Q;
  if (Q.isInfinity) return P;
  if (P.x === Q.x && P.y !== Q.y) return ECPoint.infinity();
  let lam;
  if (P.x === Q.x && P.y === Q.y)
    lam = mod(3n * P.x * P.x * modInv(mod(2n * P.y, SECP256K1_P), SECP256K1_P), SECP256K1_P);
  else
    lam = mod((Q.y - P.y) * modInv(mod(Q.x - P.x, SECP256K1_P), SECP256K1_P), SECP256K1_P);
  const x = mod(lam * lam - P.x - Q.x, SECP256K1_P);
  const y = mod(lam * (P.x - x) - P.y, SECP256K1_P);
  return new ECPoint(x, y);
}

function ecMul(k, P) {
  let result = ECPoint.infinity(), addend = P;
  while (k > 0n) { if (k & 1n) result = ecAdd(result, addend); addend = ecAdd(addend, addend); k >>= 1n; }
  return result;
}

const G = new ECPoint(SECP256K1_GX, SECP256K1_GY);

function taggedHash(tag, data) {
  const tagHash = sha256buf(Buffer.from(tag, 'utf-8'));
  return sha256buf(Buffer.concat([tagHash, tagHash, data]));
}

function verifyBip340(pubkeyXonly, msg, sig) {
  const P_x = BigInt('0x' + pubkeyXonly.toString('hex'));
  if (P_x === 0n || P_x >= SECP256K1_P) return false;
  const P_y_sq = mod(P_x * P_x * P_x + SECP256K1_B, SECP256K1_P);
  const P_y = sqrtMod(P_y_sq, SECP256K1_P);
  if (P_y === null) return false;
  const P = new ECPoint(P_x, P_y % 2n === 0n ? P_y : mod(-P_y, SECP256K1_P));
  const R_x = BigInt('0x' + sig.slice(0, 32).toString('hex'));
  const s   = BigInt('0x' + sig.slice(32, 64).toString('hex'));
  if (R_x >= SECP256K1_P || s >= SECP256K1_N) return false;
  const eInput = Buffer.concat([sig.slice(0, 32), pubkeyXonly, msg]);
  const eHash  = taggedHash('BIP0340/challenge', eInput);
  const e      = mod(BigInt('0x' + eHash.toString('hex')), SECP256K1_N);
  const sG = ecMul(s, G);
  const eP = ecMul(e, P);
  const negEP = new ECPoint(eP.x, mod(-eP.y, SECP256K1_P));
  const Rprime = ecAdd(sG, negEP);
  if (Rprime.isInfinity) return false;
  if (Rprime.y % 2n !== 0n) return false;
  if (Rprime.x !== R_x) return false;
  return true;
}

// ═══════════════════════════════════════════════════════════════════════════
// bech32m encoding (BIP-350)
// ═══════════════════════════════════════════════════════════════════════════

const BECH32M_CHARSET = 'qpzry9x8gf2tvdw0s3jn54khce6mua7l';

function bech32mPolymod(values) {
  const GEN = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3];
  let chk = 1;
  for (const v of values) {
    const b = chk >> 25;
    chk = ((chk & 0x1ffffff) << 5) ^ v;
    for (let i = 0; i < 5; i++) chk ^= ((b >> i) & 1) ? GEN[i] : 0;
  }
  return chk;
}

function bech32mHrpExpand(hrp) {
  const ret = [];
  for (let i = 0; i < hrp.length; i++) ret.push(hrp.charCodeAt(i) >> 5);
  ret.push(0);
  for (let i = 0; i < hrp.length; i++) ret.push(hrp.charCodeAt(i) & 31);
  return ret;
}

function bech32mCreateChecksum(hrp, data) {
  const values = [...bech32mHrpExpand(hrp), ...data, 0, 0, 0, 0, 0, 0];
  const mod = bech32mPolymod(values) ^ 0x2bc830a3;
  const ret = [];
  for (let i = 0; i < 6; i++) ret.push((mod >> (5 * (5 - i))) & 31);
  return ret;
}

function bech32mEncode(hrp, witver, witprog) {
  const data = [witver];
  let acc = 0, bits = 0;
  for (const byte of witprog) {
    acc = (acc << 8) | byte;
    bits += 8;
    while (bits >= 5) { data.push((acc >> (bits - 5)) & 31); bits -= 5; }
  }
  if (bits > 0) data.push((acc << (5 - bits)) & 31);
  const checksum = bech32mCreateChecksum(hrp, data);
  let result = hrp + '1';
  for (const d of [...data, ...checksum]) result += BECH32M_CHARSET[d];
  return result;
}

/** Derive Taproot (P2TR) address from x-only pubkey per BIP-341/BIP-86 */
function deriveTaprootAddress(xonlyHex) {
  const xonlyBuf = BigInt('0x' + xonlyHex);
  const tweakHash = taggedHash('TapTweak', Buffer.from(xonlyHex, 'hex'));
  const P_y_sq = mod(xonlyBuf * xonlyBuf * xonlyBuf + SECP256K1_B, SECP256K1_P);
  const P_y = sqrtMod(P_y_sq, SECP256K1_P);
  if (P_y === null) return null;
  const P = new ECPoint(xonlyBuf, P_y % 2n === 0n ? P_y : mod(-P_y, SECP256K1_P));
  const t = BigInt('0x' + tweakHash.toString('hex'));
  const Q = ecAdd(P, ecMul(t, G));
  if (Q.isInfinity) return null;
  const xQ = Q.x;
  const progBuf = Buffer.alloc(32);
  let tmp = xQ;
  for (let i = 31; i >= 0; i--) { progBuf[i] = Number(tmp & 0xffn); tmp >>= 8n; }
  return bech32mEncode('bc', 1, progBuf);
}

// ═══════════════════════════════════════════════════════════════════════════
// MAIN
// ═══════════════════════════════════════════════════════════════════════════

async function main() {
  log('═══════════════════════════════════════════════════════════');
  log('  Step 3: BTC BIP340 / Taproot Signature Coverage');
  log('═══════════════════════════════════════════════════════════\n');

  const result = {
    btc_signature_valid: false,
    signature_method_match: false,
    signed_message_sha256_match: false,
    taproot_address_match: false,
    derived_address: null,
    address_derivation_method: null,
    authority_bitcoin_address_match: false,
    authority_covers_digest_manifest: false,
    digest_manifest_json_sha256_match: false,
    digest_manifest_json_size_match: false,
    digest_manifest_csv_sha256_match: false,
    digest_manifest_csv_size_match: false,
    digest_manifest_hash_anchored_by_btc_signature: false,
    btc_signature_coverage_pass: false,
    critical_errors: [],
  };

  // 1. Read btc-signature.json
  const btcSig = readRepoJson(BTC_SIG_FILE);
  if (!btcSig) {
    result.critical_errors.push('btc-signature.json not found');
    err('❌ btc-signature.json not found');
    writeOutput(result); process.exit(1);
  }

  const method = btcSig.bitcoin_signature?.method || btcSig.method;
  const address = btcSig.bitcoin_signature?.address || btcSig.address;
  const messageSha256 = btcSig.bitcoin_signature?.message_sha256 || btcSig.message_sha256;
  const pubkeyXonly = btcSig.bitcoin_signature?.pubkey_xonly || btcSig.pubkey_xonly;
  const signature = btcSig.bitcoin_signature?.signature || btcSig.signature;

  log(`  Method      : ${method}`);
  log(`  Address     : ${address}`);
  log(`  Msg SHA-256 : ${messageSha256?.slice(0, 16)}...`);

  // 2. Verify method
  result.signature_method_match = method === 'bip340-taproot-xonly';
  log(`  Method match: ${result.signature_method_match}`);

  // 3. Read authority and compute SHA-256
  const authorityRaw = readRepoFile(AUTHORITY_JCS_FILE);
  if (!authorityRaw) {
    result.critical_errors.push('authority.jcs.json not found');
    err('❌ authority.jcs.json not found');
    writeOutput(result); process.exit(1);
  }
  const authoritySha256 = sha256hex(authorityRaw);
  log(`  Authority SHA-256: ${authoritySha256.slice(0, 16)}...`);

  // 4. Compare sha256
  if (messageSha256) {
    result.signed_message_sha256_match = authoritySha256 === messageSha256.toLowerCase();
    log(`  Signed message SHA-256 match: ${result.signed_message_sha256_match}`);
  }

  // 5. Verify BIP-340 Schnorr signature
  if (pubkeyXonly && messageSha256 && signature) {
    const pubkey = Buffer.from(pubkeyXonly, 'hex');
    const msg = Buffer.from(messageSha256, 'hex');
    const sig = Buffer.from(signature, 'hex');
    if (pubkey.length === 32 && msg.length === 32 && sig.length === 64) {
      try {
        result.btc_signature_valid = verifyBip340(pubkey, msg, sig);
      } catch (e) {
        result.critical_errors.push(`BIP-340 verify error: ${e.message}`);
      }
    } else {
      result.critical_errors.push('Invalid pubkey/msg/sig lengths');
    }
  } else {
    result.critical_errors.push('Missing btc-signature fields');
  }
  log(`  BIP-340 valid: ${result.btc_signature_valid}`);

  // 6. Verify x-only pubkey → Taproot address binding
  if (address && pubkeyXonly) {
    const pubkeyBuf = Buffer.from(pubkeyXonly, 'hex');
    const pubkeyValid = pubkeyBuf.length === 32 && BigInt('0x' + pubkeyXonly) > 0n && BigInt('0x' + pubkeyXonly) < SECP256K1_P;
    if (pubkeyValid) {
      const derivedTweaked = deriveTaprootAddress(pubkeyXonly);
      const derivedDirect = bech32mEncode('bc', 1, pubkeyBuf);
      const matchesTweaked = derivedTweaked === address;
      const matchesDirect = derivedDirect === address;
      result.taproot_address_match = matchesTweaked || matchesDirect;
      result.derived_address = matchesTweaked ? derivedTweaked : derivedDirect;
      result.address_derivation_method = matchesTweaked ? 'bip341-tweaked' : matchesDirect ? 'direct-untweaked' : 'none';
      log(`  Taproot address match: ${result.taproot_address_match} (${result.address_derivation_method})`);
      if (!matchesTweaked && !matchesDirect) {
        log(`    Tweaked : ${derivedTweaked}`);
        log(`    Direct  : ${derivedDirect}`);
        log(`    Declared: ${address}`);
        result.critical_errors.push('P2TR address mismatch');
      }
    } else {
      result.taproot_address_match = false;
      result.critical_errors.push('Invalid pubkey_xonly');
    }

    // Verify against authority guardian BTC address
    const authority = readRepoJson(AUTHORITY_JCS_FILE);
    if (authority?.guardian?.btc_minter_address) {
      const authBtcAddr = authority.guardian.btc_minter_address;
      result.authority_bitcoin_address_match = address === authBtcAddr;
      if (!result.authority_bitcoin_address_match) {
        result.taproot_address_match = false;
        result.critical_errors.push(`BTC address mismatch: declared=${address}, authority=${authBtcAddr}`);
      }
      log(`  Authority BTC address match: ${result.authority_bitcoin_address_match}`);
    }
  }

  // 7. Authority covers digest-manifest
  const authority = JSON.parse(authorityRaw.toString('utf-8'));
  const arweaveDocs = authority.arweave?.documents || [];
  let declaredJson = null, declaredCsv = null;
  for (const doc of arweaveDocs) {
    const label = (doc.label || '').toLowerCase();
    if (label === 'digest-manifest.json') declaredJson = doc;
    if (label === 'digest-manifest.csv') declaredCsv = doc;
  }
  if (declaredJson && declaredCsv) result.authority_covers_digest_manifest = true;
  log(`  Authority covers digest-manifest: ${result.authority_covers_digest_manifest}`);

  // 8. Verify digest-manifest sha256 + size
  const actualJson = readRepoFile(DIGEST_MANIFEST_JSON);
  if (actualJson && declaredJson) {
    const actualJsonSha = sha256hex(actualJson);
    result.digest_manifest_json_sha256_match = declaredJson.ar_sha256 ? declaredJson.ar_sha256.toLowerCase() === actualJsonSha : false;
    result.digest_manifest_json_size_match = (declaredJson.size === actualJson.length) || (declaredJson.size_bytes === actualJson.length);
    log(`  digest-manifest.json sha256 match: ${result.digest_manifest_json_sha256_match}`);
    log(`  digest-manifest.json size match  : ${result.digest_manifest_json_size_match}`);
  } else if (!actualJson) {
    result.critical_errors.push('digest-manifest.json not found');
  }

  const actualCsv = readRepoFile(DIGEST_MANIFEST_CSV);
  if (actualCsv && declaredCsv) {
    const actualCsvSha = sha256hex(actualCsv);
    result.digest_manifest_csv_sha256_match = declaredCsv.ar_sha256 ? declaredCsv.ar_sha256.toLowerCase() === actualCsvSha : false;
    result.digest_manifest_csv_size_match = (declaredCsv.size === actualCsv.length) || (declaredCsv.size_bytes === actualCsv.length);
    log(`  digest-manifest.csv sha256 match : ${result.digest_manifest_csv_sha256_match}`);
    log(`  digest-manifest.csv size match   : ${result.digest_manifest_csv_size_match}`);
  } else if (!actualCsv) {
    result.critical_errors.push('digest-manifest.csv not found');
  }

  // 9. Hash chain
  result.digest_manifest_hash_anchored_by_btc_signature =
    result.btc_signature_valid &&
    result.signed_message_sha256_match &&
    result.authority_covers_digest_manifest &&
    result.digest_manifest_json_sha256_match &&
    result.digest_manifest_json_size_match &&
    result.digest_manifest_csv_sha256_match &&
    result.digest_manifest_csv_size_match;

  // 10. Overall pass
  result.btc_signature_coverage_pass =
    result.btc_signature_valid &&
    result.signature_method_match &&
    result.signed_message_sha256_match &&
    result.taproot_address_match &&
    result.authority_bitcoin_address_match &&
    result.authority_covers_digest_manifest &&
    result.digest_manifest_hash_anchored_by_btc_signature;

  if (declaredJson && !declaredJson.ar_sha256) {
    result.btc_signature_coverage_pass = false;
    result.critical_errors.push('authority does not declare digest-manifest.json sha256');
  }
  if (declaredCsv && !declaredCsv.ar_sha256) {
    result.btc_signature_coverage_pass = false;
    result.critical_errors.push('authority does not declare digest-manifest.csv sha256');
  }

  log(`\n  Chain B pass: ${result.btc_signature_coverage_pass}`);

  writeOutput(result);

  if (!result.btc_signature_coverage_pass) {
    err('\n  ❌ BTC SIGNATURE COVERAGE VERIFICATION FAILED');
    for (const e of result.critical_errors) err(`    ❌ ${e}`);
    process.exit(1);
  }
  log('\n  ✅ BTC signature coverage verification passed.');
}

function writeOutput(result) {
  const outPath = path.join(process.cwd(), 'BTC-SIGNATURE-COVERAGE-AUDIT.json');
  const audit = {
    schema: 'trinity-accord.btc-signature-coverage.v1',
    generated_at: new Date().toISOString(),
    ...result,
  };
  fs.writeFileSync(outPath, JSON.stringify(audit, null, 2));
  log(`\n📝 ${outPath} written`);
}

main().catch(e => { err('Fatal:', e.message || e); if (e.stack) err(e.stack); process.exit(1); });
