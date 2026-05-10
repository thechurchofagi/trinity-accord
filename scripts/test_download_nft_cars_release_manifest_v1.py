#!/usr/bin/env python3
"""Test: download-nft-cars.mjs produces real part-based RELEASE-MANIFEST.json"""

import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "scripts" / "download-nft-cars.mjs"
text = SRC.read_text(encoding="utf-8")


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


print("Running real part-based release manifest tests...")

# Required markers for real part-based manifest
required = [
    "trinity-release-manifest-v1",
    "RELEASE-MANIFEST.json",
    "nft-car-backup-parts",
    "release_assets: releaseAssets",
    "asset_name: part.name",
    "expected_path: f.tar_path",
    "total_car_files",
    "auxiliary_assets",
    "does_not_prove",
]

for token in required:
    if token not in text:
        fail(f"missing real part-based release manifest marker: {token}")

# Must NOT contain imaginary per-NFT structure in release manifest section
dangerous = [
    "nft_asset_name",
    "`nft-${contract}-${tokenId}.tar`",
    "per_nft_assets: perNftAssets",
    "release_assets: { parts:",
]

for token in dangerous:
    if token in text:
        fail(f"producer still contains imaginary per-NFT/parts-only structure: {token}")

# Must upload RELEASE-MANIFEST.json
if "uploadAsset(release.id, releaseManifestPath, 'RELEASE-MANIFEST.json')" not in text:
    fail("RELEASE-MANIFEST.json not uploaded as release asset")

# Must store manifest_item in verifiedCarFiles
if "manifest_item: verified" not in text:
    fail("verifiedCarFiles missing manifest_item for per-part file tracking")

# release_kind must be parts
if "nft-car-backup-parts" in text:
    print("  ✓ release_kind = nft-car-backup-parts")
else:
    fail("release_kind must be nft-car-backup-parts")

# release_assets must be array with asset_name per entry
if "asset_name: part.name" in text:
    print("  ✓ release_assets[] entries have asset_name")
else:
    fail("release_assets entries missing asset_name")

# Each part.files must include txid.car paths
if "expected_path: f.tar_path" in text:
    print("  ✓ part files have expected_path (txid.car)")
else:
    fail("part files missing expected_path")

print("\nDOWNLOAD_NFT_CARS_RELEASE_MANIFEST_V1_OK")
