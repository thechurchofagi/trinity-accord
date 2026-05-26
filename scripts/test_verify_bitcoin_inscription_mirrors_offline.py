#!/usr/bin/env python3
"""Test: offline verification of Bitcoin inscription mirrors."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFY_SCRIPT = ROOT / "scripts" / "verify_bitcoin_inscription_mirrors.py"

errors = []

# Test 1: --offline --all should pass
result = subprocess.run(
    [sys.executable, str(VERIFY_SCRIPT), "--offline", "--all"],
    capture_output=True, text=True, cwd=str(ROOT)
)
if result.returncode != 0:
    errors.append(f"--offline --all failed (rc={result.returncode}): {result.stderr}")

# Test 2: Verify count of records checked
if "Checked: 8" not in result.stdout:
    errors.append(f"Expected 'Checked: 8' in output, got: {result.stdout}")

# Test 3: Verify all offline checks passed
if "All offline checks passed" not in result.stdout:
    errors.append(f"Expected 'All offline checks passed' in output")

if errors:
    print("FAIL:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("PASS: offline verification test")
    sys.exit(0)
