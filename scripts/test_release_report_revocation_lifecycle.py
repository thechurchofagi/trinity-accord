#!/usr/bin/env python3
"""Test release report revocation/supersession lifecycle (TA-REDTEAM-2026-012)."""
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from validate_verify_release_report import validate_report, make_valid_report


def main():
    passed = 0
    failed = 0

    def check(label, report, expect_errors_contain=None):
        nonlocal passed, failed
        errs = validate_report(report)
        if expect_errors_contain:
            if any(expect_errors_contain in e for e in errs):
                print(f"  PASS: {label}")
                passed += 1
            else:
                print(f"  FAIL: {label} — expected error containing '{expect_errors_contain}', got: {errs}")
                failed += 1
        else:
            if len(errs) == 0:
                print(f"  PASS: {label}")
                passed += 1
            else:
                print(f"  FAIL: {label} — expected no errors, got: {errs}")
                failed += 1

    # 1. PASS current report accepted
    r = make_valid_report()
    r["report_status"] = "current"
    r["is_current"] = True
    r["historical_report_only"] = False
    check("PASS current report accepted", r)

    # 2. PASS report missing report_status (lifecycle required = rejected)
    r = make_valid_report()
    del r["report_status"]
    check("PASS report missing lifecycle fields rejected", r, "report_status")

    # 3. revoked PASS report with is_current=true rejected
    r = make_valid_report()
    r["report_status"] = "revoked"
    r["is_current"] = True
    r["historical_report_only"] = True
    r["revocation_reason"] = "Compromised."
    check("revoked PASS report with is_current=true rejected", r, "PASS")

    # 4. revoked report missing revocation_reason rejected
    r = make_valid_report()
    r["status"] = "FAIL"
    r["errors"] = [{"type": "test"}]
    r["report_status"] = "revoked"
    r["is_current"] = False
    r["historical_report_only"] = True
    check("revoked report missing revocation_reason rejected", r, "revocation_reason")

    # 5. superseded report missing superseded_by rejected
    r = make_valid_report()
    r["status"] = "FAIL"
    r["errors"] = [{"type": "test"}]
    r["report_status"] = "superseded"
    r["is_current"] = False
    r["historical_report_only"] = True
    check("superseded report missing superseded_by rejected", r, "supersession_reason")

    # 6. invalidated report missing invalidation_reason rejected
    r = make_valid_report()
    r["status"] = "FAIL"
    r["errors"] = [{"type": "test"}]
    r["report_status"] = "invalidated"
    r["is_current"] = False
    r["historical_report_only"] = True
    check("invalidated report missing invalidation_reason rejected", r, "invalidation_reason")

    # 7. historical_report_only must be true for non-current
    r = make_valid_report()
    r["status"] = "FAIL"
    r["errors"] = [{"type": "test"}]
    r["report_status"] = "historical"
    r["is_current"] = False
    r["historical_report_only"] = False
    check("historical_report_only must be true for non-current", r, "historical_report_only")

    # 8. Static source check: verify-release-assets.mjs contains lifecycle fields
    generator_path = os.path.join(ROOT, "scripts", "verify-release-assets.mjs")
    with open(generator_path, encoding="utf-8") as f:
        generator_text = f.read()
    for token in ["report_status", "is_current", "historical_report_only", "current_status_url", "corrections_index_url"]:
        if token in generator_text:
            print(f"  PASS: verify-release-assets.mjs contains {token}")
            passed += 1
        else:
            print(f"  FAIL: verify-release-assets.mjs missing {token}")
            failed += 1

    print(f"\n{'=' * 50}")
    print(f"test_release_report_revocation_lifecycle: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
