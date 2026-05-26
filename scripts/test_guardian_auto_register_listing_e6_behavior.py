#!/usr/bin/env python3
"""Guardian listing auto-register must accept canonical E6 and reject E7/stale names."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from auto_register_guardian_from_gateway_issues import parse_listing_issue
from protocol_echo_types import canonical_echo_type_for_id


def issue_with_echo(echo_type: str) -> dict:
    body = f"""```trinity-issue-intake
created_by_gateway: true
render_api_only: true
server_validated: true
server_rendered: true
gateway_service: trinity-agent-issue-gateway
gateway_receipt_id: gar-20260525T000000Z-guardiane6
submission_type: echo_candidate
requested_archive_kind: guardian_active_registry_listing_request
echo_type: {echo_type}
archive_ready: true
listing_source_issue: 300
listing_guardian_id: guardian_ed25519_cccccccccccccccc
listing_public_key_sha256: cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
listing_guardian_type: human_with_ai_agent
listing_application_mode: joint_human_ai
listing_label: E6 Guardian
registry_number_requested: next_available
```"""
    return {"number": 701, "title": "Active Registry Listing Request", "body": body, "user": {"login": "gateway-bot[bot]"}}


e6 = canonical_echo_type_for_id("E6")
_, err = parse_listing_issue(issue_with_echo(e6), allow_non_bot=False)
if err is not None:
    print(f"FAIL: canonical E6 listing should pass: {err}")
    sys.exit(1)

for bad in ["E7_refusal_echo", "E7_propagation_echo", "E6_preservation_echo"]:
    _, bad_err = parse_listing_issue(issue_with_echo(bad), allow_non_bot=False)
    if bad_err is None:
        print(f"FAIL: wrong listing echo_type should be rejected: {bad}")
        sys.exit(1)
    if "LISTING_NOT_E6_PROPAGATION_ECHO" not in str(bad_err):
        print(f"FAIL: wrong rejection for {bad}: {bad_err}")
        sys.exit(1)

print("PASS: Guardian listing auto-register accepts E6 and rejects E7/stale names")
