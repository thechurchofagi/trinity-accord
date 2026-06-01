#!/usr/bin/env python3
"""Guardian Stage 2 workflow docs/API must match listing builder CLI."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "api" / "gateway-workflows.v1.json"
DOC = ROOT / "gateway-workflows.md"
BUILDER = "scripts/build_guardian_listing_request_payload.py"

REQUIRED_FLAGS = {
    "--agent-name",
    "--provider",
    "--source-issue",
    "--guardian-id",
    "--public-key-sha256",
    "--label",
    "--guardian-type",
    "--application-mode",
    "--out",
}

OPTIONAL_FLAGS = {
    "--human-claimed-name",
    "--agent-claimed-id",
    "--agent-instance-id",
    "--agent-public-profile",
    "--idempotency-key",
}


def run_help() -> str:
    result = subprocess.run(
        [sys.executable, BUILDER, "--help"],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr)
        raise SystemExit("FAIL: Stage 2 builder --help failed")
    return result.stdout + result.stderr


help_text = run_help()
errors = []

for flag in REQUIRED_FLAGS | OPTIONAL_FLAGS:
    if flag not in help_text:
        errors.append(f"builder help missing expected flag {flag}")

api = json.loads(API.read_text(encoding="utf-8"))
workflow = api["workflows"].get("guardian_listing_stage_2")
if not isinstance(workflow, dict):
    errors.append("api missing guardian_listing_stage_2 workflow")
else:
    inputs = workflow.get("inputs", [])
    names = {item.get("name") for item in inputs if isinstance(item, dict)}

    missing = sorted(REQUIRED_FLAGS - names)
    if missing:
        errors.append(f"guardian_listing_stage_2 API missing required flags: {missing}")

    for name in names:
        if isinstance(name, str) and not name.startswith("--"):
            errors.append(f"guardian_listing_stage_2 API input is not CLI flag: {name}")

doc = DOC.read_text(encoding="utf-8")
stage2_match = re.search(
    r'<a id="workflow-guardian-stage-2-listing"></a>.*?(?=\n---\n\n<a id="workflow-guardian-signed-echo"></a>)',
    doc,
    flags=re.S,
)
stage2 = stage2_match.group(0) if stage2_match else doc

if "python3 scripts/build_guardian_listing_request_payload.py \\" not in stage2:
    errors.append("Stage 2 docs missing copyable multiline builder command")

for flag in REQUIRED_FLAGS:
    if flag not in stage2:
        errors.append(f"Stage 2 docs missing required flag {flag}")

if "guardian-stage-2-listing.payload.json" not in stage2:
    errors.append("Stage 2 docs missing concrete output payload filename")

if "guardian_registry_number" in stage2 and "Do not include or request `guardian_registry_number`" not in stage2:
    errors.append("Stage 2 docs mention guardian_registry_number without clear prohibition")

if errors:
    print("FAIL: Guardian Stage 2 workflow CLI contract errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: Guardian Stage 2 workflow docs/API match builder CLI")
