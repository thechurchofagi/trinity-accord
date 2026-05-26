#!/usr/bin/env python3
"""apply_*.sh scripts must not present themselves as verification-complete tools."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
files = [
    ROOT / "scripts" / "apply_runbook.sh",
    ROOT / "scripts" / "apply_semantic_validator_patches.sh",
]

ok = True
for path in files:
    if not path.exists():
        continue
    text = path.read_text(encoding="utf-8")
    if "not a verification tool" not in text and "does NOT mean the repository is valid" not in text:
        print(f"FAIL: {path.relative_to(ROOT)} lacks verification warning")
        ok = False

if not ok:
    sys.exit(1)

print("PASS: apply scripts do not overclaim verification")
