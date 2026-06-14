#!/usr/bin/env python3
"""Part E: Test that guardian-registry.md does not claim current active status."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def ok(msg: str) -> None:
    print(f"PASS: {msg}")


def main() -> int:
    path = ROOT / "guardian-registry.md"
    if not path.exists():
        fail("missing guardian-registry.md")

    text = path.read_text(encoding="utf-8").lower()

    # Must NOT contain these phrases as headings or claims of current status
    forbidden = [
        "current active guardians",
        "current active guardian",
    ]
    forbidden_lines = []
    for line in text.splitlines():
        line_stripped = line.strip().lower()
        # Skip lines that say it's NOT the current status (boundary text)
        if "not the current active guardian" in line_stripped:
            continue
        if "not current" in line_stripped:
            continue
        for phrase in forbidden:
            if phrase in line_stripped:
                forbidden_lines.append((phrase, line_stripped))

    for phrase, line in forbidden_lines:
        fail(f"guardian-registry.md still claims '{phrase}': {line}")

    # Must contain these phrases
    required = [
        "historical",
        "not the current active guardian status",
        "does not create authority",
    ]
    for phrase in required:
        if phrase not in text:
            fail(f"guardian-registry.md missing required text: '{phrase}'")

    ok("guardian-registry.md correctly describes historical-only status")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
