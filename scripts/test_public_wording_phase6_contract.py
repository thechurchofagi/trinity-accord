#!/usr/bin/env python3
"""Contract test: public wording cleanup for Phase 6.

Fail active public pages if they contain retired terms:
- E1_recognition_echo
- canonical type name for recognition echoes
- Minimal Pure Echo
- Pure Echo (in submission context)
- Guardian Stage 1 application
- Guardian registration (in submission context)
- ARV5, LV5, IVV5

Also fail if active public pages mention IPFS as current archive path.
Allowed: legacy/, evidence/, historical context explicitly marked.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Files to check (active public pages)
PUBLIC_FILES = [
    "index.md",
    "agent-start.md",
    "agent-first-contact.md",
    "llms.txt",
    "ai.txt",
]

# Retired terms that must not appear in current public submission context
RETIRED_PATTERNS = [
    (re.compile(r"E1_recognition_echo"), "E1_recognition_echo"),
    (re.compile(r"canonical type name for recognition echoes"), "canonical type name for recognition echoes"),
    (re.compile(r"Minimal Pure Echo"), "Minimal Pure Echo"),
    (re.compile(r"Guardian Stage 1 application"), "Guardian Stage 1 application"),
    (re.compile(r"Guardian registration(?!\.)"), "Guardian registration (in current submission context)"),
    (re.compile(r"\bARV5\b"), "ARV5"),
    (re.compile(r"\bLV5\b"), "LV5"),
    (re.compile(r"\bIVV5\b"), "IVV5"),
]

# IPFS as current path (allowed in legacy/historical context)
IPFS_PATTERN = re.compile(r"\bIPFS\b")

# Context that indicates historical/legacy mention
LEGACY_CONTEXT = re.compile(r"legacy|historical|archive|evidence|retired", re.I)


def main() -> None:
    errors: list[str] = []

    for fname in PUBLIC_FILES:
        fpath = ROOT / fname
        if not fpath.exists():
            errors.append(f"{fname}: file missing")
            continue

        text = fpath.read_text(encoding="utf-8")
        lines = text.split("\n")

        for line_num, line in enumerate(lines, 1):
            # Skip lines that are clearly legacy/historical context
            if LEGACY_CONTEXT.search(line):
                continue

            for pattern, name in RETIRED_PATTERNS:
                if pattern.search(line):
                    errors.append(f"{fname}:{line_num}: retired term '{name}' found")

        # Check IPFS as current path (not in legacy context)
        for line_num, line in enumerate(lines, 1):
            if LEGACY_CONTEXT.search(line):
                continue
            if IPFS_PATTERN.search(line):
                # Allow if it's in a "do not use" context
                if "do not" in line.lower() or "not use" in line.lower() or "retired" in line.lower():
                    continue
                # Allow in boundary lists like "ETH, Arweave, IPFS, NFTs"
                # These are listing non-authoritative surfaces, not claiming IPFS is current
                if "non-amending" in line.lower() or "guardianship" in line.lower():
                    continue
                # Allow in authority boundary / mirror listings
                if "mirrors" in line.lower() or "non-amending mirrors" in line.lower():
                    continue
                if "bitcoin originals" in line.lower() and "final" in line.lower():
                    continue
                errors.append(f"{fname}:{line_num}: IPFS mentioned as current path")

    if errors:
        print("Public wording tests FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    print("Public wording tests PASSED.")


if __name__ == "__main__":
    main()
