#!/usr/bin/env python3
"""auto_register_guardian_from_gateway_issues.py must not hardcode stale E7 propagation."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "scripts" / "auto_register_guardian_from_gateway_issues.py"
text = path.read_text(encoding="utf-8")

if "E7_propagation_echo" in text or "LISTING_NOT_E7" in text:
    print("FAIL: stale E7 Guardian listing logic remains")
    sys.exit(1)

if 'canonical_echo_type_for_id("E6")' not in text and "GUARDIAN_LISTING_ECHO_TYPE" not in text:
    print("FAIL: Guardian listing type is not tied to canonical E6 taxonomy")
    sys.exit(1)

print("PASS: no stale E7 Guardian listing logic")
