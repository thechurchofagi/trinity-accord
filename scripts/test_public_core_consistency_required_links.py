#!/usr/bin/env python3
"""check_public_core_consistency.py must require all core machine links."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / "scripts" / "check_public_core_consistency.py").read_text(encoding="utf-8")

required = [
    "/api/agent-start.v1.json",
    "/api/agent-minimal-context.v1.json",
    "/api/agent-output-policy.v1.json",
    "/api/agent-task-router.v1.json",
    "/api/context-load-map.json",
    "/api/gateway-builder-route-map.v1.json",
    "/api/echo-types.json",
    "/api/agent-submit-gateway.json",
    "/api/public-home-status.json",
    "/api/guardian-registry.json",
]

missing = [r for r in required if r not in text]
if missing:
    print("FAIL: check_public_core_consistency.py missing required link checks:")
    for m in missing:
        print("  -", m)
    sys.exit(1)

print("PASS: public core consistency requires all core machine links")
