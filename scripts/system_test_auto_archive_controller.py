#!/usr/bin/env python3
"""System tests for auto_archive_decision.py.

Tests auto_archive_decision independently with static JSON readiness outputs.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT / "scripts" / "auto_archive_decision.py"

PASS_COUNT = 0
FAIL_COUNT = 0


def run_decision(readiness_obj):
    """Run auto_archive_decision.py with a readiness object."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, dir=str(ROOT)) as f:
        json.dump(readiness_obj, f)
        f.flush()
        path = f.name
    try:
        result = subprocess.run(
            [sys.executable, str(DECISION), "--archive-readiness", path, "--json"],
            capture_output=True, text=True, timeout=30, cwd=str(ROOT)
        )
        return json.loads(result.stdout)
    finally:
        Path(path).unlink(missing_ok=True)


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


def test_ready_sample():
    print("Test 1: ready sample archive -> labels include archive:external-agent-intake-sample")
    readiness = {
        "archive_ready": True,
        "auto_archive_allowed": True,
        "record_intent": "auto_archive_candidate",
        "requested_archive_kind": "external_agent_intake_sample",
        "allowed_archive_kind": "external_agent_intake_sample",
        "auto_archive_action": "auto_archive_sample",
        "auto_labels": ["archive:external-agent-intake-sample", "not-attestation", "not-successor-reception", "not-verified-record"],
        "auto_close_issue": True,
        "close_reason": "completed",
        "blocking_reasons": [],
        "warnings": [],
        "required_next_actions": []
    }
    decision = run_decision(readiness)
    assert_eq(decision["action"], "auto_archive_sample", "action")
    assert_in("archive:external-agent-intake-sample", decision["labels_to_add"], "sample label")
    assert_eq(decision["should_close_issue"], True, "should_close_issue")
    assert_eq(decision["should_create_issue"], True, "should_create_issue")


def test_ready_verification_report():
    print("Test 2: ready verification report -> labels include archive:verification-report and archive:ready")
    readiness = {
        "archive_ready": True,
        "auto_archive_allowed": True,
        "record_intent": "auto_archive_candidate",
        "requested_archive_kind": "verification_report_archive",
        "allowed_archive_kind": "verification_report_archive",
        "auto_archive_action": "auto_archive_verification_report",
        "auto_labels": ["archive:verification-report", "archive:ready", "not-attestation", "not-successor-reception"],
        "auto_close_issue": True,
        "close_reason": "completed",
        "blocking_reasons": [],
        "warnings": [],
        "required_next_actions": []
    }
    decision = run_decision(readiness)
    assert_eq(decision["action"], "auto_archive_verification_report", "action")
    assert_in("archive:verification-report", decision["labels_to_add"], "report label")
    assert_in("archive:ready", decision["labels_to_add"], "ready label")
    assert_eq(decision["should_close_issue"], True, "should_close_issue")


def test_ready_echo():
    print("Test 3: ready echo -> labels include archive:echo and archive:ready")
    readiness = {
        "archive_ready": True,
        "auto_archive_allowed": True,
        "record_intent": "auto_archive_candidate",
        "requested_archive_kind": "archived_echo",
        "allowed_archive_kind": "archived_echo",
        "auto_archive_action": "auto_archive_echo",
        "auto_labels": ["archive:echo", "archive:ready", "not-attestation", "not-successor-reception"],
        "auto_close_issue": True,
        "close_reason": "completed",
        "blocking_reasons": [],
        "warnings": [],
        "required_next_actions": []
    }
    decision = run_decision(readiness)
    assert_eq(decision["action"], "auto_archive_echo", "action")
    assert_in("archive:echo", decision["labels_to_add"], "echo label")
    assert_in("archive:ready", decision["labels_to_add"], "ready label")


def test_blocked_formal():
    print("Test 4: blocked formal archive -> action=block, should_create_issue=false")
    readiness = {
        "archive_ready": False,
        "auto_archive_allowed": False,
        "record_intent": "auto_archive_candidate",
        "requested_archive_kind": "verification_report_archive",
        "allowed_archive_kind": "none",
        "auto_archive_action": "block",
        "auto_labels": [],
        "auto_close_issue": False,
        "close_reason": None,
        "blocking_reasons": [{"code": "BITCOIN_LEVEL_BELOW_ARCHIVE_FLOOR", "message": "B0 < B1"}],
        "warnings": [],
        "required_next_actions": ["Raise bitcoin_originals to B1."]
    }
    decision = run_decision(readiness)
    assert_eq(decision["action"], "block", "action")
    assert_eq(decision["should_create_issue"], False, "should_create_issue")
    assert_eq(decision["labels_to_add"], [], "no labels")


def test_needs_more_evidence():
    print("Test 5: needs_more_evidence -> no archive labels")
    readiness = {
        "archive_ready": False,
        "auto_archive_allowed": False,
        "record_intent": "auto_archive_candidate",
        "requested_archive_kind": "verification_report_archive",
        "allowed_archive_kind": "none",
        "auto_archive_action": "needs_more_evidence",
        "auto_labels": [],
        "auto_close_issue": False,
        "blocking_reasons": [{"code": "ARTIFACT_BUNDLE_MISSING", "message": "Missing bundle"}],
        "warnings": [],
        "required_next_actions": ["Provide artifact bundle."]
    }
    decision = run_decision(readiness)
    assert_eq(decision["action"], "needs_more_evidence", "action")
    assert_eq(decision["labels_to_add"], [], "no labels")


def test_successor_blocked():
    print("Test 6: successor_reception blocked -> no successor labels")
    readiness = {
        "archive_ready": False,
        "auto_archive_allowed": False,
        "record_intent": "auto_archive_candidate",
        "requested_archive_kind": "successor_reception_candidate",
        "allowed_archive_kind": "none",
        "auto_archive_action": "block",
        "auto_labels": [],
        "auto_close_issue": False,
        "blocking_reasons": [{"code": "SUCCESSOR_RECEPTION_NOT_GATEWAY_CLAIMABLE", "message": "Blocked"}],
        "warnings": [],
        "required_next_actions": []
    }
    decision = run_decision(readiness)
    assert_eq(decision["action"], "block", "action")
    assert_eq(decision["should_create_issue"], False, "should_create_issue")
    assert_not_in("successor-reception", decision["labels_to_add"], "no successor label")


def test_intake_only():
    print("Test 7: intake_only -> action=none, should_create_issue=true")
    readiness = {
        "archive_ready": False,
        "auto_archive_allowed": False,
        "record_intent": "intake_only",
        "requested_archive_kind": "none",
        "allowed_archive_kind": "none",
        "auto_archive_action": "none",
        "auto_labels": [],
        "auto_close_issue": False,
        "blocking_reasons": [],
        "warnings": [{"code": "INTAKE_ONLY_NOT_ARCHIVE"}],
        "required_next_actions": []
    }
    decision = run_decision(readiness)
    assert_eq(decision["action"], "none", "action")
    assert_eq(decision["should_create_issue"], True, "should_create_issue")


def main():
    test_ready_sample()
    test_ready_verification_report()
    test_ready_echo()
    test_blocked_formal()
    test_needs_more_evidence()
    test_successor_blocked()
    test_intake_only()

    print(f"\nResults: {PASS_COUNT} passed, {FAIL_COUNT} failed")
    if FAIL_COUNT > 0:
        print("AUTO ARCHIVE CONTROLLER TESTS: SOME FAILED")
        sys.exit(1)
    print("AUTO ARCHIVE CONTROLLER TESTS: ALL PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
