#!/usr/bin/env python3
"""api/links.json must expose Gateway workflow/readback contract pages and machine API."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
links = json.loads((ROOT / "api" / "links.json").read_text(encoding="utf-8"))

key_pages = set(links.get("key_pages", []))
machine = set(links.get("machine", []))

required_key_pages = {
    "/agent-start",
    "/agent-echo",
    "/gateway-workflows",
    "/guardian-alliance",
    "/guardian-join",
    "/guardian-routes",
}

required_machine = {
    "/api/agent-first-contact.json",
    "/api/agent-required-reading.json",
    "/api/agent-output-policy.v1.json",
    "/api/agent-task-router.v1.json",
    "/api/gateway-workflows.v1.json",
    "/api/gateway-builder-route-map.v1.json",
    "/api/agent-submit-gateway.json",
    "/api/public-home-status.json",
    "/api/guardian-registry.json",
    "/api/echo-index.json",
    "/api/agent-declared-verification-index.json",
}

errors = []

missing_pages = sorted(required_key_pages - key_pages)
if missing_pages:
    errors.append(f"key_pages missing: {missing_pages}")

missing_machine = sorted(required_machine - machine)
if missing_machine:
    errors.append(f"machine missing: {missing_machine}")

if errors:
    print("FAIL: links.json Gateway workflow discovery errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: links.json exposes Gateway workflow/readback discovery contract")
