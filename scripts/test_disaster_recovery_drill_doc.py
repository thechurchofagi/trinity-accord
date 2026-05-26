#!/usr/bin/env python3
"""Test disaster-recovery-drill.md exists and has required content (TA-REDTEAM-2026-014)."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "disaster-recovery-drill.md"

REQUIRED = [
    "quarterly",
    "GitHub Pages compromised",
    "GitHub main compromised",
    "Release asset replaced",
    "Arweave/IPFS partial outage",
    "Maintainer account compromised",
    "partial_recovery",
    "full_recovery",
    "corrections-index checked",
]

if not DOC.exists():
    print("FAIL: disaster-recovery-drill.md missing")
    sys.exit(1)

text = DOC.read_text(encoding="utf-8").lower()
missing = [x for x in REQUIRED if x.lower() not in text]
if missing:
    print("FAIL: disaster-recovery-drill.md missing required tokens:")
    for x in missing:
        print("  -", x)
    sys.exit(1)

print("DISASTER_RECOVERY_DRILL_OK")
