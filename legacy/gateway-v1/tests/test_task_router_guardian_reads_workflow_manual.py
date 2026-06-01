#!/usr/bin/env python3
"""Task-router Guardian route must read workflow manual/API and output policy."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
router = json.loads((ROOT / "api" / "agent-task-router.v1.json").read_text(encoding="utf-8"))

route = router.get("routes", {}).get("guardian_alliance")
if not isinstance(route, dict):
    print("FAIL: routes.guardian_alliance missing")
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
    print(f"FAIL: guardian_alliance task-router route missing reads: {missing}")
    sys.exit(1)

if route.get("must_follow_post_submit_readback") is not True:
    print("FAIL: guardian_alliance task-router route must require post-submit readback")
    sys.exit(1)

print("PASS: task-router Guardian route reads workflow/readback policy")
