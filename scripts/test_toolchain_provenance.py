#!/usr/bin/env python3
"""Test: toolchain_provenance.py must exist and output valid JSON with required fields."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "toolchain_provenance.py"

if not SCRIPT.exists():
    print("FAIL: scripts/toolchain_provenance.py missing")
    sys.exit(1)

res = subprocess.run(["python3", str(SCRIPT)], cwd=ROOT, text=True, capture_output=True)
if res.returncode != 0:
    print(res.stdout)
    print(res.stderr)
    sys.exit(res.returncode)

data = json.loads(res.stdout)

required_top = ["schema", "platform", "github_actions", "tools"]
for k in required_top:
    if k not in data:
        print(f"FAIL: missing top-level key {k}")
        sys.exit(1)

required_tools = ["python", "pip", "node", "git", "curl", "tar", "gzip", "sha256sum", "ots"]
for tool in required_tools:
    if tool not in data["tools"]:
        print(f"FAIL: missing tool provenance for {tool}")
        sys.exit(1)

print("TOOLCHAIN_PROVENANCE_OK")
