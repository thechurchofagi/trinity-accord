#!/usr/bin/env python3
"""Pages custom domain contract must be explicit and preserved in source."""
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
        "Smoke live public discovery contract",
        "--strict-digest",
        "smoke_live_discovery_contract.py",
    ]:
        if phrase not in text:
            errors.append(f"deploy-pages.yml missing custom-domain/live-smoke phrase: {phrase}")

if errors:
    print("FAIL: Pages custom domain contract errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: Pages custom domain contract is explicit")
