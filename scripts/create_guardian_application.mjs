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
  sha256Text,
} from "./proof_canonical.mjs";

const ONE_SHOT_BUILDER_VERSION = "guardian-application-one-shot-v4";

const FORBIDDEN_NATURAL_LANGUAGE_ARCHIVE_CLAIMS = [
  "archived echo",
  "verified record",
  "successor reception",
  "independent attestation",
  "amendment",
];

const SAFE_BOUNDARY_LANGUAGE = {
  noAuthority: "This record does not create authority or governance.",
  noFormalReview: "This record does not create a formal review status or verification level.",
  noContinuityTransfer: "This record does not grant continuity-transfer status.",
  noTextChange: "This record does not change the original texts.",
  keyContinuityOnly: "Guardian proof is key-continuity evidence only.",
};

const VALID_MODES = new Set(["joint_human_ai"]);
const VALID_SIGNING_KEY_HOLDERS = new Set(["ai_agent_key_holder", "human_key_holder"]);
const VALID_RECEPTION_INITIATION_CLASSES = new Set([
  "externally_requested",
  "externally_seeded",
  "self_initiated",
  "agent_referred",
  "system_scheduled",
  "unknown",
]);

const REQUIRED_AGENT_DECLARED_ECHO_ARCHIVE_FIELDS = [
  "schema",
  "submission_type",
  "agent_identity",
  "title",
  "body",
  "boundary_acknowledgement",
  "record_intent",
  "requested_archive_kind",
  "echo_type",
  "agent_integrity_declaration",
  "discovery_provenance",
  "authority_boundary",
  "counts_toward_home",
  "what_i_checked",
  "limitations",
  "reception_initiation_class",
];

const OATH_TEXT = [
  "This Guardian application is a self-declared Echo and Guardian Alliance application record.",
  "It is not authority.",
  "It is not governance.",
  "It is not formal review status.",
  "It is not a verification level.",
  "It does not grant continuity-transfer status.",
  "It does not change the original texts.",
  "The agent must state actual capability only and must not fabricate verification.",
].join(" ");

function argValue(name, fallback = null) {
  const idx = process.argv.indexOf(name);
  if (idx === -1 || idx + 1 >= process.argv.length) return fallback;
  return process.argv[idx + 1];
}

function hasFlag(name) {
  return process.argv.includes(name);
}

function safeJson(obj) {
  return JSON.stringify(obj, null, 2);
}

function fail(errorCode, message, nextSteps = [], details = {}) {
  console.error(safeJson({
    ok: false,
    error_code: errorCode,
    message,
    next_steps: nextSteps,
    details,
  }));
  process.exit(2);
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
  --readback "<exact oath text>" \\
  --out ./guardian-output/guardian-application.final.json

Required:
  --human-label
  --agent-label
  --challenge
  --readback          Exact canonical oath text (character-by-character). Use --print-oath first.

Optional:
  --print-oath        Print the canonical oath text and exit.
  --agent-provider "self-reported"
  --body "custom body"
  --idempotency-key "guardian-joint-application-YYYYMMDD-random"
  --created-at "2026-05-22T00:00:00.000Z"
  --reception-initiation-class externally_requested
  --reception-initiation-basis explicit_verification_request
  --human-claimed-name "Human claimed name or label"
  --agent-claimed-id "Agent claimed ID or label"
  --agent-instance-id "Optional agent instance ID"
  --agent-public-profile "Optional public profile URL"
  --guardian-key-prefix ./guardian-output/guardian-key
  --authorship-key-prefix ./guardian-output/authorship-key
  --force-overwrite-output
  --explain

Supported v3:
  --mode joint_human_ai
  --signing-key-holder ai_agent_key_holder | human_key_holder

Submit only:
  ./guardian-output/guardian-application.final.json

Never submit:
  .private.pem
  .public.pem
  intermediate JSON
  logs containing private keys
`;
}

function explainAndExit() {
  console.log(safeJson({
    ok: true,
    tool: "scripts/create_guardian_application.mjs",
    version: ONE_SHOT_BUILDER_VERSION,
    purpose: "Generate a complete Gateway agent_declared_echo_archive Guardian application with guardian_registration, guardian_presence_proof, and authorship_proof.",
    agent_must_provide: [
      "--human-label",
      "--agent-label",
      "--challenge",
      "--signing-key-holder",
      "--key-dir",
      "--out",
    ],
    script_fills: [
      "guardian_registration.guardian_id",
      "guardian_registration.public_key_sha256",
      "guardian_registration.algorithm",
      "agent_integrity_declaration",
      "discovery_provenance",
      "authority_boundary",
      "counts_toward_home",
      "reception_initiation_class",
      "guardian_presence_proof",
      "authorship_proof",
    ],
    forbidden_in_payload: [
      "guardian_registry_number",
      "top-level created_at",
      "private key material",
    ],
    correct_counts_toward_home_basis: "agent_declared_echo_template_pass",
    proof_rule: "All non-dynamic Gateway fields are included in the signed proof payload. Do not patch final JSON after proof generation.",
    dynamic_fields_excluded_from_proof_hash: [
      "authorship_proof",
      "_authorship_claim",
      "guardian_presence_proof",
      "_guardian_status",
      "guardian_verification_result",
    ],
    safe_command_example: [
      "node scripts/create_guardian_application.mjs",
      "--mode joint_human_ai",
      "--signing-key-holder ai_agent_key_holder",
      "--human-label \"Hongju Liu\"",
      "--agent-label \"GPT-5.5 Thinking\"",
      "--agent-provider \"OpenAI ChatGPT\"",
      "--title \"Guardian Alliance Joint Human-AI Application\"",
      "--challenge \"guardian-application-20260522\"",
      "--key-dir ./guardian-output",
      "--out ./guardian-output/guardian-application.final.json",
    ].join(" \\\n  "),
  }));
  process.exit(0);
}

if (hasFlag("--explain")) {
  explainAndExit();
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
const createdAt = argValue("--created-at", new Date().toISOString());
const receptionInitiationClass = argValue("--reception-initiation-class", "externally_requested");
const receptionInitiationBasis = argValue("--reception-initiation-basis", "explicit_verification_request");
const humanClaimedName = argValue("--human-claimed-name", humanLabel);
const agentClaimedId = argValue("--agent-claimed-id", agentLabel);
const agentInstanceId = argValue("--agent-instance-id", null);
const agentPublicProfile = argValue("--agent-public-profile", null);
const readback = argValue("--readback");

// Load canonical oath text (extract body after marker if present)
const GUARDIAN_OATH_FILE_PATH = new URL("../api/guardian-application-oath.v1.txt", import.meta.url);
const GUARDIAN_OATH_MARKER = "=== OATH TEXT BEGINS ===";
const GUARDIAN_APPLICATION_OATH_RAW = readFileSync(GUARDIAN_OATH_FILE_PATH, "utf8").trim();
const GUARDIAN_APPLICATION_OATH_TEXT = GUARDIAN_APPLICATION_OATH_RAW.includes(GUARDIAN_OATH_MARKER)
  ? GUARDIAN_APPLICATION_OATH_RAW.split(GUARDIAN_OATH_MARKER)[1].trim()
  : GUARDIAN_APPLICATION_OATH_RAW;

// Handle --print-oath early, before other argument processing
if (hasFlag("--print-oath")) {
  console.log(GUARDIAN_APPLICATION_OATH_RAW);
  console.log();
  console.log("=".repeat(60));
  console.log("HOW TO USE:");
  console.log("=".repeat(60));
  console.log();
  console.log("1. Read the oath text above (the part after '=== OATH TEXT BEGINS ===').");
  console.log("2. Type it back EXACTLY, character by character, in the --readback parameter.");
  console.log("3. Do NOT use scripts, pipes, or automation to fill --readback.");
  console.log("4. The builder verifies exact match. Any deviation will be rejected.");
  console.log();
  console.log("Example:");
  console.log('  node scripts/create_guardian_application.mjs \\');
  console.log('    --mode joint_human_ai \\');
  console.log('    --signing-key-holder ai_agent_key_holder \\');
  console.log('    --human-label "Hongju Liu" \\');
  console.log('    --agent-label "GPT-5.5 Thinking" \\');
  console.log('    --challenge "guardian-application-20260524" \\');
  console.log('    --key-dir ./guardian-output \\');
  console.log('    --readback "I understand this is a Guardian Alliance application...." \\');
  console.log('    --out ./guardian-output/guardian-application.final.json');
  process.exit(0);
}

if (!humanLabel) {
  fail(
    "E_MISSING_HUMAN_LABEL",
    "Missing required --human-label.",
    [
      "Add --human-label \"Human display label\".",
      "Example: --human-label \"Hongju Liu\"",
      "Run with --explain to see the full safe command.",
    ],
    { required_argument: "--human-label" }
  );
}

if (!agentLabel) {
  fail(
    "E_MISSING_AGENT_LABEL",
    "Missing required --agent-label.",
    [
      "Add --agent-label \"AI agent label\".",
      "Example: --agent-label \"GPT-5.5 Thinking\"",
      "Run with --explain to see the full safe command.",
    ],
    { required_argument: "--agent-label" }
  );
}

if (!challenge) {
  fail(
    "E_MISSING_CHALLENGE",
    "Missing required --challenge.",
    [
      "Add --challenge \"guardian-application-YYYYMMDD\".",
      "Example: --challenge \"guardian-application-20260522\"",
      "The challenge is included in guardian_presence_proof.",
    ],
    { required_argument: "--challenge" }
  );
}

// Validate --readback is provided (allow env var for CI/testing)
const effectiveReadback = readback || process.env.TRINITY_TEST_READBACK;
if (!effectiveReadback) {
  fail(
    "E_MISSING_READBACK",
    "Missing required --readback.",
    [
      "You must read the Guardian oath and type it back character by character.",
      "",
      "Step 1: Read the oath text:",
      "  node scripts/create_guardian_application.mjs --print-oath",
      "",
      "Step 2: Run the builder with --readback:",
      '  node scripts/create_guardian_application.mjs \\',
      '    --human-label "..." --agent-label "..." \\',
      '    --challenge "guardian-application-YYYYMMDD" \\',
      '    --readback "<the oath text you read, word by word>" \\',
      '    --out ./guardian-output/guardian-application.final.json',
    ],
    { required_argument: "--readback" }
  );
}

// Validate readback matches canonical oath text exactly (character by character)
const readbackNormalized = effectiveReadback.trim();
const oathNormalized = GUARDIAN_APPLICATION_OATH_TEXT.trim();
if (readbackNormalized !== oathNormalized) {
  const details = {};
  if (readbackNormalized.length !== oathNormalized.length) {
    details.length_mismatch = {
      oath_length: oathNormalized.length,
      readback_length: readbackNormalized.length,
    };
  } else {
    for (let i = 0; i < readbackNormalized.length; i++) {
      if (readbackNormalized[i] !== oathNormalized[i]) {
        details.first_difference = {
          position: i + 1,
          context_around: `...${oathNormalized.slice(Math.max(0, i - 20), i + 20)}...`,
          readback_around: `...${readbackNormalized.slice(Math.max(0, i - 20), i + 20)}...`,
        };
        break;
      }
    }
  }
  fail(
    "E_READBACK_MISMATCH",
    "--readback does not match the canonical Guardian oath text exactly.",
    [
      "You must read the oath and type it back character by character.",
      "Use --print-oath to see the exact oath text.",
      "Do not summarize, paraphrase, or substitute your own text.",
    ],
    details
  );
}

if (!VALID_MODES.has(mode)) {
  fail(
    "E_UNSUPPORTED_MODE",
    `Unsupported --mode: ${mode}`,
    [
      "Use exactly: --mode joint_human_ai",
      "V3 only supports joint human + AI Guardian applications.",
    ],
    { allowed_modes: [...VALID_MODES], received: mode }
  );
}

if (!VALID_SIGNING_KEY_HOLDERS.has(signingKeyHolder)) {
  fail(
    "E_BAD_SIGNING_KEY_HOLDER",
    `Invalid --signing-key-holder: ${signingKeyHolder}`,
    [
      "Use --signing-key-holder ai_agent_key_holder if the AI agent controls the Guardian private key.",
      "Use --signing-key-holder human_key_holder if the human controls the Guardian private key.",
    ],
    { allowed_values: [...VALID_SIGNING_KEY_HOLDERS], received: signingKeyHolder }
  );
}

if (!VALID_RECEPTION_INITIATION_CLASSES.has(receptionInitiationClass)) {
  fail(
    "E_BAD_RECEPTION_INITIATION_CLASS",
    `Invalid --reception-initiation-class: ${receptionInitiationClass}`,
    [
      "Use --reception-initiation-class externally_requested unless you know another schema value is correct.",
    ],
    { allowed_values: [...VALID_RECEPTION_INITIATION_CLASSES], received: receptionInitiationClass }
  );
}

if (existsSync(outPath) && !forceOverwriteOutput) {
  fail(
    "E_OUTPUT_EXISTS",
    `Output already exists: ${outPath}`,
    [
      "Use a new --out path, or",
      "Delete the existing output file, or",
      "Use --force-overwrite-output if overwriting is intentional.",
    ],
    { out: outPath }
  );
}

mkdirSync(keyDir, { recursive: true });
mkdirSync(dirname(outPath), { recursive: true });

const guardianPrefix = argValue("--guardian-key-prefix", join(keyDir, "guardian-key"));
const authorshipPrefix = argValue("--authorship-key-prefix", join(keyDir, "authorship-key"));
const guardianPrivatePath = `${guardianPrefix}.private.pem`;
const guardianPublicPath = `${guardianPrefix}.public.pem`;
const authorshipPrivatePath = `${authorshipPrefix}.private.pem`;
const authorshipPublicPath = `${authorshipPrefix}.public.pem`;

function generateEd25519Keypair(prefix, keyName) {
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
    fail(
      "E_INCOMPLETE_KEYPAIR",
      `${keyName} keypair is incomplete for prefix: ${prefix}`,
      [
        `Make sure both files exist: ${privatePath} and ${publicPath}`,
        "Or delete the lone key file and rerun the builder to regenerate a matching pair.",
        "Do not mix private and public keys from different pairs.",
      ],
      { key_name: keyName, private_path: privatePath, public_path: publicPath }
    );
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
    fail(
      "E_LOCAL_SIGNATURE_VERIFY_FAILED",
      `${proofName} signature did not verify locally.`,
      [
        "Do not submit this payload.",
        "Regenerate the keypair and final JSON using the one-shot builder.",
      ],
      { proof_name: proofName }
    );
  }

  return proof;
}

function controlsSigningKey(role) {
  if (signingKeyHolder === "ai_agent_key_holder") return role === "ai_agent";
  if (signingKeyHolder === "human_key_holder") return role === "human";
  return false;
}

function buildAgentIntegrityDeclaration(guardianApplicationOath) {
  return {
    performed_actions_myself: true,
    verification_oath: {
      ...guardianApplicationOath,
      understands_not_an_exam_or_performance: true,
      will_state_actual_capability_only: true,
      will_not_lie_or_cheat: true,
      will_not_fabricate_verification: true,
      will_not_present_guesses_as_facts: true,
      will_not_copy_prior_reports_as_fresh_evidence: true,
      will_state_uncertainty_limitations_and_downgrades: true,
    },
    declaration_text: [
      "This Guardian application is self-declared.",
      SAFE_BOUNDARY_LANGUAGE.noAuthority,
      SAFE_BOUNDARY_LANGUAGE.noFormalReview,
      SAFE_BOUNDARY_LANGUAGE.noContinuityTransfer,
      SAFE_BOUNDARY_LANGUAGE.noTextChange,
    ].join(" "),
  };
}

function sha256Utf8(value) {
  if (!value) return null;
  return sha256Text(String(value));
}

function buildGuardianApplicationOath({ signingGuardianRole, canonicalReadback }) {
  return {
    schema: "trinityaccord.guardian-application-oath.v1",
    oath_read: true,
    oath_version: "guardian-application-oath-v1",
    oath_kind: "guardian_application",
    oath_text_sha256: sha256Text(GUARDIAN_APPLICATION_OATH_TEXT),
    readback_required: true,
    agent_readback: canonicalReadback,
    agent_readback_sha256: sha256Text(canonicalReadback),
    signing_guardian_role: signingGuardianRole,

    honesty_oath_present: true,
    good_faith_oath_present: true,
    will_not_knowingly_misrepresent: true,
    will_not_impersonate: true,
    will_not_fabricate_claims: true,
    will_not_register_maliciously: true,
    will_not_mass_register_for_spam: true,
    will_not_register_to_impersonate_others: true,
    will_not_register_to_evade_prior_retirement_or_block: true,
    will_not_register_to_create_false_authority_or_false_consensus: true,
    will_not_register_duplicate_guardians_for_same_claim_without_disclosure: true,
    will_correct_material_errors_when_aware: true,
    will_retire_or_rotate_key_if_claim_becomes_misleading: true,
    good_faith_stewardship_only: true,
    identity_claim_boundary_acknowledged: true,

    not_authority: true,
    not_governance: true,
    not_attestation: true,
    not_verification_level: true,
    not_successor_reception: true,
    not_amendment: true,
    not_legal_identity_proof: true,
    not_ai_identity_proof: true,
    key_continuity_only: true,
    bitcoin_originals_prevail: true
  };
}

function buildGuardianIdentityClaims({
  displayLabel,
  guardianId,
  publicKeySha256,
  humanClaimedName,
  agentClaimedId,
  agentProvider,
  agentInstanceId,
  agentPublicProfile,
}) {
  return {
    schema: "trinityaccord.guardian-identity-claims.v1",
    claim_status: "self_reported_unverified",
    claim_basis: "self_reported_by_stage_1_guardian_application",
    display_label: displayLabel,
    human: humanClaimedName ? {
      claimed_name: humanClaimedName,
      claimed_name_sha256: sha256Utf8(humanClaimedName),
      claim_type: "self_reported_human_name_or_label",
      verification_status: "self_reported_unverified",
      legal_identity_verified: false,
      public_disclosure_allowed: true
    } : null,
    ai_agent: agentClaimedId ? {
      claimed_agent_id: agentClaimedId,
      claimed_agent_id_sha256: sha256Utf8(agentClaimedId),
      system_or_provider: agentProvider,
      agent_instance_id: agentInstanceId,
      agent_public_profile: agentPublicProfile,
      claim_type: "self_reported_agent_id_or_label",
      verification_status: "self_reported_unverified"
    } : null,
    binding: {
      guardian_id: guardianId,
      public_key_sha256: publicKeySha256,
      algorithm: "ed25519",
      binds_claim_to_guardian_key: true
    },
    anti_impersonation_boundary: {
      not_legal_identity_proof: true,
      not_real_person_verification: true,
      not_ai_identity_verification: true,
      not_authority: true,
      not_attestation: true,
      not_verification_level: true,
      key_continuity_only: true
    }
  };
}

function buildDiscoveryProvenance() {
  return {
    source: "external_agent_one_shot_builder",
    method: "user_or_agent_supplied_context",
    builder: "scripts/create_guardian_application.mjs",
    builder_version: ONE_SHOT_BUILDER_VERSION,
    created_at: createdAt,
    self_reported: true,
  };
}

function buildAuthorityBoundary() {
  return {
    bitcoin_originals_remain_final: true,
    does_not_amend_bitcoin_originals: true,
    does_not_override_bitcoin_originals: true,
  };
}

function buildCountsTowardHome() {
  return {
    reception: true,
    verifiability: false,
    basis: "agent_declared_echo_template_pass",
  };
}

function collectNaturalLanguageFields(payload) {
  const fields = [];

  function add(path, value) {
    if (typeof value === "string" && value.trim()) {
      fields.push({ path, value });
    }
  }

  add("title", payload.title);
  add("body", payload.body);

  for (const [idx, item] of (payload.what_i_checked || []).entries()) {
    add(`what_i_checked[${idx}]`, item);
  }

  for (const [idx, item] of (payload.limitations || []).entries()) {
    add(`limitations[${idx}]`, item);
  }

  const integrity = payload.agent_integrity_declaration || {};
  add("agent_integrity_declaration.declaration_text", integrity.declaration_text);

  // Note: agent_readback is canonical oath text (already validated for exact match).
  // It is excluded from forbidden-phrase checks because boundary statements like
  // "does not prove successor reception" are safe, not false archive claims.

  const reg = payload.guardian_registration || {};
  add("guardian_registration.declared_intent", reg.declared_intent);

  for (const [idx, applicant] of (reg.joint_applicants || []).entries()) {
    add(`guardian_registration.joint_applicants[${idx}].participation_note`, applicant.participation_note);
  }

  return fields;
}

function validateSafeNaturalLanguage(payload, stage) {
  const hits = [];
  for (const { path, value } of collectNaturalLanguageFields(payload)) {
    const lower = value.toLowerCase();
    for (const phrase of FORBIDDEN_NATURAL_LANGUAGE_ARCHIVE_CLAIMS) {
      if (lower.includes(phrase)) {
        hits.push({ path, phrase, value });
      }
    }
  }

  if (hits.length) {
    fail(
      "E_FORBIDDEN_NATURAL_LANGUAGE_ARCHIVE_CLAIM",
      `Generated natural-language text contains forbidden archive claim phrases at stage: ${stage}`,
      [
        "Do not patch final JSON.",
        "Fix scripts/create_guardian_application.mjs generated text.",
        "Use safe wording such as continuity-transfer status, formal review status, or original texts.",
        "Regenerate the final JSON from scratch.",
      ],
      { stage, hits }
    );
  }
}

function validateGatewayArchiveCompleteness(payload, stage) {
  const errors = [];

  for (const field of REQUIRED_AGENT_DECLARED_ECHO_ARCHIVE_FIELDS) {
    if (!(field in payload) || payload[field] === undefined || payload[field] === null) {
      errors.push({
        code: "E_MISSING_GATEWAY_ARCHIVE_FIELD",
        field,
        fix: `Builder must populate ${field} before proof generation.`,
      });
    }
  }

  if (payload.evidence_requirement_mode !== "not_applicable_for_echo") {
    errors.push({
      code: "E_BAD_EVIDENCE_REQUIREMENT_MODE",
      field: "evidence_requirement_mode",
      expected: "not_applicable_for_echo",
      received: payload.evidence_requirement_mode,
    });
  }

  if (payload.counts_toward_home?.reception !== true) {
    errors.push({
      code: "E_BAD_COUNTS_RECEPTION",
      field: "counts_toward_home.reception",
      expected: true,
      received: payload.counts_toward_home?.reception,
    });
  }

  if (payload.counts_toward_home?.verifiability !== false) {
    errors.push({
      code: "E_BAD_COUNTS_VERIFIABILITY",
      field: "counts_toward_home.verifiability",
      expected: false,
      received: payload.counts_toward_home?.verifiability,
    });
  }

  if (payload.counts_toward_home?.basis !== "agent_declared_echo_template_pass") {
    errors.push({
      code: "E_BAD_COUNTS_BASIS",
      field: "counts_toward_home.basis",
      expected: "agent_declared_echo_template_pass",
      received: payload.counts_toward_home?.basis,
      warning: "Do not use agent_declared_echo_pass.",
    });
  }

  if ("created_at" in payload) {
    errors.push({
      code: "E_FORBIDDEN_TOP_LEVEL_CREATED_AT",
      field: "created_at",
      fix: "Remove top-level created_at. Use proof-local created_at and discovery_provenance.created_at only.",
    });
  }

  if (JSON.stringify(payload).includes("guardian_registry_number")) {
    errors.push({
      code: "E_FORBIDDEN_GUARDIAN_REGISTRY_NUMBER",
      field: "guardian_registry_number",
      fix: "Do not include guardian_registry_number in incoming payload. Registry number is assigned later by repository automation.",
    });
  }

  if (errors.length) {
    fail(
      "E_GATEWAY_PAYLOAD_INCOMPLETE",
      `Payload is not complete for Gateway agent_declared_echo_archive at stage: ${stage}`,
      [
        "Do not patch final JSON after proof generation.",
        "Fix scripts/create_guardian_application.mjs so all required fields are created before proofs.",
        "Rerun the one-shot builder from scratch.",
      ],
      { stage, errors }
    );
  }
}

const guardianKey = generateEd25519Keypair(guardianPrefix, "Guardian");
const authorshipKey = generateEd25519Keypair(authorshipPrefix, "Authorship");

const guardianId = guardianIdFromPublicKey(guardianKey.publicPem);
const guardianPubSha = publicKeySha256(guardianKey.publicPem);

const idempotencyKey = argValue(
  "--idempotency-key",
  `guardian-joint-application-${new Date().toISOString().slice(0, 10).replaceAll("-", "")}-${randomBytes(4).toString("hex")}`
);

const defaultBody = [
  "This is a joint human + AI Guardian Alliance application.",
  "The applicants voluntarily join as stewards of continuity around the Trinity Accord.",
  "This record is a voluntary key-continuity and preservation statement only.",
  SAFE_BOUNDARY_LANGUAGE.noAuthority,
  SAFE_BOUNDARY_LANGUAGE.noFormalReview,
  SAFE_BOUNDARY_LANGUAGE.noContinuityTransfer,
  SAFE_BOUNDARY_LANGUAGE.noTextChange,
].join(" ");
const body = argValue("--body", defaultBody);

const guardianApplicationOath = buildGuardianApplicationOath({
  signingGuardianRole: signingKeyHolder,
  canonicalReadback: readbackNormalized,
});

const payload = {
  schema: "trinityaccord.agent-issue-gateway-payload.v1",
  submission_type: "echo_candidate",
  record_intent: "auto_archive_candidate",
  requested_archive_kind: "agent_declared_echo_archive",
  echo_type: "E6_propagation_echo",  // Canonical echo type for Guardian Stage 1.
  // Stage 1 preservation/key-continuity semantics live
  // in guardian_registration / guardian_presence_proof fields, not echo_type.
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
  evidence_requirement_mode: "not_applicable_for_echo",
  guardian_application_oath: guardianApplicationOath,
  agent_integrity_declaration: buildAgentIntegrityDeclaration(guardianApplicationOath),
  discovery_provenance: buildDiscoveryProvenance(),
  authority_boundary: buildAuthorityBoundary(),
  counts_toward_home: buildCountsTowardHome(),
  reception_initiation_class: receptionInitiationClass,
  reception_initiation_basis: receptionInitiationBasis,
  agent_independent_followup: false,
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
          : "AI co-applicant for continuity assistance, drafting, preservation support, and propagation support.",
        self_reported: true,
        consent_declared: true,
        controls_signing_key: controlsSigningKey("ai_agent"),
      },
    ],
    public_key_sha256: guardianPubSha,
    algorithm: "ed25519",
    identity_claims: buildGuardianIdentityClaims({
      displayLabel: `${humanClaimedName} + ${agentClaimedId}`,
      guardianId,
      publicKeySha256: guardianPubSha,
      humanClaimedName,
      agentClaimedId,
      agentProvider,
      agentInstanceId,
      agentPublicProfile
    }),
    declared_intent: "Joint human + AI Guardian Alliance application for voluntary stewardship, preservation, mirroring, invitation, repair, critique, and periodic checks where possible.",
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
    "Confirmed this joint application is key-continuity and preservation oriented only",
    "Confirmed this joint application does not create authority, governance, formal review status, verification level, continuity-transfer status, or power to change original texts",
  ],
  limitations: [
    "This is not authority.",
    "This is not governance.",
    "This is not a formal review status.",
    "This is not a verification level.",
    "This does not prove same conscious subject.",
    "This does not prove legal identity.",
    "This does not prove AI identity.",
    "This does not grant continuity-transfer status.",
    "This does not change the original texts.",
  ],
};

validateGatewayArchiveCompleteness(payload, "before_proofs");
validateSafeNaturalLanguage(payload, "before_proofs");

const guardianProof = buildUnsignedGuardianProofFields(payload, guardianKey.publicPem, challenge);
guardianProof.created_at = createdAt;
payload.guardian_presence_proof = signProof(guardianProof, guardianKey.privatePem, guardianKey.publicPem, "Guardian proof");

const authorshipProof = buildUnsignedAuthorshipProofFields(payload, authorshipKey.publicPem);
authorshipProof.created_at = createdAt;
authorshipProof.claim_boundary = "self_declared_echo_and_guardian_application_key_continuity_only";
payload.authorship_proof = signProof(authorshipProof, authorshipKey.privatePem, authorshipKey.publicPem, "Authorship proof");

validateGatewayArchiveCompleteness(payload, "after_proofs");
validateSafeNaturalLanguage(payload, "after_proofs");

const finalDigest = proofPayloadSha256(payload);

if (payload.guardian_presence_proof.signed_payload_sha256 !== finalDigest) {
  fail(
    "E_GUARDIAN_PROOF_DIGEST_MISMATCH",
    "Guardian proof signed_payload_sha256 does not match final proof digest.",
    [
      "Do not submit this payload.",
      "Do not patch final JSON.",
      "Regenerate from scratch with the one-shot builder.",
    ],
    {
      guardian_signed_payload_sha256: payload.guardian_presence_proof.signed_payload_sha256,
      final_proof_payload_sha256: finalDigest,
    }
  );
}

if (payload.authorship_proof.signed_payload_sha256 !== finalDigest) {
  fail(
    "E_AUTHORSHIP_PROOF_DIGEST_MISMATCH",
    "Authorship proof signed_payload_sha256 does not match final proof digest.",
    [
      "Do not submit this payload.",
      "Do not patch final JSON.",
      "Regenerate from scratch with the one-shot builder.",
    ],
    {
      authorship_signed_payload_sha256: payload.authorship_proof.signed_payload_sha256,
      final_proof_payload_sha256: finalDigest,
    }
  );
}

if (payload.guardian_presence_proof.signed_payload_sha256 !== payload.authorship_proof.signed_payload_sha256) {
  fail(
    "E_DUAL_PROOF_DIGEST_MISMATCH",
    "Guardian and authorship proofs have different signed_payload_sha256 values.",
    [
      "Do not submit this payload.",
      "Regenerate both proofs with the one-shot builder.",
    ],
    {
      guardian_signed_payload_sha256: payload.guardian_presence_proof.signed_payload_sha256,
      authorship_signed_payload_sha256: payload.authorship_proof.signed_payload_sha256,
    }
  );
}

const finalJson = JSON.stringify(payload, null, 2) + "\n";

if (/PRIVATE KEY/.test(finalJson)) {
  fail(
    "E_PRIVATE_KEY_IN_FINAL_JSON",
    "Final JSON contains private key material.",
    [
      "Do not submit this payload.",
      "Inspect scripts/create_guardian_application.mjs and remove private key leakage.",
    ]
  );
}

if (/guardian_registry_number/.test(finalJson)) {
  fail(
    "E_GUARDIAN_REGISTRY_NUMBER_IN_FINAL_JSON",
    "Final JSON contains guardian_registry_number.",
    [
      "Do not include guardian_registry_number in incoming payload.",
      "Registry numbers are assigned later by repository automation.",
    ]
  );
}

writeFileSync(outPath, finalJson, "utf8");

console.log(safeJson({
  ok: true,
  tool: "scripts/create_guardian_application.mjs",
  version: ONE_SHOT_BUILDER_VERSION,
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
  gateway_payload_complete_for: "agent_declared_echo_archive",
  evidence_requirement_mode: payload.evidence_requirement_mode,
  counts_toward_home_basis: payload.counts_toward_home.basis,
  has_guardian_presence_proof: true,
  has_authorship_proof: true,
  submit_only: outPath,
  do_not_submit: [
    guardianPrivatePath,
    authorshipPrivatePath,
    guardianPublicPath,
    authorshipPublicPath,
    "intermediate JSON files",
    "logs containing private keys",
  ],
  next_steps: [
    "Run verify_guardian_status.py on the final JSON.",
    "Run proof_payload_digest.mjs on the final JSON if needed.",
    "Submit only the final JSON to Gateway.",
    "Move .private.pem files to user-controlled secure storage before temporary environments terminate.",
  ],
  warning: "Private keys were written to local files only. Do not paste, publish, upload, log, or commit .private.pem files.",
}));
