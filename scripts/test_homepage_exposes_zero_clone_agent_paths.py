#!/usr/bin/env python3
"""Homepage must expose first-contact and zero-clone external-agent paths."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.md"

REQUIRED = [
    "/agent-first-contact/",
    "/external-agent-quickstart/",
    "/zero-clone-builders/",
    "/api/formal-builder-bundles.v1.json",
    "/llms.txt",
    "/ai.txt",
]

def main() -> int:
    text = INDEX.read_text(encoding="utf-8")
    missing = [item for item in REQUIRED if item not in text]
    if missing:
        print("FAIL: homepage missing zero-clone agent paths:")
        for item in missing:
            print("  -", item)
        return 1

    print("PASS: homepage exposes zero-clone external-agent paths")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
