#!/usr/bin/env python3
"""Test corrections index validator (TA-REDTEAM-2026-012).

Wrapper that runs validate_corrections_index.py --self-test and validate_corrections_index.py.
"""
import subprocess
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    passed = 0
    failed = 0

    # Run self-test
    print("Running corrections index self-test...")
    result = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "validate_corrections_index.py"), "--self-test"],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode == 0:
        print("  PASS: corrections index self-test")
        passed += 1
    else:
        print(f"  FAIL: corrections index self-test (exit code {result.returncode})")
        failed += 1

    # Run actual validation
    print("\nRunning corrections index validation...")
    result = subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "validate_corrections_index.py")],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode == 0:
        print("  PASS: corrections index validation")
        passed += 1
    else:
        print(f"  FAIL: corrections index validation (exit code {result.returncode})")
        failed += 1

    print(f"\n{'=' * 50}")
    print(f"test_corrections_index: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
