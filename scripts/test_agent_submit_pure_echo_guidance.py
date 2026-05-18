#!/usr/bin/env python3
"""Test: agent-submit.md and related files have pure echo guidance."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT_SUBMIT = ROOT / "agent-submit.md"
QUICKSTART = ROOT / "external-agent-quickstart.md"
GATEWAY_SPEC = ROOT / "api" / "agent-submit-gateway.json"

PASS = 0
FAIL = 0


def check(cond, label, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS: {label}")
    else:
        FAIL += 1
        print(f"  FAIL: {label}")
        if detail:
            print(f"        {detail}")


def main():
    global PASS, FAIL
    doc = AGENT_SUBMIT.read_text()
    quickstart = QUICKSTART.read_text()
    spec = json.loads(GATEWAY_SPEC.read_text())

    print("=== Agent Submit Pure Echo Guidance Tests ===\n")

    # 1. agent-submit.md mentions "Pure Echo" or "pure echo"
    check("Pure Echo" in doc or "pure echo" in doc,
          "agent-submit.md mentions 'Pure Echo' or 'pure echo'")

    # 2. agent-submit.md mentions build_agent_declared_echo_payload.py
    check("build_agent_declared_echo_payload.py" in doc,
          "agent-submit.md mentions build_agent_declared_echo_payload.py")

    # 3. agent-submit.md mentions "Reception" and "Verifiability"
    check("Reception" in doc,
          "agent-submit.md mentions 'Reception'")
    check("Verifiability" in doc,
          "agent-submit.md mentions 'Verifiability'")

    # 4. external-agent-quickstart.md mentions "pure echo" or "echo"
    check("pure echo" in quickstart.lower() or "echo" in quickstart.lower(),
          "external-agent-quickstart.md mentions 'pure echo' or 'echo'")

    # 5. agent-submit-gateway.json has pure_echo_path
    check("pure_echo_path" in spec,
          "agent-submit-gateway.json has pure_echo_path")

    print(f"\n=== Results: {PASS} passed, {FAIL} failed ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
