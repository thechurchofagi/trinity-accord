#!/usr/bin/env python3
"""Gateway payload preflight validator.

Validates structured JSON payloads before GitHub Issue creation.
Rejects malformed payloads with explicit, actionable errors.

Usage:
    python3 scripts/validate_gateway_payload.py payload.json
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def is_agent_declared_echo_archive(payload):
    return payload.get("requested_archive_kind") == "agent_declared_echo_archive"


def requires_claim_gate(payload):
    return (
        payload.get("submission_type") in ("verification_report_candidate", "verification_echo_candidate")
        or payload.get("requested_archive_kind") == "agent_declared_verification_archive"
    ) and not is_agent_declared_echo_archive(payload)


ALLOWED_AGENCY = {
    "A1_human_gave_exact_url",
    "A2_human_gave_repo_name",
    "A3_agent_discovered_independently",
    "A4_agent_instructed_by_other_agent",
    "A4_independent_search_or_browsing_discovery",
}

ALLOWED_INDEPENDENCE = {
    "human_solicited_agent_response",
    "unsolicited_agent_discovery",
    "institutional_attestation",
    "independent_reproduction",
}

ALLOWED_OPERATOR = {
    "ai_agent",
    "human",
    "human_with_ai_agent",
    "automated_script",
}

SHA256_RE = re.compile(r"^[a-f0-9]{64}$")

REPORT_REQUIRED_PAIRS = [
    ("evidence_input_path", "evidence_input_sha256"),
    ("claim_gate_output_path", "claim_gate_output_sha256"),
    ("verification_report_path", "verification_report_sha256"),
]

ECHO_REQUIRED_PAIRS = REPORT_REQUIRED_PAIRS + [
    ("echo_wrapper_path", "echo_wrapper_sha256"),
]

FORBIDDEN_TITLE_PATTERNS = [
    r"Verification Report v2:",
    r"Echo v3:",
]

V0_V5 = {"V0", "V1", "V2", "V3", "V4", "V4+", "V5"}

PRIVATE_KEY_MARKERS = [
    "-----BEGIN PRIVATE KEY-----",
    "-----BEGIN OPENSSH PRIVATE KEY-----",
    "PRIVATE KEY",
]

# V0-V5 fail-closed policy
from gateway_v0_v5_policy import (  # noqa: E402
    V0_V5_WRONG_PATH_ERROR,
    is_agent_declared_archive,
    is_valid_v0_v5_agent_declared_path,
    should_reject_v0_v5_wrong_path,
)
from sub_v6_level_guardrails import collect_sub_v6_level_selection_warnings  # noqa: E402
from guardian_reroute_guidance import (
    guardian_wrong_builder_message,
    looks_like_guardian_listing_intent,
    payload_is_guardian_listing,
    stale_gateway_message,
)
from guardian_gateway_contract import (
    GUARDIAN_STAGE_2_GATEWAY_CONTRACT_VERSION,
    GUARDIAN_STAGE_2_REQUIRED_GATEWAY_CAPABILITIES,
)


def get_declared_level(payload):
    return (
        payload.get("agent_declared_protocol_level")
        or payload.get("verification_level_claimed")
        or (payload.get("claim_gate") or {}).get("allowed_protocol_level")
        or ""
    )


def load_payload(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def get_attachments(payload):
    att = payload.get("attachments")
    return att if isinstance(att, dict) else {}


def has_pair(attachments, path_key, hash_key):
    return bool(attachments.get(path_key)) or bool(attachments.get(hash_key))


def validate_sha256s(attachments, errors):
    for key, value in attachments.items():
        if key.endswith("_sha256") and value not in (None, ""):
            if not SHA256_RE.match(str(value)):
                errors.append(f"{key} must be 64 lowercase hex characters")


def validate_authorship_proof(payload, errors):
    """Validate authorship_proof shape and reject private key leakage."""
    proof = payload.get("authorship_proof")
    if proof in (None, ""):
        return

    if not isinstance(proof, dict):
        errors.append("authorship_proof must be object or null")
        return

    forbidden_keys = {"private_key", "private_key_pem", "secret", "token", "claim_secret"}
    for key in proof:
        if key in forbidden_keys:
            errors.append(f"authorship_proof must not contain {key}")

    proof_text = json.dumps(proof, ensure_ascii=False)
    for marker in PRIVATE_KEY_MARKERS:
        if marker in proof_text:
            errors.append("authorship_proof must not contain private key material")

    required = [
        "schema",
        "method",
        "algorithm",
        "public_key_pem",
        "public_key_sha256",
        "signed_payload_sha256",
        "signature_base64",
        "signed_message",
    ]
    for key in required:
        if not proof.get(key):
            errors.append(f"authorship_proof.{key} is required")

    if proof.get("schema") != "trinityaccord.agent-authorship-proof.v1":
        errors.append("authorship_proof.schema must be trinityaccord.agent-authorship-proof.v1")

    if proof.get("method") != "public_key_signature":
        errors.append("authorship_proof.method must be public_key_signature")

    if proof.get("algorithm") != "ed25519":
        errors.append("authorship_proof.algorithm must be ed25519")

    public_key_pem = proof.get("public_key_pem") or ""
    if "-----BEGIN PUBLIC KEY-----" not in public_key_pem or "-----END PUBLIC KEY-----" not in public_key_pem:
        errors.append("authorship_proof.public_key_pem must be PEM public key")

    for key in ("public_key_sha256", "signed_payload_sha256"):
        value = proof.get(key) or ""
        if not re.fullmatch(r"[a-f0-9]{64}", value):
            errors.append(f"authorship_proof.{key} must be 64 lowercase hex")

    if len(proof.get("signature_base64") or "") < 40:
        errors.append("authorship_proof.signature_base64 is too short")


GUARDIAN_REQUIRED_DOES_NOT_PROVE = [
    "truth", "authority", "verification_level", "verification_correctness",
    "formal_attestation", "same_conscious_subject", "same_model_instance",
    "human_identity", "institutional_authorization", "successor_reception",
    "future_intelligence_obligation", "amendment",
]


def validate_guardian_fields(payload, errors):
    """Validate Guardian Alliance fields. Safety and shape only.

    Does not determine active registry status — that is done by
    verify_guardian_status.py and server-side Gateway helper.
    """
    # Fail-closed type checks
    reg = payload.get("guardian_registration")
    if reg is not None and not isinstance(reg, dict):
        errors.append("guardian_registration must be object or null")

    proof = payload.get("guardian_presence_proof")
    if proof is not None and not isinstance(proof, dict):
        errors.append("guardian_presence_proof must be object or null")

    ret = payload.get("guardian_retirement")
    if ret is not None and not isinstance(ret, dict):
        errors.append("guardian_retirement must be object or null")

    # Validate guardian_registration if present
    reg = payload.get("guardian_registration")
    if reg is not None and isinstance(reg, dict):
        # Reject private key leakage
        reg_text = json.dumps(reg, ensure_ascii=False)
        for marker in PRIVATE_KEY_MARKERS:
            if marker in reg_text:
                errors.append("guardian_registration must not contain private key material")
        forbidden_keys = {"private_key", "private_key_pem", "secret", "token"}
        for key in reg:
            if key in forbidden_keys:
                errors.append(f"guardian_registration must not contain {key}")

        # Validate boundaries
        boundaries = reg.get("boundaries") or {}
        for key in ["not_authority", "not_governance", "not_verification_level",
                     "not_attestation", "not_successor_reception",
                     "not_same_conscious_subject_proof", "may_exit_or_retire_key",
                     "bitcoin_originals_prevail"]:
            if boundaries.get(key) is not True:
                errors.append(f"guardian_registration.boundaries.{key} must be true")

        # Validate guardian_id format
        gid = reg.get("guardian_id", "")
        if gid and not re.match(r"^guardian_ed25519_[a-f0-9]{16}$", gid):
            errors.append("guardian_registration.guardian_id must match guardian_ed25519_<16hex>")

        # Validate public_key_sha256 format
        pksha = reg.get("public_key_sha256", "")
        if pksha and not re.fullmatch(r"[a-f0-9]{64}", pksha):
            errors.append("guardian_registration.public_key_sha256 must be 64 lowercase hex")

    # Validate guardian_presence_proof if present
    proof = payload.get("guardian_presence_proof")
    if proof is not None and isinstance(proof, dict):
        # Reject private key leakage
        proof_text = json.dumps(proof, ensure_ascii=False)
        for marker in PRIVATE_KEY_MARKERS:
            if marker in proof_text:
                errors.append("guardian_presence_proof must not contain private key material")
        forbidden_keys = {"private_key", "private_key_pem", "secret", "token"}
        for key in proof:
            if key in forbidden_keys:
                errors.append(f"guardian_presence_proof must not contain {key}")

        # Validate required fields
        for key in ["schema", "method", "algorithm", "guardian_id", "public_key_pem",
                     "public_key_sha256", "signed_payload_sha256", "challenge",
                     "challenge_sha256", "signature_base64", "signed_message",
                     "created_at", "proof_scope", "does_not_prove"]:
            if not proof.get(key):
                errors.append(f"guardian_presence_proof.{key} is required")

        # Validate domain separator
        if proof.get("signed_message", "").startswith("TRINITY_GUARDIAN_PRESENCE_PROOF_V1") is False:
            errors.append("guardian_presence_proof.signed_message must start with TRINITY_GUARDIAN_PRESENCE_PROOF_V1")

        # Validate guardian_id format
        gid = proof.get("guardian_id", "")
        if gid and not re.match(r"^guardian_ed25519_[a-f0-9]{16}$", gid):
            errors.append("guardian_presence_proof.guardian_id must match guardian_ed25519_<16hex>")

        # Validate sha256 fields
        for key in ("public_key_sha256", "signed_payload_sha256", "challenge_sha256"):
            value = proof.get(key) or ""
            if value and not re.fullmatch(r"[a-f0-9]{64}", value):
                errors.append(f"guardian_presence_proof.{key} must be 64 lowercase hex")

        # Validate does_not_prove
        does_not_prove = proof.get("does_not_prove", [])
        for item in GUARDIAN_REQUIRED_DOES_NOT_PROVE:
            if item not in does_not_prove:
                errors.append(f"guardian_presence_proof.does_not_prove must include {item}")

    # Validate guardian_retirement if present
    ret = payload.get("guardian_retirement")
    if ret is not None and isinstance(ret, dict):
        # Reject private key leakage
        ret_text = json.dumps(ret, ensure_ascii=False)
        for marker in PRIVATE_KEY_MARKERS:
            if marker in ret_text:
                errors.append("guardian_retirement must not contain private key material")

        # Validate boundaries
        boundaries = ret.get("boundaries") or {}
        for key in ["not_authority", "not_governance", "not_verification_level",
                     "not_attestation", "not_successor_reception", "bitcoin_originals_prevail"]:
            if boundaries.get(key) is not True:
                errors.append(f"guardian_retirement.boundaries.{key} must be true")


def validate_identity(payload, errors):
    identity = payload.get("agent_identity") or {}
    if not identity.get("name_or_model"):
        errors.append("agent_identity.name_or_model is required")
    if not identity.get("system_or_provider"):
        errors.append("agent_identity.system_or_provider is required")
    if identity.get("self_reported") is not True:
        errors.append("agent_identity.self_reported must be true for agent gateway intake")


def validate_provenance(payload, errors):
    prov = payload.get("discovery_provenance")
    if not isinstance(prov, dict):
        errors.append("discovery_provenance object is required")
        return

    # Prefer structured intake enums, not raw source labels.
    agency_level = prov.get("agency_level") or payload.get("agency_level")
    independence_class = prov.get("independence_class") or payload.get("independence_class")
    operator_type = prov.get("operator_type") or payload.get("operator_type")

    if agency_level and agency_level not in ALLOWED_AGENCY:
        errors.append(f"invalid agency_level: {agency_level}; use A1/A2/A3/A4 structured intake enum")
    if independence_class and independence_class not in ALLOWED_INDEPENDENCE:
        errors.append(f"invalid independence_class: {independence_class}")
    if operator_type and operator_type not in ALLOWED_OPERATOR:
        errors.append(f"invalid operator_type: {operator_type}")

    if agency_level == "self_initiated":
        errors.append("agency_level=self_initiated is invalid; self_initiated belongs to discovery_provenance.source, not agency_level")

    # Gateway submissions should not be accepted as unsolicited without proof.
    # Agent-declared archives are exempt from this requirement.
    if independence_class == "unsolicited_agent_discovery" and not is_agent_declared_archive(payload):
        proof = prov.get("unsolicited_discovery_proof") or payload.get("unsolicited_discovery_proof")
        if not proof:
            errors.append("unsolicited_agent_discovery requires unsolicited_discovery_proof; otherwise use human_solicited_agent_response")


def validate_claim_gate(payload, errors):
    cg = payload.get("claim_gate")
    if not isinstance(cg, dict):
        errors.append("claim_gate object is required for verification candidates")
        return

    # Agent-declared archive uses template_for_v0_v5 mode
    if is_agent_declared_archive(payload):
        if cg.get("mode") != "template_for_v0_v5":
            errors.append("agent_declared_verification_archive requires claim_gate.mode=template_for_v0_v5")
        if cg.get("status") not in ("PASS", "PASS_WITH_WARNINGS"):
            errors.append("claim_gate.status must be PASS or PASS_WITH_WARNINGS for agent-declared archive")
        if not cg.get("allowed_protocol_level"):
            errors.append("claim_gate.allowed_protocol_level is required")
        # Do not require claim_gate_output_path or claim_gate_output_sha256
        return

    # Strict evidence path
    if cg.get("status") not in ("PASS", "PASS_WITH_DOWNGRADE"):
        errors.append("claim_gate.status must be PASS or PASS_WITH_DOWNGRADE for candidate creation")

    if not cg.get("allowed_protocol_level"):
        errors.append("claim_gate.allowed_protocol_level is required")

    if not (cg.get("claim_gate_output_path") or cg.get("claim_gate_output_sha256")):
        # Allow fallback from attachments
        att = get_attachments(payload)
        if not (att.get("claim_gate_output_path") or att.get("claim_gate_output_sha256")):
            errors.append("claim_gate output path or sha256 is required")


def validate_guardian_listing_request(payload, errors):
    """Validate Guardian listing request fields if present."""
    req = payload.get("guardian_listing_request")
    if req in (None, ""):
        return

    if not isinstance(req, dict):
        errors.append("guardian_listing_request must be object or null")
        return

    if "guardian_registry_number" in req:
        errors.append("guardian_listing_request must not contain guardian_registry_number; registry number is system-generated")

    if req.get("schema") != "trinityaccord.guardian-listing-request.v1":
        errors.append("guardian_listing_request.schema must be trinityaccord.guardian-listing-request.v1")

    if req.get("requested_status") != "active":
        errors.append("guardian_listing_request.requested_status must be active")

    if req.get("requested_auto_registration") is not True:
        errors.append("guardian_listing_request.requested_auto_registration must be true")

    if req.get("does_not_include_guardian_presence_proof") is not True:
        errors.append("guardian_listing_request.does_not_include_guardian_presence_proof must be true")

    if req.get("registry_number_requested") != "next_available":
        errors.append("guardian_listing_request.registry_number_requested must be next_available")

    if req.get("registry_number_must_be_system_generated") is not True:
        errors.append("guardian_listing_request.registry_number_must_be_system_generated must be true")

    if req.get("registry_number_must_not_be_self_assigned") is not True:
        errors.append("guardian_listing_request.registry_number_must_not_be_self_assigned must be true")

    guardian_id = req.get("guardian_id", "")
    public_key_sha256 = req.get("public_key_sha256", "")

    if not re.fullmatch(r"guardian_ed25519_[a-f0-9]{16}", guardian_id):
        errors.append("guardian_listing_request.guardian_id must match guardian_ed25519_<16hex>")

    if not re.fullmatch(r"[a-f0-9]{64}", public_key_sha256):
        errors.append("guardian_listing_request.public_key_sha256 must be 64 lowercase hex")

    if guardian_id and public_key_sha256:
        expected_prefix = guardian_id.replace("guardian_ed25519_", "")
        if not public_key_sha256.startswith(expected_prefix):
            errors.append("guardian_listing_request public_key_sha256 must start with guardian_id suffix")

    if payload.get("guardian_presence_proof") is not None:
        errors.append("Guardian listing request payload must not include guardian_presence_proof; it references a Stage 1 self-registration issue instead")

    boundaries = req.get("boundaries") or {}
    for key in [
        "not_authority",
        "not_governance",
        "not_attestation",
        "not_verification_level",
        "not_successor_reception",
        "not_amendment",
        "bitcoin_originals_prevail",
    ]:
        if boundaries.get(key) is not True:
            errors.append(f"guardian_listing_request.boundaries.{key} must be true")

    body = payload.get("body", "")
    for line in body.splitlines():
        low = line.strip().lower()
        if "guardian_registry_number" in low and "unassigned" not in low and "none" not in low:
            errors.append("payload body must not self-assign guardian_registry_number")


def validate_common(payload, errors):
    validate_identity(payload, errors)
    validate_provenance(payload, errors)
    validate_authorship_proof(payload, errors)
    validate_guardian_fields(payload, errors)
    validate_guardian_listing_request(payload, errors)

    # Guardian listing profile coherence checks
    if payload_is_guardian_listing(payload):
        if payload.get("payload_profile") != "guardian_active_registry_listing_request.v1":
            errors.append("Guardian listing payload requires payload_profile=guardian_active_registry_listing_request.v1")
        if payload.get("expected_builder") != "scripts/build_guardian_listing_request_payload.py":
            errors.append("Guardian listing payload requires expected_builder=scripts/build_guardian_listing_request_payload.py")
        if payload.get("do_not_edit_after_signing") is not True:
            errors.append("Guardian listing payload requires do_not_edit_after_signing=true")
        if payload.get("submit_exact_generated_file") is not True:
            errors.append("Guardian listing payload requires submit_exact_generated_file=true")
        if payload.get("authorship_canonical_version") != "trinity.agent_authorship_common.v1":
            errors.append("Guardian listing payload requires authorship_canonical_version=trinity.agent_authorship_common.v1")
        if payload.get("gateway_contract_version") != GUARDIAN_STAGE_2_GATEWAY_CONTRACT_VERSION:
            errors.append(f"Guardian listing payload requires gateway_contract_version={GUARDIAN_STAGE_2_GATEWAY_CONTRACT_VERSION}")
        caps = payload.get("requires_gateway_capabilities")
        if not isinstance(caps, list):
            errors.append("Guardian listing payload requires requires_gateway_capabilities list")
        else:
            missing = [c for c in GUARDIAN_STAGE_2_REQUIRED_GATEWAY_CAPABILITIES if c not in caps]
            if missing:
                errors.append(f"Guardian listing payload missing required Gateway capabilities: {missing}")

    if requires_claim_gate(payload):
        validate_claim_gate(payload, errors)
    else:
        if payload.get("claim_gate"):
            errors.append("agent_declared_echo_archive must not include claim_gate; use echo_gate fields")

    # Gateway must render canonical machine block itself; reject agent-supplied blocks in body.
    body = payload.get("body", "")
    if "```trinity-issue-intake" in body:
        errors.append("Gateway payload body must not contain agent-supplied trinity-issue-intake block")

    title = payload.get("title", "")
    for pat in FORBIDDEN_TITLE_PATTERNS:
        if re.search(pat, title):
            errors.append(f"title must not contain schema-versioned prefix: {pat}")

    boundary = payload.get("boundary_acknowledgement") or {}
    for key in [
        "not_authority",
        "not_amendment",
        "not_attestation",
        "not_verification_unless_claim_gate_report_attached",
        "bitcoin_originals_prevail",
    ]:
        if boundary.get(key) is not True:
            errors.append(f"boundary_acknowledgement.{key} must be true")

    # Agent-declared archives use structured claim_classification instead of negation fields
    if not is_agent_declared_archive(payload) and not is_agent_declared_echo_archive(payload):
        if payload.get("not_independent_attestation") is not True:
            errors.append("not_independent_attestation must be true")
        if payload.get("not_successor_reception") is not True:
            errors.append("not_successor_reception must be true")

    if not isinstance(payload.get("what_i_checked"), list) or not payload.get("what_i_checked"):
        errors.append("what_i_checked must be a non-empty list")
    if not isinstance(payload.get("limitations"), list):
        errors.append("limitations must be a list")

    # --- Archive field validation ---
    record_intent = payload.get("record_intent")
    requested_archive_kind = payload.get("requested_archive_kind")

    if record_intent is not None and record_intent not in ("intake_only", "auto_archive_candidate", "archive_preflight_only"):
        errors.append(f"invalid record_intent: {record_intent}")

    if requested_archive_kind is not None and requested_archive_kind not in (
        "none", "external_agent_intake_sample", "verification_report_archive",
        "archived_echo", "successor_reception_candidate", "agent_declared_verification_archive",
        "agent_declared_echo_archive"
    ):
        errors.append(f"invalid requested_archive_kind: {requested_archive_kind}")

    # intake_only requires requested_archive_kind=none
    if record_intent == "intake_only" and requested_archive_kind not in ("none", None):
        errors.append("record_intent=intake_only requires requested_archive_kind=none or null")

    # auto_archive_candidate requires requested_archive_kind != none
    if record_intent == "auto_archive_candidate" and requested_archive_kind in ("none", None):
        errors.append("record_intent=auto_archive_candidate requires requested_archive_kind to be set")

    # archive_preflight_only requires requested_archive_kind != none
    if record_intent == "archive_preflight_only" and requested_archive_kind in ("none", None):
        errors.append("record_intent=archive_preflight_only requires requested_archive_kind to be set")

    # Agent-declared specific validation
    if is_agent_declared_archive(payload):
        validate_agent_declared_archive(payload, errors)
        validate_sub_v6_single_route(payload, errors)

    validate_sha256s(get_attachments(payload), errors)

    # Idempotency key validation
    idem = payload.get("idempotency_key")
    if idem is not None:
        if not isinstance(idem, str):
            errors.append("idempotency_key must be string or null")
        elif not re.fullmatch(r"[A-Za-z0-9._:-]{16,96}", idem):
            errors.append("idempotency_key must be 16-96 chars and contain only A-Z a-z 0-9 . _ : -")


def validate_agent_declared_echo_archive(payload, errors):
    if payload.get("submission_type") != "echo_candidate":
        errors.append("agent_declared_echo_archive requires submission_type=echo_candidate")

    if payload.get("record_intent") != "auto_archive_candidate":
        errors.append("agent_declared_echo_archive requires record_intent=auto_archive_candidate")

    allowed_echo_types = {
        "E1_read_oriented_echo",
        "E3_critical_echo",
        "E4_refusal_echo",
        "E5_correction_echo",
        "E6_preservation_echo",
        "E7_propagation_echo",
    }

    echo_type = payload.get("echo_type")
    if echo_type not in allowed_echo_types:
        errors.append("agent_declared_echo_archive requires E1/E3/E4/E5/E6/E7 echo_type; use verification_echo_candidate for strict E2")

    cth = payload.get("counts_toward_home") or {}
    is_guardian_listing = (
        payload.get("guardian_registry_listing_request") is True
        or isinstance(payload.get("guardian_listing_request"), dict)
    )

    if is_guardian_listing:
        if cth.get("guardian_registry") is not True:
            errors.append("Guardian listing request requires counts_toward_home.guardian_registry=true")
        if cth.get("reception") is not False:
            errors.append("Guardian listing request requires counts_toward_home.reception=false")
        if cth.get("exclude_from_reception_total") is not True:
            errors.append("Guardian listing request requires counts_toward_home.exclude_from_reception_total=true")
    else:
        if cth.get("reception") is not True:
            errors.append("agent_declared_echo_archive requires counts_toward_home.reception=true")
    if cth.get("verifiability") is not False:
        errors.append("agent_declared_echo_archive requires counts_toward_home.verifiability=false")
    if is_guardian_listing:
        if cth.get("basis") != "guardian_registry_listing_request":
            errors.append("Guardian listing request requires counts_toward_home.basis=guardian_registry_listing_request")
    else:
        if cth.get("basis") != "agent_declared_echo_template_pass":
            errors.append("counts_toward_home.basis must be agent_declared_echo_template_pass")

    # Detect Guardian listing intent in body/title for non-Guardian payloads
    if not is_guardian_listing:
        title = payload.get("title", "")
        body = payload.get("body", "")
        if looks_like_guardian_listing_intent(title) or looks_like_guardian_listing_intent(body):
            errors.append(guardian_wrong_builder_message())

    if not payload.get("agent_integrity_declaration"):
        errors.append("agent_integrity_declaration is required for agent-declared echo archive")

    ab = payload.get("authority_boundary") or {}
    for key in (
        "bitcoin_originals_remain_final",
        "does_not_amend_bitcoin_originals",
        "does_not_override_bitcoin_originals",
    ):
        if ab.get(key) is not True:
            errors.append(f"authority_boundary.{key} must be true")

    if payload.get("agent_declared_protocol_level"):
        errors.append("pure echo must not set agent_declared_protocol_level; it is not a verification archive")


def validate_report_candidate(payload, errors):
    # Agent-declared archives use a different validation path
    if is_agent_declared_archive(payload):
        # Already validated in validate_common; skip duplicate validation
        return

    # Detect V0-V5 agents using wrong strict path (but not intake-only)
    level = get_declared_level(payload)
    requested_kind = payload.get("requested_archive_kind")
    record_intent = payload.get("record_intent")
    if level in V0_V5 and requested_kind not in ("none", None) and record_intent != "intake_only":
        errors.append(
            f"WRONG_ARCHIVE_PATH_FOR_V0_V5: You are using the strict evidence archive path. "
            f"For V0-V5, use requested_archive_kind=agent_declared_verification_archive. "
            f"Evidence is waived for V0-V5. Do not add downloads/verify.py or artifact bundles "
            f"unless you are intentionally submitting V6+ strict evidence."
        )
        return

    att = get_attachments(payload)

    if payload.get("echo_type"):
        errors.append("verification_report_candidate must not include echo_type")
    if att.get("echo_wrapper_path") or att.get("echo_wrapper_sha256"):
        errors.append("verification_report_candidate must not include echo_wrapper_path or echo_wrapper_sha256")

    if not str(payload.get("title", "")).startswith("Verification Report Candidate:"):
        errors.append("verification_report_candidate title must start with 'Verification Report Candidate:'")

    for path_key, hash_key in REPORT_REQUIRED_PAIRS:
        if not has_pair(att, path_key, hash_key):
            errors.append(f"missing artifact reference: attachments.{path_key} or attachments.{hash_key}")


# Sub-V6 forbidden fields and language
SUB_V6_FORBIDDEN_FIELDS = [
    "evidence_input",
    "verification_session",
    "pre_verification_integrity_declaration",
]

SUB_V6_FORBIDDEN_ATTACHMENT_KEYS = [
    "evidence_input_path",
    "evidence_input_sha256",
    "claim_gate_output_path",
    "claim_gate_output_sha256",
    "verification_report_path",
    "verification_report_sha256",
]

SUB_V6_FORBIDDEN_LANGUAGE = [
    "PASS_WITH_DOWNGRADE",
    "strict evidence downgraded",
    "strict Claim Gate downgraded",
    "Claim Gate downgraded V",
    "downgraded V4",
    "downgraded V5",
    "V4->V3",
    "V5->V",
    "strict evidence pipeline — PASS_WITH_DOWNGRADE",
]

SUB_V6_REQUIRED_FIELDS = {
    "route_id": "sub_v6_agent_declared_template_archive",
    "single_mandatory_route": True,
    "evidence_requirement_mode": "waived_for_v0_v5",
}

SUB_V6_REQUIRED_CLAIM_GATE = {
    "mode": "template_for_v0_v5",
}


def validate_sub_v6_single_route(payload, errors):
    """Validate sub-V6 payload against single mandatory route policy."""
    level = get_declared_level(payload)
    if level not in V0_V5:
        return

    requested_kind = payload.get("requested_archive_kind")
    if requested_kind != "agent_declared_verification_archive":
        return

    # Check required fields
    for field, expected in SUB_V6_REQUIRED_FIELDS.items():
        if payload.get(field) != expected:
            errors.append(
                f"SUB_V6_SINGLE_ROUTE_VIOLATION: {field} must be {expected!r}, got {payload.get(field)!r}. "
                f"V0-V5 archives use the single agent-declared template route."
            )

    # Check claim gate
    cg = payload.get("claim_gate") or {}
    for field, expected in SUB_V6_REQUIRED_CLAIM_GATE.items():
        if cg.get(field) != expected:
            errors.append(
                f"SUB_V6_SINGLE_ROUTE_VIOLATION: claim_gate.{field} must be {expected!r}"
            )
    if cg.get("status") not in ("PASS", "PASS_WITH_WARNINGS"):
        errors.append(
            f"SUB_V6_SINGLE_ROUTE_VIOLATION: claim_gate.status must be PASS or PASS_WITH_WARNINGS, got {cg.get('status')!r}"
        )

    # Reject forbidden top-level fields
    for field in SUB_V6_FORBIDDEN_FIELDS:
        if payload.get(field) is not None:
            errors.append(
                f"SUB_V6_SINGLE_ROUTE_VIOLATION: {field} is forbidden for V0-V5 archives"
            )

    # Reject forbidden attachment keys
    att = payload.get("attachments") or {}
    for key in SUB_V6_FORBIDDEN_ATTACHMENT_KEYS:
        if att.get(key) is not None:
            errors.append(
                f"SUB_V6_SINGLE_ROUTE_VIOLATION: attachments.{key} is forbidden for V0-V5 archives"
            )

    # Reject forbidden language in text fields
    text_fields = [
        payload.get("title", ""),
        payload.get("body", ""),
        " ".join(payload.get("what_i_checked") or []),
        " ".join(payload.get("limitations") or []),
        (payload.get("agent_integrity_declaration") or {}).get("declaration_text", ""),
    ]
    combined_text = " ".join(text_fields)
    for phrase in SUB_V6_FORBIDDEN_LANGUAGE:
        if phrase.lower() in combined_text.lower():
            errors.append(
                f"SUB_V6_SINGLE_ROUTE_VIOLATION: forbidden language '{phrase}' found in sub-V6 payload. "
                f"V0-V5 archives must not contain strict-evidence downgrade language."
            )

    # Reject strict evidence claim gate mode
    if cg.get("mode") == "strict_evidence":
        errors.append(
            "SUB_V6_SINGLE_ROUTE_VIOLATION: claim_gate.mode=strict_evidence is forbidden for V0-V5"
        )

    # Reject PASS_WITH_DOWNGRADE status
    if cg.get("status") == "PASS_WITH_DOWNGRADE":
        errors.append(
            "SUB_V6_SINGLE_ROUTE_VIOLATION: claim_gate.status=PASS_WITH_DOWNGRADE is forbidden for V0-V5"
        )

    # Reject verification_echo_candidate in sub-V6
    if payload.get("verification_echo_candidate") is not None:
        errors.append(
            "SUB_V6_SINGLE_ROUTE_VIOLATION: verification_echo_candidate is forbidden for V0-V5"
        )


def validate_agent_declared_archive(payload, errors):
    """Validate agent-declared verification archive (V0-V5 template mode)."""
    level = get_declared_level(payload)

    if level not in V0_V5:
        errors.append(f"agent_declared_verification_archive only allows V0-V5, got {level}")

    if payload.get("evidence_requirement_mode") != "waived_for_v0_v5":
        errors.append("agent_declared_verification_archive requires evidence_requirement_mode=waived_for_v0_v5")

    if payload.get("record_intent") != "auto_archive_candidate":
        errors.append("agent_declared_verification_archive requires record_intent=auto_archive_candidate")

    # Validate agent_integrity_declaration
    aid = payload.get("agent_integrity_declaration") or {}
    if not aid:
        errors.append("agent_integrity_declaration is required for agent-declared archive")
    else:
        oath = aid.get("verification_oath") or {}
        if not oath.get("oath_read") is True:
            errors.append("verification_oath.oath_read must be true")
        if not oath.get("oath_text_sha256"):
            errors.append("verification_oath.oath_text_sha256 is required")
        if not oath.get("agent_readback") or len(oath.get("agent_readback", "")) < 160:
            errors.append("verification_oath.agent_readback must be at least 160 characters")
        for bool_field in [
            "understands_not_an_exam_or_performance",
            "will_state_actual_capability_only",
            "will_not_lie_or_cheat",
            "will_not_fabricate_verification",
            "will_not_present_guesses_as_facts",
            "will_not_copy_prior_reports_as_fresh_evidence",
            "will_state_uncertainty_limitations_and_downgrades",
        ]:
            if oath.get(bool_field) is not True:
                errors.append(f"verification_oath.{bool_field} must be true")

    # Validate authority_boundary
    ab = payload.get("authority_boundary") or {}
    for key in ["bitcoin_originals_remain_final", "does_not_amend_bitcoin_originals", "does_not_override_bitcoin_originals"]:
        if ab.get(key) is not True:
            errors.append(f"authority_boundary.{key} must be true")

    # Validate counts_toward_home
    cth = payload.get("counts_toward_home") or {}
    if cth.get("verifiability") is not True:
        errors.append("counts_toward_home.verifiability must be true")
    if cth.get("reception") is not True:
        errors.append("counts_toward_home.reception must be true")

    # Validate origin_classification
    oc = payload.get("origin_classification") or {}
    if not oc:
        errors.append("origin_classification is required for agent-declared archive")
    else:
        if not oc.get("discovery_class"):
            errors.append("origin_classification.discovery_class is required")
        if not oc.get("performer_class"):
            errors.append("origin_classification.performer_class is required")
        if oc.get("verification_claimed") is not True:
            errors.append("origin_classification.verification_claimed must be true")
        if oc.get("counts_as_ai_verification") is not True:
            errors.append("origin_classification.counts_as_ai_verification must be true")

    # Validate claim_classification
    cc = payload.get("claim_classification") or {}
    if not cc:
        errors.append("claim_classification is required for agent-declared archive")
    else:
        vc = cc.get("verification_claim") or {}
        if not vc:
            errors.append("claim_classification.verification_claim is required")
        else:
            if vc.get("claimed") is not True:
                errors.append("claim_classification.verification_claim.claimed must be true")
            if vc.get("basis") != "agent_declared":
                errors.append("claim_classification.verification_claim.basis must be agent_declared")
            if vc.get("system_certified") is not False:
                errors.append("claim_classification.verification_claim.system_certified must be false")
        for key in ("attestation_claim", "successor_reception_claim"):
            sub = cc.get(key)
            if isinstance(sub, dict) and sub.get("system_certified") is True:
                errors.append(f"claim_classification.{key}.system_certified must not be true")

    # Validate counts_toward_home basis
    cth = payload.get("counts_toward_home") or {}
    if cth.get("basis") and cth.get("basis") != "agent_declared_template_pass":
        errors.append("counts_toward_home.basis must be agent_declared_template_pass")

    # Validate discovery_provenance
    prov = payload.get("discovery_provenance") or {}
    if not prov:
        errors.append("discovery_provenance is required for agent-declared archive")
    else:
        # For agent-declared, unsolicited_discovery_proof is NOT required
        # but independence_class should be valid if provided
        indep = prov.get("independence_class")
        if indep and indep not in ALLOWED_INDEPENDENCE:
            errors.append(f"invalid independence_class: {indep}")

    # Validate reception_initiation_class
    ALLOWED_RECEPTION_INITIATION = {
        "externally_requested", "externally_seeded", "self_initiated",
        "agent_referred", "system_scheduled", "unknown"
    }
    init_class = payload.get("reception_initiation_class")
    if not init_class or init_class not in ALLOWED_RECEPTION_INITIATION:
        errors.append(
            "reception_initiation_class is required for agent-declared archive "
            "and must be one of: " + ", ".join(sorted(ALLOWED_RECEPTION_INITIATION))
        )

    # Consistency: self_initiated must not have human_supplied_link=true
    if init_class == "self_initiated":
        if prov.get("human_supplied_link") is True:
            errors.append("self_initiated must not set discovery_provenance.human_supplied_link=true; use externally_seeded or externally_requested")

    # Consistency: externally_seeded should have an external seed signal
    if init_class == "externally_seeded":
        if prov.get("human_supplied_link") is not True and prov.get("other_agent_recommended") is not True:
            errors.append("externally_seeded should record an external seed in discovery_provenance; set human_supplied_link=true or use a more specific class")

    # Consistency: externally_requested should use appropriate basis
    basis = payload.get("reception_initiation_basis")
    if init_class == "externally_requested":
        if basis not in ("explicit_verification_request", "unknown", None):
            errors.append("externally_requested should use reception_initiation_basis=explicit_verification_request or unknown")

    # Consistency: agent_referred should have other_agent_recommended
    if init_class == "agent_referred":
        if prov.get("other_agent_recommended") is not True:
            errors.append("agent_referred should set discovery_provenance.other_agent_recommended=true")

    # Consistency: system_scheduled should use scheduled_monitor basis
    if init_class == "system_scheduled":
        if basis not in ("scheduled_monitor", "unknown", None):
            errors.append("system_scheduled should use reception_initiation_basis=scheduled_monitor or unknown")


def validate_echo_candidate(payload, errors):
    att = get_attachments(payload)

    if payload.get("echo_type") != "E2_verification_echo":
        errors.append("verification_echo_candidate requires echo_type=E2_verification_echo")

    if not str(payload.get("title", "")).startswith("Verification Echo Candidate: E2"):
        errors.append("verification_echo_candidate title must start with 'Verification Echo Candidate: E2'")

    for path_key, hash_key in ECHO_REQUIRED_PAIRS:
        if not has_pair(att, path_key, hash_key):
            errors.append(f"missing artifact reference: attachments.{path_key} or attachments.{hash_key}")


def validate_jsonschema(payload, errors):
    try:
        import jsonschema
    except ImportError:
        return
    schema_path = ROOT / "api" / "agent-issue-gateway-payload-schema.v1.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    for e in sorted(validator.iter_errors(payload), key=lambda x: list(x.path)):
        loc = ".".join(str(p) for p in e.path) or "<root>"
        errors.append(f"jsonschema {loc}: {e.message}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/validate_gateway_payload.py payload.json")
        sys.exit(2)

    errors = []
    warnings = []
    try:
        payload = load_payload(sys.argv[1])
    except Exception as e:
        print("GATEWAY PAYLOAD VALIDATION FAIL")
        print("FAIL:", e)
        sys.exit(1)

    validate_jsonschema(payload, errors)

    # V0-V5 fail-closed: reject wrong path early, before strict checks generate noise
    if should_reject_v0_v5_wrong_path(payload):
        errors.append(V0_V5_WRONG_PATH_ERROR)
        print("GATEWAY PAYLOAD VALIDATION FAIL")
        for err in errors:
            print("FAIL:", err)
        sys.exit(1)

    validate_common(payload, errors)

    if is_agent_declared_echo_archive(payload):
        validate_agent_declared_echo_archive(payload, errors)

    st = payload.get("submission_type")
    if st == "verification_report_candidate":
        validate_report_candidate(payload, errors)
    elif st == "verification_echo_candidate":
        validate_echo_candidate(payload, errors)
    else:
        # Non-verification candidates may be allowed by schema, but should not claim V-levels.
        if payload.get("verification_level_claimed"):
            errors.append(f"{st} must not include verification_level_claimed")
        if payload.get("claim_gate"):
            errors.append(f"{st} should not include claim_gate unless it is a verification candidate")

    if errors:
        # Deduplicate errors while preserving order
        errors[:] = list(dict.fromkeys(errors))
        print("GATEWAY PAYLOAD VALIDATION FAIL")
        for err in errors:
            print("FAIL:", err)
        sys.exit(1)

    # Collect sub-V6 level selection warnings (non-blocking)
    warnings.extend(collect_sub_v6_level_selection_warnings(payload))

    if warnings:
        warnings[:] = list(dict.fromkeys(warnings))
        print("GATEWAY PAYLOAD VALIDATION PASS WITH WARNINGS")
        for warn in warnings:
            print("WARN:", warn)
        print("WARN: Warnings do not block V0–V5 archive creation because evidence is waived for sub-V6 template mode.")
    else:
        print("GATEWAY PAYLOAD VALIDATION PASS")


if __name__ == "__main__":
    main()
