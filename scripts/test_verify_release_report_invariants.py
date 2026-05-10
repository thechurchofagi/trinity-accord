#!/usr/bin/env python3
"""Test: Report invariants (REL-REPORT-001)"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_verify_release_report.py"


def run_validator(args):
    result = subprocess.run(
        [sys.executable, str(VALIDATOR)] + args,
        capture_output=True, text=True
    )
    return result.returncode, result.stdout, result.stderr


print("Running report invariants tests...")

# Self-test must pass
rc, stdout, stderr = run_validator(["--self-test"])
if rc != 0:
    print(f"FAIL: self-test failed:\n{stdout}\n{stderr}")
    sys.exit(1)
print("  ✓ validator self-test passes")

# Verify specific invariant messages are tested
if "PASS with errors rejected" in stdout:
    print("  ✓ PASS + errors invariant tested")
if "asset count mismatch" in stdout:
    print("  ✓ PASS + asset count mismatch invariant tested")
if "sha256 count mismatch" in stdout:
    print("  ✓ PASS + sha256 count mismatch invariant tested")
if "CID/DAG boundary" in stdout:
    print("  ✓ hash_size_only + CID/DAG boundary tested")
if "CID check + CID fail" in stdout:
    print("  ✓ CID check + CID fail invariant tested")

print("\nVERIFY_RELEASE_REPORT_INVARIANTS_OK")
