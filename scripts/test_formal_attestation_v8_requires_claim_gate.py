#!/usr/bin/env python3
"""
Test: V8 formal attestation requires Claim Gate output.
TA-REDTEAM-2026-003 — V8-specific admission gate tests.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_independent_attestation_index import validate_formal_record
from generate_public_home_status import is_formal_independent_attestation_index_record


def make_valid_v8():
    """Minimal valid V8 formal record."""
    return {
        "id": "formal-v8", "type": "independent_verification_report",
        "source": "External verifier", "date": "2026-05-10",
        "summary": "Full V8 protocol verification.",
        "verification_level_if_any": "V8",
        "limitations": ["No onsite physical inspection."],
        "url_or_archive": "verification-reports/formal-v8.md",
        "report_hash": "a" * 64,
        "boundary_preserved": True,
        "counts_as_independent_attestation": True,
        "verification_status": "accepted",
        "verifier_identity_or_role": "external verifier",
        "independence_class": "unsolicited_independent",
        "evidence_summary": "Full protocol V8 verification with Claim Gate.",
        "accepted_by": ["reviewer-1", "reviewer-2"],
        "claim_gate_result": {
            "allowed_protocol_level": "V8",
            "can_build_verification_report": True,
            "source_report_hash": "b" * 64,
            "core_baseline_satisfied": True,
            "high_path_satisfied": True,
        },
    }


def test(label, record, expect_valid):
    errors = validate_formal_record(record, "test")
    ok = (len(errors) == 0) == expect_valid
    homepage = is_formal_independent_attestation_index_record(record)
    h_ok = homepage == expect_valid

    if ok and h_ok:
        print(f"  PASS: {label}")
        return True
    else:
        print(f"  FAIL: {label}")
        if not ok:
            print(f"    validator: expected {'valid' if expect_valid else 'invalid'}, errors={errors}")
        if not h_ok:
            print(f"    homepage: expected {expect_valid}, got {homepage}")
        return False


def main():
    passed = 0
    failed = 0
    v8 = make_valid_v8()

    # ── Positive control ──
    if test("V8 complete positive control", v8, True):
        passed += 1
    else:
        failed += 1

    # ── V8 no claim_gate_result ──
    r = {**v8}
    del r["claim_gate_result"]
    if test("V8 missing claim_gate_result", r, False):
        passed += 1
    else:
        failed += 1

    # ── V8 allowed_protocol_level != V8 ──
    if test("V8 allowed_protocol_level=V7",
            {**v8, "claim_gate_result": {**v8["claim_gate_result"], "allowed_protocol_level": "V7"}},
            False):
        passed += 1
    else:
        failed += 1

    # ── V8 can_build_verification_report false ──
    if test("V8 can_build_verification_report=false",
            {**v8, "claim_gate_result": {**v8["claim_gate_result"], "can_build_verification_report": False}},
            False):
        passed += 1
    else:
        failed += 1

    # ── V8 core_baseline_satisfied false ──
    if test("V8 core_baseline_satisfied=false",
            {**v8, "claim_gate_result": {**v8["claim_gate_result"], "core_baseline_satisfied": False}},
            False):
        passed += 1
    else:
        failed += 1

    # ── V8 core_baseline_satisfied missing ──
    cg = {**v8["claim_gate_result"]}
    del cg["core_baseline_satisfied"]
    if test("V8 core_baseline_satisfied missing", {**v8, "claim_gate_result": cg}, False):
        passed += 1
    else:
        failed += 1

    # ── V8 high_path_satisfied false ──
    if test("V8 high_path_satisfied=false",
            {**v8, "claim_gate_result": {**v8["claim_gate_result"], "high_path_satisfied": False}},
            False):
        passed += 1
    else:
        failed += 1

    # ── V8 no source_report_hash or claim_gate_report_hash ──
    cg = {**v8["claim_gate_result"]}
    del cg["source_report_hash"]
    if test("V8 no source_report_hash/claim_gate_report_hash",
            {**v8, "claim_gate_result": cg}, False):
        passed += 1
    else:
        failed += 1

    # ── V8 with claim_gate_report_hash instead of source_report_hash ──
    cg = {**v8["claim_gate_result"]}
    del cg["source_report_hash"]
    cg["claim_gate_report_hash"] = "c" * 64
    if test("V8 with claim_gate_report_hash (alt)", {**v8, "claim_gate_result": cg}, True):
        passed += 1
    else:
        failed += 1

    # ── V8 claim_gate_result not a dict ──
    if test("V8 claim_gate_result=string", {**v8, "claim_gate_result": "invalid"}, False):
        passed += 1
    else:
        failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    if failed > 0:
        print("FORMAL_ATTESTATION_V8_CLAIM_GATE_FAIL")
        sys.exit(1)
    print("FORMAL_ATTESTATION_V8_CLAIM_GATE_OK")


if __name__ == "__main__":
    main()
