#!/usr/bin/env python3
"""
Agent Submit Gateway Render API Only Contract Test.
Loads api/agent-submit-gateway.json and validates the v0_v5_archive_submission contract.

Usage:
    python3 scripts/test_agent_submit_gateway_render_api_only_contract.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PASS_COUNT = 0
FAIL_COUNT = 0
TOTAL = 0


def check(condition, label):
    global PASS_COUNT, FAIL_COUNT, TOTAL
    TOTAL += 1
    if condition:
        PASS_COUNT += 1
        print(f"  PASS: {label}")
    else:
        FAIL_COUNT += 1
        print(f"  FAIL: {label}")


print("=== Agent Submit Gateway Render API Only Contract Test ===\n")

gateway_path = ROOT / "api" / "agent-submit-gateway.json"
check(gateway_path.exists(), "api/agent-submit-gateway.json exists")

try:
    data = json.loads(gateway_path.read_text(encoding="utf-8"))
    check(True, "api/agent-submit-gateway.json is valid JSON")
except json.JSONDecodeError as e:
    check(False, f"api/agent-submit-gateway.json is valid JSON: {e}")
    print(f"\n=== Results: {PASS_COUNT}/{TOTAL} passed ===")
    sys.exit(1)

# Check v0_v5_archive_submission exists
v = data.get("v0_v5_archive_submission")
check(v is not None, "v0_v5_archive_submission object exists")

if v:
    check(v.get("render_api_only") is True,
          "v0_v5_archive_submission.render_api_only = true")
    check(v.get("agent_declared_template_levels") == ["V0", "V1", "V2", "V3", "V4", "V4+", "V5"],
          "agent_declared_template_levels includes all V0-V5 including V4+")
    check(v.get("v4_plus_is_distinct_level") is True,
          "v4_plus_is_distinct_level = true")
    check(v.get("v4_plus_is_not_v4_and_above") is True,
          "v4_plus_is_not_v4_and_above = true")
    check(v.get("v6_plus_included") is False,
          "v6_plus_included = false")
    check(v.get("v6_plus_mode") == "strict_evidence",
          "v6_plus_mode = strict_evidence")
    check(v.get("github_pat_required_from_agent") is False,
          "github_pat_required_from_agent = false")
    check(v.get("agent_should_request_github_pat") is False,
          "agent_should_request_github_pat = false")
    check(v.get("direct_github_issue_allowed") is False,
          "direct_github_issue_allowed = false")
    check(v.get("human_manual_issue_creation_allowed") is False,
          "human_manual_issue_creation_allowed = false")
    check(v.get("gateway_creates_issue_server_side") is True,
          "gateway_creates_issue_server_side = true")
    check(v.get("agent_creates_issue") is False,
          "agent_creates_issue = false")
    check("if_agent_cannot_post" in v,
          "if_agent_cannot_post field exists")

# Check top-level does NOT contain misleading legacy fields at top level
print("\n--- Legacy field isolation check ---")
misleading_fields = [
    "agent_has_no_pat",
    "agent_cannot_create_issue",
    "create_github_issue_or_intake_record",
    "label_as_agent-gateway-intake",
    "do_not_mark_as_archived_echo",
]
for field in misleading_fields:
    if field in data:
        # Check if it's under legacy section
        legacy = data.get("legacy_or_non_archive_general_intake", {})
        if field in legacy:
            check(True, f"'{field}' is under legacy_or_non_archive_general_intake (isolated)")
        else:
            check(False, f"'{field}' should not be at top level; move to legacy_or_non_archive_general_intake")
    else:
        check(True, f"'{field}' not at top level (removed or isolated)")

# Check legacy section has proper not_for
legacy = data.get("legacy_or_non_archive_general_intake", {})
if legacy:
    not_for = legacy.get("not_for", [])
    for level in ["V0", "V1", "V2", "V3", "V4", "V4+", "V5"]:
        check(level in not_for,
              f"legacy.not_for includes {level}")
    check(legacy.get("v0_v5_archive_overrides_this_section") is True,
          "legacy.v0_v5_archive_overrides_this_section = true")

# Check expected_gateway_behavior_v0_v5
behavior = data.get("expected_gateway_behavior_v0_v5", [])
check(len(behavior) > 0, "expected_gateway_behavior_v0_v5 exists and is non-empty")
required_behaviors = [
    "never_request_github_pat_from_agent",
    "never_expose_github_credentials_to_agent",
    "create_github_issue_server_side",
]
for rb in required_behaviors:
    check(rb in behavior, f"expected_gateway_behavior includes '{rb}'")

print(f"\n=== Results: {PASS_COUNT}/{TOTAL} passed ===")
if FAIL_COUNT > 0:
    print(f"FAILED: {FAIL_COUNT} checks failed")
    sys.exit(1)
else:
    print("AGENT_SUBMIT_GATEWAY_RENDER_API_ONLY_CONTRACT_OK")
    sys.exit(0)
