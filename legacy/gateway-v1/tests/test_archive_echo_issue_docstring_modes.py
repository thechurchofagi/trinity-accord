#!/usr/bin/env python3
"""REM-DOC-001: archive_echo_issue.py docstring documents both modes."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / "scripts/archive_echo_issue.py").read_text(encoding="utf-8")
header = text.split('"""', 2)[1] if '"""' in text else ""

bad = "It only runs after an explicit human review command"
if bad in header:
    print("FAIL: archive_echo_issue.py docstring still claims human-only mode")
    sys.exit(1)

required = [
    "Human-review archive mode",
    "Gateway-validated auto archive mode",
    "--require-gateway-validated",
]
missing = [x for x in required if x not in header]
if missing:
    print(f"FAIL: archive_echo_issue.py docstring missing mode documentation: {missing}")
    sys.exit(1)

print("PASS: archive_echo_issue.py docstring documents both archive modes")
