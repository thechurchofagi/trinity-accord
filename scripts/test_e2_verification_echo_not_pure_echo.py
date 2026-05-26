#!/usr/bin/env python3
"""E2 verification echo must remain separate from pure Echo routes."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

agent_start = json.loads((ROOT / "api" / "agent-start.v1.json").read_text(encoding="utf-8"))
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

e2_route = agent_start["routes"].get("e2_verification_echo")
if not e2_route or not e2_route.get("not_pure_echo"):
    print("FAIL: agent-start E2 route must be marked not_pure_echo")
    ok = False

if not ok:
    sys.exit(1)

print("PASS: E2 verification echo remains separate from pure Echo")
