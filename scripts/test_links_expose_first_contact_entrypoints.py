#!/usr/bin/env python3
"""api/links.json should expose canonical first-contact machine entrypoints."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
links = json.loads((ROOT / "api" / "links.json").read_text(encoding="utf-8"))

machine = set(links.get("machine", []))
required = {
    "/api/agent-minimal-context.v1.json",
    "/api/agent-first-contact.json",
    "/api/agent-required-reading.json",
    "/api/agent-start.v1.json",
    "/api/agent-output-policy.v1.json",
    "/api/agent-task-router.v1.json",
    "/api/context-load-map.json",
    "/api/gateway-workflows.v1.json",
    "/api/gateway-builder-route-map.v1.json",
    "/api/agent-submit-gateway.json",
}

missing = sorted(required - machine)
if missing:
    print(f"FAIL: api/links.json machine list missing first-contact/workflow entries: {missing}")
    sys.exit(1)

print("PASS: api/links.json exposes canonical first-contact/workflow entrypoints")
