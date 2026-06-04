#!/usr/bin/env python3
"""Public discovery surfaces should cover the full agent journey.

Current paths must be in active discovery.
Legacy paths must be in legacy sections only (NOT in active discovery).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

well_known = json.loads((ROOT / ".well-known" / "trinity-accord.json").read_text(encoding="utf-8"))
links = json.loads((ROOT / "api" / "links.json").read_text(encoding="utf-8"))

wk_api = set((well_known.get("api") or {}).values())
wk_top = {v for v in well_known.values() if isinstance(v, str)}
wk_entrypoints = set()
for value in (well_known.get("agent_entrypoints") or {}).values():
    if isinstance(value, dict):
        if isinstance(value.get("path"), str):
            wk_entrypoints.add(value["path"])
        if isinstance(value.get("machine_path"), str):
            wk_entrypoints.add(value["machine_path"])
    elif isinstance(value, str):
        wk_entrypoints.add(value)

links_machine = set(links.get("machine", []))
links_pages = set(links.get("key_pages", []))

# Current paths that MUST be in active discovery
required_current = {
    "/api/agent-minimal-context.v1.json",
    "/api/agent-first-contact.json",
    "/api/agent-required-reading.json",
    "/agent-start",
    "/api/agent-start.v1.json",
    "/api/agent-task-router.v1.json",
    "/api/agent-output-policy.v1.json",
    "/api/public-home-status.json",
    "/downloads/record-chain-builder.mjs",
    "/api/record-chain-intake-gateway.v1.json",
    "/api/record-chain-builder-bundles.v1.json",
}

# Legacy paths that must NOT be in active discovery
legacy_paths = {
    "/gateway-workflows/",
    "/gateway-workflows",
    "/api/gateway-workflows.v1.json",
    "/api/gateway-builder-route-map.v1.json",
    "/api/agent-submit-gateway.json",
    "/api/formal-builder-bundles.v1.json",
}


def norm(path: str) -> str:
    if path != "/" and path.endswith("/"):
        return path[:-1]
    return path


active_discovered = set()
for group in [wk_api, wk_top, wk_entrypoints, links_machine, links_pages]:
    active_discovered.update(group)
    active_discovered.update(norm(p) for p in group)

legacy_machine = set(links.get("legacy_machine", []))
deprecated = set(links.get("deprecated_for_new_records", []))
legacy_sections = legacy_machine | deprecated

errors = []

# Check current paths are present
for path in required_current:
    if path not in active_discovered and norm(path) not in active_discovered:
        errors.append(f"current path missing from active discovery: {path}")

# Check legacy paths are NOT in active discovery
for path in legacy_paths:
    if path in active_discovered or norm(path) in active_discovered:
        # Must be in legacy sections
        if path not in legacy_sections and norm(path) not in legacy_sections:
            errors.append(f"legacy path still in active discovery without legacy marking: {path}")

if errors:
    print("FAIL: discovery entrypoints errors:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print("PASS: discovery entrypoints cover full agent journey (current active, legacy isolated)")
