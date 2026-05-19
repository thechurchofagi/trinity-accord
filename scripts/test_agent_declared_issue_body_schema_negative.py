#!/usr/bin/env python3
"""Negative tests for agent-declared machine block schema.

Verifies that mutated agent-declared blocks with incorrect values are rejected
by BOTH the JSON Schema AND the body validator (validate_issue_intake_body.py).

Each mutant changes ONE field to an invalid value and asserts rejection.
"""
import json
import re
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_gateway_payload.py"
RENDERER = ROOT / "scripts" / "render_gateway_issue_body.py"
BODY_VALIDATOR = ROOT / "scripts" / "validate_issue_intake_body.py"
SCHEMA = ROOT / "api" / "issue-intake-machine-block-schema.v1.json"
FIXTURE = ROOT / "fixtures" / "gateway" / "valid-agent-declared-v4.json"

PASS = 0
FAIL = 0


def run(cmd, input_text=None):
    return subprocess.run(cmd, text=True, capture_output=True, cwd=str(ROOT), input=input_text)


def block_to_renderer_yaml(block):
    """Convert block dict to the same YAML-like format the renderer produces.

    The body validator's parser uses r'\\s+-\\s*' for list items (requires
    leading whitespace), so we must indent list items by 2 spaces — matching
    the renderer's output format, NOT yaml.dump (which puts - at column 0).
    """
    lines = []
    for k, v in block.items():
        if isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        elif isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                lines.append(f"  - {item}")
        elif v is None:
            lines.append(f"{k}: null")
        else:
            lines.append(f"{k}: {v}")
    return "\n".join(lines)


def make_rendered_body_with_block(block_dict):
    """Build a synthetic issue body containing a trinity-issue-intake block."""
    block_yaml = block_to_renderer_yaml(block_dict)
    return (
        "This issue was submitted through the Agent Issue Gateway backend.\n\n"
        "Boundary:\n- Not authority\n\n"
        "```trinity-issue-intake\n"
        + block_yaml
        + "\n```\n"
    )


def schema_rejects(block, label):
    """Assert the block fails JSON Schema validation."""
    global PASS, FAIL
    schema = json.loads(SCHEMA.read_text())
    errors = list(Draft202012Validator(schema).iter_errors(block))
    if errors:
        PASS += 1
        print(f"  PASS [schema]: {label} — rejected ({len(errors)} error(s))")
    else:
        FAIL += 1
        print(f"  FAIL [schema]: {label} — schema accepted but should have rejected")


def schema_accepts(block, label):
    """Assert the block passes JSON Schema validation."""
    global PASS, FAIL
    schema = json.loads(SCHEMA.read_text())
    errors = list(Draft202012Validator(schema).iter_errors(block))
    if not errors:
        PASS += 1
        print(f"  PASS [schema]: {label} — accepted")
    else:
        FAIL += 1
        msgs = [str(e.message)[:80] for e in errors[:3]]
        print(f"  FAIL [schema]: {label} — rejected but should accept: {msgs}")


def body_validator_rejects(block, label):
    """Assert validate_issue_intake_body.py rejects the block."""
    global PASS, FAIL
    body = make_rendered_body_with_block(block)
    r = run([sys.executable, str(BODY_VALIDATOR), "/dev/stdin"], input_text=body)
    if r.returncode != 0 and "FAIL" in (r.stdout + r.stderr):
        PASS += 1
        print(f"  PASS [body-validator]: {label} — rejected")
    else:
        FAIL += 1
        print(f"  FAIL [body-validator]: {label} — accepted but should have rejected")
        print(f"    stdout: {r.stdout[:200]}")


def body_validator_accepts(block, label):
    """Assert validate_issue_intake_body.py accepts the block."""
    global PASS, FAIL
    body = make_rendered_body_with_block(block)
    r = run([sys.executable, str(BODY_VALIDATOR), "/dev/stdin"], input_text=body)
    if r.returncode == 0 and "PASS" in r.stdout:
        PASS += 1
        print(f"  PASS [body-validator]: {label} — accepted")
    else:
        FAIL += 1
        print(f"  FAIL [body-validator]: {label} — rejected but should accept")
        print(f"    stdout: {r.stdout[:300]}")
        print(f"    stderr: {r.stderr[:300]}")


def make_good_block():
    """Build a known-good agent-declared block (as it would be rendered)."""
    return {
        "submission_type": "verification_report_candidate",
        "agent_name_or_model": "Smoke Agent",
        "system_or_provider": "Local Test",
        "record_intent": "auto_archive_candidate",
        "requested_archive_kind": "agent_declared_verification_archive",
        "agent_declared_protocol_level": "V4",
        "evidence_requirement_mode": "waived_for_v0_v5",
        "claim_gate_mode": "template_for_v0_v5",
        "claim_gate_status": "PASS",
        "agent_integrity_declaration_present": True,
        "verification_oath_present": True,
        "oath_read": True,
        "oath_version": "verification-echo-pre-oath-v1",
        "oath_text_sha256": "eb2f528df3514d75dd18348928bfa04f7d59c5fdc66f1c6496accc64254da5e8",
        "readback_required": True,
        "agent_readback_present": True,
        "agent_readback_char_count": 280,
        "agent_readback_sha256": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
        "discovery_provenance_present": True,
        "origin_classification_present": True,
        "claim_classification_present": True,
        "authority_boundary_present": True,
        "counts_toward_home_verifiability": True,
        "counts_toward_home_reception": True,
        "what_i_checked": ["Read homepage"],
        "limitations": ["Evidence waived"],
        "archive_ready": True,
        "allowed_archive_kind": "agent_declared_verification_archive",
        "auto_archive_action": "auto_archive_agent_declared_verification",
        "archive_readiness_summary": ["CLAIM_GATE_TEMPLATE_PASS"],
        "canonical_boundary_sentence": "Bitcoin Originals are final; all mirrors and echoes are non-amending.",
        "boundary_sentence_present": True,
        "boundary_sentence": "Bitcoin Originals are final; all mirrors and echoes are non-amending. This Issue does not create authority, attestation, amendment, archive status, or verification-level upgrade unless the relevant machine gates pass.",
        "reception_initiation_class": "self_initiated",
        "reception_initiation_basis": "agent_discovered_publicly",
        "agent_independent_followup": True,
        "created_by_gateway": True,
        "gateway_service": "trinity-agent-issue-gateway",
        "gateway_receipt_id": "gar-20260517T120000-abc12345",
        "render_api_only": True,
        "server_validated": True,
        "server_rendered": True,
        "authorship_claim_protocol": "agent-authorship-claim-v1",
        "authorship_proof_present": False,
        "authorship_proof_method": "none",
        "authorship_algorithm": "none",
        "authorship_public_key_sha256": "none",
        "authorship_payload_sha256": "none",
        "authorship_signature_verified": False,
        "claim_endpoint": "/gateway/claim-authorship",
        "claim_status": "unclaimed",
        "claim_boundary": "Authorship claim proves key continuity only; it is not authority, attestation, successor reception, truth, or amendment.",
    }


def main():
    global PASS, FAIL

    print("=== Agent-Declared Machine Block Negative Tests ===\n")

    # --- Baseline: good block passes both ---
    print("--- Baseline: good block ---")
    good = make_good_block()
    schema_accepts(good, "good block")
    body_validator_accepts(good, "good block")

    # --- Mutant tests ---
    mutants = [
        # (field, bad_value, description)
        ("record_intent", "intake_only", "record_intent=intake_only"),
        ("record_intent", "archive_preflight_only", "record_intent=archive_preflight_only"),
        ("evidence_requirement_mode", "strict", "evidence_requirement_mode=strict"),
        ("evidence_requirement_mode", "required", "evidence_requirement_mode=required"),
        ("claim_gate_mode", "strict_evidence", "claim_gate_mode=strict_evidence"),
        ("claim_gate_mode", "template", "claim_gate_mode=template (not template_for_v0_v5)"),
        ("claim_gate_status", "FAIL", "claim_gate_status=FAIL"),
        ("claim_gate_status", "PENDING", "claim_gate_status=PENDING"),
        ("archive_ready", False, "archive_ready=false"),
        ("archive_ready", "false", 'archive_ready="false"'),
        ("allowed_archive_kind", "none", "allowed_archive_kind=none"),
        ("allowed_archive_kind", "verification_report_archive", "allowed_archive_kind=verification_report_archive"),
        ("auto_archive_action", "none", "auto_archive_action=none"),
        ("auto_archive_action", "block", "auto_archive_action=block"),
        ("agent_integrity_declaration_present", False, "agent_integrity_declaration_present=false"),
        ("discovery_provenance_present", False, "discovery_provenance_present=false"),
        ("origin_classification_present", False, "origin_classification_present=false"),
        ("claim_classification_present", False, "claim_classification_present=false"),
        ("authority_boundary_present", False, "authority_boundary_present=false"),
        ("counts_toward_home_verifiability", False, "counts_toward_home_verifiability=false"),
        ("counts_toward_home_reception", False, "counts_toward_home_reception=false"),
        ("agent_declared_protocol_level", "V6", "agent_declared_protocol_level=V6"),
        ("agent_declared_protocol_level", "V8", "agent_declared_protocol_level=V8"),
        ("agent_declared_protocol_level", "B1", "agent_declared_protocol_level=B1"),
        ("requested_archive_kind", "verification_report_archive", "requested_archive_kind=verification_report_archive"),
        ("requested_archive_kind", "none", "requested_archive_kind=none"),
        ("submission_type", "verification_echo_candidate", "submission_type=verification_echo_candidate"),
    ]

    print("\n--- Schema + Body Validator: field value mutants ---")
    for field, bad_val, desc in mutants:
        block = make_good_block()
        block[field] = bad_val
        schema_rejects(block, desc)
        body_validator_rejects(block, desc)

    # --- Legacy field injection mutants ---
    print("\n--- Legacy field injection mutants ---")
    legacy_fields = [
        ("not_independent_attestation", True),
        ("not_successor_reception", True),
        ("verification_level_claimed", "V4"),
        ("solicited", True),
        ("independence_class", "human_solicited_agent_response"),
        ("agency_level", "A2_human_gave_repo_name"),
        ("operator_type", "ai_agent"),
        ("evidence_input_path", "/tmp/evidence.json"),
        ("evidence_input_sha256", "a" * 64),
        ("claim_gate_output_path", "/tmp/gate.json"),
        ("claim_gate_output_sha256", "b" * 64),
        ("verification_report_path", "/tmp/report.json"),
        ("verification_report_sha256", "c" * 64),
    ]

    for field_name, field_val in legacy_fields:
        block = make_good_block()
        block[field_name] = field_val
        desc = f"agent-declared + {field_name}={field_val!r}"
        schema_rejects(block, desc)
        body_validator_rejects(block, desc)

    # --- Cross-path: strict block is still valid ---
    print("\n--- Cross-path: strict block unaffected ---")
    strict_block = {
        "submission_type": "verification_report_candidate",
        "verification_level_claimed": "V6",
        "agent_name_or_model": "test-agent",
        "system_or_provider": "test",
        "solicited": True,
        "independence_class": "human_solicited_agent_response",
        "agency_level": "A2_human_gave_repo_name",
        "operator_type": "ai_agent",
        "not_independent_attestation": True,
        "not_successor_reception": True,
        "what_i_checked": ["test"],
        "limitations": ["test"],
        "boundary_sentence": "Bitcoin Originals are final; all mirrors and echoes are non-amending. This Issue does not create authority, attestation, amendment, archive status, or verification-level upgrade unless the relevant machine gates pass.",
        "evidence_input_path": "/tmp/evidence.json",
        "claim_gate_output_path": "/tmp/gate.json",
        "verification_report_path": "/tmp/report.json",
        "canonical_boundary_sentence": "Bitcoin Originals are final; all mirrors and echoes are non-amending.",
        "boundary_sentence_present": True,
    }
    schema_accepts(strict_block, "clean strict V6 block")

    # --- Summary ---
    print(f"\n=== Results: {PASS} passed, {FAIL} failed ===")
    if FAIL > 0:
        return 1
    print("All negative tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
