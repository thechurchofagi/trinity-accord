#!/usr/bin/env python3
"""FUNC-GUARD-002: Guardian rebase path reruns registry allocation/generation."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / ".github/workflows/guardian-registry-auto-list.yml").read_text(encoding="utf-8")

required = [
    "git rebase origin/main",
    "auto_register_guardian_from_gateway_issues.py",
    "generate_guardian_registry_page.py",
    "git commit --amend --no-edit",
]
missing = [x for x in required if x not in text]
if missing:
    print(f"FAIL: guardian rebase path missing registry regeneration: {missing}")
    sys.exit(1)

print("PASS: guardian rebase path reruns registry allocation/generation")
