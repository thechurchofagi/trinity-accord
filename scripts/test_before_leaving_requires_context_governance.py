#!/usr/bin/env python3
"""Test: before_leaving schema requires context governance fields."""
import json, sys
from pathlib import Path
p = Path("api/agent-before-leaving-report-schema.v1.json")
if not p.exists(): print("FAIL: schema file missing"); sys.exit(1)
data = json.loads(p.read_text())
errors = []
for field in ["context_depth_achieved","context_readiness_level","context_limitations","action_family"]:
    if field not in data.get("required",[]): errors.append(f"missing required: {field}")
    if field not in data.get("properties",{}): errors.append(f"missing property: {field}")
if errors:
    for e in errors: print(f"FAIL: {e}")
    sys.exit(1)
print("PASS: before_leaving context governance")
