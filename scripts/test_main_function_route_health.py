#!/usr/bin/env python3
"""Main agent-facing route/context files must be internally consistent."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from protocol_echo_types import allowed_canonical_echo_types

allowed_echo_types = allowed_canonical_echo_types()

agent_start_v1 = json.loads((ROOT / "api" / "agent-start.v1.json").read_text(encoding="utf-8"))
agent_start_v2 = json.loads((ROOT / "api" / "agent-start.v2.json").read_text(encoding="utf-8"))
route_map = json.loads((ROOT / "api" / "gateway-builder-route-map.v1.json").read_text(encoding="utf-8"))
context_map = json.loads((ROOT / "api" / "context-load-map.json").read_text(encoding="utf-8"))

# v1 must be retired; v2 must be active
if not agent_start_v1.get("schema", "").endswith(".retired"):
    print("FAIL: agent-start.v1.json must be retired")
    sys.exit(1)
if agent_start_v2.get("schema") != "trinityaccord.agent-start.v2":
    print("FAIL: agent-start.v2.json schema must be trinityaccord.agent-start.v2")
    sys.exit(1)

# v2 must reference record-chain gateway
csm = agent_start_v2.get("current_public_submission_method", {})
if "/record-chain/" not in csm.get("submit", ""):
    print("FAIL: agent-start.v2.json must reference record-chain gateway")
    sys.exit(1)

required_route_map_routes = {
    "pure_echo",
    "v0_v5_agent_declared_archive",
    "guardian_application_stage_1",
    "guardian_listing_stage_2",
    "guardian_signed_echo",
}
missing_route_map_routes = required_route_map_routes - set(route_map.get("routes", {}))
if missing_route_map_routes:
    print(f"FAIL: route-map missing routes: {sorted(missing_route_map_routes)}")
    sys.exit(1)

for route_id, route in route_map.get("routes", {}).items():
    for echo_type in route.get("echo_types", []):
        if echo_type not in allowed_echo_types:
            print(f"FAIL: route-map route {route_id} has non-canonical echo_type={echo_type!r}")
            sys.exit(1)

for route_id in required_route_map_routes:
    builder = route_map["routes"][route_id].get("builder")
    if builder and not (ROOT / builder).exists():
        print(f"FAIL: route-map builder missing for {route_id}: {builder}")
        sys.exit(1)

cc_actions = context_map.get("cc_action_requirements", {})
for action in ["meaningful_echo", "qualified_assessment", "verification_claim", "chronicle_research"]:
    if action not in cc_actions:
        print(f"FAIL: context-load-map missing action requirement: {action}")
        sys.exit(1)

print("PASS: main agent route/context health")
