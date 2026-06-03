#!/usr/bin/env python3
"""agent-first-contact must not contain stale echo_types arrays.

Verify that agent-first-contact.json (v2) does not contain deprecated
echo_types arrays. The v2 structure uses choose_one actions and
current_public_submission_method instead of pure_echo_path.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

data = json.loads((ROOT / "api" / "agent-first-contact.json").read_text(encoding="utf-8"))

# Must be v2 active
if data.get("schema") != "trinityaccord.agent-first-contact.v2":
    print(f"FAIL: expected schema trinityaccord.agent-first-contact.v2, got {data.get('schema')}")
    sys.exit(1)

# Must reference record-chain gateway
csm = data.get("current_public_submission_method", {})
if "/record-chain/" not in csm.get("submit", ""):
    print("FAIL: agent-first-contact must reference record-chain gateway")
    sys.exit(1)

# Must have choose_one actions
actions = data.get("choose_one", [])
if not actions:
    print("FAIL: agent-first-contact missing choose_one actions")
    sys.exit(1)

# Echo types should not appear anywhere in the file
text = json.dumps(data, ensure_ascii=False)
if "echo_types" in text:
    print("FAIL: agent-first-contact still contains echo_types (deprecated)")
    sys.exit(1)

print("PASS: agent-first-contact v2 structure valid, no stale echo_types")
