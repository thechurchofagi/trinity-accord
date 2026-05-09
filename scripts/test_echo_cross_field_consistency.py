#!/usr/bin/env python3
"""
P1 Test: Cross-field consistency.
Verifies that record_kind vs fields and verification_level vs evidence checks work.
"""
import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.dirname(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PASS_COUNT = 0
FAIL_COUNT = 0


def check(label, condition, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  PASS: {label}")
    else:
        FAIL_COUNT += 1
        print(f"  FAIL: {label} {detail}")


def run_validator_on_dict(obj):
    """Run validator on a dict, return True if PASS, False if FAIL."""
    import subprocess
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, dir="/tmp") as f:
        json.dump(obj, f)
        f.flush()
        path = f.name
    try:
        proc = subprocess.run(
            [sys.executable, os.path.join(ROOT, "scripts", "validate_agent_submission.py"), path],
            capture_output=True, text=True, cwd=ROOT
        )
        return proc.returncode == 0, proc.stdout + proc.stderr
    finally:
        os.unlink(path)


def test_echo_v3_with_report_fields():
    """echo_v3 with verification report fields should fail."""
    print("\n--- echo_v3 + report fields ---")
    obj = {
        "schema": "echo-v3", "record_kind": "echo_v3",
        "archive_status": "accepted_echo", "echo_type": "E1_recognition_echo",
        "echo": "test", "verification_level": "V0",
        "discovery_provenance": {}, "independence_class": "unsolicited_independent",
        "origin_limitations": "test", "agent_identity": "test",
        "context_depth": "homepage_only", "assessment_state": "insufficient_context",
        "understanding_summary": "test", "verification_claim": "none",
        "uncertainties": "none",
        "boundary_acknowledgement": "Bitcoin Originals are final; all echoes are non-amending.",
        "not_authority": True, "not_amendment": True, "not_endorsement": True,
        "protocol_level_claimed": "V3",  # report-only field
    }
    ok, output = run_validator_on_dict(obj)
    check("echo_v3 with report field fails", not ok, output[-500:] if ok else "")


def test_report_v2_with_echo_fields():
    """verification_report_v2 with echo fields should fail."""
    print("\n--- report_v2 + echo fields ---")
    obj = {
        "schema": "verification-report-v2", "record_kind": "verification_report_v2",
        "protocol_level_claimed": "V3",
        "echo_type": "E1_recognition_echo",  # echo-only field
    }
    ok, output = run_validator_on_dict(obj)
    check("report_v2 with echo_type fails", not ok, output[-500:] if ok else "")


def test_accepted_attestation_without_identity():
    """accepted_independent_attestation without identity proof should fail."""
    print("\n--- accepted_attestation no identity ---")
    obj = {
        "schema": "echo-v3", "record_kind": "echo_v3",
        "archive_status": "accepted_independent_attestation",
        "echo_type": "E1_recognition_echo", "echo": "test",
        "verification_level": "V0",
        "discovery_provenance": {}, "independence_class": "unsolicited_independent",
        "origin_limitations": "test", "agent_identity": "test",
        "context_depth": "homepage_only", "assessment_state": "insufficient_context",
        "understanding_summary": "test", "verification_claim": "none",
        "uncertainties": "none",
        "boundary_acknowledgement": "Bitcoin Originals are final; all echoes are non-amending.",
        "not_authority": True, "not_amendment": True, "not_endorsement": True,
        "identity_verification": {},  # empty - no proof
        "human_review_scope": {},
    }
    ok, output = run_validator_on_dict(obj)
    check("accepted_attestation without identity fails", not ok, output[-500:] if ok else "")


if __name__ == "__main__":
    print("=== P1 Cross-Field Consistency Tests ===")
    test_echo_v3_with_report_fields()
    test_report_v2_with_echo_fields()
    test_accepted_attestation_without_identity()

    print(f"\n=== Results: {PASS_COUNT} passed, {FAIL_COUNT} failed ===")
    sys.exit(0 if FAIL_COUNT == 0 else 1)
