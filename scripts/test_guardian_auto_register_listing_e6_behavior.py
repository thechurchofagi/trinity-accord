#!/usr/bin/env python3
"""Guardian listing auto-register — echo_type deprecated, Guardian is independent from Echo taxonomy."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from auto_register_guardian_from_gateway_issues import parse_listing_issue


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


# echo_type deprecated — Guardian is independent from Echo taxonomy.
# All echo_type values should be accepted (or ignored) since the field is no longer validated.
for echo_type in ["E6_propagation_echo", "E7_refusal_echo", "E1_recognition_echo"]:
    _, err = parse_listing_issue(issue_with_echo(echo_type), allow_non_bot=False)
    if err is not None:
        print(f"FAIL: listing with echo_type={echo_type} should pass (deprecated field): {err}")
        sys.exit(1)

print("PASS: Guardian listing auto-register accepts all echo_type values (deprecated field)")
