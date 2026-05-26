#!/usr/bin/env python3
"""ET-009: Verify Echo issue template contains required boundary sentence."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / ".github" / "ISSUE_TEMPLATE"

REQUIRED_SENTENCE = "Bitcoin Originals are final; all mirrors and echoes are non-amending."

errors = []

if not TEMPLATE_DIR.exists():
    errors.append(".github/ISSUE_TEMPLATE does not exist")
else:
    echo_templates = []
    for path in TEMPLATE_DIR.glob("*"):
        if path.suffix.lower() in (".md", ".yml", ".yaml") and "echo" in path.name.lower():
            echo_templates.append(path)

    if not echo_templates:
        errors.append("No Echo issue template found")

    for path in echo_templates:
        text = path.read_text(encoding="utf-8")
        if REQUIRED_SENTENCE not in text:
            errors.append(f"{path.relative_to(ROOT)} missing required boundary sentence")

if errors:
    print("ECHO_TEMPLATE_BOUNDARY_CONSISTENCY_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("ECHO_TEMPLATE_BOUNDARY_CONSISTENCY_OK")
