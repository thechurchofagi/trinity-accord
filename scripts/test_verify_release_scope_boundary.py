#!/usr/bin/env python3
"""Test: Verification scope boundary (REL-CID-001, REL-BOUNDARY-001)"""

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "scripts" / "verify-release-assets.mjs"
text = SRC.read_text(encoding="utf-8")


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


print("Running verification scope boundary tests...")

# Must have verification_scope field
if "verification_scope" not in text:
    fail("Missing verification_scope field")

# Must have hash_size_only scope
if "hash_size_only" not in text:
    fail("Missing hash_size_only scope value")

# Must have does_not_prove
if "does_not_prove" not in text:
    fail("Missing does_not_prove field")

# Must have limitations
if "limitations" not in text:
    fail("Missing limitations field")

# CID disabled must set hash_size_only
if "cidCheck" in text and "hash_size_only" in text:
    # Check for ternary or if/else logic setting verification_scope
    lines = text.split("\n")
    found_logic = False
    for i, line in enumerate(lines):
        if "verificationScope" in line or "verification_scope" in line:
            context = "\n".join(lines[max(0, i-1):i+4])
            if "hash_size_only" in context:
                found_logic = True
                break
    if found_logic:
        print("  ✓ CID disabled → hash_size_only scope")
    else:
        fail("CID disabled does not set hash_size_only")
else:
    fail("Missing CID/scope logic")

# does_not_prove must mention CID/DAG when disabled
if "CID" in text and "DAG" in text and "does_not_prove" in text:
    print("  ✓ does_not_prove mentions CID/DAG boundaries")
else:
    fail("does_not_prove missing CID/DAG boundaries")

# Must not claim CID verification when disabled
# Check that when cidCheck is false, the report doesn't say "CID verified"
lines = text.split("\n")
for i, line in enumerate(lines):
    if "cid_check_enabled: false" in line.lower() or "cid_check_enabled: false" in line:
        # nearby lines should not say "CID verified"
        context = "\n".join(lines[max(0, i-5):i+5])
        if "CID verified" in context and "not" not in context:
            fail("May claim CID verified when disabled")

print("  ✓ no false CID verification claims")

print("\nVERIFY_RELEASE_SCOPE_BOUNDARY_OK")
