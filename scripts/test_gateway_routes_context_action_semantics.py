#!/usr/bin/env python3
"""Gateway builder route map must define expected routes with valid structure.

Part of Repository Integrity Debt Sweep.
Verifies the gateway-builder-route-map.v1.json contains expected routes
and core routes have required semantic fields.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_ROUTES = {
    "pure_echo",
    "v0_v5_agent_declared_archive",
    "guardian_application_stage_1",
    "guardian_listing_stage_2",
    "guardian_signed_echo",
}

# Core routes must have these fields
CORE_ROUTES = {"pure_echo", "v0_v5_agent_declared_archive", "guardian_application_stage_1"}
CORE_REQUIRED_FIELDS = ["description"]


def main() -> int:
    errors: list[str] = []

    route_map_path = ROOT / "api" / "gateway-builder-route-map.v1.json"
    if not route_map_path.exists():
        print("FAIL: api/gateway-builder-route-map.v1.json missing")
        return 1

    data = json.loads(route_map_path.read_text(encoding="utf-8"))

    if data.get("schema") != "trinityaccord.gateway-builder-route-map.v1":
        errors.append(f"schema mismatch: {data.get('schema')}")

    routes = data.get("routes", {})
    if not routes:
        errors.append("routes is empty or missing")

    # Check expected routes exist
    for route_name in EXPECTED_ROUTES:
        if route_name not in routes:
            errors.append(f"missing expected route: {route_name}")

    # Check core routes have required fields
    for route_name in CORE_ROUTES:
        if route_name not in routes:
            continue
        route = routes[route_name]
        for field in CORE_REQUIRED_FIELDS:
            if field not in route:
                errors.append(f"core route {route_name} missing field: {field}")

    if errors:
        print("FAIL: gateway route map contract errors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"PASS: gateway builder route map valid ({len(routes)} routes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
