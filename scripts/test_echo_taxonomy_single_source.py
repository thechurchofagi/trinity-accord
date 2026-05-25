#!/usr/bin/env python3
"""TAXONOMY-001: Echo taxonomy single source loader test."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from protocol_echo_types import canonical_echo_type_for_id, allowed_canonical_echo_types

checks = {
    "E6": "E6_propagation_echo",
    "E7": "E7_refusal_echo",
    "E4": "E4_interpretive_echo",
    "E5": "E5_technical_audit_echo",
}

for eid, expected in checks.items():
    got = canonical_echo_type_for_id(eid)
    if got != expected:
        print(f"FAIL: {eid} expected {expected}, got {got}")
        sys.exit(1)

allowed = allowed_canonical_echo_types()
if "E7_propagation_echo" in allowed:
    print("FAIL: E7_propagation_echo is incorrectly allowed by canonical taxonomy")
    sys.exit(1)

if "E6_propagation_echo" not in allowed:
    print("FAIL: E6_propagation_echo missing from allowed set")
    sys.exit(1)

print("PASS: Echo taxonomy single source works")
