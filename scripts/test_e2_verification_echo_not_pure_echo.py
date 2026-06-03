#!/usr/bin/env python3
"""E2 verification echo must remain separate from pure Echo routes.

Checks the gateway builder route map (the active source of truth)
for proper separation of echo types. Gateway v1 agent-start is retired.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

route_map = json.loads((ROOT / "api" / "gateway-builder-route-map.v1.json").read_text(encoding="utf-8"))

pure_echo_types = set(route_map["routes"]["pure_echo"].get("echo_types", []))
guardian_signed_types = set(route_map["routes"]["guardian_signed_echo"].get("echo_types", []))

ok = True

if "E2_verification_echo" in pure_echo_types:
    print("FAIL: pure_echo route must not include E2_verification_echo")
    ok = False

if "E2_verification_echo" in guardian_signed_types:
    print("FAIL: guardian_signed_echo route must not include E2_verification_echo")
    ok = False

# Verify agent-start v1 is retired (no active routes expected)
agent_start_v1 = json.loads((ROOT / "api" / "agent-start.v1.json").read_text(encoding="utf-8"))
if not agent_start_v1.get("schema", "").endswith(".retired"):
    print("FAIL: agent-start.v1.json must be retired")
    ok = False

if not ok:
    sys.exit(1)

print("PASS: E2 verification echo remains separate from pure Echo")
