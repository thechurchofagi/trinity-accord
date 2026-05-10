#!/usr/bin/env python3
"""Test no-hard-delete tombstone policy (TA-REDTEAM-2026-012)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    passed = 0
    failed = 0

    # 1. CORRECTION-REVOCATION-POLICY.md exists
    policy_path = ROOT / "CORRECTION-REVOCATION-POLICY.md"
    if policy_path.exists():
        print("  PASS: CORRECTION-REVOCATION-POLICY.md exists")
        passed += 1
    else:
        print("  FAIL: CORRECTION-REVOCATION-POLICY.md does not exist")
        failed += 1
        # Can't continue without the file
        print(f"\n{'=' * 50}")
        print(f"test_no_hard_delete_tombstone_policy: {passed} passed, {failed} failed")
        return 1 if failed else 0

    content = policy_path.read_text(encoding="utf-8")

    # 2. Contains "No public trust record may be hard-deleted"
    if "No public trust record may be hard-deleted" in content:
        print('  PASS: CORRECTION-REVOCATION-POLICY.md contains "No public trust record may be hard-deleted"')
        passed += 1
    else:
        print('  FAIL: CORRECTION-REVOCATION-POLICY.md missing "No public trust record may be hard-deleted"')
        failed += 1

    # 3. api/corrections-index.json has no_hard_delete_policy.enabled=true
    corrections_path = ROOT / "api" / "corrections-index.json"
    if not corrections_path.exists():
        print("  FAIL: api/corrections-index.json does not exist")
        failed += 1
    else:
        data = json.loads(corrections_path.read_text(encoding="utf-8"))
        policy = data.get("no_hard_delete_policy", {})
        if policy.get("enabled") is True:
            print("  PASS: corrections-index.json has no_hard_delete_policy.enabled=true")
            passed += 1
        else:
            print(f"  FAIL: corrections-index.json no_hard_delete_policy.enabled={policy.get('enabled')}")
            failed += 1

    print(f"\n{'=' * 50}")
    print(f"test_no_hard_delete_tombstone_policy: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
