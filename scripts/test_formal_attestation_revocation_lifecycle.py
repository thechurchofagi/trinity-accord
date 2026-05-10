#!/usr/bin/env python3
"""Test formal attestation revocation/supersession lifecycle (TA-REDTEAM-2026-012)."""
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from validate_independent_attestation_index import validate_formal_record, is_current_formal_record


def main():
    passed = 0
    failed = 0

    def check(label, record, expect_valid, expect_current=None):
        nonlocal passed, failed
        errs = validate_formal_record(record, "test")
        valid = len(errs) == 0

        if expect_current is not None:
            actual_current = is_current_formal_record(record)
            if actual_current != expect_current:
                print(f"  FAIL: {label} — expected is_current={expect_current}, got {actual_current}")
                failed += 1
                return

        if valid != expect_valid:
            print(f"  FAIL: {label} — expected {'valid' if expect_valid else 'invalid'}, "
                  f"got {'valid' if valid else 'invalid'}: {errs}")
            failed += 1
        else:
            print(f"  PASS: {label}")
            passed += 1

    base_record = {
        "id": "test-record", "type": "independent_verification_report",
        "source": "External", "date": "2026-05-10",
        "summary": "Test verification.", "verification_level_if_any": "V3",
        "limitations": ["No physical inspection."],
        "url_or_archive": "reports/v3.md", "report_hash": "a" * 64,
        "boundary_preserved": True, "counts_as_independent_attestation": True,
        "verification_status": "accepted",
        "verifier_identity_or_role": "external verifier",
        "independence_class": "unsolicited_independent",
        "evidence_summary": "Hash comparison.",
        "accepted_by": ["reviewer-1", "reviewer-2"],
    }

    # 1. Current accepted record counts
    current = {**base_record, "record_lifecycle_status": "current", "is_current": True, "historical_record_only": False}
    check("current accepted record counts", current, True, expect_current=True)

    # 2. Revoked record does not count
    revoked = {**base_record, "record_lifecycle_status": "revoked", "is_current": False,
               "historical_record_only": True, "counts_as_independent_attestation": False,
               "revoked_at": "2026-05-10", "revocation_reason": "Compromised."}
    check("revoked record does not count", revoked, True, expect_current=False)

    # 3. Revoked record with counts_as_independent_attestation=true rejected
    revoked_bad = {**base_record, "record_lifecycle_status": "revoked", "is_current": False,
                   "historical_record_only": True, "counts_as_independent_attestation": True,
                   "revoked_at": "2026-05-10", "revocation_reason": "Compromised."}
    check("revoked record with counts_as=true rejected", revoked_bad, False)

    # 4. Revoked record missing revocation_reason rejected
    revoked_no_reason = {**base_record, "record_lifecycle_status": "revoked", "is_current": False,
                         "historical_record_only": True, "counts_as_independent_attestation": False,
                         "revoked_at": "2026-05-10"}
    check("revoked record missing revocation_reason rejected", revoked_no_reason, False)

    # 5. Invalidated record missing invalidation_reason rejected
    invalidated_no_reason = {**base_record, "record_lifecycle_status": "invalidated", "is_current": False,
                             "historical_record_only": True, "counts_as_independent_attestation": False,
                             "invalidated_at": "2026-05-10"}
    check("invalidated record missing invalidation_reason rejected", invalidated_no_reason, False)

    # 6. Superseded record missing superseded_by rejected
    superseded_no_by = {**base_record, "record_lifecycle_status": "superseded", "is_current": False,
                        "historical_record_only": True, "counts_as_independent_attestation": False,
                        "superseded_at": "2026-05-10"}
    check("superseded record missing superseded_by rejected", superseded_no_by, False)

    # 7. Superseded record does not count
    superseded = {**base_record, "record_lifecycle_status": "superseded", "is_current": False,
                  "historical_record_only": True, "counts_as_independent_attestation": False,
                  "superseded_at": "2026-05-10", "superseded_by": "record-new",
                  "supersession_reason": "New evidence."}
    check("superseded record does not count", superseded, True, expect_current=False)

    # 8. Historical_only record does not count
    historical = {**base_record, "record_lifecycle_status": "historical_only", "is_current": False,
                  "historical_record_only": True, "counts_as_independent_attestation": False}
    check("historical_only record does not count", historical, True, expect_current=False)

    # 9. Homepage formal count ignores revoked/superseded records
    # Verify is_current_formal_record returns False for revoked
    revoked_record = {**base_record, "record_lifecycle_status": "revoked", "is_current": False,
                      "historical_record_only": True, "counts_as_independent_attestation": False,
                      "revoked_at": "2026-05-10", "revocation_reason": "Compromised."}
    if is_current_formal_record(revoked_record):
        print("  FAIL: homepage formal count should ignore revoked records")
        failed += 1
    else:
        print("  PASS: homepage formal count ignores revoked records")
        passed += 1

    # 10. Current record missing is_current=true rejected
    no_current = {**base_record, "record_lifecycle_status": "current", "is_current": False,
                  "historical_record_only": False}
    check("current record missing is_current=true rejected", no_current, False)

    print(f"\n{'=' * 50}")
    print(f"test_formal_attestation_revocation_lifecycle: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
