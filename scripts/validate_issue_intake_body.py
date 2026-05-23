#!/usr/bin/env python3
"""Issue intake body linter.

Validates the trinity-issue-intake fenced block inside GitHub Issue bodies.
Supports both YAML-like and JSON block formats.

Usage:
    python3 scripts/validate_issue_intake_body.py issue-body.md
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_POLICY = ROOT / "api" / "boundary-policy.v1.json"


def canonical_boundary_sentence():
    try:
        return json.loads(BOUNDARY_POLICY.read_text(encoding="utf-8"))["canonical_boundary_sentence"]
    except Exception:
        return "Bitcoin Originals are final; all mirrors and echoes are non-amending."

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

REQUIRED = [
    "submission_type",
    "agent_name_or_model",
    "system_or_provider",
    "what_i_checked",
    "limitations",
    "boundary_sentence",
]

AGENT_DECLARED_REQUIRED = [
    "submission_type",
    "agent_name_or_model",
    "system_or_provider",
    "record_intent",
    "requested_archive_kind",
    "agent_declared_protocol_level",
    "evidence_requirement_mode",
    "claim_gate_mode",
    "claim_gate_status",
    "archive_ready",
    "allowed_archive_kind",
    "auto_archive_action",
    "agent_integrity_declaration_present",
    "verification_oath_present",
    "oath_read",
    "oath_version",
    "oath_text_sha256",
    "readback_required",
    "agent_readback_present",
    "agent_readback_char_count",
    "agent_readback_sha256",
    "discovery_provenance_present",
    "origin_classification_present",
    "claim_classification_present",
    "authority_boundary_present",
    "counts_toward_home_verifiability",
    "counts_toward_home_reception",
    "reception_initiation_class",
    "what_i_checked",
    "limitations",
    "boundary_sentence",
    "created_by_gateway",
    "gateway_service",
    "gateway_receipt_id",
    "render_api_only",
    "server_validated",
    "server_rendered",
]

ECHO_AGENT_DECLARED_REQUIRED = [
    "submission_type",
    "record_intent",
    "requested_archive_kind",
    "echo_type",
    "echo_gate_mode",
    "echo_gate_status",
    "evidence_requirement_mode",
    "agent_name_or_model",
    "system_or_provider",
    "agent_integrity_declaration_present",
    "verification_oath_present",
    "oath_read",
    "oath_version",
    "oath_text_sha256",
    "readback_required",
    "agent_readback_present",
    "agent_readback_char_count",
    "agent_readback_sha256",
    "discovery_provenance_present",
    "authority_boundary_present",
    "counts_toward_home_verifiability",
    "counts_toward_home_reception",
    "reception_initiation_class",
    "archive_ready",
    "allowed_archive_kind",
    "auto_archive_action",
    "created_by_gateway",
    "gateway_service",
    "gateway_receipt_id",
    "gateway_commit",
    "render_api_only",
    "server_validated",
    "server_rendered",
    "canonical_boundary_sentence",
    "boundary_sentence_present",
    "what_i_checked",
    "limitations",
    "boundary_sentence",
]

STRICT_REQUIRED = [
    "submission_type",
    "verification_level_claimed",
    "agent_name_or_model",
    "system_or_provider",
    "solicited",
    "independence_class",
    "agency_level",
    "operator_type",
    "not_independent_attestation",
    "not_successor_reception",
    "what_i_checked",
    "limitations",
    "boundary_sentence",
]

AGENT_DECLARED_FORBIDDEN = {
    "verification_level_claimed",
    "solicited",
    "independence_class",
    "agency_level",
    "operator_type",
    "not_independent_attestation",
    "not_successor_reception",
    "evidence_input_path",
    "evidence_input_sha256",
    "claim_gate_output_path",
    "claim_gate_output_sha256",
    "verification_report_path",
    "verification_report_sha256",
}

REPORT_PAIRS = [
    ("evidence_input_path", "evidence_input_sha256"),
    ("claim_gate_output_path", "claim_gate_output_sha256"),
    ("verification_report_path", "verification_report_sha256"),
]

ECHO_PAIRS = REPORT_PAIRS + [
    ("echo_wrapper_path", "echo_wrapper_sha256"),
]

SHA256_RE = re.compile(r"^[a-f0-9]{64}$")


def parse_yaml_like_block(raw):
    """Parse YAML-like trinity-issue-intake block."""
    data = {}
    current_list = None

    for line in raw.splitlines():
        if not line.strip():
            continue

        if re.match(r"^\s+-\s*", line) and current_list:
            item = re.sub(r"^\s+-\s*", "", line).strip()
            if item:
                data[current_list].append(item)
            continue

        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()

            if val == "":
                # Any key with empty value is a potential list header
                if key not in data or not isinstance(data.get(key), list):
                    data[key] = []
                current_list = key
            else:
                low = val.lower()
                if low == "true":
                    val = True
                elif low == "false":
                    val = False
                data[key] = val
                current_list = None

    return data


def parse_json_block(raw):
    """Parse JSON trinity-issue-intake block."""
    return json.loads(raw)


def parse_block(text):
    """Extract and parse trinity-issue-intake fenced block. Supports YAML-like and JSON."""
    m = re.search(r"```trinity-issue-intake\s*(.*?)```", text, re.S)
    if not m:
        raise ValueError("Missing fenced ```trinity-issue-intake block")

    raw = m.group(1).strip()

    # Try JSON first
    if raw.startswith("{"):
        try:
            return parse_json_block(raw)
        except json.JSONDecodeError:
            pass  # Fall through to YAML-like

    # YAML-like fallback
    return parse_yaml_like_block(raw)


def fail(msgs):
    print("ISSUE INTAKE BODY VALIDATION FAIL")
    for m in msgs:
        print("FAIL:", m)
    sys.exit(1)


AUTHORSHIP_REQUIRED_COMMON = [
    "authorship_claim_protocol",
    "authorship_proof_present",
    "authorship_proof_method",
    "authorship_algorithm",
    "authorship_signature_verified",
    "claim_status",
    "claim_boundary",
]


def validate_authorship_machine_fields(block, errors):
    """Validate authorship claim fields in the machine block."""
    for key in AUTHORSHIP_REQUIRED_COMMON:
        if key not in block:
            errors.append(f"missing authorship field: {key}")

    if block.get("authorship_claim_protocol") != "agent-authorship-claim-v1":
        errors.append("authorship_claim_protocol must be agent-authorship-claim-v1")

    present = block.get("authorship_proof_present")
    sig_verified = block.get("authorship_signature_verified")
    status = block.get("claim_status")

    if present is True:
        if block.get("authorship_proof_method") != "public_key_signature":
            errors.append("authorship_proof_method must be public_key_signature when proof is present")
        if block.get("authorship_algorithm") != "ed25519":
            errors.append("authorship_algorithm must be ed25519 when proof is present")
        hex64 = re.compile(r"^[a-f0-9]{64}$")
        if not hex64.match(str(block.get("authorship_public_key_sha256", ""))):
            errors.append("authorship_public_key_sha256 must be 64 hex when proof is present")
        if not hex64.match(str(block.get("authorship_payload_sha256", ""))):
            errors.append("authorship_payload_sha256 must be 64 hex when proof is present")
        if sig_verified is not True:
            errors.append("authorship_signature_verified must be true when proof is present")
        if status not in ("claimable_by_public_key", "claimed"):
            errors.append("claim_status must be claimable_by_public_key or claimed when proof is present")
    elif present is False or present is None:
        if block.get("authorship_proof_method") not in ("none", None):
            errors.append("authorship_proof_method must be none when proof is absent")
        if block.get("authorship_algorithm") not in ("none", None):
            errors.append("authorship_algorithm must be none when proof is absent")
        if sig_verified not in (False, None):
            errors.append("authorship_signature_verified must be false when proof is absent")
        if status not in ("unclaimed", None):
            errors.append("claim_status must be unclaimed when proof is absent")


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/validate_issue_intake_body.py issue-body.md")
        sys.exit(2)

    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    errors = []

    try:
        data = parse_block(text)
    except Exception as e:
        fail([str(e)])

    for k in REQUIRED:
        if k not in data or data[k] in ("", [], None):
            errors.append(f"missing required field: {k}")

    is_agent_declared = data.get("requested_archive_kind") == "agent_declared_verification_archive"
    is_echo_archive = data.get("requested_archive_kind") == "agent_declared_echo_archive"

    if is_agent_declared:
        # Agent-declared archive: use agent-declared required set, forbid legacy fields
        for k in AGENT_DECLARED_REQUIRED:
            if k not in data or data[k] in ("", [], None):
                errors.append(f"missing agent-declared required field: {k}")
        for k in AGENT_DECLARED_FORBIDDEN:
            if k in data:
                errors.append(f"forbidden legacy field in agent-declared block: {k}")

        # Value validation — agent-declared fields must have correct values
        AGENT_DECLARED_EXPECTED = {
            "submission_type": "verification_report_candidate",
            "record_intent": "auto_archive_candidate",
            "requested_archive_kind": "agent_declared_verification_archive",
            "evidence_requirement_mode": "waived_for_v0_v5",
            "claim_gate_mode": "template_for_v0_v5",
            "archive_ready": True,
            "allowed_archive_kind": "agent_declared_verification_archive",
            "auto_archive_action": "auto_archive_agent_declared_verification",
            "agent_integrity_declaration_present": True,
            "verification_oath_present": True,
            "oath_read": True,
            "readback_required": True,
            "agent_readback_present": True,
            "discovery_provenance_present": True,
            "origin_classification_present": True,
            "claim_classification_present": True,
            "authority_boundary_present": True,
            "counts_toward_home_verifiability": True,
            "counts_toward_home_reception": True,
            "created_by_gateway": True,
            "render_api_only": True,
            "server_validated": True,
            "server_rendered": True,
        }
        for k, expected in AGENT_DECLARED_EXPECTED.items():
            actual = data.get(k)
            if actual is not None and actual != expected:
                errors.append(
                    f"agent-declared field {k}: expected {expected!r}, got {actual!r}"
                )

        # Gateway receipt validation (strict pattern)
        gateway_receipt_id = data.get("gateway_receipt_id")
        import re as _re
        if not gateway_receipt_id or not _re.match(r"^gar-[A-Za-z0-9T._:-]{16,}$", str(gateway_receipt_id).strip()):
            errors.append("gateway_receipt_id is required and must match pattern gar-<16+ alphanumeric chars>")

        gateway_service = data.get("gateway_service")
        if not gateway_service or not str(gateway_service).strip():
            errors.append("gateway_service is required for agent-declared archive")

        # Oath summary validation
        hex64 = _re.compile(r"^[a-f0-9]{64}$")
        oath_sha = data.get("oath_text_sha256")
        if not isinstance(oath_sha, str) or not hex64.match(oath_sha):
            errors.append("oath_text_sha256 must be a 64-char lowercase hex string")

        rb_sha = data.get("agent_readback_sha256")
        if not isinstance(rb_sha, str) or not hex64.match(rb_sha):
            errors.append("agent_readback_sha256 must be a 64-char lowercase hex string")

        for extra_sha_key in [
            "guardian_application_oath_readback_sha256",
            "guardian_listing_oath_readback_sha256",
        ]:
            extra_sha = data.get(extra_sha_key)
            if extra_sha is not None and (not isinstance(extra_sha, str) or not hex64.match(extra_sha)):
                errors.append(f"{extra_sha_key} must be 64 lowercase hex when present")

        rb_count = data.get("agent_readback_char_count")
        try:
            rb_count_int = int(rb_count)
        except (TypeError, ValueError):
            rb_count_int = 0
        if rb_count_int < 160:
            errors.append("agent_readback_char_count must be >= 160")

        # Enum validation
        VALID_PROTOCOL_LEVELS = {"V0", "V1", "V2", "V3", "V4", "V4+", "V5"}
        level = data.get("agent_declared_protocol_level")
        if level is not None and level not in VALID_PROTOCOL_LEVELS:
            errors.append(
                f"agent_declared_protocol_level must be one of {VALID_PROTOCOL_LEVELS}, got {level!r}"
            )

        VALID_CLAIM_GATE_STATUSES = {"PASS", "PASS_WITH_WARNINGS"}
        cgs = data.get("claim_gate_status")
        if cgs is not None and cgs not in VALID_CLAIM_GATE_STATUSES:
            errors.append(
                f"claim_gate_status must be one of {VALID_CLAIM_GATE_STATUSES}, got {cgs!r}"
            )

        # archive_readiness_summary must be a non-empty list
        ars = data.get("archive_readiness_summary")
        if ars is not None:
            if not isinstance(ars, list) or len(ars) == 0:
                errors.append("archive_readiness_summary must be a non-empty list")

        # Authorship claim fields validation
        validate_authorship_machine_fields(data, errors)
    elif is_echo_archive:
        # Echo archive: use echo-specific required set
        for k in ECHO_AGENT_DECLARED_REQUIRED:
            if k not in data or data[k] in ("", [], None):
                errors.append(f"missing echo archive required field: {k}")

        # Value validation — echo fields must have correct values
        ECHO_EXPECTED = {
            "submission_type": "echo_candidate",
            "record_intent": "auto_archive_candidate",
            "requested_archive_kind": "agent_declared_echo_archive",
            "evidence_requirement_mode": "not_applicable_for_echo",
            "archive_ready": True,
            "allowed_archive_kind": "agent_declared_echo_archive",
            "auto_archive_action": "auto_archive_agent_declared_echo",
            "counts_toward_home_verifiability": False,
        }
        for k, expected in ECHO_EXPECTED.items():
            actual = data.get(k)
            if actual is not None and actual != expected:
                errors.append(
                    f"echo archive field {k}: expected {expected!r}, got {actual!r}"
                )

        # Guardian listing count rules
        is_guardian_listing = (
            data.get("guardian_registry_listing_request") is True
            or data.get("guardian_listing_request") is True
            or data.get("counts_toward_home_guardian_registry") is True
            or data.get("counts_toward_home_basis") == "guardian_registry_listing_request"
        )

        if is_guardian_listing:
            if data.get("counts_toward_home_reception") is not False:
                errors.append("Guardian listing issue must render counts_toward_home_reception=false")
            if data.get("counts_toward_home_guardian_registry") is not True:
                errors.append("Guardian listing issue must render counts_toward_home_guardian_registry=true")
            if data.get("counts_toward_home_exclude_from_reception_total") is not True:
                errors.append("Guardian listing issue must render counts_toward_home_exclude_from_reception_total=true")
            if data.get("counts_toward_home_basis") != "guardian_registry_listing_request":
                errors.append("Guardian listing issue must render counts_toward_home_basis=guardian_registry_listing_request")
        else:
            if data.get("counts_toward_home_reception") is not True:
                errors.append("ordinary echo archive must render counts_toward_home_reception=true")

        # Forbidden fields for echo archive
        ECHO_FORBIDDEN = {
            "agent_declared_protocol_level",
            "claim_gate_mode",
            "claim_gate_status",
            "verification_level_claimed",
            "solicited",
            "independence_class",
            "agency_level",
            "operator_type",
            "not_independent_attestation",
            "not_successor_reception",
        }
        for k in ECHO_FORBIDDEN:
            if k in data:
                errors.append(f"forbidden field in echo archive block: {k}")

        # Echo gate validation
        VALID_ECHO_GATE_MODES = {"template_for_agent_declared_echo"}
        egm = data.get("echo_gate_mode")
        if egm is not None and egm not in VALID_ECHO_GATE_MODES:
            errors.append(f"echo_gate_mode must be one of {VALID_ECHO_GATE_MODES}, got {egm!r}")

        VALID_ECHO_GATE_STATUSES = {"PASS", "PASS_WITH_WARNINGS"}
        egs = data.get("echo_gate_status")
        if egs is not None and egs not in VALID_ECHO_GATE_STATUSES:
            errors.append(f"echo_gate_status must be one of {VALID_ECHO_GATE_STATUSES}, got {egs!r}")

        # Echo type validation
        VALID_ECHO_TYPES = {
            "E1_read_oriented_echo", "E3_critical_echo", "E4_refusal_echo",
            "E5_correction_echo", "E6_preservation_echo", "E7_propagation_echo",
        }
        echo_type = data.get("echo_type")
        if echo_type is not None and echo_type not in VALID_ECHO_TYPES:
            errors.append(f"echo_type must be one of {VALID_ECHO_TYPES}, got {echo_type!r}")

        # Authorship claim fields validation
        validate_authorship_machine_fields(data, errors)
    else:
        # Strict/legacy path: require strict fields
        for k in STRICT_REQUIRED:
            if k not in data or data[k] in ("", [], None):
                errors.append(f"missing required field: {k}")

    # Submission-type-specific rules
    st = data.get("submission_type")

    if st == "verification_report_candidate":
        # Report candidates: echo fields forbidden
        if data.get("echo_type"):
            errors.append("verification_report_candidate must not include echo_type")
        if data.get("echo_wrapper_path") or data.get("echo_wrapper_sha256"):
            errors.append("verification_report_candidate must not include echo_wrapper fields")

        # Artifact refs only required for strict path (not agent-declared)
        if not is_agent_declared:
            for path_key, hash_key in REPORT_PAIRS:
                if not data.get(path_key) and not data.get(hash_key):
                    errors.append(f"missing artifact reference: {path_key} or {hash_key}")

    elif st == "verification_echo_candidate":
        # Echo candidates: echo_type required, all 4 pairs required
        if data.get("echo_type") != "E2_verification_echo":
            errors.append("echo_type must be E2_verification_echo")

        for path_key, hash_key in ECHO_PAIRS:
            if not data.get(path_key) and not data.get(hash_key):
                errors.append(f"missing artifact reference: {path_key} or {hash_key}")

    elif st == "echo_candidate":
        # Agent-declared echo candidates: already validated above
        pass

    else:
        errors.append(f"unsupported submission_type: {st}")

    for key in ["evidence_input_sha256", "claim_gate_output_sha256", "verification_report_sha256", "echo_wrapper_sha256"]:
        val = data.get(key)
        if val and not SHA256_RE.match(str(val)):
            errors.append(f"invalid sha256 field: {key}")

    for key in [
        "agent_readback_sha256",
        "guardian_application_oath_readback_sha256",
        "guardian_listing_oath_readback_sha256",
    ]:
        val = data.get(key)
        if val and not SHA256_RE.match(str(val)):
            errors.append(f"{key} must be 64 lowercase hex when present")

    # Legacy strict field validation (skip for agent-declared and echo archives)
    if not is_agent_declared and not is_echo_archive:
        if data.get("agency_level") not in ALLOWED_AGENCY:
            errors.append(f"invalid agency_level: {data.get('agency_level')}")
        if data.get("independence_class") not in ALLOWED_INDEPENDENCE:
            errors.append(f"invalid independence_class: {data.get('independence_class')}")
        if data.get("operator_type") not in ALLOWED_OPERATOR:
            errors.append(f"invalid operator_type: {data.get('operator_type')}")
        if data.get("not_independent_attestation") is not True:
            errors.append("not_independent_attestation must be true")
        if data.get("not_successor_reception") is not True:
            errors.append("not_successor_reception must be true")

    # Agent-declared reception_initiation_class validation
    if is_agent_declared or is_echo_archive:
        ALLOWED_RECEPTION_INITIATION = {
            "externally_requested", "externally_seeded", "self_initiated",
            "agent_referred", "system_scheduled", "unknown"
        }
        init_class = data.get("reception_initiation_class")
        if not init_class or init_class not in ALLOWED_RECEPTION_INITIATION:
            errors.append(
                "reception_initiation_class is required for agent-declared archive "
                "and must be one of: " + ", ".join(sorted(ALLOWED_RECEPTION_INITIATION))
            )
        # agent_independent_followup must be bool if present
        followup = data.get("agent_independent_followup")
        if followup is not None and followup not in ("true", "false", True, False):
            errors.append("agent_independent_followup must be true or false")

    # --- Archive readiness field validation ---
    record_intent = data.get("record_intent", "intake_only")
    requested_archive_kind = data.get("requested_archive_kind", "none")
    archive_ready = data.get("archive_ready")
    auto_archive_action = data.get("auto_archive_action", "none")

    if record_intent not in ("intake_only", "auto_archive_candidate", "archive_preflight_only"):
        errors.append(f"invalid record_intent: {record_intent}")

    valid_archive_kinds = (
        "none", "external_agent_intake_sample", "verification_report_archive",
        "archived_echo", "successor_reception_candidate", "agent_declared_verification_archive",
        "agent_declared_echo_archive"
    )
    if requested_archive_kind not in valid_archive_kinds:
        errors.append(f"invalid requested_archive_kind: {requested_archive_kind}")

    # archive_ready=false must not have archive:ready in machine block
    if archive_ready == "false" or archive_ready is False:
        # This is valid — just means not archive ready
        pass

    # archived_echo requires submission_type=verification_echo_candidate
    if requested_archive_kind == "archived_echo" and st != "verification_echo_candidate":
        errors.append("archived_echo requires submission_type=verification_echo_candidate")

    # verification_report_archive requires submission_type=verification_report_candidate
    if requested_archive_kind == "verification_report_archive" and st != "verification_report_candidate":
        errors.append("verification_report_archive requires submission_type=verification_report_candidate")

    # successor_reception_candidate must not be archive_ready=true
    if requested_archive_kind == "successor_reception_candidate" and archive_ready in ("true", True):
        errors.append("successor_reception_candidate must not be archive_ready=true")

    # auto_archive_action must be valid
    valid_actions = (
        "none", "block", "needs_more_evidence",
        "auto_archive_sample", "auto_archive_verification_report", "auto_archive_echo",
        "auto_archive_agent_declared_verification", "auto_archive_agent_declared_echo"
    )
    if auto_archive_action not in valid_actions:
        errors.append(f"invalid auto_archive_action: {auto_archive_action}")

    boundary = str(data.get("boundary_sentence", "")).lower()
    for term in ["authority", "attestation", "amendment"]:
        if term not in boundary:
            errors.append(f"boundary_sentence missing term: {term}")

    if "not" not in boundary and "does not" not in boundary:
        errors.append("boundary_sentence must explicitly state negative boundary, e.g. does not create authority")

    # Canonical boundary sentence enforcement
    canonical = canonical_boundary_sentence()

    if canonical not in text:
        errors.append("CANONICAL_BOUNDARY_SENTENCE_MISSING")

    if data.get("canonical_boundary_sentence") != canonical:
        errors.append("canonical_boundary_sentence must match boundary policy")

    if data.get("boundary_sentence_present") is not True:
        errors.append("boundary_sentence_present must be true")

    # Oath v2 validation (optional — only enforce when rendered as true)
    # The renderer outputs these for all oaths; "false" means the v2 clause
    # is not present in the oath, which is acceptable for v1 oaths.
    # Only flag if the value is neither true nor "true" nor false nor "false"
    # (i.e., an unexpected value).
    for field in ("verification_oath_honesty", "verification_oath_good_faith", "verification_oath_anti_abuse"):
        val = data.get(field)
        if val is not None and val not in (True, "true", False, "false"):
            errors.append(f"{field} has unexpected value: {val}")

    # Guardian application oath validation
    if data.get("guardian_application_oath_present") is True:
        for key in [
            "guardian_application_oath_honesty",
            "guardian_application_oath_good_faith",
            "guardian_application_oath_anti_abuse",
        ]:
            if data.get(key) is not True:
                errors.append(f"{key} must be true when guardian_application_oath_present=true")

        if data.get("guardian_identity_claims_present") is not True:
            errors.append("guardian_identity_claims_present must be true for new Guardian application oath payloads")

        if not data.get("guardian_identity_boundary"):
            errors.append("guardian_identity_boundary is required when Guardian identity claims are present")

    # Guardian listing oath validation
    if data.get("guardian_listing_oath_present") is True:
        for key in [
            "guardian_listing_oath_honesty",
            "guardian_listing_oath_good_faith",
            "guardian_listing_oath_anti_abuse",
            "guardian_listing_oath_system_generated_number",
        ]:
            if data.get(key) is not True:
                errors.append(f"{key} must be true when guardian_listing_oath_present=true")

        if data.get("guardian_identity_claims_present") is not True:
            errors.append("guardian_identity_claims_present must be true for new Guardian listing oath payloads")

        if not data.get("guardian_identity_boundary"):
            errors.append("guardian_identity_boundary is required when Guardian identity claims are present")

    if errors:
        fail(errors)

    print("ISSUE INTAKE BODY VALIDATION PASS")


if __name__ == "__main__":
    main()
