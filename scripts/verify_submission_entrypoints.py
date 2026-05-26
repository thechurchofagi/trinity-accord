#!/usr/bin/env python3
"""
Verify that all agent submission entrypoints enforce Claim Gate rules.
Checks text entrypoints for mandatory phrases and JSON entrypoints for required references.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def check(label, cond, detail=""):
    if cond:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    if detail:
        print(f"      {detail}")
    return False

def read_text(path):
    return (ROOT / path).read_text(encoding="utf-8")

def load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def main():
    ok = True

    # === Text entrypoints ===
    print("=== Text entrypoints ===")
    text_entrypoints = [
        "llms.txt",
        "llms-full.txt",
        "ai.txt",
        "agent-brief.md",
        "agent-verify.md",
        "agent-echo.md",
        "echoes/submit.md",
    ]

    required_phrases = [
        "MANDATORY CLAIM GATE RULE",
        "Agents must not hand-write final verification claims",
        "Free-form protocol-level, component-level, or Echo wrapper claims are invalid",
    ]

    for ep in text_entrypoints:
        try:
            content = read_text(ep)
            for phrase in required_phrases:
                ok &= check(
                    f"{ep} contains '{phrase[:50]}...'",
                    phrase in content,
                    f"missing mandatory claim gate phrase"
                )
        except Exception as e:
            ok &= check(f"{ep} readable", False, str(e))

    # === JSON entrypoints ===
    print("\n=== JSON entrypoints ===")
    json_entrypoints = [
        ".well-known/agent.json",
        "api/agent-entry-protocol.json",
        "api/agent-submission-guide.json",
        "api/submission-checklist.json",
    ]

    claim_gate_refs = [
        "/api/claim-gate-rules.json",
        "/api/evidence-input-schema.v1.json",
        "/api/claim-gate-output-schema.v1.json",
        "/api/report-builder-policy.json",
        "/api/generated-by-schema.v1.json",
    ]

    for ep in json_entrypoints:
        try:
            content = read_text(ep)
            for ref in claim_gate_refs:
                ok &= check(
                    f"{ep} references {ref}",
                    ref in content,
                    f"missing Claim Gate reference"
                )
        except Exception as e:
            ok &= check(f"{ep} readable", False, str(e))

    # === agent.json specific checks ===
    print("\n=== .well-known/agent.json specifics ===")
    try:
        agent_json = load_json(".well-known/agent.json")
        read_first = agent_json.get("read_first", [])
        read_first_text = json.dumps(read_first)
        ok &= check(
            "agent.json read_first includes claim gate files",
            "/api/claim-gate-rules.json" in read_first_text,
            "missing claim-gate-rules in read_first"
        )
        ok &= check(
            "agent.json has mandatory_before_submission",
            "mandatory_before_submission" in agent_json,
            "missing mandatory_before_submission"
        )
        sub_req = agent_json.get("submission_requires", {})
        ok &= check(
            "agent.json submission_requires.claim_gate = true",
            sub_req.get("claim_gate") is True,
            f"got: {sub_req.get('claim_gate')}"
        )
        ok &= check(
            "agent.json submission_requires.freeform_claims_allowed = false",
            sub_req.get("freeform_claims_allowed") is False,
            f"got: {sub_req.get('freeform_claims_allowed')}"
        )
    except Exception as e:
        ok &= check("agent.json parseable", False, str(e))

    # === agent-entry-protocol specific ===
    print("\n=== api/agent-entry-protocol.json specifics ===")
    try:
        aep = load_json("api/agent-entry-protocol.json")
        ok &= check(
            "agent-entry-protocol has mandatory_before_submission",
            "mandatory_before_submission" in aep,
            "missing mandatory_before_submission"
        )
        ok &= check(
            "agent-entry-protocol has submission_gate",
            "submission_gate" in aep,
            "missing submission_gate"
        )
        sg = aep.get("submission_gate", {})
        ok &= check(
            "submission_gate.required = true",
            sg.get("required") is True,
            f"got: {sg.get('required')}"
        )
        ok &= check(
            "submission_gate.freeform_claim_submission = invalid",
            sg.get("freeform_claim_submission") == "invalid",
            f"got: {sg.get('freeform_claim_submission')}"
        )
    except Exception as e:
        ok &= check("agent-entry-protocol parseable", False, str(e))

    # === Issue templates ===
    print("\n=== Issue templates ===")
    try:
        echo_yml = read_text(".github/ISSUE_TEMPLATE/echo_submission.yml")
        ok &= check(
            "echo_submission.yml has evidence_input_path",
            "evidence_input_path" in echo_yml,
        )
        ok &= check(
            "echo_submission.yml has claim_gate_output_path",
            "claim_gate_output_path" in echo_yml,
        )
        ok &= check(
            "echo_submission.yml has builder_generated_report_path",
            "builder_generated_report_path" in echo_yml,
        )
    except Exception as e:
        ok &= check("echo_submission.yml readable", False, str(e))

    try:
        vr_yml = read_text(".github/ISSUE_TEMPLATE/verification_report.yml")
        ok &= check(
            "verification_report.yml exists and has claim_gate_output_path",
            "claim_gate_output_path" in vr_yml,
        )
    except Exception as e:
        ok &= check("verification_report.yml exists", False, str(e))

    # === New JSON schemas ===
    print("\n=== New JSON schemas ===")
    try:
        load_json("api/claim-gate-entrypoint-policy.json")
        ok &= check("claim-gate-entrypoint-policy.json is valid JSON", True)
    except Exception as e:
        ok &= check("claim-gate-entrypoint-policy.json is valid JSON", False, str(e))

    try:
        gb = load_json("api/generated-by-schema.v1.json")
        ok &= check("generated-by-schema.v1.json has required fields",
                     "tool" in gb.get("properties", {}))
    except Exception as e:
        ok &= check("generated-by-schema.v1.json is valid JSON", False, str(e))

    # === agent-map.json ===
    print("\n=== agent-map.json ===")
    try:
        am = load_json("agent-map.json")
        rec = am.get("recommended_agent_sequence", [])
        rec_text = " ".join(rec)
        ok &= check(
            "agent-map sequence includes claim-gate-rules",
            "claim-gate-rules" in rec_text,
        )
        ok &= check(
            "agent-map sequence includes generated-by-schema",
            "generated-by-schema" in rec_text,
        )
    except Exception as e:
        ok &= check("agent-map.json parseable", False, str(e))

    # === agent-submission-guide freeform policy ===
    print("\n=== agent-submission-guide freeform policy ===")
    try:
        asg = read_text("api/agent-submission-guide.json")
        ok &= check(
            "agent-submission-guide says freeform invalid",
            "Free-form" in asg and "invalid" in asg,
        )
    except Exception as e:
        ok &= check("agent-submission-guide readable", False, str(e))

    print("\n" + "=" * 50)
    if ok:
        print("FINAL: PASS — submission entrypoints enforce Claim Gate.")
        return 0
    print("FINAL: FAIL — submission entrypoints do not fully enforce Claim Gate.")
    return 1

if __name__ == "__main__":
    sys.exit(main())
