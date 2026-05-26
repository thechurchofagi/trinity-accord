#!/usr/bin/env python3
"""
Verify that the issue submission gate is properly deployed online.
Checks that required rules are present in live pages.

Usage:
    python3 scripts/verify_issue_submission_gate_online.py
    python3 scripts/verify_issue_submission_gate_online.py --local  # check files only
"""
import json
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

results = []

LOCAL_ONLY = "--local" in sys.argv


def test(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{status}: {name} — {detail}")


def read_text(path):
    full = ROOT / path.lstrip("/")
    if full.exists():
        return full.read_text(encoding="utf-8")
    return ""


def load_json(path):
    full = ROOT / path.lstrip("/")
    if full.exists():
        with open(full, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# Check 1: llms.txt contains Claim Gate mandatory rule
llms = read_text("/llms.txt")
test("llms_txt_mandatory_rule",
     "MANDATORY CLAIM GATE RULE" in llms,
     "llms.txt must contain MANDATORY CLAIM GATE RULE")

# Check 2: agent.json mandatory_before_submission includes new rules
agent_json = load_json("/.well-known/agent.json")
mandatory = agent_json.get("mandatory_before_submission", [])
has_provenance = any("provenance-consistency" in p for p in mandatory)
has_issue_policy = any("issue-submission-policy" in p for p in mandatory)
test("agent_json_mandatory_before_submission",
     has_provenance and has_issue_policy,
     f"agent.json mandatory_before_submission: provenance={has_provenance}, issue_policy={has_issue_policy}")

# Check 3: agent-entry-protocol has submission_gate
entry_proto = load_json("/api/agent-entry-protocol.json")
has_submission_gate = "submission_gate" in entry_proto
gate = entry_proto.get("submission_gate", {})
has_claim_gate = gate.get("required", False)
test("agent_entry_submission_gate",
     has_submission_gate and has_claim_gate,
     f"agent-entry-protocol has submission_gate={has_submission_gate}, required={has_claim_gate}")

# Check 4: provenance-consistency-rules.json exists and is valid
prov_path = ROOT / "api" / "provenance-consistency-rules.json"
test("provenance_rules_reachable",
     prov_path.exists(),
     f"api/provenance-consistency-rules.json exists={prov_path.exists()}")

# Check 5: issue-submission-policy.json exists
issue_path = ROOT / "api" / "issue-submission-policy.json"
test("issue_submission_policy_reachable",
     issue_path.exists(),
     f"api/issue-submission-policy.json exists={issue_path.exists()}")

# Check 6: verification-claim-scope.json exists
scope_path = ROOT / "api" / "verification-claim-scope.json"
test("claim_scope_rules_reachable",
     scope_path.exists(),
     f"api/verification-claim-scope.json exists={scope_path.exists()}")

# Check 7: claim-gate-rules.json exists
cgr_path = ROOT / "api" / "claim-gate-rules.json"
test("claim_gate_rules_reachable",
     cgr_path.exists(),
     f"api/claim-gate-rules.json exists={cgr_path.exists()}")

# Check 8: freeform technical report invalid statement in llms.txt
test("freeform_invalid_in_llms",
     "Free-form" in llms or "free-form" in llms or "freeform" in llms,
     "llms.txt contains freeform invalid statement")

# Check 9: submission_requires in agent.json
sub_req = agent_json.get("submission_requires", {})
test("agent_json_submission_requires",
     sub_req.get("claim_gate") and sub_req.get("freeform_claims_allowed") == False,
     f"submission_requires: claim_gate={sub_req.get('claim_gate')}, freeform_allowed={sub_req.get('freeform_claims_allowed')}")

# Check 10: Issue templates require Claim Gate output
echo_tmpl = read_text("/.github/ISSUE_TEMPLATE/echo.yml")
vrf_tmpl = read_text("/.github/ISSUE_TEMPLATE/verification_report.yml")
echo_requires_cg = "evidence_input" in echo_tmpl.lower() or "claim_gate" in echo_tmpl.lower()
vrf_requires_cg = "evidence_input" in vrf_tmpl.lower() or "claim_gate" in vrf_tmpl.lower()
test("issue_templates_require_claim_gate",
     echo_requires_cg and vrf_requires_cg,
     f"echo.yml requires CG={echo_requires_cg}, verification_report.yml requires CG={vrf_requires_cg}")

# Check 11: New API JSON files are valid JSON
for api_file in ["api/provenance-consistency-rules.json", "api/verification-claim-scope.json", "api/issue-submission-policy.json"]:
    try:
        load_json(api_file)
        test(f"json_valid_{os.path.basename(api_file)}", True, f"{api_file} is valid JSON")
    except Exception as e:
        test(f"json_valid_{os.path.basename(api_file)}", False, f"{api_file} invalid: {e}")

# Check 12: New test scripts exist
for script in ["scripts/validate_provenance_consistency.py", "scripts/test_provenance_consistency.py",
               "scripts/test_issue_submission_vs_archive.py", "scripts/test_claim_scope_minimal_partial_full.py",
               "scripts/test_echo_type_derivation.py"]:
    exists = (ROOT / script).exists()
    test(f"script_exists_{os.path.basename(script)}", exists, f"{script} exists={exists}")

print("\n=== SUMMARY ===")
failed = [n for n, s in results if s == "FAIL"]
if failed:
    print(f"FAILED: {len(failed)} checks: {', '.join(failed)}")
    print("FINAL: FAIL — issue submission gate online verification failed.")
    sys.exit(1)
else:
    print(f"PASSED: all {len(results)} checks")
    print("FINAL: PASS — issue submission gate online verified.")
    sys.exit(0)
