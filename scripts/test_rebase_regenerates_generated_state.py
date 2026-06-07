#!/usr/bin/env python3
"""DEEP-REBASE-001: active rebase paths regenerate generated state before push."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

checks = {
    ".github/workflows/echo-human-review-action.yml": [
        "git pull --rebase",
        "generate_public_home_status.py",
        "git push --force-with-lease",
    ],
    ".github/workflows/rebuild-agent-declared-index.yml": [
        "git pull --rebase",
        "generate_public_home_status.py",
        "git commit --amend --no-edit",
    ],
    ".github/workflows/record-chain-append.yml": [
        "git pull --rebase",
        "generate_public_home_status.py",
        "Push failed on attempt",
    ],
}

for file, terms in checks.items():
    p = ROOT / file
    if not p.exists():
        print(f"FAIL: active workflow missing: {file}")
        sys.exit(1)
    text = p.read_text(encoding="utf-8")
    missing = [t for t in terms if t not in text]
    if missing:
        print(f"FAIL: {file} missing rebase-regeneration terms: {missing}")
        sys.exit(1)

print("PASS: active rebase paths regenerate generated state before push")
