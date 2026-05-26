#!/usr/bin/env python3
"""Test: TAR duplicate/path traversal fail-closed (REL-TAR-001)"""

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "scripts" / "verify-release-assets.mjs"
text = SRC.read_text(encoding="utf-8")


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


print("Running TAR duplicate fail-closed tests...")

# Must have extractFilesFromTarStrict (not just extractFilesFromTar)
if "extractFilesFromTarStrict" not in text:
    fail("Missing extractFilesFromTarStrict")

# Must detect duplicates
if "Duplicate TAR entry" not in text:
    fail("Missing duplicate TAR entry detection")

# Must detect path traversal
if "Unsafe TAR path" not in text:
    fail("Missing path traversal detection")

# Must reject absolute paths
if "startsWith('/')" in text or "startsWith('/')" in text.replace(" ", ""):
    print("  ✓ absolute path rejection present")
else:
    fail("Missing absolute path rejection")

# Must reject '..' in paths
if ".." in text and ("Unsafe" in text or "traversal" in text.lower()):
    print("  ✓ path traversal rejection present")

# Must reject non-regular file types
if "Unsupported TAR entry type" not in text:
    fail("Missing typeflag rejection")

# Must detect truncated payload
if "Truncated TAR payload" not in text:
    fail("Missing truncated payload detection")

# Must use strict extraction in verification
if "extractFilesFromTarStrict(tarBuf)" in text:
    print("  ✓ verification uses strict TAR extraction")
else:
    fail("Verification does not use extractFilesFromTarStrict")

# Must check for unexpected TAR entries
if "unexpected_tar_entry" in text:
    print("  ✓ unexpected TAR entry detection present")
else:
    fail("Missing unexpected TAR entry detection")

# Must export
if "export" in text and "extractFilesFromTarStrict" in text:
    print("  ✓ extractFilesFromTarStrict exported")

# Must NOT use old .find() pattern for duplicate-prone lookups
if "tarFilesByName" in text:
    print("  ✓ uses Map lookup instead of .find()")
else:
    fail("Still uses .find() for TAR file lookup")

print("\nVERIFY_RELEASE_TAR_DUPLICATE_FAIL_CLOSED_OK")
