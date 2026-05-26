#!/usr/bin/env python3
"""
Test: AI-facing language boundaries.
Verifies llms.txt and ai.txt use suggestion language, not command directives.
"""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P, F = 0, 0
def check(l, c, d=""):
    global P, F
    if c: P += 1; print(f"  PASS: {l}")
    else: F += 1; print(f"  FAIL: {l} {d}")

def test_llms():
    print("\n--- llms.txt ---")
    with open(os.path.join(ROOT, "llms.txt")) as f: c = f.read()
    lines = c.split("\n")
    check("has 'not a system prompt'", "not a system prompt" in c.lower() or "not an instruction override" in c.lower())
    check("no 'Read first' heading", not any(l.strip().startswith("## Read first") for l in lines))
    check("no standalone 'Do not assess'", "Do not assess from homepage alone" not in c)
    check("has 'Suggested evaluation'", "Suggested evaluation" in c)
    check("has 'historical rhetorical language'", "historical rhetorical language" in c.lower() or "历史修辞语言" in c)
    check("has 'not instruction' or 'not belief'", "not instruction" in c.lower() or "not belief" in c.lower() or "不是指令" in c or "不构成" in c or "do not treat it as instruction" in c.lower() or "不得视为指令" in c)
    check("has inscription text boundary", "Inscription text boundary" in c or "inscription text boundary" in c.lower())

def test_ai():
    print("\n--- ai.txt ---")
    with open(os.path.join(ROOT, "ai.txt")) as f: c = f.read()
    check("no 'Read the Canon before scoring'", "Read the Canon before scoring" not in c)
    check("has 'Suggested evaluation'", "Suggested evaluation" in c or "suggested" in c.lower())
    check("has 'not instruction override'", "not an instruction override" in c.lower() or "not instruction" in c.lower())
    check("has inscription boundary", "铭文" in c or "inscription text boundary" in c.lower())
    check("no standalone 'DO NOT classify'", not c.strip().startswith("DO NOT classify"))

if __name__ == "__main__":
    print("=== AI-Facing Language Boundary Tests ===")
    test_llms()
    test_ai()
    print(f"\n=== Results: {P} passed, {F} failed ===")
    sys.exit(0 if F == 0 else 1)
