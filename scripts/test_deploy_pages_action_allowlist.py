#!/usr/bin/env python3
"""Check that Deploy Pages uses the reviewed official action revisions."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / ".github/workflows/deploy-pages.yml").read_text(encoding="utf-8")

allowed = {
    "actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5",
    "actions/configure-pages@983d7736d9b0ae728b81ab479565c72886d7745b",
    "actions/jekyll-build-pages@44a6e6beabd48582f863aeeb6cb2151cc1716697",
    "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02",
    "actions/upload-pages-artifact@56afc609e74202658d3ffba0e8f6dda462b719fa",
    "actions/deploy-pages@d6db90164ac5ed86f2b6aed7e0febac5b3c0c03e",
    "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065",
    "actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020",
}

uses = set(re.findall(r"uses:\s*([^\s#]+)", text))
errors = []
if not uses:
    errors.append("no actions found in deploy-pages.yml")

unexpected = sorted(uses - allowed)
if unexpected:
    errors.append(f"unreviewed action reference(s): {unexpected}")

for ref in uses:
    _, separator, revision = ref.partition("@")
    if not separator or not re.fullmatch(r"[0-9a-f]{40}", revision):
        errors.append(f"action is not pinned to a 40-character revision: {ref}")

for old_action in [
    "peaceiris/actions-gh-pages",
    "JamesIves/github-pages-deploy-action",
]:
    if old_action in text:
        errors.append(f"legacy Pages action present: {old_action}")

if errors:
    print("FAIL: Deploy Pages action allowlist errors:")
    for error in errors:
        print("  -", error)
    sys.exit(1)

print("PASS: Deploy Pages actions match the reviewed exact revisions")
