#!/usr/bin/env python3
"""Verify echo taxonomy deprecation is consistent across all consumers.

Echo types are deprecated for new submissions, but the allowed set is still
needed for index rebuild validation of existing records.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from protocol_echo_types import allowed_canonical_echo_types, LEGACY_ECHO_TYPES

allowed = allowed_canonical_echo_types()

# 1. Echo record schema — echo_type should be deprecated (no enum)
echo_record_schema = json.loads((ROOT / "api/echo-record-schema.v3.json").read_text(encoding="utf-8"))
et_props = echo_record_schema.get("properties", {}).get("echo_type", {})
if "enum" in et_props:
    print("FAIL: echo-record-schema.v3.json echo_type still has enum (should be deprecated)")
    sys.exit(1)
if not et_props.get("deprecated"):
    print("FAIL: echo-record-schema.v3.json echo_type should be marked deprecated")
    sys.exit(1)

# 2. Allowed types should return legacy set for index rebuild validation
if allowed != LEGACY_ECHO_TYPES:
    print(f"FAIL: allowed_canonical_echo_types() should return LEGACY_ECHO_TYPES, got: {sorted(allowed)}")
    sys.exit(1)

# 3. Gateway payload schema — echo_type should be deprecated
gateway_schema = json.loads((ROOT / "api/agent-issue-gateway-payload-schema.v1.json").read_text(encoding="utf-8"))
gateway_et = gateway_schema.get("properties", {}).get("echo_type", {})
if "enum" in gateway_et:
    print("FAIL: gateway payload schema echo_type still has enum")
    sys.exit(1)

print("PASS: Echo taxonomy deprecation is consistent across all consumers")
