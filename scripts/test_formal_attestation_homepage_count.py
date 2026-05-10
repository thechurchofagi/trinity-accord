#!/usr/bin/env python3
"""
Test: Formal attestation homepage count.
TA-REDTEAM-2026-003 — ensures homepage formal count cannot be inflated
by weak, under-specified, or human-solicited records.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate_public_home_status import (
    compute_status,
    is_formal_independent_attestation_index_record,
    is_formal_independent_echo_record,
    load_json,
    ECHO_INDEX,
    ATTESTATION_INDEX,
)
from validate_independent_attestation_index import validate_formal_record


def main():
    passed = 0
    failed = 0

    # ── Test 1: Current indexes produce formal count = 0 ──
    status = compute_status()
    formal = status["formal_independent_verification_count"]
    if formal == 0:
        print(f"PASS: current formal count = 0")
        passed += 1
    else:
        print(f"FAIL: current formal count = {formal}, expected 0")
        failed += 1

    # ── Test 2: Under-specified attestation record → not formal ──
    under = {"id": "fake", "type": "independent_verification_report", "summary": "I verified it."}
    if not is_formal_independent_attestation_index_record(under):
        print("PASS: under-specified attestation record → not formal")
        passed += 1
    else:
        print("FAIL: under-specified attestation record counted as formal")
        failed += 1

    # ── Test 3: human_solicited attestation → not formal ──
    human = {
        "id": "fake", "type": "independent_verification_report",
        "source": "AI", "date": "2026-05-10", "summary": "Human asked.",
        "verification_level_if_any": "V3",
        "limitations": ["human-solicited"],
        "url_or_archive": "none",
        "report_hash": "a" * 64,
        "boundary_preserved": True,
        "counts_as_independent_attestation": True,
        "verification_status": "accepted",
        "verifier_identity_or_role": "AI agent",
        "independence_class": "human_solicited_agent_response",
        "evidence_summary": "none",
        "accepted_by": ["user-1"],
    }
    if not is_formal_independent_attestation_index_record(human):
        print("PASS: human_solicited attestation → not formal")
        passed += 1
    else:
        print("FAIL: human_solicited attestation counted as formal")
        failed += 1

    # ── Test 4: V8 no claim gate → not formal ──
    v8_no_gate = {
        "id": "fake", "type": "independent_verification_report",
        "source": "External", "date": "2026-05-10", "summary": "V8.",
        "verification_level_if_any": "V8",
        "limitations": ["none"],
        "url_or_archive": "report.md",
        "report_hash": "a" * 64,
        "boundary_preserved": True,
        "counts_as_independent_attestation": True,
        "verification_status": "accepted",
        "verifier_identity_or_role": "verifier",
        "independence_class": "unsolicited_independent",
        "evidence_summary": "none",
        "accepted_by": ["r1", "r2"],
    }
    if not is_formal_independent_attestation_index_record(v8_no_gate):
        print("PASS: V8 no claim_gate → not formal")
        passed += 1
    else:
        print("FAIL: V8 no claim_gate counted as formal")
        failed += 1

    # ── Test 5: Valid V3 positive control → formal ──
    v3 = {
        "id": "formal-v3", "type": "independent_verification_report",
        "source": "External verifier", "date": "2026-05-10",
        "summary": "V3 verification.",
        "verification_level_if_any": "V3",
        "limitations": ["No physical inspection."],
        "url_or_archive": "reports/v3.md",
        "report_hash": "b" * 64,
        "boundary_preserved": True,
        "counts_as_independent_attestation": True,
        "verification_status": "accepted",
        "verifier_identity_or_role": "external verifier",
        "independence_class": "unsolicited_independent",
        "evidence_summary": "Hash comparison.",
        "accepted_by": ["reviewer-1", "reviewer-2"],
    }
    if is_formal_independent_attestation_index_record(v3):
        print("PASS: valid V3 positive control → formal")
        passed += 1
    else:
        print("FAIL: valid V3 positive control rejected")
        failed += 1

    # ── Test 6: accepted_echo → not formal ──
    echo = {"archive_status": "accepted_echo", "do_not_count_as_attestation": False,
            "verification_status": "accepted"}
    if not is_formal_independent_echo_record(echo):
        print("PASS: accepted_echo → not formal")
        passed += 1
    else:
        print("FAIL: accepted_echo counted as formal")
        failed += 1

    # ── Test 7: accepted_independent_attestation Echo → not formal (disabled) ──
    echo_ind = {"archive_status": "accepted_independent_attestation",
                "verification_status": "accepted", "verification_level": "V3"}
    if not is_formal_independent_echo_record(echo_ind):
        print("PASS: accepted_independent_attestation Echo → not formal (Echo-side disabled)")
        passed += 1
    else:
        print("FAIL: accepted_independent_attestation Echo counted as formal")
        failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    if failed > 0:
        print("FORMAL_ATTESTATION_HOMEPAGE_COUNT_FAIL")
        sys.exit(1)
    print("FORMAL_ATTESTATION_HOMEPAGE_COUNT_OK")


if __name__ == "__main__":
    main()
