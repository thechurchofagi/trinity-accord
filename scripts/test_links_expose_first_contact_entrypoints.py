#!/usr/bin/env python3
"""api/links.json should expose canonical first-contact machine entrypoints.

Current paths must be in machine.
Legacy paths must be in legacy_machine (not in machine).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
links = json.loads((ROOT / "api" / "links.json").read_text(encoding="utf-8"))

machine = set(links.get("machine", []))
legacy_machine = set(links.get("legacy_machine", []))

# Current paths that MUST be in machine
required_current = {
    "/api/agent-minimal-context.v1.json",
    "/api/agent-first-contact.json",
    "/api/agent-required-reading.json",
    "/api/agent-start.v2.json",
    "/api/agent-output-policy.v1.json",
    "/api/agent-task-router.v1.json",
    "/api/context-load-map.json",
    "/downloads/record-chain-builder.mjs",
    "/api/record-chain-intake-gateway.v1.json",
}

# Legacy paths that must be in legacy_machine (NOT in machine)
legacy_paths = {
    "/api/gateway-workflows.v1.json",
    "/api/gateway-builder-route-map.v1.json",
    "/api/agent-submit-gateway.json",
}

errors = []

missing_current = sorted(required_current - machine)
if missing_current:
    errors.append(f"machine missing current paths: {missing_current}")

for lp in legacy_paths:
    if lp in machine and lp not in legacy_machine:
        errors.append(f"legacy path {lp} in machine but not in legacy_machine")

if errors:
    print("FAIL: api/links.json first-contact/workflow entrypoint errors:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print("PASS: api/links.json exposes canonical first-contact/workflow entrypoints (current active, legacy isolated)")
