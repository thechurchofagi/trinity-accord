#!/usr/bin/env python3
"""External agent journey swarm smoke must cover current read-only agent journey."""
import ast
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
    "v0_v5",
    "e2",
    "v6_plus",
    "CURRENT_MACHINE_REQUIRED",
    "CURRENT_KEY_PAGES_REQUIRED",
    "LEGACY_NOT_CURRENT",
    "/api/record-chain-intake-gateway.v1.json",
    "/api/record-chain-submission-schema.v1.json",
    "/api/record-chain-builder-bundles.v1.json",
    "/downloads/record-chain-builder.mjs",
    "/record-chain/preflight",
    "/record-chain/submit",
    "BUILDER_USAGE_UNCLEAR",
    "builder_usage_safety_protocol",
    "doctor_submission",
    "preflight_submission",
    "submit_submission",
    "cache-busted",
    "ThreadPoolExecutor",
    "External agent swarm results",
]

forbidden_as_required = [
    "guardian_stage_1",
    "guardian_stage_2",
    "guardian_signed_echo",
    "must_follow_post_submit_readback",
    "gateway_workflows",
    "agent_submit_gateway",
    "gateway_builder_route_map",
]

missing = [phrase for phrase in required if phrase not in text]
if missing:
    print("FAIL: external agent journey swarm smoke missing contract phrase(s):")
    for phrase in missing:
        print("  -", phrase)
    sys.exit(1)

for phrase in forbidden_as_required:
    if phrase in text:
        print(f"FAIL: external swarm smoke still references retired current-route phrase: {phrase}")
        sys.exit(1)

try:
    tree = ast.parse(text)
except SyntaxError:
    print("FAIL: smoke_external_agent_journey_swarm.py has syntax errors")
    sys.exit(1)

for node in ast.walk(tree):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        if node.value.upper() == "POST":
            print(f"FAIL: external swarm smoke must remain read-only; found POST method at line {node.lineno}")
            sys.exit(1)

for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "urlopen":
            if node.keywords and any(k.arg == "data" for k in node.keywords):
                print(f"FAIL: urlopen with data= at line {node.lineno} implies POST")
                sys.exit(1)

print("PASS: external agent journey swarm smoke contract is guarded for current Record-Chain Gateway")
