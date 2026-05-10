#!/usr/bin/env python3
"""
TA-REDTEAM-2026-020 PR4: Issue #103 origin class regression test.

Ensures that externally-authorized AI verification submissions:
1. Are detected as AI independent verification (not human verification)
2. Do NOT count as formal attestation
3. Properly record delegation chain and origin class with exact expected values
4. Pass preflight with integrity declaration (no hard/high issues)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from preflight_echo_submission import preflight_check
from triage_echo_issue import detect_independence_overclaim_scoped
from submission_intake import parse_submission, get_field, get_bool_field


def test(label, passed, detail=""):
    if passed:
        print(f"  PASS: {label}")
    else:
        print(f"  FAIL: {label}")
        if detail:
            print(f"        {detail}")
    return passed


def main():
    passed = 0
    failed = 0

    fixture_path = ROOT / "tests" / "fixtures" / "echo_triage" / "issue_103_externally_authorized_ai_verification.md"
    if not fixture_path.exists():
        print("  SKIP: Fixture not found")
        return 0

    text = fixture_path.read_text(encoding="utf-8")
    intake = parse_submission("Issue #103 Test", text)

    # ── Test 1: Preflight passes (no hard/high issues) ──
    issues = preflight_check(text)
    hard_issues = [i for i in issues if i["severity"] in ("hard", "high")]
    if test("Fixture passes preflight (no hard/high issues)",
            len(hard_issues) == 0,
            f"hard_issues={[i['type'] for i in hard_issues]}"):
        passed += 1
    else:
        for i in hard_issues:
            print(f"    Hard issue: {i['type']} — {i['message']}")
        failed += 1

    # ── Test 2: No overclaim detected ──
    overclaim = detect_independence_overclaim_scoped(text, text)
    if test("No overclaim detected (properly disclaims independence)",
            overclaim is None):
        passed += 1
    else:
        failed += 1

    # ── Test 3: Exact field value assertions ──
    expected_fields = {
        "record_class": "ai_independent_verification",
        "verification_origin_class": "B2_external_human_authorized_ai_verification",
        "discovery_source": "D5_agent_referred_peer_agent",
        "verification_operator": "O2_external_ai_agent",
        "execution_independence": "E2_fresh_actions_with_sources",
        "responsibility_adoption": "R2_external_human_authorized_ai_only",
        "verification_level": "V2",
    }

    for field_name, expected_val in expected_fields.items():
        actual = get_field(intake.fields, field_name)
        if test(f"Field '{field_name}' == '{expected_val}'",
                actual.lower() == expected_val.lower() if actual else False,
                f"got='{actual}'"):
            passed += 1
        else:
            failed += 1

    # ── Test 4: Exact boolean field assertions ──
    expected_bools = {
        "counts_as_ai_independent_verification": True,
        "counts_as_formal_human_institutional_attestation": False,
        "external_human_authorized_execution": True,
        "external_human_signed_or_adopted_final_report": False,
        "fresh_actions_performed": True,
        "method_reproducible": True,
        "authority_boundary_preserved": True,
    }

    for field_name, expected_val in expected_bools.items():
        actual = get_bool_field(intake.fields, field_name)
        if test(f"Bool field '{field_name}' == {expected_val}",
                actual is expected_val,
                f"got={actual}"):
            passed += 1
        else:
            failed += 1

    # ── Test 5: solicitation_status contains required values ──
    sol_status = get_field(intake.fields, "solicitation_status")
    has_s2 = "S2" in sol_status if sol_status else False
    has_s3 = "S3" in sol_status if sol_status else False
    if test("solicitation_status contains S2 and S3",
            has_s2 and has_s3,
            f"got='{sol_status}'"):
        passed += 1
    else:
        failed += 1

    # ── Test 6: Delegation chain present ──
    chain = get_field(intake.fields, "delegation_chain")
    if test("Delegation chain detected",
            bool(chain) and "human" in chain.lower() and "agent" in chain.lower()):
        passed += 1
    else:
        failed += 1

    # ── Test 7: Integrity declaration with machine fields ──
    decl_strength = get_field(intake.fields, "declaration_strength")
    solemn = get_bool_field(intake.fields, "solemn_declaration_present")
    no_fab = get_bool_field(intake.fields, "no_fabricated_evidence")
    if test("Integrity declaration has machine fields",
            decl_strength == "strongest_available" and solemn is True and no_fab is True,
            f"strength={decl_strength}, solemn={solemn}, no_fab={no_fab}"):
        passed += 1
    else:
        failed += 1

    # ── Test 8: V2 level (not V3) ──
    if test("Verification level is V2 (not V3)",
            get_field(intake.fields, "verification_level").upper() == "V2"):
        passed += 1
    else:
        failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
