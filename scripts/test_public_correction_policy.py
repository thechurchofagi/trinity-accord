#!/usr/bin/env python3
"""Test public correction policy documents (TA-REDTEAM-2026-012)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_TERMS = [
    "corrections-index",
    "non-amending",
    "Bitcoin Originals",
    "do not silently delete",
    "tombstone",
    "revoked",
    "superseded",
    "invalidated",
    "stale",
    "trust-root",
]


def main():
    passed = 0
    failed = 0

    # 1. SECURITY.md exists and contains required terms
    security_path = ROOT / "SECURITY.md"
    if not security_path.exists():
        print("  FAIL: SECURITY.md does not exist")
        failed += 1
    else:
        content = security_path.read_text(encoding="utf-8").lower()
        for term in REQUIRED_TERMS:
            if term.lower() in content:
                print(f"  PASS: SECURITY.md contains '{term}'")
                passed += 1
            else:
                print(f"  FAIL: SECURITY.md missing '{term}'")
                failed += 1

    # 2. CORRECTION-REVOCATION-POLICY.md exists and contains required terms
    policy_path = ROOT / "CORRECTION-REVOCATION-POLICY.md"
    if not policy_path.exists():
        print("  FAIL: CORRECTION-REVOCATION-POLICY.md does not exist")
        failed += 1
    else:
        content = policy_path.read_text(encoding="utf-8").lower()
        for term in REQUIRED_TERMS:
            if term.lower() in content:
                print(f"  PASS: CORRECTION-REVOCATION-POLICY.md contains '{term}'")
                passed += 1
            else:
                print(f"  FAIL: CORRECTION-REVOCATION-POLICY.md missing '{term}'")
                failed += 1

    print(f"\n{'=' * 50}")
    print(f"test_public_correction_policy: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
