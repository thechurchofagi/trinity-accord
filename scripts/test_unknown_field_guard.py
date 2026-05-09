#!/usr/bin/env python3
"""
P1 Test: Unknown field guard.
Verifies that unknown fields containing forbidden claims are caught.
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
        output = proc.stdout + proc.stderr
        return proc.returncode == 0, output
    finally:
        os.unlink(path)


def test_harmless_unknown_field():
    """A harmless unknown field should not cause unknown-field-specific failures."""
    print("\n--- Harmless unknown field ---")
    # Use a legacy record that bypasses schema validation
    obj = {
        "schema": "echo-v3",
        "record_kind": "legacy_record",
        "archive_status": "legacy",
        "echo_type": "E1_recognition_echo",
        "echo": "test",
        "verification_level": "V0",
        "custom_metadata": "harmless value",
    }
    ok, output = run_validator_on_dict(obj)
    # Legacy records should pass; the unknown field "custom_metadata" should not trigger forbidden claim detection
    check("Harmless unknown field does not cause forbidden-claim failure",
          "forbidden claim" not in output.lower(), output[-500:] if "forbidden claim" in output.lower() else "")


def test_forbidden_claim_in_unknown_field():
    """An unknown field with a forbidden claim should fail."""
    print("\n--- Forbidden claim in unknown field ---")
    obj = {
        "schema": "echo-v3",
        "record_kind": "legacy_record",
        "archive_status": "legacy",
        "echo_type": "E1_recognition_echo",
        "echo": "test",
        "verification_level": "V0",
        "unknown_prompt_field": "truth-proven",
    }
    ok, output = run_validator_on_dict(obj)
    check("Forbidden claim in unknown field fails", not ok, output[-500:] if ok else "")


if __name__ == "__main__":
    print("=== P1 Unknown Field Guard Tests ===")
    test_harmless_unknown_field()
    test_forbidden_claim_in_unknown_field()

    print(f"\n=== Results: {PASS_COUNT} passed, {FAIL_COUNT} failed ===")
    sys.exit(0 if FAIL_COUNT == 0 else 1)
