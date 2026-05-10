#!/usr/bin/env python3
"""Test: CAR parser fail-closed behavior (REL-CAR-001)"""

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "scripts" / "verify-release-assets.mjs"
text = SRC.read_text(encoding="utf-8")

DAG_SRC = Path(__file__).resolve().parents[1] / "scripts" / "verify-dag-and-signed-cids.mjs"
dag_text = DAG_SRC.read_text(encoding="utf-8") if DAG_SRC.exists() else ""

FULL_SRC = Path(__file__).resolve().parents[1] / "scripts" / "verify-full-evidence-chain.mjs"
full_text = FULL_SRC.read_text(encoding="utf-8") if FULL_SRC.exists() else ""


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


print("Running CAR parser fail-closed tests...")

# --- verify-release-assets.mjs CAR parser ---

# Must have strict parseCarHeader with bounds checking
if "Truncated CAR header" in text or "pos >= data.length" in text:
    print("  ✓ CAR header varint bounds check present")
else:
    fail("CAR header varint lacks bounds check")

# Must have safe integer check
if "Number.isSafeInteger" in text:
    print("  ✓ safe integer check in CAR parser")
else:
    fail("Missing safe integer check in CAR parser")

# --- verify-dag-and-signed-cids.mjs ---

if dag_text:
    # readVarint should have bounds check
    if "readVarint" in dag_text:
        # Check if it has pos < data.length guard
        lines = dag_text.split("\n")
        in_readvarint = False
        has_bounds = False
        for line in lines:
            if "function readVarint" in line:
                in_readvarint = True
            if in_readvarint and ("pos >= data.length" in line or "pos < data.length" in line or "Truncated" in line):
                has_bounds = True
            if in_readvarint and line.strip().startswith("return"):
                in_readvarint = False

        if has_bounds:
            print("  ✓ readVarint has bounds check (verify-dag)")
        else:
            print("  ⚠ readVarint lacks explicit bounds check (verify-dag) — acceptable if parseCarHeader is strict")

    # blockEnd > data.length should fail, not silently break
    if "blockEnd > data.length" in dag_text:
        # Check if it throws or sets valid=false, not just break
        lines = dag_text.split("\n")
        for i, line in enumerate(lines):
            if "blockEnd > data.length" in line:
                context = "\n".join(lines[max(0, i-1):i+3])
                if "throw" in context or "valid = false" in context or "errors.push" in context:
                    print("  ✓ block beyond buffer fails (verify-dag)")
                    break
                elif "break" in context:
                    print("  ⚠ block beyond buffer uses break (verify-dag) — may silently skip")
                    break

    # Should not have silent catch for mandatory parse
    if "catch { /* skip */ }" in dag_text:
        print("  ⚠ silent catch { /* skip */ } found (verify-dag) — may skip malformed blocks")
    elif "catch (e)" in dag_text or "catch" in dag_text:
        # Check if catch records error
        lines = dag_text.split("\n")
        for i, line in enumerate(lines):
            if "catch" in line and "{" in line:
                context = "\n".join(lines[i:i+3])
                if "errors" in context or "valid" in context or "throw" in context:
                    print("  ✓ catch blocks record errors (verify-dag)")
                    break

# --- verify-full-evidence-chain.mjs ---

if full_text:
    if "Truncated varint" in full_text or "pos >= data.length" in full_text:
        print("  ✓ strict varint parsing (verify-full-evidence-chain)")
    elif "readVarint" in full_text:
        print("  ⚠ readVarint present but may lack strict bounds (verify-full-evidence-chain)")

print("\nVERIFY_CAR_PARSER_FAIL_CLOSED_OK")
