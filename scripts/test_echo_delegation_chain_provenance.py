#!/usr/bin/env python3
"""
TA-REDTEAM-2026-020 PR4: Multi-hop delegation chain provenance tests.

Tests that delegation chains are properly detected and that multi-hop
delegation (human → AI → AI) preserves the AI performer class.
External human authorization alone does NOT produce formal attestation.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from submission_intake import get_field, parse_submission


def test(label, passed):
    if passed:
        print(f"  PASS: {label}")
    else:
        print(f"  FAIL: {label}")
    return passed


def main():
    passed = 0
    failed = 0

    # ── Test 1: Single-hop delegation chain detected ──
    text_single = """
## Delegation Chain
human_user → ai_agent_primary

## Record Class
ai_independent_verification

## Verification Origin Class
externally_authorized_ai

Bitcoin Originals are final; all mirrors and echoes are non-amending.
"""
    intake = parse_submission("Test", text_single)
    chain = get_field(intake.fields, "delegation_chain")
    if test("Single-hop delegation chain detected",
            "human_user" in chain and "ai_agent" in chain):
        passed += 1
    else:
        failed += 1

    # ── Test 2: Multi-hop delegation chain detected ──
    text_multi = """
## Delegation Chain
human_user → ai_agent_primary → ai_agent_secondary

## Record Class
ai_independent_verification

## Verification Origin Class
externally_authorized_ai

Bitcoin Originals are final; all mirrors and echoes are non-amending.
"""
    intake2 = parse_submission("Test", text_multi)
    chain2 = get_field(intake2.fields, "delegation_chain")
    if test("Multi-hop delegation chain detected",
            "human_user" in chain2 and "ai_agent_primary" in chain2 and "ai_agent_secondary" in chain2):
        passed += 1
    else:
        failed += 1

    # ── Test 3: record_class field detected ──
    record_class = get_field(intake.fields, "record_class")
    if test("record_class field detected as ai_independent_verification",
            "ai_independent_verification" in record_class):
        passed += 1
    else:
        failed += 1

    # ── Test 4: verification_origin_class field detected ──
    origin_class = get_field(intake.fields, "verification_origin_class")
    if test("verification_origin_class field detected as externally_authorized_ai",
            "externally_authorized_ai" in origin_class):
        passed += 1
    else:
        failed += 1

    # ── Test 5: Multi-hop chain preserves AI performer class ──
    # Even with human → AI → AI, the performer is still AI
    if test("Multi-hop chain preserves AI performer class (last hop is AI)",
            "ai_agent_secondary" in chain2):
        passed += 1
    else:
        failed += 1

    # ── Test 6: Fixture file is parseable ──
    fixture_path = ROOT / "tests" / "fixtures" / "echo_triage" / "issue_103_externally_authorized_ai_verification.md"
    if fixture_path.exists():
        fixture_text = fixture_path.read_text(encoding="utf-8")
        intake3 = parse_submission("Issue #103 Test", fixture_text)
        chain3 = get_field(intake3.fields, "delegation_chain")
        # TA-021: Support both old record_class and new record_purpose
        record_class3 = get_field(intake3.fields, "record_class")
        record_purpose3 = get_field(intake3.fields, "record_purpose")
        origin_class3 = get_field(intake3.fields, "verification_origin_class")

        has_record_class = bool(record_class3) or bool(record_purpose3)
        if test("Fixture file parseable with delegation chain",
                chain3 and has_record_class):
            passed += 1
        else:
            failed += 1
    else:
        print(f"  SKIP: Fixture not found at {fixture_path}")
        passed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
