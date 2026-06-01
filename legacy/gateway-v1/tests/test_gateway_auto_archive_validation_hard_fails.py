#!/usr/bin/env python3
"""DEEP-ARCH-001: gateway-auto-archive.yml must fail closed on validation failure."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
wf = ROOT / ".github/workflows/gateway-auto-archive.yml"
text = wf.read_text(encoding="utf-8")

if "Archiving anyway" in text:
    print("FAIL: gateway-auto-archive still allows validation failure to archive anyway.")
    sys.exit(1)

required = [
    "Validation failed",
    "Refusing to commit archive",
    'rm -f "$RECORD_PATH"',
    "exit 1",
]

missing = [s for s in required if s not in text]
if missing:
    print(f"FAIL: validation hard-fail guard missing: {missing}")
    sys.exit(1)

print("PASS: gateway-auto-archive hard-fails on validation failure.")
