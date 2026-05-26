#!/usr/bin/env python3
"""Document current policy for missing timestamp on Guardian body fallback."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from auto_register_guardian_from_gateway_issues import is_before_body_listing_fallback_cutoff

if is_before_body_listing_fallback_cutoff({}) is not True:
    print("FAIL: current compatibility policy expects missing timestamp to be treated as before cutoff")
    sys.exit(1)

print("PASS: Guardian body fallback missing timestamp compatibility policy documented")
