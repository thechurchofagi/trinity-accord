#!/usr/bin/env python3
"""Test that GitHub Actions are pinned to full commit SHAs.

RF-006: All third-party actions must use 40-char commit SHA.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"

ALLOW_UNPINNED = {
    # Temporary exceptions with documented reasons:
    # "some/action@v1": "temporary exception until YYYY-MM-DD because ..."
}

errors = []

for path in WORKFLOWS.glob("*.yml"):
    text = path.read_text(encoding="utf-8")
    for m in re.finditer(r"uses:\s*([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@([^\s#]+)", text):
        action = m.group(1)
        ref = m.group(2)
        key = f"{action}@{ref}"

        if key in ALLOW_UNPINNED:
            continue

        if not re.fullmatch(r"[a-f0-9]{40}", ref):
            errors.append(f"{path.relative_to(ROOT)}: {key} is not pinned to full commit SHA")

if errors:
    print("ACTION_PINNING_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("ACTION_PINNING_OK")
