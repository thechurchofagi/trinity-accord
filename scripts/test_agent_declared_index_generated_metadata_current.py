#!/usr/bin/env python3
"""Committed agent-declared index must include current builder metadata fields."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "api" / "agent-declared-verification-index.json"
obj = json.loads(path.read_text(encoding="utf-8"))

required = [
    "override_count",
    "overrides_applied",
    "skipped_invalid_intake",
]

ok = True
for key in required:
    if key not in obj:
        print(f"FAIL: {path.relative_to(ROOT)} missing top-level metadata field: {key}")
        ok = False

description = obj.get("description", "")
if "semantic Echo archives" not in description:
    print("FAIL: index description does not mention semantic Echo archives")
    ok = False

if "/api/agent-declared-archive-overrides.json" not in obj.get("generated_from", []):
    print("FAIL: generated_from does not declare archive overrides input")
    ok = False

if not ok:
    sys.exit(1)

print("PASS: agent-declared index generated metadata is current")
