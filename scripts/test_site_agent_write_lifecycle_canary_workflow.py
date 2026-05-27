#!/usr/bin/env python3
"""Write lifecycle canary workflow must be manual-only and gated."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
workflow = ROOT / ".github" / "workflows" / "site-agent-write-lifecycle-canary.yml"

if not workflow.exists():
    print("FAIL: site-agent-write-lifecycle-canary.yml missing")
    sys.exit(1)

text = workflow.read_text(encoding="utf-8")

required = [
    "workflow_dispatch:",
    "permissions:",
    "contents: read",
    "smoke_external_agent_write_lifecycle_canary.py",
    "TRINITY_LIVE_CANARY_WRITE",
    "secrets.TRINITY_LIVE_CANARY_WRITE",
    "preflight-only",
    "single-write-canary",
    "duplicate-canary",
]

missing = [phrase for phrase in required if phrase not in text]
if missing:
    print("FAIL: write lifecycle canary workflow missing phrase(s):")
    for phrase in missing:
        print("  -", phrase)
    sys.exit(1)

for forbidden in [
    "schedule:",
    "contents: write",
    "issues: write",
    "pages: write",
    "id-token: write",
]:
    if forbidden in text:
        print(f"FAIL: write canary workflow should not include {forbidden}")
        sys.exit(1)

print("PASS: write lifecycle canary workflow is manual-only and gated")
