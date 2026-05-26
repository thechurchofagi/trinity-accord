#!/usr/bin/env python3
"""Test toolchain documentation in RECOVERY.md (TA-REDTEAM-2026-014).

Checks:
- RECOVERY.md references .node-version
- RECOVERY.md references requirements-ci.txt
- RECOVERY.md references OpenTimestamps
- RECOVERY.md includes tool install/version check commands
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    errors = []

    recovery_path = ROOT / "RECOVERY.md"
    if not recovery_path.exists():
        print("TOOLCHAIN_DOCS_FAIL\n  - RECOVERY.md missing")
        sys.exit(1)

    text = recovery_path.read_text(encoding="utf-8")

    required_tokens = [
        ".node-version",
        "requirements-ci.txt",
        "OpenTimestamps",
        "node --version",
        "python3 --version",
    ]

    for token in required_tokens:
        if token not in text:
            errors.append(f"RECOVERY.md missing toolchain reference: {token}")

    if errors:
        print("TOOLCHAIN_DOCS_FAIL")
        for e in errors:
            print("  -", e)
        sys.exit(1)

    print("TOOLCHAIN_DOCS_OK")


if __name__ == "__main__":
    main()
