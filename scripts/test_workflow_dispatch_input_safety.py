#!/usr/bin/env python3
"""Final red-team regression: workflow_dispatch inputs must be validated and passed safely.

Rules:
- No direct `${{ inputs.* }}` interpolation inside `run:` blocks.
- No string ARGS="..." command construction.
- No `node script $ARGS` / `python script $ARGS`.
- Any workflow using concurrency input must validate numeric range.
"""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"

errors = []

def extract_run_blocks(text: str):
    return re.findall(r"run:\s*\|\n((?:\s{10,}.+\n?)+)", text)

for path in sorted(WORKFLOWS.glob("*.yml")):
    text = path.read_text(encoding="utf-8")

    if "workflow_dispatch:" not in text:
        continue

    rel = path.relative_to(ROOT)
    run_blocks = extract_run_blocks(text)

    for block in run_blocks:
        if "${{ inputs." in block:
            errors.append(f"{rel}: workflow inputs must not be interpolated directly inside run block")

        if re.search(r'\bARGS="', block):
            errors.append(f"{rel}: use Bash array ARGS=(), not string ARGS=\"...\"")

        if re.search(r"\bnode\s+\S+\s+\$ARGS\b", block):
            errors.append(f'{rel}: node command must expand Bash array as "${{ARGS[@]}}"')

        if re.search(r"\bpython3?\s+\S+\s+\$ARGS\b", block):
            errors.append(f'{rel}: python command must expand Bash array as "${{ARGS[@]}}"')

    if "inputs.concurrency" in text:
        if "CONCURRENCY" not in text:
            errors.append(f"{rel}: inputs.concurrency should be assigned to an env var containing CONCURRENCY")
        if not re.search(r"\[\[\s+\"\$[A-Z_]*CONCURRENCY\"\s+=~\s+\^\[0-9\]\+\$", text):
            errors.append(f"{rel}: concurrency input must be regex-validated")
        if "-le 25" not in text and "-le 50" not in text:
            errors.append(f"{rel}: concurrency input must have an upper bound")

if errors:
    print("WORKFLOW_INPUT_SAFETY_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("WORKFLOW_INPUT_SAFETY_OK")
