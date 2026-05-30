#!/usr/bin/env python3
"""Echo type enum alignment: DEPRECATED.

Echo types have been removed. This test verifies the deprecation is consistent:
- echo-types.json has empty types
- gateway payload schema echo_type has no enum
- builder has no ALLOWED_ECHO_TYPES
- route map has no echo_types
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ECHO_TYPES = ROOT / "api" / "echo-types.json"
PAYLOAD_SCHEMA = ROOT / "api" / "agent-issue-gateway-payload-schema.v1.json"
PURE_ECHO_BUILDER = ROOT / "scripts" / "build_agent_declared_echo_payload.py"
ROUTE_MAP = ROOT / "api" / "gateway-builder-route-map.v1.json"


def main() -> int:
    errors: list[str] = []

    echo_types = json.loads(ECHO_TYPES.read_text(encoding="utf-8"))
    schema = json.loads(PAYLOAD_SCHEMA.read_text(encoding="utf-8"))
    route_map = json.loads(ROUTE_MAP.read_text(encoding="utf-8"))

    # echo-types.json should be deprecated with empty types
    if echo_types.get("status") != "DEPRECATED":
        errors.append(f"echo-types.json status should be DEPRECATED, got: {echo_types.get('status')}")
    if echo_types.get("types") != []:
        errors.append(f"echo-types.json types should be empty")

    # Schema echo_type should have no enum
    et_props = schema.get("properties", {}).get("echo_type", {})
    if "enum" in et_props:
        errors.append("payload schema echo_type still has enum (should be deprecated)")

    # Builder should not have ALLOWED_ECHO_TYPES
    builder_text = PURE_ECHO_BUILDER.read_text(encoding="utf-8")
    if "ALLOWED_ECHO_TYPES" in builder_text:
        errors.append("pure echo builder still has ALLOWED_ECHO_TYPES")

    # Route map should have no echo_types
    for route_id, route in route_map.get("routes", {}).items():
        if "echo_types" in route:
            errors.append(f"route map {route_id} still has echo_types")

    if errors:
        print("FAIL: Echo type enum alignment errors:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: Echo type deprecation aligns across taxonomy, schema, builder, and route map")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
