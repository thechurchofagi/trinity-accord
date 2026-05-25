#!/usr/bin/env python3
"""Semantic overrides must use canonical Echo types."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from protocol_echo_types import allowed_canonical_echo_types

data = json.loads((ROOT / "api/agent-declared-archive-overrides.json").read_text(encoding="utf-8"))
overrides = data.get("overrides", {})

allowed = allowed_canonical_echo_types()
ok = True

for issue_number, override in overrides.items():
    if override.get("semantic_archive_kind") == "agent_declared_echo_archive":
        echo_type = override.get("echo_type")
        if echo_type not in allowed:
            print(
                f"FAIL: override for issue #{issue_number} uses non-canonical echo_type={echo_type!r}"
            )
            ok = False

if not ok:
    sys.exit(1)

print("PASS: all agent-declared Echo archive overrides use canonical Echo types")
