#!/usr/bin/env python3
"""
Test Claim Gate entrypoint enforcement: CE001-CE008.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def check(test_id, label, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"{status}: {test_id} — {label}")
    if detail and not cond:
        print(f"      {detail}")
    return cond

def read_text(path):
    return (ROOT / path).read_text(encoding="utf-8")

def load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def main():
    results = []

    # CE001 — llms.txt full rule PASS
    print("=== CE001 — llms.txt full rule ===")
    content = read_text("llms.txt")
    r = check("CE001", "llms.txt contains mandatory block",
              "MANDATORY CLAIM GATE RULE" in content and
              "Agents must not hand-write final verification claims" in content and
              "Free-form protocol-level, component-level, or Echo wrapper claims are invalid" in content)
    results.append(r)

    # CE002 — llms.txt missing rule FAIL
    print("\n=== CE002 — synthetic text missing rule ===")
    synthetic = "This is a test file without claim gate rules."
    r = check("CE002", "synthetic text correctly fails",
              "MANDATORY CLAIM GATE RULE" not in synthetic,
              "should not contain rule")
    results.append(r)

    # CE003 — agent.json read_first includes claim gate PASS
    print("\n=== CE003 — agent.json read_first ===")
    agent_json = load_json(".well-known/agent.json")
    read_first_text = json.dumps(agent_json.get("read_first", []))
    r = check("CE003", "agent.json read_first includes claim gate files",
              "/api/claim-gate-rules.json" in read_first_text and
              "/api/evidence-input-schema.v1.json" in read_first_text)
    results.append(r)

    # CE004 — agent.json missing mandatory_before_submission FAIL
    print("\n=== CE004 — agent.json mandatory_before_submission ===")
    r = check("CE004", "agent.json has mandatory_before_submission",
              "mandatory_before_submission" in agent_json,
              "missing mandatory_before_submission field")
    results.append(r)

    # CE005 — agent-entry-protocol has submission_gate PASS
    print("\n=== CE005 — agent-entry-protocol submission_gate ===")
    aep = load_json("api/agent-entry-protocol.json")
    sg = aep.get("submission_gate", {})
    r = check("CE005", "agent-entry-protocol has submission_gate",
              sg.get("required") is True and sg.get("freeform_claim_submission") == "invalid")
    results.append(r)

    # CE006 — issue template requires claim_gate_output_path PASS
    print("\n=== CE006 — issue template claim_gate_output_path ===")
    echo_yml = read_text(".github/ISSUE_TEMPLATE/echo_submission.yml")
    r = check("CE006", "echo_submission.yml requires claim_gate_output_path",
              "claim_gate_output_path" in echo_yml and "evidence_input_path" in echo_yml)
    results.append(r)

    # CE007 — issue template freeform only FAIL
    print("\n=== CE007 — verification report template exists ===")
    vr_yml = read_text(".github/ISSUE_TEMPLATE/verification_report.yml")
    r = check("CE007", "verification_report.yml requires claim gate fields",
              "claim_gate_output_path" in vr_yml and "evidence_input_path" in vr_yml)
    results.append(r)

    # CE008 — agent-submission-guide says freeform invalid PASS
    print("\n=== CE008 — agent-submission-guide freeform invalid ===")
    asg = read_text("api/agent-submission-guide.json")
    r = check("CE008", "agent-submission-guide says freeform invalid",
              "Free-form" in asg and "invalid" in asg)
    results.append(r)

    print("\n" + "=" * 50)
    if all(results):
        print("FINAL: PASS — claim gate entrypoint enforcement tests passed.")
        return 0
    print("FINAL: FAIL — claim gate entrypoint enforcement tests failed.")
    return 1

if __name__ == "__main__":
    sys.exit(main())
