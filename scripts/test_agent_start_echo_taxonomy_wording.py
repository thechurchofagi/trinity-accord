#!/usr/bin/env python3
"""Current public API files must not use stale Echo taxonomy language.

Checks active API files for deprecated echo type names.
Gateway v1 retired pointers are exempt (they contain no active content).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STALE_TERMS = [
    "E1_read_oriented_echo",
    "E4_refusal_echo",
    "E5_correction_echo",
    "E6_preservation_echo",
    "E7_propagation_echo",
]

# Files to check for stale terminology
ACTIVE_FILES = [
    "api/agent-first-contact.json",
    "api/agent-start.v2.json",
    "api/gateway-builder-route-map.v1.json",
    "api/gateway-workflows.v1.json",
    "api/record-chain-submission-schema.v1.json",
    "api/record-chain-intake-gateway.v1.json",
]

RETIRED_SCHEMA = "trinityaccord.gateway-v1-retired-pointer.v1"


def main() -> int:
    ok = True
    for rel in ACTIVE_FILES:
        path = ROOT / rel
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        # Skip retired pointers
        if data.get("schema") == RETIRED_SCHEMA or data.get("schema", "").endswith(".retired"):
            continue
        text = json.dumps(data, ensure_ascii=False)
        for term in STALE_TERMS:
            if term in text:
                print(f"FAIL: stale Echo taxonomy term '{term}' found in {rel}")
                ok = False

    if not ok:
        sys.exit(1)

    print("PASS: no stale Echo taxonomy wording in active API files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
