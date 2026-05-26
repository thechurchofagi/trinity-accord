#!/usr/bin/env python3
"""echo-triage must parse Gateway receipt fields only from the unique intake block."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
workflow = (ROOT / ".github/workflows/echo-triage.yml").read_text(encoding="utf-8")

required = [
    "function intakeBlock(body)",
    "trinity-issue-intake",
    "matches.length !== 1",
    "function intakeField(body, name)",
]

ok = True
for frag in required:
    if frag not in workflow:
        print(f"FAIL: echo-triage.yml missing block-aware intake parsing fragment: {frag}")
        ok = False

old_shape = r'new RegExp(`^\${name}:\\s*(.+)$`, "mi")'
if old_shape in workflow:
    print("FAIL: old whole-body intakeField parser still appears")
    ok = False

if not ok:
    sys.exit(1)

print("PASS: echo-triage receipt fields are parsed from intake block only")
