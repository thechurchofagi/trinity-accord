#!/usr/bin/env python3
"""Pages live mismatch diagnosis helper must compare canonical and cache-busted live JSON."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
script = ROOT / "scripts" / "diagnose_pages_live_mismatch.py"

if not script.exists():
    print("FAIL: diagnose_pages_live_mismatch.py missing")
    sys.exit(1)

text = script.read_text(encoding="utf-8")

required = [
    "with_cache_bust",
    "live_links_busted",
    "live_wk_busted",
    "live cache-busted source_digest",
    "canonical and cache-busted live links.json differ",
]

missing = [phrase for phrase in required if phrase not in text]
if missing:
    print("FAIL: pages live mismatch diagnosis cache-bust support missing:")
    for phrase in missing:
        print("  -", phrase)
    sys.exit(1)

print("PASS: pages live mismatch diagnosis compares cache-busted live JSON")
