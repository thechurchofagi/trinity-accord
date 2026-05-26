#!/usr/bin/env python3
"""Live discovery smoke must diagnose cache/edge inconsistencies."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
script = ROOT / "scripts" / "smoke_live_discovery_contract.py"

text = script.read_text(encoding="utf-8")

required = [
    "fetch_json_with_headers",
    "with_cache_bust",
    "print_cache_headers",
    "cache-busted live links",
    "canonical and cache-busted live links.json source_digest differ",
    "cache_busted",
    "strict_digest",
    "source_digest mismatch",
    "CDN/edge/cache inconsistency",
]

missing = [phrase for phrase in required if phrase not in text]
if missing:
    print("FAIL: live discovery smoke cache diagnostics missing:")
    for phrase in missing:
        print("  -", phrase)
    sys.exit(1)

print("PASS: live discovery smoke includes cache/edge diagnostics")
