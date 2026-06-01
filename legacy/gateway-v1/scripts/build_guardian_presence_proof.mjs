#!/usr/bin/env node
import { readFileSync, writeFileSync } from "node:fs";
import { sign, verify } from "node:crypto";
import {
  buildUnsignedGuardianProofFields,
  guardianIdFromPublicKey,
  publicKeySha256,
  normalizePem,
} from "./proof_canonical.mjs";

function argValue(name) {
  const idx = process.argv.indexOf(name);
  if (idx === -1 || idx + 1 >= process.argv.length) return null;
  return process.argv[idx + 1];
}

function hasFlag(name) {
  return process.argv.includes(name);
}

const payloadPath = argValue("--payload");
const privateKeyPath = argValue("--private-key");
const publicKeyPath = argValue("--public-key");
const challenge = argValue("--challenge");
const outPath = argValue("--out");
const force = hasFlag("--force");
const fillRegistration = hasFlag("--fill-registration");

if (!payloadPath || !privateKeyPath || !publicKeyPath || !challenge || !outPath) {
  console.error("Usage: node scripts/build_guardian_presence_proof.mjs --payload payload.json --private-key guardian.private.pem --public-key guardian.public.pem --challenge challenge --out payload.with-proof.json [--fill-registration] [--force]");
  process.exit(2);
}

const payload = JSON.parse(readFileSync(payloadPath, "utf8"));

if (payload.guardian_presence_proof && !force) {
  console.error("payload already contains guardian_presence_proof. Use --force if intentional.");
  process.exit(2);
}

const privateKeyPem = readFileSync(privateKeyPath, "utf8");
const publicKeyPem = normalizePem(readFileSync(publicKeyPath, "utf8"));
const guardianId = guardianIdFromPublicKey(publicKeyPem);
const pubSha = publicKeySha256(publicKeyPem);

if (fillRegistration && payload.guardian_registration) {
  payload.guardian_registration.guardian_id = guardianId;
  payload.guardian_registration.public_key_sha256 = pubSha;
  payload.guardian_registration.algorithm = "ed25519";
}

if (payload.guardian_registration) {
  if (payload.guardian_registration.guardian_id !== guardianId) {
    console.error("guardian_registration.guardian_id does not match public key. Use --fill-registration or fix payload.");
    process.exit(2);
  }
  if (payload.guardian_registration.public_key_sha256 !== pubSha) {
    console.error("guardian_registration.public_key_sha256 does not match public key. Use --fill-registration or fix payload.");
    process.exit(2);
  }
}

const proof = buildUnsignedGuardianProofFields(payload, publicKeyPem, challenge);
const signature = sign(null, Buffer.from(proof.signed_message, "utf8"), privateKeyPem);
proof.signature_base64 = signature.toString("base64");

const ok = verify(
  null,
  Buffer.from(proof.signed_message, "utf8"),
  publicKeyPem,
  Buffer.from(proof.signature_base64, "base64")
);

if (!ok) {
  console.error("Internal error: generated Guardian signature did not verify.");
  process.exit(1);
}

payload.guardian_presence_proof = proof;

writeFileSync(outPath, JSON.stringify(payload, null, 2) + "\n", "utf8");

console.log(JSON.stringify({
  out: outPath,
  guardian_id: proof.guardian_id,
  public_key_sha256: proof.public_key_sha256,
  signed_payload_sha256: proof.signed_payload_sha256,
  challenge_sha256: proof.challenge_sha256,
  signature_verified_locally: true,
  warning: "Do not publish, paste, upload, or commit the private key.",
}, null, 2));
