#!/usr/bin/env python3
"""agent-submit-gateway pure Echo path: echo types have been removed.

Verify that agent-submit-gateway.json no longer contains echo_types arrays.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

data = json.loads((ROOT / "api" / "agent-submit-gateway.json").read_text(encoding="utf-8"))

pure = data.get("pure_echo_path")
if not isinstance(pure, dict):
    print("FAIL: agent-submit-gateway missing pure_echo_path object")
    sys.exit(1)

# Echo types should no longer be present
if "echo_types" in pure:
    print(f"FAIL: agent-submit-gateway pure_echo_path still has echo_types (deprecated)")
    sys.exit(1)

# Core fields should still be present
if pure.get("requested_archive_kind") != "agent_declared_echo_archive":
    print(f"FAIL: pure_echo_path.requested_archive_kind should be agent_declared_echo_archive")
    sys.exit(1)

if pure.get("submission_type") != "echo_candidate":
    print(f"FAIL: pure_echo_path.submission_type should be echo_candidate")
    sys.exit(1)

print("PASS: agent-submit-gateway pure_echo_path correctly has no echo_types")
