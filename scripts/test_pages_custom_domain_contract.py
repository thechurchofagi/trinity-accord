#!/usr/bin/env python3
"""Pages custom-domain identity and live verification must be explicit."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
cname = ROOT / "CNAME"

errors = []

if not cname.exists():
    errors.append("missing root CNAME file")
else:
    content = cname.read_text(encoding="utf-8").strip()
    if content != "www.trinityaccord.org":
        errors.append(f"CNAME must be exactly www.trinityaccord.org, got {content!r}")

workflow = ROOT / ".github" / "workflows" / "deploy-pages.yml"
if not workflow.exists():
    errors.append("missing deploy-pages.yml")
else:
    text = workflow.read_text(encoding="utf-8")
    for phrase in [
        "_site/CNAME",
        "www.trinityaccord.org",
        "Verify live machine contract after edge propagation",
        "--strict-digest",
        "smoke_live_discovery_contract_v2.py",
        "check_deployment_freshness_v2.py",
    ]:
        if phrase not in text:
            errors.append(f"deploy-pages.yml missing custom-domain/live-smoke phrase: {phrase}")

if errors:
    print("FAIL: Pages custom domain contract errors:")
    for error in errors:
        print("  -", error)
    sys.exit(1)

print("PASS: Pages custom-domain identity and v2 live verification are explicit")
