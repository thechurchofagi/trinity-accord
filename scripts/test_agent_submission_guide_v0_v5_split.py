#!/usr/bin/env python3
"""Test agent-submission-guide.json has V0-V5 / V6+ split."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "api" / "agent-submission-guide.json"


def main():
    passed = 0
    failed = 0
    total = 0

    def check(label, condition, detail=""):
        nonlocal passed, failed, total
        total += 1
        if condition:
            print(f"PASS: {label}")
            passed += 1
        else:
            print(f"FAIL: {label}")
            if detail:
                print(f"  {detail}")
            failed += 1

    data = json.loads(GUIDE.read_text(encoding="utf-8"))

    # Test 1: v0_v5_agent_declared_rules exists
    check(
        "v0_v5_agent_declared_rules exists",
        "v0_v5_agent_declared_rules" in data,
    )

    # Test 2: v6_plus_strict_evidence_rules exists
    check(
        "v6_plus_strict_evidence_rules exists",
        "v6_plus_strict_evidence_rules" in data,
    )

    # Test 3: common_mistakes does not unconditionally say "Claiming V4 without script audit fields"
    mistakes = data.get("common_mistakes", [])
    for m in mistakes:
        if "Claiming V4 without script audit" in m:
            check(
                "common_mistakes V4 script audit has V0-V5 exception",
                "V0–V5" in m or "V0-V5" in m or "agent-declared" in m,
                f"Found: {m}",
            )

    # Test 4: verification_echo_intake_fields scope is V6+ strict only
    intake = data.get("verification_echo_intake_fields", {})
    scope = intake.get("scope", "")
    check(
        "verification_echo_intake_fields scope mentions V6+",
        "V6+" in scope or "V6" in scope,
        f"scope: {scope}",
    )
    check(
        "verification_echo_intake_fields scope mentions not required for V0-V5",
        "V0-V5" in scope or "V0–V5" in scope or "not required" in scope.lower(),
        f"scope: {scope}",
    )

    # Test 5: claim_gate.required_for mentions both paths
    cg = data.get("claim_gate", {})
    req_for = cg.get("required_for", "")
    check(
        "claim_gate.required_for mentions V0-V5 template",
        "V0" in req_for and "template" in req_for.lower(),
        f"required_for: {req_for}",
    )
    check(
        "claim_gate.required_for mentions V6+ strict",
        "V6+" in req_for or "strict" in req_for.lower(),
        f"required_for: {req_for}",
    )

    print(f"\n--- Results: {passed}/{total} passed, {failed} failed ---")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
