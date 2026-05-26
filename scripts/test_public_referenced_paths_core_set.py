#!/usr/bin/env python3
"""The public referenced-path test must cover all core machine entrypoints."""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "scripts" / "test_public_referenced_paths_exist.py"
tree = ast.parse(path.read_text(encoding="utf-8"))

core = None
for node in tree.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "CORE_JSON":
                core = ast.literal_eval(node.value)

if core is None:
    print("FAIL: CORE_JSON not found")
    sys.exit(1)

required = {
    "api/agent-minimal-context.v1.json",
    "api/agent-first-contact.json",
    "api/agent-output-policy.v1.json",
    "api/agent-task-router.v1.json",
    "api/agent-start.v1.json",
    "api/context-load-map.json",
    "api/gateway-builder-route-map.v1.json",
    "api/public-home-status.json",
    "api/agent-required-reading.json",
    "api/agent-entry-protocol.json",
    "api/agent-tasks.json",
    "api/links.json",
    "api/gateway-workflows.v1.json",
    "api/guardian-active-listing-policy.v1.json",
    "api/external-agent-quickstart.json",
    "api/agent-submit-gateway.json",
}

missing = sorted(required - set(core))
if missing:
    print(f"FAIL: test_public_referenced_paths_exist.py CORE_JSON missing: {missing}")
    sys.exit(1)

print("PASS: public referenced-path core set covers main machine entrypoints")
