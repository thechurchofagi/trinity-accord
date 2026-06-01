#!/usr/bin/env python3
"""DEEP-ARCH-003: gateway archive requires staged changes for STATUS=archived."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
wf = ROOT / ".github/workflows/gateway-auto-archive.yml"
text = wf.read_text(encoding="utf-8")

required = [
    'if [ "$STATUS" = "archived" ] && git diff --cached --quiet',
    "archive_echo_issue.py reported archived but no archive/generated changes are staged",
    "Refusing to close or comment success",
]

missing = [s for s in required if s not in text]
if missing:
    print(f"FAIL: gateway archive staged-change guard missing: {missing}")
    sys.exit(1)

print("PASS: gateway archive requires staged changes for STATUS=archived")
