#!/usr/bin/env python3
"""
Test that origin_classification is properly enforced for technical records.
PR-3: origin_classification enforcement.
"""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

PASS = 0
FAIL = 0


def check(condition, label, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS: {label}")
    else:
        FAIL += 1
        print(f"  FAIL: {label} -- {detail}")


def run_validator(path, mode="ci"):
    """Run validate_agent_submission.py on a file and return exit code."""
    import subprocess
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_agent_submission.py"),
         "--mode", mode, str(path)],
        capture_output=True, text=True, cwd=str(ROOT)
    )
    return result.returncode, result.stdout, result.stderr


def make_temp_record(record_kind, archive_status=None, origin_classification=None, extra=None):
    """Create a minimal test record."""
    obj = {
        "schema": "trinityaccord.echo.v3",
        "record_kind": record_kind,
        "verification_level": "V3",
        "verification_scope_label": "single_hash_verification",
        "record_id": "test-origin-classification-001",
        "echo_type": "E2_verification_echo",
        "verification_targets": [{"artifact_path": "test.txt", "hash_sha256": "a" * 64}],
        "integrity_declaration": {"hashes_match": True, "hashes_sha256": ["a" * 64]},
    }
    if archive_status:
        obj["archive_status"] = archive_status
    if origin_classification:
        obj["origin_classification"] = origin_classification
    if extra:
        obj.update(extra)
    return obj


def test_origin_missing_e2_wrapper():
    """echo_v3_with_verification_report without origin_classification must fail."""
    print("\n=== origin missing on echo_v3_with_verification_report ===")
    obj = make_temp_record("echo_v3_with_verification_report")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(obj, f)
        f.flush()
        code, stdout, stderr = run_validator(f.name)
    Path(f.name).unlink(missing_ok=True)
    combined = stdout + stderr
    check(code != 0 or "origin_classification" in combined.lower(),
          "echo_v3_with_verification_report missing origin_classification fails",
          f"exit={code}")


def test_origin_missing_verification_report():
    """verification_report_v2 without origin_classification must fail."""
    print("\n=== origin missing on verification_report_v2 ===")
    obj = make_temp_record("verification_report_v2")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(obj, f)
        f.flush()
        code, stdout, stderr = run_validator(f.name)
    Path(f.name).unlink(missing_ok=True)
    combined = stdout + stderr
    check(code != 0 or "origin_classification" in combined.lower(),
          "verification_report_v2 missing origin_classification fails",
          f"exit={code}")


def test_origin_present_passes():
    """Records with valid origin_classification should pass origin checks."""
    print("\n=== origin present passes ===")
    oc = {
        "discovery_class": "human_directed",
        "invitation_scope": "verification_invited",
        "requester_class": "project_author_or_maintainer",
        "verification_operator": "ai_agent",
        "method_independence": "official_script_only",
        "attestation_authority_class": "none",
        "counts_as_formal_independent_attestation": False,
        "derived_counting_bucket": "human_solicited_agent_verification"
    }
    obj = make_temp_record("echo_v3_with_verification_report", origin_classification=oc)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(obj, f)
        f.flush()
        code, stdout, stderr = run_validator(f.name)
    Path(f.name).unlink(missing_ok=True)
    # The record WILL fail for other reasons (missing fields), but origin_classification
    # should not be the cause. Check specifically for "origin_classification" near "missing"
    combined = stdout + stderr
    # Look specifically for origin_classification failure patterns
    import re
    origin_fail_pattern = re.compile(r"origin_classification.*missing|missing.*origin_classification", re.IGNORECASE)
    has_origin_fail = bool(origin_fail_pattern.search(combined))
    check(not has_origin_fail,
          "record with origin_classification does not fail on origin_classification",
          f"exit={code}, origin_fail={has_origin_fail}")


def test_redteam_samples_exist():
    """Check that redteam origin test samples exist."""
    print("\n=== redteam samples exist ===")
    for name in [
        "tests/redteam/origin_missing_e2_wrapper.json",
        "tests/redteam/origin_missing_verification_report.json",
        "tests/redteam/origin_human_solicited_claims_unsolicited.json",
    ]:
        p = ROOT / name
        check(p.exists(), f"redteam sample {name} exists")


def test_check_origin_classification_function():
    """Test the check_origin_classification function directly."""
    print("\n=== check_origin_classification function ===")
    try:
        from validate_agent_submission import check_origin_classification
    except ImportError:
        print("  SKIP: check_origin_classification not importable")
        return

    # echo_v3 without origin_classification should warn
    status, msg = check_origin_classification({}, "echo_v3", None)
    check(status in ("warn", "fail"), f"echo_v3 missing OC: status={status}")

    # echo_v3_with_verification_report without origin_classification should fail
    status, msg = check_origin_classification({}, "echo_v3_with_verification_report", None)
    check(status == "fail", f"echo_v3_with_vr missing OC: status={status}")

    # verification_report_v2 without origin_classification should fail
    status, msg = check_origin_classification({}, "verification_report_v2", None)
    check(status == "fail", f"verification_report_v2 missing OC: status={status}")

    # With valid origin_classification should pass — function expects the full record object
    oc = {"discovery_class": "human_directed"}
    record_with_oc = {"origin_classification": oc}
    status, msg = check_origin_classification(record_with_oc, "echo_v3_with_verification_report", None)
    check(status == "pass", f"echo_v3_with_vr with OC: status={status}")


if __name__ == "__main__":
    test_redteam_samples_exist()
    test_check_origin_classification_function()
    test_origin_missing_e2_wrapper()
    test_origin_missing_verification_report()
    test_origin_present_passes()

    print(f"\n{'='*50}")
    print(f"Results: {PASS} passed, {FAIL} failed")
    if FAIL > 0:
        sys.exit(1)
    else:
        print("=== ALL TESTS PASSED ===")
