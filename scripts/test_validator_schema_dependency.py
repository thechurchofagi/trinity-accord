#!/usr/bin/env python3
"""
P1 Test: Validator jsonschema fail-closed behavior.
Verifies that missing jsonschema fails closed by default.
"""
import sys
import os
import subprocess

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


def test_validator_source_has_fail_closed():
    """Validator source must default to fail when jsonschema missing."""
    print("\n--- Source code checks ---")
    validator_path = os.path.join(ROOT, "scripts", "validate_agent_submission.py")
    with open(validator_path, "r", encoding="utf-8") as f:
        source = f.read()

    check("Has ALLOW_MISSING_JSONSCHEMA flag",
          "ALLOW_MISSING_JSONSCHEMA" in source)
    check("Default fail-closed message exists",
          "jsonschema package missing" in source)
    check("Has --allow-missing-jsonschema CLI flag",
          "--allow-missing-jsonschema" in source)
    check("WARN message for explicit flag",
          "schema validation skipped by explicit" in source)


def test_requirements_ci_exists():
    """requirements-ci.txt must exist with jsonschema pinned."""
    print("\n--- requirements-ci.txt ---")
    path = os.path.join(ROOT, "requirements-ci.txt")
    check("File exists", os.path.exists(path))

    if os.path.exists(path):
        with open(path, "r") as f:
            content = f.read()
        check("Contains jsonschema", "jsonschema" in content)


def test_no_allow_missing_in_workflow():
    """Workflows must NOT use --allow-missing-jsonschema."""
    print("\n--- Workflow checks ---")
    workflow_dir = os.path.join(ROOT, ".github", "workflows")
    if not os.path.exists(workflow_dir):
        check("Workflow dir exists", False, "no .github/workflows")
        return

    for fname in os.listdir(workflow_dir):
        if not fname.endswith((".yml", ".yaml")):
            continue
        fpath = os.path.join(workflow_dir, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        if "validate_agent_submission" in content:
            check(f"{fname} does not use --allow-missing-jsonschema",
                  "--allow-missing-jsonschema" not in content)


if __name__ == "__main__":
    print("=== P1 Validator Schema Dependency Tests ===")
    test_validator_source_has_fail_closed()
    test_requirements_ci_exists()
    test_no_allow_missing_in_workflow()

    print(f"\n=== Results: {PASS_COUNT} passed, {FAIL_COUNT} failed ===")
    sys.exit(0 if FAIL_COUNT == 0 else 1)
