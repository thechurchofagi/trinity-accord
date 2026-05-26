#!/usr/bin/env node
/**
 * Verify Guardian Ed25519 signature over signed_message.
 *
 * This verifies ONLY the cryptographic signature.
 * It does NOT determine active registered Guardian status.
 *
 * Usage:
 *   node scripts/verify_guardian_signature.mjs --proof guardian-proof.json
 *
 * Output: GUARDIAN_SIGNATURE_OK or error
 *
 * WARNING: Valid signature alone is not active registered Guardian.
 * Use verify_guardian_status.py for full status verification.
 */
import { createHash, verify } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

function parseArgs() {
  const args = process.argv.slice(2);
  const parsed = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--proof") parsed.proof = args[++i];
    else if (args[i] === "--signed-message") parsed.signedMessage = args[++i];
    else if (args[i] === "--public-key") parsed.publicKey = args[++i];
    else if (args[i] === "--signature") parsed.signature = args[++i];
  }
  return parsed;
}

function normalizePem(pem) {
  return String(pem).trim() + "\n";
}

function sha256Hex(text) {
  return createHash("sha256").update(text, "utf8").digest("hex");
}

function main() {
  const opts = parseArgs();

  let signedMessage, publicKeyPem, signatureBase64;

  if (opts.proof) {
    // Read from proof JSON file
    const proof = JSON.parse(readFileSync(resolve(opts.proof), "utf-8"));
    signedMessage = proof.signed_message;
    publicKeyPem = proof.public_key_pem;
    signatureBase64 = proof.signature_base64;
  } else if (opts.signedMessage && opts.publicKey && opts.signature) {
    // Read from individual arguments
    signedMessage = opts.signedMessage;
    publicKeyPem = readFileSync(resolve(opts.publicKey), "utf-8");
    signatureBase64 = opts.signature;
  } else {
    console.error("Usage: node verify_guardian_signature.mjs --proof <guardian-proof.json>");
    console.error("   or: node verify_guardian_signature.mjs --signed-message <msg> --public-key <file> --signature <base64>");
    process.exit(1);
  }

  if (!signedMessage || !publicKeyPem || !signatureBase64) {
    console.error("ERROR: Missing required fields in proof (signed_message, public_key_pem, signature_base64)");
    process.exit(1);
  }

  // Verify public key hash
  const normalizedPem = normalizePem(publicKeyPem);
  const computedSha = sha256Hex(normalizedPem);

  let ok = false;
  try {
    ok = verify(
      null,
      Buffer.from(signedMessage, "utf8"),
      normalizedPem,
      Buffer.from(signatureBase64, "base64")
    );
  } catch (err) {
    console.error(`GUARDIAN_SIGNATURE_ERROR: ${err.message}`);
    process.exit(1);
  }

  if (ok) {
    console.log("GUARDIAN_SIGNATURE_OK");
    console.log(`public_key_sha256: ${computedSha}`);
    process.exit(0);
  } else {
    console.error("GUARDIAN_SIGNATURE_INVALID");
    process.exit(1);
  }
}

main();
