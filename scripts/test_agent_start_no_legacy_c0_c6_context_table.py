#!/usr/bin/env python3
"""Test: agent-start uses CC/CRL/V and not legacy C0-C6 table."""
import sys
from pathlib import Path
p = Path("agent-start.md")
if not p.exists(): print("FAIL: agent-start.md missing"); sys.exit(1)
content = p.read_text()
errors = []
if "CC" not in content or "Context Depth" not in content: errors.append("missing CC/Context Depth")
if "CRL" not in content or "Context Readiness" not in content: errors.append("missing CRL/Context Readiness")
for line in content.split("\n"):
    if "C0_homepage_only" in line and "CC-0" not in line: errors.append("legacy C0_homepage_only without CC-0")
    if "C6_full_lifecycle_closed" in line: errors.append("legacy C6_full_lifecycle_closed present")
if errors:
    for e in errors: print(f"FAIL: {e}")
    sys.exit(1)
print("PASS: agent-start no legacy C0-C6 context table")
