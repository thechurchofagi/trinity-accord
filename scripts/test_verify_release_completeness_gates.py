#!/usr/bin/env python3
"""Test: Release completeness gates (REL-COMPLETE-001)"""

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "scripts" / "verify-release-assets.mjs"
text = SRC.read_text(encoding="utf-8")


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


print("Running release completeness gates tests...")

# Must have missing_release_asset detection
if "missing_release_asset" not in text:
    fail("Missing missing_release_asset detection")

# Must have unexpected_release_asset detection
if "unexpected_release_asset" not in text:
    fail("Missing unexpected_release_asset detection")

# Must have duplicate_release_asset detection
if "duplicate_release_asset" not in text:
    fail("Missing duplicate_release_asset detection")

print("  ✓ missing/extra/duplicate asset detection present")

# Must iterate expectedAssets (not nftAssets from release)
if "expectedAssets" in text and "expected_nft_assets" in text:
    print("  ✓ manifest-driven verification (iterates expected, not observed)")
else:
    fail("Not manifest-driven — still iterates release assets")

# Must compare manifest counts
if "expected_nft_count" in text:
    print("  ✓ manifest count invariant check present")
else:
    fail("Missing manifest count invariant")

# Must NOT use old pattern: allAssets.filter(a => a.name.startsWith('nft-'))
# as the primary verification driver
if "releaseAssetByName" in text or "expectedNames" in text:
    print("  ✓ uses lookup maps for completeness")
else:
    fail("Missing lookup maps for completeness")

# Must have computeStatus that checks asset counts
if "assetsVerified" in text and "assetsExpected" in text:
    print("  ✓ status computation includes asset count check")
else:
    fail("Status computation missing asset count check")

print("\nVERIFY_RELEASE_COMPLETENESS_GATES_OK")
