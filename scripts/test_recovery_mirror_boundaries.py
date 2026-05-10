#!/usr/bin/env python3
"""Test mirror boundaries in RECOVERY.md (TA-REDTEAM-2026-014).

Checks:
- RECOVERY.md says GitHub/Pages/Releases/Arweave/IPFS/NFT are mirrors/non-amending
- RECOVERY.md says availability_only != verified
- RECOVERY.md says NFT ownership != authority
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    errors = []

    recovery_path = ROOT / "RECOVERY.md"
    if not recovery_path.exists():
        print("MIRROR_BOUNDARIES_FAIL\n  - RECOVERY.md missing")
        sys.exit(1)

    text = recovery_path.read_text(encoding="utf-8")

    # Mirror boundary checks
    mirror_checks = [
        ("GitHub Releases are mirrors, not canonical authority", "GitHub Releases mirror boundary"),
        ("non-amending", "non-amending boundary"),
        ("NFT ownership does not imply", "NFT ownership != authority"),
        ("availability_only", "availability_only status defined"),
        ("unverified_mirror", "unverified_mirror status defined"),
    ]

    for token, desc in mirror_checks:
        if token.lower() not in text.lower():
            errors.append(f"RECOVERY.md missing mirror boundary: {desc}")

    if errors:
        print("MIRROR_BOUNDARIES_FAIL")
        for e in errors:
            print("  -", e)
        sys.exit(1)

    print("MIRROR_BOUNDARIES_OK")


if __name__ == "__main__":
    main()
