#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

commands = [
    ["python3", "scripts/validate_trust_root_policy.py", "--self-test"],
    ["python3", "scripts/validate_trust_root_policy.py", "archive/trust-root-policy.json"],
]

for cmd in commands:
    res = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if res.returncode != 0:
        print(res.stdout)
        print(res.stderr)
        sys.exit(res.returncode)

print("TRUST_ROOT_POLICY_OK")
