#!/usr/bin/env python3
"""Guardian listing body-level fallback should work only before cutoff."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from auto_register_guardian_from_gateway_issues import parse_listing_issue


INTAKE_WITHOUT_LISTING_FIELDS = """```trinity-issue-intake
created_by_gateway: true
render_api_only: true
server_validated: true
server_rendered: true
gateway_service: trinity-agent-issue-gateway
gateway_receipt_id: gar-20260601T000000Z-bodyfallback
submission_type: echo_candidate
requested_archive_kind: guardian_active_registry_listing_request
echo_type: E6_propagation_echo
archive_ready: true
registry_number_requested: next_available
```"""

BODY_LISTING_FIELDS = """
listing_source_issue: 300
listing_guardian_id: guardian_ed25519_cccccccccccccccc
listing_public_key_sha256: cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
listing_guardian_type: human_with_ai_agent
listing_application_mode: joint_human_ai
listing_label: Body Fallback Guardian
"""


def issue(created_at: str) -> dict:
    return {
        "number": 703,
        "title": "Active Registry Listing Request — Body Fallback Cutoff",
        "body": INTAKE_WITHOUT_LISTING_FIELDS + "\n\n" + BODY_LISTING_FIELDS,
        "createdAt": created_at,
        "user": {"login": "gateway-bot[bot]"},
    }


def expect_ok(created_at: str, label: str):
    parsed, err = parse_listing_issue(issue(created_at), allow_non_bot=False)
    if err is not None:
        print(f"FAIL: expected ok for {label}: {err}")
        sys.exit(1)
    if parsed["guardian_id"] != "guardian_ed25519_cccccccccccccccc":
        print(f"FAIL: guardian_id not parsed from historical body fallback for {label}: {parsed}")
        sys.exit(1)


def expect_block(created_at: str, label: str):
    parsed, err = parse_listing_issue(issue(created_at), allow_non_bot=False)
    if err is None:
        print(f"FAIL: expected block for {label}, got parsed={parsed}")
        sys.exit(1)
    if "LISTING_BODY_FALLBACK_EXPIRED" not in str(err):
        print(f"FAIL: wrong block for {label}: {err}")
        sys.exit(1)


expect_ok("2026-06-01T00:00:00Z", "historical body fallback before cutoff")
expect_block("2026-07-01T00:00:00Z", "body fallback after cutoff")

print("PASS: Guardian listing body fallback cutoff enforced")
