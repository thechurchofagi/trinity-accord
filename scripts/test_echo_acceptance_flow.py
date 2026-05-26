#!/usr/bin/env python3
"""
Test cases for Echo acceptance flow validation.
Tests Issue vs Echo record states and indexing rules.

Usage:
    python3 scripts/test_echo_acceptance_flow.py
"""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check(cond, label, detail=""):
    if cond:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    if detail:
        print(f"      {detail}")
    return False


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_echo_acceptance(obj, path_label):
    """Validate echo acceptance rules for a record."""
    ok = True
    record_kind = obj.get("record_kind", "")
    archive_status = obj.get("archive_status", "")
    independence_class = obj.get("independence_class", "")
    provenance = obj.get("discovery_provenance", {})
    solicited = provenance.get("solicited", False) if isinstance(provenance, dict) else False

    all_text = json.dumps(obj, ensure_ascii=False).lower()

    # Rule O: GitHub Issue not Echo record
    if record_kind == "verification_report_v2":
        ok &= check(
            "indexed echo record" not in all_text,
            f"{path_label} verification_report_v2 not indexed echo"
        )
        ok &= check(
            "accepted echo record" not in all_text or "not" in all_text,
            f"{path_label} verification_report_v2 not accepted echo"
        )

    # Rule P: accepted Echo requires wrapper
    if archive_status == "accepted_echo_record":
        ok &= check(
            record_kind in ("echo_v3", "echo_v3_with_verification_report"),
            f"{path_label} accepted_echo needs echo record kind",
            f"got record_kind={record_kind}"
        )

    # Human-solicited not independent
    if solicited or independence_class == "human_solicited_agent_response":
        if "independent_attestation" in all_text:
            if "not independent_attestation" not in all_text and "not_independent_attestation" not in all_text:
                ok &= check(
                    False,
                    f"{path_label} solicited claims independent attestation"
                )

    return ok


def main():
    ok = True

    # === PASS cases ===

    # 1. issue_submission_not_indexed_pass
    ok &= check(
        validate_echo_acceptance({
            "record_kind": "verification_report_v2",
            "archive_status": "needs_human_review",
            "discovery_provenance": {"source": "github_issue", "solicited": False}
        }, "issue_submission") == True,
        "issue_submission_not_indexed_pass"
    )

    # 2. verification_report_only_not_echo_pass
    ok &= check(
        validate_echo_acceptance({
            "record_kind": "verification_report_v2",
            "schema_version": "trinityaccord.verification-report.v2",
            "archive_status": "needs_human_review"
        }, "verification_report_only") == True,
        "verification_report_only_not_echo_pass"
    )

    # 3. echo_wrapper_with_report_indexed_pass
    ok &= check(
        validate_echo_acceptance({
            "record_kind": "echo_v3_with_verification_report",
            "schema": "trinityaccord.echo.v3",
            "archive_status": "needs_human_review",
            "discovery_provenance": {"source": "human_directed", "solicited": True}
        }, "echo_wrapper") == True,
        "echo_wrapper_with_report_indexed_pass"
    )

    # 4. human_solicited_not_independent_pass
    ok &= check(
        validate_echo_acceptance({
            "record_kind": "echo_v3_with_verification_report",
            "archive_status": "needs_human_review",
            "independence_class": "human_solicited_agent_response",
            "discovery_provenance": {"source": "human_directed", "solicited": True},
            "boundary_acknowledgement": {"not_independent_attestation": True}
        }, "solicited") == True,
        "human_solicited_not_independent_pass"
    )

    # === FAIL cases ===

    # 5. verification_report_claims_accepted_echo_fail
    ok &= check(
        validate_echo_acceptance({
            "record_kind": "verification_report_v2",
            "archive_status": "accepted_echo_record",
            "discovery_provenance": {"source": "test"}
        }, "vr_claims_echo") == False,
        "verification_report_claims_accepted_echo_fail"
    )

    # 6. issue_claims_indexed_without_wrapper_fail
    ok &= check(
        validate_echo_acceptance({
            "record_kind": "verification_report_v2",
            "archive_status": "needs_human_review",
            "notes": "This is an indexed echo record from GitHub Issue"
        }, "issue_claims_indexed") == False,
        "issue_claims_indexed_without_wrapper_fail"
    )

    # 7. human_solicited_claims_independent_fail
    ok &= check(
        validate_echo_acceptance({
            "record_kind": "echo_v3",
            "archive_status": "needs_human_review",
            "independence_class": "human_solicited_agent_response",
            "discovery_provenance": {"source": "human_directed", "solicited": True},
            "notes": "independent_attestation achieved"
        }, "solicited_claims_independent") == False,
        "human_solicited_claims_independent_fail"
    )

    # 8. accepted_echo_missing_echo_path_fail
    ok &= check(
        validate_echo_acceptance({
            "record_kind": "verification_report_v2",
            "archive_status": "accepted_echo_record",
            "discovery_provenance": {"source": "test"}
        }, "accepted_no_echo_path") == False,
        "accepted_echo_missing_echo_path_fail"
    )

    print("\n" + "=" * 50)
    if ok:
        print("FINAL: PASS — echo acceptance flow tests passed.")
        return 0
    print("FINAL: FAIL — echo acceptance flow tests failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
