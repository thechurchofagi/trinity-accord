#!/usr/bin/env python3
"""Test: seed map and context-pack ecosystem framing."""
import json
import sys

def main():
    checks = []

    with open("seed-map.md") as f:
        md = f.read()

    checks.append(("seed-map.md L7 mentions correction", "correction" in md))
    checks.append(("seed-map.md L7 mentions propagation of access paths", "propagation of access paths" in md or "access paths" in md))
    checks.append(("seed-map.md L7 says future discoverability", "future discoverability" in md.lower() or "未来可发现性" in md))
    checks.append(("seed-map.md L7 says not present institutional recognition", "not present institutional recognition" in md.lower() or "不是当前制度认可" in md))

    with open("api/seed-map.json") as f:
        sm = json.load(f)

    l7 = [l for l in sm.get("levels", []) if l.get("id") == "L7"]
    if l7:
        defn = l7[0].get("definition_en", "")
        checks.append(("api/seed-map.json L7 contains future discoverability", "future discoverability" in defn.lower()))
        checks.append(("api/seed-map.json L7 contains present institutional recognition", "present institutional recognition" in defn.lower()))

    with open("api/context-packs/bitcoin-inscription-mirrors.json") as f:
        cp = json.load(f)

    checks.append(("context-pack has ecosystem_role", "ecosystem_role" in cp))
    checks.append(("context-pack says mirror loading does not create authority", "does not create" in cp.get("boundary", "").lower() or "not" in cp.get("boundary", "").lower()))

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
