#!/usr/bin/env python3
"""Agent-declared index builder must support --check drift detection."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "scripts" / "build_agent_declared_verification_index_from_issues.py"
text = path.read_text(encoding="utf-8")

required = [
    'parser.add_argument("--check"',
    "args.check",
    "is stale",
    "return 1",
]

ok = True
for frag in required:
    if frag not in text:
        print(f"FAIL: builder missing --check drift fragment: {frag}")
        ok = False

if not ok:
    sys.exit(1)

print("PASS: agent-declared index builder has --check mode")
