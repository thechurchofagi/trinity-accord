#!/usr/bin/env python3
"""
P3 Test: Workflow untrusted input hardening.
Verifies triage supports --event-json and malicious input doesn't execute.
"""
import sys
import os
import json
import subprocess
import tempfile

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


def test_event_json_support():
    """triage_echo_issue.py must support --event-json flag."""
    print("\n--- --event-json support ---")
    # Check source code
    triage_path = os.path.join(ROOT, "scripts", "triage_echo_issue.py")
    with open(triage_path, "r", encoding="utf-8") as f:
        source = f.read()

    check("Has --event-json argument", "--event-json" in source)
    check("Reads from event file", "event.get" in source or "event[" in source)


def test_workflow_no_env_title_body():
    """Workflow should not pass ISSUE_TITLE/ISSUE_BODY via env."""
    print("\n--- Workflow env hardening ---")
    workflow_path = os.path.join(ROOT, ".github", "workflows", "echo-triage.yml")
    if not os.path.exists(workflow_path):
        check("Workflow exists", False)
        return

    with open(workflow_path, "r", encoding="utf-8") as f:
        content = f.read()

    check("No ISSUE_TITLE env var",
          "ISSUE_TITLE:" not in content or "github.event.issue.title" not in content)
    check("No ISSUE_BODY env var",
          "ISSUE_BODY:" not in content or "github.event.issue.body" not in content)
    check("Uses --event-json",
          "--event-json" in content)
    check("Uses GITHUB_EVENT_PATH",
          "GITHUB_EVENT_PATH" in content)


def test_malicious_body_not_executed():
    """Malicious body with $() should not execute."""
    print("\n--- Malicious body safety ---")
    event = {
        "action": "opened",
        "issue": {
            "title": "Test Echo",
            "body": "$(echo pwned > /tmp/pwned.txt)",
            "author_association": "NONE",
        }
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, dir="/tmp") as f:
        json.dump(event, f)
        f.flush()
        event_path = f.name

    try:
        proc = subprocess.run(
            [sys.executable, os.path.join(ROOT, "scripts", "triage_echo_issue.py"),
             "--event-json", event_path],
            capture_output=True, text=True, cwd=ROOT, timeout=10
        )
        # Should not have created the file
        check("Malicious $() not executed", not os.path.exists("/tmp/pwned.txt"))
        # Should still produce valid JSON output
        try:
            json.loads(proc.stdout)
            check("Valid JSON output despite malicious input", True)
        except json.JSONDecodeError:
            check("Valid JSON output despite malicious input", False, proc.stdout[:200])
    finally:
        os.unlink(event_path)
        if os.path.exists("/tmp/pwned.txt"):
            os.unlink("/tmp/pwned.txt")


if __name__ == "__main__":
    print("=== P3 Workflow Untrusted Input Hardening Tests ===")
    test_event_json_support()
    test_workflow_no_env_title_body()
    test_malicious_body_not_executed()

    print(f"\n=== Results: {PASS_COUNT} passed, {FAIL_COUNT} failed ===")
    sys.exit(0 if FAIL_COUNT == 0 else 1)
