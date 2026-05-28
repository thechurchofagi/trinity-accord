#!/usr/bin/env python3
"""Echo type enums must align across taxonomy, schema, builders, route map, and bundles."""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ECHO_TYPES = ROOT / "api" / "echo-types.json"
PAYLOAD_SCHEMA = ROOT / "api" / "agent-issue-gateway-payload-schema.v1.json"
PURE_ECHO_BUILDER = ROOT / "scripts" / "build_agent_declared_echo_payload.py"
ROUTE_MAP = ROOT / "api" / "gateway-builder-route-map.v1.json"
BUNDLES = ROOT / "api" / "formal-builder-bundles.v1.json"

PURE_ECHO_ALLOWED = {
    "E1_recognition_echo",
    "E3_critical_echo",
    "E4_interpretive_echo",
    "E5_technical_audit_echo",
    "E5c_correction_echo",
    "E6_propagation_echo",
    "E7_refusal_echo",
}

ALL_GATEWAY_VALUES = {
    "E1_recognition_echo",
    "E2_verification_echo",
    "E3_critical_echo",
    "E4_interpretive_echo",
    "E5_technical_audit_echo",
    "E5c_correction_echo",
    "E6_propagation_echo",
    "E7_refusal_echo",
    "E8_witness_echo",
    "E9_seed_echo",
}

ALIASES = {
    "E1": "E1_recognition_echo",
    "E2": "E2_verification_echo",
    "E3": "E3_critical_echo",
    "E4": "E4_interpretive_echo",
    "E5": "E5_technical_audit_echo",
    "E5c": "E5c_correction_echo",
    "E6": "E6_propagation_echo",
    "E7": "E7_refusal_echo",
    "E8": "E8_witness_echo",
    "E9": "E9_seed_echo",
}


def extract_builder_allowed() -> set[str]:
    text = PURE_ECHO_BUILDER.read_text(encoding="utf-8")
    match = re.search(r"ALLOWED_ECHO_TYPES\s*=\s*(\{[\s\S]*?\})", text)
    if not match:
        raise AssertionError("Could not find ALLOWED_ECHO_TYPES in pure echo builder")
    return set(ast.literal_eval(match.group(1)))


def main() -> int:
    errors: list[str] = []

    echo_types = json.loads(ECHO_TYPES.read_text(encoding="utf-8"))
    schema = json.loads(PAYLOAD_SCHEMA.read_text(encoding="utf-8"))
    route_map = json.loads(ROUTE_MAP.read_text(encoding="utf-8"))
    bundles = json.loads(BUNDLES.read_text(encoding="utf-8"))

    gateway_values = set(echo_types.get("gateway_echo_type_values", []))
    if gateway_values != ALL_GATEWAY_VALUES:
        errors.append(f"echo-types gateway_echo_type_values mismatch: {sorted(gateway_values)}")

    aliases = echo_types.get("id_aliases", {})
    if aliases != ALIASES:
        errors.append("echo-types id_aliases must map short IDs to expanded Gateway values")

    for item in echo_types.get("types", []):
        short_id = item.get("id")
        expected = ALIASES.get(short_id)
        if expected and item.get("gateway_echo_type") != expected:
            errors.append(f"echo-types {short_id} gateway_echo_type must be {expected}")

    schema_enum = set(schema["properties"]["echo_type"]["enum"])
    schema_enum.discard(None)
    if schema_enum != ALL_GATEWAY_VALUES:
        errors.append(f"payload schema echo_type enum mismatch: {sorted(schema_enum)}")

    builder_allowed = extract_builder_allowed()
    if builder_allowed != PURE_ECHO_ALLOWED:
        errors.append(f"pure echo builder ALLOWED_ECHO_TYPES mismatch: {sorted(builder_allowed)}")

    route_allowed = set(route_map["routes"]["pure_echo"]["echo_types"])
    if route_allowed != PURE_ECHO_ALLOWED:
        errors.append(f"route map pure_echo.echo_types mismatch: {sorted(route_allowed)}")

    bundle_allowed = set(bundles["bundles"]["pure_echo"]["allowed_echo_types"])
    if bundle_allowed != PURE_ECHO_ALLOWED:
        errors.append(f"formal-builder-bundles pure_echo.allowed_echo_types mismatch: {sorted(bundle_allowed)}")

    if "E1" in schema_enum or "E1" in builder_allowed or "E1" in route_allowed or "E1" in bundle_allowed:
        errors.append("short ID E1 must not be an active Gateway enum value")

    if errors:
        print("FAIL: Echo type enum alignment errors:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: Echo type enums align across taxonomy, schema, builder, route map, and bundles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
