#!/usr/bin/env python3
"""Test that post-effective records missing oath summary are excluded from index,
and legacy pre-effective records missing oath summary are included with flag.

Tests the index builder's oath gate logic without requiring a live GitHub API.
"""
import json
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from gateway_v0_v5_policy import RENDER_API_ONLY_EFFECTIVE_AT
from build_agent_declared_verification_index_from_issues import (
    build_index,
    parse_int,
    is_after_effective_date,
)

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


def make_issue(number, created_at, intake_fields):
    """Create a fake issue dict with a trinity-issue-intake block."""
    lines = ["```trinity-issue-intake"]
    for k, v in intake_fields.items():
        lines.append(f"{k}: {v}")
    lines.append("```")
    body = "\n".join(lines)
    return {
        "number": number,
        "body": body,
        "createdAt": created_at,
        "closedAt": created_at,
        "url": f"https://github.com/test/repo/issues/{number}",
        "labels": [],
    }


def test_post_effective_missing_oath_excluded():
    """Post-effective record with valid receipt but no oath summary must be excluded."""
    global PASS, FAIL
    print("\n--- Post-effective missing oath → excluded ---")

    after = "2026-05-17T10:00:00Z"
    issue = make_issue(200, after, {
        "requested_archive_kind": "agent_declared_verification_archive",
        "archive_ready": "true",
        "auto_archive_action": "auto_archive_agent_declared_verification",
        "created_by_gateway": "true",
        "render_api_only": "true",
        "server_validated": "true",
        "server_rendered": "true",
        "gateway_service": "trinity-agent-issue-gateway",
        "gateway_receipt_id": "gar-20260517T100000Z-abcdef",
        # No verification_oath_present or oath fields
    })

    index = build_index([issue], repo="test/repo")
    check(len(index["records"]) == 0, "post-effective missing oath → 0 records")
    check(200 in index["skipped_missing_oath_summary"], "issue #200 in skipped_missing_oath_summary")


def test_post_effective_short_readback_excluded():
    """Post-effective record with oath but readback < 160 chars must be excluded."""
    global PASS, FAIL
    print("\n--- Post-effective short readback → excluded ---")

    after = "2026-05-17T10:00:00Z"
    issue = make_issue(201, after, {
        "requested_archive_kind": "agent_declared_verification_archive",
        "archive_ready": "true",
        "auto_archive_action": "auto_archive_agent_declared_verification",
        "created_by_gateway": "true",
        "render_api_only": "true",
        "server_validated": "true",
        "server_rendered": "true",
        "gateway_service": "trinity-agent-issue-gateway",
        "gateway_receipt_id": "gar-20260517T100001Z-abcdef",
        "verification_oath_present": "true",
        "oath_read": "true",
        "oath_version": "v1",
        "oath_text_sha256": "a" * 64,
        "readback_required": "true",
        "agent_readback_present": "true",
        "agent_readback_char_count": "100",  # < 160
        "agent_readback_sha256": "b" * 64,
    })

    index = build_index([issue], repo="test/repo")
    check(len(index["records"]) == 0, "post-effective short readback → 0 records")
    check(201 in index["skipped_missing_oath_summary"], "issue #201 in skipped_missing_oath_summary")


def test_legacy_missing_oath_included_with_flag():
    """Legacy pre-effective record missing oath summary must be included with legacy flag."""
    global PASS, FAIL
    print("\n--- Legacy missing oath → included with flag ---")

    before = "2026-05-16T00:00:00Z"
    issue = make_issue(100, before, {
        "requested_archive_kind": "agent_declared_verification_archive",
        "archive_ready": "true",
        "auto_archive_action": "auto_archive_agent_declared_verification",
        # No gateway receipt, no oath
    })

    index = build_index([issue], repo="test/repo")
    check(len(index["records"]) == 1, "legacy missing oath → 1 record")
    rec = index["records"][0]
    check(rec.get("legacy_oath_summary_missing") is True, "legacy_oath_summary_missing=true")
    check(rec.get("verification_oath_present") is None, "verification_oath_present absent")


def test_post_effective_valid_oath_included():
    """Post-effective record with valid oath summary must be included."""
    global PASS, FAIL
    print("\n--- Post-effective valid oath → included ---")

    after = "2026-05-17T10:00:00Z"
    issue = make_issue(300, after, {
        "requested_archive_kind": "agent_declared_verification_archive",
        "archive_ready": "true",
        "auto_archive_action": "auto_archive_agent_declared_verification",
        "created_by_gateway": "true",
        "render_api_only": "true",
        "server_validated": "true",
        "server_rendered": "true",
        "gateway_service": "trinity-agent-issue-gateway",
        "gateway_receipt_id": "gar-20260517T100002Z-abcdef",
        "verification_oath_present": "true",
        "oath_read": "true",
        "oath_version": "v1",
        "oath_text_sha256": "a" * 64,
        "readback_required": "true",
        "agent_readback_present": "true",
        "agent_readback_char_count": "200",
        "agent_readback_sha256": "b" * 64,
    })

    index = build_index([issue], repo="test/repo")
    check(len(index["records"]) == 1, "post-effective valid oath → 1 record")
    rec = index["records"][0]
    check(rec.get("verification_oath_present") is True, "verification_oath_present=true")
    check(rec.get("agent_readback_char_count") == 200, "agent_readback_char_count=200")
    check(rec.get("legacy_oath_summary_missing") is None, "no legacy flag")


def test_malformed_char_count_does_not_crash():
    """Malformed agent_readback_char_count must not crash the builder."""
    global PASS, FAIL
    print("\n--- Malformed char_count → no crash ---")

    after = "2026-05-17T10:00:00Z"
    issue = make_issue(400, after, {
        "requested_archive_kind": "agent_declared_verification_archive",
        "archive_ready": "true",
        "auto_archive_action": "auto_archive_agent_declared_verification",
        "created_by_gateway": "true",
        "render_api_only": "true",
        "server_validated": "true",
        "server_rendered": "true",
        "gateway_service": "trinity-agent-issue-gateway",
        "gateway_receipt_id": "gar-20260517T100003Z-abcdef",
        "verification_oath_present": "true",
        "oath_read": "true",
        "oath_version": "v1",
        "oath_text_sha256": "a" * 64,
        "readback_required": "true",
        "agent_readback_present": "true",
        "agent_readback_char_count": "abc",  # malformed
        "agent_readback_sha256": "b" * 64,
    })

    try:
        index = build_index([issue], repo="test/repo")
        check(True, "no crash on malformed char_count")
        # Should be excluded (count defaults to 0 < 160)
        check(len(index["records"]) == 0, "malformed char_count → excluded")
        check(400 in index["skipped_missing_oath_summary"], "issue #400 in skipped list")
    except (ValueError, TypeError) as e:
        FAIL += 1
        print(f"  FAIL: crashed on malformed char_count: {e}")


def test_parse_int():
    """parse_int helper must handle edge cases."""
    global PASS, FAIL
    print("\n--- parse_int helper ---")

    check(parse_int("42") == 42, "parse_int('42') = 42")
    check(parse_int("abc") == 0, "parse_int('abc') = 0")
    check(parse_int(None) == 0, "parse_int(None) = 0")
    check(parse_int("") == 0, "parse_int('') = 0")
    check(parse_int("159", 0) == 159, "parse_int('159', 0) = 159")


def test_skipped_missing_oath_summary_in_output():
    """Index output must include skipped_missing_oath_summary list."""
    global PASS, FAIL
    print("\n--- skipped_missing_oath_summary in output ---")

    after = "2026-05-17T10:00:00Z"
    issue = make_issue(500, after, {
        "requested_archive_kind": "agent_declared_verification_archive",
        "archive_ready": "true",
        "auto_archive_action": "auto_archive_agent_declared_verification",
        "created_by_gateway": "true",
        "render_api_only": "true",
        "server_validated": "true",
        "server_rendered": "true",
        "gateway_service": "trinity-agent-issue-gateway",
        "gateway_receipt_id": "gar-20260517T100004Z-abcdef",
        # No oath
    })

    index = build_index([issue], repo="test/repo")
    check("skipped_missing_oath_summary" in index, "key present in index output")
    check(isinstance(index["skipped_missing_oath_summary"], list), "is a list")
    check(500 in index["skipped_missing_oath_summary"], "issue #500 in list")


def main():
    global PASS, FAIL
    print("=== Agent-Declared Index Oath Fields Tests ===")

    test_post_effective_missing_oath_excluded()
    test_post_effective_short_readback_excluded()
    test_legacy_missing_oath_included_with_flag()
    test_post_effective_valid_oath_included()
    test_malformed_char_count_does_not_crash()
    test_parse_int()
    test_skipped_missing_oath_summary_in_output()

    print(f"\n=== Results: {PASS} passed, {FAIL} failed ===")
    return 1 if FAIL > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
