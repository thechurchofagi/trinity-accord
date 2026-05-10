#!/usr/bin/env python3
"""Validate FULL-EVIDENCE-CHAIN-AUDIT.json against schema and PASS invariants.

Usage:
  python3 scripts/validate_full_evidence_chain_audit.py --self-test
  python3 scripts/validate_full_evidence_chain_audit.py FULL-EVIDENCE-CHAIN-AUDIT.json
"""
import json, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VALID_REPORT_STATUSES = {"current", "historical", "superseded", "revoked", "invalidated"}
NON_CURRENT_REPORT_STATUSES = {"historical", "superseded", "revoked", "invalidated"}


def validate_report(report):
    errors = []

    # Schema
    if report.get("schema") != "trinity-accord.full-evidence-chain-audit.v1":
        errors.append(f"schema must be trinity-accord.full-evidence-chain-audit.v1, got: {report.get('schema')}")

    # overall_status
    status = report.get("overall_status")
    if status not in ("PASS", "FAIL"):
        errors.append(f"overall_status must be PASS or FAIL, got: {status}")

    # required_chains
    required_chains = report.get("required_chains")
    if not isinstance(required_chains, dict) or not required_chains:
        errors.append("required_chains must be non-empty object")

    # PASS invariants
    if status == "PASS":
        if report.get("errors"):
            errors.append(f"PASS report must have empty errors, got {len(report['errors'])} errors")
        for name, chain in (required_chains or {}).items():
            if chain.get("required") is True and chain.get("status") != "PASS":
                errors.append(f"PASS report has non-PASS required chain: {name} = {chain.get('status')}")

    # limitations / does_not_prove
    if not report.get("limitations"):
        errors.append("limitations required")
    if not report.get("does_not_prove"):
        errors.append("does_not_prove required")

    # ci-api / fullnode invariant
    # Check nested chain_d2 or top-level ots fields
    ots = report.get("ots_time_anchor") or report.get("ots") or {}
    if not isinstance(ots, dict) or not ots.get("ots_verification_mode"):
        # Check chain_d2
        chain_d2 = report.get("chain_d2")
        if isinstance(chain_d2, dict) and chain_d2.get("ots_verification_mode"):
            ots = chain_d2

    if isinstance(ots, dict):
        mode = ots.get("ots_verification_mode") or ots.get("mode")
        fullnode = ots.get("fullnode_independent_verification")
        if mode == "ci-api" and fullnode is True:
            errors.append("ci-api mode cannot set fullnode_independent_verification=true")
        if fullnode is True and mode != "fullnode":
            errors.append("fullnode_independent_verification=true requires mode=fullnode")

    # TA-REDTEAM-2026-012: report lifecycle validation
    report_status = report.get("report_status")
    is_current_val = report.get("is_current")
    historical_report_only = report.get("historical_report_only")

    if report_status is not None or is_current_val is not None or historical_report_only is not None:
        if report_status is not None and report_status not in VALID_REPORT_STATUSES:
            errors.append(f"report_status must be one of {sorted(VALID_REPORT_STATUSES)}, got: {report_status}")

        # PASS reports must be current
        if status == "PASS" and report_status is not None:
            if report_status != "current":
                errors.append(f"PASS report must have report_status='current', got: '{report_status}'")
            if is_current_val is not None and is_current_val is not True:
                errors.append("PASS report must have is_current=true")

        # Non-current reports
        if report_status in NON_CURRENT_REPORT_STATUSES:
            if is_current_val is not None and is_current_val is not False:
                errors.append(f"non-current report_status '{report_status}' requires is_current=false")
            if historical_report_only is not None and historical_report_only is not True:
                errors.append(f"non-current report_status '{report_status}' requires historical_report_only=true")

        # Revoked requires revocation_reason
        if report_status == "revoked":
            if not report.get("revocation_reason"):
                errors.append("revoked report requires revocation_reason")

        # Superseded requires superseded_by + supersession_reason
        if report_status == "superseded":
            if report.get("superseded_by") is None and not report.get("supersession_reason"):
                errors.append("superseded report requires superseded_by or supersession_reason")
            if not report.get("supersession_reason"):
                errors.append("superseded report requires supersession_reason")

        # Invalidated requires invalidation_reason
        if report_status == "invalidated":
            if not report.get("invalidation_reason"):
                errors.append("invalidated report requires invalidation_reason")

    return errors


def self_test():
    print("Full evidence chain audit validator self-test")
    print("=" * 50)
    passed = 0
    failed = 0

    # 1. Valid PASS report
    report = {
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
    errs = validate_report(report)
    if not errs:
        print("  ✓ valid PASS report"); passed += 1
    else:
        print(f"  ✗ valid PASS report: {errs}"); failed += 1

    # 2. PASS with errors rejected
    r2 = {**report, "errors": ["some error"]}
    errs = validate_report(r2)
    if any("empty errors" in e for e in errs):
        print("  ✓ PASS with errors rejected"); passed += 1
    else:
        print(f"  ✗ PASS with errors rejected: {errs}"); failed += 1

    # 3. PASS with missing required chain rejected
    r3 = {**report, "required_chains": {
        "dag_digest_chain": {"required": True, "status": "FAIL"},
    }}
    errs = validate_report(r3)
    if any("non-PASS required chain" in e for e in errs):
        print("  ✓ PASS with missing required chain rejected"); passed += 1
    else:
        print(f"  ✗ PASS with missing required chain rejected: {errs}"); failed += 1

    # 4. ci-api + fullnode_independent_verification=true rejected
    r4 = {**report, "chain_d2": {
        "ots_verification_mode": "ci-api",
        "fullnode_independent_verification": True,
    }}
    errs = validate_report(r4)
    if any("ci-api" in e for e in errs):
        print("  ✓ ci-api + fullnode=true rejected"); passed += 1
    else:
        print(f"  ✗ ci-api + fullnode=true rejected: {errs}"); failed += 1

    # 5. missing limitations rejected
    r5 = {**report, "limitations": []}
    errs = validate_report(r5)
    if any("limitations" in e for e in errs):
        print("  ✓ missing limitations rejected"); passed += 1
    else:
        print(f"  ✗ missing limitations rejected: {errs}"); failed += 1

    # 6. missing does_not_prove rejected
    r6 = {**report, "does_not_prove": []}
    errs = validate_report(r6)
    if any("does_not_prove" in e for e in errs):
        print("  ✓ missing does_not_prove rejected"); passed += 1
    else:
        print(f"  ✗ missing does_not_prove rejected: {errs}"); failed += 1

    # 7. FAIL report accepted with errors
    r7 = {**report, "overall_status": "FAIL", "errors": ["chain failed"]}
    errs = validate_report(r7)
    if not errs:
        print("  ✓ FAIL with errors accepted"); passed += 1
    else:
        print(f"  ✗ FAIL with errors accepted: {errs}"); failed += 1

    # 8. invalid schema rejected
    r8 = {**report, "schema": "wrong"}
    errs = validate_report(r8)
    if any("schema" in e for e in errs):
        print("  ✓ invalid schema rejected"); passed += 1
    else:
        print(f"  ✗ invalid schema rejected: {errs}"); failed += 1

    # 9. fullnode + mode=fullnode accepted
    r9 = {**report, "chain_d2": {
        "ots_verification_mode": "fullnode",
        "fullnode_independent_verification": True,
    }}
    errs = validate_report(r9)
    if not errs:
        print("  ✓ fullnode + fullnode=true accepted"); passed += 1
    else:
        print(f"  ✗ fullnode + fullnode=true accepted: {errs}"); failed += 1

    # TA-REDTEAM-2026-012: lifecycle tests
    # 10. PASS current report accepted
    r10 = {**report, "report_status": "current", "is_current": True, "historical_report_only": False}
    errs = validate_report(r10)
    if not errs:
        print("  ✓ PASS current report accepted"); passed += 1
    else:
        print(f"  ✗ PASS current report accepted: {errs}"); failed += 1

    # 11. revoked PASS report with is_current=true rejected
    r11 = {**report, "report_status": "revoked", "is_current": True, "historical_report_only": True, "revocation_reason": "test"}
    errs = validate_report(r11)
    if any("PASS" in e and "current" in e for e in errs):
        print("  ✓ revoked PASS report with is_current=true rejected"); passed += 1
    else:
        print(f"  ✗ revoked PASS report with is_current=true rejected: {errs}"); failed += 1

    # 12. revoked report missing revocation_reason
    r12 = {**report, "overall_status": "FAIL", "errors": ["test"], "report_status": "revoked", "is_current": False, "historical_report_only": True}
    errs = validate_report(r12)
    if any("revocation_reason" in e for e in errs):
        print("  ✓ revoked report missing revocation_reason rejected"); passed += 1
    else:
        print(f"  ✗ revoked report missing revocation_reason rejected: {errs}"); failed += 1

    # 13. superseded report missing supersession_reason
    r13 = {**report, "overall_status": "FAIL", "errors": ["test"], "report_status": "superseded", "is_current": False, "historical_report_only": True}
    errs = validate_report(r13)
    if any("supersession_reason" in e for e in errs):
        print("  ✓ superseded report missing supersession_reason rejected"); passed += 1
    else:
        print(f"  ✗ superseded report missing supersession_reason rejected: {errs}"); failed += 1

    # 14. invalidated report missing invalidation_reason
    r14 = {**report, "overall_status": "FAIL", "errors": ["test"], "report_status": "invalidated", "is_current": False, "historical_report_only": True}
    errs = validate_report(r14)
    if any("invalidation_reason" in e for e in errs):
        print("  ✓ invalidated report missing invalidation_reason rejected"); passed += 1
    else:
        print(f"  ✗ invalidated report missing invalidation_reason rejected: {errs}"); failed += 1

    # 15. historical_report_only must be true for non-current
    r15 = {**report, "overall_status": "FAIL", "errors": ["test"], "report_status": "historical", "is_current": False, "historical_report_only": False}
    errs = validate_report(r15)
    if any("historical_report_only" in e for e in errs):
        print("  ✓ historical_report_only=false for non-current rejected"); passed += 1
    else:
        print(f"  ✗ historical_report_only=false for non-current rejected: {errs}"); failed += 1

    print(f"\n{'=' * 50}")
    if failed:
        print(f"SELF-TEST FAILED: {failed} failed, {passed} passed")
        sys.exit(1)
    else:
        print(f"VALIDATE_FULL_EVIDENCE_CHAIN_AUDIT_SELF_TEST_OK ({passed} passed)")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    elif len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        path = sys.argv[1]
        with open(path) as f:
            report = json.load(f)
        errs = validate_report(report)
        if errs:
            print(f"INVALID: {path}")
            for e in errs:
                print(f"  ✗ {e}")
            sys.exit(1)
        else:
            print(f"VALID: {path}")
    else:
        print("Usage: python3 validate_full_evidence_chain_audit.py [--self-test|file.json]")
        sys.exit(1)
