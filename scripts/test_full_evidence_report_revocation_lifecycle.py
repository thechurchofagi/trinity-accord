#!/usr/bin/env python3
"""Test full evidence chain report revocation/supersession lifecycle (TA-REDTEAM-2026-012)."""
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from validate_full_evidence_chain_audit import validate_report


def make_valid_report():
    return {
        "schema": "trinity-accord.full-evidence-chain-audit.v1",
        "generated_at": "2026-05-10T00:00:00Z",
        "overall_status": "PASS",
        "verification_scope": "full_evidence_chain_required_links",
        "required_chains": {
            "dag_digest_chain": {"required": True, "status": "PASS"},
            "btc_signature_coverage": {"required": True, "status": "PASS"},
            "eth_witness_coverage": {"required": True, "status": "PASS"},
            "bitcoin_tx_anchor": {"required": True, "status": "PASS"},
            "ots_time_anchor": {"required": True, "status": "PASS"},
        },
        "errors": [],
        "warnings": [],
        "limitations": ["ci-api OTS mode uses public Bitcoin APIs"],
        "does_not_prove": ["human independent attestation"],
        "chain_d2": {
            "ots_verification_mode": "ci-api",
            "fullnode_independent_verification": False,
        },
    }


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

    # 2. PASS report without lifecycle fields accepted
    r = make_valid_report()
    check("PASS report without lifecycle fields accepted", r)

    # 3. revoked PASS report with is_current=true rejected
    r = make_valid_report()
    r["report_status"] = "revoked"
    r["is_current"] = True
    r["historical_report_only"] = True
    r["revocation_reason"] = "Compromised."
    check("revoked PASS report with is_current=true rejected", r, "PASS")

    # 4. revoked report missing revocation_reason rejected
    r = make_valid_report()
    r["overall_status"] = "FAIL"
    r["errors"] = ["test"]
    r["report_status"] = "revoked"
    r["is_current"] = False
    r["historical_report_only"] = True
    check("revoked report missing revocation_reason rejected", r, "revocation_reason")

    # 5. superseded report missing supersession_reason rejected
    r = make_valid_report()
    r["overall_status"] = "FAIL"
    r["errors"] = ["test"]
    r["report_status"] = "superseded"
    r["is_current"] = False
    r["historical_report_only"] = True
    check("superseded report missing supersession_reason rejected", r, "supersession_reason")

    # 6. invalidated report missing invalidation_reason rejected
    r = make_valid_report()
    r["overall_status"] = "FAIL"
    r["errors"] = ["test"]
    r["report_status"] = "invalidated"
    r["is_current"] = False
    r["historical_report_only"] = True
    check("invalidated report missing invalidation_reason rejected", r, "invalidation_reason")

    # 7. historical_report_only must be true for non-current
    r = make_valid_report()
    r["overall_status"] = "FAIL"
    r["errors"] = ["test"]
    r["report_status"] = "historical"
    r["is_current"] = False
    r["historical_report_only"] = False
    check("historical_report_only must be true for non-current", r, "historical_report_only")

    print(f"\n{'=' * 50}")
    print(f"test_full_evidence_report_revocation_lifecycle: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
