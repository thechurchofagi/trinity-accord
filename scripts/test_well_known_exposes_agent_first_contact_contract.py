#!/usr/bin/env python3
"""Well-known discovery must expose current agent first-contact/workflow contracts.

Current Record-Chain paths must be present.
Legacy Gateway v1 paths must NOT be in active sections.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
well_known = json.loads((ROOT / ".well-known" / "trinity-accord.json").read_text(encoding="utf-8"))

api = well_known.get("api", {})
entrypoints = well_known.get("agent_entrypoints", {})

# Current paths that MUST be in api
required_api = {
    "agent_minimal_context": "/api/agent-minimal-context.v1.json",
    "agent_first_contact": "/api/agent-first-contact.json",
    "agent_required_reading": "/api/agent-required-reading.json",
    "agent_output_policy": "/api/agent-output-policy.v1.json",
    "agent_task_router": "/api/agent-task-router.v1.json",
}

# Legacy paths that must NOT be in active api
legacy_api_keys = {
    "gateway_workflows",
    "agent_submit_gateway",
    "gateway_builder_route_map",
    "formal_builder_bundles",
}

errors = []

for key, expected in required_api.items():
    if api.get(key) != expected:
        errors.append(f"api.{key} expected {expected!r}, got {api.get(key)!r}")

# Verify legacy keys are NOT in active api
for key in legacy_api_keys:
    if key in api:
        errors.append(f"legacy key api.{key} should not be in active api section")

# Current entrypoints that MUST exist
required_entrypoints = {
    "agent_minimal_context",
    "agent_first_contact",
    "agent_required_reading",
    "agent_start",
    "agent_output_policy",
    "agent_task_router",
}

missing = sorted(required_entrypoints - set(entrypoints))
if missing:
    errors.append(f"agent_entrypoints missing current entries: {missing}")

# Legacy entrypoints that must NOT be in agent_entrypoints
legacy_entrypoint_keys = {
    "gateway_workflows",
    "agent_submit_gateway",
    "gateway_builder_route_map",
}

for key in legacy_entrypoint_keys:
    if key in entrypoints:
        errors.append(f"legacy key agent_entrypoints.{key} should not be in active entrypoints")

# Validate current entrypoint paths.
expected_paths = {
    "agent_first_contact": "/api/agent-first-contact.json",
    "agent_required_reading": "/api/agent-required-reading.json",
}

for key, expected_path in expected_paths.items():
    value = entrypoints.get(key)
    if not isinstance(value, dict):
        errors.append(f"agent_entrypoints.{key} must be object")
        continue
    if value.get("path") != expected_path:
        errors.append(f"agent_entrypoints.{key}.path expected {expected_path!r}, got {value.get('path')!r}")

# current_public_submission must exist and point to Record-Chain
cps = well_known.get("current_public_submission", {})
if cps.get("builder") != "/downloads/record-chain-builder.mjs":
    errors.append(f"current_public_submission.builder expected '/downloads/record-chain-builder.mjs', got {cps.get('builder')!r}")
if cps.get("gateway_contract") != "/api/record-chain-intake-gateway.v1.json":
    errors.append(f"current_public_submission.gateway_contract expected '/api/record-chain-intake-gateway.v1.json', got {cps.get('gateway_contract')!r}")

# Convenience aliases for current paths
required_aliases = {
    "agent_first_contact": "/api/agent-first-contact.json",
    "agent_required_reading": "/api/agent-required-reading.json",
}

for key, expected in required_aliases.items():
    if well_known.get(key) != expected:
        errors.append(f"top-level {key} expected {expected!r}, got {well_known.get(key)!r}")

if errors:
    print("FAIL: .well-known agent discovery contract errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: .well-known exposes current agent first-contact/workflow contracts (legacy isolated)")
