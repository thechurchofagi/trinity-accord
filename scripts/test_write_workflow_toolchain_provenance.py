#!/usr/bin/env python3
"""Test: Write workflows must record toolchain provenance."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
WF_DIR = ROOT / ".github" / "workflows"

WRITE_MARKERS = [
    "contents: write",
    "git push",
    "gh release",
    "upload-release",
    "tar czf",
]

errors = []

for path in WF_DIR.glob("*.yml"):
    text = path.read_text(encoding="utf-8")
    if any(m in text for m in WRITE_MARKERS):
        if "scripts/toolchain_provenance.py" not in text:
            errors.append(f"{path.name}: write workflow missing toolchain provenance step")

if errors:
    print("FAIL: write workflow provenance missing:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("WRITE_WORKFLOW_TOOLCHAIN_PROVENANCE_OK")
