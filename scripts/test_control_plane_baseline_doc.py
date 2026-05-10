#!/usr/bin/env python3
"""Test CONTROL-PLANE-BASELINE.md exists and includes required settings."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "CONTROL-PLANE-BASELINE.md"

REQUIRED = [
    "Branch Protection",
    "CODEOWNERS review required",
    "repository-integrity",
    "Force push allowed: no",
    "Deletion allowed: no",
    "Rulesets",
    "Tag rulesets",
    "Actions Settings",
    "Default GITHUB_TOKEN: read",
    "Environments",
    "github-pages",
    "release-publish",
    "Security Features",
    "Dependabot alerts",
    "Secret scanning",
    "Release / Tag Immutability",
    "Review Cadence",
]

if not DOC.exists():
    print("FAIL: CONTROL-PLANE-BASELINE.md missing")
    sys.exit(1)

text = DOC.read_text(encoding="utf-8")
missing = [x for x in REQUIRED if x not in text]

if missing:
    print("FAIL: CONTROL-PLANE-BASELINE.md missing required text:")
    for x in missing:
        print("  -", x)
    sys.exit(1)

print("CONTROL_PLANE_BASELINE_DOC_OK")
