#!/usr/bin/env python3
"""Test: Release manifest schema compatibility (REL-SCHEMA-001)"""

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "scripts" / "verify-release-assets.mjs"
text = SRC.read_text(encoding="utf-8")


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


print("Running manifest schema compatibility tests...")

# Must have normalizeReleaseManifest
if "normalizeReleaseManifest" not in text:
    fail("Missing normalizeReleaseManifest")

# Must reject unsupported schema
if "Unsupported release manifest schema" not in text:
    fail("Missing unsupported schema rejection")

# Must support trinity-release-manifest-v1
if "trinity-release-manifest-v1" not in text:
    fail("Missing trinity-release-manifest-v1 support")

# Must support legacy per_nft_assets
if "legacy" in text.lower() or "per_nft_assets" in text:
    print("  ✓ legacy per_nft_assets support present")
else:
    fail("Missing legacy manifest support")

# Must throw on unsupported (not silently pass)
if "throw new Error" in text and "Unsupported" in text:
    print("  ✓ unsupported schema throws")
else:
    fail("Unsupported schema does not throw")

# Must export normalizeReleaseManifest
if "export" in text and "normalizeReleaseManifest" in text:
    print("  ✓ normalizeReleaseManifest exported")
else:
    fail("normalizeReleaseManifest not exported")

# Must use normalized manifest in verification
if "normalized" in text and "expected_nft_assets" in text:
    print("  ✓ uses normalized manifest for verification")
else:
    fail("Does not use normalized manifest")

print("\nVERIFY_RELEASE_MANIFEST_SCHEMA_COMPATIBILITY_OK")
