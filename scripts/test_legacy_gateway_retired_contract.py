#!/usr/bin/env python3
"""Verify legacy Gateway v1 surfaces are properly retired."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def require(cond: bool, msg: str) -> None:
    if not cond:
        errors.append(msg)


route_map = json.loads((ROOT / "api/gateway-builder-route-map.v1.json").read_text(encoding="utf-8"))

require(route_map.get("status") == "historical_archive_only", "route map must be historical_archive_only")
require(route_map.get("historical_archive_only") is True, "route map must set historical_archive_only true")
require(route_map.get("do_not_use_for_new_public_submissions") is True, "route map must forbid new public submissions")
require(route_map.get("all_routes_retired") is True, "route map must mark all routes retired")
require(route_map.get("replacement") == "/api/agent-first-contact.json", "route map replacement must be agent-first-contact")
require(
    route_map.get("current_public_submission_contract") == "/api/record-chain-intake-gateway.v1.json",
    "route map must point to active record-chain contract",
)

routes = route_map.get("routes", {})
for name, route in routes.items():
    text = json.dumps(route, ensure_ascii=False)
    if "/gateway/preflight" in text or "/agent-submit" in text:
        require(
            route.get("retired") is True or route_map.get("all_routes_retired") is True,
            f"legacy route {name} must be retired",
        )
        require(
            "/record-chain/preflight" in text or "/record-chain/preflight" in json.dumps(route_map),
            f"legacy route {name} must mention current preflight replacement",
        )
        require(
            "/record-chain/submit" in text or "/record-chain/submit" in json.dumps(route_map),
            f"legacy route {name} must mention current submit replacement",
        )

server = (ROOT / "examples/github-app-backend/server.js").read_text(encoding="utf-8")
require("LEGACY_GATEWAY_RETIRED" in server, "server.js must define LEGACY_GATEWAY_RETIRED")
require("retiredGatewayV1Response" in server, "server.js must define retiredGatewayV1Response")
require(
    'app.all("/gateway/preflight"' in server or 'app.post("/gateway/preflight"' in server,
    "server.js must guard /gateway/preflight",
)
require(
    'app.all("/agent-submit"' in server or 'app.post("/agent-submit"' in server,
    "server.js must guard /agent-submit",
)
require("/record-chain/preflight" in server, "server.js retired response must mention current preflight")
require("/record-chain/submit" in server, "server.js retired response must mention current submit")

render = (ROOT / "render.yaml").read_text(encoding="utf-8")
require("TRINITY_LEGACY_ISSUE_GATEWAY_RETIRED" in render, "render.yaml must set TRINITY_LEGACY_ISSUE_GATEWAY_RETIRED")
require("autoDeploy: false" in render, "legacy gateway must not auto-deploy")

# Active public files must not reference retired endpoints
for rel in [
    "agent-start.md",
    "agent-first-contact.md",
    "api/agent-start.v2.json",
    "api/agent-first-contact.json",
    "api/record-chain-intake-gateway.v1.json",
]:
    path = ROOT / rel
    if not path.exists():
        continue
    text = path.read_text(encoding="utf-8")
    if "/gateway/preflight" in text or "/agent-submit" in text:
        errors.append(f"active public file references retired Gateway v1 endpoint: {rel}")

if errors:
    raise SystemExit("\n".join(f"ERROR: {e}" for e in errors))

print("legacy gateway retired contract OK")
