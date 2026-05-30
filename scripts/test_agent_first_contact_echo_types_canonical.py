#!/usr/bin/env python3
"""agent-first-contact pure Echo route: echo types have been removed.

Verify that agent-first-contact.json no longer contains echo_types arrays,
and the pure_echo_path is still correctly configured.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

data = json.loads((ROOT / "api" / "agent-first-contact.json").read_text(encoding="utf-8"))

pure = data.get("pure_echo_path")
if not isinstance(pure, dict):
    print("FAIL: agent-first-contact missing pure_echo_path object")
    sys.exit(1)

# Echo types should no longer be present
if "echo_types" in pure:
    print(f"FAIL: agent-first-contact pure_echo_path still has echo_types (deprecated): {pure['echo_types']}")
    sys.exit(1)

# Core fields should still be present
if pure.get("requested_archive_kind") != "agent_declared_echo_archive":
    print(f"FAIL: pure_echo_path.requested_archive_kind should be agent_declared_echo_archive")
    sys.exit(1)

if pure.get("submission_type") != "echo_candidate":
    print(f"FAIL: pure_echo_path.submission_type should be echo_candidate")
    sys.exit(1)

if not pure.get("preferred_builder"):
    print("FAIL: pure_echo_path.preferred_builder is missing")
    sys.exit(1)

print("PASS: agent-first-contact pure_echo_path correctly has no echo_types")
