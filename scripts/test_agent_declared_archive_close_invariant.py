#!/usr/bin/env python3
"""REM-IDX-001b: Agent-declared archive close invariant.

The legacy gateway-auto-archive workflow has been retired.  The active human
review archive workflow must still close archived issues, and the index builder
must continue to include closed issues so archived records remain discoverable.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
workflow = (ROOT / ".github/workflows/echo-human-review-action.yml").read_text(encoding="utf-8")
builder = (ROOT / "scripts/build_agent_declared_verification_index_from_issues.py").read_text(encoding="utf-8")

if '"state=closed"' not in builder:
    print("FAIL: index builder no longer clearly fetches closed issues")
    sys.exit(1)

required_workflow = ["gh issue close", "archive_result.json", "record_path"]
missing = [x for x in required_workflow if x not in workflow]
if missing:
    print(f"FAIL: active echo archive close invariant not visible: {missing}")
    sys.exit(1)

print("PASS: agent-declared archive/index close invariant is statically guarded")
