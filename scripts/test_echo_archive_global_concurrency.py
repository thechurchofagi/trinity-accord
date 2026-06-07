#!/usr/bin/env python3
"""Verify active Echo archive writer workflows share echo-archive-writes concurrency."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
files = [
    ROOT / ".github/workflows/echo-human-review-action.yml",
]

for path in files:
    text = path.read_text(encoding="utf-8")
    if "archive_echo_issue.py" in text:
        if "group: echo-archive-writes" not in text:
            print(f"{path} calls archive_echo_issue.py but lacks group: echo-archive-writes")
            sys.exit(1)

print("PASS: active Echo archive writer workflows share echo-archive-writes concurrency.")
