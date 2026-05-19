#!/usr/bin/env python3
"""Test that V0-V5 per-level Gateway examples exist and are consistent."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []

LEVELS = ["v0", "v1", "v2", "v3", "v4", "v4plus", "v5"]
LEVEL_LABELS = {"v0": "V0", "v1": "V1", "v2": "V2", "v3": "V3", "v4": "V4", "v4plus": "V4+", "v5": "V5"}


def check(condition, msg):
    if not condition:
        errors.append(msg)
        print(f"  FAIL: {msg}")
    else:
        print(f"  PASS: {msg}")


# 1. Fixture files exist
print("--- Fixture files ---")
for level in LEVELS:
    fixture = ROOT / "tests" / "fixtures" / "gateway" / f"valid_agent_declared_{level}.json"
    check(fixture.exists(), f"valid_agent_declared_{level}.json exists")
    if fixture.exists():
        d = json.loads(fixture.read_text())
        label = LEVEL_LABELS[level]
        check(d.get("agent_declared_protocol_level") == label,
              f"{level} fixture has agent_declared_protocol_level={label}")
        check(d.get("claim_gate", {}).get("allowed_protocol_level") == label,
              f"{level} fixture has claim_gate.allowed_protocol_level={label}")
        check(d.get("evidence_requirement_mode") == "waived_for_v0_v5",
              f"{level} fixture uses waived_for_v0_v5")
        check(d.get("claim_gate", {}).get("mode") == "template_for_v0_v5",
              f"{level} fixture uses template_for_v0_v5")

# 2. Server.js has endpoints
print("\n--- Server.js endpoints ---")
server = (ROOT / "examples" / "github-app-backend" / "server.js").read_text()
for level in LEVELS:
    check(f"/gateway/examples/agent-declared-{level}/raw" in server,
          f"server has /gateway/examples/agent-declared-{level}/raw")
    check(f"/gateway/examples/agent-declared-{level}" in server,
          f"server has /gateway/examples/agent-declared-{level}")

# 3. Capabilities JSON has per-level endpoints
print("\n--- Capabilities ---")
check("agent_declared_v0_raw" in server, "capabilities has agent_declared_v0_raw")
check("agent_declared_v5_raw" in server, "capabilities has agent_declared_v5_raw")
check("agent_declared_v4plus_raw" in server, "capabilities has agent_declared_v4plus_raw")

print(f"\n--- Results: {len(errors)} errors ---")
if errors:
    for e in errors:
        print(f"  ERROR: {e}")
    sys.exit(1)
print("V0_V5_PER_LEVEL_GATEWAY_EXAMPLES_OK")
