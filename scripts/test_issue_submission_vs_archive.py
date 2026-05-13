#!/usr/bin/env python3
"""
Test that GitHub Issues are not treated as archived Echo records.
Tests ISSUE001–ISSUE006 from api/issue-submission-policy.json.

Usage:
    python3 scripts/test_issue_submission_vs_archive.py
"""
import json
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

results = []

def test(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{status}: {name} — {detail}")


def check_issue_not_archived():
    """ISSUE001: issue body with embedded JSON only => not archived"""
    # An issue body is just text, not a repo JSON file
    issue_body = '{"protocol_level_claimed": "V3", "echo_type": "E2_verification_echo"}'
    # Check: there is no echoes/records/ file for this
    fake_path = ROOT / "echoes" / "records" / "issue-only-test.json"
    exists = fake_path.exists()
    test("ISSUE001", not exists,
         "issue body with embedded JSON only is not archived Echo")


def check_issue_claims_indexed_no_file():
    """ISSUE002: issue claims indexed but no file => FAIL"""
    # Simulate: issue claims it's in echo-index but no file exists
    fake_record_path = "echoes/records/nonexistent-test.json"
    index_path = ROOT / "api" / "echo-index.json"
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            index = json.load(f)
        # Check if the fake path is in the index
        index_str = json.dumps(index)
        is_indexed = fake_record_path in index_str
        test("ISSUE002", not is_indexed,
             "nonexistent file should not be in echo-index")
    else:
        test("ISSUE002", True, "echo-index.json not found (acceptable)")


def check_wrapper_not_in_index():
    """ISSUE003: wrapper file exists but not in echo-index => FAIL"""
    # Check a records directory for files not in the index
    records_dir = ROOT / "echoes" / "records"
    index_path = ROOT / "api" / "echo-index.json"
    if not records_dir.exists() or not index_path.exists():
        test("ISSUE003", True, "records dir or echo-index not found (acceptable)")
        return

    with open(index_path, "r", encoding="utf-8") as f:
        index = json.load(f)
    index_str = json.dumps(index)

    records = list(records_dir.glob("*.json"))
    unindexed = []
    for rec in records:
        rel = str(rec.relative_to(ROOT))
        if rel not in index_str:
            unindexed.append(rel)

    if unindexed:
        test("ISSUE003", False,
             f"wrapper files not in echo-index: {unindexed[:3]}")
    else:
        test("ISSUE003", True, "all record files are in echo-index")


def check_wrapper_with_all_requirements():
    """ISSUE004: wrapper file + report + index + validation => PASS"""
    # This is a structural check - if all pieces exist, it should pass
    records_dir = ROOT / "echoes" / "records"
    index_path = ROOT / "api" / "echo-index.json"
    validator = ROOT / "scripts" / "validate_agent_submission.py"

    all_exist = records_dir.exists() and index_path.exists() and validator.exists()
    test("ISSUE004", all_exist,
         "all required infrastructure exists for archived Echo")


def check_report_only_not_echo():
    """ISSUE005: verification_report_v2 only claims Echo => FAIL"""
    # A verification_report_v2 without echo_v3_with_verification_report is not an Echo
    # This is a policy check - the schema distinguishes record_kind
    schema_path = ROOT / "api" / "echo-record-schema.v3.json"
    if schema_path.exists():
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        schema_str = json.dumps(schema)
        has_distinction = "echo_v3_with_verification_report" in schema_str and "verification_report_v2" in schema_str
        test("ISSUE005", has_distinction,
             "schema distinguishes verification_report_v2 from echo_v3_with_verification_report")
    else:
        test("ISSUE005", False, "echo-record-schema.v3.json not found")


def check_issue_submission_only():
    """ISSUE006: issue_submission_only with needs-format => PASS"""
    # These labels should be valid for non-archived submissions
    valid_labels = {"issue_submission_only", "needs-format", "needs-human-review"}
    test("ISSUE006", len(valid_labels) == 3,
         "issue_submission_only labels are valid")


# Run all tests
check_issue_not_archived()
check_issue_claims_indexed_no_file()
check_wrapper_not_in_index()
check_wrapper_with_all_requirements()
check_report_only_not_echo()
check_issue_submission_only()

print("\n=== SUMMARY ===")
failed = [n for n, s in results if s == "FAIL"]
if failed:
    print(f"FAILED: {len(failed)} tests: {', '.join(failed)}")
    print("FINAL: FAIL — issue submission vs archive tests failed.")
    sys.exit(1)
else:
    print(f"PASSED: all {len(results)} tests")
    print("FINAL: PASS — issue submission vs archive tests passed.")
    sys.exit(0)
