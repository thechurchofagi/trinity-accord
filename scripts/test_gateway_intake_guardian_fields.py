#!/usr/bin/env python3
"""gateway_intake must preserve Guardian listing/source fields."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from gateway_intake import parse_intake_block

body = """```trinity-issue-intake
created_by_gateway: true
render_api_only: true
server_validated: true
server_rendered: true
gateway_service: trinity-agent-issue-gateway
gateway_receipt_id: gar-20260525T000000Z-guardianfixture
submission_type: echo_candidate
requested_archive_kind: guardian_active_registry_listing_request
echo_type: E6_propagation_echo
archive_ready: true
listing_source_issue: 300
listing_guardian_id: guardian_ed25519_cccccccccccccccc
listing_public_key_sha256: cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
listing_guardian_type: human_with_ai_agent
listing_application_mode: joint_human_ai
listing_label: Test Guardian
registry_number_requested: next_available
guardian_status: valid_self_registered_guardian_claim
guardian_signature_valid: true
guardian_payload_hash_matches: true
guardian_id_matches_public_key: true
```"""

fields = parse_intake_block(body, required=True)

required = [
    "submission_type",
    "listing_source_issue",
    "listing_guardian_id",
    "listing_public_key_sha256",
    "listing_guardian_type",
    "listing_application_mode",
    "listing_label",
    "registry_number_requested",
    "guardian_status",
    "guardian_signature_valid",
    "guardian_payload_hash_matches",
    "guardian_id_matches_public_key",
]

missing = [k for k in required if k not in fields]
if missing:
    print(f"FAIL: gateway_intake dropped Guardian fields: {missing}")
    sys.exit(1)

print("PASS: gateway_intake preserves Guardian listing/source fields")
