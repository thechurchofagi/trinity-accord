#!/usr/bin/env python3
"""Shared helper: canonical oath readback text for test scripts.

Tests that call builder scripts need to pass --readback with the exact
oath text. This module provides it so tests don't hard-code stale copies.
"""
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_OATH_FILE = _ROOT / "api" / "verification-echo-pre-oath.v2.txt"
_GUARDIAN_OATH_FILE = _ROOT / "api" / "guardian-application-oath.v1.txt"


def _extract_oath(filepath: Path) -> str:
    """Extract the oath body from an oath file (after '=== OATH TEXT BEGINS ===')."""
    text = filepath.read_text(encoding="utf-8")
    marker = "=== OATH TEXT BEGINS ==="
    end_marker = "HOW TO USE:"
    if marker in text:
        oath = text.split(marker)[1].split(end_marker)[0].strip()
        lines = oath.split("\n")
        while lines and lines[-1].strip().startswith("==="):
            lines.pop()
        return "\n".join(lines).strip()
    return text.strip()


def get_oath_readback() -> str:
    """Return the canonical verification oath text (the part agents must type back)."""
    return _extract_oath(_OATH_FILE)


def get_guardian_oath_readback() -> str:
    """Return the canonical Guardian application oath text."""
    return _extract_oath(_GUARDIAN_OATH_FILE)
