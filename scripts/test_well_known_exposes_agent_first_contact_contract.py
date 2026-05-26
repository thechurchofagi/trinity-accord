#!/usr/bin/env python3
"""Well-known discovery must expose current agent first-contact/workflow contracts."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
well_known = json.loads((ROOT / ".well-known" / "trinity-accord.json").read_text(encoding="utf-8"))

api = well_known.get("api", {})
entrypoints = well_known.get("agent_entrypoints", {})

required_api = {
    "agent_minimal_context": "/api/agent-minimal-context.v1.json",
    "agent_first_contact": "/api/agent-first-contact.json",
    "agent_required_reading": "/api/agent-required-reading.json",
    "agent_output_policy": "/api/agent-output-policy.v1.json",
    "agent_task_router": "/api/agent-task-router.v1.json",
    "gateway_workflows": "/api/gateway-workflows.v1.json",
    "agent_submit_gateway": "/api/agent-submit-gateway.json",
    "gateway_builder_route_map": "/api/gateway-builder-route-map.v1.json",
}

errors = []

for key, expected in required_api.items():
    if api.get(key) != expected:
        errors.append(f"api.{key} expected {expected!r}, got {api.get(key)!r}")

required_entrypoints = {
    "agent_minimal_context",
    "agent_first_contact",
    "agent_required_reading",
    "agent_start",
    "agent_output_policy",
    "agent_task_router",
    "gateway_workflows",
    "agent_submit_gateway",
    "gateway_builder_route_map",
}

missing = sorted(required_entrypoints - set(entrypoints))
if missing:
    errors.append(f"agent_entrypoints missing: {missing}")

# Validate key entrypoint paths.
expected_paths = {
    "agent_first_contact": "/api/agent-first-contact.json",
    "agent_required_reading": "/api/agent-required-reading.json",
    "gateway_workflows": "/gateway-workflows/",
    "agent_submit_gateway": "/api/agent-submit-gateway.json",
    "gateway_builder_route_map": "/api/gateway-builder-route-map.v1.json",
}

for key, expected_path in expected_paths.items():
    value = entrypoints.get(key)
    if not isinstance(value, dict):
        errors.append(f"agent_entrypoints.{key} must be object")
        continue
    if value.get("path") != expected_path:
        errors.append(f"agent_entrypoints.{key}.path expected {expected_path!r}, got {value.get('path')!r}")

# Convenience aliases should also exist.
required_aliases = {
    "agent_first_contact": "/api/agent-first-contact.json",
    "agent_required_reading": "/api/agent-required-reading.json",
    "gateway_workflows": "/gateway-workflows/",
    "gateway_workflows_json": "/api/gateway-workflows.v1.json",
    "agent_submit_gateway": "/api/agent-submit-gateway.json",
    "gateway_builder_route_map": "/api/gateway-builder-route-map.v1.json",
}

for key, expected in required_aliases.items():
    if well_known.get(key) != expected:
        errors.append(f"top-level {key} expected {expected!r}, got {well_known.get(key)!r}")

if errors:
    print("FAIL: .well-known agent discovery contract errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: .well-known exposes current agent first-contact/workflow contracts")
