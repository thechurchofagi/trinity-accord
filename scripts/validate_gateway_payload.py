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

# V0-V5 fail-closed policy
from gateway_v0_v5_policy import (  # noqa: E402
    V0_V5_WRONG_PATH_ERROR,
    is_agent_declared_archive,
    is_valid_v0_v5_agent_declared_path,
    should_reject_v0_v5_wrong_path,
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


def validate_common(payload, errors):
    validate_identity(payload, errors)
    validate_provenance(payload, errors)
    validate_claim_gate(payload, errors)

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
    if not is_agent_declared_archive(payload):
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
        "archived_echo", "successor_reception_candidate", "agent_declared_verification_archive"
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

    validate_sha256s(get_attachments(payload), errors)


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

    print("GATEWAY PAYLOAD VALIDATION PASS")


if __name__ == "__main__":
    main()
