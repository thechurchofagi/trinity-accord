#!/usr/bin/env python3
"""
TA-REDTEAM-2026-020 PR3: External human authorization of AI does NOT produce formal attestation.

External human authorization alone does NOT produce formal attestation.
AI independent verification must NOT count as formal human/institutional attestation.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "scripts"))

from triage_echo_issue import detect_independence_overclaim_scoped, detect_human_solicited_context


def test(label, passed):
    if passed:
        print(f"  PASS: {label}")
    else:
        print(f"  FAIL: {label}")
    return passed


def main():
    passed = 0
    failed = 0

    # ── Test 1: Human-solicited AI work claiming "independent attestation" → overclaim ──
    text = """
## Provenance / Agency
- solicited: true
- independence_class: human_solicited_agent_response
- agency_level: A1_human_gave_exact_url
- operator_type: ai_agent

This is an independent attestation of the Trinity Accord.
"""
    result = detect_independence_overclaim_scoped(text, text)
    if test("Human-solicited AI claiming 'independent attestation' → overclaim detected",
            result is not None and result["severity"] == "hard"):
        passed += 1
    else:
        failed += 1

    # ── Test 2: AI verification with structured attestation denial → no overclaim ──
    # The triage script checks has_structured_attestation_denial() first.
    # When structured denial markers are present, independence overclaim is suppressed.
    text2 = """
## Provenance / Agency
- solicited: true
- independence_class: human_solicited_agent_response
- agency_level: A1_human_gave_exact_url
- operator_type: ai_agent
- not_independent_attestation: true
- do_not_count_as_attestation: true

This is a human-solicited agent-performed technical verification run.
"""
    from triage_echo_issue import has_structured_attestation_denial
    has_denial = has_structured_attestation_denial(text2)
    if test("Structured attestation denial detected",
            has_denial):
        passed += 1
    else:
        failed += 1

    # ── Test 3: Human-authorized AI claiming "institutional attestation" → overclaim ──
    text3 = """
## Provenance / Agency
- solicited: true
- independence_class: human_solicited_agent_response
- agency_level: A1_human_gave_exact_url
- operator_type: ai_agent

This is an institutional attestation verified by the AI agent.
"""
    result3 = detect_independence_overclaim_scoped(text3, text3)
    if test("Human-authorized AI claiming 'institutional attestation' → overclaim detected",
            result3 is not None and result3["severity"] == "hard"):
        passed += 1
    else:
        failed += 1

    # ── Test 4: AI verification mentioning "independent verification" (soft risk) ──
    text4 = """
## Provenance / Agency
- solicited: true
- independence_class: human_solicited_agent_response
- agency_level: A1_human_gave_exact_url
- operator_type: ai_agent

The agent performed an independent verification of the repository.
"""
    result4 = detect_independence_overclaim_scoped(text4, text4)
    if test("Human-solicited AI with 'independent verification' → soft overclaim risk",
            result4 is not None and result4["severity"] == "soft"):
        passed += 1
    else:
        failed += 1

    # ── Test 5: Verify claim registry flags ──
    registry = json.loads((ROOT / "api" / "claim-registry.json").read_text(encoding="utf-8"))
    claims = {c["claim_id"]: c for c in registry["claims"]}

    ai_claim = claims.get("ai_independent_verification_is_not_formal_attestation")
    if ai_claim:
        flags_correct = (
            ai_claim.get("counts_as_independent_attestation") is False
            and ai_claim.get("formal_attestation_gate_required") is True
        )
        if test("AI verification claim has correct attestation flags", flags_correct):
            passed += 1
        else:
            failed += 1
    else:
        print("  FAIL: Missing ai_independent_verification_is_not_formal_attestation claim")
        failed += 1

    auth_claim = claims.get("external_human_authorization_of_ai_does_not_produce_formal_attestation")
    if auth_claim:
        flags_correct = (
            auth_claim.get("counts_as_independent_attestation") is False
            and auth_claim.get("formal_attestation_gate_required") is True
        )
        if test("External authorization claim has correct attestation flags", flags_correct):
            passed += 1
        else:
            failed += 1
    else:
        print("  FAIL: Missing external_human_authorization_of_ai_does_not_produce_formal_attestation claim")
        failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
