#!/usr/bin/env python3
"""TAXONOMY-001: Echo taxonomy deprecation test.

Echo types are deprecated. Verify the module returns empty/deprecated values.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from protocol_echo_types import canonical_echo_type_for_id, allowed_canonical_echo_types, load_echo_types

# Verify empty types
types = load_echo_types()
if types != []:
    print(f"FAIL: load_echo_types() should return empty list, got: {types}")
    sys.exit(1)

# Verify empty allowed set
allowed = allowed_canonical_echo_types()
if allowed != set():
    print(f"FAIL: allowed_canonical_echo_types() should return empty set, got: {allowed}")
    sys.exit(1)

# Verify legacy constants are still accessible for backward compatibility
from protocol_echo_types import LEGACY_ECHO_TYPES
if "E6_propagation_echo" not in LEGACY_ECHO_TYPES:
    print("FAIL: LEGACY_ECHO_TYPES missing E6_propagation_echo for backward compat")
    sys.exit(1)

print("PASS: Echo taxonomy deprecation verified")
