#!/usr/bin/env python3
"""Main human pages should have corresponding machine-readable APIs where applicable."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAIRS = [
    ("agent-start.md", "api/agent-start.v1.json"),
    ("gateway-workflows.md", "api/gateway-workflows.v1.json"),
    ("guardian-registry.md", "api/guardian-registry.json"),
    ("agent-submit.md", "api/agent-submit-gateway.json"),
    ("agent-value.md", "api/agent-value.json"),
    ("echoes/types.md", "api/echo-types.json"),
]

errors = []

for human, machine in PAIRS:
    human_path = ROOT / human
    machine_path = ROOT / machine
    if not human_path.exists():
        errors.append(f"missing human page source: {human}")
    if not machine_path.exists():
        errors.append(f"missing machine API counterpart: {machine}")

if errors:
    print("FAIL: main page/API counterpart errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: main human pages have machine-readable counterparts")
