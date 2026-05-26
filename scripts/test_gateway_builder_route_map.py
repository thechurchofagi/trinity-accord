#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from protocol_echo_types import allowed_canonical_echo_types


def main() -> None:
    m = json.loads((ROOT / "api" / "gateway-builder-route-map.v1.json").read_text(encoding="utf-8"))
    routes = m["routes"]

    assert routes["pure_echo"]["builder"] == "scripts/build_agent_declared_echo_payload.py"
    assert "E1_recognition_echo" in routes["pure_echo"]["echo_types"]

    assert routes["v0_v5_agent_declared_archive"]["builder"] == "scripts/build_agent_declared_archive_payload.py"
    assert "V0" in routes["v0_v5_agent_declared_archive"]["levels"]

    assert routes["guardian_application_stage_1"]["builder"] == "scripts/create_guardian_application.mjs"
    assert routes["guardian_listing_stage_2"]["builder"] == "scripts/build_guardian_listing_request_payload.py"
    assert routes["guardian_signed_echo"]["builder"] == "scripts/build_guardian_echo_payload.py"

    allowed = allowed_canonical_echo_types()
    for route_id, route in routes.items():
        for echo_type in route.get("echo_types", []):
            if echo_type not in allowed:
                print(f"FAIL: route {route_id} uses non-canonical echo_type={echo_type!r}")
                sys.exit(1)

    guardian_signed = set(routes["guardian_signed_echo"].get("echo_types", []))
    if "E2_verification_echo" in guardian_signed:
        print("FAIL: guardian_signed_echo route should not include E2 unless strict wrapper support is added")
        sys.exit(1)

    print("PASS: test_gateway_builder_route_map")


if __name__ == "__main__":
    main()
