#!/usr/bin/env python3
"""Gateway workflow docs/API: echo types have been removed.

Verify that --echo-type is no longer present in gateway workflows.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

API = ROOT / "api" / "gateway-workflows.v1.json"

workflow = json.loads(API.read_text(encoding="utf-8"))
errors = []

for workflow_id, wf in workflow.get("workflows", {}).items():
    for inp in wf.get("inputs", []):
        if inp.get("name") == "--echo-type":
            errors.append(f"{workflow_id}: --echo-type should be removed (deprecated)")

if errors:
    print("FAIL: Gateway workflow Echo type errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: Gateway workflows correctly have no --echo-type")
