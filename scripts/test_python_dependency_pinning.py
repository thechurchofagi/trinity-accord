#!/usr/bin/env python3
"""Test: Python CI dependencies must be pinned via requirements-ci.txt."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REQ = ROOT / "requirements-ci.txt"
WF_DIR = ROOT / ".github" / "workflows"

errors = []

if not REQ.exists():
    errors.append("requirements-ci.txt missing")
else:
    req_text = REQ.read_text(encoding="utf-8")
    for required in ["jsonschema==", "opentimestamps-client=="]:
        if required not in req_text:
            errors.append(f"requirements-ci.txt missing pinned {required}")

for path in WF_DIR.glob("*.yml"):
    text = path.read_text(encoding="utf-8")

    if "pip install --upgrade pip" in text or "python3 -m pip install --upgrade pip" in text:
        errors.append(f"{path.name}: unpinned pip upgrade")

    for line in text.splitlines():
        stripped = line.strip()
        if "pip install" not in stripped:
            continue
        if "-r requirements-ci.txt" in stripped:
            continue
        if re.search(r"\b[a-zA-Z0-9_.-]+==[0-9]", stripped):
            continue
        if stripped.startswith("#"):
            continue
        errors.append(f"{path.name}: unpinned pip install line: {stripped}")

if errors:
    print("FAIL: Python dependency pinning violations:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PYTHON_DEPENDENCY_PINNING_OK")
