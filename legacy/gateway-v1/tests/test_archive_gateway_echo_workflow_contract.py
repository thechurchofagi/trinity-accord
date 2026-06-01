#!/usr/bin/env python3
"""Test: Archive Gateway Echo workflow satisfies persistence contract."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = [
    ROOT / ".github/workflows/archive-gateway-echo.yml",
    ROOT / ".github/workflows/gateway-auto-archive.yml",
    ROOT / ".github/workflows/archive-echo.yml",
    ROOT / ".github/workflows/archive-gateway-agent-echo.yml",
]

def main() -> int:
    path = next((p for p in CANDIDATES if p.exists()), None)
    if not path:
        print("FAIL: Archive Gateway Echo workflow not found")
        return 1

    text = path.read_text(encoding="utf-8")
    required = [
        "contents: write",
        "issues: write",
        "trinity-receipt-bearing-archive-v1",
        "actions/checkout",
        "persist-credentials: true",
        "git config user.name",
        "git commit",
        "git push",
    ]
    missing = [x for x in required if x not in text]
    if missing:
        print("FAIL: missing workflow requirements:", missing)
        return 1

    # Must not require issue to be open
    if "state == 'open'" in text or 'state != "open"' in text:
        print("FAIL: archive workflow must not require issue to be open")
        return 1

    print(f"PASS: {path.relative_to(ROOT)} satisfies Gateway archive workflow contract")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
