#!/usr/bin/env python3
"""submit_echo route should require workflow manual/API and output policy."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
router = json.loads((ROOT / "api" / "agent-task-router.v1.json").read_text(encoding="utf-8"))

route = router.get("routes", {}).get("submit_echo")
if not isinstance(route, dict):
    print("FAIL: routes.submit_echo missing")
    sys.exit(1)

read = set(route.get("read", []))
required = {
    "/api/agent-first-contact.json",
    "/api/agent-output-policy.v1.json",
    "/gateway-workflows/",
    "/api/gateway-workflows.v1.json",
    "/api/agent-submit-gateway.json",
    "/api/gateway-builder-route-map.v1.json",
    "/agent-echo",
}

missing = sorted(required - read)
if missing:
    print(f"FAIL: submit_echo route missing workflow/manual reads: {missing}")
    sys.exit(1)

if route.get("must_follow_post_submit_readback") is not True:
    print("FAIL: submit_echo route must require post-submit readback")
    sys.exit(1)

print("PASS: submit_echo route reads workflow manual/API and output policy")
