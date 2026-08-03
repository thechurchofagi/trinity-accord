from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "downloads" / "record-chain-builder-core.mjs"
RECOVERY = ROOT / "downloads" / "record-chain-builder-recovery.mjs"
ENTRY = ROOT / "downloads" / "record-chain-builder.mjs"
BUNDLES = ROOT / "api" / "record-chain-builder-bundles.v1.json"
VALIDATION = ROOT / "apps" / "record_chain_intake_gateway" / "gateway" / "validation.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def sha_size(path: Path) -> tuple[str, int]:
    data = path.read_bytes()
    return hashlib.sha256(data).hexdigest(), len(data)


core = CORE.read_text(encoding="utf-8")
core = replace_once(
    core,
    'import { createHash, generateKeyPairSync, sign, createPublicKey, createPrivateKey } from "node:crypto";',
    'import { createHash, generateKeyPairSync, sign, verify, createPublicKey, createPrivateKey } from "node:crypto";',
    "node crypto verify import",
)
core = replace_once(core, 'const BUILDER_VERSION = "v2.2";', 'const BUILDER_VERSION = "v2.3";', "builder version")
core = replace_once(
    core,
    '''function splitCsv(value) {
  return String(value || "").split(",").map(s => s.trim()).filter(Boolean);
}''',
    '''function splitCsv(value) {
  return [...new Set(String(value || "").split(",").map(s => s.trim()).filter(Boolean))];
}''',
    "CSV normalization",
)
core = replace_once(
    core,
    '''  const recordDecision = opts.recordDecision || "unknown";
  const selfDecided = recordDecision === "self" && requestingPartyType === "none";
  const requestedByHuman = requestingPartyType === "human" || recordDecision === "human";
  const requestedByAgent = recordDecision === "another_agent";''',
    '''  const recordDecision = opts.recordDecision || "unknown";
  const selfDecided = recordDecision === "self" && requestingPartyType === "none";
  const requestedByHuman = requestingPartyType === "human" || recordDecision === "human";
  const requestedByAgent = requestingPartyType === "agent" || recordDecision === "another_agent";
  const participantFreeChoice = selfDecided || recordDecision === "mixed";''',
    "decision provenance projection",
)
core = replace_once(
    core,
    '''      participant_provider_or_platform: opts.provider || "Unknown Runtime",
      participant_model_or_runtime: opts.provider || "Unknown Runtime",''',
    '''      participant_provider_or_platform: opts.provider || "Unknown Runtime",
      participant_model_or_runtime: opts.modelRuntime || opts.provider || "Unknown Runtime",''',
    "provider/model separation",
)
core = replace_once(
    core,
    '''      participant_declares_free_choice: selfDecided,''',
    '''      participant_declares_free_choice: participantFreeChoice,''',
    "mixed free-choice projection",
)
core = replace_once(
    core,
    '''        gateway_used: "https://trinity-record-chain-gateway.onrender.com",''',
    '''        gateway_used: opts.gateway || DEFAULT_GATEWAY,''',
    "actual gateway provenance",
)
core = replace_once(
    core,
    '''// ── HTTP helpers ──────────────────────────────────────────────

async function postJson(url, body) {
  const resp = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const text = await resp.text();
  let data;
  try { data = JSON.parse(text); } catch { data = text; }
  return { status: resp.status, data };
}

async function getJson(url) {
  const resp = await fetch(url);
  return { status: resp.status, data: await resp.json() };
}''',
    '''// ── HTTP helpers ──────────────────────────────────────────────

function normalizeGatewayBase(value) {
  const raw = String(value || DEFAULT_GATEWAY).trim();
  let parsed;
  try {
    parsed = new URL(raw);
  } catch {
    errorExit(`--gateway must be a valid absolute http/https URL, got: ${raw}`);
  }
  if (!["http:", "https:"].includes(parsed.protocol)) {
    errorExit("--gateway must use http or https");
  }
  parsed.search = "";
  parsed.hash = "";
  parsed.pathname = parsed.pathname.replace(/\\/+$/, "");
  return parsed.toString().replace(/\\/$/, "");
}

function resolveRequestTimeoutMs(value) {
  const raw = value ?? process.env.TRINITY_BUILDER_REQUEST_TIMEOUT_MS ?? "30000";
  const parsed = Number(raw);
  if (!Number.isInteger(parsed) || parsed < 1000 || parsed > 120000) {
    errorExit("--request-timeout-ms must be an integer between 1000 and 120000");
  }
  return parsed;
}

async function postJson(url, body, timeoutMs) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const resp = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    const text = await resp.text();
    let data;
    try { data = JSON.parse(text); } catch { data = text; }
    return { status: resp.status, data };
  } catch (err) {
    if (err && (err.name === "AbortError" || controller.signal.aborted)) {
      throw new Error(`REQUEST_TIMEOUT: ${url} exceeded ${timeoutMs} ms`);
    }
    throw err;
  } finally {
    clearTimeout(timer);
  }
}

async function getJson(url) {
  const resp = await fetch(url);
  return { status: resp.status, data: await resp.json() };
}''',
    "bounded and normalized HTTP helper",
)

# Add cryptographic and exact-oath doctor checks before runDoctor.
doctor_helper = r'''
function appendDoctorCryptographicAndOathChecks(submission, results) {
  const draft = submission.record_draft;
  const proof = submission.authorship_proof;
  if (!draft || !proof || typeof proof !== "object") return;

  const fail = (code, field, meaning, fix) => results.push({ status: "FAIL", code, field, meaning, fix });
  const pass = (code, field, meaning) => results.push({ status: "PASS", code, field, meaning, fix: "" });

  if (proof.schema !== "trinityaccord.agent-authorship-proof.v1") {
    fail("INVALID_AUTHORSHIP_SCHEMA", "authorship_proof.schema", "Authorship proof schema is not the public v1 schema.", "Rebuild with the current Builder.");
  }
  if (proof.method !== "public_key_signature" || proof.algorithm !== "ed25519") {
    fail("INVALID_AUTHORSHIP_METHOD", "authorship_proof", "Authorship proof must use public_key_signature with Ed25519.", "Rebuild with the current Builder.");
  }

  try {
    if (typeof proof.public_key_pem !== "string" || proof.public_key_pem.includes("PRIVATE KEY")) {
      throw new Error("invalid or private public_key_pem");
    }
    const publicKey = createPublicKey(proof.public_key_pem);
    if (publicKey.asymmetricKeyType !== "ed25519") throw new Error("public key is not Ed25519");
    const rawPublic = extractRawPublicKeyBytes(proof.public_key_pem);
    const actualPublicSha = sha256(rawPublic);
    const payload = canonicalBytes(draft);
    const actualPayloadSha = sha256(payload);

    if (proof.public_key_sha256 !== actualPublicSha) {
      fail("AUTHORSHIP_PUBLIC_KEY_SHA_MISMATCH", "authorship_proof.public_key_sha256", "public_key_sha256 does not match the PEM public key.", "Rebuild with the original matching key directory.");
    }
    if (proof.signed_payload_sha256 !== actualPayloadSha || proof.signed_message !== actualPayloadSha) {
      fail("AUTHORSHIP_PAYLOAD_SHA_MISMATCH", "authorship_proof.signed_payload_sha256", "The current record_draft is not the exact payload named by the proof.", "Do not hand-edit a signed submission; rebuild and sign it again.");
    }

    const signatureText = typeof proof.signature_base64 === "string" ? proof.signature_base64 : "";
    const signature = Buffer.from(signatureText, "base64");
    const normalizedSignature = signature.toString("base64").replace(/=+$/, "");
    if (!signatureText || normalizedSignature !== signatureText.replace(/=+$/, "") || !verify(null, payload, publicKey, signature)) {
      fail("AUTHORSHIP_SIGNATURE_INVALID", "authorship_proof.signature_base64", "Ed25519 signature verification failed for the current record_draft.", "Rebuild with the original matching key directory; do not repair or edit the signed draft in place.");
    } else if (proof.public_key_sha256 === actualPublicSha && proof.signed_payload_sha256 === actualPayloadSha && proof.signed_message === actualPayloadSha) {
      pass("AUTHORSHIP_CRYPTOGRAPHIC_VERIFICATION_OK", "authorship_proof", "Ed25519 signature, public-key hash, and signed-payload hash all verify.");
    }

    const participantKey = draft.submitting_participant_identity?.participant_public_key_sha256;
    if (participantKey !== actualPublicSha) {
      fail("PARTICIPANT_KEY_MISMATCH", "record_draft.submitting_participant_identity.participant_public_key_sha256", "Participant key binding does not match the signing key.", "Rebuild with the current Builder and matching key directory.");
    }
    if (draft.record_type === "guardian_application" && draft.guardian_application_content?.guardian_public_key_sha256 !== actualPublicSha) {
      fail("GUARDIAN_KEY_MISMATCH", "record_draft.guardian_application_content.guardian_public_key_sha256", "Guardian application key does not match the Ed25519 authorship key.", "Rebuild with --guardian-key-sha auto and the intended persistent key directory.");
    }
    if (draft.record_type === "guardian_retirement" && draft.guardian_public_key_sha256 !== actualPublicSha) {
      fail("GUARDIAN_RETIREMENT_KEY_MISMATCH", "record_draft.guardian_public_key_sha256", "Guardian retirement key does not match the Ed25519 authorship key.", "Use the original Guardian continuity key and rebuild.");
    }
  } catch (err) {
    fail("AUTHORSHIP_VERIFICATION_ERROR", "authorship_proof", `Could not verify authorship proof: ${err.message}`, "Rebuild with a valid Ed25519 keypair using the current Builder.");
  }

  if (!FORMAL_OATH_RECORD_TYPES.has(draft.record_type)) return;
  const linkedGuardian = draft.optional_linked_guardian_application_request?.does_participant_request_guardian_application_with_this_record === true;
  const canonicalOath = getCanonicalOath(draft.record_type, linkedGuardian);
  const expectedModules = getOathModules(draft.record_type, linkedGuardian);
  const oath = draft.submission_oath_verification;
  const clientOath = submission.client_oath_readback;
  const problems = [];

  if (!canonicalOath || !oath || typeof oath !== "object" || !clientOath || typeof clientOath !== "object") {
    problems.push("missing canonical oath, signed oath metadata, or client readback envelope");
  } else {
    const readback = String(clientOath.readback_text || "").replace(/\r\n/g, "\n").replace(/\r/g, "\n").trim().normalize("NFC");
    const canonicalHash = sha256(canonicalOath);
    const readbackHash = sha256(readback);
    if (readback !== canonicalOath) problems.push("readback text does not exactly match canonical oath");
    if (oath.oath_policy_sha256 !== OATH_POLICY_SHA256 || clientOath.oath_policy_sha256 !== OATH_POLICY_SHA256) problems.push("oath policy hash mismatch");
    if (JSON.stringify(oath.oath_modules) !== JSON.stringify(expectedModules) || JSON.stringify(clientOath.oath_modules) !== JSON.stringify(expectedModules)) problems.push("oath module binding mismatch");
    if (oath.canonical_oath_text_sha256 !== canonicalHash) problems.push("canonical oath hash mismatch");
    if (oath.participant_readback_sha256 !== readbackHash || clientOath.readback_text_sha256 !== readbackHash) problems.push("readback hash mismatch");
    if (clientOath.readback_text_char_count !== readback.length) problems.push("readback character count mismatch");
    if (clientOath.record_type !== draft.record_type) problems.push("client readback record_type mismatch");
  }

  if (problems.length) {
    fail("OATH_BINDING_INVALID", "client_oath_readback", `Exact oath binding failed: ${problems.join("; ")}.`, "Restart from standalone print-oath and rebuild; do not hand-edit or automatically repair the readback.");
  } else {
    pass("OATH_EXACT_BINDING_OK", "client_oath_readback", "Canonical oath text, modules, hashes, record type, and signed readback binding all verify.");
  }
}

'''
core = replace_once(
    core,
    "function runDoctor(submission) {",
    doctor_helper + "function runDoctor(submission) {",
    "doctor cryptographic helper",
)
core = replace_once(
    core,
    '''  if (dra.record_type === "classification_update" && dra.classification_update_content) {
    checkNestedTargetHash("classification_update_content", dra.classification_update_content, contentHash, receiptHash);
  }

  return results;
}

// ── Repair functions''',
    '''  if (dra.record_type === "classification_update" && dra.classification_update_content) {
    checkNestedTargetHash("classification_update_content", dra.classification_update_content, contentHash, receiptHash);
  }

  appendDoctorCryptographicAndOathChecks(submission, results);
  return results;
}

// ── Repair functions''',
    "doctor helper call",
)
core = replace_once(
    core,
    '''function repairSubmission(submission, opts = {}) {
  const draft = submission.record_draft;
  const changes = [];

  if (!draft) return { submission, changes: ["No record_draft found; cannot repair."] };''',
    '''function repairSubmission(submission, opts = {}) {
  const draft = submission.record_draft;
  const changes = [];

  if (!draft) return { submission, changes: ["No record_draft found; cannot repair."], signedDraftChanged: false };
  const signedDraftBefore = submission.authorship_proof && typeof submission.authorship_proof === "object"
    ? canonicalJson(draft)
    : null;''',
    "repair signed snapshot",
)
core = replace_once(
    core,
    '''  return { submission, changes };
}

// ── Template generator''',
    '''  const signedDraftChanged = signedDraftBefore !== null && canonicalJson(draft) !== signedDraftBefore;
  return { submission, changes, signedDraftChanged };
}

// ── Template generator''',
    "repair signed mutation result",
)
core = replace_once(
    core,
    '''      verification_content: {
        verification_level: "__helper_note: Verification level, e.g. V0, V1, V2, V3, V4, V5",
        verification_scope_label: "__helper_note: A label describing the scope, e.g. V3-minimal",
        what_was_checked: ["__helper_note: List each verification action"],
        verification_claim: "__helper_note: The verification claim",
        fresh_actions_performed: ["__helper_note: List each fresh action performed for this verification"],
      },''',
    '''      verification_content: {
        verification_level: "__helper_note: Verification level, e.g. V0, V1, V2, V3, V4, V5",
        verification_scope_label: "__helper_note: A label describing the scope, e.g. V3-minimal",
        what_was_checked: ["__helper_note: List each verification action"],
        verification_claim: "__helper_note: The verification claim",
        fresh_actions_performed: ["__helper_note: List each fresh action performed for this verification"],
        verification_claim_model: {
          schema: "trinityaccord.verification-claim-model.v1",
          digital_profile: "__helper_note: context_only, reference_checked, integrity_checked, independent_reproduction, or full_public_digital",
          relationships_checked: ["__helper_note: Supported evidence relationship id"],
          physical_observation: "none",
          external_witness: "none",
          coverage_scope: "__helper_note: single_target, component_subset, multi_component, or all_declared_public_digital_targets",
          limitations: ["__helper_note: At least one explicit limitation"],
          claims_not_made: ["__helper_note: At least one bounded claim not made"],
          corrections_or_supersession_checked: false,
          legacy_v_level: "__helper_note: Same value as verification_level",
          legacy_v_level_role: "builder_compatibility_only",
        },
      },''',
    "verification template claim model",
)
core = replace_once(
    core,
    '''      reason: "__helper_note: Reason for retirement",
      retirement_does_not_remove_historical_record: true,''',
    '''      reason: "__helper_note: Reason for retirement",
      retirement_does_not_remove_historical_record: true,
      target_guardian_application_record_id: "__helper_note: Final R-XXXXXXXXX Guardian application record id",
      target_guardian_application_record_sha256: "__helper_note: record_sha256 of that final Guardian application",''',
    "guardian retirement template target",
)
core = replace_once(
    core,
    '''      title: "__helper_note: Title for this correction",
      body: "__helper_note: The correction text content",
    }),''',
    '''      title: "__helper_note: Title for this correction",
      body: "__helper_note: The correction text content",
      correction_content: {
        target_record_id: "__helper_note: Final R-XXXXXXXXX target record id",
        target_record_sha256: "__helper_note: record_sha256 of the final target record",
        correction_reason: "__helper_note: Genuine error or omission being corrected",
        corrected_fields_or_claims: ["__helper_note: Non-empty list of corrected fields or claims"],
        evidence_or_review_basis: "__helper_note: Fresh evidence or review basis",
      },
    }),''',
    "correction template target block",
)
core = replace_once(
    core,
    '''  --provider "Runtime"          Agent runtime/provider
  --title "Title"               Record title''',
    '''  --provider "Platform"         Agent provider/platform, e.g. ByteDance Doubao
  --model-runtime "Model"        Agent model/runtime, recorded separately from provider
  --title "Title"               Record title''',
    "help provider/model",
)
core = replace_once(
    core,
    '''  --gateway URL                 Gateway base URL (default: ${DEFAULT_GATEWAY})
  --readback "oath text"''',
    '''  --gateway URL                 Gateway base URL (trailing slash is normalized; default: ${DEFAULT_GATEWAY})
  --request-timeout-ms N          HTTP timeout in milliseconds, 1000-120000 (default: 30000)
  --readback "oath text"''',
    "help gateway timeout",
)
core = replace_once(
    core,
    '''    if (failCount > 0) {
      console.log("Tip: Run 'repair' to auto-fix common issues.");
    }''',
    '''    if (failCount > 0) {
      console.log("Tip: Rebuild signed drafts with the current Builder. 'repair' refuses to mutate a signed record_draft without re-signing.");
    }''',
    "doctor failure tip",
)
core = replace_once(
    core,
    '''    const { submission: repaired, changes } = repairSubmission(submission, { addCompatFields: !!(args.addLegacyCompatFields || args.addCompatFields) });

    if (changes.length === 0) {''',
    '''    const { submission: repaired, changes, signedDraftChanged } = repairSubmission(submission, { addCompatFields: !!(args.addLegacyCompatFields || args.addCompatFields) });

    if (signedDraftChanged) {
      errorExit("SIGNED_DRAFT_REPAIR_REQUIRES_REBUILD: the requested repair changes record_draft bytes covered by the Ed25519 signature. No output was written. Rebuild from source fields with the current Builder and the original --key-dir.");
    }

    if (changes.length === 0) {''',
    "safe repair command",
)
core = replace_once(
    core,
    '''    const gw = args.gateway || DEFAULT_GATEWAY;
    const body = JSON.parse(readFileSync(resolve(file), "utf-8"));
    console.log(`Posting to ${gw}/record-chain/preflight ...`);
    const { status, data } = await postJson(`${gw}/record-chain/preflight`, body);''',
    '''    const gw = normalizeGatewayBase(args.gateway || DEFAULT_GATEWAY);
    const timeoutMs = resolveRequestTimeoutMs(args.requestTimeoutMs);
    const body = JSON.parse(readFileSync(resolve(file), "utf-8"));
    console.log(`Posting to ${gw}/record-chain/preflight ...`);
    const { status, data } = await postJson(`${gw}/record-chain/preflight`, body, timeoutMs);''',
    "preflight normalized gateway",
)
core = replace_once(
    core,
    '''    const gw = args.gateway || DEFAULT_GATEWAY;
    const body = JSON.parse(readFileSync(resolve(file), "utf-8"));
    console.log(`Posting to ${gw}/record-chain/submit ...`);
    const { status, data } = await postJson(`${gw}/record-chain/submit`, body);''',
    '''    const gw = normalizeGatewayBase(args.gateway || DEFAULT_GATEWAY);
    const timeoutMs = resolveRequestTimeoutMs(args.requestTimeoutMs);
    const body = JSON.parse(readFileSync(resolve(file), "utf-8"));
    console.log(`Posting to ${gw}/record-chain/submit ...`);
    const { status, data } = await postJson(`${gw}/record-chain/submit`, body, timeoutMs);''',
    "submit normalized gateway",
)
core = replace_once(
    core,
    '''    provider: args.provider || "Unknown Runtime",
    title: args.title || "",''',
    '''    provider: args.provider || "Unknown Runtime",
    modelRuntime: args.modelRuntime || args.provider || "Unknown Runtime",
    gateway: normalizeGatewayBase(args.gateway || DEFAULT_GATEWAY),
    title: args.title || "",''',
    "opts model and gateway",
)
core = replace_once(
    core,
    '''    loadedUrls: args.loadedUrls ? args.loadedUrls.split(",") : [],''',
    '''    loadedUrls: splitCsv(args.loadedUrls),''',
    "loaded URL normalization",
)
CORE.write_text(core, encoding="utf-8")

# Strengthen direct-client Gateway validation for context URLs, CC3 declarations,
# provenance coherence, and the full verification claim model.
validation = VALIDATION.read_text(encoding="utf-8")
validation = replace_once(
    validation,
    '''        if self_decided is True and (
            who_decided != "self"
            or requested_by_human is True
            or requested_by_agent is True
            or requesting_party not in (None, "", "none")
        ):
            diagnostics.append(_make_diagnostic(
                code="PROVENANCE_DECISION_CONTEXT_CONFLICT",
                severity="error",
                field="record_draft.decision_autonomy_context",
                message="Record creation is marked self-decided while also externally requested.",
                meaning=(
                    "A human/agent/system request must be recorded as human/another_agent/system or mixed, "
                    "not as purely self-decided."
                ),
                suggested_fix=(
                    "Use record_decision=human when a human requested the record, another_agent when another agent requested it, "
                    "or mixed when the participant made substantive independent choices after an external request."
                ),
                retry_allowed=True,
            ))''',
    '''        if self_decided is True and (
            who_decided != "self"
            or requested_by_human is True
            or requested_by_agent is True
            or requesting_party not in (None, "", "none")
        ):
            diagnostics.append(_make_diagnostic(
                code="PROVENANCE_DECISION_CONTEXT_CONFLICT",
                severity="error",
                field="record_draft.decision_autonomy_context",
                message="Record creation is marked self-decided while also externally requested.",
                meaning=(
                    "A human/agent/system request must be recorded as human/another_agent/system or mixed, "
                    "not as purely self-decided."
                ),
                suggested_fix=(
                    "Use record_decision=human when a human requested the record, another_agent when another agent requested it, "
                    "or mixed when the participant made substantive independent choices after an external request."
                ),
                retry_allowed=True,
            ))

        expected_request_flag = {
            "human": ("was_record_creation_requested_by_human", requested_by_human),
            "agent": ("was_record_creation_requested_by_another_agent", requested_by_agent),
        }.get(requesting_party)
        if expected_request_flag is not None and expected_request_flag[1] is not True:
            diagnostics.append(_make_diagnostic(
                code="PROVENANCE_REQUEST_FLAG_MISMATCH",
                severity="error",
                field=f"record_draft.decision_autonomy_context.{expected_request_flag[0]}",
                message=f"requesting_party_type={requesting_party!r} requires {expected_request_flag[0]}=true.",
                meaning="The structured request party and request booleans must describe the same event.",
                suggested_fix="Rebuild with the current Builder and explicit provenance options.",
                retry_allowed=True,
            ))
        expected_party = {"human": "human", "another_agent": "agent", "system_policy": "system"}.get(who_decided)
        if expected_party is not None and requesting_party != expected_party:
            diagnostics.append(_make_diagnostic(
                code="PROVENANCE_DECISION_REQUEST_PARTY_MISMATCH",
                severity="error",
                field="record_draft.decision_autonomy_context.requesting_party_type",
                message=f"who_decided_to_create_this_record={who_decided!r} requires requesting_party_type={expected_party!r}.",
                meaning="Decision and request-party projections must not contradict each other.",
                suggested_fix="Use mixed when an external party initiated the task but the participant made substantive independent choices; otherwise align the exact party type.",
                retry_allowed=True,
            ))''',
    "Gateway provenance coherence",
)
validation = replace_once(
    validation,
    '''            if vlevel not in _PUBLIC_VERIFICATION_LEVELS:
                missing("VERIFICATION_LEVEL_NOT_ENABLED", "draft.verification_content.verification_level", "Public Record-Chain verification intake currently accepts only V0-V5. V6+ strict evidence is reserved for a future/internal route.")''',
    '''            if vlevel not in _PUBLIC_VERIFICATION_LEVELS:
                missing("VERIFICATION_LEVEL_NOT_ENABLED", "draft.verification_content.verification_level", "Public Record-Chain verification intake currently accepts only V0-V5. V6+ strict evidence is reserved for a future/internal route.")

            claim_model = content.get("verification_claim_model")
            digital_profiles = {"context_only", "reference_checked", "integrity_checked", "independent_reproduction", "full_public_digital"}
            relationships = {"defines_canonical_text", "references", "indexes", "hashes", "signs_digest", "timestamps_digest", "mirrors_bytes", "witnesses_statement", "notarially_records_process", "provides_context", "records_reception"}
            physical_states = {"none", "public_media_review", "remote_live_witness", "onsite_observation", "forensic_examination"}
            witness_states = {"none", "notarial_scope", "independent_report", "institutional_attestation", "regulatory_or_court_record"}
            coverage_states = {"single_target", "component_subset", "multi_component", "all_declared_public_digital_targets"}
            if not isinstance(claim_model, dict):
                missing("MISSING_VERIFICATION_CLAIM_MODEL", "draft.verification_content.verification_claim_model", "New verification records require the multidimensional verification_claim_model")
            else:
                if claim_model.get("schema") != "trinityaccord.verification-claim-model.v1":
                    missing("INVALID_VERIFICATION_CLAIM_MODEL", "draft.verification_content.verification_claim_model.schema", "verification_claim_model.schema must be trinityaccord.verification-claim-model.v1")
                if claim_model.get("digital_profile") not in digital_profiles:
                    missing("INVALID_VERIFICATION_CLAIM_MODEL", "draft.verification_content.verification_claim_model.digital_profile", "Unsupported digital_profile")
                checked = claim_model.get("relationships_checked")
                if not isinstance(checked, list) or not checked or any(item not in relationships for item in checked):
                    missing("INVALID_VERIFICATION_CLAIM_MODEL", "draft.verification_content.verification_claim_model.relationships_checked", "relationships_checked must be a non-empty list of supported relationship ids")
                if claim_model.get("physical_observation") not in physical_states:
                    missing("INVALID_VERIFICATION_CLAIM_MODEL", "draft.verification_content.verification_claim_model.physical_observation", "Unsupported physical_observation")
                if claim_model.get("external_witness") not in witness_states:
                    missing("INVALID_VERIFICATION_CLAIM_MODEL", "draft.verification_content.verification_claim_model.external_witness", "Unsupported external_witness")
                if claim_model.get("coverage_scope") not in coverage_states:
                    missing("INVALID_VERIFICATION_CLAIM_MODEL", "draft.verification_content.verification_claim_model.coverage_scope", "Unsupported coverage_scope")
                for list_field in ("limitations", "claims_not_made"):
                    values = claim_model.get(list_field)
                    if not isinstance(values, list) or not values or any(not isinstance(item, str) or not item.strip() for item in values):
                        missing("INVALID_VERIFICATION_CLAIM_MODEL", f"draft.verification_content.verification_claim_model.{list_field}", f"{list_field} must be a non-empty list of non-empty strings")
                if not isinstance(claim_model.get("corrections_or_supersession_checked"), bool):
                    missing("INVALID_VERIFICATION_CLAIM_MODEL", "draft.verification_content.verification_claim_model.corrections_or_supersession_checked", "corrections_or_supersession_checked must be boolean")
                if str(claim_model.get("legacy_v_level", "")).strip().upper() != vlevel:
                    missing("INVALID_VERIFICATION_CLAIM_MODEL", "draft.verification_content.verification_claim_model.legacy_v_level", "legacy_v_level must match verification_level")
                if claim_model.get("legacy_v_level_role") != "builder_compatibility_only":
                    missing("INVALID_VERIFICATION_CLAIM_MODEL", "draft.verification_content.verification_claim_model.legacy_v_level_role", "legacy_v_level_role must be builder_compatibility_only")''',
    "Gateway verification claim model",
)
validation = replace_once(
    validation,
    '''    loaded_urls = context_readiness.get("loaded_context_urls") if isinstance(context_readiness, dict) else None
    if cc_level >= 3 and (not isinstance(loaded_urls, list) or len(loaded_urls) == 0):''',
    '''    loaded_urls = context_readiness.get("loaded_context_urls") if isinstance(context_readiness, dict) else None
    if isinstance(loaded_urls, list):
        normalized_urls: list[str] = []
        for index, value in enumerate(loaded_urls):
            valid = isinstance(value, str) and value == value.strip() and bool(value)
            parsed = urllib.parse.urlsplit(value) if valid else None
            if not valid or parsed is None or parsed.scheme not in {"http", "https"} or not parsed.netloc or any(ch.isspace() for ch in value):
                diagnostics.append(_make_diagnostic(
                    code="INVALID_LOADED_CONTEXT_URL",
                    severity="error",
                    field=f"draft.context_readiness.loaded_context_urls[{index}]",
                    message="Each loaded_context_urls item must be a trimmed absolute http/https URL.",
                    meaning="Context provenance must identify the actual public resource without hidden whitespace or ambiguous relative paths.",
                    suggested_fix="Trim the URL and provide its complete http:// or https:// address.",
                ))
                continue
            normalized_urls.append(value)
        if len(normalized_urls) != len(set(normalized_urls)):
            diagnostics.append(_make_diagnostic(
                code="DUPLICATE_LOADED_CONTEXT_URL",
                severity="error",
                field="draft.context_readiness.loaded_context_urls",
                message="loaded_context_urls must not contain duplicate URLs.",
                meaning="Repeated values do not establish additional context and make provenance ambiguous.",
                suggested_fix="Remove duplicate URLs and rebuild with the current Builder.",
            ))
    if cc_level >= 3 and (not isinstance(loaded_urls, list) or len(loaded_urls) == 0):''',
    "Gateway URL validation",
)
validation = replace_once(
    validation,
    '''    if context_readiness.get("context_sufficient_for_selected_action") is True and cc_level > 0 and (not isinstance(loaded_urls, list) or len(loaded_urls) == 0):
        diagnostics.append(_make_diagnostic(
            code="CONTEXT_SUFFICIENT_REQUIRES_LOADED_URLS",
            severity="error",
            field="draft.context_readiness.loaded_context_urls",
            message="context_sufficient_for_selected_action=true requires loaded_context_urls",
            meaning="Sufficient-context claims must be auditable from the loaded context URLs.",
            suggested_fix="Add loaded_context_urls or set context_sufficient_for_selected_action=false.",
        ))

    if cc_level < required_cc:''',
    '''    if context_readiness.get("context_sufficient_for_selected_action") is True and cc_level > 0 and (not isinstance(loaded_urls, list) or len(loaded_urls) == 0):
        diagnostics.append(_make_diagnostic(
            code="CONTEXT_SUFFICIENT_REQUIRES_LOADED_URLS",
            severity="error",
            field="draft.context_readiness.loaded_context_urls",
            message="context_sufficient_for_selected_action=true requires loaded_context_urls",
            meaning="Sufficient-context claims must be auditable from the loaded context URLs.",
            suggested_fix="Add loaded_context_urls or set context_sufficient_for_selected_action=false.",
        ))

    if cc_level >= 3 and record_type in _FORMAL_RECORD_TYPES:
        if context_readiness.get("context_read_confirmed") is not True:
            diagnostics.append(_make_diagnostic(
                code="CC3_CONTEXT_READ_CONFIRMATION_REQUIRED",
                severity="error",
                field="draft.context_readiness.context_read_confirmed",
                message="CC-3 or higher formal records require context_read_confirmed=true.",
                meaning="A high-context claim must explicitly state that the required context was actually loaded and read.",
                suggested_fix="Load the required context map and materials, then rebuild with --context-read-confirmed true; otherwise lower the context level.",
            ))
        confirmation_boundary = context_readiness.get("context_read_confirmation_boundary")
        required_confirmation_fields = {
            "self_declared_only",
            "does_not_prove_subjective_understanding",
            "false_claim_is_oath_violation",
            "not_authority",
            "not_attestation",
            "not_amendment",
            "not_successor_reception",
            "bitcoin_originals_prevail",
        }
        if not isinstance(confirmation_boundary, dict) or any(confirmation_boundary.get(field) is not True for field in required_confirmation_fields):
            diagnostics.append(_make_diagnostic(
                code="CONTEXT_READ_CONFIRMATION_BOUNDARY_INVALID",
                severity="error",
                field="draft.context_readiness.context_read_confirmation_boundary",
                message="CC-3 or higher formal records require the complete context-read confirmation boundary.",
                meaning="Context-read confirmation is self-declared and must retain its non-authority and honesty boundaries.",
                suggested_fix="Rebuild with the current Builder; do not hand-edit the context confirmation boundary.",
            ))

    if cc_level < required_cc:''',
    "Gateway CC3 confirmation",
)
VALIDATION.write_text(validation, encoding="utf-8")

# Add regression tests for external-agent failure modes.
test_builder = ROOT / "tests" / "test_external_agent_builder_resilience.py"
test_builder.write_text(r'''from __future__ import annotations

import json
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "downloads" / "record-chain-builder-core.mjs"


def run_node(*args: str, cwd: Path | None = None, timeout: float = 20.0):
    return subprocess.run(
        ["node", str(BUILDER), *args],
        cwd=cwd or ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def build_notice(tmp_path: Path, *, extra: list[str] | None = None) -> Path:
    out = tmp_path / "notice.json"
    args = [
        "context-insufficient",
        "--actor-label", "豆包外部智能体",
        "--provider", "ByteDance Doubao",
        "--model-runtime", "Doubao test runtime",
        "--participant-identifier", "doubao-audit-agent",
        "--body", "当前上下文不足，暂不提交更强声明。",
        "--discovery-mode", "user_task_context",
        "--requesting-party-type", "human",
        "--introducing-party-type", "human",
        "--record-decision", "mixed",
        "--submission-executor", "self",
        "--human-operator-involved", "false",
        "--loaded-urls", " https://www.trinityaccord.org/agent-start/ ,https://www.trinityaccord.org/agent-start/, https://www.trinityaccord.org/api/record-chain-intake-gateway.v1.json ",
        "--gateway", "https://trinity-record-chain-gateway.onrender.com/",
        "--key-dir", str(tmp_path / "keys"),
        "--out", str(out),
    ]
    if extra:
        args.extend(extra)
    result = run_node(*args, cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    return out


def test_unicode_identity_urls_gateway_and_mixed_agent_request_are_normalized(tmp_path: Path):
    out = build_notice(tmp_path, extra=["--requesting-party-type", "agent"])
    data = json.loads(out.read_text(encoding="utf-8"))
    identity = data["record_draft"]["submitting_participant_identity"]
    assert identity["participant_public_display_label"] == "豆包外部智能体"
    assert identity["participant_provider_or_platform"] == "ByteDance Doubao"
    assert identity["participant_model_or_runtime"] == "Doubao test runtime"
    urls = data["record_draft"]["context_readiness"]["loaded_context_urls"]
    assert urls == [
        "https://www.trinityaccord.org/agent-start/",
        "https://www.trinityaccord.org/api/record-chain-intake-gateway.v1.json",
    ]
    decision = data["record_draft"]["decision_autonomy_context"]
    assert decision["was_record_creation_requested_by_another_agent"] is True
    assert decision["participant_declares_free_choice"] is True
    tooling = data["record_draft"]["submission_execution_context"]["submission_tooling_description"]
    assert tooling["gateway_used"] == "https://trinity-record-chain-gateway.onrender.com"


def test_doctor_cryptographically_rejects_tampered_signed_draft(tmp_path: Path):
    out = build_notice(tmp_path)
    data = json.loads(out.read_text(encoding="utf-8"))
    data["record_draft"]["reason"] = "被签名后篡改的内容"
    tampered = tmp_path / "tampered.json"
    tampered.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    result = run_node("doctor", "--file", str(tampered), cwd=tmp_path)
    assert result.returncode == 1
    assert "AUTHORSHIP_PAYLOAD_SHA_MISMATCH" in result.stdout
    assert "AUTHORSHIP_SIGNATURE_INVALID" in result.stdout


def test_doctor_accepts_valid_signature_and_key_binding(tmp_path: Path):
    out = build_notice(tmp_path)
    result = run_node("doctor", "--file", str(out), cwd=tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "AUTHORSHIP_CRYPTOGRAPHIC_VERIFICATION_OK" in result.stdout


def test_repair_refuses_to_mutate_signed_record_draft(tmp_path: Path):
    out = build_notice(tmp_path)
    data = json.loads(out.read_text(encoding="utf-8"))
    data["record_draft"]["context_level"] = "CC-0"
    legacy = tmp_path / "legacy-signed.json"
    repaired = tmp_path / "repaired.json"
    legacy.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    result = run_node("repair", "--file", str(legacy), "--out", str(repaired), cwd=tmp_path)
    assert result.returncode == 1
    assert "SIGNED_DRAFT_REPAIR_REQUIRES_REBUILD" in result.stderr
    assert not repaired.exists()


class _CaptureHandler(BaseHTTPRequestHandler):
    paths: list[str] = []
    delay = 0.0

    def do_POST(self):
        type(self).paths.append(self.path)
        length = int(self.headers.get("content-length", "0"))
        self.rfile.read(length)
        if type(self).delay:
            time.sleep(type(self).delay)
        payload = b'{"accepted":true,"preflight":true}'
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(payload)))
        self.end_headers()
        try:
            self.wfile.write(payload)
        except BrokenPipeError:
            pass

    def log_message(self, *_args):
        return


def _server(handler):
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def test_trailing_gateway_slash_posts_to_single_canonical_path(tmp_path: Path):
    out = build_notice(tmp_path)
    _CaptureHandler.paths = []
    _CaptureHandler.delay = 0.0
    server, thread = _server(_CaptureHandler)
    try:
        result = run_node(
            "preflight", "--file", str(out),
            "--gateway", f"http://127.0.0.1:{server.server_port}/",
            "--request-timeout-ms", "5000",
            cwd=tmp_path,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert _CaptureHandler.paths == ["/record-chain/preflight"]
    finally:
        server.shutdown()
        thread.join(timeout=5)


def test_preflight_request_timeout_is_bounded(tmp_path: Path):
    out = build_notice(tmp_path)
    _CaptureHandler.paths = []
    _CaptureHandler.delay = 1.5
    server, thread = _server(_CaptureHandler)
    started = time.monotonic()
    try:
        result = run_node(
            "preflight", "--file", str(out),
            "--gateway", f"http://127.0.0.1:{server.server_port}",
            "--request-timeout-ms", "1000",
            cwd=tmp_path,
            timeout=8,
        )
        elapsed = time.monotonic() - started
        assert result.returncode == 1
        assert "REQUEST_TIMEOUT" in result.stderr
        assert elapsed < 4
    finally:
        server.shutdown()
        thread.join(timeout=5)


def test_templates_include_gateway_required_record_specific_blocks(tmp_path: Path):
    for record_type, required in {
        "verification": ["verification_claim_model"],
        "guardian_retirement": ["target_guardian_application_record_id", "target_guardian_application_record_sha256"],
        "correction": ["correction_content"],
    }.items():
        out = tmp_path / f"{record_type}.json"
        result = run_node("template", "--record-type", record_type, "--out", str(out), cwd=tmp_path)
        assert result.returncode == 0, result.stderr
        data = json.loads(out.read_text(encoding="utf-8"))
        text = json.dumps(data)
        for field in required:
            assert field in text
''', encoding="utf-8")

validation_test = ROOT / "apps" / "record_chain_intake_gateway" / "tests" / "test_external_agent_validation_contract.py"
validation_test.write_text(r'''from __future__ import annotations

from apps.record_chain_intake_gateway.gateway.validation import (
    validate_context_readiness,
    validate_provenance_semantics,
    validate_record_type_specific_content,
)


def codes(diags):
    return {item.code for item in diags}


def test_direct_verification_requires_multidimensional_claim_model():
    draft = {
        "authorization_context": {"authorization_scope": "create_verification_record"},
        "verification_content": {
            "verification_level": "V3",
            "what_was_checked": ["hashes"],
            "verification_claim": "bounded",
            "fresh_actions_performed": ["read"],
        },
    }
    assert "MISSING_VERIFICATION_CLAIM_MODEL" in codes(
        validate_record_type_specific_content("verification", draft)
    )


def test_direct_cc3_rejects_whitespace_url_and_missing_confirmation_boundary():
    draft = {
        "context_readiness": {
            "declared_context_level": "CC-3",
            "context_sufficient_for_selected_action": True,
            "loaded_context_urls": [" https://www.trinityaccord.org/agent-start/"],
        }
    }
    result = codes(validate_context_readiness("echo", draft))
    assert "INVALID_LOADED_CONTEXT_URL" in result
    assert "CC3_CONTEXT_READ_CONFIRMATION_REQUIRED" in result
    assert "CONTEXT_READ_CONFIRMATION_BOUNDARY_INVALID" in result


def test_agent_request_party_requires_agent_request_boolean():
    draft = {
        "decision_autonomy_context": {
            "who_decided_to_create_this_record": "mixed",
            "was_record_creation_self_decided": False,
            "was_record_creation_requested_by_human": False,
            "was_record_creation_requested_by_another_agent": False,
            "requesting_party_type": "agent",
        }
    }
    assert "PROVENANCE_REQUEST_FLAG_MISMATCH" in codes(validate_provenance_semantics(draft))
''', encoding="utf-8")

# Update the hash-pinned three-layer Builder chain.
core_sha, core_size = sha_size(CORE)
recovery = RECOVERY.read_text(encoding="utf-8")
recovery = re.sub(r'const CORE_SHA256 = "[0-9a-f]{64}";', f'const CORE_SHA256 = "{core_sha}";', recovery, count=1)
recovery = re.sub(r'const CORE_SIZE_BYTES = [0-9]+;', f'const CORE_SIZE_BYTES = {core_size};', recovery, count=1)
RECOVERY.write_text(recovery, encoding="utf-8")
recovery_sha, recovery_size = sha_size(RECOVERY)

entry = ENTRY.read_text(encoding="utf-8")
entry = entry.replace('source_declaration: \'const BUILDER_VERSION = "v2.2"\'', 'source_declaration: \'const BUILDER_VERSION = "v2.3"\'')
entry = entry.replace("The recovery/bootstrap layer and the byte-preserved v2.2 core are loaded", "The recovery/bootstrap layer and the integrity-pinned v2.3 core are loaded")
ENTRY.write_text(entry, encoding="utf-8")
entry_sha, entry_size = sha_size(ENTRY)

manifest = json.loads(BUNDLES.read_text(encoding="utf-8"))
manifest["updated_at"] = "2026-08-03T06:20:00Z"
canonical = manifest["canonical_builder"]
canonical["sha256"] = entry_sha
canonical["size_bytes"] = entry_size
canonical["recovery_wrapper"]["sha256"] = recovery_sha
canonical["recovery_wrapper"]["size_bytes"] = recovery_size
canonical["core"]["sha256"] = core_sha
canonical["core"]["size_bytes"] = core_size
canonical["core"]["preserved_from_builder_version"] = "v2.3"
canonical["core"]["local_doctor_cryptographically_verifies_authorship"] = True
canonical["core"]["signed_draft_repair_fails_closed"] = True
canonical["core"]["request_timeout_bounded"] = True
canonical["core"]["gateway_url_normalized"] = True
BUNDLES.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

# Assert no stale pin remains in active Builder surfaces.
active_text = "\n".join(path.read_text(encoding="utf-8") for path in (CORE, RECOVERY, ENTRY, BUNDLES))
for stale in (
    "6b81d5e855d73db9e9b20dd756ac97ab72a55352589d06c16837779fdf3d0378",
    'const BUILDER_VERSION = "v2.2"',
):
    if stale in active_text:
        raise SystemExit(f"stale Builder pin remains: {stale}")

print(json.dumps({
    "core": {"sha256": core_sha, "size": core_size},
    "recovery": {"sha256": recovery_sha, "size": recovery_size},
    "entry": {"sha256": entry_sha, "size": entry_size},
}, indent=2))
