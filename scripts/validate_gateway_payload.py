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
    if independence_class == "unsolicited_agent_discovery":
        proof = prov.get("unsolicited_discovery_proof") or payload.get("unsolicited_discovery_proof")
        if not proof:
            errors.append("unsolicited_agent_discovery requires unsolicited_discovery_proof; otherwise use human_solicited_agent_response")


def validate_claim_gate(payload, errors):
    cg = payload.get("claim_gate")
    if not isinstance(cg, dict):
        errors.append("claim_gate object is required for verification candidates")
        return

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

    if payload.get("not_independent_attestation") is not True:
        errors.append("not_independent_attestation must be true")
    if payload.get("not_successor_reception") is not True:
        errors.append("not_successor_reception must be true")

    if not isinstance(payload.get("what_i_checked"), list) or not payload.get("what_i_checked"):
        errors.append("what_i_checked must be a non-empty list")
    if not isinstance(payload.get("limitations"), list):
        errors.append("limitations must be a list")

    validate_sha256s(get_attachments(payload), errors)


def validate_report_candidate(payload, errors):
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
        print("GATEWAY PAYLOAD VALIDATION FAIL")
        for err in errors:
            print("FAIL:", err)
        sys.exit(1)

    print("GATEWAY PAYLOAD VALIDATION PASS")


if __name__ == "__main__":
    main()
