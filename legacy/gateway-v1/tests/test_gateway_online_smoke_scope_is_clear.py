#!/usr/bin/env python3
"""Gateway online smoke must clearly state its limited scope."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
script = ROOT / "scripts" / "smoke_gateway_online.sh"

text = script.read_text(encoding="utf-8")

required = [
    "checks Gateway reachability only",
    "does not validate live site discovery",
    "does not validate live site discovery, Gateway preflight semantics, issue creation, archive automation, or Pages deployment",
    "smoke_live_discovery_contract.py",
]

missing = [p for p in required if p not in text]
if missing:
    print("FAIL: Gateway online smoke scope note missing:")
    for p in missing:
        print("  -", p)
    sys.exit(1)

print("PASS: Gateway online smoke scope is clear")
