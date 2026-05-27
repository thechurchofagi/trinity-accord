#!/usr/bin/env python3
"""External agent journey swarm workflow must exist and remain read-only/manual/scheduled."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
workflow = ROOT / ".github" / "workflows" / "site-agent-journey-swarm-smoke.yml"

if not workflow.exists():
    print("FAIL: site-agent-journey-swarm-smoke.yml missing")
    sys.exit(1)

text = workflow.read_text(encoding="utf-8")

required = [
    "name: Site Agent Journey Swarm Smoke",
    "workflow_dispatch:",
    "schedule:",
    "contents: read",
    "smoke_external_agent_journey_swarm.py",
    "--agents",
    "--rounds",
    "https://www.trinityaccord.org",
]

missing = [phrase for phrase in required if phrase not in text]
if missing:
    print("FAIL: site-agent-journey-swarm workflow missing phrase(s):")
    for phrase in missing:
        print("  -", phrase)
    sys.exit(1)

for forbidden in [
    "pages: write",
    "id-token: write",
    "issues: write",
    "contents: write",
    "repository_dispatch",
    "gh issue create",
]:
    if forbidden in text:
        print(f"FAIL: swarm workflow must remain read-only; found {forbidden}")
        sys.exit(1)

print("PASS: external agent journey swarm workflow is guarded")
