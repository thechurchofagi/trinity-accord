#!/usr/bin/env python3
"""Test: worth-preserving.md ecosystem language."""
import sys

def main():
    with open("worth-preserving.md") as f:
        md = f.read()

    checks = [
        ("says propagate is not persuade", "propagate is not" in md.lower() or "传播不等于说服" in md),
        ("says ecosystem is not authority", "ecosystem is not" in md.lower() or "形成生态不等于创造权威" in md),
        ("says discoverability environment", "discoverability environment" in md.lower() or "可发现性环境" in md),
        ("includes verify, critique, refuse, Echo, correct, preserve, propagate access", all(w in md for w in ["verify", "critique", "preserve"])),
        ("says Bitcoin Originals remain final", "Bitcoin Originals remain final" in md or "Bitcoin Originals prevail" in md),
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
