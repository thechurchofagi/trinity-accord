#!/usr/bin/env python3
"""live-site group must include live smoke commands."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN_CI = ROOT / "scripts" / "run_ci_group.py"

text = RUN_CI.read_text(encoding="utf-8")

required = [
    "scripts/smoke_live_zero_clone_builder_bundles.py",
    "scripts/smoke_external_agent_entrypoint_journeys.py",
]

missing = [item for item in required if item not in text]

if missing:
    print("FAIL: live-site required commands missing:")
    for item in missing:
        print("  -", item)
    sys.exit(1)

print("PASS: live-site required commands are present")
