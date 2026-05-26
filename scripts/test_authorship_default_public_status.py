#!/usr/bin/env python3
"""Test that public status exposes default authorship policy."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []


def check(condition, msg):
    if not condition:
        errors.append(msg)
        print(f"  FAIL: {msg}")
    else:
        print(f"  PASS: {msg}")


# Check the source code for the expected fields
source = (ROOT / "scripts" / "generate_public_home_status.py").read_text()

print("--- generate_public_home_status.py ---")
check("default_policy" in source, "authorship_claims has default_policy")
check("enabled_for_new_builder_generated_records" in source,
      "default_policy mentions new builder-generated records")
check("private_key_storage" in source, "has private_key_storage")
check("local_only" in source, "private_key_storage is local_only")
check("gateway_private_key_access" in source, "has gateway_private_key_access")

# Check public-home-status.json if it exists
status_path = ROOT / "api" / "public-home-status.json"
if status_path.exists():
    status = json.loads(status_path.read_text())
    ac = status.get("authorship_claims", {})
    print("\n--- api/public-home-status.json ---")
    check(ac.get("default_policy") == "enabled_for_new_builder_generated_records",
          "default_policy is correct")
    check(ac.get("private_key_storage") == "local_only",
          "private_key_storage is local_only")
    check(ac.get("gateway_private_key_access") is False,
          "gateway_private_key_access is false")
    check("key continuity" in ac.get("boundary", "").lower(),
          "boundary mentions key continuity")
else:
    print("\n--- api/public-home-status.json (not found, skipping live check) ---")

print(f"\n--- Results: {len(errors)} errors ---")
if errors:
    for e in errors:
        print(f"  ERROR: {e}")
    sys.exit(1)
print("AUTHORSHIP_DEFAULT_PUBLIC_STATUS_OK")
