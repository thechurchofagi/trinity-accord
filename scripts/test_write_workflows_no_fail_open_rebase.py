#!/usr/bin/env python3
"""Write workflows must not ignore git pull/rebase/push failures."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / ".github" / "workflows"

WRITE_MARKERS = [
    "contents: write",
    "git push",
    "git commit",
]

BAD_PATTERNS = [
    r"git\s+pull\s+--rebase[^\n]*\|\|\s*true",
    r"git\s+pull[^\n]*\|\|\s*true",
    r"git\s+push[^\n]*\|\|\s*true",
    r"git\s+commit[^\n]*\|\|\s*true",
]

bad = []

for path in sorted(WF.glob("*.yml")):
    text = path.read_text(encoding="utf-8")
    if not any(marker in text for marker in WRITE_MARKERS):
        continue

    for pattern in BAD_PATTERNS:
        if re.search(pattern, text):
            bad.append(f"{path.name}: {pattern}")

if bad:
    print("FAIL: write workflows contain fail-open git write/rebase patterns:")
    for item in bad:
        print("  -", item)
    sys.exit(1)

print("PASS: write workflows do not ignore git pull/rebase/push failures")
