#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    agent_start = json.loads((ROOT / "api" / "agent-start.v1.json").read_text(encoding="utf-8"))

    assert agent_start["schema"] == "trinityaccord.agent-start.v1"
    assert agent_start["canonical_human_url"] == "/agent-start/"
    assert agent_start["route_map_url"] == "/api/gateway-builder-route-map.v1.json"
    assert "do_not_patch_signed_payload_after_authorship_proof" in agent_start["never"]

    routes = agent_start["routes"]
    assert routes["pure_echo"]["builder"] == "scripts/build_agent_declared_echo_payload.py"
    assert routes["v0_v5_agent_declared_archive"]["builder"] == "scripts/build_agent_declared_archive_payload.py"
    assert routes["guardian_application_stage_1"]["builder"] == "scripts/create_guardian_application.mjs"
    assert routes["guardian_listing_stage_2"]["builder"] == "scripts/build_guardian_listing_request_payload.py"
    assert routes["guardian_signed_echo"]["builder"] == "scripts/build_guardian_echo_payload.py"

    gateway = json.loads((ROOT / "api" / "agent-submit-gateway.json").read_text(encoding="utf-8"))
    assert gateway["agent_start_url"] == "/agent-start/"
    assert gateway["agent_start_machine_url"] == "/api/agent-start.v1.json"
    assert gateway["builder_route_map_url"] == "/api/gateway-builder-route-map.v1.json"

    first_contact = json.loads((ROOT / "api" / "agent-first-contact.json").read_text(encoding="utf-8"))
    assert first_contact["gateway_submission_origin"]["human_url"] == "/agent-start/"

    print("PASS: test_agent_start_api")

if __name__ == "__main__":
    main()
