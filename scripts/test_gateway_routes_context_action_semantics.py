#!/usr/bin/env python3
"""Gateway routes must have correct context and action semantics.

Verifies that the gateway builder route map defines proper context/action
pairs for all active routes, and that the semantics match the expected
agent journey (preflight -> submit -> readback).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_ROUTE_KEYS = ["route", "echo_type", "preflight_path", "submit_path"]

EXPECTED_ROUTES = {
    "pure_echo": {"echo_type": "E1_recognition_echo"},
    "v0_v5_agent_declared_archive": {"echo_type": "E5_technical_audit_echo"},
    "guardian_application_stage_1": {"echo_type": "E1_recognition_echo"},
}


def main() -> int:
    errors: list[str] = []

    route_map_path = ROOT / "api" / "gateway-builder-route-map.v1.json"
    if not route_map_path.exists():
        print("FAIL: api/gateway-builder-route-map.v1.json missing")
        return 1

    data = json.loads(route_map_path.read_text(encoding="utf-8"))
    routes = data.get("routes", {})

    for route_name, expected in EXPECTED_ROUTES.items():
        if route_name not in routes:
            errors.append(f"missing route: {route_name}")
            continue
        route = routes[route_name]
        for key in REQUIRED_ROUTE_KEYS:
            if key not in route:
                errors.append(f"route {route_name} missing key: {key}")
        if route.get("echo_type") != expected["echo_type"]:
            errors.append(f"route {route_name}: echo_type mismatch, expected {expected['echo_type']}, got {route.get('echo_type')}")

    # Verify context/action pairs are consistent
    for route_name, route in routes.items():
        preflight = route.get("preflight_path", "")
        submit = route.get("submit_path", "")
        if not preflight.startswith("/gateway/"):
            errors.append(f"route {route_name}: preflight_path must start with /gateway/")
        if submit and not submit.startswith("/agent-submit"):
            errors.append(f"route {route_name}: submit_path must start with /agent-submit")

    if errors:
        print("FAIL: gateway route context/action semantics errors:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("PASS: gateway route context/action semantics valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
