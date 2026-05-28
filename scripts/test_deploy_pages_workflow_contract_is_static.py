#!/usr/bin/env python3
"""Deploy Pages workflow contract test must remain static/source-only."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "scripts" / "test_deploy_pages_workflow_contract.py"

text = path.read_text(encoding="utf-8")
errors: list[str] = []

# These patterns indicate actual dynamic/blocking operations.
# We skip strings that appear inside list literals (FORBIDDEN_* constants)
# since those are just contract definitions, not actual calls.
forbidden_patterns = [
    ("urllib.request", r"urllib\.request(?!\s*=)"),
    ("requests.get/post", r"requests\.(get|post|put|delete)\s*\("),
    ("urlopen call", r"urlopen\s*\("),
    ("subprocess.run call", r"subprocess\.run\s*\("),
    ("subprocess.check_call call", r"subprocess\.check_call\s*\("),
    ("subprocess.check_output call", r"subprocess\.check_output\s*\("),
    ("time.sleep call", r"time\.sleep\s*\("),
    ("while True loop", r"while\s+[Tt]rue\s*:"),
]

for label, pattern in forbidden_patterns:
    if re.search(pattern, text):
        errors.append(f"deploy workflow contract test contains actual dynamic operation: {label}")

required = [
    "yaml.safe_load",
    "deploy-pages.yml",
    "PASS: deploy-pages workflow contract",
]

for item in required:
    if item not in text:
        errors.append(f"deploy workflow contract test missing static-test marker: {item}")

if errors:
    print("FAIL: deploy workflow contract static-test errors:")
    for error in errors:
        print("  -", error)
    sys.exit(1)

print("PASS: deploy workflow contract test is static/source-only")
