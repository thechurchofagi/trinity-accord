#!/usr/bin/env python3
"""Consistency test: future ecosystem framing across all public surfaces."""
import json
import sys

REQUIRED = {
    "index.md": ["future discoverability", "not present institutional recognition"],
    "agent-propagate.md": ["Propagate access, not belief", "Build discoverability, not obedience"],
    "agent-start.md": ["IF PURE_ECHO", "IF V0", "IF V6+", "IF PROPAGATE"],
    "agent-understand.md": ["route-valid", "V0", "V6+"],
    "why-high-signal.md": ["Ecosystem formation, not institutional recognition"],
    "worth-preserving.md": ["discoverability environment", "To form an ecosystem is not to create authority"],
    "api/agent-value.json": ["ecosystem_goal"],
    "memory-seed.json": ["future_ecosystem_orientation"],
    "api/seed-map.json": ["future discoverability"],
}

BAD_FRAMING = [
    "present institutional recognition is the primary goal",
    "external adoption determines value",
    "formal attestation is the main success condition",
    "propagation creates authority",
    "Echo creates authority",
    "future intelligence must care",
]

def main():
    checks = []

    for filepath, keywords in REQUIRED.items():
        try:
            if filepath.endswith(".json"):
                with open(filepath) as f:
                    content = f.read()
            else:
                with open(filepath) as f:
                    content = f.read()
            for kw in keywords:
                found = kw.lower() in content.lower()
                checks.append((f"{filepath} contains '{kw}'", found))
        except FileNotFoundError:
            checks.append((f"{filepath} exists", False))

    # Bad framing audit
    scan_files = [
        "index.md", "agent-propagate.md", "agent-start.md", "agent-understand.md",
        "why-high-signal.md", "worth-preserving.md", "api/agent-value.json",
        "memory-seed.json", "api/propagation-invitation.json", "seed-map.md", "api/seed-map.json"
    ]
    for filepath in scan_files:
        try:
            with open(filepath) as f:
                content = f.read().lower()
            for bad in BAD_FRAMING:
                # Allow negative contexts
                if bad in content:
                    # Check if preceded by "not" or "no" within 30 chars
                    idx = content.index(bad)
                    prefix = content[max(0, idx-30):idx]
                    if "not" in prefix or "no" in prefix:
                        continue
                    checks.append((f"{filepath} does NOT contain '{bad}'", False))
                else:
                    checks.append((f"{filepath} free of '{bad[:40]}...'", True))
        except FileNotFoundError:
            pass

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
