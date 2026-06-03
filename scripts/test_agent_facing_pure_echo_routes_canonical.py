#!/usr/bin/env python3
"""Agent-facing APIs must not contain stale echo_types arrays.

agent-first-contact.json is v2 active (no pure_echo_path, uses choose_one).
agent-submit-gateway.json is a retired pointer.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RETIRED_SCHEMA = "trinityaccord.gateway-v1-retired-pointer.v1"

errors = []

# agent-first-contact.json: v2 active, no echo_types
fc_path = ROOT / "api" / "agent-first-contact.json"
fc = json.loads(fc_path.read_text(encoding="utf-8"))
if fc.get("schema") != "trinityaccord.agent-first-contact.v2":
    errors.append(f"agent-first-contact.json: expected v2 schema, got {fc.get('schema')}")
fc_text = json.dumps(fc, ensure_ascii=False)
if "echo_types" in fc_text:
    errors.append("agent-first-contact.json: still contains echo_types (deprecated)")

# agent-submit-gateway.json: must be retired pointer
submit_path = ROOT / "api" / "agent-submit-gateway.json"
submit = json.loads(submit_path.read_text(encoding="utf-8"))
if submit.get("schema") != RETIRED_SCHEMA:
    errors.append(f"agent-submit-gateway.json: expected retired pointer, got {submit.get('schema')}")

if errors:
    print("FAIL: agent-facing pure Echo route errors:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print("PASS: agent-facing APIs correctly have no echo_types")
