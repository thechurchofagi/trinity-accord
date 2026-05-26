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
    "pure_echo": ("python", "scripts/build_agent_declared_echo_payload.py"),
    "guardian_signed_echo": ("python", "scripts/build_guardian_echo_payload.py"),
    "v0_v5_agent_declared_archive": ("python", "scripts/build_agent_declared_archive_payload.py"),
    "guardian_listing_stage_2": ("python", "scripts/build_guardian_listing_request_payload.py"),
    "guardian_application_stage_1": ("node", "scripts/create_guardian_application.mjs"),
}

# Some workflow API names are transport/config concepts, not builder flags.
NON_CLI_INPUTS = {
    "--payload-json",
    "--preflight-url",
    "--submit-url",
}


def is_cli_flag(name: object) -> bool:
    return isinstance(name, str) and name.startswith("--")


def builder_help(kind: str, script: str) -> str:
    if kind == "node":
        # Some node builders use --explain instead of --help.
        # Also extract flags from script source for completeness.
        text = ""
        for flag in ["--help", "--explain"]:
            cmd = ["node", script, flag]
            result = subprocess.run(
                cmd,
                cwd=str(ROOT),
                text=True,
                capture_output=True,
            )
            text += result.stdout + result.stderr
            if result.returncode == 0:
                break
        # Also extract --flag patterns from source
        import re
        source = (ROOT / script).read_text(encoding="utf-8")
        for m in re.finditer(r"--[a-z][a-z0-9-]*", source):
            if m.group() not in text:
                text += " " + m.group()
        return text
    else:
        cmd = [sys.executable, script, "--help"]
        result = subprocess.run(
            cmd,
            cwd=str(ROOT),
            text=True,
            capture_output=True,
        )
        if result.returncode != 0:
            raise AssertionError(f"{' '.join(cmd)} failed:\n{result.stdout}\n{result.stderr}")
        return result.stdout + result.stderr


data = json.loads(WORKFLOWS.read_text(encoding="utf-8"))

errors = []

for workflow_id, (kind, builder) in CHECK_WORKFLOWS.items():
    workflow = data["workflows"].get(workflow_id)
    if not isinstance(workflow, dict):
        errors.append(f"{workflow_id}: workflow missing from API")
        continue
    help_text = builder_help(kind, builder)

    for item in workflow.get("inputs", []):
        name = item.get("name")
        if not isinstance(name, str):
            errors.append(f"{workflow_id}: input missing string name: {item}")
            continue

        if name in NON_CLI_INPUTS:
            continue

        if not is_cli_flag(name):
            if item.get("kind") == "logical_field":
                continue
            errors.append(
                f"{workflow_id}: input {name!r} is not a CLI flag; "
                f"use real builder flag or mark kind=logical_field"
            )
            continue

        if name not in help_text:
            errors.append(f"{workflow_id}: {name} advertised but not accepted by {builder}")

        for alias in item.get("aliases", []):
            if not isinstance(alias, str) or not alias.startswith("--"):
                errors.append(f"{workflow_id}: alias {alias!r} for {name} is not a CLI flag")
                continue
            if alias not in help_text:
                errors.append(f"{workflow_id}: alias {alias} advertised but not accepted by {builder}")

if errors:
    print("FAIL: workflow API / builder CLI contract errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: workflow API input names match builder CLI help")
