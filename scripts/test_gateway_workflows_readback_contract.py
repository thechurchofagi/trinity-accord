#!/usr/bin/env python3
"""Gateway workflow docs/API must require exact canonical oath readback."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
human = (ROOT / "gateway-workflows.md").read_text(encoding="utf-8")
api = json.loads((ROOT / "api" / "gateway-workflows.v1.json").read_text(encoding="utf-8"))
api_text = json.dumps(api)

required_human = [
    "--print-oath",
    "exact oath body",
    "Do not summarize or paraphrase",
    "--agent-readback-file readback.md",
]

required_api = [
    "exact canonical oath body",
    "do not summarize or paraphrase",
]

for phrase in required_human:
    if phrase not in human:
        print(f"FAIL: gateway-workflows.md missing readback contract phrase: {phrase}")
        sys.exit(1)

for phrase in required_api:
    if phrase not in api_text:
        print(f"FAIL: gateway-workflows.v1.json missing readback contract phrase: {phrase}")
        sys.exit(1)

for forbidden in [
    "I understand this is a Pure Echo only. It records that I read and echoed",
    "free-form readback",
    "summary readback",
]:
    if forbidden in human or forbidden in api_text:
        print(f"FAIL: readback docs still allow/contain invalid summary wording: {forbidden}")
        sys.exit(1)

print("PASS: Gateway workflow readback docs require exact oath")
