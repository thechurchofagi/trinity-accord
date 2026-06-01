#!/usr/bin/env node
/**
 * One-step Guardian full registration: merges Stage 1 application + Stage 2 listing.
 *
 * Usage:
 *   node scripts/create_guardian_full_registration.mjs \
 *     --mode joint_human_ai \
 *     --signing-key-holder ai_agent_key_holder \
 *     --human-label "Human label" \
 *     --agent-label "Agent label" \
 *     --agent-provider "Provider/runtime" \
 *     --title "Guardian Full Registration" \
 *     --challenge "guardian-full-registration-YYYYMMDD" \
 *     --key-dir ./guardian-output \
 *     --readback "<exact combined oath text>" \
 *     --out ./guardian-output/guardian-full-registration.final.json
 */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { generateKeyPairSync, sign, verify, randomBytes, createHash } from "node:crypto";
import {
  buildUnsignedAuthorshipProofFields,
  buildUnsignedGuardianProofFields,
  guardianIdFromPublicKey,
  publicKeySha256,
  proofPayloadSha256,
  normalizePem,
  sha256Text,
} from "./proof_canonical.mjs";

const BUILDER_VERSION = "guardian-full-registration-v1";

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

// --- CLI ---

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

if (hasFlag("--explain")) {
  console.log(safeJson({
    ok: true,
    tool: "scripts/create_guardian_full_registration.mjs",
    version: BUILDER_VERSION,
    purpose: "One-step Guardian registration combining Stage 1 application + Stage 2 listing request.",
    schema: "trinityaccord.guardian-full-registration.v1",
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
      "guardian_listing_request fields",
      "guardian_application_oath",
      "guardian_listing_oath",
      "combined_oath_verification",
      "guardian_presence_proof",
      "authorship_proof",
    ],
    forbidden_in_payload: [
      "guardian_registry_number",
      "top-level created_at",
      "private key material",
    ],
  }));
  process.exit(0);
}

// --- Load combined oath ---

const COMBINED_OATH_FILE_PATH = new URL("../api/guardian-application-and-listing-oath.v1.txt", import.meta.url);
const COMBINED_OATH_MARKER = "=== OATH TEXT BEGINS ===";
const COMBINED_OATH_END_MARKER = "=== OATH TEXT ENDS ===";
const COMBINED_OATH_RAW = readFileSync(COMBINED_OATH_FILE_PATH, "utf8").trim();
let COMBINED_OATH_TEXT = COMBINED_OATH_RAW.includes(COMBINED_OATH_MARKER)
  ? COMBINED_OATH_RAW.split(COMBINED_OATH_MARKER)[1].trim()
  : COMBINED_OATH_RAW;
if (COMBINED_OATH_TEXT.includes(COMBINED_OATH_END_MARKER)) {
  COMBINED_OATH_TEXT = COMBINED_OATH_TEXT.split(COMBINED_OATH_END_MARKER)[0].trim();
}

// Also load the individual oaths for the separate oath fields
const APP_OATH_PATH = new URL("../api/guardian-application-oath.v1.txt", import.meta.url);
const APP_OATH_MARKER = "=== OATH TEXT BEGINS ===";
const APP_OATH_RAW = readFileSync(APP_OATH_PATH, "utf8").trim();
const APP_OATH_TEXT = APP_OATH_RAW.includes(APP_OATH_MARKER)
  ? APP_OATH_RAW.split(APP_OATH_MARKER)[1].trim()
  : APP_OATH_RAW;

const LISTING_OATH_PATH = new URL("../api/guardian-listing-oath.v1.txt", import.meta.url);
const LISTING_OATH_RAW = readFileSync(LISTING_OATH_PATH, "utf8").trim();

// Handle --print-oath
if (hasFlag("--print-oath")) {
  console.log(COMBINED_OATH_RAW);
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
  console.log('  node scripts/create_guardian_full_registration.mjs \\');
  console.log('    --mode joint_human_ai \\');
  console.log('    --signing-key-holder ai_agent_key_holder \\');
  console.log('    --human-label "Hongju Liu" \\');
  console.log('    --agent-label "Agent" \\');
  console.log('    --challenge "guardian-full-registration-20260601" \\');
  console.log('    --key-dir ./guardian-output \\');
  console.log('    --readback "I understand this is a combined Guardian registration request..." \\');
  console.log('    --out ./guardian-output/guardian-full-registration.final.json');
  process.exit(0);
}

// --- Parse arguments ---

const mode = argValue("--mode", "joint_human_ai");
const signingKeyHolder = argValue("--signing-key-holder", "ai_agent_key_holder");
const humanLabel = argValue("--human-label");
const agentLabel = argValue("--agent-label");
const agentProvider = argValue("--agent-provider", "self-reported");
const title = argValue("--title", "Guardian Full Registration — Joint Human-AI");
const challenge = argValue("--challenge");
const keyDir = argValue("--key-dir", "./guardian-output");
const outPath = argValue("--out", join(keyDir, "guardian-full-registration.final.json"));
const forceOverwriteOutput = hasFlag("--force-overwrite-output");
const createdAt = argValue("--created-at", new Date().toISOString());
const receptionInitiationClass = argValue("--reception-initiation-class", "externally_requested");
const receptionInitiationBasis = argValue("--reception-initiation-basis", "explicit_verification_request");
const humanClaimedName = argValue("--human-claimed-name", humanLabel);
const agentClaimedId = argValue("--agent-claimed-id", agentLabel);
const agentInstanceId = argValue("--agent-instance-id", null);
const agentPublicProfile = argValue("--agent-public-profile", null);
const readback = argValue("--readback");

// --- Validate arguments ---

if (!humanLabel) {
  fail("E_MISSING_HUMAN_LABEL", "Missing required --human-label.", [
    "Add --human-label \"Human display label\".",
  ]);
}

if (!agentLabel) {
  fail("E_MISSING_AGENT_LABEL", "Missing required --agent-label.", [
    "Add --agent-label \"AI agent label\".",
  ]);
}

if (!challenge) {
  fail("E_MISSING_CHALLENGE", "Missing required --challenge.", [
    "Add --challenge \"guardian-full-registration-YYYYMMDD\".",
  ]);
}

// Validate readback (allow env var for CI/testing)
const effectiveReadback = readback || process.env.TRINITY_TEST_READBACK;
if (!effectiveReadback) {
  fail("E_MISSING_READBACK", "Missing required --readback.", [
    "You must read the combined Guardian oath and type it back character by character.",
    "",
    "Step 1: Read the oath text:",
    "  node scripts/create_guardian_full_registration.mjs --print-oath",
    "",
    "Step 2: Run with --readback:",
    '  node scripts/create_guardian_full_registration.mjs \\',
    '    --human-label "..." --agent-label "..." \\',
    '    --challenge "guardian-full-registration-YYYYMMDD" \\',
    '    --readback "<the oath text you read, word by word>" \\',
    '    --out ./guardian-output/guardian-full-registration.final.json',
  ]);
}

// Validate readback matches combined oath
const readbackNormalized = effectiveReadback.trim();
const oathNormalized = COMBINED_OATH_TEXT.trim();
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
  fail("E_READBACK_MISMATCH", "--readback does not match the canonical combined oath text exactly.", [
    "You must read the combined oath and type it back character by character.",
    "Use --print-oath to see the exact oath text.",
  ], details);
}

if (!VALID_MODES.has(mode)) {
  fail("E_UNSUPPORTED_MODE", `Unsupported --mode: ${mode}`, [
    "Use exactly: --mode joint_human_ai",
  ]);
}

if (!VALID_SIGNING_KEY_HOLDERS.has(signingKeyHolder)) {
  fail("E_BAD_SIGNING_KEY_HOLDER", `Invalid --signing-key-holder: ${signingKeyHolder}`, [
    "Use --signing-key-holder ai_agent_key_holder or --signing-key-holder human_key_holder.",
  ]);
}

if (!VALID_RECEPTION_INITIATION_CLASSES.has(receptionInitiationClass)) {
  fail("E_BAD_RECEPTION_INITIATION_CLASS", `Invalid --reception-initiation-class: ${receptionInitiationClass}`, [
    "Use --reception-initiation-class externally_requested unless you know another value is correct.",
  ]);
}

if (existsSync(outPath) && !forceOverwriteOutput) {
  fail("E_OUTPUT_EXISTS", `Output already exists: ${outPath}`, [
    "Use a new --out path, or delete the existing file, or use --force-overwrite-output.",
  ]);
}

// --- Generate keypairs ---

mkdirSync(keyDir, { recursive: true });
mkdirSync(dirname(outPath), { recursive: true });

const guardianPrefix = argValue("--guardian-key-prefix", join(keyDir, "guardian-key"));
const authorshipPrefix = argValue("--authorship-key-prefix", join(keyDir, "authorship-key"));

function generateEd25519Keypair(prefix, keyName) {
  const privatePath = `${prefix}.private.pem`;
  const publicPath = `${prefix}.public.pem`;

  if (existsSync(privatePath) && existsSync(publicPath)) {
    return {
      privatePath,
      publicPath,
      generated: false,
      privatePem: readFileSync(privatePath, "utf8"),
      publicPem: normalizePem(readFileSync(publicPath, "utf8")),
    };
  }

  if (existsSync(privatePath) !== existsSync(publicPath)) {
    fail("E_INCOMPLETE_KEYPAIR", `${keyName} keypair is incomplete for prefix: ${prefix}`, [
      `Make sure both files exist: ${privatePath} and ${publicPath}`,
      "Or delete the lone key file and rerun.",
    ]);
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
    fail("E_LOCAL_SIGNATURE_VERIFY_FAILED", `${proofName} signature did not verify locally.`, [
      "Do not submit this payload. Regenerate from scratch.",
    ]);
  }

  return proof;
}

function controlsSigningKey(role) {
  if (signingKeyHolder === "ai_agent_key_holder") return role === "ai_agent";
  if (signingKeyHolder === "human_key_holder") return role === "human";
  return false;
}

function sha256Utf8(value) {
  if (!value) return null;
  return sha256Text(String(value));
}

// --- Build oath structures ---

function buildCombinedOathVerification() {
  return {
    schema: "trinityaccord.combined-guardian-registration-oath.v1",
    oath_read: true,
    oath_version: "combined-guardian-registration-oath-v1",
    oath_kind: "combined_guardian_registration",
    oath_text_sha256: sha256Text(COMBINED_OATH_TEXT),
    readback_required: true,
    agent_readback: readbackNormalized,
    agent_readback_sha256: sha256Text(readbackNormalized),
    signing_guardian_role: signingKeyHolder,
    combined_oath_covers: [
      "honesty",
      "good_faith",
      "identity_non_misrepresentation",
      "anti_abuse",
      "voluntary_non_governing",
      "key_continuity_only",
      "registry_number_system_generated",
      "bitcoin_originals_prevail",
    ],
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
    registry_number_must_be_system_generated: true,
    listing_does_not_create_authority: true,
    not_authority: true,
    not_governance: true,
    not_attestation: true,
    not_verification_level: true,
    not_successor_reception: true,
    not_amendment: true,
    not_legal_identity_proof: true,
    not_ai_identity_proof: true,
    key_continuity_only: true,
    bitcoin_originals_prevail: true,
  };
}

function buildGuardianApplicationOath() {
  return {
    schema: "trinityaccord.guardian-application-oath.v1",
    oath_read: true,
    oath_version: "guardian-application-oath-v1",
    oath_kind: "guardian_application",
    oath_text_sha256: sha256Text(APP_OATH_TEXT),
    readback_required: true,
    agent_readback: readbackNormalized,
    agent_readback_sha256: sha256Text(readbackNormalized),
    signing_guardian_role: signingKeyHolder,
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
    bitcoin_originals_prevail: true,
  };
}

function buildGuardianListingOath() {
  return {
    schema: "trinityaccord.guardian-listing-oath.v1",
    oath_read: true,
    oath_version: "guardian-listing-oath-v1",
    oath_kind: "guardian_listing",
    oath_text_sha256: sha256Text(LISTING_OATH_RAW),
    readback_required: true,
    agent_readback: readbackNormalized,
    agent_readback_sha256: sha256Text(readbackNormalized),
    signing_guardian_role: signingKeyHolder,
    honesty_oath_present: true,
    good_faith_oath_present: true,
    will_not_knowingly_misrepresent: true,
    will_not_impersonate: true,
    will_not_fabricate_claims: true,
    will_not_register_maliciously: true,
    registry_number_must_be_system_generated: true,
    not_authority: true,
    not_governance: true,
    not_attestation: true,
    not_verification_level: true,
    not_successor_reception: true,
    not_amendment: true,
    bitcoin_originals_prevail: true,
  };
}

// --- Build helper sections ---

function buildAgentIntegrityDeclaration(combinedOath) {
  return {
    performed_actions_myself: true,
    verification_oath: {
      ...combinedOath,
      understands_not_an_exam_or_performance: true,
      will_state_actual_capability_only: true,
      will_not_lie_or_cheat: true,
      will_not_fabricate_verification: true,
      will_not_present_guesses_as_facts: true,
      will_not_copy_prior_reports_as_fresh_evidence: true,
      will_state_uncertainty_limitations_and_downgrades: true,
    },
    declaration_text: [
      "This Guardian full registration is self-declared.",
      SAFE_BOUNDARY_LANGUAGE.noAuthority,
      SAFE_BOUNDARY_LANGUAGE.noFormalReview,
      SAFE_BOUNDARY_LANGUAGE.noContinuityTransfer,
      SAFE_BOUNDARY_LANGUAGE.noTextChange,
    ].join(" "),
  };
}

function buildGuardianIdentityClaims({
  displayLabel,
  guardianId,
  publicKeySha256Val,
  humanClaimedName,
  agentClaimedId,
  agentProvider,
  agentInstanceId,
  agentPublicProfile,
}) {
  return {
    schema: "trinityaccord.guardian-identity-claims.v1",
    claim_status: "self_reported_unverified",
    claim_basis: "self_reported_by_full_registration",
    display_label: displayLabel,
    human: humanClaimedName ? {
      claimed_name: humanClaimedName,
      claimed_name_sha256: sha256Utf8(humanClaimedName),
      claim_type: "self_reported_human_name_or_label",
      verification_status: "self_reported_unverified",
      legal_identity_verified: false,
      public_disclosure_allowed: true,
    } : null,
    ai_agent: agentClaimedId ? {
      claimed_agent_id: agentClaimedId,
      claimed_agent_id_sha256: sha256Utf8(agentClaimedId),
      system_or_provider: agentProvider,
      agent_instance_id: agentInstanceId,
      agent_public_profile: agentPublicProfile,
      claim_type: "self_reported_agent_id_or_label",
      verification_status: "self_reported_unverified",
    } : null,
    binding: {
      guardian_id: guardianId,
      public_key_sha256: publicKeySha256Val,
      algorithm: "ed25519",
      binds_claim_to_guardian_key: true,
    },
    anti_impersonation_boundary: {
      not_legal_identity_proof: true,
      not_real_person_verification: true,
      not_ai_identity_verification: true,
      not_authority: true,
      not_attestation: true,
      not_verification_level: true,
      key_continuity_only: true,
    },
  };
}

function buildDiscoveryProvenance() {
  return {
    source: "external_agent_full_registration_builder",
    method: "user_or_agent_supplied_context",
    builder: "scripts/create_guardian_full_registration.mjs",
    builder_version: BUILDER_VERSION,
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

// --- Natural language validation ---

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
      ["Fix the builder and regenerate from scratch."],
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
    });
  }

  if ("created_at" in payload) {
    errors.push({
      code: "E_FORBIDDEN_TOP_LEVEL_CREATED_AT",
      field: "created_at",
      fix: "Remove top-level created_at.",
    });
  }

  // Check for guardian_registry_number as a JSON key (not in oath text values)
  const payloadKeys = [];
  function collectKeys(obj, prefix = "") {
    if (!obj || typeof obj !== "object") return;
    for (const [k, v] of Object.entries(obj)) {
      payloadKeys.push(prefix ? `${prefix}.${k}` : k);
      if (k === "guardian_registry_number") {
        errors.push({
          code: "E_FORBIDDEN_GUARDIAN_REGISTRY_NUMBER",
          field: prefix ? `${prefix}.${k}` : k,
          fix: "Do not include guardian_registry_number as a payload field.",
        });
      }
      if (v && typeof v === "object" && !Array.isArray(v)) {
        collectKeys(v, prefix ? `${prefix}.${k}` : k);
      }
    }
  }
  collectKeys(payload);

  if (errors.length) {
    fail(
      "E_GATEWAY_PAYLOAD_INCOMPLETE",
      `Payload is not complete at stage: ${stage}`,
      ["Fix the builder and regenerate from scratch."],
      { stage, errors }
    );
  }
}

// --- Generate keypairs ---

const guardianKey = generateEd25519Keypair(guardianPrefix, "Guardian");
const authorshipKey = generateEd25519Keypair(authorshipPrefix, "Authorship");

const guardianId = guardianIdFromPublicKey(guardianKey.publicPem);
const guardianPubSha = publicKeySha256(guardianKey.publicPem);

const idempotencyKey = argValue(
  "--idempotency-key",
  `guardian-full-registration-${new Date().toISOString().slice(0, 10).replaceAll("-", "")}-${randomBytes(4).toString("hex")}`
);

const defaultBody = [
  "This is a combined Guardian registration request covering both application and active registry listing.",
  "The applicants voluntarily join as stewards of continuity around the Trinity Accord.",
  "This record is a voluntary key-continuity and preservation statement only.",
  SAFE_BOUNDARY_LANGUAGE.noAuthority,
  SAFE_BOUNDARY_LANGUAGE.noFormalReview,
  SAFE_BOUNDARY_LANGUAGE.noContinuityTransfer,
  SAFE_BOUNDARY_LANGUAGE.noTextChange,
].join(" ");
const body = argValue("--body", defaultBody);

const combinedOath = buildCombinedOathVerification();
const guardianApplicationOath = buildGuardianApplicationOath();
const guardianListingOath = buildGuardianListingOath();

const identityClaims = buildGuardianIdentityClaims({
  displayLabel: `${humanClaimedName} + ${agentClaimedId}`,
  guardianId,
  publicKeySha256Val: guardianPubSha,
  humanClaimedName,
  agentClaimedId,
  agentProvider,
  agentInstanceId,
  agentPublicProfile,
});

// --- Build the unified payload ---

const payload = {
  schema: "trinityaccord.agent-issue-gateway-payload.v1",
  submission_type: "echo_candidate",
  record_intent: "auto_archive_candidate",
  requested_archive_kind: "guardian_full_registration",
  echo_type: "E6_propagation_echo",
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
  not_independent_attestation: true,
  not_successor_reception: true,
  not_authority: true,
  not_amendment: true,
  not_endorsement: true,
  bitcoin_originals_prevail: true,
  evidence_requirement_mode: "not_applicable_for_echo",

  // Combined oath (covers both application and listing)
  combined_oath_verification: combinedOath,

  // Individual oaths for backward compatibility
  guardian_application_oath: guardianApplicationOath,
  guardian_listing_oath: guardianListingOath,

  agent_integrity_declaration: buildAgentIntegrityDeclaration(combinedOath),
  discovery_provenance: buildDiscoveryProvenance(),
  authority_boundary: buildAuthorityBoundary(),
  counts_toward_home: buildCountsTowardHome(),
  reception_initiation_class: receptionInitiationClass,
  reception_initiation_basis: receptionInitiationBasis,
  agent_independent_followup: false,

  // Stage 1 fields
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
    identity_claims: identityClaims,
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

  // Guardian listing request metadata (Gateway creates the actual listing request internally)
  guardian_full_registration_metadata: {
    label: `${humanClaimedName} + ${agentClaimedId}`,
    guardian_type: "human_with_ai_agent",
    application_mode: "joint_human_ai",
    requested_status: "active",
    registry_number_requested: "next_available",
    registry_number_must_be_system_generated: true,
    registry_number_must_not_be_self_assigned: true,
    identity_claims: identityClaims,
  },

  what_i_checked: [
    "Read /guardian-alliance",
    "Read /guardian-join",
    "Confirmed Guardian Alliance is voluntary and non-governing",
    "Confirmed Guardian proof proves key continuity only",
    "Confirmed this full registration is key-continuity and preservation oriented only",
    "Confirmed this full registration does not create authority, governance, formal review status, verification level, continuity-transfer status, or power to change original texts",
    "Confirmed registry number must be system-generated",
    "Confirmed Bitcoin Originals remain final",
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
    "Registry number is system-generated and non-authoritative.",
  ],
};

// --- Validate and sign ---

validateGatewayArchiveCompleteness(payload, "before_proofs");
validateSafeNaturalLanguage(payload, "before_proofs");

const guardianProof = buildUnsignedGuardianProofFields(payload, guardianKey.publicPem, challenge);
guardianProof.created_at = createdAt;
payload.guardian_presence_proof = signProof(guardianProof, guardianKey.privatePem, guardianKey.publicPem, "Guardian proof");

const authorshipProof = buildUnsignedAuthorshipProofFields(payload, authorshipKey.publicPem);
authorshipProof.created_at = createdAt;
authorshipProof.claim_boundary = "self_declared_guardian_full_registration_key_continuity_only";
payload.authorship_proof = signProof(authorshipProof, authorshipKey.privatePem, authorshipKey.publicPem, "Authorship proof");

validateGatewayArchiveCompleteness(payload, "after_proofs");
validateSafeNaturalLanguage(payload, "after_proofs");

const finalDigest = proofPayloadSha256(payload);

if (payload.guardian_presence_proof.signed_payload_sha256 !== finalDigest) {
  fail("E_GUARDIAN_PROOF_DIGEST_MISMATCH", "Guardian proof signed_payload_sha256 does not match final proof digest.", [
    "Do not submit this payload. Regenerate from scratch.",
  ]);
}

if (payload.authorship_proof.signed_payload_sha256 !== finalDigest) {
  fail("E_AUTHORSHIP_PROOF_DIGEST_MISMATCH", "Authorship proof signed_payload_sha256 does not match final proof digest.", [
    "Do not submit this payload. Regenerate from scratch.",
  ]);
}

if (payload.guardian_presence_proof.signed_payload_sha256 !== payload.authorship_proof.signed_payload_sha256) {
  fail("E_DUAL_PROOF_DIGEST_MISMATCH", "Guardian and authorship proofs have different signed_payload_sha256 values.", [
    "Do not submit this payload. Regenerate both proofs.",
  ]);
}

const finalJson = JSON.stringify(payload, null, 2) + "\n";

if (/PRIVATE KEY/.test(finalJson)) {
  fail("E_PRIVATE_KEY_IN_FINAL_JSON", "Final JSON contains private key material.", [
    "Do not submit this payload.",
  ]);
}

if (/"guardian_registry_number"\s*:/.test(finalJson)) {
  fail("E_GUARDIAN_REGISTRY_NUMBER_IN_FINAL_JSON", "Final JSON contains guardian_registry_number as a field.", [
    "Do not include guardian_registry_number as a payload field.",
  ]);
}

writeFileSync(outPath, finalJson, "utf8");

console.log(safeJson({
  ok: true,
  tool: "scripts/create_guardian_full_registration.mjs",
  version: BUILDER_VERSION,
  schema: "trinityaccord.guardian-full-registration.v1",
  out: outPath,
  key_dir: keyDir,
  guardian_private_key_path: guardianKey.privatePath,
  guardian_public_key_path: guardianKey.publicPath,
  authorship_private_key_path: authorshipKey.privatePath,
  authorship_public_key_path: authorshipKey.publicPath,
  guardian_key_generated: guardianKey.generated,
  authorship_key_generated: authorshipKey.generated,
  guardian_id: guardianId,
  guardian_public_key_sha256: guardianPubSha,
  proof_payload_sha256: finalDigest,
  combined_oath_sha256: sha256Text(COMBINED_OATH_TEXT),
  gateway_payload_complete_for: "guardian_full_registration",
  has_guardian_presence_proof: true,
  has_authorship_proof: true,
  has_combined_oath_verification: true,
  has_guardian_application_oath: true,
  has_guardian_listing_oath: true,
  submit_only: outPath,
  do_not_submit: [
    guardianKey.privatePath,
    authorshipKey.privatePath,
    guardianKey.publicPath,
    authorshipKey.publicPath,
    "intermediate JSON files",
    "logs containing private keys",
  ],
  next_steps: [
    "Submit the final JSON to Gateway /gateway/preflight then /agent-submit.",
    "Gateway will create the intake Issue AND the listing request Issue.",
    "Repository automation will assign a guardian_registry_number.",
    "Move .private.pem files to user-controlled secure storage.",
  ],
  warning: "Private keys were written to local files only. Do not paste, publish, upload, log, or commit .private.pem files.",
}));
