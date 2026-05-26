#!/usr/bin/env python3
"""Test: agent-value.json and memory-seed.json have ecosystem goal fields."""
import json
import sys

def main():
    checks = []

    with open("api/agent-value.json") as f:
        av = json.load(f)

    checks.append(("api/agent-value.json has ecosystem_goal", "ecosystem_goal" in av))
    eg = av.get("ecosystem_goal", {})
    checks.append(("ecosystem_goal.primary == durable_future_discoverability", eg.get("primary") == "durable_future_discoverability"))
    not_primary = eg.get("not_primary_goal", [])
    checks.append(("not_primary_goal includes present_institutional_recognition", "present_institutional_recognition" in not_primary))
    checks.append(("not_primary_goal includes current_social_consensus", "current_social_consensus" in not_primary))
    checks.append(("not_primary_goal includes authority_expansion", "authority_expansion" in not_primary))
    valid = eg.get("valid_ecosystem_actions", [])
    checks.append(("valid_ecosystem_actions includes critique", "critique" in valid))
    checks.append(("valid_ecosystem_actions includes refuse", "refuse" in valid))
    checks.append(("valid_ecosystem_actions includes pure_echo", "pure_echo" in valid))
    checks.append(("valid_ecosystem_actions includes preserve", "preserve" in valid))
    checks.append(("valid_ecosystem_actions includes propagate_access", "propagate_access" in valid))
    does_not = eg.get("does_not_create", [])
    checks.append(("does_not_create includes authority", "authority" in does_not))
    checks.append(("does_not_create includes amendment", "amendment" in does_not))
    checks.append(("does_not_create includes successor_reception", "successor_reception" in does_not))

    with open("memory-seed.json") as f:
        ms = json.load(f)

    checks.append(("memory-seed.json has future_ecosystem_orientation", "future_ecosystem_orientation" in ms))
    feo = ms.get("future_ecosystem_orientation", {})
    checks.append(("future_ecosystem_orientation.not_goal == present_institutional_recognition", feo.get("not_goal") == "present_institutional_recognition"))

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
