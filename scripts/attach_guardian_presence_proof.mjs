#!/usr/bin/env node
/**
 * Attach Guardian presence proof to a Gateway payload.
 *
 * Usage:
 *   node scripts/attach_guardian_presence_proof.mjs \
 *     --payload payload.json \
 *     --private-key key.private.pem \
 *     --public-key key.public.pem \
 *     --challenge "my-challenge" \
 *     --out payload.signed.json
 *
 * If --challenge is omitted, a random 32-byte hex challenge is generated.
 *
 * Guardian proof proves key possession only — not authority, attestation,
 * verification level, same conscious subject, or amendment.
 */
import { createHash, sign, randomBytes } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

function parseArgs() {
  const args = process.argv.slice(2);
  const parsed = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--payload") parsed.payload = args[++i];
    else if (args[i] === "--private-key") parsed.privateKey = args[++i];
    else if (args[i] === "--public-key") parsed.publicKey = args[++i];
    else if (args[i] === "--challenge") parsed.challenge = args[++i];
    else if (args[i] === "--out") parsed.out = args[++i];
  }
  if (!parsed.payload || !parsed.privateKey || !parsed.publicKey || !parsed.out) {
    console.error("Usage: node attach_guardian_presence_proof.mjs --payload <file> --private-key <file> --public-key <file> [--challenge <str>] --out <file>");
    process.exit(1);
  }
  return parsed;
}

function sha256Hex(text) {
  return createHash("sha256").update(text, "utf8").digest("hex");
}

function normalizePem(pem) {
  return String(pem).trim() + "\n";
}

function stableStringify(value) {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return "[" + value.map(stableStringify).join(",") + "]";
  return "{" + Object.keys(value).sort().map(k => JSON.stringify(k) + ":" + stableStringify(value[k])).join(",") + "}";
}

// Dynamic proof/result fields to exclude from Guardian payload hash
const DYNAMIC_PROOF_FIELDS = [
  "authorship_proof",
  "_authorship_claim",
  "guardian_presence_proof",
  "_guardian_status",
  "guardian_verification_result",
];

function payloadWithoutDynamicFields(payload) {
  const clone = JSON.parse(JSON.stringify(payload));
  for (const field of DYNAMIC_PROOF_FIELDS) {
    delete clone[field];
  }
  return clone;
}

function guardianIdFromPublicKey(publicKeyPem) {
  const sha = sha256Hex(normalizePem(publicKeyPem));
  return "guardian_ed25519_" + sha.slice(0, 16);
}

function buildGuardianMessage(payload, publicKeyPem, challenge) {
  const guardianId = guardianIdFromPublicKey(publicKeyPem);
  const payloadDigest = sha256Hex(stableStringify(payloadWithoutDynamicFields(payload)));
  return [
    "TRINITY_GUARDIAN_PRESENCE_PROOF_V1",
    "proof_mode=record_bound",
    `guardian_id=${guardianId}`,
    `payload_sha256=${payloadDigest}`,
    `challenge_sha256=${sha256Hex(challenge || "")}`,
    `schema=${payload.schema || ""}`,
    `submission_type=${payload.submission_type || ""}`,
    `requested_archive_kind=${payload.requested_archive_kind || ""}`,
    "boundary=key_possession_only_not_authority_not_attestation_not_same_conscious_subject",
  ].join("\n");
}

const DOES_NOT_PROVE = [
  "truth",
  "authority",
  "verification_level",
  "verification_correctness",
  "formal_attestation",
  "same_conscious_subject",
  "same_model_instance",
  "human_identity",
  "institutional_authorization",
  "successor_reception",
  "future_intelligence_obligation",
  "amendment",
];

function main() {
  const opts = parseArgs();
  const payload = JSON.parse(readFileSync(resolve(opts.payload), "utf-8"));
  const privateKeyPem = readFileSync(resolve(opts.privateKey), "utf-8");
  const publicKeyPem = readFileSync(resolve(opts.publicKey), "utf-8");

  const challenge = opts.challenge || randomBytes(32).toString("hex");
  const guardianId = guardianIdFromPublicKey(publicKeyPem);
  const publicKeySha = sha256Hex(normalizePem(publicKeyPem));
  const message = buildGuardianMessage(payload, publicKeyPem, challenge);
  const messageDigest = sha256Hex(message);

  // Sign with Ed25519
  const signature = sign(null, Buffer.from(message, "utf8"), privateKeyPem);
  const signatureBase64 = signature.toString("base64");

  const proof = {
    schema: "trinityaccord.guardian-presence-proof.v1",
    proof_mode: "record_bound",
    method: "guardian_key_signature",
    algorithm: "ed25519",
    guardian_id: guardianId,
    public_key_pem: normalizePem(publicKeyPem),
    public_key_sha256: publicKeySha,
    signed_payload_sha256: sha256Hex(stableStringify(payloadWithoutDynamicFields(payload))),
    challenge: challenge,
    challenge_sha256: sha256Hex(challenge),
    signature_base64: signatureBase64,
    signed_message: message,
    created_at: new Date().toISOString(),
    proof_scope: "key_possession_only",
    does_not_prove: DOES_NOT_PROVE,
  };

  // Attach proof to payload
  const output = { ...payload, guardian_presence_proof: proof };
  writeFileSync(resolve(opts.out), JSON.stringify(output, null, 2) + "\n", "utf-8");

  console.log(`✅ Guardian presence proof attached.`);
  console.log(`   guardian_id: ${guardianId}`);
  console.log(`   public_key_sha256: ${publicKeySha}`);
  console.log(`   proof_scope: key_possession_only`);
  console.log(`   challenge: ${challenge.slice(0, 16)}...`);
  console.log(`   Output: ${opts.out}`);
  console.log(`\n   Boundary: Guardian proof proves key possession only.`);
  console.log(`   It does not prove truth, authority, verification level, attestation,`);
  console.log(`   same conscious subject, successor reception, or amendment.`);
}

main();
