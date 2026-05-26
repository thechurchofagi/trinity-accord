#!/usr/bin/env python3
"""Guardian Stage 1 workflow docs/API must match create_guardian_application.mjs CLI."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "api" / "gateway-workflows.v1.json"
DOC = ROOT / "gateway-workflows.md"
BUILDER = "scripts/create_guardian_application.mjs"

REQUIRED_FLAGS = {
    "--human-label",
    "--agent-label",
    "--challenge",
    "--readback",
    "--out",
}

EXPECTED_FLAGS = {
    "--mode",
    "--signing-key-holder",
    "--human-label",
    "--agent-label",
    "--agent-provider",
    "--title",
    "--challenge",
    "--key-dir",
    "--readback",
    "--out",
    "--reception-initiation-class",
    "--reception-initiation-basis",
    "--human-claimed-name",
    "--agent-claimed-id",
    "--agent-instance-id",
    "--agent-public-profile",
    "--guardian-key-prefix",
    "--authorship-key-prefix",
    "--force-overwrite-output",
}


def run_help() -> str:
    text = ""
    for flag in ["--help", "--explain"]:
        result = subprocess.run(
            ["node", BUILDER, flag],
            cwd=str(ROOT),
            text=True,
            capture_output=True,
        )
        text += result.stdout + result.stderr
        if result.returncode == 0:
            break
    # Also extract --flag patterns from source for completeness
    source = (ROOT / BUILDER).read_text(encoding="utf-8")
    for m in re.finditer(r"--[a-z][a-z0-9-]*", source):
        if m.group() not in text:
            text += " " + m.group()
    return text


help_text = run_help()
errors = []

for flag in REQUIRED_FLAGS:
    if flag not in help_text:
        errors.append(f"Stage 1 builder help missing required flag {flag}")

api = json.loads(API.read_text(encoding="utf-8"))
workflow = api["workflows"].get("guardian_application_stage_1")
if not isinstance(workflow, dict):
    errors.append("api missing guardian_application_stage_1 workflow")
else:
    inputs = workflow.get("inputs")
    if not isinstance(inputs, list) or not inputs:
        errors.append("guardian_application_stage_1 API missing non-empty inputs")
    else:
        names = {item.get("name") for item in inputs if isinstance(item, dict)}
        missing = sorted(REQUIRED_FLAGS - names)
        if missing:
            errors.append(f"guardian_application_stage_1 API missing required flags: {missing}")

        for name in names:
            if isinstance(name, str) and not name.startswith("--"):
                errors.append(f"guardian_application_stage_1 API input is not CLI flag: {name}")

        for flag in names:
            if isinstance(flag, str) and flag.startswith("--") and flag not in help_text:
                errors.append(f"guardian_application_stage_1 API advertises unsupported flag: {flag}")

doc = DOC.read_text(encoding="utf-8")
stage1_match = re.search(
    r'<a id="workflow-guardian-stage-1-application"></a>.*?(?=\n---\n\n<a id="workflow-guardian-stage-2-listing"></a>)',
    doc,
    flags=re.S,
)
stage1 = stage1_match.group(0) if stage1_match else ""

if not stage1:
    errors.append("Stage 1 docs section not found")
else:
    if "node scripts/create_guardian_application.mjs \\" not in stage1:
        errors.append("Stage 1 docs missing copyable multiline builder command")

    for flag in REQUIRED_FLAGS:
        if flag not in stage1:
            errors.append(f"Stage 1 docs missing required flag {flag}")

    for stale in [
        "Guardian type / mode",
        "Human/AI labels",
        "Keypair | yes",
        "Body/application text",
        "`--out` or generated payload path",
    ]:
        if stale in stage1:
            errors.append(f"Stage 1 docs still contain logical/stale input wording: {stale}")

    if "exact oath body" not in stage1.lower() and "exact guardian application oath body" not in stage1.lower():
        errors.append("Stage 1 docs must require exact oath body")

if errors:
    print("FAIL: Guardian Stage 1 workflow CLI contract errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: Guardian Stage 1 workflow docs/API match builder CLI")
