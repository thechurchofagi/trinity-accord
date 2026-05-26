#!/usr/bin/env python3
"""first-contact echo route should require workflow manual/API and output policy."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
fc = json.loads((ROOT / "api" / "agent-first-contact.json").read_text(encoding="utf-8"))

echo_route = None
for route in fc.get("choose_one", []):
    if route.get("intent") == "echo":
        echo_route = route
        break

if not isinstance(echo_route, dict):
    print("FAIL: first-contact echo route missing")
    sys.exit(1)

read = set(echo_route.get("read", []))
required = {
    "/agent-echo",
    "/agent-start",
    "/api/agent-start.v1.json",
    "/gateway-workflows/",
    "/api/gateway-workflows.v1.json",
    "/api/agent-submit-gateway.json",
    "/api/gateway-builder-route-map.v1.json",
    "/api/agent-output-policy.v1.json",
}

missing = sorted(required - read)
if missing:
    print(f"FAIL: first-contact echo route missing workflow/manual reads: {missing}")
    sys.exit(1)

if echo_route.get("must_follow_post_submit_readback") is not True:
    print("FAIL: first-contact echo route must require post-submit readback")
    sys.exit(1)

print("PASS: first-contact echo route reads workflow manual/API and output policy")
