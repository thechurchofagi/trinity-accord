#!/usr/bin/env python3
"""Agent output policy must expose explicit before_leaving exit/readback contract."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
policy = json.loads((ROOT / "api" / "agent-output-policy.v1.json").read_text(encoding="utf-8"))

exit_policy = policy.get("agent_exit_readback_policy", {})
errors = []

if exit_policy.get("before_leaving_required") is not True:
    errors.append("agent_exit_readback_policy.before_leaving_required must be true")

before = exit_policy.get("before_leaving")
if not isinstance(before, dict):
    errors.append("agent_exit_readback_policy.before_leaving must be an object")
else:
    text = json.dumps(before, sort_keys=True).lower()
    for phrase in [
        "before leaving",
        "final readback",
        "lifecycle stopped",
        "public_status_readback",
        "do not imply later background completion",
    ]:
        if phrase not in text:
            errors.append(f"before_leaving contract missing phrase: {phrase}")

required_fields = set(exit_policy.get("required_fields", []))
for field in [
    "route_chosen",
    "submission_attempted",
    "submission_result",
    "archive_status_if_known",
    "public_status_readback_performed",
    "verification_state_by_this_agent",
    "remaining_uncertainty",
    "next_step_or_stop_reason",
]:
    if field not in required_fields:
        errors.append(f"required_fields missing {field}")

if errors:
    print("FAIL: before_leaving exit/readback contract errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: agent output policy exposes before_leaving exit/readback contract")
