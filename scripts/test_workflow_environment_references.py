#!/usr/bin/env python3
"""Test that workflow environment references are documented in CONTROL-PLANE-BASELINE.md."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / ".github" / "workflows"
BASELINE = ROOT / "CONTROL-PLANE-BASELINE.md"

ALLOWED_ENVIRONMENTS = {
    "github-pages",
    "release-publish",
}

errors = []

for path in sorted(WF.glob("*.yml")):
    text = path.read_text(encoding="utf-8")
    for m in re.finditer(r"^\s*environment:\s*([A-Za-z0-9_.-]+)\s*$", text, re.M):
        env = m.group(1)
        if env not in ALLOWED_ENVIRONMENTS:
            errors.append(f"{path.name}: unknown environment {env}")

if BASELINE.exists():
    baseline = BASELINE.read_text(encoding="utf-8")
    for env in ALLOWED_ENVIRONMENTS:
        if env not in baseline:
            errors.append(f"CONTROL-PLANE-BASELINE.md missing environment {env}")
else:
    errors.append("CONTROL-PLANE-BASELINE.md missing")

if errors:
    print("FAIL: workflow environment reference errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("WORKFLOW_ENVIRONMENT_REFERENCES_OK")
