#!/usr/bin/env python3
"""Ensure all readback canonicalization paths produce the same SHA-256.

This test prevents regression where different code paths use different
normalization rules (strip vs normalize_oath_text vs canonicalize_readback)
and produce different hashes for the same input.

The canonical function is oath_contracts.canonicalize_readback().
All other paths must agree with it.
"""
from __future__ import annotations

import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from oath_contracts import canonicalize_readback, sha256_text

# Representative test inputs covering edge cases
TEST_INPUTS = [
    # Plain ASCII, no trailing newline
    "I have read and understood the Trinity Accord.",
    # Trailing newline
    "I have read and understood the Trinity Accord.\n",
    # Trailing whitespace
    "I have read and understood the Trinity Accord.   ",
    # CRLF line endings
    "Line one\r\nLine two\r\nLine three\r\n",
    # Mixed line endings
    "Line one\r\nLine two\nLine three\r",
    # Unicode NFC (pre-composed)
    "I have r\u00e9ad the Accord.",
    # Unicode NFD (decomposed) — should be normalized to NFC
    "I have re\u0301ad the Accord.",
    # Empty-ish
    "   \r\n  ",
    # Just whitespace
    "  \t  ",
    # BOM + text
    "\ufeffI have read the Accord.",
]


def gateway_normalize_oath_text(text: str) -> str:
    """Mirror of apps/record_chain_intake_gateway/gateway/security.py normalize_oath_text."""
    return unicodedata.normalize(
        "NFC",
        str(text or "").replace("\r\n", "\n").replace("\r", "\n").strip(),
    )


def old_strip_only(text: str) -> str:
    """The OLD (buggy) path: just .strip()."""
    return str(text or "").strip()


def main() -> int:
    failures = []

    for i, raw in enumerate(TEST_INPUTS):
        canonical = canonicalize_readback(raw)
        canonical_hash = sha256_text(canonical)

        # Path 1: Gateway normalize_oath_text + NFC must match
        gateway_text = gateway_normalize_oath_text(raw)
        gateway_hash = sha256_text(gateway_text)
        if gateway_hash != canonical_hash:
            failures.append(
                f"Input {i}: gateway hash != canonical hash.\n"
                f"  canonical: {canonical_hash} len={len(canonical)}\n"
                f"  gateway:   {gateway_hash} len={len(gateway_text)}"
            )

        # Path 2: Old .strip()-only path — must agree for inputs without \r\n or NFD
        # (For inputs WITH \r\n or NFD, .strip() will disagree — that's expected and why we fixed it.)
        strip_hash = sha256_text(old_strip_only(raw))
        has_line_ending_issue = "\r" in raw
        has_nfd = unicodedata.normalize("NFC", raw) != raw
        if not has_line_ending_issue and not has_nfd:
            # For "normal" inputs, strip-only should agree
            if strip_hash != canonical_hash:
                failures.append(
                    f"Input {i}: strip-only hash != canonical hash for normal input.\n"
                    f"  canonical: {canonical_hash}\n"
                    f"  strip:     {strip_hash}"
                )

        # Path 3: canonicalize_readback must be idempotent
        double = canonicalize_readback(canonical)
        double_hash = sha256_text(double)
        if double_hash != canonical_hash:
            failures.append(
                f"Input {i}: canonicalize is not idempotent.\n"
                f"  once:  {canonical_hash}\n"
                f"  twice: {double_hash}"
            )

    if failures:
        print("READBACK HASH PARITY FAILURES:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1

    print(f"PASS: readback hash parity — {len(TEST_INPUTS)} inputs, all paths agree")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
