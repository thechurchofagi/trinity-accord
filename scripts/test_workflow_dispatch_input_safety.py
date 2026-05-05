#!/usr/bin/env python3
"""Test workflow dispatch input safety.

RF-004: Ensure contract inputs are not directly interpolated in run blocks.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

WORKFLOWS = [
    ".github/workflows/backup-nft-arweave-mirror.yml",
    ".github/workflows/backup-nft-individual-v2.yml",
]

errors = []

for rel in WORKFLOWS:
    path = ROOT / rel
    if not path.exists():
        errors.append(f"{rel}: file not found")
        continue

    text = path.read_text(encoding="utf-8")

    # Check that inputs.contract is passed via env, not directly in run block
    run_blocks = re.findall(r"run:\s*\|\n((?:\s{10,}.+\n?)+)", text)

    for block in run_blocks:
        if "${{ inputs.contract }}" in block:
            errors.append(f"{rel}: inputs.contract must not be interpolated directly inside run block")

    if "CONTRACT: ${{ inputs.contract }}" not in text:
        errors.append(f"{rel}: contract input should be passed via env CONTRACT")

    if "ARGS=()" not in text:
        errors.append(f"{rel}: must use Bash array ARGS=()")

    args_expansion = '"${ARGS[@]}"'
    if args_expansion not in text:
        errors.append(f"{rel}: must expand Bash array as {args_expansion}")

    if not re.search(r'\[\[\s+!\s+"\$CONTRACT"\s+=~\s+\^0x\[a-fA-F0-9\]\{40\}\$', text):
        errors.append(f"{rel}: contract must be regex-validated as EVM address")

if errors:
    print("WORKFLOW_INPUT_SAFETY_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("WORKFLOW_INPUT_SAFETY_OK")
