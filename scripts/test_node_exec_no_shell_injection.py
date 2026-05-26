#!/usr/bin/env python3
"""Regression test: Node verification scripts must not use shell-parsed execSync with variable input."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts"
errors = []

for path in sorted(SCRIPT_DIR.glob("*.mjs")):
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(ROOT)

    if re.search(r"import\s*\{[^}]*\bexecSync\b[^}]*\}\s*from\s*['\"]child_process['\"]", text):
        errors.append(f"{rel}: imports execSync; use execFileSync/spawnSync with shell:false")

    if re.search(r"\bexecSync\s*\(", text):
        errors.append(f"{rel}: calls execSync; use execFileSync/spawnSync with args array")

    # Also flag obvious shell:true use.
    if re.search(r"shell\s*:\s*true", text):
        errors.append(f"{rel}: shell:true is forbidden in verification scripts")

if errors:
    print("NODE_EXEC_NO_SHELL_INJECTION_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("NODE_EXEC_NO_SHELL_INJECTION_OK")
