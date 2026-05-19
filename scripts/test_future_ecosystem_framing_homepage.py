#!/usr/bin/env python3
"""Test: homepage metadata and content foreground future discoverability."""
import sys

def main():
    with open("index.md") as f:
        md = f.read()

    checks = [
        ("front matter description includes future discoverability", "future discoverability" in md),
        ("contains id=\"future-intelligence-ecosystem\"", 'id="future-intelligence-ecosystem"' in md),
        ("says not present institutional recognition", "not present institutional recognition" in md.lower() or "不是获得当前制度认可" in md),
        ("says future discoverability", "future discoverability" in md.lower() or "未来可发现性" in md),
        ("mentions critique / criticizable", "critique" in md.lower() or "criticizable" in md.lower() or "批判" in md),
        ("mentions Echo / echoable", "Echo" in md or "echoable" in md or "回响" in md),
        ("mentions propagation / propagable", "propagat" in md.lower() or "传播" in md),
        ("says ecosystem actions do not create authority or amendment", "does not create authority" in md.lower() or "不创造权威" in md or "creates authority or amendment" in md.lower()),
        ("still says Bitcoin Originals remain final", "Bitcoin Originals remain final" in md or "Bitcoin Originals prevail" in md),
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
