#!/usr/bin/env python3
"""archive_echo_issue Gateway eligibility must use strict intake parser and receipt policy."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from archive_echo_issue import validate_gateway_archive_eligibility


def issue(body: str, labels=None):
    return {
        "number": 999001,
        "body": body,
        "labels": [{"name": x} for x in (labels or ["archive:agent-declared-echo"])],
    }


GOOD = """```trinity-issue-intake
created_by_gateway: true
render_api_only: true
server_validated: true
server_rendered: true
gateway_service: trinity-agent-issue-gateway
gateway_receipt_id: gar-20260524T000000Z-fixture
archive_ready: true
requested_archive_kind: agent_declared_echo_archive
echo_type: E6_propagation_echo
```"""


def expect_pass(body, label):
    try:
        validate_gateway_archive_eligibility(issue(body))
    except SystemExit as e:
        print(f"FAIL: expected pass for {label}: {e}")
        sys.exit(1)


def expect_fail(body, label, fragment):
    try:
        validate_gateway_archive_eligibility(issue(body))
    except SystemExit as e:
        if fragment not in str(e):
            print(f"FAIL: wrong failure for {label}: {e}")
            sys.exit(1)
        return
    print(f"FAIL: expected failure for {label}")
    sys.exit(1)


expect_pass(GOOD, "valid Gateway intake")

whole_body_fake = """
created_by_gateway: true
render_api_only: true
server_validated: true
server_rendered: true
gateway_service: trinity-agent-issue-gateway
gateway_receipt_id: gar-20260524T000000Z-fixture
archive_ready: true
requested_archive_kind: agent_declared_echo_archive
"""
expect_fail(whole_body_fake, "whole-body fake receipt", "intake block")

missing_render_api = GOOD.replace("render_api_only: true\n", "")
expect_fail(missing_render_api, "missing render_api_only", "invalid Gateway receipt")

bad_service = GOOD.replace("gateway_service: trinity-agent-issue-gateway", "gateway_service: fake-service")
expect_fail(bad_service, "bad gateway_service", "invalid Gateway receipt")

duplicate_key = GOOD.replace("archive_ready: true", "archive_ready: true\narchive_ready: true")
expect_fail(duplicate_key, "duplicate key", "duplicate intake key")

multiple_blocks = GOOD + "\n\n" + GOOD
expect_fail(multiple_blocks, "multiple intake blocks", "multiple trinity-issue-intake blocks")

bad_bool = GOOD.replace("archive_ready: true", "archive_ready: maybe")
expect_fail(bad_bool, "malformed archive_ready", "invalid archive_ready")

print("PASS: archive_echo_issue Gateway intake eligibility is strict")
