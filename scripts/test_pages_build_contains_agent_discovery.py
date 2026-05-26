#!/usr/bin/env python3
"""Pages source/build inputs must contain the full agent discovery contract."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

links_path = ROOT / "api" / "links.json"
well_known_path = ROOT / ".well-known" / "trinity-accord.json"

links = json.loads(links_path.read_text(encoding="utf-8"))
well_known = json.loads(well_known_path.read_text(encoding="utf-8"))

machine = set(links.get("machine", []))
key_pages = set(links.get("key_pages", []))

required_machine = {
    "/api/agent-first-contact.json",
    "/api/agent-required-reading.json",
    "/api/agent-output-policy.v1.json",
    "/api/agent-task-router.v1.json",
    "/api/gateway-workflows.v1.json",
    "/api/agent-submit-gateway.json",
    "/api/gateway-builder-route-map.v1.json",
    "/api/public-home-status.json",
}

required_pages = {
    "/agent-start",
    "/agent-echo",
    "/gateway-workflows",
    "/guardian-alliance",
    "/guardian-join",
    "/guardian-routes",
}

errors = []

missing_machine = sorted(required_machine - machine)
if missing_machine:
    errors.append(f"api/links.json machine missing: {missing_machine}")

missing_pages = sorted(required_pages - key_pages)
if missing_pages:
    errors.append(f"api/links.json key_pages missing: {missing_pages}")

wk_api = well_known.get("api", {})
required_wk_api = {
    "agent_first_contact": "/api/agent-first-contact.json",
    "agent_required_reading": "/api/agent-required-reading.json",
    "gateway_workflows": "/api/gateway-workflows.v1.json",
    "agent_submit_gateway": "/api/agent-submit-gateway.json",
    "gateway_builder_route_map": "/api/gateway-builder-route-map.v1.json",
}

for key, expected in required_wk_api.items():
    if wk_api.get(key) != expected:
        errors.append(f".well-known api.{key} expected {expected!r}, got {wk_api.get(key)!r}")

required_aliases = {
    "gateway_workflows": "/gateway-workflows/",
    "gateway_workflows_json": "/api/gateway-workflows.v1.json",
    "agent_first_contact": "/api/agent-first-contact.json",
    "agent_submit_gateway": "/api/agent-submit-gateway.json",
    "gateway_builder_route_map": "/api/gateway-builder-route-map.v1.json",
}

for key, expected in required_aliases.items():
    if well_known.get(key) != expected:
        errors.append(f".well-known top-level {key} expected {expected!r}, got {well_known.get(key)!r}")

required_files = [
    "api/links.json",
    ".well-known/trinity-accord.json",
    "api/agent-first-contact.json",
    "api/gateway-workflows.v1.json",
    "api/agent-submit-gateway.json",
    "api/gateway-builder-route-map.v1.json",
]

for rel in required_files:
    if not (ROOT / rel).exists():
        errors.append(f"required Pages artifact source missing: {rel}")

if errors:
    print("FAIL: Pages source discovery artifact errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: Pages source contains full agent discovery contract")
