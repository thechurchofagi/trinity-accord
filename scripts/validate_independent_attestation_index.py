#!/usr/bin/env python3
"""
Validate independent-attestation-index.json formal admission gates.

Positive-gate validator: records must explicitly satisfy all requirements
to be counted as formal independent verification.

Usage:
    python3 scripts/validate_independent_attestation_index.py
    python3 scripts/validate_independent_attestation_index.py --index path/to/index.json
    python3 scripts/validate_independent_attestation_index.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX = ROOT / "api" / "independent-attestation-index.json"

SHA256_RE = re.compile(r"^[a-f0-9]{64}$", re.I)

VALID_LEVELS = {"V1", "V2", "V3", "V4", "V4+", "V5", "V6", "V7", "V8"}

DISALLOWED_INDEPENDENCE_CLASSES = {
    "human_solicited_agent_response",
    "self_reported",
    "maintainer_submitted",
    "maintainer_assisted",
    "test_record",
    "legacy",
    "unknown",
    "imported_public_commentary",
}

ALLOWED_INDEPENDENCE_CLASSES = {
    "unsolicited_independent",
    "solicited_independent_check",
    "institutional_third_party_attestation",
}

ACCEPTED_STATUSES = {
    "accepted",
    "formally_accepted",
    "accepted_independent_attestation",
}

LEVEL_ORDER = {
    "V1": 1, "V2": 2, "V3": 3, "V4": 4, "V4+": 4.5,
    "V5": 5, "V6": 6, "V7": 7, "V8": 8,
}


def is_sha256(value) -> bool:
    return isinstance(value, str) and SHA256_RE.fullmatch(value) is not None


def validate_formal_record(record: dict, path_label: str = "record") -> list[str]:
    """Validate a formal independent attestation record.

    Returns a list of error strings.  Empty list means valid.
    Positive-gate: every requirement must be explicitly satisfied.
    """
    errors: list[str] = []

    def require(cond: bool, msg: str):
        if not cond:
            errors.append(msg)

    # ── Type ──
    require(record.get("type") == "independent_verification_report",
            f"{path_label}: type must be independent_verification_report")

    # ── Positive flags (must be explicitly True, not just absent) ──
    require(record.get("counts_as_independent_attestation") is True,
            f"{path_label}: counts_as_independent_attestation must be true")

    require(record.get("boundary_preserved") is True,
            f"{path_label}: boundary_preserved must be true")

    # ── Verification status ──
    require(record.get("verification_status") in ACCEPTED_STATUSES,
            f"{path_label}: verification_status must be accepted/formally_accepted/accepted_independent_attestation")

    # ── Required non-empty string fields ──
    for field in ["id", "source", "date", "summary", "url_or_archive", "verifier_identity_or_role"]:
        require(isinstance(record.get(field), str) and record.get(field).strip(),
                f"{path_label}: missing non-empty {field}")

    # ── Limitations: non-empty list of non-empty strings ──
    limitations = record.get("limitations")
    require(isinstance(limitations, list) and len(limitations) >= 1
            and all(isinstance(x, str) and x.strip() for x in limitations),
            f"{path_label}: limitations must be non-empty list[str]")

    # ── Verification level ──
    level = record.get("verification_level_if_any")
    require(level in VALID_LEVELS,
            f"{path_label}: verification_level_if_any must be V1..V8")

    # ── Independence class ──
    independence = record.get("independence_class")
    require(independence in ALLOWED_INDEPENDENCE_CLASSES,
            f"{path_label}: independence_class must be one of {sorted(ALLOWED_INDEPENDENCE_CLASSES)}")
    require(independence not in DISALLOWED_INDEPENDENCE_CLASSES,
            f"{path_label}: disallowed independence_class: {independence}")

    # ── Accepted by: at least 2 reviewers ──
    accepted_by = record.get("accepted_by")
    require(isinstance(accepted_by, list) and len(accepted_by) >= 2
            and all(isinstance(x, str) and x.strip() for x in accepted_by),
            f"{path_label}: accepted_by must contain at least 2 reviewers")

    # ── Report hash ──
    report_hash = record.get("report_hash")
    hash_if_available = record.get("hash_if_available")
    require(is_sha256(report_hash) or is_sha256(hash_if_available),
            f"{path_label}: report_hash or hash_if_available must be valid 64-hex SHA-256")

    # ── V3+ additional requirements ──
    level_num = LEVEL_ORDER.get(level, 0)
    if level_num >= 3:
        require(is_sha256(report_hash),
                f"{path_label}: V3+ formal record requires report_hash (64-hex)")
        require(bool(record.get("evidence_summary") or record.get("linked_verification_report")),
                f"{path_label}: V3+ formal record requires evidence_summary or linked_verification_report")

    # ── V8 additional requirements ──
    if level == "V8":
        cg = record.get("claim_gate_result")
        require(isinstance(cg, dict),
                f"{path_label}: V8 requires claim_gate_result object")
        if isinstance(cg, dict):
            require(cg.get("allowed_protocol_level") == "V8",
                    f"{path_label}: V8 claim_gate_result.allowed_protocol_level must be V8")
            require(cg.get("can_build_verification_report") is True,
                    f"{path_label}: V8 claim_gate_result.can_build_verification_report must be true")
            require(cg.get("core_baseline_satisfied") is True,
                    f"{path_label}: V8 claim_gate_result.core_baseline_satisfied must be true")
            require(cg.get("high_path_satisfied") is True,
                    f"{path_label}: V8 claim_gate_result.high_path_satisfied must be true")
            require(is_sha256(cg.get("source_report_hash")) or is_sha256(cg.get("claim_gate_report_hash")),
                    f"{path_label}: V8 claim_gate_result requires source_report_hash or claim_gate_report_hash (64-hex)")

    return errors


def validate_index(index_path: str | Path) -> list[str]:
    """Validate all formal records in the independent attestation index."""
    obj = json.loads(Path(index_path).read_text(encoding="utf-8"))
    errors: list[str] = []

    records = obj.get("records", [])
    if not isinstance(records, list):
        return ["records must be a list"]

    for i, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"records[{i}] must be object")
            continue

        # Formal records must pass positive-gate validation
        if (record.get("type") == "independent_verification_report"
                or record.get("archive_status") == "accepted_independent_attestation"):
            errors.extend(validate_formal_record(record, f"records[{i}]"))
        else:
            # Non-formal types must explicitly opt out
            if record.get("counts_as_independent_attestation") is not False:
                errors.append(f"records[{i}]: non-formal record must set counts_as_independent_attestation=false")

    return errors


def run_self_test() -> bool:
    """Run built-in self-tests to verify validator correctness."""
    passed = 0
    failed = 0

    def check(label: str, record: dict, expect_valid: bool):
        nonlocal passed, failed
        errs = validate_formal_record(record, "test")
        ok = (len(errs) == 0) == expect_valid
        status = "PASS" if ok else "FAIL"
        if not ok:
            print(f"  {status}: {label} — expected {'valid' if expect_valid else 'invalid'}, "
                  f"got {'valid' if not errs else 'invalid'}: {errs}")
            failed += 1
        else:
            print(f"  {status}: {label}")
            passed += 1

    # Full valid V3 record
    valid_v3 = {
        "id": "test-v3", "type": "independent_verification_report",
        "source": "External", "date": "2026-05-10",
        "summary": "V3 verification.", "verification_level_if_any": "V3",
        "limitations": ["No physical inspection."],
        "url_or_archive": "reports/v3.md", "report_hash": "a" * 64,
        "boundary_preserved": True, "counts_as_independent_attestation": True,
        "verification_status": "accepted",
        "verifier_identity_or_role": "external verifier",
        "independence_class": "unsolicited_independent",
        "evidence_summary": "Hash comparison.",
        "accepted_by": ["reviewer-1", "reviewer-2"],
    }
    check("valid V3 record", valid_v3, True)

    # Under-specified
    check("under-specified (only type+summary)",
          {"id": "x", "type": "independent_verification_report", "summary": "Done."},
          False)

    # Missing boundary_preserved
    r = {**valid_v3, "boundary_preserved": None}
    del r["boundary_preserved"]
    check("missing boundary_preserved", r, False)

    # Missing counts_as
    r = {**valid_v3}
    del r["counts_as_independent_attestation"]
    check("missing counts_as_independent_attestation", r, False)

    # boundary_preserved = False
    check("boundary_preserved=False", {**valid_v3, "boundary_preserved": False}, False)

    # counts_as = False
    check("counts_as=False", {**valid_v3, "counts_as_independent_attestation": False}, False)

    # human_solicited
    check("human_solicited_agent_response",
          {**valid_v3, "independence_class": "human_solicited_agent_response"}, False)

    # self_reported
    check("self_reported",
          {**valid_v3, "independence_class": "self_reported"}, False)

    # V8 no claim gate
    valid_v8 = {**valid_v3, "verification_level_if_any": "V8",
                "claim_gate_result": {
                    "allowed_protocol_level": "V8",
                    "can_build_verification_report": True,
                    "source_report_hash": "b" * 64,
                    "core_baseline_satisfied": True,
                    "high_path_satisfied": True,
                }}
    check("V8 complete claim gate", valid_v8, True)

    # V8 missing claim gate
    r = {**valid_v3, "verification_level_if_any": "V8"}
    check("V8 missing claim_gate_result", r, False)

    # V8 incomplete claim gate
    check("V8 incomplete claim gate (no high_path)",
          {**valid_v8, "claim_gate_result": {**valid_v8["claim_gate_result"], "high_path_satisfied": False}},
          False)

    # Missing limitations
    r = {**valid_v3}
    del r["limitations"]
    check("missing limitations", r, False)

    # Empty limitations
    check("empty limitations list", {**valid_v3, "limitations": []}, False)

    # Missing verifier
    r = {**valid_v3}
    del r["verifier_identity_or_role"]
    check("missing verifier_identity_or_role", r, False)

    # Missing accepted_by
    r = {**valid_v3}
    del r["accepted_by"]
    check("missing accepted_by", r, False)

    # accepted_by with only 1
    check("accepted_by with 1 reviewer", {**valid_v3, "accepted_by": ["solo"]}, False)

    # Missing report_hash for V3
    r = {**valid_v3}
    del r["report_hash"]
    check("V3 missing report_hash (only hash_if_available)", {**r, "hash_if_available": "c" * 64}, False)

    # V1 with hash_if_available (no report_hash required)
    valid_v1 = {**valid_v3, "verification_level_if_any": "V1"}
    del valid_v1["report_hash"]
    valid_v1["hash_if_available"] = "a" * 64
    del valid_v1["evidence_summary"]
    check("V1 with hash_if_available (no report_hash needed)", valid_v1, True)

    print(f"\nSelf-test: {passed} passed, {failed} failed")
    return failed == 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate independent attestation index")
    ap.add_argument("--index", default=str(DEFAULT_INDEX))
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return 0 if run_self_test() else 1

    errors = validate_index(args.index)
    if errors:
        print("INDEPENDENT_ATTESTATION_INDEX_INVALID")
        for e in errors:
            print(f"FAIL: {e}")
        return 1

    print("INDEPENDENT_ATTESTATION_INDEX_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
