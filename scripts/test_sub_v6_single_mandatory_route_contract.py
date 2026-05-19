#!/usr/bin/env python3
"""Test: Sub-V6 single mandatory route contract is declared in API files."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PASS = 0
FAIL = 0


def check(condition, msg):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {msg}")
    else:
        FAIL += 1
        print(f"  ❌ {msg}")


# --- agent-first-contact.json ---
print("\n=== agent-first-contact.json ===")
fc = json.loads((ROOT / "api" / "agent-first-contact.json").read_text())

v0v5_intent = None
for item in fc.get("choose_one", []):
    if item.get("intent") == "verify_v0_v5_agent_declared":
        v0v5_intent = item
        break

check(v0v5_intent is not None, "verify_v0_v5_agent_declared intent exists")

policy = (v0v5_intent or {}).get("single_mandatory_route_policy")
check(policy is not None, "single_mandatory_route_policy exists")

if policy:
    check(policy.get("route_id") == "sub_v6_agent_declared_template_archive",
          "route_id == sub_v6_agent_declared_template_archive")
    check(policy.get("only_valid_route_for_below_v6") is True,
          "only_valid_route_for_below_v6 == true")
    check(policy.get("declared_level_source") == "agent_oath_template_declaration",
          "declared_level_source == agent_oath_template_declaration")
    check(policy.get("evidence_chain_required") is False,
          "evidence_chain_required == false")
    check(policy.get("strict_evidence_path_forbidden") is True,
          "strict_evidence_path_forbidden == true")
    check(policy.get("strict_claim_gate_forbidden") is True,
          "strict_claim_gate_forbidden == true")
    check(policy.get("strict_evidence_downgrade_language_forbidden") is True,
          "strict_evidence_downgrade_language_forbidden == true")
    check(policy.get("wrong_path_result") == "reject_before_issue_creation",
          "wrong_path_result == reject_before_issue_creation")

# Check not_required includes needed items
not_req = (v0v5_intent or {}).get("not_required", [])
for item in ["evidence_input", "artifact_bundle", "downloads/verify.py", "build_from_evidence", "verification_session"]:
    check(item in not_req, f"not_required includes {item}")

# --- agent-submit-gateway.json ---
print("\n=== agent-submit-gateway.json ===")
sg = json.loads((ROOT / "api" / "agent-submit-gateway.json").read_text())

v0v5_sub = sg.get("v0_v5_archive_submission", {})
policy2 = v0v5_sub.get("single_mandatory_route_policy")
check(policy2 is not None, "v0_v5_archive_submission.single_mandatory_route_policy exists")

if policy2:
    check(policy2.get("route_id") == "sub_v6_agent_declared_template_archive",
          "route_id == sub_v6_agent_declared_template_archive")
    check(policy2.get("only_valid_route_for_below_v6") is True,
          "only_valid_route_for_below_v6 == true")
    check(policy2.get("declared_level_source") == "agent_oath_template_declaration",
          "declared_level_source == agent_oath_template_declaration")
    check(policy2.get("evidence_chain_required") is False,
          "evidence_chain_required == false")
    check(policy2.get("strict_evidence_path_forbidden") is True,
          "strict_evidence_path_forbidden == true")
    check(policy2.get("strict_claim_gate_forbidden") is True,
          "strict_claim_gate_forbidden == true")
    check(policy2.get("strict_evidence_downgrade_language_forbidden") is True,
          "strict_evidence_downgrade_language_forbidden == true")

# Check top-level alias
alias = sg.get("sub_v6_single_mandatory_route")
check(alias is not None, "sub_v6_single_mandatory_route top-level alias exists")
if alias:
    check(alias.get("enabled") is True, "alias.enabled == true")
    check(alias.get("strict_evidence_forbidden") is True, "alias.strict_evidence_forbidden == true")

print(f"\n{'='*50}")
print(f"Results: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
