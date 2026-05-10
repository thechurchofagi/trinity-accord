#!/usr/bin/env python3
"""Test: CAR parser fail-closed behavior (REL-CAR-001)

Hard-fails if verify-dag-and-signed-cids.mjs or verify-full-evidence-chain.mjs
still contain unsafe CAR parsing patterns.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


def check_script(name, path):
    if not path.exists():
        fail(f"{name} not found at {path}")
    text = path.read_text(encoding="utf-8")

    # Must have readVarintStrict
    if "readVarintStrict" not in text:
        fail(f"{name}: Missing readVarintStrict")

    # Must have bounds checks
    for token in ["Truncated", "Overlong", "Unsafe"]:
        if token not in text:
            fail(f"{name}: Missing {token} error in strict varint")

    # Must have block length exceeds buffer error
    if "CAR block length exceeds buffer" not in text:
        fail(f"{name}: Missing block length exceeds buffer error")

    # Must have header length exceeds buffer
    if "CAR header length exceeds buffer" not in text:
        fail(f"{name}: Missing header length exceeds buffer error")

    # Must have duplicate CID conflict detection
    if "Duplicate CID with conflicting block data" not in text:
        fail(f"{name}: Missing duplicate CID conflict detection")

    # Must NOT have silent catch
    if "catch { /* skip */ }" in text:
        fail(f"{name}: Silent catch {{ /* skip */ }} remains")

    # Must NOT have blockEnd > data.length break pattern
    if re.search(r"blockEnd\s*>\s*carData\.length\)\s*break", text):
        fail(f"{name}: blockEnd > carData.length still uses break")

    # readVarint must be a strict wrapper (or not exist)
    if "function readVarint(data, offset)" in text:
        if "readVarintStrict(data, offset" not in text:
            fail(f"{name}: readVarint exists but is not a strict wrapper")

    # Must have consumeVarint for CID parsing
    if "consumeVarint" not in text:
        fail(f"{name}: Missing consumeVarint helper for bounds-checked CID parsing")

    print(f"  ✓ {name}: strict CAR parser verified")


print("Running CAR parser fail-closed tests...")

check_script("verify-dag-and-signed-cids.mjs", ROOT / "scripts" / "verify-dag-and-signed-cids.mjs")
check_script("verify-full-evidence-chain.mjs", ROOT / "scripts" / "verify-full-evidence-chain.mjs")

# Also verify verify-release-assets.mjs has strict CAR header parsing
verifier = ROOT / "scripts" / "verify-release-assets.mjs"
if verifier.exists():
    text = verifier.read_text(encoding="utf-8")
    if "Truncated CAR header" not in text:
        fail("verify-release-assets.mjs: Missing strict CAR header parsing")
    if "Number.isSafeInteger" not in text:
        fail("verify-release-assets.mjs: Missing safe integer check")
    print("  ✓ verify-release-assets.mjs: strict CAR header parsing verified")

print("\nVERIFY_CAR_PARSER_FAIL_CLOSED_OK")
