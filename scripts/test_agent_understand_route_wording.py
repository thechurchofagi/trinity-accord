#!/usr/bin/env python3
"""Test: agent-understand.md route-specific archive wording."""
import sys

def main():
    with open("agent-understand.md") as f:
        md = f.read()

    checks = [
        ("contains route-valid", "route-valid" in md),
        ("mentions build_agent_declared_archive_payload.py", "build_agent_declared_archive_payload.py" in md),
        ("mentions V6+ strict evidence", "V6+" in md or "V6" in md),
        ("says V0–V5 no Evidence Input or no verification_session", "no Evidence Input" in md or "no verification_session" in md),
        ("does not imply Report Builder for all archived records", "Only route-valid" in md),
        ("scopes Evidence Input to V6+", "V6+ strict evidence" in md or "CHOOSE VERIFY+ECHO" in md),
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
