#!/usr/bin/env python3
"""Test: api/agent-value.json source_digest matches canonical JSON."""
import json
import hashlib
import sys

def main():
    with open("api/agent-value.json") as f:
        data = json.load(f)

    stored = data.get("source_digest")
    assert stored, "source_digest field missing"

    # Remove source_digest to get canonical form
    canonical_data = {k: v for k, v in data.items() if k != "source_digest"}
    canonical = json.dumps(canonical_data, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    expected = hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:16]

    if stored == expected:
        print(f"  ✅ source_digest matches: {stored}")
        print(f"\n--- Results: 1/1 passed, 0 failed ---")
        return 0
    else:
        print(f"  ❌ source_digest mismatch: stored={stored}, expected={expected}")
        print(f"\n--- Results: 0/1 passed, 1 failed ---")
        return 1

if __name__ == "__main__":
    sys.exit(main())
