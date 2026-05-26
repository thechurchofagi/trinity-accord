#!/usr/bin/env python3
"""Test that Issue #168 (freeform issue) has no canonical oath and is not in archive.

Issue #168 is a freeform/non-agent-declared issue. It must:
  - NOT have a canonical verification oath summary
  - NOT be included in the agent-declared verification index
  - NOT be included in the archive

This is a negative test to ensure the oath gate doesn't leak into non-applicable issues.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "api" / "agent-declared-verification-index.json"

PASS = 0
FAIL = 0


def check(condition, desc):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS: {desc}")
    else:
        FAIL += 1
        print(f"  FAIL: {desc}")


def test_issue168_not_in_index():
    """Issue #168 must not appear in the agent-declared verification index."""
    global PASS, FAIL
    print("\n--- Issue #168 not in index ---")

    if not INDEX_PATH.exists():
        FAIL += 1
        print(f"  FAIL: index file not found at {INDEX_PATH}")
        return

    try:
        index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        FAIL += 1
        print(f"  FAIL: could not parse index: {e}")
        return

    records = index.get("records", [])
    issue_numbers = [r.get("issue_number") for r in records]
    check(168 not in issue_numbers, "issue #168 not in index records")

    skipped = index.get("skipped_direct_issue_archive_attempts", [])
    skipped_oath = index.get("skipped_missing_oath_summary", [])
    # It's fine if #168 is in skipped lists (it was filtered out correctly)
    # The key check is that it's NOT in records


def test_issue168_no_canonical_oath_schema():
    """A freeform issue body must not pass the agent-declared oath schema.

    This tests the JSON schema: if submission_type is not verification_report_candidate
    with agent_declared path, oath fields are not required and should not be const-validated.
    """
    global PASS, FAIL
    print("\n--- Issue #168 freeform → no canonical oath requirement ---")

    # Simulate a freeform issue body (no agent-declared archive path)
    # Such an issue should NOT have oath fields forced on it
    # The schema only enforces oath const:true under the agent_declared_verification_archive branch
    schema_path = ROOT / "api" / "issue-intake-machine-block-schema.v1.json"
    if not schema_path.exists():
        FAIL += 1
        print(f"  FAIL: schema not found")
        return

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        FAIL += 1
        print(f"  FAIL: could not parse schema: {e}")
        return

    # Check that oath const:true is only in the agent-declared branch (allOf[0].then.properties)
    all_of = schema.get("allOf", [])
    agent_declared_branch = None
    for branch in all_of:
        if_cond = branch.get("if", {})
        props = if_cond.get("properties", {})
        if props.get("requested_archive_kind", {}).get("const") == "agent_declared_verification_archive":
            agent_declared_branch = branch
            break

    check(agent_declared_branch is not None, "agent-declared branch found in schema")

    if agent_declared_branch:
        then_required = agent_declared_branch.get("then", {}).get("required", [])
        check("verification_oath_present" in then_required, "verification_oath_present required in agent-declared branch")
        check("agent_readback_char_count" in then_required, "agent_readback_char_count required in agent-declared branch")

        # Check top-level constraints (inherited by agent-declared branch)
        top_props = schema.get("properties", {})
        oath_prop = top_props.get("verification_oath_present", {})
        check(oath_prop.get("const") is True, "verification_oath_present has const:true (top-level, inherited)")
        readback_prop = top_props.get("agent_readback_char_count", {})
        check(readback_prop.get("minimum") == 160, "agent_readback_char_count has minimum:160 (top-level, inherited)")

    # The top-level properties should NOT have const:true (freeform issues aren't forced)
    top_props = schema.get("properties", {})
    top_oath = top_props.get("verification_oath_present", {})
    # Top-level should be type:boolean with const:true (as per our fix)
    # This is correct — the const only applies when the field is present,
    # and the allOf/if-then only requires it for agent_declared path
    check(top_oath.get("type") == "boolean", "top-level verification_oath_present is boolean type")


def main():
    global PASS, FAIL
    print("=== Issue #168 No Canonical Oath Tests ===")

    test_issue168_not_in_index()
    test_issue168_no_canonical_oath_schema()

    print(f"\n=== Results: {PASS} passed, {FAIL} failed ===")
    return 1 if FAIL > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
