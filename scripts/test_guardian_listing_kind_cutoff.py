#!/usr/bin/env python3
"""Guardian Stage 2 listing should accept legacy archive kind only before cutoff."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from auto_register_guardian_from_gateway_issues import parse_listing_issue


def body(kind: str) -> str:
    return f"""```trinity-issue-intake
created_by_gateway: true
render_api_only: true
server_validated: true
server_rendered: true
gateway_service: trinity-agent-issue-gateway
gateway_receipt_id: gar-20260525T000000Z-kindcutoff
submission_type: echo_candidate
requested_archive_kind: {kind}
echo_type: E6_propagation_echo
archive_ready: true
listing_source_issue: 300
listing_guardian_id: guardian_ed25519_cccccccccccccccc
listing_public_key_sha256: cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
listing_guardian_type: human_with_ai_agent
listing_application_mode: joint_human_ai
listing_label: Cutoff Guardian
registry_number_requested: next_available
```"""


def issue(kind: str, created_at: str) -> dict:
    return {
        "number": 702,
        "title": "Active Registry Listing Request — Kind Cutoff",
        "body": body(kind),
        "createdAt": created_at,
        "user": {"login": "gateway-bot[bot]"},
    }


def expect_ok(kind: str, created_at: str, label: str):
    parsed, err = parse_listing_issue(issue(kind, created_at), allow_non_bot=False)
    if err is not None:
        print(f"FAIL: expected ok for {label}: {err}")
        sys.exit(1)


def expect_block(kind: str, created_at: str, label: str):
    parsed, err = parse_listing_issue(issue(kind, created_at), allow_non_bot=False)
    if err is None:
        print(f"FAIL: expected block for {label}, got parsed={parsed}")
        sys.exit(1)
    if "LISTING_WRONG_ARCHIVE_KIND" not in str(err):
        print(f"FAIL: wrong block for {label}: {err}")
        sys.exit(1)


expect_ok("guardian_active_registry_listing_request", "2026-06-01T00:00:00Z", "current kind after cutoff")
expect_ok("agent_declared_echo_archive", "2026-05-25T00:00:00Z", "legacy kind before cutoff")
expect_block("agent_declared_echo_archive", "2026-06-01T00:00:00Z", "legacy kind after cutoff")

print("PASS: Guardian listing archive kind cutoff enforced")
