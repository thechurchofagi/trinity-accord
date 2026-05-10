#!/usr/bin/env python3
"""Test RECOVERY.md contains required sections and tokens (TA-REDTEAM-2026-014)."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "RECOVERY.md"

REQUIRED = [
    "Cold-Start Recovery",
    "Minimal Trusted Bootstrap Root",
    "Bitcoin Originals",
    "97631551",
    "98369145",
    "98387475",
    "bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf",
    "Do Not Trust GitHub Main",
    "corrections-index",
    "full_recovery",
    "partial_recovery",
    "availability_only",
    "unverified_mirror",
    "failed_recovery",
    "verify-release-assets.mjs",
    "Arweave",
    "IPFS",
    "CAR",
    "NFT",
    "requirements-ci.txt",
    ".node-version",
    "OpenTimestamps",
]

if not DOC.exists():
    print("FAIL: RECOVERY.md missing")
    sys.exit(1)

text = DOC.read_text(encoding="utf-8")
missing = [x for x in REQUIRED if x not in text]
if missing:
    print("FAIL: RECOVERY.md missing required tokens:")
    for x in missing:
        print("  -", x)
    sys.exit(1)

print("RECOVERY_DOCS_OK")
