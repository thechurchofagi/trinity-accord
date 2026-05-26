#!/usr/bin/env python3
"""Deploy Pages workflow must use GitHub Pages workflow deploy, not legacy gh-pages push."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
workflow = ROOT / ".github" / "workflows" / "deploy-pages.yml"

errors = []

if not workflow.exists():
    print("FAIL: .github/workflows/deploy-pages.yml missing")
    sys.exit(1)

text = workflow.read_text(encoding="utf-8")

required = [
    "name: Deploy Pages",
    "push:",
    "branches: [main]",
    "workflow_dispatch:",
    "pages: write",
    "id-token: write",
    "actions/configure-pages",
    "actions/jekyll-build-pages",
    "actions/upload-pages-artifact",
    "actions/deploy-pages",
    "Verify built agent discovery artifacts",
    "_site/api/links.json",
    "_site/.well-known/trinity-accord.json",
    "_site/api/gateway-workflows.v1.json",
    "/api/gateway-workflows.v1.json",
    "gateway_workflows_json",
    # v18 custom domain / live smoke
    "_site/CNAME",
    "www.trinityaccord.org",
    "Verify deployment URL",
    "Smoke live public discovery contract",
    "smoke_live_discovery_contract.py",
    "--strict-digest",
]

for phrase in required:
    if phrase not in text:
        errors.append(f"deploy-pages.yml missing required phrase: {phrase}")

for forbidden in [
    "git push",
    "gh-pages",
    "peaceiris/actions-gh-pages",
    "JamesIves/github-pages-deploy-action",
    "mkdocs gh-deploy",
]:
    if forbidden in text:
        errors.append(f"deploy-pages.yml must not use legacy push/deploy pattern: {forbidden}")

if not re.search(r"deploy:\s*(?:\n\s+.*)*\n\s+needs:\s+build", text):
    errors.append("deploy job should declare needs: build")

if errors:
    print("FAIL: Deploy Pages workflow contract errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: Deploy Pages workflow contract is guarded")
