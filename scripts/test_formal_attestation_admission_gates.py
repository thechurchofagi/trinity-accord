#!/usr/bin/env python3
"""
Test: External witness admission gates (legacy: formal attestation admission gates).
TA-REDTEAM-2026-003 — positive-gate regression tests.

Verifies that the validator and homepage helper correctly reject
weak, under-specified, human-solicited, or overclaiming records.

Note: formal_attestation is legacy terminology. External witness records
are evidence provenance only, not the project's highest status.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_independent_attestation_index import validate_formal_record
from generate_public_home_status import is_formal_independent_attestation_index_record


def make_valid_v3():
    """Minimal valid V3 formal record."""
    return {
        "id": "formal-positive-control-v3",
        "type": "independent_verification_report",
        "source": "External verifier",
        "date": "2026-05-10",
        "summary": "Independent V3 hash verification with limitations.",
        "verification_level_if_any": "V3",
        "limitations": ["No physical inspection.", "No V4 script audit."],
        "url_or_archive": "verification-reports/formal-positive-control-v3.md",
        "hash_if_available": "a" * 64,
        "report_hash": "b" * 64,
        "boundary_preserved": True,
        "counts_as_independent_attestation": True,
        "verification_status": "accepted",
        "verifier_identity_or_role": "external verifier",
        "independence_class": "unsolicited_independent",
        "evidence_summary": "SHA-256 hash comparison of one artifact.",
        "accepted_by": ["reviewer-1", "reviewer-2"],
    }


def test(label, record, expect_valid):
    """Test a record against both validator and homepage helper."""
    errors = validate_formal_record(record, "test")
    validator_ok = len(errors) == 0
    homepage_ok = is_formal_independent_attestation_index_record(record)

    v_pass = validator_ok == expect_valid
    h_pass = homepage_ok == expect_valid

    if v_pass and h_pass:
        print(f"  PASS: {label}")
        return True
    else:
        print(f"  FAIL: {label}")
        if not v_pass:
            print(f"    validator: expected {'valid' if expect_valid else 'invalid'}, got {'valid' if validator_ok else 'invalid'}: {errors}")
        if not h_pass:
            print(f"    homepage: expected {expect_valid}, got {homepage_ok}")
        return False


def main():
    passed = 0
    failed = 0
    v3 = make_valid_v3()

    # ── Positive controls ──
    if test("valid V3 positive control", v3, True):
        passed += 1
    else:
        failed += 1

    # ── Under-specified ──
    if test("under-specified (only type+summary)",
            {"id": "x", "type": "independent_verification_report", "summary": "Done."},
            False):
        passed += 1
    else:
        failed += 1

    # ── Missing boundary_preserved ──
    r = {**v3}
    del r["boundary_preserved"]
    if test("missing boundary_preserved", r, False):
        passed += 1
    else:
        failed += 1

    # ── Missing counts_as_independent_attestation ──
    r = {**v3}
    del r["counts_as_independent_attestation"]
    if test("missing counts_as_independent_attestation", r, False):
        passed += 1
    else:
        failed += 1

    # ── boundary_preserved = False ──
    if test("boundary_preserved=False", {**v3, "boundary_preserved": False}, False):
        passed += 1
    else:
        failed += 1

    # ── counts_as = False ──
    if test("counts_as=False", {**v3, "counts_as_independent_attestation": False}, False):
        passed += 1
    else:
        failed += 1

    # ── Disallowed independence classes ──
    for cls in ["human_solicited_agent_response", "self_reported", "maintainer_submitted",
                "test_record", "legacy", "unknown"]:
        if test(f"disallowed independence_class={cls}",
                {**v3, "independence_class": cls}, False):
            passed += 1
        else:
            failed += 1

    # ── Missing limitations ──
    r = {**v3}
    del r["limitations"]
    if test("missing limitations", r, False):
        passed += 1
    else:
        failed += 1

    # ── Empty limitations ──
    if test("empty limitations list", {**v3, "limitations": []}, False):
        passed += 1
    else:
        failed += 1

    # ── Missing verifier ──
    r = {**v3}
    del r["verifier_identity_or_role"]
    if test("missing verifier_identity_or_role", r, False):
        passed += 1
    else:
        failed += 1

    # ── Missing accepted_by ──
    r = {**v3}
    del r["accepted_by"]
    if test("missing accepted_by", r, False):
        passed += 1
    else:
        failed += 1

    # ── accepted_by with 1 reviewer ──
    if test("accepted_by with 1 reviewer", {**v3, "accepted_by": ["solo"]}, False):
        passed += 1
    else:
        failed += 1

    # ── Missing report_hash for V3 ──
    r = {**v3}
    del r["report_hash"]
    if test("V3 missing report_hash", r, False):
        passed += 1
    else:
        failed += 1

    # ── V3 missing evidence_summary and linked_verification_report ──
    r = {**v3}
    del r["evidence_summary"]
    if test("V3 missing evidence_summary/linked_report", r, False):
        passed += 1
    else:
        failed += 1

    # ── V8 no claim gate ──
    r = {**v3, "verification_level_if_any": "V8"}
    if test("V8 missing claim_gate_result", r, False):
        passed += 1
    else:
        failed += 1

    # ── V8 complete claim gate ──
    v8 = {**v3, "verification_level_if_any": "V8",
          "claim_gate_result": {
              "allowed_protocol_level": "V8",
              "can_build_verification_report": True,
              "source_report_hash": "c" * 64,
              "core_baseline_satisfied": True,
              "high_path_satisfied": True,
          }}
    if test("V8 complete claim gate", v8, True):
        passed += 1
    else:
        failed += 1

    # ── V1 with hash_if_available (no report_hash needed) ──
    v1 = {**v3, "verification_level_if_any": "V1"}
    del v1["report_hash"]
    del v1["evidence_summary"]
    v1["hash_if_available"] = "a" * 64
    if test("V1 with hash_if_available", v1, True):
        passed += 1
    else:
        failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    if failed > 0:
        print("FORMAL_ATTESTATION_ADMISSION_GATES_FAIL")
        sys.exit(1)
    print("FORMAL_ATTESTATION_ADMISSION_GATES_OK")


if __name__ == "__main__":
    main()
