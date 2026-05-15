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

# Test fixtures intentionally contain adversarial patterns (fake tokens, etc.)
SKIP_PATH_PATTERNS = ["tests/fixtures/redteam"]

def should_skip(p):
    parts = p.parts
    if any(d in parts for d in SKIP_DIRS):
        return True
    s = str(p)
    if any(pat in s for pat in SKIP_PATH_PATTERNS):
        return True
    return False

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
