#!/usr/bin/env python3
"""gateway-workflows API must include Stage 1 real CLI inputs."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
api = json.loads((ROOT / "api" / "gateway-workflows.v1.json").read_text(encoding="utf-8"))

workflow = api["workflows"].get("guardian_application_stage_1")
if not isinstance(workflow, dict):
    print("FAIL: guardian_application_stage_1 workflow missing")
    sys.exit(1)

inputs = workflow.get("inputs")
if not isinstance(inputs, list) or not inputs:
    print("FAIL: guardian_application_stage_1 inputs must be non-empty")
    sys.exit(1)

names = {item.get("name") for item in inputs if isinstance(item, dict)}

required = {
    "--human-label",
    "--agent-label",
    "--challenge",
    "--readback",
    "--out",
}

missing = sorted(required - names)
if missing:
    print(f"FAIL: guardian_application_stage_1 missing required CLI inputs: {missing}")
    sys.exit(1)

for name in names:
    if isinstance(name, str) and not name.startswith("--"):
        print(f"FAIL: Stage 1 input is not a CLI flag: {name}")
        sys.exit(1)

print("PASS: Stage 1 workflow API has real CLI inputs")
