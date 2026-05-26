#!/usr/bin/env python3
"""Test trust-root historical records (TA-REDTEAM-2026-012)."""
import sys
import os
import json
import copy
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from validate_trust_root_policy import validate


def main():
    passed = 0
    failed = 0

    # Load actual trust-root-policy.json for reference
    policy_path = os.path.join(ROOT, "archive", "trust-root-policy.json")
    with open(policy_path) as f:
        actual_policy = json.load(f)

    def check(label, data, expect_error_contains=None):
        nonlocal passed, failed
        errs = validate(data)
        if expect_error_contains:
            if any(expect_error_contains in e for e in errs):
                print(f"  PASS: {label}")
                passed += 1
            else:
                print(f"  FAIL: {label} — expected '{expect_error_contains}', got: {errs}")
                failed += 1
        else:
            if not errs:
                print(f"  PASS: {label}")
                passed += 1
            else:
                print(f"  FAIL: {label} — expected no errors, got: {errs}")
                failed += 1

    # Base valid policy
    base = copy.deepcopy(actual_policy)

    # 1. Valid current historical root accepted
    check("valid current historical root accepted", base)

    # 2. Missing historical_roots rejected
    no_roots = copy.deepcopy(base)
    del no_roots["historical_roots"]
    check("missing historical_roots rejected", no_roots, "historical_roots must be a list")

    # 3. Two current roots rejected
    two_current = copy.deepcopy(base)
    two_current["historical_roots"].append(copy.deepcopy(base["historical_roots"][0]))
    check("two current roots rejected", two_current, "exactly one current root")

    # 4. Current root hash mismatch rejected
    bad_hash = copy.deepcopy(base)
    bad_hash["historical_roots"][0]["authority_manifest_sha256"] = "0" * 64
    check("current root hash mismatch rejected", bad_hash, "mismatch")

    # 5. Revoked root with is_current=true rejected
    # (Adding a revoked root with is_current=true creates two current roots)
    revoked_current = copy.deepcopy(base)
    revoked_current["historical_roots"].append({
        "root_id": "revoked-root",
        "status": "revoked",
        "is_current": True,
        "historical_record_only": False,
        "effective_from": "2026-01-01",
        "reason": "Compromised."
    })
    check("revoked root with is_current=true rejected", revoked_current, "exactly one current root")

    # 6. Superseded root missing successor rejected
    superseded = copy.deepcopy(base)
    superseded["historical_roots"].append({
        "root_id": "old-root",
        "status": "superseded",
        "is_current": False,
        "historical_record_only": True,
        "effective_from": "2026-01-01",
        "reason": "Old root."
    })
    check("superseded root missing successor rejected", superseded, "superseded_by")

    print(f"\n{'=' * 50}")
    print(f"test_trust_root_historical_records: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
