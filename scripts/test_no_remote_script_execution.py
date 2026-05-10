#!/usr/bin/env python3
"""Test: Ban curl|bash, wget|sh, and unpinned npx in CI/scripts."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SEARCH_DIRS = [ROOT / ".github" / "workflows", ROOT / "scripts"]

PATTERNS = [
    r"curl\s+[^|\n]+\|\s*(bash|sh)",
    r"wget\s+[^|\n]+\|\s*(bash|sh)",
    r"Invoke-WebRequest.+\|\s*iex",
]

# npx check: only in workflow files (not test scripts that contain pattern strings)
NPX_PATTERN = r"npx\s+[^@\s]+(\s|$)"

errors = []

for base in SEARCH_DIRS:
    if not base.exists():
        continue
    for path in base.rglob("*"):
        if path.is_dir():
            continue
        if path.suffix not in (".yml", ".yaml", ".sh", ".py", ".mjs", ".js"):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pat in PATTERNS:
            if re.search(pat, text, re.I):
                errors.append(f"{path.relative_to(ROOT)} matches {pat}")

# Check npx in workflow files only (test scripts contain pattern strings)
for path in (ROOT / ".github" / "workflows").glob("*.yml"):
    text = path.read_text(encoding="utf-8")
    if re.search(NPX_PATTERN, text, re.I):
        errors.append(f"{path.name}: uses unpinned npx")

if errors:
    print("FAIL: remote script execution pattern found:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("NO_REMOTE_SCRIPT_EXECUTION_OK")
