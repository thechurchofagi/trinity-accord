#!/usr/bin/env python3
"""Test oath strictness consistency: schema, validator, and claim_gate all enforce 160-char readback."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "api" / "agent-issue-gateway-payload-schema.v1.json"
VALIDATOR = ROOT / "scripts" / "validate_gateway_payload.py"


def make_payload(readback_length=160):
    """Create a minimal agent-declared payload with given readback length."""
    return {
        "schema": "trinityaccord.agent-issue-gateway-payload.v1",
        "submission_type": "verification_report_candidate",
        "agent_identity": {
            "name_or_model": "Test Agent",
            "system_or_provider": "Test System",
            "self_reported": True,
        },
        "title": "Verification Report Candidate: V4 test",
        "body": "A" * 100,
        "boundary_acknowledgement": {
            "not_authority": True,
            "not_amendment": True,
            "not_attestation": True,
            "not_verification_unless_claim_gate_report_attached": True,
            "bitcoin_originals_prevail": True,
        },
        "requested_archive_kind": "agent_declared_verification_archive",
        "agent_declared_protocol_level": "V4",
        "evidence_requirement_mode": "waived_for_v0_v5",
        "record_intent": "auto_archive_candidate",
        "claim_gate": {
            "status": "PASS",
            "mode": "template_for_v0_v5",
            "allowed_protocol_level": "V4",
        },
        "agent_integrity_declaration": {
            "performed_actions_myself": True,
            "verification_oath": {
                "oath_read": True,
                "oath_version": "v1",
                "oath_text_sha256": "a" * 64,
                "readback_required": True,
                "agent_readback": "x" * readback_length,
                "understands_not_an_exam_or_performance": True,
                "will_state_actual_capability_only": True,
                "will_not_lie_or_cheat": True,
                "will_not_fabricate_verification": True,
                "will_not_present_guesses_as_facts": True,
                "will_not_copy_prior_reports_as_fresh_evidence": True,
                "will_state_uncertainty_limitations_and_downgrades": True,
            },
        },
        "discovery_provenance": {
            "source": "test",
            "independence_class": "human_solicited_agent_response",
            "agency_level": "A1_human_gave_exact_url",
        },
        "origin_classification": {"origin": "test"},
        "claim_classification": {"class": "test"},
        "authority_boundary": {
            "bitcoin_originals_remain_final": True,
            "does_not_amend_bitcoin_originals": True,
            "does_not_override_bitcoin_originals": True,
        },
        "counts_toward_home": {
            "verifiability": True,
            "reception": True,
            "basis": "test",
        },
        "what_i_checked": ["test"],
        "limitations": ["test"],
    }


def run_validator(payload_path):
    result = subprocess.run(
        ["python3", str(VALIDATOR), str(payload_path)],
        capture_output=True, text=True,
    )
    return result.returncode, result.stdout + result.stderr


def main():
    passed = 0
    failed = 0
    total = 0

    def check(label, condition, detail=""):
        nonlocal passed, failed, total
        total += 1
        if condition:
            print(f"PASS: {label}")
            passed += 1
        else:
            print(f"FAIL: {label}")
            if detail:
                print(f"  {detail}")
            failed += 1

    schema_data = json.loads(SCHEMA.read_text(encoding="utf-8"))
    schema_text = json.dumps(schema_data)

    # Test 1: Schema rejects agent_readback length 80
    # The schema has minLength: 160 on agent_readback
    oath_schema = (
        schema_data.get("properties", {})
        .get("agent_integrity_declaration", {})
        .get("properties", {})
        .get("verification_oath", {})
        .get("properties", {})
        .get("agent_readback", {})
    )
    check(
        "Schema agent_readback minLength is 160",
        oath_schema.get("minLength") == 160,
        f"minLength: {oath_schema.get('minLength')}",
    )

    # Test 2: Validator rejects agent_readback length 80
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(make_payload(80), f)
        f.flush()
        code, output = run_validator(f.name)
    check(
        "Validator rejects agent_readback length 80",
        code != 0 and "160" in output,
        f"exit={code}, output snippet: {output[:200]}",
    )

    # Test 3: Validator accepts agent_readback length 160+
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(make_payload(200), f)
        f.flush()
        code, output = run_validator(f.name)
    check(
        "Validator accepts agent_readback length 200",
        code == 0,
        f"exit={code}, output: {output[:200]}",
    )

    # Test 4: Schema verification_oath has required fields
    oath_required = (
        schema_data.get("properties", {})
        .get("agent_integrity_declaration", {})
        .get("properties", {})
        .get("verification_oath", {})
        .get("required", [])
    )
    check(
        "Schema verification_oath has required fields",
        len(oath_required) >= 10,
        f"count: {len(oath_required)}",
    )

    print(f"\n--- Results: {passed}/{total} passed, {failed} failed ---")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
