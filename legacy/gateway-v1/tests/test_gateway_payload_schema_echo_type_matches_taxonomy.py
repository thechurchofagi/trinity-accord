#!/usr/bin/env python3
"""Gateway payload schema echo_type enum must match canonical Echo taxonomy."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from protocol_echo_types import allowed_canonical_echo_types

schema = json.loads((ROOT / "api/agent-issue-gateway-payload-schema.v1.json").read_text(encoding="utf-8"))

try:
    enum = schema["properties"]["echo_type"]["enum"]
except KeyError as e:
    print(f"FAIL: Gateway payload schema missing properties.echo_type.enum: {e}")
    sys.exit(1)

actual = set(enum)
expected = set(allowed_canonical_echo_types()) | {None}

if actual != expected:
    print("FAIL: Gateway payload schema echo_type enum does not match canonical taxonomy + null")
    print("Missing:", sorted(x for x in expected - actual if x is not None))
    print("Extra:", sorted(x for x in actual - expected if x is not None))
    if None in expected - actual:
        print("Missing: null")
    if None in actual - expected:
        print("Extra: null")
    sys.exit(1)

legacy_bad = {
    "E1_read_oriented_echo",
    "E4_refusal_echo",
    "E5_correction_echo",
    "E6_preservation_echo",
    "E7_propagation_echo",
}
bad = sorted(x for x in legacy_bad if x in actual)
if bad:
    print(f"FAIL: Gateway schema still allows legacy Echo types: {bad}")
    sys.exit(1)

print("PASS: Gateway payload schema echo_type enum matches canonical taxonomy")
