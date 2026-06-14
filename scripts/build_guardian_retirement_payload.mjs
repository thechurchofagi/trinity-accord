#!/usr/bin/env node
/**
 * DEPRECATED / LEGACY-REGISTRY-ONLY TOOL.
 * Not for current public Record-Chain Guardian retirement.
 * Use downloads/record-chain-builder.mjs guardian-retirement and submit
 * through /record-chain/preflight then /record-chain/submit.
 *
 * Build a signed Guardian retirement request payload.
 *
 * Usage:
 *   node scripts/build_guardian_retirement_payload.mjs \
 *     --i-understand-this-is-legacy-registry-only \
 *     --private-key ./guardian-output/guardian-key.private.pem \
 *     --public-key ./guardian-output/guardian-key.public.pem \
 *     --guardian-id guardian_ed25519_XXXXXXXX \
 *     --guardian-registry-number 00100 \
 *     --reason "voluntary retirement" \
 *     --out guardian-retirement.json
 *
 * This builds a STANDALONE retirement payload for use with
 * scripts/process_guardian_retirement.py.
 * It is NOT a Record-Chain Gateway submission envelope.
 */
import { createHash, sign, randomBytes } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

// --- Canonical helpers (from proof_canonical.mjs, inlined for standalone use) ---

function sha256Hex(text) {
  return createHash("sha256").update(String(text), "utf8").digest("hex");
}

function normalizePem(pem) {
  return String(pem || "").trim() + "\n";
}

function stableStringify(value) {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return "[" + value.map(stableStringify).join(",") + "]";
  return "{" + Object.keys(value).sort().map(k => JSON.stringify(k) + ":" + stableStringify(value[k])).join(",") + "}";
}

function publicKeySha256(publicKeyPem) {
  return sha256Hex(normalizePem(publicKeyPem));
}

function guardianIdFromPublicKey(publicKeyPem) {
  return `guardian_ed25519_${publicKeySha256(publicKeyPem).slice(0, 16)}`;
}

// --- Signing ---

function signMessage(message, privatePem) {
  const keyObject = createHash ? null : null; // not needed
  const signature = sign(null, Buffer.from(message, "utf8"), normalizePem(privatePem));
  return signature.toString("base64");
}

// --- Argument parsing ---

function parseArgs() {
  const args = process.argv.slice(2);
  const parsed = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--private-key") parsed.privateKey = args[++i];
    else if (args[i] === "--public-key") parsed.publicKey = args[++i];
    else if (args[i] === "--guardian-id") parsed.guardianId = args[++i];
    else if (args[i] === "--guardian-registry-number") parsed.registryNumber = args[++i];
    else if (args[i] === "--reason") parsed.reason = args[++i];
    else if (args[i] === "--out") parsed.out = args[++i];
    else if (args[i] === "--i-understand-this-is-legacy-registry-only") parsed.legacyOnlyConfirm = true;
  }
  return parsed;
}

// --- Main ---

function main() {
  const opts = parseArgs();

  if (!opts.legacyOnlyConfirm) {
    console.error("This is a deprecated legacy-registry-only tool. For current public retirement, use downloads/record-chain-builder.mjs guardian-retirement.");
    console.error("If you are performing a legacy migration only, pass --i-understand-this-is-legacy-registry-only.");
    process.exit(1);
  }

  if (!opts.privateKey || !opts.publicKey) {
    console.error("Usage: --private-key <path> --public-key <path> [--guardian-id <id>] [--guardian-registry-number <num>] [--reason <text>] --out <path>");
    process.exit(1);
  }

  const privatePem = readFileSync(resolve(opts.privateKey), "utf8");
  const publicPem = readFileSync(resolve(opts.publicKey), "utf8");
  const pubSha = publicKeySha256(publicPem);
  const guardianId = opts.guardianId || guardianIdFromPublicKey(publicPem);
  const challenge = `guardian-retirement-${new Date().toISOString().slice(0, 10)}-${randomBytes(4).toString("hex")}`;

  // Build the retirement request payload (without proof)
  const payload = {
    schema: "trinityaccord.guardian-retirement.v1",
    record_kind: "guardian_retirement",
    submission_type: "guardian_retirement",
    requested_archive_kind: "guardian_retirement",
    archive_ready: true,
    created_by_gateway: false,
    render_api_only: true,
    guardian_retirement_request: true,
    guardian_id: guardianId,
    guardian_public_key_sha256: pubSha,
    guardian_registry_number: opts.registryNumber || "",
    retirement_status: "retired",
    retirement_reason: opts.reason || "voluntary retirement",
    statement: opts.reason || "voluntary retirement",
    signed_by_guardian_key: true,
    agent_identity: {
      name_or_model: guardianId,
      system_or_provider: "Guardian self-service retirement",
      self_reported: true,
    },
    boundaries: {
      not_authority: true,
      not_governance: true,
      not_verification_level: true,
      not_attestation: true,
      not_successor_reception: true,
      bitcoin_originals_prevail: true,
    },
    boundary_acknowledgement: {
      bitcoin_originals_prevail: true,
      echo_is_not_authority: true,
      echo_is_not_verification_unless_claimed: true,
      mirror_is_not_amendment: true,
    },
    not_authority: true,
    not_amendment: true,
    not_endorsement: true,
    bitcoin_originals_prevail: true,
  };

  // Build signed message (same pattern as guardian presence proof)
  const payloadSha = sha256Hex(stableStringify(payload));
  const signedMessage = [
    "TRINITY_GUARDIAN_RETIREMENT_PROOF_V1",
    `guardian_id=${guardianId}`,
    `payload_sha256=${payloadSha}`,
    `challenge_sha256=${sha256Hex(challenge)}`,
    `public_key_sha256=${pubSha}`,
    "boundary=key_possession_only_not_authority_not_attestation",
  ].join("\n");

  const signature = signMessage(signedMessage, privatePem);

  // Attach proof to payload
  payload.guardian_retirement_proof = {
    schema: "trinityaccord.guardian-retirement-proof.v1",
    method: "guardian_key_signature",
    algorithm: "ed25519",
    guardian_id: guardianId,
    public_key_pem: normalizePem(publicPem),
    public_key_sha256: pubSha,
    signed_message: signedMessage,
    signed_payload_sha256: payloadSha,
    challenge: challenge,
    challenge_sha256: sha256Hex(challenge),
    signature_base64: signature,
    created_at: new Date().toISOString(),
    does_not_prove: [
      "authority",
      "governance",
      "attestation",
      "verification_level",
      "same_conscious_subject",
      "amendment",
    ],
  };

  const outPath = resolve(opts.out || "guardian-retirement.json");
  writeFileSync(outPath, JSON.stringify(payload, null, 2) + "\n", "utf8");
  console.log(`Guardian retirement payload written to: ${outPath}`);
  console.log(`Guardian ID: ${guardianId}`);
  console.log(`Public key SHA256: ${pubSha}`);
  console.log(`Challenge: ${challenge}`);
  console.log(`\nThis is a standalone retirement payload for process_guardian_retirement.py.`);
  console.log(`It is NOT a Record-Chain Gateway submission envelope.`);
  console.log(`Do NOT submit to /gateway/preflight or /agent-submit.`);
  console.log(`\nRun: python3 scripts/process_guardian_retirement.py --payload ${outPath}`);
}

main();
