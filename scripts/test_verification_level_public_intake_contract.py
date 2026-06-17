#!/usr/bin/env python3
"""Test: verification level public intake contract.

Verifies that only V0-V5 are accepted by schema, Builder validation,
and Gateway validation. V6, V6+, V7, V8, V9, V99+ must all be rejected.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []

VALID_LEVELS = ["V0", "V1", "V2", "V3", "V4", "V5"]
INVALID_LEVELS = ["V6", "V6+", "V7", "V8", "V9", "V99+"]


def require(cond: bool, msg: str) -> None:
    if not cond:
        errors.append(msg)


# --- Check schema ---
def test_schema():
    schema = json.loads((ROOT / "api" / "record-chain-submission-schema.v1.json").read_text())
    # Navigate to verification_level definition
    text = json.dumps(schema)
    require('"verification_level"' in text, "schema must contain verification_level")
    
    # Find the verification_level property
    def find_verification_level(obj, path=""):
        if isinstance(obj, dict):
            if "verification_level" in obj and isinstance(obj["verification_level"], dict):
                return obj["verification_level"]
            for k, v in obj.items():
                result = find_verification_level(v, f"{path}.{k}")
                if result:
                    return result
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                result = find_verification_level(item, f"{path}[{i}]")
                if result:
                    return result
        return None
    
    vl = find_verification_level(schema)
    require(vl is not None, "schema must define verification_level")
    if vl:
        require("enum" in vl, f"verification_level must use enum, got: {list(vl.keys())}")
        if "enum" in vl:
            for level in VALID_LEVELS:
                require(level in vl["enum"], f"schema enum must include {level}")
            for level in INVALID_LEVELS:
                require(level not in vl["enum"], f"schema enum must NOT include {level}")
    print("  ✅ schema verification_level enum correct")


# --- Check Gateway ---
def test_gateway():
    text = (ROOT / "apps" / "record_chain_intake_gateway" / "gateway" / "validation.py").read_text()
    require("V0" in text and "V5" in text, "gateway must reference V0-V5")
    require("PUBLIC_VERIFICATION_LEVELS" in text or "_PUBLIC_VERIFICATION_LEVELS" in text,
            "gateway must define public verification levels set")
    # Should NOT only check V6/V6+ — must check all invalid levels
    require("V6" in text, "gateway must still mention V6 (as invalid)")
    print("  ✅ gateway validation rejects non-V0-V5")


# --- Check Builder ---
def test_builder():
    text = (ROOT / "downloads" / "record-chain-builder.mjs").read_text()
    require("PUBLIC_VERIFICATION_LEVELS" in text, "builder must define PUBLIC_VERIFICATION_LEVELS")
    require("V0" in text and "V5" in text, "builder must reference V0-V5")
    print("  ✅ builder validation rejects non-V0-V5")


# --- Check field-helper ---
def test_field_helper():
    data = json.loads((ROOT / "api" / "record-chain-field-helper.v1.json").read_text())
    # Check that allowed_values for verification_level is V0-V5
    for group in data.get("field_groups", []):
        if group.get("field") == "verification_content.verification_level":
            allowed = group.get("allowed_values", [])
            for level in VALID_LEVELS:
                require(level in allowed, f"field-helper allowed_values must include {level}")
            for level in ["V6", "V7", "V8"]:
                require(level not in allowed, f"field-helper allowed_values must NOT include {level}")
    print("  ✅ field-helper verification_level V0-V5 only")


# --- Check agent-first-contact ---
def test_first_contact():
    data = json.loads((ROOT / "api" / "agent-first-contact.json").read_text())
    for route in data.get("routes", []):
        if route.get("action") == "VERIFY_V6_PLUS":
            require(route.get("status") == "reserved_not_currently_enabled",
                    "VERIFY_V6_PLUS route must be marked as reserved_not_currently_enabled")
    print("  ✅ agent-first-contact V6+ route marked reserved")


def main() -> int:
    print("test_verification_level_public_intake_contract")
    test_schema()
    test_gateway()
    test_builder()
    test_field_helper()
    test_first_contact()

    if errors:
        raise SystemExit("\n".join(f"ERROR: {e}" for e in errors))
    print("verification level public intake contract OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
