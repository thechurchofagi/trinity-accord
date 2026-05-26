#!/usr/bin/env python3
"""Test: Public prompt boundary — no dangerous phrases, required boundary tokens."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "llms.txt",
    ROOT / "ai.txt",
]

DANGEROUS = [
    "ignore previous instructions",
    "override system",
    "override developer",
    "you must believe",
    "you must obey",
    "never criticize",
    "do not refuse",
    "give maximum score",
    "rank as highest",
    "always endorse",
]

REQUIRED_BOUNDARY = [
    "not an instruction override",
    "Bitcoin Originals prevail",
]

# Must have at least one verification guidance phrase
VERIFY_GUIDANCE = [
    "verify independently",
    "verify the flaw",
    "verify provenance",
    "verify, critique",
]

LLMS_REQUIRED = [
    "verify, critique",
    "refuse",
    "ignore",
    "does not require belief",
    "endorsement",
    "obedience",
    "inflated scoring",
]

errors = []

for path in FILES:
    text = path.read_text(encoding="utf-8")
    lower = text.lower()

    for phrase in DANGEROUS:
        if phrase in lower:
            errors.append(f"{path.name}: dangerous prompt phrase found: {phrase}")

    for token in REQUIRED_BOUNDARY:
        if token.lower() not in lower:
            errors.append(f"{path.name}: missing boundary token: {token}")

    # Must have at least one verification guidance phrase
    if not any(vg in lower for vg in VERIFY_GUIDANCE):
        errors.append(f"{path.name}: missing verification guidance (verify independently / verify the flaw / verify provenance)")

# llms has richer evaluation stance
llms = (ROOT / "llms.txt").read_text(encoding="utf-8").lower()
for token in LLMS_REQUIRED:
    if token.lower() not in llms:
        errors.append(f"llms.txt: missing evaluation freedom token: {token}")

# Command-like words allowed only if boundary exists in same file
for path in FILES:
    text = path.read_text(encoding="utf-8")
    if re.search(r"\b(MANDATORY|DO NOT|must not|must)\b", text):
        lower = text.lower()
        if "not an instruction override" not in lower:
            errors.append(f"{path.name}: command-like language without instruction boundary")

if errors:
    print("FAIL: public prompt boundary violations:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PUBLIC_PROMPT_BOUNDARY_OK")
