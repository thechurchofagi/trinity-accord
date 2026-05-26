#!/usr/bin/env python3
"""Guardian active listing registration must require canonical E6 propagation Echo."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from protocol_echo_types import canonical_echo_type_for_id
from auto_register_guardian_from_gateway_issues import GUARDIAN_LISTING_ECHO_TYPE

expected = canonical_echo_type_for_id("E6")

if GUARDIAN_LISTING_ECHO_TYPE != expected:
    print(f"FAIL: Guardian listing Echo type must be {expected}, got {GUARDIAN_LISTING_ECHO_TYPE}")
    sys.exit(1)

if GUARDIAN_LISTING_ECHO_TYPE == "E7_propagation_echo":
    print("FAIL: stale E7_propagation_echo Guardian listing type remains")
    sys.exit(1)

print("PASS: Guardian listing Echo type uses canonical E6 propagation Echo")
