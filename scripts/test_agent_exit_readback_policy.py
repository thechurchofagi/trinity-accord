#!/usr/bin/env python3
"""agent-output-policy should require explicit lifecycle exit/readback reporting."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
policy = json.loads((ROOT / "api" / "agent-output-policy.v1.json").read_text(encoding="utf-8"))

exit_policy = policy.get("agent_exit_readback_policy")
if not isinstance(exit_policy, dict):
    print("FAIL: missing agent_exit_readback_policy")
    sys.exit(1)

required = {
    "route_chosen",
    "builder_used",
    "payload_generated",
    "preflight_attempted",
    "preflight_result",
    "submission_attempted",
    "submission_result",
    "gateway_receipt_id_if_any",
    "github_issue_url_if_any",
    "archive_status_if_known",
    "public_status_readback_performed",
    "verification_state_by_this_agent",
    "remaining_uncertainty",
    "next_step_or_stop_reason",
}

fields = set(exit_policy.get("required_fields", []))
missing = sorted(required - fields)
if missing:
    print(f"FAIL: agent_exit_readback_policy missing required fields: {missing}")
    sys.exit(1)

must_not = set(exit_policy.get("must_not_claim", []))
for item in [
    "submitted_if_not_submitted",
    "archived_if_only_intake_created",
    "verified_if_only_gateway_accepted",
    "active_guardian_if_stage_2_not_listed",
    "public_status_updated_if_not_read_back",
]:
    if item not in must_not:
        print(f"FAIL: agent_exit_readback_policy missing must_not_claim {item}")
        sys.exit(1)

print("PASS: agent exit/readback policy is complete")
