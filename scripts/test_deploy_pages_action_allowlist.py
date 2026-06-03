#!/usr/bin/env python3
"""Deploy Pages workflow must use only explicit allowed official GitHub actions."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
workflow = ROOT / ".github" / "workflows" / "deploy-pages.yml"

text = workflow.read_text(encoding="utf-8")

allowed = {
    "actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5",
    "actions/configure-pages@983d7736d9b0ae728b81ab479565c72886d7745b",
    "actions/jekyll-build-pages@44a6e6beabd48582f863aeeb6cb2151cc1716697",
    "actions/upload-pages-artifact@56afc609e74202658d3ffba0e8f6dda462b719fa",
    "actions/deploy-pages@d6db90164ac5ed86f2b6aed7e0febac5b3c0c03e",
    "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065",
}

uses = set(re.findall(r"uses:\s*([^\s#]+)", text))

# Extract action names (without version/SHA) for matching
def action_name(ref):
    return ref.split("@")[0]

allowed_names = {action_name(a) for a in allowed}
used_names = {action_name(u) for u in uses}

unexpected_names = sorted(used_names - allowed_names)
unexpected_refs = sorted(u for u in uses if action_name(u) not in allowed_names)

errors = []
if unexpected_refs:
    errors.append(f"unexpected action(s) in deploy-pages.yml: {unexpected_refs}")
if not used_names:
    errors.append("no actions found in deploy-pages.yml")

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
