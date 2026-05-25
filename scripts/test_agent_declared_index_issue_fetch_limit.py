#!/usr/bin/env python3
"""Verify agent-declared index fetch limit is not 200."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "scripts/build_agent_declared_verification_index_from_issues.py"
text = p.read_text(encoding="utf-8")

if "default=200" in text:
    print("FAIL: agent-declared index fetch limit is still 200")
    sys.exit(1)

if "--paginate" not in text and "default=10000" not in text:
    print("FAIL: no pagination or high default limit found")
    sys.exit(1)

print("PASS: agent-declared index fetch limit/pagination hardened")
