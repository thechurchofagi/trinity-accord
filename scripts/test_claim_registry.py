#!/usr/bin/env python3
"""Test claim registry (TA-REDTEAM-2026-017).

Runs validate_claim_registry.py --self-test and validate_claim_registry.py.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_claim_registry.py"


def main():
    failures = []

    # Run self-test
    print("Running validate_claim_registry.py --self-test ...")
    r = subprocess.run([sys.executable, str(VALIDATOR), "--self-test"], capture_output=True, text=True)
    if r.returncode != 0:
        failures.append(f"self-test failed:\n{r.stdout}\n{r.stderr}")
    else:
        print(r.stdout)

    # Run validation
    print("Running validate_claim_registry.py ...")
    r = subprocess.run([sys.executable, str(VALIDATOR)], capture_output=True, text=True)
    if r.returncode != 0:
        failures.append(f"validation failed:\n{r.stdout}\n{r.stderr}")
    else:
        print(r.stdout)

    if failures:
        for f in failures:
            print(f"FAIL: {f}")
        sys.exit(1)
    print("CLAIM_REGISTRY_TEST_OK")


if __name__ == "__main__":
    main()
