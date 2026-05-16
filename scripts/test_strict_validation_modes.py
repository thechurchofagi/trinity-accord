#!/usr/bin/env python3
"""
Tests for strict validation modes (PR-2).
Ensures archive/ci modes fail closed, dev mode allows flexibility.
"""
import subprocess
import sys
import os
import tempfile
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = str(ROOT / "scripts" / "validate_agent_submission.py")

# Minimal valid submission for testing (matches echo-record-schema.v3.json)
MINIMAL_SUBMISSION = {
    "schema": "trinityaccord.echo.v3",
    "echo_version": "3.0",
    "record_kind": "echo_v3",
    "echo_type": "E1_recognition_echo",
    "echo": "Test echo",
    "agent_identity": {
        "name_or_model": "test",
        "system_or_provider": "test-system",
        "self_reported": True,
    },
    "context_depth": "C0_homepage_only",
    "assessment_state": "insufficient_context",
    "verification_level": "V0",
    "discovery_provenance": {
        "schema": "trinityaccord.discovery-provenance.v1",
        "source": "human_directed",
        "agency_level": "A1_human_gave_exact_url",
        "first_entry": {"url_or_path": "/verify", "entry_type": "agent_start"},
        "human_supplied_link": True,
        "other_agent_recommended": False,
        "agent_performed_independent_followup": False,
        "confidence": "medium",
    },
    "understanding_summary": "test",
    "verification_claim": "none",
    "uncertainties": [],
    "boundary_acknowledgement": {
        "bitcoin_originals_prevail": True,
        "echo_is_not_authority": True,
        "echo_is_not_verification_unless_claimed": True,
        "mirror_is_not_amendment": True,
        "homepage_only_is_insufficient_for_final_evaluation": True,
    },
    "bitcoin_originals_prevail": True,
    "not_verification_unless_claimed": True,
    "not_authority": True,
    "not_amendment": True,
    "not_endorsement": True,
    "independence_class": "human_solicited_agent_response",
    "archive_status": "test_record",
    "origin_limitations": ["test"],
    "not_authority": True,
    "not_amendment": True,
    "not_endorsement": True,
    "origin_classification": {
        "schema": "trinityaccord.origin-classification.v1",
        "discovery_class": "agent_referred",
        "invitation_scope": "verification_invited",
        "requester_class": "ai_agent",
        "performer_class": "ai_agent",
        "method_independence_class": "official_script_run",
        "attestation_authority_class": "none",
        "derived_counting_bucket": "human_directed_agent_verification",
        "counts_as_formal_independent_attestation": False,
    },
}


def run_validator(extra_args, input_data=None):
    """Run the validator with given args. Returns (returncode, stdout, stderr)."""
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(input_data or MINIMAL_SUBMISSION, f, indent=2)
        f.flush()
        tmp_path = f.name

    try:
        cmd = [sys.executable, VALIDATOR] + extra_args + [tmp_path]
        proc = subprocess.run(cmd, text=True, capture_output=True, cwd=str(ROOT))
        return proc.returncode, proc.stdout, proc.stderr
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def test_case(name, expected_pass, extra_args, input_data=None):
    """Run a single test case."""
    rc, stdout, stderr = run_validator(extra_args, input_data)
    passed = (rc == 0) == expected_pass
    status = "PASS" if passed else "FAIL"
    print(f"  {status}: {name} (rc={rc}, expected_pass={expected_pass})")
    if not passed:
        print(f"    stdout: {stdout[-500:]}")
        print(f"    stderr: {stderr[-500:]}")
    return passed


def main():
    print("=== Testing strict validation modes ===\n")
    all_passed = True

    # Test 1: --mode archive --allow-missing-jsonschema should FAIL
    all_passed &= test_case(
        "archive mode rejects --allow-missing-jsonschema",
        expected_pass=False,
        extra_args=["--mode", "archive", "--allow-missing-jsonschema"],
    )

    # Test 2: --mode ci --allow-missing-jsonschema should FAIL
    all_passed &= test_case(
        "ci mode rejects --allow-missing-jsonschema",
        expected_pass=False,
        extra_args=["--mode", "ci", "--allow-missing-jsonschema"],
    )

    # Test 3: --mode dev --allow-missing-jsonschema should work
    all_passed &= test_case(
        "dev mode allows --allow-missing-jsonschema",
        expected_pass=True,
        extra_args=["--mode", "dev", "--allow-missing-jsonschema"],
    )

    # Test 4: archive mode default (jsonschema must be available)
    all_passed &= test_case(
        "archive mode works when jsonschema is available",
        expected_pass=True,
        extra_args=["--mode", "archive"],
    )

    # Test 5: ci mode default (jsonschema must be available)
    all_passed &= test_case(
        "ci mode works when jsonschema is available",
        expected_pass=True,
        extra_args=["--mode", "ci"],
    )

    # Test 6: dev mode without --allow-missing-jsonschema (normal)
    all_passed &= test_case(
        "dev mode works normally",
        expected_pass=True,
        extra_args=["--mode", "dev"],
    )

    # Test 7: default mode (archive) works
    all_passed &= test_case(
        "default mode (archive) works",
        expected_pass=True,
        extra_args=[],
    )

    # Test 8: mode info is printed
    rc, stdout, stderr = run_validator(["--mode", "ci"])
    if "INFO: Validation mode: ci" in stdout:
        print("  PASS: mode info printed for ci")
    else:
        print(f"  FAIL: mode info not found in stdout: {stdout[:200]}")
        all_passed = False

    # Test 9: mode info for archive
    rc, stdout, stderr = run_validator(["--mode", "archive"])
    if "INFO: Validation mode: archive" in stdout:
        print("  PASS: mode info printed for archive")
    else:
        print(f"  FAIL: mode info not found in stdout: {stdout[:200]}")
        all_passed = False

    # Test 10: mode info for dev
    rc, stdout, stderr = run_validator(["--mode", "dev"])
    if "INFO: Validation mode: dev" in stdout:
        print("  PASS: mode info printed for dev")
    else:
        print(f"  FAIL: mode info not found in stdout: {stdout[:200]}")
        all_passed = False

    # Test 11: TRINITY_VALIDATION_MODE env var respected
    env = os.environ.copy()
    env["TRINITY_VALIDATION_MODE"] = "ci"
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(MINIMAL_SUBMISSION, f, indent=2)
        f.flush()
        tmp_path = f.name
    try:
        proc = subprocess.run(
            [sys.executable, VALIDATOR, tmp_path],
            text=True, capture_output=True, cwd=str(ROOT), env=env,
        )
        if "INFO: Validation mode: ci" in proc.stdout:
            print("  PASS: TRINITY_VALIDATION_MODE env var respected")
        else:
            print(f"  FAIL: env var not respected: {proc.stdout[:200]}")
            all_passed = False
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    # Test 12: validation_modes.py unit tests
    print("\n--- validation_modes.py unit tests ---")
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        import validation_modes as vm

        # Test get_validation_mode default
        os.environ.pop("TRINITY_VALIDATION_MODE", None)
        assert vm.get_validation_mode() == "archive", "default should be archive"
        print("  PASS: get_validation_mode default is archive")

        # Test get_validation_mode from env
        os.environ["TRINITY_VALIDATION_MODE"] = "dev"
        assert vm.get_validation_mode() == "dev"
        os.environ["TRINITY_VALIDATION_MODE"] = "ci"
        assert vm.get_validation_mode() == "ci"
        os.environ.pop("TRINITY_VALIDATION_MODE", None)
        print("  PASS: get_validation_mode reads env")

        # Test is_strict_mode
        assert vm.is_strict_mode("archive") is True
        assert vm.is_strict_mode("ci") is True
        assert vm.is_strict_mode("dev") is False
        print("  PASS: is_strict_mode correct")

        # Test enforce_strict_jsonschema: dev + allow_missing should work
        result = vm.enforce_strict_jsonschema("dev", allow_missing_flag=True)
        print(f"  PASS: enforce_strict_jsonschema dev+allow_missing returns {result}")

    except Exception as e:
        print(f"  FAIL: validation_modes unit tests: {e}")
        all_passed = False

    # Test 13: enforce_strict_jsonschema: archive + allow_missing should exit
    print("\n--- enforce_strict_jsonschema exit tests ---")
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        import validation_modes as vm

        # This should sys.exit(1)
        try:
            vm.enforce_strict_jsonschema("archive", allow_missing_flag=True)
            print("  FAIL: archive + allow_missing should have exited")
            all_passed = False
        except SystemExit as e:
            if e.code == 1:
                print("  PASS: archive + allow_missing raises SystemExit(1)")
            else:
                print(f"  FAIL: unexpected exit code: {e.code}")
                all_passed = False

        # ci + allow_missing should exit
        try:
            vm.enforce_strict_jsonschema("ci", allow_missing_flag=True)
            print("  FAIL: ci + allow_missing should have exited")
            all_passed = False
        except SystemExit as e:
            if e.code == 1:
                print("  PASS: ci + allow_missing raises SystemExit(1)")
            else:
                print(f"  FAIL: unexpected exit code: {e.code}")
                all_passed = False

    except Exception as e:
        print(f"  FAIL: enforce_strict_jsonschema tests: {e}")
        all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("FINAL: ALL TESTS PASSED")
        return 0
    print("FINAL: SOME TESTS FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
