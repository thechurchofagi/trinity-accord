#!/usr/bin/env python3
"""Test wrapper for recovery index validation (TA-REDTEAM-2026-014)."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

commands = [
    ["python3", "scripts/validate_recovery_index.py", "--self-test"],
    ["python3", "scripts/validate_recovery_index.py"],
]

for cmd in commands:
    r = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if r.returncode != 0:
        print(r.stdout)
        print(r.stderr)
        sys.exit(r.returncode)

print("RECOVERY_INDEX_OK")
