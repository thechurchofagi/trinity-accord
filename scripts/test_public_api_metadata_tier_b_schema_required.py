#!/usr/bin/env python3
"""Tier B public route/context/status APIs must require schema identity."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / "scripts" / "validate_public_api_metadata.py").read_text(encoding="utf-8")

bad_fragments = [
    "Schema identity is recommended but not enforced for legacy route/context/status APIs.",
]

ok = True

for frag in bad_fragments:
    if frag in text:
        print(f"FAIL: stale weak Tier B schema policy remains: {frag}")
        ok = False

if "missing schema/$schema" not in text:
    print("FAIL: validate_minimal_public_api does not enforce missing schema/$schema")
    ok = False

if "TIER_B_SCHEMA_IDENTITY_EXEMPT" not in text:
    print("FAIL: missing explicit Tier B schema identity exemption set")
    ok = False

if not ok:
    sys.exit(1)

print("PASS: Tier B public API schema identity is enforced")
