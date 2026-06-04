#!/usr/bin/env python3
"""Public active discovery surfaces should cover the current Record-Chain agent journey."""
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

current_submission = well_known.get("current_public_submission") or {}
wk_current = {v for v in current_submission.values() if isinstance(v, str) and v.startswith("/")}
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
    "/downloads/record-chain-builder.mjs",
    "/api/record-chain-intake-gateway.v1.json",
    "/api/record-chain-submission-schema.v1.json",
    "/api/record-chain-field-helper.v1.json",
    "/api/record-chain-oath-policy.v1.json",
    "/api/public-home-status.json",
}

legacy_active_forbidden = {
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


all_discovered = set()
for group in [wk_api, wk_top, wk_entrypoints, wk_current, links_machine, links_pages]:
    all_discovered.update(group)
    all_discovered.update(norm(p) for p in group)

missing = [path for path in required if path not in all_discovered and norm(path) not in all_discovered]
active_groups = wk_api | wk_entrypoints | links_machine | links_pages
legacy_active = sorted(path for path in legacy_active_forbidden if path in active_groups or norm(path) in {norm(p) for p in active_groups})

if missing or legacy_active:
    if missing:
        print(f"FAIL: active discovery surfaces missing current agent journey paths: {sorted(missing)}")
    if legacy_active:
        print(f"FAIL: active discovery surfaces still expose legacy submission paths: {legacy_active}")
    sys.exit(1)

print("PASS: active discovery entrypoints cover the current Record-Chain agent journey")
