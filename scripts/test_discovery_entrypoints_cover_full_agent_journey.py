#!/usr/bin/env python3
"""Public discovery surfaces should cover the full agent journey."""
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

required = {
    "/api/agent-minimal-context.v1.json",
    "/api/agent-first-contact.json",
    "/api/agent-required-reading.json",
    "/agent-start",
    "/api/agent-start.v1.json",
    "/api/agent-task-router.v1.json",
    "/api/agent-output-policy.v1.json",
    "/gateway-workflows/",
    "/gateway-workflows",
    "/api/gateway-workflows.v1.json",
    "/api/gateway-builder-route-map.v1.json",
    "/api/agent-submit-gateway.json",
    "/api/public-home-status.json",
}


def norm(path: str) -> str:
    if path != "/" and path.endswith("/"):
        return path[:-1]
    return path


all_discovered = set()
for group in [wk_api, wk_top, wk_entrypoints, links_machine, links_pages]:
    all_discovered.update(group)
    all_discovered.update(norm(p) for p in group)

missing = []
for path in required:
    if path not in all_discovered and norm(path) not in all_discovered:
        missing.append(path)

if missing:
    print(f"FAIL: discovery surfaces missing full agent journey paths: {sorted(missing)}")
    sys.exit(1)

print("PASS: discovery entrypoints cover full agent journey")
