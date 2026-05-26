#!/usr/bin/env python3
"""REM-CI-001: repository-integrity.yml has no duplicate step names."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / ".github/workflows/repository-integrity.yml").read_text(encoding="utf-8")
names = re.findall(r"^\s*-\s+name:\s*(.+?)\s*$", text, re.M)

dupes = sorted({name for name in names if names.count(name) > 1})
if dupes:
    print("FAIL: duplicate repository-integrity step names:")
    for name in dupes:
        print("  -", name)
    sys.exit(1)

print("PASS: repository-integrity has no duplicate step names")
