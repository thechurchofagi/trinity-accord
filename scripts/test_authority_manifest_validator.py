#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

commands = [
    ["python3", "scripts/validate_authority_manifest.py", "--self-test"],
    ["python3", "scripts/validate_authority_manifest.py", "archive/authority-manifest/authority.jcs.json"],
]

for cmd in commands:
    res = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if res.returncode != 0:
        print(res.stdout)
        print(res.stderr)
        sys.exit(res.returncode)

print("AUTHORITY_MANIFEST_VALIDATOR_OK")
