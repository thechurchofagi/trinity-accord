#!/usr/bin/env python3
"""Test agent-declared index builder extracts reception_initiation_class correctly.

Tests:
  - Issue with class externally_requested → index record class externally_requested
  - Issue with class externally_seeded → index record class externally_seeded
  - Issue missing class → index record class unknown
  - No name/provider inference happens
  - Explicit test_record still excluded unless include_test
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_agent_declared_verification_index_from_issues import build_index, parse_intake_block

PASS = 0
FAIL = 0


def make_issue(number, body, labels=None):
    return {
        "number": number,
        "url": f"https://github.com/test/repo/issues/{number}",
        "body": body,
        "createdAt": "2026-05-17T00:00:00Z",
        "labels": [{"name": l} for l in (labels or [])],
    }


AGENT_DECLARED_BLOCK = """```trinity-issue-intake
submission_type: verification_report_candidate
record_intent: auto_archive_candidate
requested_archive_kind: agent_declared_verification_archive
agent_declared_protocol_level: V4
evidence_requirement_mode: waived_for_v0_v5
claim_gate_mode: template_for_v0_v5
claim_gate_status: PASS
agent_name_or_model: TestAgent
system_or_provider: TestProvider
counts_toward_home_verifiability: true
counts_toward_home_reception: true
archive_ready: true
allowed_archive_kind: agent_declared_verification_archive
auto_archive_action: auto_archive_agent_declared_verification
canonical_boundary_sentence: Bitcoin Originals are final; all mirrors and echoes are non-amending.
boundary_sentence_present: true
```"""


def make_block(init_class, basis=None, followup=None):
    """Build an issue body with a given initiation class."""
    lines = AGENT_DECLARED_BLOCK.rstrip().rstrip("`").split("\n")
    # Insert before the closing ```
    insert_idx = len(lines) - 1
    lines.insert(insert_idx, f"reception_initiation_class: {init_class}")
    if basis:
        lines.insert(insert_idx + 1, f"reception_initiation_basis: {basis}")
    if followup is not None:
        lines.insert(insert_idx + 2, f"agent_independent_followup: {'true' if followup else 'false'}")
    lines.append("```")
    return "Test issue\n\n" + "\n".join(lines)


def test_record_has_class(issues, expected_class, include_test=False):
    global PASS, FAIL
    index = build_index(issues, repo="test/repo", include_test=include_test)
    records = index["records"]
    if not records:
        FAIL += 1
        print(f"  FAIL: no records found, expected {expected_class}")
        return
    actual = records[0].get("reception_initiation_class")
    if actual == expected_class:
        PASS += 1
        print(f"  PASS: record has reception_initiation_class={actual}")
    else:
        FAIL += 1
        print(f"  FAIL: expected {expected_class}, got {actual}")


def test_no_records(issues, include_test=False):
    global PASS, FAIL
    index = build_index(issues, repo="test/repo", include_test=include_test)
    if not index["records"]:
        PASS += 1
        print(f"  PASS: no records (as expected)")
    else:
        FAIL += 1
        print(f"  FAIL: found {len(index['records'])} records, expected 0")


def test_breakdown_sum(issues):
    global PASS, FAIL
    index = build_index(issues, repo="test/repo", include_test=True)
    records = index["records"]
    INIT_CLASSES = ["externally_requested", "externally_seeded", "self_initiated",
                    "agent_referred", "system_scheduled", "unknown"]
    by_class = {k: sum(1 for r in records if r.get("reception_initiation_class") == k) for k in INIT_CLASSES}
    total = sum(by_class.values())
    if total == len(records):
        PASS += 1
        print(f"  PASS: breakdown sum ({total}) == record count ({len(records)})")
    else:
        FAIL += 1
        print(f"  FAIL: breakdown sum ({total}) != record count ({len(records)})")


def main():
    global PASS, FAIL
    print("=== Agent-Declared Index Initiation Breakdown Tests ===\n")

    # Test 1: externally_requested
    print("--- externally_requested ---")
    issues = [make_issue(1, make_block("externally_requested", "explicit_verification_request"))]
    test_record_has_class(issues, "externally_requested")

    # Test 2: externally_seeded
    print("--- externally_seeded ---")
    issues = [make_issue(2, make_block("externally_seeded", "external_url_only", True))]
    test_record_has_class(issues, "externally_seeded")

    # Test 3: missing class → unknown
    print("--- missing class ---")
    body_no_class = AGENT_DECLARED_BLOCK + "\n"
    issues = [make_issue(3, body_no_class)]
    test_record_has_class(issues, "unknown")

    # Test 4: self_initiated
    print("--- self_initiated ---")
    issues = [make_issue(4, make_block("self_initiated", "agent_discovered_publicly"))]
    test_record_has_class(issues, "self_initiated")

    # Test 5: test_record label excluded
    print("--- test_record label excluded ---")
    issues = [make_issue(5, make_block("externally_seeded"), labels=["test-record"])]
    test_no_records(issues, include_test=False)

    # Test 6: test_record label included with flag
    print("--- test_record label included ---")
    issues = [make_issue(5, make_block("externally_seeded"), labels=["test-record"])]
    test_record_has_class(issues, "externally_seeded", include_test=True)

    # Test 7: no name/provider inference
    print("--- no name inference ---")
    body_smoke = make_block("self_initiated").replace("TestAgent", "Smoke Agent").replace("TestProvider", "Local Test")
    issues = [make_issue(6, body_smoke)]
    test_record_has_class(issues, "self_initiated")  # should be self_initiated, not guessed as test

    # Test 8: breakdown sum
    print("--- breakdown sum ---")
    all_issues = [
        make_issue(10, make_block("externally_requested")),
        make_issue(11, make_block("externally_seeded")),
        make_issue(12, make_block("self_initiated")),
        make_issue(13, make_block("unknown")),
        make_issue(14, make_block("externally_seeded")),
    ]
    test_breakdown_sum(all_issues)

    print(f"\n=== Results: {PASS} passed, {FAIL} failed ===")
    return 1 if FAIL > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
