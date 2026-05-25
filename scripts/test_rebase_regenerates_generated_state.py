#!/usr/bin/env python3
"""DEEP-REBASE-001: rebase paths regenerate generated state before push."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

checks = {
    ".github/workflows/gateway-auto-archive.yml": [
        "git pull --rebase",
        "generate_public_home_status.py",
        "git commit --amend --no-edit",
    ],
    ".github/workflows/guardian-registry-auto-list.yml": [
        "git rebase origin/main",
        "auto_register_guardian_from_gateway_issues.py",
        "generate_public_home_status.py",
        "generate_guardian_registry_page.py",
        "git commit --amend --no-edit",
    ],
    ".github/workflows/rebuild-agent-declared-index.yml": [
        "git pull --rebase",
        "generate_public_home_status.py",
        "git commit --amend --no-edit",
    ],
}

for file, terms in checks.items():
    p = ROOT / file
    text = p.read_text(encoding="utf-8")
    missing = [t for t in terms if t not in text]
    if missing:
        print(f"FAIL: {file} missing rebase-regeneration terms: {missing}")
        sys.exit(1)

print("PASS: rebase paths regenerate generated state before push")
