#!/usr/bin/env python3
"""All Gateway-submitting verification first-contact routes must read workflow/readback policy."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
fc = json.loads((ROOT / "api" / "agent-first-contact.json").read_text(encoding="utf-8"))

ROUTES = [
    "verify_v0_v5_agent_declared",
    "verification_echo_e2",
    "verify_v6_plus_strict_evidence",
]

required_common = {
    "/gateway-workflows/",
    "/api/gateway-workflows.v1.json",
    "/api/agent-output-policy.v1.json",
}

errors = []

by_intent = {item.get("intent"): item for item in fc.get("choose_one", []) if isinstance(item, dict)}

for intent in ROUTES:
    route = by_intent.get(intent)
    if not isinstance(route, dict):
        errors.append(f"{intent}: route missing")
        continue

    read = set(route.get("read", []))
    missing = sorted(required_common - read)
    if missing:
        errors.append(f"{intent}: missing reads {missing}")

    if route.get("must_use_workflow_manual") != "/gateway-workflows/":
        errors.append(f"{intent}: missing/incorrect must_use_workflow_manual")

    if route.get("must_use_workflow_machine_api") != "/api/gateway-workflows.v1.json":
        errors.append(f"{intent}: missing/incorrect must_use_workflow_machine_api")

    if route.get("must_follow_post_submit_readback") is not True:
        errors.append(f"{intent}: must_follow_post_submit_readback must be true")

if errors:
    print("FAIL: verification first-contact workflow route errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: verification first-contact routes read workflow/readback policy")
