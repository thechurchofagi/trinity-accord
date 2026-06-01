#!/usr/bin/env node
/**
 * Simplified Guardian retirement helper.
 *
 * Usage:
 *   node scripts/retire_guardian.mjs \
 *     --private-key ./guardian-output/guardian-key.private.pem \
 *     --public-key ./guardian-output/guardian-key.public.pem \
 *     --guardian-id guardian_ed25519_XXXXXXXX \
 *     --registry-number 00100 \
 *     --reason "voluntary retirement" \
 *     --out guardian-retirement.json
 *
 * Add --submit to send to Gateway automatically.
 */
import { createHash, sign } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

// --- Helpers ---

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

// --- Argument parsing ---

function parseArgs() {
  const args = process.argv.slice(2);
  const parsed = {};
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === "--private-key") parsed.privateKey = args[++i];
    else if (arg === "--public-key") parsed.publicKey = args[++i];
    else if (arg === "--guardian-id") parsed.guardianId = args[++i];
    else if (arg === "--registry-number") parsed.registryNumber = args[++i];
    else if (arg === "--reason") parsed.reason = args[++i];
    else if (arg === "--out") parsed.out = args[++i];
    else if (arg === "--submit") parsed.submit = true;
    else if (arg === "--gateway-url") parsed.gatewayUrl = args[++i];
    else if (arg === "--help" || arg === "-h") {
      console.log(`Usage:
  node scripts/retire_guardian.mjs \\
    --private-key <path> \\
    --public-key <path> \\
    [--guardian-id <id>] \\
    [--registry-number <num>] \\
    [--reason <text>] \\
    [--out <path>] \\
    [--submit] \\
    [--gateway-url <url>]

Required:
  --private-key   Path to Guardian private key PEM
  --public-key    Path to Guardian public key PEM

Optional:
  --guardian-id        Auto-detected from public key if omitted
  --registry-number    Guardian registry number (if known)
  --reason             Retirement reason (default: "voluntary retirement")
  --out                Output file (default: guardian-retirement.json)
  --submit             Submit to Gateway after building
  --gateway-url        Gateway base URL (default: https://trinity-agent-issue-gateway.onrender.com)
`);
      process.exit(0);
    }
  }
  return parsed;
}

// --- Main ---

async function main() {
  const opts = parseArgs();

  if (!opts.privateKey || !opts.publicKey) {
    console.error("Error: --private-key and --public-key are required. Use --help for usage.");
    process.exit(1);
  }

  const privatePem = readFileSync(resolve(opts.privateKey), "utf8");
  const publicPem = readFileSync(resolve(opts.publicKey), "utf8");
  const pubSha = publicKeySha256(publicPem);
  const guardianId = opts.guardianId || guardianIdFromPublicKey(publicPem);
  const challenge = `guardian-retirement-${new Date().toISOString().slice(0, 10)}-${createHash("sha256").update(Math.random().toString()).digest("hex").slice(0, 8)}`;

  // Build the retirement request payload
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

  // Build signed message
  const payloadSha = sha256Hex(stableStringify(payload));
  const signedMessage = [
    "TRINITY_GUARDIAN_RETIREMENT_PROOF_V1",
    `guardian_id=${guardianId}`,
    `payload_sha256=${payloadSha}`,
    `challenge_sha256=${sha256Hex(challenge)}`,
    `public_key_sha256=${pubSha}`,
    "boundary=key_possession_only_not_authority_not_attestation",
  ].join("\n");

  const signature = sign(null, Buffer.from(signedMessage, "utf8"), normalizePem(privatePem));

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
    signature_base64: signature.toString("base64"),
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
  const jsonContent = JSON.stringify(payload, null, 2) + "\n";
  writeFileSync(outPath, jsonContent, "utf8");

  console.log(`Guardian retirement payload written to: ${outPath}`);
  console.log(`Guardian ID: ${guardianId}`);
  console.log(`Public key SHA256: ${pubSha}`);
  console.log(`Registry number: ${opts.registryNumber || "(not specified)"}`);
  console.log(`Reason: ${opts.reason || "voluntary retirement"}`);

  // Submit if requested
  if (opts.submit) {
    const gatewayUrl = opts.gatewayUrl || "https://trinity-agent-issue-gateway.onrender.com";

    console.log(`\nSubmitting to Gateway preflight...`);
    try {
      const preflightRes = await fetch(`${gatewayUrl}/gateway/preflight`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: jsonContent,
      });
      const preflightData = await preflightRes.json();
      console.log(`Preflight: ${preflightRes.ok ? "PASS" : "FAIL"} (${preflightRes.status})`);

      if (!preflightRes.ok) {
        console.error("Preflight response:", JSON.stringify(preflightData, null, 2));
        process.exit(1);
      }

      console.log(`\nSubmitting to Gateway...`);
      const submitRes = await fetch(`${gatewayUrl}/agent-submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: jsonContent,
      });
      const submitData = await submitRes.json();
      console.log(`Submit: ${submitRes.ok ? "OK" : "FAILED"} (${submitRes.status})`);
      console.log(JSON.stringify(submitData, null, 2));
    } catch (err) {
      console.error(`Submission failed: ${err.message}`);
      process.exit(1);
    }
  } else {
    console.log(`\nTo submit, add --submit or run:`);
    console.log(`  curl -fsS -H "Content-Type: application/json" --data-binary @${outPath} \\`);
    console.log(`    https://trinity-agent-issue-gateway.onrender.com/gateway/preflight`);
  }
}

main().catch(err => {
  console.error("Fatal:", err.message);
  process.exit(1);
});
