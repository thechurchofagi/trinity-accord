#!/usr/bin/env python3
"""Gateway workflow API input names must match declared builder CLI flags."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / "api" / "gateway-workflows.v1.json"

# Map workflow IDs to builder scripts for CLI contract checks.
CHECK_WORKFLOWS = {
    "pure_echo": "scripts/build_agent_declared_echo_payload.py",
    "guardian_signed_echo": "scripts/build_guardian_echo_payload.py",
    "v0_v5_agent_declared_archive": "scripts/build_agent_declared_archive_payload.py",
    "guardian_listing_stage_2": "scripts/build_guardian_listing_request_payload.py",
}

# Some workflow API names are transport/config concepts, not builder flags.
NON_CLI_INPUTS = {
    "--payload-json",
    "--preflight-url",
    "--submit-url",
}

def builder_help(script: str) -> str:
    result = subprocess.run(
        [sys.executable, script, "--help"],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"{script} --help failed:\n{result.stdout}\n{result.stderr}")
    return result.stdout + result.stderr

data = json.loads(WORKFLOWS.read_text(encoding="utf-8"))

errors = []

for workflow_id, builder in CHECK_WORKFLOWS.items():
    workflow = data["workflows"][workflow_id]
    help_text = builder_help(builder)

    for item in workflow.get("inputs", []):
        name = item.get("name")
        if not isinstance(name, str) or not name.startswith("--"):
            continue
        if name in NON_CLI_INPUTS:
            continue
        if name not in help_text:
            errors.append(f"{workflow_id}: {name} advertised but not accepted by {builder}")

if errors:
    print("FAIL: workflow API / builder CLI contract errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: workflow API input names match builder CLI help")
