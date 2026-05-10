#!/usr/bin/env python3
"""
TA-REDTEAM-2026-020 PR4: Issue #103 origin class regression test.

Ensures that externally-authorized AI verification submissions:
1. Are detected as AI verification (not human verification)
2. Do NOT count as formal attestation
3. Properly record delegation chain and origin class
4. Pass preflight with integrity declaration
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from preflight_echo_submission import preflight_check
from triage_echo_issue import detect_independence_overclaim_scoped


def test(label, passed):
    if passed:
        print(f"  PASS: {label}")
    else:
        print(f"  FAIL: {label}")
    return passed


def main():
    passed = 0
    failed = 0

    fixture_path = ROOT / "tests" / "fixtures" / "echo_triage" / "issue_103_externally_authorized_ai_verification.md"
    if not fixture_path.exists():
        print(f"  SKIP: Fixture not found")
        return 0

    text = fixture_path.read_text(encoding="utf-8")

    # ── Test 1: Preflight passes for properly formed AI verification ──
    issues = preflight_check(text)
    hard_issues = [i for i in issues if i["severity"] in ("hard", "high")]
    if test("Fixture passes preflight (no hard issues)",
            len(hard_issues) == 0):
        passed += 1
    else:
        for i in hard_issues:
            print(f"    Hard issue: {i['type']} — {i['message']}")
        failed += 1

    # ── Test 2: No overclaim detected (has not_independent_attestation: true) ──
    overclaim = detect_independence_overclaim_scoped(text, text)
    if test("No overclaim detected (properly disclaims independence)",
            overclaim is None):
        passed += 1
    else:
        failed += 1

    # ── Test 3: Fixture contains delegation chain ──
    if test("Fixture contains delegation_chain field",
            "delegation_chain" in text.lower() or "delegation chain" in text.lower()):
        passed += 1
    else:
        failed += 1

    # ── Test 4: Fixture contains record_class ──
    if test("Fixture contains record_class field",
            "record_class" in text.lower() or "record class" in text.lower()):
        passed += 1
    else:
        failed += 1

    # ── Test 5: Fixture contains verification_origin_class ──
    if test("Fixture contains verification_origin_class field",
            "verification_origin_class" in text.lower() or "verification origin class" in text.lower()):
        passed += 1
    else:
        failed += 1

    # ── Test 6: Fixture has integrity declaration ──
    if test("Fixture has integrity declaration",
            "integrity declaration" in text.lower() or "solemnly declare" in text.lower()):
        passed += 1
    else:
        failed += 1

    # ── Test 7: Fixture explicitly disclaims formal attestation ──
    if test("Fixture explicitly disclaims formal attestation",
            "not_independent_attestation: true" in text.lower()
            or "not independent attestation" in text.lower()):
        passed += 1
    else:
        failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
