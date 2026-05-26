#!/usr/bin/env python3
"""Test: Public API metadata completeness (wraps validate_public_api_metadata)."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

commands = [
    ["python3", "scripts/validate_public_api_metadata.py", "--self-test"],
    ["python3", "scripts/validate_public_api_metadata.py"],
]

for cmd in commands:
    res = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if res.returncode != 0:
        print(res.stdout)
        print(res.stderr)
        sys.exit(res.returncode)

print("PUBLIC_API_METADATA_COMPLETENESS_OK")
