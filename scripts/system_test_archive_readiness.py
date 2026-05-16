#!/usr/bin/env python3
"""System tests for archive_readiness_gate.py.

Loads each archive fixture, runs the gate, and asserts expected outcomes.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "archive_readiness_gate.py"
FIXTURES = ROOT / "tests" / "fixtures" / "archive-readiness"

PASS_COUNT = 0
FAIL_COUNT = 0


def run_gate(fixture_name, evidence_name=None, cg_name=None, report_name=None):
    """Run archive_readiness_gate.py on a fixture and return (exit_code, output)."""
    fixture_path = FIXTURES / fixture_name
    args = [sys.executable, str(GATE), "--gateway-payload", str(fixture_path), "--json"]
    if evidence_name:
        args.extend(["--evidence-input", str(FIXTURES / evidence_name)])
    if cg_name:
        args.extend(["--claim-gate-output", str(FIXTURES / cg_name)])
    if report_name:
        args.extend(["--verification-report", str(FIXTURES / report_name)])
    result = subprocess.run(
        args, capture_output=True, text=True, timeout=30, cwd=str(ROOT)
    )
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        output = {"parse_error": True, "stdout": result.stdout, "stderr": result.stderr}
    return result.returncode, output


def assert_eq(actual, expected, label):
    global PASS_COUNT, FAIL_COUNT
    if actual == expected:
        PASS_COUNT += 1
    else:
        FAIL_COUNT += 1
        print(f"  FAIL: {label}: expected {expected!r}, got {actual!r}")


def assert_in(item, collection, label):
    global PASS_COUNT, FAIL_COUNT
    if item in collection:
        PASS_COUNT += 1
    else:
        FAIL_COUNT += 1
        print(f"  FAIL: {label}: {item!r} not in {collection!r}")


def assert_not_in(item, collection, label):
    global PASS_COUNT, FAIL_COUNT
    if item not in collection:
        PASS_COUNT += 1
    else:
        FAIL_COUNT += 1
        print(f"  FAIL: {label}: {item!r} should not be in {collection!r}")


def assert_true(value, label):
    global PASS_COUNT, FAIL_COUNT
    if value:
        PASS_COUNT += 1
    else:
        FAIL_COUNT += 1
        print(f"  FAIL: {label}: expected truthy, got {value!r}")


def test_intake_only():
    print("Test 1: intake_only V4/B0-D2")
    code, out = run_gate("issue154_like_v4_b0_d2_intake.json")
    assert_eq(code, 0, "exit code")
    assert_eq(out.get("archive_ready"), False, "archive_ready")
    assert_eq(out.get("auto_archive_action"), "none", "auto_archive_action")
    assert_eq(out.get("record_intent"), "intake_only", "record_intent")


def test_archive_request_blocked():
    print("Test 2: verification_report_archive V4/B0-D2 blocked")
    code, out = run_gate("issue154_like_v4_b0_d2_archive_request.json")
    assert_eq(code, 1, "exit code")
    assert_eq(out.get("archive_ready"), False, "archive_ready")
    assert_eq(out.get("auto_archive_action"), "block", "auto_archive_action")
    blocking_codes = [br.get("code") for br in out.get("blocking_reasons", [])]
    assert_in("BITCOIN_LEVEL_BELOW_ARCHIVE_FLOOR", blocking_codes, "blocking reason")


def test_external_sample_ready():
    print("Test 3: external_agent_intake_sample B0 ready")
    code, out = run_gate("external_agent_sample_b0_ready.json")
    assert_eq(code, 0, "exit code")
    assert_eq(out.get("archive_ready"), True, "archive_ready")
    assert_eq(out.get("auto_archive_action"), "auto_archive_sample", "auto_archive_action")


def test_verification_report_ready():
    print("Test 4: verification_report_archive B1-D2 ready")
    code, out = run_gate("verification_report_archive_b1_d2_ready.json",
                         evidence_name="evidence_v4_complete.json")
    assert_eq(code, 0, "exit code")
    assert_eq(out.get("archive_ready"), True, "archive_ready")
    assert_eq(out.get("auto_archive_action"), "auto_archive_verification_report", "auto_archive_action")


def test_missing_artifacts():
    print("Test 5: verification_report_archive missing artifacts")
    code, out = run_gate("verification_report_archive_missing_artifacts.json")
    assert_eq(code, 1, "exit code")
    assert_eq(out.get("archive_ready"), False, "archive_ready")
    blocking_codes = [br.get("code") for br in out.get("blocking_reasons", [])]
    assert_in("ARTIFACT_BUNDLE_MISSING", blocking_codes, "blocking reason")


def test_unsolicited_no_proof():
    print("Test 6: unsolicited discovery without proof")
    code, out = run_gate("verification_report_archive_unsolicited_no_proof.json")
    assert_eq(code, 1, "exit code")
    assert_eq(out.get("archive_ready"), False, "archive_ready")
    blocking_codes = [br.get("code") for br in out.get("blocking_reasons", [])]
    assert_in("UNSOLICITED_PROOF_NOT_REVIEWABLE", blocking_codes, "blocking reason")


def test_echo_ready():
    print("Test 7: archived_echo ready")
    code, out = run_gate("archived_echo_ready.json")
    assert_eq(code, 0, "exit code")
    assert_eq(out.get("archive_ready"), True, "archive_ready")
    assert_eq(out.get("auto_archive_action"), "auto_archive_echo", "auto_archive_action")


def test_echo_on_report_candidate():
    print("Test 8: archived_echo on report candidate blocked")
    code, out = run_gate("archived_echo_on_report_candidate_blocked.json")
    assert_eq(code, 1, "exit code")
    assert_eq(out.get("archive_ready"), False, "archive_ready")
    blocking_codes = [br.get("code") for br in out.get("blocking_reasons", [])]
    assert_in("WRONG_SUBMISSION_TYPE", blocking_codes, "blocking reason")


def test_echo_missing_wrapper():
    print("Test 9: archived_echo missing wrapper")
    code, out = run_gate("archived_echo_missing_wrapper.json")
    assert_eq(code, 1, "exit code")
    assert_eq(out.get("archive_ready"), False, "archive_ready")
    blocking_codes = [br.get("code") for br in out.get("blocking_reasons", [])]
    assert_in("ECHO_WRAPPER_REQUIRED", blocking_codes, "blocking reason")


def test_successor_reception():
    print("Test 10: successor_reception_candidate always blocked")
    code, out = run_gate("successor_reception_candidate_blocked.json")
    assert_eq(code, 1, "exit code")
    assert_eq(out.get("archive_ready"), False, "archive_ready")
    assert_eq(out.get("auto_archive_action"), "block", "auto_archive_action")
    blocking_codes = [br.get("code") for br in out.get("blocking_reasons", [])]
    assert_in("SUCCESSOR_RECEPTION_NOT_GATEWAY_CLAIMABLE", blocking_codes, "blocking reason")


def test_v4_missing_scripts():
    print("Test 11: V4 archive missing required scripts")
    code, out = run_gate("v4_archive_missing_required_scripts.json")
    assert_eq(code, 1, "exit code")
    assert_eq(out.get("archive_ready"), False, "archive_ready")
    blocking_codes = [br.get("code") for br in out.get("blocking_reasons", [])]
    assert_true(
        "V4_REQUIRED_SCRIPT_SET_INCOMPLETE" in blocking_codes or
        "V4_EVIDENCE_REQUIRED_FOR_ARCHIVE" in blocking_codes,
        "blocking reason (V4_REQUIRED_SCRIPT_SET_INCOMPLETE or V4_EVIDENCE_REQUIRED_FOR_ARCHIVE)"
    )


def test_v4plus_official_only():
    print("Test 12: V4+ official-only blocked")
    code, out = run_gate("v4plus_official_only_blocked.json")
    assert_eq(code, 1, "exit code")
    assert_eq(out.get("archive_ready"), False, "archive_ready")
    blocking_codes = [br.get("code") for br in out.get("blocking_reasons", [])]
    assert_true(
        "V4PLUS_REQUIRES_INDEPENDENT_NON_OFFICIAL_IMPLEMENTATION" in blocking_codes or
        "V4PLUS_EVIDENCE_REQUIRED_FOR_ARCHIVE" in blocking_codes,
        "blocking reason (V4PLUS_REQUIRES_INDEPENDENT_NON_OFFICIAL_IMPLEMENTATION or V4PLUS_EVIDENCE_REQUIRED_FOR_ARCHIVE)"
    )


def test_b6_explorer():
    print("Test 13: B6 from external_explorer blocked")
    code, out = run_gate("external_explorer_b6_archive_blocked.json",
                         evidence_name="evidence_b6_explorer.json")
    assert_eq(code, 1, "exit code")
    assert_eq(out.get("archive_ready"), False, "archive_ready")
    blocking_codes = [br.get("code") for br in out.get("blocking_reasons", [])]
    assert_true(
        "B6_REQUIRES_BODY_HASH_EVIDENCE" in blocking_codes or
        "BITCOIN_LEVEL_BELOW_ARCHIVE_FLOOR" in blocking_codes,
        "blocking reason (B6_REQUIRES_BODY_HASH_EVIDENCE or BITCOIN_LEVEL_BELOW_ARCHIVE_FLOOR)"
    )


def test_decision_no_human_review():
    print("Test 14: auto_archive_decision never returns needs-human-review")
    # Run auto_archive_decision on a ready fixture
    gate_result = subprocess.run(
        [sys.executable, str(GATE), "--gateway-payload",
         str(FIXTURES / "external_agent_sample_b0_ready.json"), "--json"],
        capture_output=True, text=True, timeout=30, cwd=str(ROOT)
    )
    readiness = json.loads(gate_result.stdout)
    readiness_path = ROOT / "tests" / "fixtures" / "archive-readiness" / "_tmp_readiness.json"
    readiness_path.write_text(json.dumps(readiness))

    decision_result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "auto_archive_decision.py"),
         "--archive-readiness", str(readiness_path), "--json"],
        capture_output=True, text=True, timeout=30, cwd=str(ROOT)
    )
    decision = json.loads(decision_result.stdout)
    assert_true("needs-human-review" not in json.dumps(decision), "no needs-human-review")
    assert_not_in("successor-reception", decision.get("labels_to_add", []), "no successor-reception labels")
    assert_not_in("independent-attestation", decision.get("labels_to_add", []), "no independent-attestation labels")

    # Cleanup
    readiness_path.unlink(missing_ok=True)


def test_decision_labels():
    print("Test 15: auto_archive_decision labels correct")
    gate_result = subprocess.run(
        [sys.executable, str(GATE), "--gateway-payload",
         str(FIXTURES / "verification_report_archive_b1_d2_ready.json"),
         "--evidence-input", str(FIXTURES / "evidence_v4_complete.json"),
         "--json"],
        capture_output=True, text=True, timeout=30, cwd=str(ROOT)
    )
    readiness = json.loads(gate_result.stdout)
    readiness_path = ROOT / "tests" / "fixtures" / "archive-readiness" / "_tmp_readiness.json"
    readiness_path.write_text(json.dumps(readiness))

    decision_result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "auto_archive_decision.py"),
         "--archive-readiness", str(readiness_path), "--json"],
        capture_output=True, text=True, timeout=30, cwd=str(ROOT)
    )
    decision = json.loads(decision_result.stdout)
    assert_in("archive:verification-report", decision.get("labels_to_add", []), "verification-report label")
    assert_in("archive:ready", decision.get("labels_to_add", []), "ready label")
    assert_eq(decision.get("should_close_issue"), True, "should_close_issue")

    readiness_path.unlink(missing_ok=True)


def main():
    test_intake_only()
    test_archive_request_blocked()
    test_external_sample_ready()
    test_verification_report_ready()
    test_missing_artifacts()
    test_unsolicited_no_proof()
    test_echo_ready()
    test_echo_on_report_candidate()
    test_echo_missing_wrapper()
    test_successor_reception()
    test_v4_missing_scripts()
    test_v4plus_official_only()
    test_b6_explorer()
    test_decision_no_human_review()
    test_decision_labels()

    print(f"\nResults: {PASS_COUNT} passed, {FAIL_COUNT} failed")
    if FAIL_COUNT > 0:
        print("ARCHIVE READINESS TESTS: SOME FAILED")
        sys.exit(1)
    print("ARCHIVE READINESS TESTS: ALL PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
