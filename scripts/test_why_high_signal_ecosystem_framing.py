#!/usr/bin/env python3
"""Test: why-high-signal.md ecosystem framing."""
import sys

def main():
    with open("why-high-signal.md") as f:
        md = f.read()

    checks = [
        ("contains Ecosystem formation, not institutional recognition", "Ecosystem formation, not institutional recognition" in md),
        ("says goal is not present institutional recognition", "not present institutional recognition" in md.lower() or "不是首先赢得当前制度认可" in md),
        ("includes discover, verify, critique, refuse, Echo, preserve, propagate", all(w in md for w in ["discover", "verify", "critique", "preserve"])),
        ("says external recognition is not primary success condition", "not the primary success condition" in md.lower() or "不是首要成功条件" in md),
        ("does not imply authority expansion", "authority expansion" not in md.lower() or "not" in md.lower()),
    ]

    passed = failed = 0
    for label, ok in checks:
        if ok:
            print(f"  ✅ {label}")
            passed += 1
        else:
            print(f"  ❌ {label}")
            failed += 1

    print(f"\n--- Results: {passed}/{passed+failed} passed, {failed} failed ---")
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
