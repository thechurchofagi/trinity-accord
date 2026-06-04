#!/usr/bin/env python3
"""Pages source/build inputs must contain the current agent discovery contract.

Current Record-Chain paths must be in active discovery.
Legacy Gateway v1 paths must be in legacy sections only.
"""
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
legacy_machine = set(links.get("legacy_machine", []))

# Current paths that MUST be in active machine
required_machine = {
    "/api/agent-first-contact.json",
    "/api/agent-required-reading.json",
    "/api/agent-output-policy.v1.json",
    "/api/agent-task-router.v1.json",
    "/api/record-chain-intake-gateway.v1.json",
    "/api/record-chain-builder-bundles.v1.json",
    "/api/public-home-status.json",
}

# Current pages that MUST be in key_pages
required_pages = {
    "/agent-start",
    "/agent-echo",
    "/guardian-alliance",
}

# Legacy paths that must NOT be in active machine
legacy_paths_in_machine = {
    "/api/agent-submit-gateway.json",
    "/api/gateway-builder-route-map.v1.json",
    "/api/gateway-workflows.v1.json",
    "/api/formal-builder-bundles.v1.json",
}

errors = []

missing_machine = sorted(required_machine - machine)
if missing_machine:
    errors.append(f"api/links.json machine missing current paths: {missing_machine}")

missing_pages = sorted(required_pages - key_pages)
if missing_pages:
    errors.append(f"api/links.json key_pages missing: {missing_pages}")

# Check legacy paths are NOT in active machine
for lp in legacy_paths_in_machine:
    if lp in machine:
        if lp not in legacy_machine:
            errors.append(f"legacy path {lp} in active machine but not in legacy_machine")

# .well-known: current API entries must exist
wk_api = well_known.get("api", {})
required_wk_api = {
    "agent_first_contact": "/api/agent-first-contact.json",
    "agent_required_reading": "/api/agent-required-reading.json",
}

for key, expected in required_wk_api.items():
    if wk_api.get(key) != expected:
        errors.append(f".well-known api.{key} expected {expected!r}, got {wk_api.get(key)!r}")

# .well-known: current_public_submission must exist and point to record-chain
cps = well_known.get("current_public_submission", {})
if cps.get("builder") != "/downloads/record-chain-builder.mjs":
    errors.append(f".well-known current_public_submission.builder expected '/downloads/record-chain-builder.mjs', got {cps.get('builder')!r}")
if cps.get("gateway_contract") != "/api/record-chain-intake-gateway.v1.json":
    errors.append(f".well-known current_public_submission.gateway_contract expected '/api/record-chain-intake-gateway.v1.json', got {cps.get('gateway_contract')!r}")

# .well-known: legacy entries must NOT be in active api
legacy_wk_keys = {"gateway_workflows", "agent_submit_gateway", "gateway_builder_route_map", "formal_builder_bundles"}
for key in legacy_wk_keys:
    if key in wk_api:
        errors.append(f".well-known api.{key} should not be in active api section")

required_files = [
    "api/links.json",
    ".well-known/trinity-accord.json",
    "api/agent-first-contact.json",
    "api/record-chain-intake-gateway.v1.json",
    "api/record-chain-builder-bundles.v1.json",
]

for rel in required_files:
    if not (ROOT / rel).exists():
        errors.append(f"required Pages artifact source missing: {rel}")

if errors:
    print("FAIL: Pages source discovery artifact errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: Pages source contains current agent discovery contract (legacy isolated)")
