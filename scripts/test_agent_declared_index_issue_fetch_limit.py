#!/usr/bin/env python3
"""REM-IDX-001: Agent-declared index uses paginated REST API, not gh issue list."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "scripts/build_agent_declared_verification_index_from_issues.py"
text = p.read_text(encoding="utf-8")

if "default=200" in text:
    print("FAIL: default issue fetch limit is still 200")
    sys.exit(1)

if '"issue", "list"' in text or '"issue", "list",' in text:
    print("FAIL: agent-declared index still uses gh issue list instead of paginated REST API")
    sys.exit(1)

required = [
    '"api"',
    'f"repos/{repo}/issues"',
    '"per_page=100"',
    "page = 1",
    "page += 1",
    '"pull_request" in item',
]
missing = [x for x in required if x not in text]
if missing:
    print(f"FAIL: paginated REST issue fetch missing terms: {missing}")
    sys.exit(1)

print("PASS: agent-declared verification index uses paginated REST issue fetch")
