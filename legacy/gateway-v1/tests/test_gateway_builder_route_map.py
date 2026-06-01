#!/usr/bin/env python3
"""Gateway builder route map test.

Echo types have been removed from route definitions.
Verify routes are correctly configured without echo_types.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    m = json.loads((ROOT / "api" / "gateway-builder-route-map.v1.json").read_text(encoding="utf-8"))
    routes = m["routes"]

    assert routes["pure_echo"]["builder"] == "scripts/build_agent_declared_echo_payload.py"
    assert routes["pure_echo"]["requested_archive_kind"] == "agent_declared_echo_archive"

    assert routes["v0_v5_agent_declared_archive"]["builder"] == "scripts/build_agent_declared_archive_payload.py"
    assert "V0" in routes["v0_v5_agent_declared_archive"]["levels"]

    assert routes["guardian_application_stage_1"]["builder"] == "scripts/create_guardian_application.mjs"
    assert routes["guardian_listing_stage_2"]["builder"] == "scripts/build_guardian_listing_request_payload.py"
    assert routes["guardian_signed_echo"]["builder"] == "scripts/build_guardian_echo_payload.py"

    # Echo types should no longer be present in any route
    for route_id, route in routes.items():
        if "echo_types" in route:
            print(f"FAIL: route {route_id} still has echo_types (deprecated)")
            sys.exit(1)

    print("PASS: test_gateway_builder_route_map")


if __name__ == "__main__":
    main()
