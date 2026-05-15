#!/usr/bin/env python3
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAIL = []

def check_file(path):
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    m = re.search(r"content_digest:\s*([a-f0-9]+)", text)
    if not m:
        FAIL.append(f"{path}: missing content_digest")
        return
    expected = m.group(1)
    lines = [line for line in text.splitlines() if "content_digest:" not in line]
    normalized = "\n".join(lines) + "\n"
    actual = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:len(expected)]
    if actual != expected:
        FAIL.append(f"{path}: digest mismatch expected={expected} actual={actual}")

def main():
    check_file("llms.txt")
    check_file("ai.txt")
    if FAIL:
        print("DIGEST TEST FAIL")
        for f in FAIL:
            print("FAIL:", f)
        sys.exit(1)
    print("DIGEST TEST PASS")

if __name__ == "__main__":
    main()
