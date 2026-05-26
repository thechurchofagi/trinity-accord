#!/usr/bin/env python3
"""PUB-VER-001: Public status must not default to V4 without records."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
src = (ROOT / "scripts/generate_public_home_status.py").read_text(encoding="utf-8")

bad_patterns = [
    'if ad_verifiable else "V4"',
    'agent_declared_highest = "V4"',
]
for pattern in bad_patterns:
    if pattern in src:
        print(f"FAIL: public status still defaults missing records to V4: {pattern}")
        sys.exit(1)

required = ["no_current_agent_declared_records", "not_applicable"]
missing = [x for x in required if x not in src]
if missing:
    print(f"FAIL: missing truthful empty-state verifiability markers: {missing}")
    sys.exit(1)

print("PASS: public status does not default to V4 without records")
