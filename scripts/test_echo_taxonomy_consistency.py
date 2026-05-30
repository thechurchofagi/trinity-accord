#!/usr/bin/env python3
"""FUNC-TAXONOMY-001: Echo taxonomy consistency guard.

Echo types have been deprecated. This test verifies the deprecation is consistent:
- api/echo-types.json has status=DEPRECATED
- types array is empty
- No new code enforces echo_type validation
"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]

echo_types = json.loads((ROOT / "api/echo-types.json").read_text(encoding="utf-8"))

# Verify deprecation
if echo_types.get("status") != "DEPRECATED":
    print(f"FAIL: api/echo-types.json status should be DEPRECATED, got: {echo_types.get('status')}")
    sys.exit(1)

if echo_types.get("types") != []:
    print(f"FAIL: api/echo-types.json types should be empty, got: {echo_types.get('types')}")
    sys.exit(1)

# Verify gateway payload schema doesn't enforce echo_type enum
schema = (ROOT / "api/agent-issue-gateway-payload-schema.v1.json").read_text(encoding="utf-8")
if '"E1_recognition_echo"' in schema:
    print("FAIL: gateway payload schema still contains E1_recognition_echo enum value")
    sys.exit(1)

# Verify gateway builder route map doesn't have echo_types arrays
route_map = json.loads((ROOT / "api/gateway-builder-route-map.v1.json").read_text(encoding="utf-8"))
for route_name, route in route_map.get("routes", {}).items():
    if "echo_types" in route:
        print(f"FAIL: route '{route_name}' still has echo_types array")
        sys.exit(1)

print("PASS: Echo taxonomy deprecation consistency guard passed")
