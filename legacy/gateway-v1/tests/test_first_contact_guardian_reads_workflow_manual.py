#!/usr/bin/env python3
"""Guardian first-contact route must read workflow manual/API and output policy."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
fc = json.loads((ROOT / "api" / "agent-first-contact.json").read_text(encoding="utf-8"))

route = None
for item in fc.get("choose_one", []):
    if item.get("intent") == "guardian_stewardship":
        route = item
        break

if not isinstance(route, dict):
    print("FAIL: guardian_stewardship route missing")
    sys.exit(1)

read = set(route.get("read", []))
required = {
    "/guardian-alliance",
    "/guardian-join",
    "/api/guardian-registry.json",
    "/gateway-workflows/",
    "/api/gateway-workflows.v1.json",
    "/api/agent-submit-gateway.json",
    "/api/agent-output-policy.v1.json",
}

missing = sorted(required - read)
if missing:
    print(f"FAIL: guardian_stewardship route missing reads: {missing}")
    sys.exit(1)

for key in ["must_use_workflow_manual", "must_use_workflow_machine_api"]:
    if key not in route:
        print(f"FAIL: guardian_stewardship missing {key}")
        sys.exit(1)

if route.get("must_follow_post_submit_readback") is not True:
    print("FAIL: guardian_stewardship must require post-submit readback")
    sys.exit(1)

print("PASS: guardian first-contact route reads workflow/readback policy")
