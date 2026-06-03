#!/usr/bin/env python3
"""Agent-start and agent-submit-gateway API contracts.

v1 files are retired pointers; v2 is the active agent-start.
This test validates:
- v1 retired pointers are correct
- v2 active agent-start has required structure
- gateway-builder-route-map has expected routes
- agent-first-contact references agent-start correctly
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RETIRED_SCHEMA = "trinityaccord.gateway-v1-retired-pointer.v1"


def main() -> int:
    errors: list[str] = []

    # --- agent-start.v1.json: must be retired ---
    v1_path = ROOT / "api" / "agent-start.v1.json"
    if not v1_path.exists():
        print("FAIL: api/agent-start.v1.json missing")
        return 1
    v1 = json.loads(v1_path.read_text(encoding="utf-8"))
    if not v1.get("schema", "").endswith(".retired"):
        errors.append(f"agent-start.v1.json schema must be retired, got {v1.get('schema')}")
    if v1.get("canonical_human_url") != "/agent-start/":
        errors.append("agent-start.v1.json: canonical_human_url must be /agent-start/")
    if v1.get("do_not_use_for_new_public_submissions") is not True:
        errors.append("agent-start.v1.json: do_not_use_for_new_public_submissions must be true")

    # --- agent-start.v2.json: must be active ---
    v2_path = ROOT / "api" / "agent-start.v2.json"
    if not v2_path.exists():
        print("FAIL: api/agent-start.v2.json missing")
        return 1
    v2 = json.loads(v2_path.read_text(encoding="utf-8"))
    if v2.get("schema") != "trinityaccord.agent-start.v2":
        errors.append(f"agent-start.v2.json schema must be trinityaccord.agent-start.v2, got {v2.get('schema')}")
    if v2.get("canonical_human_url") != "/agent-start/":
        errors.append("agent-start.v2.json: canonical_human_url must be /agent-start/")

    # v2 must reference the record-chain gateway
    csm = v2.get("current_public_submission_method", {})
    if "/record-chain/" not in csm.get("submit", ""):
        errors.append("agent-start.v2.json: current submission method must point to record-chain")
    if csm.get("render_is_only_public_submission_method") is not True:
        errors.append("agent-start.v2.json: render_is_only_public_submission_method must be true")

    # v2 must have external agent rules
    rules = v2.get("external_agent_rules", {})
    if rules.get("must_not_use_legacy_gateway_v1") is not True:
        errors.append("agent-start.v2.json: must_not_use_legacy_gateway_v1 must be true")

    # --- agent-submit-gateway.json: must be retired pointer ---
    submit_path = ROOT / "api" / "agent-submit-gateway.json"
    if not submit_path.exists():
        print("FAIL: api/agent-submit-gateway.json missing")
        return 1
    submit = json.loads(submit_path.read_text(encoding="utf-8"))
    if submit.get("schema") != RETIRED_SCHEMA:
        errors.append(f"agent-submit-gateway.json schema must be {RETIRED_SCHEMA}")
    if submit.get("status") != "historical_archive_only":
        errors.append("agent-submit-gateway.json: status must be historical_archive_only")

    # --- gateway-builder-route-map: must have expected routes ---
    route_map_path = ROOT / "api" / "gateway-builder-route-map.v1.json"
    if not route_map_path.exists():
        print("FAIL: api/gateway-builder-route-map.v1.json missing")
        return 1
    route_map = json.loads(route_map_path.read_text(encoding="utf-8"))
    expected_routes = {
        "pure_echo", "v0_v5_agent_declared_archive",
        "guardian_application_stage_1", "guardian_listing_stage_2",
        "guardian_signed_echo",
    }
    routes = set(route_map.get("routes", {}).keys())
    missing = expected_routes - routes
    if missing:
        errors.append(f"gateway-builder-route-map missing routes: {sorted(missing)}")

    # Core routes must have description
    for route_name in ["pure_echo", "v0_v5_agent_declared_archive", "guardian_application_stage_1"]:
        if route_name in route_map.get("routes", {}):
            if "description" not in route_map["routes"][route_name]:
                errors.append(f"route {route_name} missing description")

    # --- agent-first-contact.json: must reference record-chain gateway ---
    fc_path = ROOT / "api" / "agent-first-contact.json"
    if not fc_path.exists():
        print("FAIL: api/agent-first-contact.json missing")
        return 1
    fc = json.loads(fc_path.read_text(encoding="utf-8"))
    if fc.get("canonical_human_url") != "/agent-first-contact/":
        errors.append("agent-first-contact.json: canonical_human_url must be /agent-first-contact/")
    fc_csm = fc.get("current_public_submission_method", {})
    if "/record-chain/" not in fc_csm.get("submit", ""):
        errors.append("agent-first-contact.json: submit must point to record-chain gateway")

    if errors:
        print("FAIL: agent-start API contract errors:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("PASS: agent-start API contracts valid (v1 retired, v2 active, route map complete)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
