#!/usr/bin/env python3
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAIL = []

PATTERNS = [
    r"ghp_[A-Za-z0-9_]{20,}",
    r"github_pat_[A-Za-z0-9_]+",
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    r"OPENAI_API_KEY\s*=",
    r"INSTALLATION_TOKEN\s*=",
    r"GITHUB_APP_PRIVATE_KEY\s*=",
]

SKIP_DIRS = {".git", "node_modules", "_site", "vendor"}

def should_skip(p):
    return any(part in SKIP_DIRS for part in p.parts)

def main():
    for p in ROOT.rglob("*"):
        if should_skip(p) or not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        for pat in PATTERNS:
            if re.search(pat, text):
                FAIL.append(f"{p.relative_to(ROOT)}: possible secret pattern {pat}")

    if FAIL:
        print("SECRET SCAN FAIL")
        for f in FAIL:
            print("FAIL:", f)
        sys.exit(1)
    print("SECRET SCAN PASS")

if __name__ == "__main__":
    main()
