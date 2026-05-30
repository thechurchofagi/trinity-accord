#!/usr/bin/env python3
"""agent-facing pure Echo routes: echo types have been removed.

Verify that agent-facing APIs no longer contain echo_types arrays.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

errors = []

for api_file in ["api/agent-first-contact.json", "api/agent-submit-gateway.json"]:
    data = json.loads((ROOT / api_file).read_text(encoding="utf-8"))
    pure = data.get("pure_echo_path")
    if not isinstance(pure, dict):
        errors.append(f"{api_file}: missing pure_echo_path object")
        continue
    if "echo_types" in pure:
        errors.append(f"{api_file}: still has echo_types (should be removed)")
    if pure.get("requested_archive_kind") != "agent_declared_echo_archive":
        errors.append(f"{api_file}: requested_archive_kind should be agent_declared_echo_archive")

if errors:
    print("FAIL: agent-facing pure Echo route errors:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print("PASS: agent-facing pure Echo routes correctly have no echo_types")
