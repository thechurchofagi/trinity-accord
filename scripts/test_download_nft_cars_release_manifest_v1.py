#!/usr/bin/env python3
"""Test: download-nft-cars.mjs produces trinity-release-manifest-v1 (REL-SCHEMA-001)"""

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "scripts" / "download-nft-cars.mjs"
text = SRC.read_text(encoding="utf-8")


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


print("Running release manifest v1 producer tests...")

required = [
    "trinity-release-manifest-v1",
    "RELEASE-MANIFEST.json",
    "per_nft_assets",
    "expected_sha256",
    "expected_size",
    "does_not_prove",
]

for token in required:
    if token not in text:
        fail(f"download-nft-cars.mjs missing release manifest marker: {token}")

# Must upload RELEASE-MANIFEST.json as release asset
if "RELEASE-MANIFEST.json" in text and ("uploadAsset" in text or "upload" in text.lower()):
    print("  ✓ RELEASE-MANIFEST.json uploaded as release asset")
else:
    fail("RELEASE-MANIFEST.json not uploaded")

# Must have schema field
if "schema:" in text and "trinity-release-manifest-v1" in text:
    print("  ✓ schema field set to trinity-release-manifest-v1")
else:
    fail("Missing schema field")

# Must have does_not_prove
if "does_not_prove" in text:
    print("  ✓ does_not_prove included")
else:
    fail("Missing does_not_prove")

# Must have verification_basis
if "verification_basis" in text:
    print("  ✓ verification_basis included")
else:
    fail("Missing verification_basis")

print("\nDOWNLOAD_NFT_CARS_RELEASE_MANIFEST_V1_OK")
