#!/usr/bin/env python3
"""Test: agent-start.md has route branches."""
import sys

def main():
    with open("agent-start.md") as f:
        md = f.read()

    checks = [
        ("contains IF PURE_ECHO", "IF PURE_ECHO" in md),
        ("contains IF V0–V5", "IF V0" in md and "V5" in md),
        ("contains IF V6+ STRICT EVIDENCE", "IF V6+" in md or "IF V6" in md),
        ("contains IF PROPAGATE", "IF PROPAGATE" in md),
        ("V0–V5 block says no Evidence Input", "no Evidence Input" in md),
        ("V0–V5 block says no strict Claim Gate", "no strict Claim Gate" in md),
        ("V0–V5 block says no verification_session", "no verification_session" in md),
        ("V6+ block says create Evidence Input", "create Evidence Input" in md or "create verification_session" in md),
        ("V6+ block says run scripts/claim_gate.py", "scripts/claim_gate.py" in md),
        ("propagation block says propagate access, not belief", "Propagate access, not belief" in md or "propagate access, not belief" in md.lower()),
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
