#!/usr/bin/env python3
"""Test that gateway server.js passes Node.js syntax check."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
server = ROOT / "examples" / "github-app-backend" / "server.js"

result = subprocess.run(
    ["node", "--check", str(server)],
    cwd=str(ROOT),
    text=True,
    capture_output=True
)

if result.returncode != 0:
    print(result.stdout)
    print(result.stderr, file=sys.stderr)
    sys.exit(result.returncode)

print("GATEWAY_SERVER_SYNTAX_OK")
