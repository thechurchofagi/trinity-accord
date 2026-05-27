#!/usr/bin/env python3
"""External agent journey swarm smoke must cover full read-only agent journey."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
script = ROOT / "scripts" / "smoke_external_agent_journey_swarm.py"

if not script.exists():
    print("FAIL: smoke_external_agent_journey_swarm.py missing")
    sys.exit(1)

text = script.read_text(encoding="utf-8")

required = [
    "GET requests only",
    "CORE_DISCOVERY_PATHS",
    "ROUTE_FAMILIES",
    "pure_echo",
    "guardian_stage_1",
    "guardian_stage_2",
    "guardian_signed_echo",
    "v0_v5",
    "e2",
    "v6_plus",
    "must_follow_post_submit_readback",
    "post_submit_readback",
    "cache-busted",
    "ThreadPoolExecutor",
    "External agent swarm results",
]

missing = [phrase for phrase in required if phrase not in text]
if missing:
    print("FAIL: external agent journey swarm smoke missing contract phrase(s):")
    for phrase in missing:
        print("  -", phrase)
    sys.exit(1)

# Verify no actual write/POST operations exist (code-level, not docstring mentions)
import ast
try:
    tree = ast.parse(text)
except SyntaxError:
    print("FAIL: smoke_external_agent_journey_swarm.py has syntax errors")
    sys.exit(1)

source_lines = text.splitlines()
for node in ast.walk(tree):
    # Check for POST method strings in actual code (not comments/docstrings)
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        if node.value.upper() == "POST":
            print(f"FAIL: external swarm smoke must remain read-only; found POST method at line {node.lineno}")
            sys.exit(1)

# Check that urlopen is only used for GET (no data= argument)
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "urlopen":
            if node.keywords and any(k.arg == "data" for k in node.keywords):
                print(f"FAIL: urlopen with data= at line {node.lineno} implies POST")
                sys.exit(1)

print("PASS: external agent journey swarm smoke contract is guarded")
