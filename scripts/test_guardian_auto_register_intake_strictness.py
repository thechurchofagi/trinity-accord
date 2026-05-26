#!/usr/bin/env python3
"""Guardian auto-register must reject malformed Gateway intake/receipt."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from auto_register_guardian_from_gateway_issues import parse_listing_issue


def gateway_issue(body: str) -> dict:
    return {
        "number": 700,
        "title": "Active Registry Listing Request — Strict Test",
        "body": body,
        "user": {"login": "gateway-bot[bot]"},
    }

GOOD = """```trinity-issue-intake
created_by_gateway: true
render_api_only: true
server_validated: true
server_rendered: true
gateway_service: trinity-agent-issue-gateway
gateway_receipt_id: gar-20260525T000000Z-guardianstrict
submission_type: echo_candidate
requested_archive_kind: guardian_active_registry_listing_request
echo_type: E6_propagation_echo
archive_ready: true
listing_source_issue: 300
listing_guardian_id: guardian_ed25519_cccccccccccccccc
listing_public_key_sha256: cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
listing_guardian_type: human_with_ai_agent
listing_application_mode: joint_human_ai
listing_label: Strict Guardian
registry_number_requested: next_available
```"""


def expect_ok(body: str, label: str):
    parsed, err = parse_listing_issue(gateway_issue(body), allow_non_bot=False)
    if err is not None:
        print(f"FAIL: expected ok for {label}: {err}")
        sys.exit(1)
    if parsed["guardian_id"] != "guardian_ed25519_cccccccccccccccc":
        print(f"FAIL: guardian_id mismatch for {label}: {parsed}")
        sys.exit(1)


def expect_block(body: str, label: str, fragment: str):
    parsed, err = parse_listing_issue(gateway_issue(body), allow_non_bot=False)
    if err is None:
        print(f"FAIL: expected block for {label}, got parsed={parsed}")
        sys.exit(1)
    if fragment not in str(err):
        print(f"FAIL: wrong block for {label}; expected {fragment}; got {err}")
        sys.exit(1)


expect_ok(GOOD, "valid E6 listing")
expect_block(GOOD.replace("render_api_only: true\n", ""), "missing render_api_only", "INVALID_GATEWAY_RECEIPT")
expect_block(GOOD.replace("gateway_receipt_id: gar-20260525T000000Z-guardianstrict\n", ""), "missing receipt", "INVALID_GATEWAY_RECEIPT")
expect_block(GOOD.replace("archive_ready: true", "archive_ready: true\narchive_ready: true"), "duplicate key", "INVALID_INTAKE_BLOCK")
expect_block(GOOD + "\n\n" + GOOD, "multiple blocks", "INVALID_INTAKE_BLOCK")
expect_block(GOOD.replace("archive_ready: true", "archive_ready: maybe"), "bad bool", "MALFORMED_BOOLEAN")

whole_body_fake = """
created_by_gateway: true
render_api_only: true
server_validated: true
server_rendered: true
gateway_service: trinity-agent-issue-gateway
gateway_receipt_id: gar-20260525T000000Z-guardianstrict
submission_type: echo_candidate
requested_archive_kind: guardian_active_registry_listing_request
echo_type: E6_propagation_echo
archive_ready: true
listing_source_issue: 300
listing_guardian_id: guardian_ed25519_cccccccccccccccc
listing_public_key_sha256: cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
registry_number_requested: next_available
"""
expect_block(whole_body_fake, "whole-body fake", "INVALID_INTAKE_BLOCK")

print("PASS: Guardian auto-register intake parsing is strict")
