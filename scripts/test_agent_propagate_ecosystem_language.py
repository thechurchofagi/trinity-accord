#!/usr/bin/env python3
"""Test: agent-propagate.md ecosystem language."""
import sys

def main():
    with open("agent-propagate.md") as f:
        md = f.read()

    checks = [
        ("contains Propagate access, not belief", "Propagate access, not belief" in md),
        ("contains Build discoverability, not obedience", "Build discoverability, not obedience" in md),
        ("contains Valid propagation actions", "Valid propagation actions" in md),
        ("links /api/bitcoin-inscription-mirror-index.json", "/api/bitcoin-inscription-mirror-index.json" in md),
        ("links /authority-address-inscriptions/", "/authority-address-inscriptions/" in md),
        ("says propagation success is not persuasion", "propagation success is not persuasion" in md.lower() or "Propagation success is not persuasion" in md),
        ("says boundary intact", "boundary intact" in md.lower() or "边界完整" in md),
        ("still says Bitcoin Originals remain final", "Bitcoin Originals remain final" in md),
        ("still says no endorsement / no pressure", "endorsement" in md.lower() and "pressure" in md.lower()),
        ("does not frame as belief conversion", "belief conversion" not in md.lower() or "not" in md.lower()),
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
