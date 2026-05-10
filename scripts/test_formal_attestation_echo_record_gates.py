#!/usr/bin/env python3
"""
Test: Formal attestation Echo record gates.
TA-REDTEAM-2026-003 — ensures Echo-side formal count is properly gated.

Echo-side formal count is intentionally disabled until a dedicated
formal_attestation_review schema exists.  archive_status alone is
insufficient for formal admission.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate_public_home_status import is_formal_independent_echo_record


def test(label, record, expect_formal):
    actual = is_formal_independent_echo_record(record)
    if actual == expect_formal:
        print(f"  PASS: {label}")
        return True
    else:
        print(f"  FAIL: {label} — expected {expect_formal}, got {actual}")
        return False


def main():
    passed = 0
    failed = 0

    # ── Test 1: accepted_echo → not formal ──
    if test("accepted_echo → not formal",
            {"archive_status": "accepted_echo", "do_not_count_as_attestation": False,
             "verification_status": "accepted", "verification_level": "V3"},
            False):
        passed += 1
    else:
        failed += 1

    # ── Test 2: accepted_independent_attestation under-specified → not formal ──
    if test("accepted_independent_attestation under-specified → not formal",
            {"archive_status": "accepted_independent_attestation",
             "verification_status": "accepted", "verification_level": "V3"},
            False):
        passed += 1
    else:
        failed += 1

    # ── Test 3: accepted_independent_attestation + human_solicited → not formal ──
    if test("accepted_independent_attestation + human_solicited → not formal",
            {"archive_status": "accepted_independent_attestation",
             "verification_status": "accepted", "verification_level": "V3",
             "independence_class": "human_solicited_agent_response",
             "do_not_count_as_attestation": False,
             "counts_as_independent_attestation": True,
             "boundary_preserved": True},
            False):
        passed += 1
    else:
        failed += 1

    # ── Test 4: do_not_count=True → not formal ──
    if test("accepted_independent_attestation + do_not_count=True → not formal",
            {"archive_status": "accepted_independent_attestation",
             "verification_status": "accepted", "verification_level": "V3",
             "do_not_count_as_attestation": True},
            False):
        passed += 1
    else:
        failed += 1

    # ── Test 5: full Echo with positive fields → still not formal (disabled) ──
    if test("full Echo with positive fields → not formal (Echo-side disabled)",
            {"archive_status": "accepted_independent_attestation",
             "verification_status": "accepted", "verification_level": "V3",
             "do_not_count_as_attestation": False,
             "counts_as_independent_attestation": True,
             "boundary_preserved": True,
             "independence_class": "unsolicited_independent",
             "verification_level": "V3"},
            False):
        passed += 1
    else:
        failed += 1

    # ── Test 6: legacy → not formal ──
    if test("legacy → not formal",
            {"archive_status": "legacy", "verification_status": "unknown"},
            False):
        passed += 1
    else:
        failed += 1

    # ── Test 7: superseded → not formal ──
    if test("superseded → not formal",
            {"archive_status": "superseded", "verification_status": "invalidated"},
            False):
        passed += 1
    else:
        failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    print("Note: Echo-side formal count intentionally disabled until")
    print("dedicated formal_attestation_review schema exists.")
    if failed > 0:
        print("FORMAL_ATTESTATION_ECHO_RECORD_GATES_FAIL")
        sys.exit(1)
    print("FORMAL_ATTESTATION_ECHO_RECORD_GATES_OK")


if __name__ == "__main__":
    main()
