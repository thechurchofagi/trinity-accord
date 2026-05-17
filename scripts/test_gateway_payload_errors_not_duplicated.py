#!/usr/bin/env python3
"""Test that validate_gateway_payload.py does not produce duplicate error messages."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_gateway_payload.py"


def make_broken_payload():
    """Create a payload missing multiple agent-declared fields."""
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
        # Missing: agent_integrity_declaration, discovery_provenance,
        # origin_classification, claim_classification, authority_boundary,
        # counts_toward_home
        "what_i_checked": ["test"],
        "limitations": ["test"],
        "reception_initiation_class": "self_initiated",
        "reception_initiation_basis": "agent_discovered_publicly",
        "agent_independent_followup": True,
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

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(make_broken_payload(), f)
        f.flush()
        code, output = run_validator(f.name)

    # Extract FAIL lines
    fail_lines = [line for line in output.splitlines() if line.startswith("FAIL:")]
    error_messages = [line.replace("FAIL: ", "") for line in fail_lines]

    # Test 1: Validator should fail
    check("Broken payload is rejected", code != 0)

    # Test 2: No duplicate error messages
    unique_errors = list(dict.fromkeys(error_messages))
    check(
        "No duplicate error messages",
        len(error_messages) == len(unique_errors),
        f"total={len(error_messages)}, unique={len(unique_errors)}",
    )

    # Test 3: At least 3 distinct errors found
    check(
        "At least 3 distinct errors found",
        len(unique_errors) >= 3,
        f"distinct errors: {len(unique_errors)}",
    )

    print(f"\n--- Results: {passed}/{total} passed, {failed} failed ---")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
