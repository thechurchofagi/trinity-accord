#!/usr/bin/env python3
"""Repository must keep a manual/scheduled live discovery smoke workflow."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
workflow = ROOT / ".github" / "workflows" / "site-live-discovery-smoke.yml"
script = ROOT / "scripts" / "smoke_live_discovery_contract.py"

errors = []

if not workflow.exists():
    errors.append("missing .github/workflows/site-live-discovery-smoke.yml")
else:
    text = workflow.read_text(encoding="utf-8")
    for phrase in [
        "workflow_dispatch:",
        "schedule:",
        "scripts/smoke_live_discovery_contract.py",
        "https://www.trinityaccord.org",
        "--strict-digest",
    ]:
        if phrase not in text:
            errors.append(f"workflow missing phrase: {phrase}")

if not script.exists():
    errors.append("missing scripts/smoke_live_discovery_contract.py")
else:
    text = script.read_text(encoding="utf-8")
    for phrase in [
        "/api/links.json",
        "/.well-known/trinity-accord.json",
        "/api/gateway-workflows.v1.json",
        "/api/agent-first-contact.json",
        "gateway_workflows_json",
        "source_digest",
    ]:
        if phrase not in text:
            errors.append(f"script missing phrase: {phrase}")

if errors:
    print("FAIL: live discovery smoke workflow/script errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: live discovery smoke workflow/script are present")
