#!/usr/bin/env python3
"""REM-IDX-001b: Agent-declared archive close invariant."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
gateway = (ROOT / ".github/workflows/gateway-auto-archive.yml").read_text(encoding="utf-8")
builder = (ROOT / "scripts/build_agent_declared_verification_index_from_issues.py").read_text(encoding="utf-8")

if '"state=closed"' not in builder:
    print("FAIL: index builder no longer clearly fetches closed issues")
    sys.exit(1)

required_gateway = ["gh issue close", "archive_record=$RECORD_PATH"]
missing = [x for x in required_gateway if x not in gateway]
if missing:
    print(f"FAIL: gateway archive close invariant not visible: {missing}")
    sys.exit(1)

print("PASS: agent-declared archive/index close invariant is statically guarded")
