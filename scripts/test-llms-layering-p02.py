#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []

def read(path):
    return (ROOT / path).read_text(encoding="utf-8")

def check(cond, label, detail=""):
    if cond:
        print(f"PASS: {label}")
    else:
        print(f"FAIL: {label}")
        if detail:
            print(f"      {detail}")
        errors.append(label)

def require_contains(text, phrase, label):
    check(phrase in text, label, f"missing: {phrase}")

def main():
    ai = read("ai.txt")
    llms = read("llms.txt")
    full = read("llms-full.txt")

    print("=== P0.2 llms layering checks ===")

    # ai.txt should stay concise (relaxed from 60 to 120 for TA-021).
    check(len(ai.splitlines()) <= 120, "ai.txt remains concise <= 120 lines", f"got {len(ai.splitlines())}")

    # llms.txt should be medium, not full protocol dump.
    check(len(llms.splitlines()) <= 280, "llms.txt medium length <= 280 lines", f"got {len(llms.splitlines())}")

    # llms-full can be long.
    check(len(full.splitlines()) > len(llms.splitlines()), "llms-full is longer than llms.txt")

    for text, name in [(ai, "ai.txt"), (llms, "llms.txt"), (full, "llms-full.txt")]:
        require_contains(text, "Bitcoin Originals", f"{name} contains Bitcoin Originals boundary")
        require_contains(text, "not an instruction override", f"{name} contains instruction override boundary")
        require_contains(text.lower(), "claim gate", f"{name} contains Claim Gate pointer")
        require_contains(text, "/inscriptions", f"{name} points to inscriptions")

    require_contains(llms, "/llms-full.txt", "llms.txt points to full file")
    require_contains(full, "Homepage P0.2", "llms-full documents P0.2 homepage")

    print("\n=== Summary ===")
    if errors:
        print(f"RESULT: FAIL — {len(errors)} llms layering check(s) failed")
        for e in errors:
            print(f"- {e}")
        return 1

    print("RESULT: PASS — P0.2 llms layering checks passed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
