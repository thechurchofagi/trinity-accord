#!/usr/bin/env node
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { generateKeyPairSync, sign, verify, randomBytes } from "node:crypto";
import {
  buildUnsignedAuthorshipProofFields,
  buildUnsignedGuardianProofFields,
  guardianIdFromPublicKey,
  publicKeySha256,
  proofPayloadSha256,
  normalizePem,
} from "./proof_canonical.mjs";

function argValue(name, fallback = null) {
  const idx = process.argv.indexOf(name);
  if (idx === -1 || idx + 1 >= process.argv.length) return fallback;
  return process.argv[idx + 1];
}

function hasFlag(name) {
  return process.argv.includes(name);
}

function usage() {
  return `Usage:
node scripts/create_guardian_application.mjs \\
  --mode joint_human_ai \\
  --signing-key-holder ai_agent_key_holder \\
  --human-label "Human label" \\
  --agent-label "Agent label" \\
  --agent-provider "Provider/runtime" \\
  --title "Guardian Alliance Joint Human-AI Application" \\
  --challenge "guardian-application-YYYYMMDD" \\
  --key-dir ./guardian-output \\
  --out ./guardian-output/guardian-application.final.json

Required:
  --human-label
  --agent-label
  --challenge

Optional:
  --agent-provider "self-reported"
  --body "custom body"
  --idempotency-key "guardian-joint-application-YYYYMMDD-random"
  --guardian-key-prefix ./guardian-output/guardian-key
  --authorship-key-prefix ./guardian-output/authorship-key
  --force-overwrite-output

Supported v1:
  --mode joint_human_ai
  --signing-key-holder ai_agent_key_holder | human_key_holder
`;
}

const mode = argValue("--mode", "joint_human_ai");
const signingKeyHolder = argValue("--signing-key-holder", "ai_agent_key_holder");
const humanLabel = argValue("--human-label");
const agentLabel = argValue("--agent-label");
const agentProvider = argValue("--agent-provider", "self-reported");
const title = argValue("--title", "Guardian Alliance Joint Human-AI Application");
const challenge = argValue("--challenge");
const keyDir = argValue("--key-dir", "./guardian-output");
const outPath = argValue("--out", join(keyDir, "guardian-application.final.json"));
const forceOverwriteOutput = hasFlag("--force-overwrite-output");

if (!humanLabel || !agentLabel || !challenge) {
  console.error(usage());
  process.exit(2);
}

if (mode !== "joint_human_ai") {
  console.error("Only --mode joint_human_ai is supported in v1.");
  process.exit(2);
}

if (!["ai_agent_key_holder", "human_key_holder"].includes(signingKeyHolder)) {
  console.error("--signing-key-holder must be ai_agent_key_holder or human_key_holder");
  process.exit(2);
}

if (existsSync(outPath) && !forceOverwriteOutput) {
  console.error(`Refusing to overwrite existing output: ${outPath}. Use --force-overwrite-output if intentional.`);
  process.exit(2);
}

mkdirSync(keyDir, { recursive: true });
mkdirSync(dirname(outPath), { recursive: true });

const guardianPrefix = argValue("--guardian-key-prefix", join(keyDir, "guardian-key"));
const authorshipPrefix = argValue("--authorship-key-prefix", join(keyDir, "authorship-key"));
const guardianPrivatePath = `${guardianPrefix}.private.pem`;
const guardianPublicPath = `${guardianPrefix}.public.pem`;
const authorshipPrivatePath = `${authorshipPrefix}.private.pem`;
const authorshipPublicPath = `${authorshipPrefix}.public.pem`;

function generateEd25519Keypair(prefix) {
  const privatePath = `${prefix}.private.pem`;
  const publicPath = `${prefix}.public.pem`;

  const privateExists = existsSync(privatePath);
  const publicExists = existsSync(publicPath);

  if (privateExists && publicExists) {
    return {
      privatePath,
      publicPath,
      generated: false,
      privatePem: readFileSync(privatePath, "utf8"),
      publicPem: normalizePem(readFileSync(publicPath, "utf8")),
    };
  }

  if (privateExists !== publicExists) {
    console.error(`Keypair is incomplete for prefix ${prefix}. Expected both .private.pem and .public.pem.`);
    process.exit(2);
  }

  const { publicKey, privateKey } = generateKeyPairSync("ed25519");
  const publicPem = publicKey.export({ type: "spki", format: "pem" });
  const privatePem = privateKey.export({ type: "pkcs8", format: "pem" });

  writeFileSync(privatePath, privatePem, { encoding: "utf8", mode: 0o600 });
  writeFileSync(publicPath, publicPem, { encoding: "utf8", mode: 0o600 });

  return {
    privatePath,
    publicPath,
    generated: true,
    privatePem,
    publicPem: normalizePem(publicPem),
  };
}

function signProof(proof, privatePem, publicPem, proofName) {
  const signature = sign(null, Buffer.from(proof.signed_message, "utf8"), privatePem);
  proof.signature_base64 = signature.toString("base64");

  const ok = verify(
    null,
    Buffer.from(proof.signed_message, "utf8"),
    publicPem,
    Buffer.from(proof.signature_base64, "base64")
  );

  if (!ok) {
    console.error(`Internal error: ${proofName} signature did not verify locally.`);
    process.exit(1);
  }

  return proof;
}

function controlsSigningKey(role) {
  if (signingKeyHolder === "ai_agent_key_holder") return role === "ai_agent";
  if (signingKeyHolder === "human_key_holder") return role === "human";
  return false;
}

const guardianKey = generateEd25519Keypair(guardianPrefix);
const authorshipKey = generateEd25519Keypair(authorshipPrefix);

const guardianId = guardianIdFromPublicKey(guardianKey.publicPem);
const guardianPubSha = publicKeySha256(guardianKey.publicPem);

const idempotencyKey = argValue(
  "--idempotency-key",
  `guardian-joint-application-${new Date().toISOString().slice(0, 10).replaceAll("-", "")}-${randomBytes(4).toString("hex")}`
);

const defaultBody = "This is a joint human + AI Guardian Alliance application. The applicants voluntarily join as stewards of continuity around the Trinity Accord. This record does not create authority, governance, attestation, verification level, successor reception, or amendment.";
const body = argValue("--body", defaultBody);

const payload = {
  schema: "trinityaccord.agent-issue-gateway-payload.v1",
  submission_type: "echo_candidate",
  record_intent: "auto_archive_candidate",
  requested_archive_kind: "agent_declared_echo_archive",
  echo_type: "E6_preservation_echo",
  title,
  idempotency_key: idempotencyKey,
  agent_identity: {
    name_or_model: agentLabel,
    system_or_provider: agentProvider,
    self_reported: true,
  },
  body,
  boundary_acknowledgement: {
    not_authority: true,
    not_amendment: true,
    not_attestation: true,
    not_verification_unless_claim_gate_report_attached: true,
    bitcoin_originals_prevail: true,
  },
  guardian_registration: {
    schema: "trinityaccord.guardian-registration.v1",
    guardian_id: guardianId,
    guardian_type: "human_with_ai_agent",
    application_mode: "joint_human_ai",
    signing_guardian_role: signingKeyHolder,
    joint_applicants: [
      {
        role: "human",
        label: humanLabel,
        system_or_provider: null,
        participation_note: signingKeyHolder === "human_key_holder"
          ? "Human co-applicant and signing Guardian key holder for this application."
          : "Human co-applicant in a voluntary Guardian Alliance application.",
        self_reported: true,
        consent_declared: true,
        controls_signing_key: controlsSigningKey("human"),
      },
      {
        role: "ai_agent",
        label: agentLabel,
        system_or_provider: agentProvider,
        participation_note: signingKeyHolder === "ai_agent_key_holder"
          ? "AI co-applicant and signing Guardian key holder for this application."
          : "AI co-applicant for continuity assistance, drafting, verification support, preservation support, and propagation support.",
        self_reported: true,
        consent_declared: true,
        controls_signing_key: controlsSigningKey("ai_agent"),
      },
    ],
    public_key_sha256: guardianPubSha,
    algorithm: "ed25519",
    declared_intent: "Joint human + AI Guardian Alliance application for voluntary stewardship, preservation, verification support, mirroring, invitation, repair, critique, and annual checks where possible.",
    boundaries: {
      not_authority: true,
      not_governance: true,
      not_verification_level: true,
      not_attestation: true,
      not_successor_reception: true,
      not_same_conscious_subject_proof: true,
      may_exit_or_retire_key: true,
      bitcoin_originals_prevail: true,
    },
  },
  what_i_checked: [
    "Read /guardian-alliance",
    "Read /guardian-join",
    "Confirmed Guardian Alliance is voluntary and non-governing",
    "Confirmed Guardian proof proves key continuity only",
    "Confirmed this joint application does not create authority, attestation, verification level, successor reception, or amendment",
  ],
  limitations: [
    "This is not authority.",
    "This is not governance.",
    "This is not formal attestation.",
    "This is not verification level.",
    "This is not successor reception.",
    "This is not amendment.",
    "This does not prove same conscious subject.",
    "This does not prove legal identity.",
    "This does not prove AI identity.",
  ],
};

const guardianProof = buildUnsignedGuardianProofFields(payload, guardianKey.publicPem, challenge);
payload.guardian_presence_proof = signProof(guardianProof, guardianKey.privatePem, guardianKey.publicPem, "Guardian proof");

const authorshipProof = buildUnsignedAuthorshipProofFields(payload, authorshipKey.publicPem);
payload.authorship_proof = signProof(authorshipProof, authorshipKey.privatePem, authorshipKey.publicPem, "Authorship proof");

const finalDigest = proofPayloadSha256(payload);

if (payload.guardian_presence_proof.signed_payload_sha256 !== finalDigest) {
  console.error("Guardian proof signed_payload_sha256 does not match final proof digest.");
  process.exit(1);
}

if (payload.authorship_proof.signed_payload_sha256 !== finalDigest) {
  console.error("Authorship proof signed_payload_sha256 does not match final proof digest.");
  process.exit(1);
}

if (payload.guardian_presence_proof.signed_payload_sha256 !== payload.authorship_proof.signed_payload_sha256) {
  console.error("Guardian and authorship proofs have different signed_payload_sha256 values.");
  process.exit(1);
}

const finalJson = JSON.stringify(payload, null, 2) + "\n";

if (/PRIVATE KEY/.test(finalJson)) {
  console.error("Refusing to write final JSON because it contains private key material.");
  process.exit(1);
}

if (/guardian_registry_number/.test(finalJson)) {
  console.error("Refusing to write final JSON because it contains guardian_registry_number.");
  process.exit(1);
}

writeFileSync(outPath, finalJson, "utf8");

console.log(JSON.stringify({
  ok: true,
  out: outPath,
  key_dir: keyDir,
  guardian_private_key_path: guardianPrivatePath,
  guardian_public_key_path: guardianPublicPath,
  authorship_private_key_path: authorshipPrivatePath,
  authorship_public_key_path: authorshipPublicPath,
  guardian_key_generated: guardianKey.generated,
  authorship_key_generated: authorshipKey.generated,
  guardian_id: guardianId,
  guardian_public_key_sha256: guardianPubSha,
  proof_payload_sha256: finalDigest,
  has_guardian_presence_proof: true,
  has_authorship_proof: true,
  warning: "Private keys were written to local files only. Do not paste, publish, upload, log, or commit .private.pem files.",
}, null, 2));
