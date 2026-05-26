#!/usr/bin/env python3
"""Deploy Pages workflow must use only explicit allowed official GitHub actions."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
workflow = ROOT / ".github" / "workflows" / "deploy-pages.yml"

text = workflow.read_text(encoding="utf-8")

allowed = {
    "actions/checkout@v4",
    "actions/configure-pages@v5",
    "actions/jekyll-build-pages@v1",
    "actions/upload-pages-artifact@v3",
    "actions/deploy-pages@v4",
}

uses = set(re.findall(r"uses:\s*([^\s#]+)", text))

unexpected = sorted(uses - allowed)
missing = sorted(allowed - uses)

errors = []
if unexpected:
    errors.append(f"unexpected action(s) in deploy-pages.yml: {unexpected}")
if missing:
    errors.append(f"missing expected action(s) in deploy-pages.yml: {missing}")

# Explicitly forbid third-party Pages deploy actions.
for forbidden in [
    "peaceiris/actions-gh-pages",
    "JamesIves/github-pages-deploy-action",
]:
    if forbidden in text:
        errors.append(f"forbidden Pages deploy action present: {forbidden}")

if errors:
    print("FAIL: Deploy Pages action allowlist errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: Deploy Pages actions are explicitly allowlisted")
