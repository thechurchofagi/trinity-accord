#!/usr/bin/env python3
"""Validate FULL-EVIDENCE-CHAIN-AUDIT.json against schema and PASS invariants.

Usage:
  python3 scripts/validate_full_evidence_chain_audit.py --self-test
  python3 scripts/validate_full_evidence_chain_audit.py FULL-EVIDENCE-CHAIN-AUDIT.json
"""
import json, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
