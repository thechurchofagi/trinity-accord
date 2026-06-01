#!/usr/bin/env python3
"""Verify gateway-auto-archive hard-fails after push retry exhaustion."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
wf = ROOT / ".github/workflows/gateway-auto-archive.yml"
text = wf.read_text(encoding="utf-8")

required = [
    'PUSHED=false',
    'PUSHED=true',
    'if [ "$PUSHED" != "true" ]',
    "Failed to push archive commit after 5 attempts",
    "exit 1",
]

missing = [s for s in required if s not in text]
if missing:
    print(f"gateway-auto-archive push failure guard missing: {missing}")
    sys.exit(1)

print("PASS: gateway-auto-archive hard-fails after push retry exhaustion.")
