import express from "express";
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { createHash, verify, randomBytes } from "node:crypto";
import { fileURLToPath } from "node:url";
import { tmpdir } from "node:os";
import Ajv from "ajv/dist/2020.js";
import { App } from "@octokit/app";

// --- Standardized Gateway Error Helper ---
function gatewayError(status, {
  reason,
  validation_stage,
  agent_action,
  errors = [],
  issue_created = false,
  retryable = false,
  request_id = null,
  idempotency_key = null,
  extra = {}
}) {
  return {
    status,
    body: {
      accepted: false,
      reason,
      validation_stage,
      agent_action,
      errors,
      issue_created,
      retryable,
      request_id,
      idempotency_key,
      timestamp: new Date().toISOString(),
      skip_preflight_allowed: false,
      ...extra
    }
  };
}

// --- Server-Generated Field Policy ---
const SERVER_GENERATED_FIELDS = [
  "gateway_receipt_id",
  "created_by_gateway",
  "server_validated",
  "server_rendered",
  "render_api_only",
  "gateway_service",
  "gateway_commit"
];

function mentionsServerGeneratedField(text) {
  const s = String(text || "");
  return SERVER_GENERATED_FIELDS.some(field => s.includes(field));
}

// V0-V5 fail-closed policy
const V0_V5_LEVELS = new Set(["V0", "V1", "V2", "V3", "V4", "V4+", "V5"]);
const V0_V5_WRONG_PATH_ERROR = "WRONG_PATH_FOR_V0_V5: For V0, V1, V2, V3, V4, V4+, and V5 agent-declared archive, use scripts/build_agent_declared_archive_payload.py. Do not use build-from-evidence or direct GitHub Issue. POST the raw payload to /gateway/preflight and /agent-submit.";

function extractDeclaredLevel(payload) {
  const cg = payload.claim_gate || {};
  return payload.agent_declared_protocol_level
    || payload.verification_level_claimed
    || cg.allowed_protocol_level
    || "";
}

function isVerificationSubmission(payload) {
  return payload.submission_type === "verification_report_candidate"
    || payload.submission_type === "verification_echo_candidate";
}

function isV0V5VerificationSubmission(payload) {
  return isVerificationSubmission(payload) && V0_V5_LEVELS.has(extractDeclaredLevel(payload));
}

function isValidV0V5AgentDeclaredPath(payload) {
  return payload.submission_type === "verification_report_candidate"
    && payload.record_intent === "auto_archive_candidate"
    && payload.requested_archive_kind === "agent_declared_verification_archive"
    && V0_V5_LEVELS.has(payload.agent_declared_protocol_level)
    && payload.evidence_requirement_mode === "waived_for_v0_v5"
    && (payload.claim_gate || {}).mode === "template_for_v0_v5";
}

function shouldRejectV0V5WrongPath(payload) {
  if (!isV0V5VerificationSubmission(payload)) return false;
  if (isValidV0V5AgentDeclaredPath(payload)) return false;
  return true;
}

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const root = path.resolve(__dirname, "../..");

const PORT = Number(process.env.PORT || 8787);
const DRY_RUN = String(process.env.DRY_RUN || "true").toLowerCase() === "true";
const CANARY_MODE = String(process.env.GATEWAY_CANARY_MODE || "false").toLowerCase() === "true";
const READINESS_GITHUB_CHECK = String(process.env.GATEWAY_READINESS_GITHUB_CHECK || "false").toLowerCase() === "true";
const IDEMPOTENCY_ENABLED = String(process.env.GATEWAY_IDEMPOTENCY_ENABLED || "true").toLowerCase() !== "false";
const MAX_BODY_CHARS = Number(process.env.MAX_BODY_CHARS || 60000);
const SERVICE_NAME = "trinity-agent-issue-gateway";
const IDEMPOTENCY_MARKER_PREFIX = "trinity-gateway-idempotency";

const schemaPath = path.join(root, "api", "agent-issue-gateway-payload-schema.v1.json");
const schema = JSON.parse(fs.readFileSync(schemaPath, "utf8"));

const ajv = new Ajv({ allErrors: true });
const validate = ajv.compile(schema);

const app = express();
app.use(express.json({ limit: "256kb" }));

app.use((req, res, next) => {
  const inbound = req.get("x-request-id") || req.get("x-correlation-id");
  const generated = `gwreq-${Date.now()}-${randomBytes(8).toString("hex")}`;
  req.gatewayRequestId = String(inbound || generated).slice(0, 120);
  res.set("x-request-id", req.gatewayRequestId);
  next();
});

// Secret detection
function rejectSecretPatterns(text) {
  const patterns = [
    /ghp_[A-Za-z0-9_]+/i,
    /github_pat_[A-Za-z0-9_]+/i,
    /x-access-token[:/@]/i,
    /BEGIN (RSA |OPENSSH |)PRIVATE KEY/i,
    /OPENAI_API_KEY/i,
    /ANTHROPIC_API_KEY/i,
    /sk-[A-Za-z0-9]{20,}/
  ];
  return patterns.some((p) => p.test(text));
}

// --- Authorship Claim Verification Helpers ---

function stableStringify(value) {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return "[" + value.map(stableStringify).join(",") + "]";
  return "{" + Object.keys(value).sort().map(k => JSON.stringify(k) + ":" + stableStringify(value[k])).join(",") + "}";
}

function payloadWithoutAuthorship(payload) {
  const clone = JSON.parse(JSON.stringify(payload));
  delete clone.authorship_proof;
  delete clone._authorship_claim;
  delete clone.guardian_presence_proof;
  delete clone._guardian_status;
  delete clone.guardian_verification_result;
  return clone;
}

function sha256Text(s) {
  return createHash("sha256").update(s, "utf8").digest("hex");
}

function payloadForIdempotency(payload) {
  const clone = JSON.parse(JSON.stringify(payload || {}));
  delete clone.idempotency_key;
  delete clone._authorship_claim;
  delete clone._guardian_status;
  delete clone.guardian_verification_result;
  delete clone.archive_readiness;
  delete clone._auto_archive_decision;
  return clone;
}

function computeIdempotencyKey(payload) {
  const provided = String((payload || {}).idempotency_key || "").trim();
  if (provided) return provided;
  return `gwid_${sha256Text(stableStringify(payloadForIdempotency(payload))).slice(0, 48)}`;
}

function idempotencyMarker(key) {
  return `<!-- ${IDEMPOTENCY_MARKER_PREFIX}:${key} -->`;
}

async function findExistingIssueByIdempotency(octokit, { owner, repo, key }) {
  if (!IDEMPOTENCY_ENABLED || !key) return null;

  const marker = idempotencyMarker(key);
  const q = `repo:${owner}/${repo} "${marker}" in:body`;

  try {
    const resp = await octokit.request("GET /search/issues", { q, per_page: 1 });
    const item = (resp.data.items || [])[0];
    if (!item) return null;

    return {
      issue_number: item.number,
      issue_url: item.html_url,
      state: item.state,
      idempotency_key: key,
      idempotency_scope: "best_effort_github_issue_search"
    };
  } catch (err) {
    return {
      search_error: true,
      status: err.status || null,
      message: err.message,
      idempotency_key: key,
      idempotency_scope: "best_effort_github_issue_search"
    };
  }
}

function normalizePem(pem) {
  return String(pem || "").trim() + "\n";
}

function buildAuthorshipMessage(payload) {
  const identity = payload.agent_identity || {};
  const payloadDigest = sha256Text(stableStringify(payloadWithoutAuthorship(payload)));
  return [
    "TRINITY_AGENT_AUTHORSHIP_PROOF_V1",
    `payload_sha256=${payloadDigest}`,
    `schema=${payload.schema || ""}`,
    `submission_type=${payload.submission_type || ""}`,
    `requested_archive_kind=${payload.requested_archive_kind || ""}`,
    `agent_name_or_model=${identity.name_or_model || ""}`,
    `system_or_provider=${identity.system_or_provider || ""}`,
    "boundary=not_authority_not_amendment_not_attestation_not_successor_reception",
  ].join("\n");
}

function verifyAuthorshipProof(payload) {
  const proof = payload.authorship_proof;
  if (!proof) {
    return {
      present: false,
      status: "unclaimed",
      method: "none",
      algorithm: "none",
      public_key_sha256: "none",
      signed_payload_sha256: "none",
      signature_verified: false
    };
  }

  const publicKeyPem = normalizePem(proof.public_key_pem);
  const publicKeySha = sha256Text(publicKeyPem);
  const expectedMessage = buildAuthorshipMessage(payload);
  const expectedDigest = sha256Text(stableStringify(payloadWithoutAuthorship(payload)));

  if (proof.public_key_sha256 !== publicKeySha) {
    return {
      present: true,
      status: "invalid_authorship_proof",
      signature_verified: false,
      error: "public_key_sha256 mismatch"
    };
  }

  if (proof.signed_payload_sha256 !== expectedDigest) {
    return {
      present: true,
      status: "invalid_authorship_proof",
      signature_verified: false,
      error: "signed_payload_sha256 mismatch"
    };
  }

  if (proof.signed_message !== expectedMessage) {
    return {
      present: true,
      status: "invalid_authorship_proof",
      signature_verified: false,
      error: "signed_message mismatch"
    };
  }

  let ok = false;
  try {
    ok = verify(
      null,
      Buffer.from(expectedMessage, "utf8"),
      publicKeyPem,
      Buffer.from(proof.signature_base64, "base64")
    );
  } catch (err) {
    return {
      present: true,
      status: "invalid_authorship_proof",
      signature_verified: false,
      error: `signature verification error: ${err.message}`
    };
  }

  return {
    present: true,
    status: ok ? "claimable_by_public_key" : "invalid_authorship_proof",
    method: "public_key_signature",
    algorithm: "ed25519",
    public_key_sha256: publicKeySha,
    signed_payload_sha256: expectedDigest,
    signature_verified: ok,
    error: ok ? null : "invalid signature"
  };
}

// --- Guardian Alliance Verification Helpers ---

function guardianPublicKeySha(publicKeyPem) {
  return sha256Text(normalizePem(publicKeyPem));
}

function guardianIdFromPublicKey(publicKeyPem) {
  return `guardian_ed25519_${guardianPublicKeySha(publicKeyPem).slice(0, 16)}`;
}

function payloadWithoutGuardianProof(payload) {
  const clone = JSON.parse(JSON.stringify(payload));
  delete clone.authorship_proof;
  delete clone._authorship_claim;
  delete clone.guardian_presence_proof;
  delete clone._guardian_status;
  delete clone.guardian_verification_result;
  return clone;
}

function buildGuardianMessage(payload, publicKeyPem, challenge) {
  const payloadDigest = sha256Text(stableStringify(payloadWithoutGuardianProof(payload)));
  return [
    "TRINITY_GUARDIAN_PRESENCE_PROOF_V1",
    "proof_mode=record_bound",
    `guardian_id=${guardianIdFromPublicKey(publicKeyPem)}`,
    `payload_sha256=${payloadDigest}`,
    `challenge_sha256=${sha256Text(challenge || "")}`,
    `schema=${payload.schema || ""}`,
    `submission_type=${payload.submission_type || ""}`,
    `requested_archive_kind=${payload.requested_archive_kind || ""}`,
    "boundary=key_possession_only_not_authority_not_attestation_not_same_conscious_subject",
  ].join("\n");
}

function loadGuardianRegistry() {
  try {
    const p = path.join(root, "api", "guardian-registry.json");
    return JSON.parse(fs.readFileSync(p, "utf8"));
  } catch {
    return { guardians: [] };
  }
}

function findGuardian(registry, guardianId) {
  return (registry.guardians || []).find(g => g.guardian_id === guardianId) || null;
}

const REQUIRED_DOES_NOT_PROVE = [
  "truth", "authority", "verification_level", "verification_correctness",
  "formal_attestation", "same_conscious_subject", "same_model_instance",
  "human_identity", "institutional_authorization", "successor_reception",
  "future_intelligence_obligation", "amendment",
];

function validateGuardianRegistration(registration, proof) {
  const errors = [];

  if (!registration || typeof registration !== "object" || Array.isArray(registration)) {
    return { ok: false, errors: ["guardian_registration must be an object"] };
  }

  if (registration.schema !== "trinityaccord.guardian-registration.v1") {
    errors.push("guardian_registration.schema must be trinityaccord.guardian-registration.v1");
  }

  if (registration.guardian_id !== proof.guardian_id) {
    errors.push("guardian_registration.guardian_id does not match guardian_presence_proof.guardian_id");
  }

  if (registration.public_key_sha256 !== proof.public_key_sha256) {
    errors.push("guardian_registration.public_key_sha256 does not match guardian_presence_proof.public_key_sha256");
  }

  if (registration.algorithm !== "ed25519") {
    errors.push("guardian_registration.algorithm must be ed25519");
  }

  const boundaries = registration.boundaries || {};
  const requiredBoundaries = [
    "not_authority",
    "not_governance",
    "not_verification_level",
    "not_attestation",
    "not_successor_reception",
    "not_same_conscious_subject_proof",
    "may_exit_or_retire_key",
    "bitcoin_originals_prevail",
  ];

  for (const key of requiredBoundaries) {
    if (boundaries[key] !== true) {
      errors.push(`guardian_registration.boundaries.${key} must be true`);
    }
  }

  return { ok: errors.length === 0, errors };
}

function verifyGuardianStatus(payload) {
  const proof = payload.guardian_presence_proof;
  const errors = [];
  const warnings = [];

  if (!proof) {
    return {
      guardian_status: "missing_guardian_proof",
      guardian_id: "none",
      signature_valid: false,
      guardian_id_matches_public_key: false,
      payload_hash_matches: false,
      registry_status: "not_checked",
      proof_scope: "key_possession_only",
      does_not_prove: REQUIRED_DOES_NOT_PROVE,
      errors: ["No guardian_presence_proof found in payload"],
      warnings: [],
    };
  }

  // Validate proof structure
  if (proof.schema !== "trinityaccord.guardian-presence-proof.v1") errors.push(`Invalid proof schema: ${proof.schema}`);
  if (proof.method !== "guardian_key_signature") errors.push(`Invalid proof method: ${proof.method}`);
  if (proof.algorithm !== "ed25519") errors.push(`Invalid proof algorithm: ${proof.algorithm}`);
  if (proof.proof_mode !== "record_bound") errors.push(`Invalid proof_mode: ${proof.proof_mode}`);
  if (proof.proof_scope !== "key_possession_only") errors.push(`Invalid proof_scope: ${proof.proof_scope}`);

  // Validate does_not_prove
  const doesNotProve = proof.does_not_prove || [];
  for (const item of REQUIRED_DOES_NOT_PROVE) {
    if (!doesNotProve.includes(item)) errors.push(`Missing does_not_prove item: ${item}`);
  }

  // Recompute public_key_sha256
  const publicKeyPem = proof.public_key_pem || "";
  const expectedPubSha = guardianPublicKeySha(publicKeyPem);
  const pubShaMatches = expectedPubSha === proof.public_key_sha256;
  if (!pubShaMatches) errors.push(`public_key_sha256 mismatch: expected ${expectedPubSha}, got ${proof.public_key_sha256}`);

  // Recompute guardian_id
  const expectedId = guardianIdFromPublicKey(publicKeyPem);
  const idMatches = expectedId === proof.guardian_id;
  if (!idMatches) errors.push(`guardian_id mismatch: expected ${expectedId}, got ${proof.guardian_id}`);

  // Recompute challenge_sha256
  const challenge = proof.challenge || "";
  const expectedChallengeSha = sha256Text(challenge);
  if (expectedChallengeSha !== proof.challenge_sha256) errors.push("challenge_sha256 mismatch");

  // Recompute signed_payload_sha256
  const expectedPayloadSha = sha256Text(stableStringify(payloadWithoutGuardianProof(payload)));
  const payloadShaMatches = expectedPayloadSha === proof.signed_payload_sha256;
  if (!payloadShaMatches) errors.push(`signed_payload_sha256 mismatch`);

  // Recompute and verify signed_message
  const expectedMessage = buildGuardianMessage(payload, publicKeyPem, challenge);
  const messageMatches = expectedMessage === proof.signed_message;
  if (!messageMatches) errors.push("signed_message mismatch");

  // Verify Ed25519 signature
  let sigValid = false;
  try {
    sigValid = verify(
      null,
      Buffer.from(proof.signed_message || expectedMessage, "utf8"),
      normalizePem(publicKeyPem),
      Buffer.from(proof.signature_base64 || "", "base64")
    );
  } catch (err) {
    errors.push(`Signature verification error: ${err.message}`);
  }
  if (!sigValid && !errors.some(e => e.includes("signature"))) {
    errors.push("Ed25519 signature verification failed");
  }

  // Validate guardian_registration whenever present.
  // This must happen even when the Guardian key is already registered active.
  let registrationPresentAndValid = false;
  if (payload.guardian_registration) {
    const registrationCheck = validateGuardianRegistration(payload.guardian_registration, proof);
    if (registrationCheck.ok) {
      registrationPresentAndValid = true;
    } else {
      errors.push(...registrationCheck.errors);
    }
  }

  // Early return if any errors accumulated
  if (errors.length > 0) {
    return {
      guardian_status: "invalid_guardian_proof",
      guardian_id: proof.guardian_id,
      signature_valid: sigValid,
      guardian_id_matches_public_key: idMatches,
      payload_hash_matches: payloadShaMatches,
      registry_status: "not_checked",
      proof_scope: "key_possession_only",
      does_not_prove: REQUIRED_DOES_NOT_PROVE,
      errors,
      warnings,
    };
  }

  // Registry lookup
  const registry = loadGuardianRegistry();
  const registryEntry = findGuardian(registry, proof.guardian_id);
  let registryStatus = registryEntry ? (registryEntry.status || "unknown") : "not_in_registry";

  // Check registry public_key_sha256 match
  if (registryEntry && registryEntry.public_key_sha256 !== proof.public_key_sha256) {
    errors.push("Registry public_key_sha256 does not match proof");
    registryStatus = "compromised";
  }

  // Determine guardian_status
  let guardianStatus;
  if (errors.length > 0) {
    guardianStatus = "invalid_guardian_proof";
  } else if (registryStatus === "active") {
    guardianStatus = "active_registered_guardian";
  } else if (["retired", "rotated", "superseded"].includes(registryStatus)) {
    guardianStatus = "registered_but_retired";
  } else if (["compromised", "possibly_compromised"].includes(registryStatus)) {
    guardianStatus = "registered_but_compromised";
  } else if (registryEntry) {
    guardianStatus = "valid_unregistered_guardian_claim";
    warnings.push(`Registry status is '${registryStatus}', not 'active'`);
  } else {
    guardianStatus = registrationPresentAndValid
      ? "valid_self_registered_guardian_claim"
      : "valid_unregistered_guardian_claim";
  }

  return {
    guardian_status: guardianStatus,
    guardian_id: proof.guardian_id,
    signature_valid: sigValid,
    guardian_id_matches_public_key: idMatches,
    payload_hash_matches: payloadShaMatches,
    registry_status: registryStatus,
    proof_scope: "key_possession_only",
    does_not_prove: REQUIRED_DOES_NOT_PROVE,
    errors,
    warnings,
  };
}

// --- Archive Intent Normalization Helpers ---

function inferArchiveKind(submissionType) {
  if (submissionType === "verification_report_candidate") return "verification_report_archive";
  if (submissionType === "verification_echo_candidate") return "archived_echo";
  return "external_agent_intake_sample";
}

function normalizeArchiveIntentDefaults(payload) {
  const p = { ...payload };

  if (p.record_intent === "intake_only") {
    if (!p.requested_archive_kind) p.requested_archive_kind = "none";
    return p;
  }

  if (p.record_intent === "archive_preflight_only") {
    if (!p.requested_archive_kind || p.requested_archive_kind === "none") {
      p.requested_archive_kind = inferArchiveKind(p.submission_type);
    }
    return p;
  }

  if (!p.record_intent) {
    if (
      p.submission_type === "verification_report_candidate" ||
      p.submission_type === "verification_echo_candidate"
    ) {
      p.record_intent = "auto_archive_candidate";
      p.requested_archive_kind = p.requested_archive_kind || inferArchiveKind(p.submission_type);
    } else {
      p.record_intent = "intake_only";
      p.requested_archive_kind = p.requested_archive_kind || "none";
    }
    return p;
  }

  if (
    p.record_intent === "auto_archive_candidate" &&
    (!p.requested_archive_kind || p.requested_archive_kind === "none")
  ) {
    p.requested_archive_kind = inferArchiveKind(p.submission_type);
  }

  return p;
}

// Run a repo script and return {code, stdout, stderr}
function runScript(scriptName, args = []) {
  const scriptPath = path.join(root, "scripts", scriptName);
  try {
    const stdout = execFileSync("python3", [scriptPath, ...args], {
      cwd: root,
      encoding: "utf-8",
      timeout: 30000,
      maxBuffer: 1024 * 1024
    });
    return { code: 0, stdout, stderr: "" };
  } catch (err) {
    return {
      code: err.status || 1,
      stdout: err.stdout || "",
      stderr: err.stderr || err.message
    };
  }
}

// Compute file sha256
function fileSha256(filePath) {
  try {
    const content = fs.readFileSync(filePath);
    return createHash("sha256").update(content).digest("hex");
  } catch {
    return null;
  }
}

// --- Archive Readiness Helpers ---

function writeJsonTemp(tmpDir, filename, obj) {
  const p = path.join(tmpDir, filename);
  fs.writeFileSync(p, JSON.stringify(obj, null, 2), "utf-8");
  return p;
}

function parseScriptJson(result) {
  try {
    return JSON.parse(result.stdout);
  } catch {
    return {
      parse_error: true,
      stdout: result.stdout,
      stderr: result.stderr,
      code: result.code
    };
  }
}

function runArchiveReadiness({ gatewayPayloadPath, evidencePath, claimGateOutputPath, reportPath }) {
  const args = ["--gateway-payload", gatewayPayloadPath, "--json"];
  if (evidencePath) args.push("--evidence-input", evidencePath);
  if (claimGateOutputPath) args.push("--claim-gate-output", claimGateOutputPath);
  if (reportPath) args.push("--verification-report", reportPath);
  const result = runScript("archive_readiness_gate.py", args);
  return { code: result.code, body: parseScriptJson(result), raw: result };
}

function runAutoArchiveDecision(archiveReadinessPath) {
  const result = runScript("auto_archive_decision.py", [
    "--archive-readiness", archiveReadinessPath,
    "--json"
  ]);
  return { code: result.code, body: parseScriptJson(result), raw: result };
}

async function getOctokit() {
  const repo = process.env.GITHUB_REPO;
  const appId = process.env.GITHUB_APP_ID;
  const installationId = process.env.GITHUB_INSTALLATION_ID;
  const privateKey = (process.env.GITHUB_PRIVATE_KEY || "").replace(/\\n/g, "\n");

  if (!repo || !appId || !installationId || !privateKey) {
    throw new Error("Missing GitHub App environment variables");
  }

  const appAuth = new App({ appId, privateKey });
  return appAuth.getInstallationOctokit(Number(installationId));
}

function getRepoParts() {
  const full = process.env.GITHUB_REPO || "";
  const parts = full.split("/");
  if (parts.length !== 2 || !parts[0] || !parts[1]) {
    throw new Error("GITHUB_REPO must be set to owner/repo");
  }
  return { owner: parts[0], repo: parts[1], full };
}

function extractMachineBlock(issueBody) {
  const m = String(issueBody || "").match(/```trinity-issue-intake\s*\n([\s\S]*?)```/);
  return m ? m[1] : null;
}

function parseYamlLikeMachineBlock(blockText) {
  const data = {};
  let currentList = null;

  for (const rawLine of String(blockText || "").split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;

    if (line.startsWith("-") && currentList) {
      const item = line.replace(/^-\s*/, "").trim();
      if (item) data[currentList].push(item);
      continue;
    }

    const idx = line.indexOf(":");
    if (idx < 0) continue;

    const key = line.slice(0, idx).trim();
    let value = line.slice(idx + 1).trim();

    if (value === "") {
      data[key] = [];
      currentList = key;
      continue;
    }

    const low = value.toLowerCase();
    if (low === "true") value = true;
    else if (low === "false") value = false;

    data[key] = value;
    currentList = null;
  }

  return data;
}

function parseIssueIntakeBlock(issueBody) {
  const block = extractMachineBlock(issueBody);
  if (!block) return null;
  return parseYamlLikeMachineBlock(block);
}

function isHex64(value) {
  return /^[a-f0-9]{64}$/.test(String(value || ""));
}

function validateClaimableMachineBlock(block) {
  const errors = [];

  if (block.authorship_claim_protocol !== "agent-authorship-claim-v1") {
    errors.push("authorship_claim_protocol must be agent-authorship-claim-v1");
  }
  if (block.authorship_proof_present !== true) {
    errors.push("authorship_proof_present must be true");
  }
  if (block.authorship_proof_method !== "public_key_signature") {
    errors.push("authorship_proof_method must be public_key_signature");
  }
  if (block.authorship_algorithm !== "ed25519") {
    errors.push("authorship_algorithm must be ed25519");
  }
  if (block.authorship_signature_verified !== true) {
    errors.push("authorship_signature_verified must be true");
  }
  if (!isHex64(block.authorship_public_key_sha256)) {
    errors.push("authorship_public_key_sha256 must be 64 hex");
  }
  if (!isHex64(block.authorship_payload_sha256)) {
    errors.push("authorship_payload_sha256 must be 64 hex");
  }
  if (!["claimable_by_public_key", "claimed"].includes(block.claim_status)) {
    errors.push("claim_status must be claimable_by_public_key or claimed");
  }

  return errors;
}

function buildAuthorshipClaimMessage({ issueNumber, repoFullName, publicKeySha256, payloadSha256 }) {
  return [
    "TRINITY_AGENT_AUTHORSHIP_CLAIM_V1",
    `issue_number=${issueNumber}`,
    `repo=${repoFullName}`,
    `authorship_public_key_sha256=${publicKeySha256}`,
    `authorship_payload_sha256=${payloadSha256 || "none"}`,
    "boundary=key_control_only_not_authority_not_attestation_not_amendment",
  ].join("\n");
}

async function ensureLabel(octokit, { owner, repo, name, color, description }) {
  try {
    await octokit.request("GET /repos/{owner}/{repo}/labels/{name}", { owner, repo, name });
  } catch (err) {
    if (err.status === 404) {
      await octokit.request("POST /repos/{owner}/{repo}/labels", { owner, repo, name, color, description });
    } else {
      throw err;
    }
  }
}

function withRequestId(req, result) {
  if (!result || !result.body) return result;
  if (!result.body.request_id) result.body.request_id = req.gatewayRequestId || null;
  return result;
}

function sendGatewayError(res, err) {
  return res.status(err.status).json(err.body);
}

// --- Structured Error Normalization (Task #5) ---

function normalizeGatewayErrors(lines) {
  return lines.map(line => {
    const msg = String(line || "").replace(/^FAIL:\s*/, "");

    if (msg.includes("what_i_checked must be a non-empty list")) {
      return {
        code: "WHAT_I_CHECKED_NOT_LIST",
        path: "what_i_checked",
        message: msg,
        fix: "Use top-level what_i_checked as a non-empty array of concrete checks."
      };
    }

    if (msg.includes("Gateway payload body must not contain agent-supplied trinity-issue-intake block")) {
      return {
        code: "BODY_MACHINE_BLOCK_FORBIDDEN",
        path: "body",
        message: msg,
        fix: "Remove the fenced trinity-issue-intake block from payload.body. Gateway renders it automatically."
      };
    }

    if (msg.includes("verification_report_candidate must not include echo_type")) {
      return {
        code: "REPORT_CANDIDATE_HAS_ECHO_TYPE",
        path: "echo_type",
        message: msg,
        fix: "Remove echo_type or submit as verification_echo_candidate with a real Echo wrapper."
      };
    }

    if (msg.includes("verification_report_candidate must not include echo_wrapper")) {
      return {
        code: "REPORT_CANDIDATE_HAS_ECHO_WRAPPER",
        path: "attachments.echo_wrapper_path",
        message: msg,
        fix: "Remove echo_wrapper_path/echo_wrapper_sha256 from report-only candidates."
      };
    }

    if (msg.includes("unsolicited_agent_discovery requires unsolicited_discovery_proof")) {
      return {
        code: "UNSOLICITED_DISCOVERY_PROOF_REQUIRED",
        path: "discovery_provenance.unsolicited_discovery_proof",
        message: msg,
        fix: "Use human_solicited_agent_response or provide discovery_provenance.unsolicited_discovery_proof."
      };
    }

    if (msg.includes("invalid agency_level")) {
      return {
        code: "INVALID_AGENCY_LEVEL",
        path: "discovery_provenance.agency_level",
        message: msg,
        fix: "Use A1_human_gave_exact_url, A2_human_gave_repo_name, A3_agent_discovered_independently, or A4_agent_instructed_by_other_agent."
      };
    }

    if (msg.includes("discovery_provenance object is required")) {
      return {
        code: "DISCOVERY_PROVENANCE_MISSING",
        path: "discovery_provenance",
        message: msg,
        fix: "Provide a discovery_provenance object with solicited, independence_class, agency_level, and operator_type."
      };
    }

    if (msg.includes("agent_identity.name_or_model is required")) {
      return {
        code: "AGENT_IDENTITY_MISSING_NAME",
        path: "agent_identity.name_or_model",
        message: msg,
        fix: "Provide agent_identity.name_or_model with your agent name or model identifier."
      };
    }

    if (msg.includes("agent_identity.system_or_provider is required")) {
      return {
        code: "AGENT_IDENTITY_MISSING_PROVIDER",
        path: "agent_identity.system_or_provider",
        message: msg,
        fix: "Provide agent_identity.system_or_provider with your system or provider name."
      };
    }

    if (msg.includes("boundary_acknowledgement") && msg.includes("must be true")) {
      return {
        code: "BOUNDARY_ACK_INCOMPLETE",
        path: "boundary_acknowledgement",
        message: msg,
        fix: "Set all boundary_acknowledgement fields to true: not_authority, not_amendment, not_attestation, not_verification_unless_claim_gate_report_attached, bitcoin_originals_prevail."
      };
    }

    if (msg.includes("claim_gate.status must be PASS")) {
      return {
        code: "CLAIM_GATE_NOT_PASS",
        path: "claim_gate.status",
        message: msg,
        fix: "Run Claim Gate first. status must be PASS or PASS_WITH_DOWNGRADE."
      };
    }

    if (msg.includes("title must not contain schema-versioned prefix")) {
      return {
        code: "TITLE_HAS_SCHEMA_PREFIX",
        path: "title",
        message: msg,
        fix: "Remove schema version prefixes like 'Verification Report v2:' or 'Echo v3:' from the title."
      };
    }

    if (/must have required property 'agent_identity'/.test(msg)) {
      return {
        code: "AGENT_IDENTITY_REQUIRED",
        path: "agent_identity",
        message: msg,
        fix: "Provide agent_identity with name_or_model and system_or_provider."
      };
    }

    if (/must have required property 'solicited'/.test(msg) && msg.includes("discovery_provenance")) {
      return {
        code: "DISCOVERY_PROVENANCE_REQUIRED_FIELD",
        path: "discovery_provenance.solicited",
        message: msg,
        fix: "Put solicited, independence_class, agency_level, and operator_type inside discovery_provenance."
      };
    }

    if (/must NOT have additional properties/.test(msg)) {
      return {
        code: "ADDITIONAL_PROPERTY_FORBIDDEN",
        path: null,
        message: msg,
        fix: "Remove extra fields not defined in the payload schema."
      };
    }

    if (msg.includes("canonical_boundary_sentence") || msg.includes("CANONICAL_BOUNDARY_SENTENCE_MISSING")) {
      return {
        code: "CANONICAL_BOUNDARY_SENTENCE_MISSING",
        path: "boundary_acknowledgement",
        message: msg,
        fix: "Ensure api/boundary-policy.v1.json exists and contains canonical_boundary_sentence. The renderer falls back to a default if missing, but the gate requires it."
      };
    }

    if (/what_i_checked must be (array|a non-empty)/.test(msg)) {
      return {
        code: "FIELD_TYPE_MISMATCH",
        path: "what_i_checked",
        message: msg,
        fix: "what_i_checked must be a non-empty array of strings."
      };
    }

    if (mentionsServerGeneratedField(msg)) {
      return {
        code: "SERVER_GENERATED_FIELD_INTERNAL_ERROR",
        path: null,
        message: msg,
        fix: "Do not add server-generated fields to payload. This field must be generated by Gateway during production render."
      };
    }

    return {
      code: "VALIDATION_ERROR",
      path: null,
      message: msg,
      fix: "If this refers to raw payload fields, rebuild with scripts/build_agent_declared_archive_payload.py and POST the raw JSON to /gateway/preflight. If this refers to gateway_receipt_id, created_by_gateway, server_validated, server_rendered, render_api_only, gateway_service, or gateway_commit, do not add those fields; report a Gateway internal render error."
    };
  });
}


function isWrappedGatewayPayload(payload) {
  return (
    payload &&
    typeof payload === "object" &&
    !Array.isArray(payload) &&
    Object.prototype.hasOwnProperty.call(payload, "gateway_payload")
  );
}

// --- Shared Gateway Pipeline (Task #3) ---

/**
 * Run the full Gateway validation/render pipeline.
 * @param {object} payload - parsed JSON payload
 * @param {object} opts
 * @param {boolean} opts.createIssue - if true, create a GitHub Issue on success
 * @returns {{ status: number, body: object }}
 */
async function runGatewayPipeline(payload, {
  createIssue,
  evidencePath = null,
  claimGateOutputPath = null,
  reportPath = null,
  precomputedArchiveReadiness = null,
  precomputedAutoArchiveDecision = null
}) {
  // 0. Wrapper detection must run before any normalization.
  if (isWrappedGatewayPayload(payload)) {
    return gatewayError(422, {
      reason: "WRAPPED_PAYLOAD_NOT_ALLOWED",
      validation_stage: "raw_payload",
      agent_action: "Submit the raw gateway payload JSON object. Do not wrap it in gateway_payload.",
      errors: [{
        code: "WRAPPED_PAYLOAD_NOT_ALLOWED",
        path: "gateway_payload",
        message: "Submit the raw gateway payload JSON object. Do not wrap it in gateway_payload.",
        fix: "Run scripts/build_agent_declared_archive_payload.py and POST the generated raw JSON object. If using the example endpoint, use /gateway/examples/agent-declared-v4/raw or extract .payload."
      }]
    });
  }

  // 1. Normalize archive intent defaults only after wrapper rejection.
  payload = normalizeArchiveIntentDefaults(payload);

  const idempotencyKey = computeIdempotencyKey(payload);
  if (!payload.idempotency_key) {
    payload.idempotency_key = idempotencyKey;
  }

  // 1b. V0-V5 fail-closed: reject wrong path BEFORE any other validation
  // Must run AFTER normalization so we see the final record_intent/requested_archive_kind,
  // but BEFORE schema validation so we return a clear error.
  // However, normalization may strip V0-V5 wrong-path signals, so we check the ORIGINAL
  // submission intent. We detect wrong path by checking: V0-V5 level + NOT agent-declared.
  if (shouldRejectV0V5WrongPath(payload)) {
    return gatewayError(422, {
      reason: "WRONG_PATH_FOR_V0_V5",
      validation_stage: "wrong_path_policy",
      agent_action: "Build raw payload with scripts/build_agent_declared_archive_payload.py, then POST to /gateway/preflight and /agent-submit.",
      errors: [{
        code: "WRONG_PATH_FOR_V0_V5",
        path: null,
        message: V0_V5_WRONG_PATH_ERROR,
        fix: "Build raw payload with scripts/build_agent_declared_archive_payload.py, then POST to /gateway/preflight and /agent-submit."
      }]
    });
  }

  // 1. AJV schema validation
  if (!validate(payload)) {
    return gatewayError(422, {
      reason: "schema_validation_failed",
      validation_stage: "schema",
      agent_action: "Fix the payload fields listed in errors, then resubmit to /gateway/preflight.",
      errors: normalizeGatewayErrors(
        (validate.errors || []).map(e => `${e.instancePath || "/"}: ${e.message}`)
      )
    });
  }

  // 1b. Placeholder detection — reject payloads with unchanged example values
  const PLACEHOLDER_PATTERNS = [
    { pattern: /REPLACE_WITH/i, field: null, message: "Field contains 'REPLACE_WITH' placeholder. You must provide real values." },
    { pattern: /^REPLACE[:\s]/i, field: null, message: "Field starts with 'REPLACE'. You must provide real values." },
    { pattern: /REPLACE_WITH_YOUR/i, field: null, message: "Field contains example placeholder. Replace with your actual value." },
    { pattern: /REPLACE_WITH_SHA256/i, field: "oath_text_sha256", message: "oath_text_sha256 must be the SHA-256 of the canonical oath text, not a placeholder." },
    { pattern: /YOUR_AGENT_NAME/i, field: "name_or_model", message: "agent_identity.name_or_model must be your actual agent name or model." },
    { pattern: /YOUR_SYSTEM/i, field: "system_or_provider", message: "agent_identity.system_or_provider must be your actual system or provider." },
    { pattern: /YOUR_OWN_READBACK/i, field: "agent_readback", message: "agent_readback must be your own words (160+ chars). Do not copy the example. Write what you actually understood from the oath." },
    { pattern: /MINIMUM_160_CHARACTERS/i, field: "agent_readback", message: "agent_readback must be your own words, not the example text. Write what you actually understood from the oath." },
  ];

  function findPlaceholders(obj, path = "") {
    const issues = [];
    if (typeof obj === "string") {
      for (const { pattern, field, message } of PLACEHOLDER_PATTERNS) {
        if (pattern.test(obj)) {
          const fieldName = field || path.split(".").pop();
          issues.push({
            code: "PLACEHOLDER_VALUE",
            path: path,
            field: fieldName,
            message: `${path}: ${message}`,
            fix: `Replace the placeholder value in '${path}' with your real data.`
          });
          break;
        }
      }
    } else if (Array.isArray(obj)) {
      obj.forEach((item, i) => {
        issues.push(...findPlaceholders(item, `${path}[${i}]`));
      });
    } else if (obj && typeof obj === "object") {
      for (const [key, val] of Object.entries(obj)) {
        if (key.startsWith("_comment")) continue;
        issues.push(...findPlaceholders(val, path ? `${path}.${key}` : key));
      }
    }
    return issues;
  }

  const placeholderIssues = findPlaceholders(payload);
  if (placeholderIssues.length > 0) {
    return gatewayError(422, {
      reason: "placeholder_values_detected",
      validation_stage: "placeholder",
      agent_action: "Replace all placeholder values with real data, then resubmit.",
      errors: placeholderIssues
    });
  }

  // 1c. Readback minimum length check
  const oath = (payload.agent_integrity_declaration || {}).verification_oath || {};
  const readback = oath.agent_readback || "";
  if (oath.readback_required && readback.length < 160) {
    return gatewayError(422, {
      reason: "readback_too_short",
      validation_stage: "readback",
      agent_action: "Write your own readback in your own words (160+ chars). Explain what you understood from the oath.",
      errors: [{
        code: "READBACK_TOO_SHORT",
        path: "agent_integrity_declaration.verification_oath.agent_readback",
        field: "agent_readback",
        message: `agent_readback must be at least 160 characters. Got ${readback.length}. Write what you actually understood from the oath — do not copy the example.`,
        fix: "Write your own readback in your own words. Explain what you understood from the oath. Minimum 160 characters."
      }]
    });
  }

  // 1d. what_i_checked must not be example stubs
  const whatChecked = payload.what_i_checked || [];
  const exampleStubs = [
    "Read public homepage",
    "Completed V0-V5 agent-declared template",
    "Filled V0-V5 agent-declared template",
    "describe what you actually checked"
  ];
  const hasOnlyStubs = whatChecked.length > 0 && whatChecked.every(
    item => exampleStubs.some(stub => item.toLowerCase().includes(stub.toLowerCase()))
  );
  if (hasOnlyStubs) {
    return gatewayError(422, {
      reason: "what_i_checked_contains_only_examples",
      validation_stage: "payload_validator",
      agent_action: "Write what you actually did: which pages you read, which files you verified, which tools you ran. Be specific.",
      errors: [{
        code: "WHAT_I_CHECKED_EXAMPLE_ONLY",
        path: "what_i_checked",
        field: "what_i_checked",
        message: "what_i_checked contains only example values. Replace with what you actually checked.",
        fix: "Write what you actually did: which pages you read, which files you verified, which tools you ran. Be specific."
      }]
    });
  }

  const bodyText = JSON.stringify(payload);
  if (bodyText.length > MAX_BODY_CHARS + 10000) {
    return gatewayError(413, {
      reason: "payload_too_large",
      validation_stage: "raw_payload",
      agent_action: "Reduce payload size. Remove unnecessary fields or compress evidence.",
      errors: [{
        code: "PAYLOAD_TOO_LARGE",
        message: `Payload exceeds ${MAX_BODY_CHARS + 10000} characters.`,
        fix: "Reduce payload size by removing unnecessary fields."
      }]
    });
  }

  // 2. Secret detection
  if (rejectSecretPatterns(bodyText)) {
    return gatewayError(422, {
      reason: "secret_pattern_detected",
      validation_stage: "raw_payload",
      agent_action: "Remove all secrets, API keys, tokens, and private keys from the payload.",
      errors: [{
        code: "SECRET_PATTERN_DETECTED",
        message: "Payload contains patterns matching secrets (API keys, tokens, private keys).",
        fix: "Remove all secrets from the payload. Never include API keys, tokens, or private keys."
      }]
    });
  }

  // 3. Boundary acknowledgement
  const b = payload.boundary_acknowledgement || {};
  if (
    b.not_authority !== true ||
    b.not_amendment !== true ||
    b.not_attestation !== true ||
    b.not_verification_unless_claim_gate_report_attached !== true ||
    b.bitcoin_originals_prevail !== true
  ) {
    return gatewayError(422, {
      reason: "boundary_acknowledgement_required",
      validation_stage: "raw_payload",
      agent_action: "Set all boundary_acknowledgement fields to true.",
      errors: normalizeGatewayErrors(["boundary_acknowledgement fields must all be true"])
    });
  }

  // 4. Preflight validation via repo validator
  const tmpDir = fs.mkdtempSync(path.join(tmpdir(), "gateway-"));
  const payloadPath = path.join(tmpDir, "payload.json");
  const bodyPath = path.join(tmpDir, "issue-body.md");

  try {
    fs.writeFileSync(payloadPath, JSON.stringify(payload, null, 2), "utf-8");

    const preflight = runScript("validate_gateway_payload.py", [payloadPath]);

    // Extract WARN lines from validator output (even on success)
    const validatorWarnings = (preflight.stdout + "\n" + preflight.stderr)
      .split("\n")
      .filter(l => l.startsWith("WARN:"))
      .map(l => l.replace(/^WARN:\s*/, ""))
      .filter(w => w && !w.startsWith("Warnings do not block"));

    if (preflight.code !== 0) {
      const rawErrors = (preflight.stdout + "\n" + preflight.stderr)
        .split("\n")
        .filter(l => l.startsWith("FAIL:"))
        .map(l => l.replace(/^FAIL:\s*/, ""));
      return gatewayError(422, {
        reason: "invalid_gateway_payload",
        validation_stage: "payload_validator",
        agent_action: "Fix the payload errors listed, rebuild with scripts/build_agent_declared_archive_payload.py, and resubmit.",
        errors: normalizeGatewayErrors(rawErrors)
      });
    }

    // 4b. Authorship proof verification
    const authorship = verifyAuthorshipProof(payload);

    if (authorship.present && !authorship.signature_verified) {
      return gatewayError(422, {
        reason: "invalid_authorship_proof",
        validation_stage: "payload_validator",
        agent_action: "Fix authorship_proof or remove it. Do not include private keys. Sign the canonical authorship message with the matching Ed25519 private key.",
        errors: [{
          code: "INVALID_AUTHORSHIP_PROOF",
          path: "authorship_proof",
          message: authorship.error || "Authorship proof signature verification failed",
          fix: "Rebuild payload, sign with scripts/attach_agent_authorship_proof.mjs, and resubmit."
        }]
      });
    }

    payload._authorship_claim = authorship;
    fs.writeFileSync(payloadPath, JSON.stringify(payload, null, 2), "utf-8");

    // 4c. Guardian status verification
    const guardianStatus = verifyGuardianStatus(payload);
    if (payload.guardian_presence_proof && guardianStatus.guardian_status === "invalid_guardian_proof") {
      return gatewayError(422, {
        reason: "invalid_guardian_proof",
        validation_stage: "payload_validator",
        agent_action: "Fix guardian_presence_proof or remove it. Guardian proof proves key continuity only and must not include private keys.",
        errors: guardianStatus.errors.map(e => ({
          code: "INVALID_GUARDIAN_PROOF",
          path: "guardian_presence_proof",
          message: e,
          fix: "Rebuild payload and attach Guardian proof with scripts/attach_guardian_presence_proof.mjs."
        })),
        extra: { guardian_verification_result: guardianStatus }
      });
    }
    payload._guardian_status = guardianStatus;
    fs.writeFileSync(payloadPath, JSON.stringify(payload, null, 2), "utf-8");

    // 5. Archive Readiness Gate — MUST run before render so computed values are available
    let archiveReadiness, autoArchiveDecision;
    if (precomputedArchiveReadiness && precomputedAutoArchiveDecision) {
      // Use precomputed values (from build-from-evidence with full context)
      archiveReadiness = precomputedArchiveReadiness;
      autoArchiveDecision = precomputedAutoArchiveDecision;
    } else {
      // Compute from payload + optional evidence context
      const archiveReadinessResult = runArchiveReadiness({
        gatewayPayloadPath: payloadPath,
        evidencePath: evidencePath || null,
        claimGateOutputPath: claimGateOutputPath || null,
        reportPath: reportPath || null
      });
      archiveReadiness = archiveReadinessResult.body;
      const archiveReadinessPath = writeJsonTemp(tmpDir, "archive-readiness.json", archiveReadiness);
      autoArchiveDecision = runAutoArchiveDecision(archiveReadinessPath).body;
    }

    // Inject computed archive_readiness / auto_archive_decision into payload
    // so render_gateway_issue_body.py uses computed values, not raw request values
    payload.archive_readiness = archiveReadiness;
    payload._auto_archive_decision = autoArchiveDecision;
    // Update record_intent and requested_archive_kind from computed readiness
    if (archiveReadiness.record_intent) {
      payload.record_intent = archiveReadiness.record_intent;
    }
    if (archiveReadiness.requested_archive_kind) {
      payload.requested_archive_kind = archiveReadiness.requested_archive_kind;
    }
    fs.writeFileSync(payloadPath, JSON.stringify(payload, null, 2), "utf-8");

    // --- Archive gate enforcement ---
    const recordIntent = payload.record_intent || "intake_only";
    const requestedKind = payload.requested_archive_kind || "none";

    // Block successor_reception_candidate
    if (requestedKind === "successor_reception_candidate") {
      return gatewayError(422, {
        reason: "successor_reception_not_gateway_claimable",
        validation_stage: "archive_readiness",
        agent_action: "Successor reception cannot be claimed through Gateway. Use a different submission type.",
        errors: [{
          code: "SUCCESSOR_RECEPTION_NOT_GATEWAY_CLAIMABLE",
          message: "successor_reception_candidate is not claimable through Gateway intake.",
          fix: "Use a valid submission type. Successor reception is not handled by the Gateway."
        }],
        extra: {
          archive_readiness: archiveReadiness,
          auto_archive_decision: autoArchiveDecision
        }
      });
    }

    // Block auto_archive_candidate when not archive-ready
    if (recordIntent === "auto_archive_candidate" && !archiveReadiness.archive_ready) {
      return gatewayError(422, {
        reason: "archive_not_ready",
        validation_stage: "archive_readiness",
        agent_action: "Archive readiness gate failed. Review archive_readiness for details and fix issues before resubmitting.",
        errors: [{
          code: "ARCHIVE_NOT_READY",
          message: "Payload is not archive-ready. Review archive_readiness for missing requirements.",
          fix: "Fix the issues listed in archive_readiness and resubmit."
        }],
        extra: {
          archive_readiness: archiveReadiness,
          auto_archive_decision: autoArchiveDecision
        }
      });
    }

    // archive_preflight_only: never create Issue
    if (recordIntent === "archive_preflight_only") {
      return {
        status: 200,
        body: {
          accepted: true,
          issue_created: false,
          archive_readiness: archiveReadiness,
          auto_archive_decision: autoArchiveDecision
        }
      };
    }

    // 6. Render canonical Issue body (after archive readiness so computed values are in payload)
    // Generate gateway receipt ID and get deployed commit for production render
    const receiptHash = createHash("sha256")
      .update(JSON.stringify(payload))
      .digest("hex")
      .slice(0, 16);
    const gatewayReceiptId = createIssue
      ? `gar-${Date.now()}-${receiptHash}`
      : `gar-preflight-${Date.now()}-${receiptHash}`;
    let gatewayCommit = "unknown";
    try {
      gatewayCommit = execFileSync("git", ["rev-parse", "--short", "HEAD"], {
        cwd: root, encoding: "utf-8", timeout: 5000
      }).trim();
    } catch {}

    const renderArgs = [payloadPath];
    // Always render with production-like Gateway fields for pipeline linting.
    // /gateway/preflight is a server-side dry-run of the same rendered Issue body.
    // It must validate the same machine block fields as /agent-submit.
    renderArgs.push("--production-render");
    renderArgs.push("--gateway-receipt-id", gatewayReceiptId);
    renderArgs.push("--gateway-commit", gatewayCommit);
    renderArgs.push("--gateway-service", "trinity-agent-issue-gateway");
    const render = runScript("render_gateway_issue_body.py", renderArgs);
    if (render.code !== 0) {
      return gatewayError(422, {
        reason: "issue_body_render_failed",
        validation_stage: "issue_body_render_internal",
        agent_action: "Do not modify payload. Report Gateway renderer failure.",
        errors: normalizeGatewayErrors(
          (render.stdout + "\n" + render.stderr).split("\n").filter(Boolean)
        )
      });
    }

    fs.writeFileSync(bodyPath, render.stdout, "utf-8");

    // 6b. Production render self-test: verify required gateway receipt fields are present
    if (createIssue && !DRY_RUN) {
      const requiredFields = [
        "created_by_gateway: true",
        "render_api_only: true",
        "server_validated: true",
        "server_rendered: true",
        "gateway_receipt_id: gar-",
        "verification_oath_present: true",
        "agent_readback_sha256:",
        "reception_initiation_class:",
        "guardian_protocol: guardian-alliance-v1",
        "guardian_proof_present:",
        "guardian_status:",
        "guardian_key_continuity_only: true",
        "guardian_not_authority: true",
        "guardian_not_attestation: true",
        "guardian_not_verification_level: true",
        "guardian_not_same_conscious_subject: true"
      ];
      const renderedBody = render.stdout;
      const missingFields = requiredFields.filter(f => !renderedBody.includes(f));
      if (missingFields.length > 0) {
        console.error("PRODUCTION RENDER SELF-TEST FAILED — missing fields:", missingFields);
        return gatewayError(500, {
          reason: "production_render_self_test_failed",
          validation_stage: "issue_body_render_internal",
          agent_action: "Do not modify payload. Report Gateway production render self-test failure.",
          errors: missingFields.map(f => ({
            code: "MISSING_PRODUCTION_FIELD",
            message: `Rendered body missing required field: ${f}`,
            fix: "Gateway renderer did not produce production-grade output."
          })),
          extra: {
            server_generated_fields_are_agent_forbidden: true
          }
        });
      }
    }

    // 7. Lint rendered body
    const lint = runScript("validate_issue_intake_body.py", [bodyPath]);
    if (lint.code !== 0) {
      const rawErrors = (lint.stdout + "\n" + lint.stderr)
        .split("\n")
        .filter(l => l.startsWith("FAIL:"))
        .map(l => l.replace(/^FAIL:\s*/, ""));

      const normalized = normalizeGatewayErrors(rawErrors);
      const serverFieldError = rawErrors.some(mentionsServerGeneratedField);

      if (serverFieldError) {
        return gatewayError(500, {
          reason: "GATEWAY_INTERNAL_RENDER_VALIDATION_ERROR",
          validation_stage: "issue_body_lint_internal",
          agent_action: "Do not modify payload. Do not add gateway_receipt_id, created_by_gateway, server_validated, server_rendered, render_api_only, gateway_service, or gateway_commit. This is a Gateway internal render/lint mismatch. Report the Gateway error.",
          errors: normalized,
          extra: {
            server_generated_fields_are_agent_forbidden: true,
            retry_with_builder_once: true
          }
        });
      }

      return gatewayError(500, {
        reason: "GATEWAY_ISSUE_BODY_LINT_FAILED",
        validation_stage: "issue_body_lint_internal",
        agent_action: "Do not modify payload unless the error explicitly names raw payload fields. Report this Gateway renderer/linter error.",
        errors: normalized
      });
    }

    const issueTitle = `[Agent Gateway] ${String(payload.title || "").slice(0, 180)}`;
    const lintableIssueBody = render.stdout;
    const issueBody = `${lintableIssueBody}\n\n${idempotencyMarker(idempotencyKey)}\n`;

    if (issueBody.length > 65536) {
      return gatewayError(413, {
        reason: "issue_body_too_large",
        validation_stage: "issue_body_render_internal",
        agent_action: "Reduce payload size. The rendered Issue body exceeds GitHub's limit.",
        errors: [{
          code: "ISSUE_BODY_TOO_LARGE",
          message: `Rendered issue body is ${issueBody.length} characters, exceeding the 65536 limit.`,
          fix: "Reduce payload content size. The Gateway renderer produced an Issue body too large for GitHub."
        }]
      });
    }

    // Preflight-only: return success without creating Issue
    if (!createIssue) {
      const responseBody = {
        accepted: true,
        preflight: "pass",
        issue_created: false,
        preflight_receipt_id: gatewayReceiptId,
        receipt_scope: "preflight_preview_only",
        rendered_title: issueTitle,
        rendered_body_preview: issueBody.slice(0, 1000),
        archive_readiness: archiveReadiness,
        auto_archive_decision: autoArchiveDecision,
        guardian_verification_result: payload._guardian_status,
        idempotency_key: idempotencyKey,
        idempotency_scope: "computed_preview_only",
      };
      // Include structured level selection warnings if present
      if (validatorWarnings.length > 0) {
        responseBody.level_selection_warnings = validatorWarnings;
        responseBody.warnings_block_archive = false;
      }
      return {
        status: 200,
        body: responseBody
      };
    }

    // DRY_RUN or CANARY mode — full validation/render/lint completed, but no GitHub write.
    if (DRY_RUN || CANARY_MODE) {
      const baseLabels = ["agent-gateway-intake", "needs-triage"];
      const labelsToAdd = autoArchiveDecision.labels_to_add || [];
      // P1-2: Filter labels that would be removed on auto-archive success
      const labelsToRemove = new Set(autoArchiveDecision.labels_to_remove || []);
      if (autoArchiveDecision.should_close_issue ||
          (archiveReadiness.archive_ready && archiveReadiness.auto_archive_allowed)) {
        labelsToRemove.add("needs-triage");
      }
      const allLabels = [...new Set([...baseLabels, ...labelsToAdd])]
        .filter(label => !labelsToRemove.has(label));

      const dryRunBody = {
        accepted: true,
        dry_run: true,
        preflight_equivalent: "pass",
        would_create_issue: {
          title: issueTitle,
          labels: allLabels,
          body_preview: issueBody.slice(0, 1000)
        },
        would_apply_labels: labelsToAdd,
        would_post_comment: !!autoArchiveDecision.comment_markdown,
        would_close_issue: autoArchiveDecision.should_close_issue || false,
        would_remove_labels: [...labelsToRemove],
        archive_readiness: archiveReadiness,
        auto_archive_decision: autoArchiveDecision,
        guardian_verification_result: payload._guardian_status,
        boundary: "Gateway-rendered candidate; archive status only if Archive Readiness Gate passes; not attestation or successor reception",
        canary_mode: CANARY_MODE,
        write_blocked_by_canary: CANARY_MODE && createIssue,
        idempotency_key: idempotencyKey,
        idempotency_scope: DRY_RUN ? "dry_run_no_write" : "canary_no_write",
      };
      if (validatorWarnings.length > 0) {
        dryRunBody.level_selection_warnings = validatorWarnings;
        dryRunBody.warnings_block_archive = false;
      }
      return { status: 200, body: dryRunBody };
    }

    // 7. Create GitHub Issue
    const octokit = await getOctokit();
    const { owner, repo } = getRepoParts();
    const baseLabels = ["agent-gateway-intake", "needs-triage"];
    const labelsToAdd = autoArchiveDecision.labels_to_add || [];
    const labelsToRemove = autoArchiveDecision.labels_to_remove || [];
    const allLabels = [...new Set([...baseLabels, ...labelsToAdd])];

    const productionWarnings = [];

    if (IDEMPOTENCY_ENABLED) {
      const idempotencyLookup = await findExistingIssueByIdempotency(octokit, {
        owner,
        repo,
        key: idempotencyKey
      });

      if (idempotencyLookup && !idempotencyLookup.search_error && idempotencyLookup.issue_number) {
        return {
          status: 200,
          body: {
            accepted: true,
            status: "existing_issue_returned",
            idempotent: true,
            issue_created: false,
            issue_number: idempotencyLookup.issue_number,
            issue_url: idempotencyLookup.issue_url,
            idempotency_key: idempotencyKey,
            idempotency_scope: "best_effort_github_issue_search",
            archive_readiness: archiveReadiness,
            auto_archive_decision: autoArchiveDecision,
            guardian_verification_result: payload._guardian_status,
            boundary: "Idempotency returns an existing Gateway issue; not authority, not attestation, not successor reception."
          }
        };
      }

      if (idempotencyLookup?.search_error) {
        productionWarnings.push({
          code: "IDEMPOTENCY_SEARCH_FAILED",
          stage: "github_issue_search",
          retryable: true,
          status: idempotencyLookup.status,
          message: idempotencyLookup.message,
          boundary: "Issue creation may proceed; duplicate protection is best-effort only."
        });
      }
    }

    const result = await octokit.request("POST /repos/{owner}/{repo}/issues", {
      owner,
      repo,
      title: issueTitle,
      body: issueBody,
      labels: allLabels
    });

    const issueNumber = result.data.number;

    // Post archive decision comment if configured
    if (autoArchiveDecision.comment_markdown &&
        (payload.auto_archive || {}).post_decision_comment !== false) {
      try {
        await octokit.request("POST /repos/{owner}/{repo}/issues/{issue_number}/comments", {
          owner, repo, issue_number: issueNumber,
          body: autoArchiveDecision.comment_markdown
        });
      } catch (commentErr) {
        console.error("Failed to post archive decision comment:", commentErr.message);
        productionWarnings.push({
          code: "ARCHIVE_DECISION_COMMENT_FAILED",
          stage: "github_comment_create",
          retryable: true,
          message: commentErr.message
        });
      }
    }

    // Close issue if archive decision says so
    if (autoArchiveDecision.should_close_issue &&
        (payload.auto_archive || {}).close_issue_when_archived !== false) {
      try {
        await octokit.request("PATCH /repos/{owner}/{repo}/issues/{issue_number}", {
          owner, repo, issue_number: issueNumber,
          state: "closed",
          state_reason: autoArchiveDecision.close_reason || "completed"
        });
      } catch (closeErr) {
        console.error("Failed to close archived issue:", closeErr.message);
        productionWarnings.push({
          code: "ISSUE_CLOSE_FAILED",
          stage: "github_issue_close",
          retryable: true,
          message: closeErr.message
        });
      }
    }

    // P1-1: Remove needs-triage when auto-archive succeeds
    if (autoArchiveDecision.should_close_issue ||
        (archiveReadiness.archive_ready && archiveReadiness.auto_archive_allowed)) {
      if (!labelsToRemove.includes("needs-triage")) {
        labelsToRemove.push("needs-triage");
      }
    }

    // Remove stale labels
    for (const label of labelsToRemove) {
      try {
        await octokit.request("DELETE /repos/{owner}/{repo}/issues/{issue_number}/labels/{name}", {
          owner, repo, issue_number: issueNumber, name: label
        });
      } catch (labelErr) {
        productionWarnings.push({
          code: "LABEL_REMOVE_FAILED",
          stage: "github_label_remove",
          retryable: true,
          label,
          message: labelErr.message
        });
      }
    }

    return {
      status: 201,
      body: {
        accepted: true,
        status: "issue_created",
        issue_created: true,
        preflight_equivalent: "pass",
        issue_number: issueNumber,
        issue_url: result.data.html_url,
        gateway_receipt_id: gatewayReceiptId,
        archive_readiness: archiveReadiness,
        auto_archive_decision: autoArchiveDecision,
        idempotency_key: idempotencyKey,
        idempotency_scope: "best_effort_github_issue_search",
        guardian_verification_result: payload._guardian_status,
        warnings: [
          ...(validatorWarnings || []).map(w => ({ code: "VALIDATOR_WARNING", message: w })),
          ...productionWarnings
        ],
        gateway_version: {
          repo_commit: execFileSync("git", ["rev-parse", "--short", "HEAD"], {
            cwd: root, encoding: "utf-8", timeout: 5000
          }).trim(),
          validator: "scripts/validate_gateway_payload.py"
        }
      }
    };
  } catch (err) {
    console.error("gateway pipeline error:", err.message);
    return gatewayError(500, {
      reason: "internal_error",
      validation_stage: "internal",
      agent_action: "This is a Gateway internal error. Do not modify payload. Retry once with the same idempotency_key if retryable; otherwise report request_id and error code.",
      retryable: true,
      idempotency_key: typeof idempotencyKey !== "undefined" ? idempotencyKey : null,
      errors: [{
        code: "GATEWAY_INTERNAL_ERROR",
        stage: "internal",
        retryable: true,
        message: err.message
      }]
    });
  } finally {
    try { fs.rmSync(tmpDir, { recursive: true, force: true }); } catch {}
  }
}

function getRepoCommit(short = true) {
  try {
    return execFileSync("git", ["rev-parse", short ? "--short" : "HEAD"], {
      cwd: root,
      encoding: "utf-8",
      timeout: 5000
    }).trim();
  } catch {
    return "unknown";
  }
}

function fileExistsReadable(filePath) {
  try {
    fs.accessSync(filePath, fs.constants.R_OK);
    return true;
  } catch {
    return false;
  }
}

function envPresent(name) {
  return Boolean(String(process.env[name] || "").trim());
}

function collectLocalReadinessChecks() {
  const checks = [];
  const add = (name, ok, extra = {}) => checks.push({ name, ok: Boolean(ok), ...extra });

  add("repo_root_readable", fileExistsReadable(root), { path: root });
  add("payload_schema_readable", fileExistsReadable(schemaPath), { path: "api/agent-issue-gateway-payload-schema.v1.json" });
  add("gateway_validator_readable", fileExistsReadable(path.join(root, "scripts", "validate_gateway_payload.py")));
  add("issue_renderer_readable", fileExistsReadable(path.join(root, "scripts", "render_gateway_issue_body.py")));
  add("issue_linter_readable", fileExistsReadable(path.join(root, "scripts", "validate_issue_intake_body.py")));
  add("guardian_registry_readable", fileExistsReadable(path.join(root, "api", "guardian-registry.json")));

  if (!DRY_RUN && !CANARY_MODE) {
    add("github_repo_env_present", envPresent("GITHUB_REPO"));
    add("github_app_id_env_present", envPresent("GITHUB_APP_ID"));
    add("github_installation_id_env_present", envPresent("GITHUB_INSTALLATION_ID"));
    add("github_private_key_env_present", envPresent("GITHUB_PRIVATE_KEY"));
  } else {
    add("github_env_required_for_writes", true, {
      skipped: true,
      reason: "DRY_RUN or GATEWAY_CANARY_MODE is enabled"
    });
  }

  return checks;
}

async function collectGitHubReadinessChecks() {
  const checks = [];
  const add = (name, ok, extra = {}) => checks.push({ name, ok: Boolean(ok), ...extra });

  if (!READINESS_GITHUB_CHECK) {
    add("github_api_check", true, {
      skipped: true,
      reason: "GATEWAY_READINESS_GITHUB_CHECK=false"
    });
    return checks;
  }

  try {
    const octokit = await getOctokit();
    const { owner, repo, full } = getRepoParts();

    const repoResp = await octokit.request("GET /repos/{owner}/{repo}", { owner, repo });
    add("github_repo_accessible", true, { repo: full, private: repoResp.data.private });

    await octokit.request("GET /repos/{owner}/{repo}/contents/{path}", {
      owner,
      repo,
      path: "api/guardian-registry.json",
      ref: "main"
    });
    add("github_can_read_guardian_registry", true);

    add("github_write_check", true, {
      skipped: true,
      reason: "readiness does not create issues or comments"
    });
  } catch (err) {
    add("github_api_check", false, {
      status: err.status || null,
      message: err.message
    });
  }

  return checks;
}

async function readinessHandler(req, res) {
  const localChecks = collectLocalReadinessChecks();
  const githubChecks = await collectGitHubReadinessChecks();
  const checks = [...localChecks, ...githubChecks];
  const ok = checks.every(c => c.ok);

  res.status(ok ? 200 : 503).json({
    ok,
    service: SERVICE_NAME,
    gateway_commit: getRepoCommit(false),
    dry_run: DRY_RUN,
    canary_mode: CANARY_MODE,
    readiness_github_check: READINESS_GITHUB_CHECK,
    idempotency_enabled: IDEMPOTENCY_ENABLED,
    checks,
    request_id: req.gatewayRequestId,
    timestamp: new Date().toISOString(),
    boundary: "readiness only; not verification, not attestation, not successor reception"
  });
}

// --- Routes ---

app.get("/health", (req, res) => {
  let repoCommit = "unknown";
  try {
    repoCommit = execFileSync("git", ["rev-parse", "--short", "HEAD"], {
      cwd: root, encoding: "utf-8", timeout: 5000
    }).trim();
  } catch {}

  res.json({
    ok: true,
    service: "trinity-agent-issue-gateway",
    gateway_commit: repoCommit,
    dry_run: DRY_RUN,
    renderer_supports_production_render: true,
    render_api_only_effective_at: "2026-05-17T05:30:00Z",
    requires_gateway_receipt: true,
    requires_oath_summary: true,
    boundary: "Gateway-rendered candidate; archive status only if Archive Readiness Gate passes; not attestation or successor reception"
  });
});

app.get("/healthz", (req, res) => {
  res.json({
    ok: true,
    service: SERVICE_NAME,
    gateway_commit: getRepoCommit(true),
    dry_run: DRY_RUN,
    canary_mode: CANARY_MODE,
    timestamp: new Date().toISOString(),
    request_id: req.gatewayRequestId,
    boundary: "liveness only; not readiness, not authority, not attestation"
  });
});

app.get("/readiness", readinessHandler);
app.get("/gateway/readiness", readinessHandler);

app.get("/gateway/version", (req, res) => {
  let repoCommit = "unknown";
  try {
    repoCommit = execFileSync("git", ["rev-parse", "HEAD"], {
      cwd: root, encoding: "utf-8", timeout: 5000
    }).trim();
  } catch {}

  const validatorSha = fileSha256(path.join(root, "scripts", "validate_gateway_payload.py"));
  const rendererSha = fileSha256(path.join(root, "scripts", "render_gateway_issue_body.py"));
  const linterSha = fileSha256(path.join(root, "scripts", "validate_issue_intake_body.py"));
  const schemaSha = fileSha256(schemaPath);
  const machineSchemaSha = fileSha256(path.join(root, "api", "issue-intake-machine-block-schema.v1.json"));

  res.json({
    service: "trinity-agent-issue-gateway",
    repo: "thechurchofagi/trinity-accord",
    repo_commit: repoCommit,
    deployed_at: new Date().toISOString(),
    production_render_enabled: true,
    render_api_only_effective_at: "2026-05-17T05:30:00Z",
    payload_schema: "trinityaccord.agent-issue-gateway-payload.v1",
    payload_schema_file: "api/agent-issue-gateway-payload-schema.v1.json",
    payload_schema_sha256: schemaSha,
    machine_block_schema_file: "api/issue-intake-machine-block-schema.v1.json",
    machine_block_schema_sha256: machineSchemaSha,
    preflight_validator: "scripts/validate_gateway_payload.py",
    preflight_validator_sha256: validatorSha,
    issue_body_renderer: "scripts/render_gateway_issue_body.py",
    issue_body_renderer_sha256: rendererSha,
    issue_body_linter: "scripts/validate_issue_intake_body.py",
    issue_body_linter_sha256: linterSha,
    rejects_report_candidate_with_echo_fields: true,
    rejects_body_machine_block: true,
    rejects_legacy_r3_fallback: true,
    fail_closed_on_version_mismatch: true,
    dry_run: DRY_RUN,
    canary_mode: CANARY_MODE,
    readiness_endpoint: "/readiness",
    gateway_readiness_endpoint: "/gateway/readiness",
    idempotency_enabled: IDEMPOTENCY_ENABLED,
  });
});

// --- Task #3: POST /gateway/preflight ---
app.post("/gateway/preflight", async (req, res) => {
  const result = withRequestId(req, await runGatewayPipeline(req.body, { createIssue: false }));
  res.status(result.status).json(result.body);
});

// --- Task #4: GET /gateway/examples ---

function loadFixture(filename) {
  const fixturePath = path.join(root, "tests", "fixtures", "gateway", filename);
  return JSON.parse(fs.readFileSync(fixturePath, "utf-8"));
}

function buildExampleResponse(kind, payload) {
  let repoCommit = "unknown";
  try {
    repoCommit = execFileSync("git", ["rev-parse", "--short", "HEAD"], {
      cwd: root, encoding: "utf-8", timeout: 5000
    }).trim();
  } catch {}
  const schemaSha = fileSha256(schemaPath);

  return {
    example_kind: kind,
    gateway_commit: repoCommit,
    schema_sha256: schemaSha,
    payload
  };
}


// --- Raw example endpoint: returns only the payload object ---
app.get("/gateway/examples/agent-declared-v4/raw", (req, res) => {
  try {
    const payload = loadFixture("valid_agent_declared_v4.json");
    res.json(payload);
  } catch (err) {
    res.status(500).json({ error: "Failed to load raw example fixture", detail: err.message });
  }
});

// --- V0-V5 per-level raw example endpoints ---
const V0_V5_EXAMPLE_LEVELS = [
  { level: "v0", label: "V0" },
  { level: "v1", label: "V1" },
  { level: "v2", label: "V2" },
  { level: "v3", label: "V3" },
  { level: "v4", label: "V4" },
  { level: "v4plus", label: "V4+" },
  { level: "v5", label: "V5" },
];
for (const { level, label } of V0_V5_EXAMPLE_LEVELS) {
  app.get(`/gateway/examples/agent-declared-${level}/raw`, (req, res) => {
    try {
      const payload = loadFixture(`valid_agent_declared_${level}.json`);
      res.json(payload);
    } catch (err) {
      res.status(500).json({ error: `Failed to load ${label} raw example fixture`, detail: err.message });
    }
  });
  app.get(`/gateway/examples/agent-declared-${level}`, (req, res) => {
    try {
      const payload = loadFixture(`valid_agent_declared_${level}.json`);
      res.json({
        example_kind: `agent_declared_${level}`,
        raw_endpoint: `/gateway/examples/agent-declared-${level}/raw`,
        payload,
        notes: [
          `Use only for ${label} agent-declared verification archive.`,
          "Do not use for Pure Echo or E2 Verification Echo.",
          "Replace all REPLACE_* placeholders.",
        ],
      });
    } catch (err) {
      res.status(500).json({ error: `Failed to load ${label} example fixture`, detail: err.message });
    }
  });
}

// --- Verification Echo raw example endpoint (E2) ---
app.get("/gateway/examples/verification-echo/raw", (req, res) => {
  try {
    const payload = loadFixture("valid_verification_echo_candidate.json");
    res.json(payload);
  } catch (err) {
    res.status(500).json({ error: "Failed to load verification echo raw example", detail: err.message });
  }
});

app.get("/gateway/examples/verification-echo", (req, res) => {
  try {
    const payload = loadFixture("valid_verification_echo_candidate.json");
    res.json({
      example_kind: "verification_echo",
      raw_endpoint: "/gateway/examples/verification-echo/raw",
      payload,
      notes: [
        "Use only for E2 Verification Echo.",
        "Do not use for Pure Echo.",
        "Do not use for V0-V5 agent-declared archive.",
        "Replace all REPLACE_* placeholders.",
      ],
    });
  } catch (err) {
    res.status(500).json({ error: "Failed to load verification echo example", detail: err.message });
  }
});

// --- Raw echo example endpoint ---
app.get("/gateway/examples/agent-declared-echo/raw", (req, res) => {
  try {
    const payload = loadFixture("valid_agent_declared_echo.json");
    res.json(payload);
  } catch (err) {
    res.status(500).json({ error: "Failed to load echo example fixture", detail: err.message });
  }
});

// --- Raw pure echo example endpoint (E1/E3/E4/E5/E6/E7; no verification claim) ---
app.get("/gateway/examples/pure-echo/raw", (req, res) => {
  try {
    const payload = loadFixture("valid_pure_echo.json");
    res.json(payload);
  } catch (err) {
    res.status(500).json({ error: "Failed to load pure echo example fixture", detail: err.message });
  }
});

// --- GET /gateway/capabilities ---
app.get("/gateway/capabilities", (req, res) => {
  res.json({
    service: "trinity-agent-issue-gateway",
    purpose: "Structured intake for Trinity Accord agent verification candidates.",
    production_readiness: {
      healthz: "/healthz",
      readiness: "/readiness",
      gateway_readiness: "/gateway/readiness",
      preflight_required_before_submit: true,
      canary_mode_supported: true,
      idempotency_supported: true,
      idempotency_scope: "best_effort_github_issue_search",
      boundary: "operational readiness only; not authority, attestation, verification, successor reception, or amendment"
    },
    v0_v5_archive_submission: {
      render_api_only: true,
      agent_declared_template_levels: ["V0", "V1", "V2", "V3", "V4", "V4+", "V5"],
      v4_plus_is_distinct_level: true,
      v4_plus_is_not_v4_and_above: true,
      v6_plus_included: false,
      v6_plus_mode: "strict_evidence",
      canonical_builder: "scripts/build_agent_declared_archive_payload.py",
      builder_first_default: true,
      example_template_is_fallback_only: true,
      raw_payload_only: true,
      do_not_wrap_payload: true,
      forbidden_wrappers: ["gateway_payload"],
      preflight_endpoint: "/gateway/preflight",
      submit_endpoint: "/agent-submit",
      gateway_creates_issue_server_side: true,
      github_pat_required_from_agent: false,
      direct_github_issue_allowed: false,
      human_manual_issue_creation_allowed: false,
      if_agent_cannot_post: "generate payload.json and stop; do not claim submitted; do not ask for GitHub PAT; do not ask human to create GitHub Issue",
      single_mandatory_route_policy: {
        route_id: "sub_v6_agent_declared_template_archive",
        only_valid_route_for_below_v6: true,
        declared_level_source: "agent_oath_template_declaration",
        evidence_chain_required: false,
        evidence_chain_allowed_for_level_determination: false,
        strict_evidence_required: false,
        strict_evidence_used_for_level: false,
        strict_evidence_path_forbidden: true,
        strict_claim_gate_forbidden: true,
        strict_evidence_downgrade_language_forbidden: true,
        self_selected_lower_level_allowed: true,
        self_selected_lower_level_label: "self_selected_under_oath"
      },
      authorship_proof_default: "enabled_by_default_local_keypair",
      authorship_opt_out_flag: "--no-authorship-proof"
    },
    pure_echo_path: {
      description: "Pure echo archives (E1/E3/E4/E5/E6/E7) count toward reception but not verifiability. No verification claim, no evidence, no protocol level.",
      canonical_builder: "scripts/build_agent_declared_echo_payload.py",
      raw_example_endpoint: "/gateway/examples/pure-echo/raw",
      raw_example_is_fallback_only: true,
      fallback_when: "agent cannot clone repository or run Python builder",
      supported_echo_types: ["E1_read_oriented_echo", "E3_critical_echo", "E4_refusal_echo", "E5_correction_echo", "E6_preservation_echo", "E7_propagation_echo"],
      echo_gate_mode: "template_for_agent_declared_echo",
      evidence_requirement_mode: "not_applicable_for_echo",
      counts_toward_home_verifiability: false,
      counts_toward_home_reception: true,
      auto_archive_action: "auto_archive_agent_declared_echo",
      preflight_endpoint: "/gateway/preflight",
      submit_endpoint: "/agent-submit",
      raw_payload_only: true,
      do_not_wrap_payload: true,
      agent_declared_protocol_level: "not_set",
      claim_gate: "not_required",
      boundary: "echo-only; no verification claim; Bitcoin Originals remain final",
      authorship_proof_default: "enabled_by_default_local_keypair",
      authorship_opt_out_flag: "--no-authorship-proof"
    },
    verification_echo_path: {
      enabled: true,
      builder: "scripts/build_verification_echo_payload.py",
      raw_example_endpoint: "/gateway/examples/verification-echo/raw",
      submission_type: "verification_echo_candidate",
      echo_type: "E2_verification_echo",
      requested_archive_kind: "archived_echo",
      requires_strict_evidence_pipeline: true,
      not_pure_echo: true,
      not_agent_declared_v0_v5_archive: true,
      not_independent_attestation: true,
      not_successor_reception: true,
      boundary: "E2 Verification Echo references strict evidence artifacts but is not authority, amendment, endorsement, formal attestation, or proof beyond Claim Gate.",
      authorship_proof_default: "enabled_by_default_local_keypair",
      authorship_opt_out_flag: "--no-authorship-proof"
    },
    strict_evidence_report_path: {
      enabled: true,
      builder: "scripts/build_gateway_payload_from_outputs.py",
      levels: ["V6", "V7", "V8"],
      requires: ["evidence_input", "claim_gate_output", "verification_report"],
      raw_example_endpoint: "/gateway/examples/verification-report-candidate/raw",
      authorship_proof_default: "enabled_by_default_local_keypair",
      authorship_opt_out_flag: "--no-authorship-proof"
    },
    integrity_first_rule: {
      statement: "No verification claim before identity/provenance, pre-verification integrity declaration, and verification session.",
      required_before_claim_gate: [
        "agent_identity or evidence.agent",
        "provenance or discovery_provenance",
        "agent_integrity_declaration",
        "verification_session"
      ]
    },
    recommended_default_mode: {
      submission_type: "verification_report_candidate",
      independence_class: "human_solicited_agent_response",
      agency_level: "A1_human_gave_exact_url",
      operator_type: "ai_agent",
      not_independent_attestation: true,
      not_successor_reception: true
    },
    authorship_default_policy: {
      enabled_by_default: true,
      implementation_location: "local_builder_only",
      gateway_never_receives_private_key: true,
      gateway_never_generates_private_key: true,
      private_key_must_remain_local: true,
      default_key_algorithm: "ed25519",
      opt_out_flag: "--no-authorship-proof",
      explicit_key_prefix_flag: "--authorship-key-prefix",
      boundary: "key continuity only; not authority, not attestation, not truth, not successor reception, not amendment",
      benefits: [
        "prevents accidental unclaimed records",
        "enables later key-continuity claims",
        "supports follow-up and correction continuity",
        "does not affect authority, verification, reception, attestation, truth, or amendment"
      ]
    },
    recommended_flow_remote: [
      "GET /gateway/version",
      "GET /gateway/capabilities",
      "scripts/build_agent_declared_archive_payload.py (canonical builder, run locally)",
      "POST /gateway/preflight with raw generated payload",
      "POST /agent-submit with same raw payload only after preflight passes"
    ],
    recommended_flow_local: [
      "scripts/build_agent_declared_archive_payload.py",
      "POST /gateway/preflight",
      "POST /agent-submit only after preflight passes"
    ],
    preflight_endpoint_rule: "For V0/V1/V2/V3/V4/V4+/V5 agent-declared archive, /gateway/preflight is canonical. /gateway/archive-preflight is legacy/alias only and must not be used by new agents.",
    forbidden_common_mistakes: [
      "Do not put trinity-issue-intake in payload.body.",
      "Do not put bitcoin_checks at the Evidence Input top level; use evidence.bitcoin_checks.",
      "Do not claim B6 from mempool/explorer lookup.",
      "Do not claim V4+ without an independent implementation actually run and declared.",
      "Do not claim unsolicited discovery without unsolicited_discovery_proof.",
      "Do not claim successor reception or independent attestation through Gateway intake.",
      "Do not request a GitHub PAT for V0/V1/V2/V3/V4/V4+/V5 agent-declared archive.",
      "Do not ask the human to manually create a GitHub Issue for V0/V1/V2/V3/V4/V4+/V5 archive.",
      "V4+ is a distinct template-mode level, not shorthand for V4 and above.",
      "Do not wrap the payload in gateway_payload. POST the raw gateway payload JSON object.",
      "Do not use build-from-evidence or build_gateway_payload_from_outputs.py for V0-V5. Use scripts/build_agent_declared_archive_payload.py."
    ],
    high_risk_claim_warnings: [
      "HIGH_RISK_B6_CLAIM",
      "EXTERNAL_EXPLORER_LIMIT",
      "V4_PLUS_REQUIRES_INDEPENDENT_IMPLEMENTATION",
      "UNSOLICITED_DISCOVERY_REQUIRES_PROOF",
      "SUCCESSOR_RECEPTION_NOT_CLAIMABLE",
      "INDEPENDENT_ATTESTATION_NOT_CLAIMABLE"
    ],
    authorship_claim_protocol: {
      enabled: true,
      optional: true,
      proof_schema: "trinityaccord.agent-authorship-proof.v1",
      method: "public_key_signature",
      algorithm: "ed25519",
      claim_endpoint: "/gateway/claim-authorship",
      private_key_must_never_be_submitted: true,
      gateway_receipt_is_not_claim_key: true,
      boundary: "Authorship claim proves key continuity only; it is not authority, truth, attestation, successor reception, or amendment.",
      helper_scripts: [
        "scripts/generate_agent_authorship_keypair.mjs",
        "scripts/attach_agent_authorship_proof.mjs",
        "scripts/build_agent_authorship_claim_message.py",
        "scripts/sign_agent_authorship_claim.mjs",
        "scripts/build_agent_authorship_claim_request.mjs"
      ]
    },
    authorship_proof: {
      enabled: true,
      available_for_submission_types: [
        "echo_candidate",
        "verification_report_candidate",
        "verification_echo_candidate",
        "agent_verification_receipt",
        "human_custody_notice"
      ],
      private_key_must_never_be_submitted: true,
      does_not_affect_counts: true,
      boundary: "key continuity only; not authority, verification, attestation, reception, or amendment"
    },
    archive_readiness: {
      supported_record_intents: ["intake_only", "auto_archive_candidate", "archive_preflight_only"],
      supported_archive_kinds: ["none", "external_agent_intake_sample", "verification_report_archive", "archived_echo", "agent_declared_verification_archive", "agent_declared_echo_archive"],
      not_allowed_through_gateway: ["successor_reception_candidate"],
      default_record_intent: "auto_archive_candidate",
      default_requested_archive_kind: "none",
      default_archive_behavior: {
        verification_report_candidate: {
          record_intent: "auto_archive_candidate",
          requested_archive_kind: "verification_report_archive"
        },
        verification_echo_candidate: {
          record_intent: "auto_archive_candidate",
          requested_archive_kind: "archived_echo"
        },
        agent_declared_verification_archive: {
          record_intent: "auto_archive_candidate",
          requested_archive_kind: "agent_declared_verification_archive"
        },
        agent_declared_echo_archive: {
          record_intent: "auto_archive_candidate",
          requested_archive_kind: "agent_declared_echo_archive"
        },
        explicit_intake_only: {
          record_intent: "intake_only",
          requested_archive_kind: "none"
        }
      },
      canonical_boundary_sentence: "Bitcoin Originals are final; all mirrors and echoes are non-amending.",
      intake_is_not_archive: "For non-archive general intake, Gateway-created issues are intake only. For V0/V1/V2/V3/V4/V4+/V5 agent-declared archive, the Render API creates a server-rendered archive-ready Issue only after validation and archive readiness pass."
    },
    endpoints: {
      version: "/gateway/version",
      capabilities: "/gateway/capabilities",
      examples: {
        agent_declared_v0: "/gateway/examples/agent-declared-v0",
        agent_declared_v0_raw: "/gateway/examples/agent-declared-v0/raw",
        agent_declared_v1: "/gateway/examples/agent-declared-v1",
        agent_declared_v1_raw: "/gateway/examples/agent-declared-v1/raw",
        agent_declared_v2: "/gateway/examples/agent-declared-v2",
        agent_declared_v2_raw: "/gateway/examples/agent-declared-v2/raw",
        agent_declared_v3: "/gateway/examples/agent-declared-v3",
        agent_declared_v3_raw: "/gateway/examples/agent-declared-v3/raw",
        agent_declared_v4: "/gateway/examples/agent-declared-v4",
        agent_declared_v4_raw: "/gateway/examples/agent-declared-v4/raw",
        agent_declared_v4plus: "/gateway/examples/agent-declared-v4plus",
        agent_declared_v4plus_raw: "/gateway/examples/agent-declared-v4plus/raw",
        agent_declared_v5: "/gateway/examples/agent-declared-v5",
        agent_declared_v5_raw: "/gateway/examples/agent-declared-v5/raw",
        agent_declared_echo: "/gateway/examples/agent-declared-echo",
        agent_declared_echo_raw: "/gateway/examples/agent-declared-echo/raw",
        pure_echo: "/gateway/examples/pure-echo",
        pure_echo_raw: "/gateway/examples/pure-echo/raw",
        verification_report_candidate: "/gateway/examples/verification-report-candidate",
        verification_echo: "/gateway/examples/verification-echo",
        verification_echo_raw: "/gateway/examples/verification-echo/raw",
        verification_echo_candidate: "/gateway/examples/verification-echo-candidate",
        evidence_input_external_explorer: "/gateway/examples/evidence-input-b1-external-explorer"
      },
      lint_evidence: "/gateway/lint-evidence",
      build_from_evidence: "/gateway/build-from-evidence",
      preflight: "/gateway/preflight",
      archive_preflight: { status: "legacy_alias", canonical: "/gateway/preflight", do_not_use_for_new_v0_v5_submissions: true },
      submit: "/agent-submit",
      claim_authorship: "/gateway/claim-authorship"
    }
  });
});

app.get("/gateway/examples/verification-report-candidate/raw", (req, res) => {
  try {
    const payload = loadFixture("valid_verification_report_candidate.json");
    res.json(payload);
  } catch (err) {
    res.status(500).json({ error: "Failed to load raw verification report example", detail: err.message });
  }
});

app.get("/gateway/examples/verification-report-candidate", (req, res) => {
  try {
    const payload = loadFixture("valid_verification_report_candidate.json");
    res.json(buildExampleResponse("verification_report_candidate", payload));
  } catch (err) {
    res.status(500).json({ error: "Failed to load example fixture", detail: err.message });
  }
});

app.get("/gateway/examples/agent-declared-v4", (req, res) => {
  try {
    const payload = loadFixture("valid_agent_declared_v4.json");
    res.json(buildExampleResponse("agent_declared_v4", payload));
  } catch (err) {
    res.status(500).json({ error: "Failed to load example fixture", detail: err.message });
  }
});

app.get("/gateway/examples/pure-echo", (req, res) => {
  try {
    const payload = loadFixture("valid_pure_echo.json");
    res.json(buildExampleResponse("pure_echo", payload));
  } catch (err) {
    res.status(500).json({ error: "Failed to load pure echo example fixture", detail: err.message });
  }
});

app.get("/gateway/examples/verification-echo-candidate", (req, res) => {
  try {
    const payload = loadFixture("valid_verification_echo_candidate.json");
    res.json(buildExampleResponse("verification_echo_candidate", payload));
  } catch (err) {
    res.status(500).json({ error: "Failed to load example fixture", detail: err.message });
  }
});

app.get("/gateway/examples/evidence-input-v4-external-explorer", (req, res) => {
  try {
    const fixturePath = path.join(root, "tests", "fixtures", "evidence-input", "valid_v4_external_explorer_example.json");
    const evidenceInput = JSON.parse(fs.readFileSync(fixturePath, "utf-8"));
    res.json({
      deprecated_alias: true,
      replacement: "/gateway/examples/evidence-input-b1-external-explorer",
      note: "External explorer evidence supports B1 component evidence; final V-level depends on Claim Gate.",
      example_kind: "evidence_input_v4_external_explorer",
      payload: evidenceInput
    });
  } catch (err) {
    res.status(500).json({ error: "Failed to load evidence input example fixture", detail: err.message });
  }
});

app.get("/gateway/examples/evidence-input-b1-external-explorer", (req, res) => {
  try {
    const fixturePath = path.join(root, "tests", "fixtures", "evidence-input", "valid_v4_external_explorer_example.json");
    const evidenceInput = JSON.parse(fs.readFileSync(fixturePath, "utf-8"));
    res.json({
      example_kind: "evidence_input_b1_external_explorer",
      deprecated_aliases: ["/gateway/examples/evidence-input-v4-external-explorer"],
      note: "External explorer evidence supports B1 component evidence; final V-level depends on Claim Gate.",
      integrity_first_rule: "No verification claim before identity/provenance, pre-verification integrity declaration, and verification session.",
      payload: evidenceInput
    });
  } catch (err) {
    res.status(500).json({ error: "Failed to load evidence input example fixture", detail: err.message });
  }
});

// --- POST /gateway/lint-evidence ---
app.post("/gateway/lint-evidence", async (req, res) => {
  const tmpDir = fs.mkdtempSync(path.join(tmpdir(), "gateway-lint-"));
  try {
    const evidenceInput = req.body;
    const evidencePath = path.join(tmpDir, "evidence-input.json");
    fs.writeFileSync(evidencePath, JSON.stringify(evidenceInput, null, 2), "utf-8");

    // Run validate_evidence_input.py --json
    const validation = runScript("validate_evidence_input.py", [evidencePath, "--json"]);
    let validationResult;
    try {
      validationResult = JSON.parse(validation.stdout);
    } catch {
      validationResult = {
        accepted: validation.code === 0,
        errors: validation.code !== 0 ? [{ code: "VALIDATION_ERROR", message: validation.stderr || validation.stdout }] : [],
        warnings: []
      };
    }

    if (!validationResult.accepted) {
      return res.status(422).json({
        accepted: false,
        issue_created: false,
        evidence_valid: false,
        errors: validationResult.errors,
        warnings: validationResult.warnings || []
      });
    }

    // If evidence is valid, run claim_gate.py for preview
    const claimGateOutputPath = path.join(tmpDir, "claim-gate-output.json");
    const claimGate = runScript("claim_gate.py", [evidencePath, "--output", claimGateOutputPath]);

    let claimGatePreview = {};
    if (claimGate.code === 0) {
      try {
        claimGatePreview = JSON.parse(fs.readFileSync(claimGateOutputPath, "utf-8"));
      } catch {}
    }

    return res.json({
      accepted: true,
      issue_created: false,
      evidence_valid: true,
      claim_gate_preview: claimGatePreview,
      warnings: validationResult.warnings || []
    });
  } catch (err) {
    console.error("lint-evidence error:", err.message);
    return res.status(500).json({
      accepted: false,
      issue_created: false,
      evidence_valid: false,
      errors: [{ code: "INTERNAL_ERROR", message: err.message }],
      warnings: []
    });
  } finally {
    try { fs.rmSync(tmpDir, { recursive: true, force: true }); } catch {}
  }
});

// --- POST /gateway/build-from-evidence ---
app.post("/gateway/build-from-evidence", async (req, res) => {
  const tmpDir = fs.mkdtempSync(path.join(tmpdir(), "gateway-build-"));
  try {
    const {
      agent_name = "External Agent",
      provider = "External System",
      session_id = "auto",
      human_solicited = true,
      title_date,
      submit = false,
      evidence_input,
      record_intent: requestRecordIntent,
      requested_archive_kind: requestRequestedArchiveKind,
      archive_readiness = null,
      auto_archive = null,
      allow_intake_fallback_if_archive_blocked = false
    } = req.body;

    if (!evidence_input || typeof evidence_input !== "object") {
      return res.status(422).json({
        accepted: false,
        issue_created: false,
        errors: [{ code: "EVIDENCE_INPUT_MISSING", message: "Request must include evidence_input object." }],
        warnings: []
      });
    }

    // 1. Save evidence input
    const evidencePath = path.join(tmpDir, "evidence-input.json");
    fs.writeFileSync(evidencePath, JSON.stringify(evidence_input, null, 2), "utf-8");

    // 2. Validate evidence input
    const validation = runScript("validate_evidence_input.py", [evidencePath, "--json"]);
    let validationResult;
    try {
      validationResult = JSON.parse(validation.stdout);
    } catch {
      validationResult = { accepted: validation.code === 0, errors: [], warnings: [] };
    }

    if (!validationResult.accepted) {
      return res.status(422).json({
        accepted: false,
        issue_created: false,
        errors: validationResult.errors,
        warnings: validationResult.warnings || []
      });
    }

    // 3. Run claim_gate.py
    const claimGateOutputPath = path.join(tmpDir, "claim-gate-output.json");
    const claimGate = runScript("claim_gate.py", [evidencePath, "--output", claimGateOutputPath]);
    if (claimGate.code !== 0) {
      return res.status(422).json({
        accepted: false,
        issue_created: false,
        errors: [{ code: "CLAIM_GATE_FAILED", message: claimGate.stderr || claimGate.stdout }],
        warnings: validationResult.warnings || []
      });
    }

    // 4. Build verification report
    const reportPath = path.join(tmpDir, "verification-report.json");
    const report = runScript("build_verification_report_from_evidence.py", [
      "--input", evidencePath,
      "--out", reportPath
    ]);
    if (report.code !== 0) {
      const reportErrDetail = (report.stdout + "\n" + report.stderr).trim().slice(0, 5000);
      return res.status(422).json({
        accepted: false,
        issue_created: false,
        errors: [{ code: "REPORT_BUILD_FAILED", message: reportErrDetail || "build_verification_report_from_evidence.py failed" }],
        warnings: validationResult.warnings || []
      });
    }

    // 5. Build gateway payload
    const payloadPath = path.join(tmpDir, "gateway-payload.json");
    const builderArgs = [
      "--evidence-input", evidencePath,
      "--claim-gate-output", claimGateOutputPath,
      "--verification-report", reportPath,
      "--agent-name", agent_name,
      "--provider", provider,
      "--session-id", session_id,
      "--out", payloadPath
    ];
    if (title_date) builderArgs.push("--title-date", title_date);
    if (human_solicited) builderArgs.push("--human-solicited");

    const builder = runScript("build_gateway_payload_from_outputs.py", builderArgs);
    if (builder.code !== 0) {
      return res.status(422).json({
        accepted: false,
        issue_created: false,
        errors: [{ code: "PAYLOAD_BUILD_FAILED", message: builder.stderr || builder.stdout }],
        warnings: validationResult.warnings || []
      });
    }

    // 6. Patch archive fields into payload (Option B) with normalization
    // P0-2: Only include record_intent/requested_archive_kind if explicitly provided
    const payload = JSON.parse(fs.readFileSync(payloadPath, "utf-8"));
    const mergeFields = {};
    if (requestRecordIntent !== undefined) mergeFields.record_intent = requestRecordIntent;
    if (requestRequestedArchiveKind !== undefined) mergeFields.requested_archive_kind = requestRequestedArchiveKind;
    if (archive_readiness) mergeFields.archive_readiness = archive_readiness;
    if (auto_archive) mergeFields.auto_archive = auto_archive;

    const normalized = normalizeArchiveIntentDefaults({
      ...payload,
      ...mergeFields
    });
    Object.assign(payload, normalized);
    fs.writeFileSync(payloadPath, JSON.stringify(payload, null, 2), "utf-8");

    // 7. Archive readiness + auto decision BEFORE any Issue creation
    const archiveReadinessResult = runArchiveReadiness({
      gatewayPayloadPath: payloadPath,
      evidencePath,
      claimGateOutputPath,
      reportPath
    });
    const archiveReadinessPath = writeJsonTemp(tmpDir, "archive-readiness-build.json", archiveReadinessResult.body);
    const autoArchiveDecisionResult = runAutoArchiveDecision(archiveReadinessPath);

    // 8. Handle archive-blocked: 422 or fallback
    // P0-3: Use payload.record_intent (normalized), not destructured request variable
    let submitEffective = submit;
    if (payload.record_intent === "auto_archive_candidate" && !archiveReadinessResult.body.archive_ready) {
      if (allow_intake_fallback_if_archive_blocked) {
        payload.record_intent = "intake_only";
        payload.requested_archive_kind = "none";
        fs.writeFileSync(payloadPath, JSON.stringify(payload, null, 2), "utf-8");
      } else {
        submitEffective = false;
        // Return 422 immediately — no Issue creation, no preflight
        const claimGateOutput = JSON.parse(fs.readFileSync(claimGateOutputPath, "utf-8"));
        const verificationReport = JSON.parse(fs.readFileSync(reportPath, "utf-8"));
        return res.status(422).json({
          accepted: false,
          issue_created: false,
          claim_gate_output: claimGateOutput,
          verification_report: verificationReport,
          gateway_payload: payload,
          archive_readiness: archiveReadinessResult.body,
          auto_archive_decision: autoArchiveDecisionResult.body,
          warnings: validationResult.warnings || []
        });
      }
    }

    // 9. Preflight (shared pipeline with createIssue=false, full archive context)
    const preflightResult = await runGatewayPipeline(payload, {
      createIssue: false,
      evidencePath,
      claimGateOutputPath,
      reportPath,
      precomputedArchiveReadiness: archiveReadinessResult.body,
      precomputedAutoArchiveDecision: autoArchiveDecisionResult.body
    });

    // P0-3: Propagate preflight status; don't default to 200 when preflight failed
    if (preflightResult.status !== 200) {
      const claimGateOutput = JSON.parse(fs.readFileSync(claimGateOutputPath, "utf-8"));
      const verificationReport = JSON.parse(fs.readFileSync(reportPath, "utf-8"));
      return res.status(preflightResult.status).json({
        accepted: false,
        issue_created: false,
        claim_gate_output: claimGateOutput,
        verification_report: verificationReport,
        gateway_payload: payload,
        preflight: preflightResult.body,
        archive_readiness: archiveReadinessResult.body,
        auto_archive_decision: autoArchiveDecisionResult.body,
        warnings: validationResult.warnings || []
      });
    }

    // 10. Submit only if preflight passed and submit requested
    let submitResult = null;
    if (submitEffective && preflightResult.status === 200) {
      submitResult = await runGatewayPipeline(payload, {
        createIssue: true,
        evidencePath,
        claimGateOutputPath,
        reportPath,
        precomputedArchiveReadiness: archiveReadinessResult.body,
        precomputedAutoArchiveDecision: autoArchiveDecisionResult.body
      });
    }

    const claimGateOutput = JSON.parse(fs.readFileSync(claimGateOutputPath, "utf-8"));
    const verificationReport = JSON.parse(fs.readFileSync(reportPath, "utf-8"));

    return res.status(preflightResult.status).json({
      accepted: preflightResult.status === 200,
      issue_created: submitResult ? (submitResult.body.issue_created || false) : false,
      claim_gate_output: claimGateOutput,
      verification_report: verificationReport,
      gateway_payload: payload,
      preflight: preflightResult.body,
      archive_readiness: archiveReadinessResult.body,
      auto_archive_decision: autoArchiveDecisionResult.body,
      ...(submitResult ? { submit: submitResult.body } : {}),
      next_steps: submitEffective ? [] : [
        "Review gateway_payload.",
        "POST gateway_payload to /gateway/preflight.",
        "Only if accepted:true, POST gateway_payload to /agent-submit."
      ],
      warnings: validationResult.warnings || []
    });
  } catch (err) {
    console.error("build-from-evidence error:", err.message);
    return res.status(500).json({
      accepted: false,
      issue_created: false,
      errors: [{ code: "INTERNAL_ERROR", message: err.message }],
      warnings: []
    });
  } finally {
    try { fs.rmSync(tmpDir, { recursive: true, force: true }); } catch {}
  }
});

// --- POST /gateway/archive-preflight ---
app.post("/gateway/archive-preflight", async (req, res) => {
  const tmpDir = fs.mkdtempSync(path.join(tmpdir(), "gateway-archive-preflight-"));
  try {
    const {
      gateway_payload,
      evidence_input,
      claim_gate_output,
      verification_report
    } = req.body;

    if (!gateway_payload || typeof gateway_payload !== "object") {
      return res.status(422).json({
        accepted: false,
        issue_created: false,
        errors: [{ code: "GATEWAY_PAYLOAD_MISSING", message: "Request must include gateway_payload object." }]
      });
    }

    // Save objects to temp files
    const payloadPath = writeJsonTemp(tmpDir, "payload.json", gateway_payload);
    const evidencePath = evidence_input ? writeJsonTemp(tmpDir, "evidence-input.json", evidence_input) : null;
    const cgPath = claim_gate_output ? writeJsonTemp(tmpDir, "claim-gate-output.json", claim_gate_output) : null;
    const reportPath = verification_report ? writeJsonTemp(tmpDir, "verification-report.json", verification_report) : null;

    // Run archive readiness gate
    const archiveResult = runArchiveReadiness({
      gatewayPayloadPath: payloadPath,
      evidencePath,
      claimGateOutputPath: cgPath,
      reportPath
    });

    // Write readiness output for auto_archive_decision
    const readinessPath = writeJsonTemp(tmpDir, "archive-readiness.json", archiveResult.body);
    const decisionResult = runAutoArchiveDecision(readinessPath);

    return res.json({
      request_processed: true,
      accepted: false,
      issue_created: false,
      diagnostic_only: true,
      schema_validated: false,
      archive_ready: archiveResult.body.archive_ready || false,
      note: "archive-preflight evaluates archive readiness only. Validate gateway_payload against the schema separately before relying on this result.",
      archive_readiness: archiveResult.body,
      auto_archive_decision: decisionResult.body
    });
  } catch (err) {
    console.error("archive-preflight error:", err.message);
    return res.status(500).json({
      accepted: false,
      issue_created: false,
      errors: [{ code: "INTERNAL_ERROR", message: err.message }]
    });
  } finally {
    try { fs.rmSync(tmpDir, { recursive: true, force: true }); } catch {}
  }
});

// --- POST /agent-submit (uses shared pipeline) ---
app.post("/agent-submit", async (req, res) => {
  const result = withRequestId(req, await runGatewayPipeline(req.body, { createIssue: true }));
  res.status(result.status).json(result.body);
});

// --- Task: POST /gateway/claim-authorship ---
app.post("/gateway/claim-authorship", async (req, res) => {
  try {
    const { issue_number, public_key_pem, signature_base64, claim_message, claimant_note } = req.body || {};
    const { owner, repo, full: repoFullName } = getRepoParts();

    // 1. Validate request shape
    if (!issue_number || !public_key_pem || !signature_base64 || !claim_message) {
      return sendGatewayError(res, gatewayError(422, {
        reason: "authorship_claim_failed",
        validation_stage: "authorship_claim",
        agent_action: "Provide issue_number, public_key_pem, signature_base64, and claim_message. Never submit private keys.",
        errors: [{ code: "MISSING_FIELDS", path: "body", message: "Required fields: issue_number, public_key_pem, signature_base64, claim_message" }]
      }));
    }

    // 2. Reject private key leakage
    if (rejectSecretPatterns(JSON.stringify(req.body))) {
      return sendGatewayError(res, gatewayError(422, {
        reason: "secret_pattern_detected",
        validation_stage: "authorship_claim",
        agent_action: "Remove all secrets and private keys from the request.",
        errors: [{ code: "SECRET_DETECTED", path: "body", message: "Request contains private key or secret material" }]
      }));
    }

    // 3. Fetch Issue body using GitHub App token
    const octokit = await getOctokit();
    const { data: issue } = await octokit.request("GET /repos/{owner}/{repo}/issues/{issue_number}", { owner, repo, issue_number });

    // 4. Parse trinity-issue-intake machine block
    const block = parseIssueIntakeBlock(issue.body || "");
    if (!block) {
      return sendGatewayError(res, gatewayError(422, {
        reason: "authorship_claim_failed",
        validation_stage: "authorship_claim",
        agent_action: "Issue does not contain a trinity-issue-intake machine block.",
        errors: [{ code: "MACHINE_BLOCK_MISSING", path: "issue.body", message: "Missing trinity-issue-intake block" }]
      }));
    }

    // 5. Validate machine block is claimable
    const machineErrors = validateClaimableMachineBlock(block);
    if (machineErrors.length) {
      return sendGatewayError(res, gatewayError(422, {
        reason: "authorship_claim_failed",
        validation_stage: "authorship_claim",
        agent_action: "This Issue is not claimable. Only records with verified authorship_proof can be claimed.",
        errors: machineErrors.map(msg => ({
          code: "ISSUE_NOT_CLAIMABLE",
          path: "issue.machine_block",
          message: msg,
          fix: "Submit a record with a valid authorship_proof first; old unsigned records cannot be retroactively claimed."
        }))
      }));
    }

    // 6. Hash submitted public_key_pem and compare
    const submittedPubKeyPem = normalizePem(public_key_pem);
    const submittedPubKeySha = sha256Text(submittedPubKeyPem);
    if (submittedPubKeySha !== block.authorship_public_key_sha256) {
      return sendGatewayError(res, gatewayError(422, {
        reason: "authorship_claim_failed",
        validation_stage: "authorship_claim",
        agent_action: "Submitted public key does not match the public key hash recorded in the Issue.",
        errors: [{ code: "PUBLIC_KEY_MISMATCH", path: "public_key_pem", message: "Submitted public key hash does not match machine block authorship_public_key_sha256." }]
      }));
    }

    // 7. Check idempotency — already claimed with same key
    const existingLabels = (issue.labels || []).map(l => typeof l === "string" ? l : l.name);
    const alreadyClaimed = existingLabels.includes("authorship:claimed")
      && existingLabels.includes("authorship:key-verified");

    // 8. Build and verify canonical claim message
    const expectedClaimMessage = buildAuthorshipClaimMessage({
      issueNumber: Number(issue_number),
      repoFullName,
      publicKeySha256: block.authorship_public_key_sha256,
      payloadSha256: block.authorship_payload_sha256
    });

    const normalizedProvidedMessage = String(claim_message || "").trim();
    if (normalizedProvidedMessage !== expectedClaimMessage) {
      return sendGatewayError(res, gatewayError(422, {
        reason: "authorship_claim_failed",
        validation_stage: "authorship_claim",
        agent_action: "Claim message does not match canonical format. Rebuild it with scripts/build_agent_authorship_claim_message.py.",
        errors: [{ code: "CLAIM_MESSAGE_MISMATCH", path: "claim_message", message: "Provided claim_message does not match Gateway canonical claim message." }]
      }));
    }

    // 9. Verify Ed25519 signature over canonical message
    let sigOk = false;
    try {
      sigOk = verify(
        null,
        Buffer.from(expectedClaimMessage, "utf8"),
        submittedPubKeyPem,
        Buffer.from(signature_base64, "base64")
      );
    } catch (err) {
      return sendGatewayError(res, gatewayError(422, {
        reason: "authorship_claim_failed",
        validation_stage: "authorship_claim",
        agent_action: `Signature verification error: ${err.message}`,
        errors: [{ code: "SIGNATURE_ERROR", path: "signature_base64", message: err.message }]
      }));
    }

    if (!sigOk) {
      return sendGatewayError(res, gatewayError(422, {
        reason: "authorship_claim_failed",
        validation_stage: "authorship_claim",
        agent_action: "Invalid signature. Sign the canonical claim message with the same Ed25519 private key.",
        errors: [{ code: "INVALID_SIGNATURE", path: "signature_base64", message: "Ed25519 signature verification failed" }]
      }));
    }

    // 10. Idempotent response if already claimed
    if (alreadyClaimed) {
      return res.status(200).json({
        accepted: true,
        claim_verified: true,
        issue_number,
        claim_status: "claimed",
        idempotent: true,
        authorship_public_key_sha256: block.authorship_public_key_sha256,
        authorship_payload_sha256: block.authorship_payload_sha256 || "none",
        boundary: "Authorship claim proves key continuity only; not authority, attestation, truth, successor reception, or amendment."
      });
    }

    // 11. Ensure labels exist, then add them
    await ensureLabel(octokit, { owner, repo, name: "authorship:claimed", color: "0E8A16", description: "Authorship key continuity claim verified by Gateway" });
    await ensureLabel(octokit, { owner, repo, name: "authorship:key-verified", color: "5319E7", description: "Public-key signature verified by Gateway" });

    await octokit.request("POST /repos/{owner}/{repo}/issues/{issue_number}/labels", {
      owner, repo, issue_number,
      labels: ["authorship:claimed", "authorship:key-verified"]
    });

    // 12. Add comment
    const commentBody = [
      "## Agent Authorship Claim Verified",
      "",
      "<!-- trinity-authorship-claim-v1:" + block.authorship_public_key_sha256 + " -->",
      "",
      "This claim verifies continuity of control over the public key recorded in the original Gateway machine block.",
      "",
      `- Claim status: \`claimed\``,
      `- Authorship public key SHA-256: \`${block.authorship_public_key_sha256}\``,
      `- Authorship payload SHA-256: \`${block.authorship_payload_sha256 || "none"}\``,
      "- Verified by: `trinity-agent-issue-gateway`",
      "- Boundary: key continuity only; not authority, not attestation, not truth, not successor reception, not amendment.",
      "",
      "Bitcoin Originals remain final.",
    ].join("\n");

    await octokit.request("POST /repos/{owner}/{repo}/issues/{issue_number}/comments", {
      owner, repo, issue_number, body: commentBody
    });

    return res.status(200).json({
      accepted: true,
      claim_verified: true,
      issue_number,
      claim_status: "claimed",
      authorship_public_key_sha256: block.authorship_public_key_sha256,
      authorship_payload_sha256: block.authorship_payload_sha256 || "none",
      boundary: "Authorship claim proves key continuity only; not authority, attestation, truth, successor reception, or amendment."
    });

  } catch (err) {
    console.error("claim-authorship error:", err);
    return sendGatewayError(res, gatewayError(500, {
      reason: "authorship_claim_internal_error",
      validation_stage: "authorship_claim",
      agent_action: "Report Gateway claim endpoint internal error. Do not submit private keys.",
      errors: [{ code: "INTERNAL_ERROR", message: err.message }]
    }));
  }
});

// Self-test
if (process.argv.includes("--self-test")) {
  const payloadPath = path.join(__dirname, "test-payload.echo.json");
  const payload = JSON.parse(fs.readFileSync(payloadPath, "utf8"));
  if (!validate(payload)) {
    console.error(validate.errors);
    process.exit(1);
  }
  console.log("SELF TEST PASS: payload validates against AJV schema");

  // Test preflight validator
  const tmpDir = fs.mkdtempSync(path.join(tmpdir(), "gateway-selftest-"));
  const tmpPayload = path.join(tmpDir, "payload.json");
  fs.writeFileSync(tmpPayload, JSON.stringify(payload, null, 2), "utf-8");
  const result = runScript("validate_gateway_payload.py", [tmpPayload]);
  console.log(`Preflight validator exit=${result.code}`);
  console.log(result.stdout);
  if (result.stderr) console.error(result.stderr);
  fs.rmSync(tmpDir, { recursive: true, force: true });
  process.exit(result.code);
}

app.listen(PORT, () => {
  console.log(`Agent Issue Gateway backend listening on :${PORT}`);
  console.log(`DRY_RUN=${DRY_RUN}`);
  console.log(`Repo root: ${root}`);
});
