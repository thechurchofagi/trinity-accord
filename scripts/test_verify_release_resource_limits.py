#!/usr/bin/env python3
"""Test: Verifier resource limits (REL-RESOURCE-001)"""

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "scripts" / "verify-release-assets.mjs"
text = SRC.read_text(encoding="utf-8")


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


print("Running resource limits tests...")

# Must have MAX_RELEASE_ASSET_BYTES
if "MAX_RELEASE_ASSET_BYTES" not in text:
    fail("Missing MAX_RELEASE_ASSET_BYTES")

# Must have MAX_TOTAL_RELEASE_BYTES
if "MAX_TOTAL_RELEASE_BYTES" not in text:
    fail("Missing MAX_TOTAL_RELEASE_BYTES")

print("  ✓ MAX_RELEASE_ASSET_BYTES defined")
print("  ✓ MAX_TOTAL_RELEASE_BYTES defined")

# Must check content-length
if "content-length" in text.lower() and "MAX_RELEASE_ASSET_BYTES" in text:
    print("  ✓ content-length cap check present")
else:
    fail("Missing content-length cap check")

# Must check actual buffer size
if "buf.length > MAX_RELEASE_ASSET_BYTES" in text:
    print("  ✓ actual buffer size cap present")
else:
    fail("Missing actual buffer size cap")

# Must check total downloaded bytes
if "totalDownloadedBytes" in text and "MAX_TOTAL_RELEASE_BYTES" in text:
    print("  ✓ total downloaded bytes cap present")
else:
    fail("Missing total downloaded bytes cap")

# Must have parseBoundedIntEnv
if "parseBoundedIntEnv" in text or "parseBoundedInt" in text:
    print("  ✓ bounded integer parsing present")
else:
    fail("Missing bounded integer parsing")

# Concurrency must be bounded
if "VERIFY_CONCURRENCY" in text and ("parseBoundedInt" in text or "1, 25" in text):
    print("  ✓ concurrency is bounded")
else:
    fail("Concurrency not bounded")

print("\nVERIFY_RELEASE_RESOURCE_LIMITS_OK")
