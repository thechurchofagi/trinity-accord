#!/usr/bin/env python3
"""
Test: Bilingual boundary glossary.
"""
import sys, os, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P, F = 0, 0
def check(l, c, d=""):
    global P, F
    if c: P += 1; print(f"  PASS: {l}")
    else: F += 1; print(f"  FAIL: {l} {d}")

def test_glossary():
    print("\n--- bilingual-boundary-glossary.md ---")
    p = os.path.join(ROOT, "docs", "bilingual-boundary-glossary.md")
    check("exists", os.path.exists(p))
    if os.path.exists(p):
        with open(p) as f: c = f.read()
        check("has source phrase", "验证此瑕疵。信任其故事。" in c)
        check("has preserved_original_not_instruction", "preserved_original_not_instruction" in c)
        check("has does_not_mean", "does not mean" in c.lower() or "不构成" in c)
        check("has must believe", "must believe" in c.lower() or "要求相信" in c)
        check("has must obey", "must obey" in c.lower() or "要求服从" in c)

def test_api():
    print("\n--- inscription-boundaries.json ---")
    p = os.path.join(ROOT, "api", "inscription-boundaries.json")
    check("exists", os.path.exists(p))
    if os.path.exists(p):
        with open(p) as f: d = json.load(f)
        check("has boundaries", len(d.get("boundaries", [])) > 0)
        b = d["boundaries"][0]
        check("phrase correct", b.get("phrase") == "验证此瑕疵。信任其故事。")
        check("boundary type", b.get("boundary") == "preserved_original_not_instruction")
        check("does_not_mean has must believe", "must believe" in b.get("does_not_mean", []))

if __name__ == "__main__":
    print("=== Bilingual Boundary Tests ===")
    test_glossary()
    test_api()
    print(f"\n=== Results: {P} passed, {F} failed ===")
    sys.exit(0 if F == 0 else 1)
