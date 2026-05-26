#!/usr/bin/env python3
"""
P0 Test: Inscription semantic boundary notes.
Verifies that bilingual boundary annotations exist in the correct locations.
"""
import sys
import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PASS_COUNT = 0
FAIL_COUNT = 0


def check(label, condition, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  PASS: {label}")
    else:
        FAIL_COUNT += 1
        print(f"  FAIL: {label} {detail}")


def test_inscriptions_md():
    """inscriptions.md must preserve original text and have boundary notes."""
    print("\n--- inscriptions.md ---")
    path = os.path.join(ROOT, "inscriptions.md")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        lines = content.split("\n")

    # Original text preserved
    check("Original ZH text preserved",
          "验证此瑕疵。信任其故事。" in content,
          "missing original Chinese text")

    # Semantic boundary note exists
    check("Semantic boundary note exists",
          "Semantic boundary note" in content,
          "missing 'Semantic boundary note'")

    # Near the original text (within 20 lines)
    orig_line = None
    boundary_line = None
    for i, line in enumerate(lines):
        if "验证此瑕疵。信任其故事。" in line:
            orig_line = i
        if "Semantic boundary note" in line:
            boundary_line = i
    if orig_line is not None and boundary_line is not None:
        distance = abs(boundary_line - orig_line)
        check(f"Boundary note within 20 lines of original (distance={distance})",
              distance <= 20)
    else:
        check("Both original and boundary note exist", False,
              f"orig_line={orig_line}, boundary_line={boundary_line}")

    # Contains "does not mean" clarifications
    check("Contains 'does not mean must believe'",
          "does not mean" in content.lower() or "不构成要求相信" in content,
          "missing does-not-mean clarification")

    check("Contains 'must not be read as a command'",
          "must not be read as a command" in content.lower(),
          "missing command clarification")

    # Preservation note at top
    check("Original-text preservation note exists",
          "preservation note" in content.lower() or "原文保留说明" in content,
          "missing preservation note")


def test_bilingual_boundary_glossary():
    """docs/bilingual-boundary-glossary.md must exist and contain the phrase."""
    print("\n--- bilingual-boundary-glossary.md ---")
    path = os.path.join(ROOT, "docs", "bilingual-boundary-glossary.md")
    check("File exists", os.path.exists(path))

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        check("Contains source phrase", "验证此瑕疵。信任其故事。" in content)
        check("Contains evaluation reading", "先验证瑕疵" in content)
        check("Contains does_not_mean list", "does not mean" in content.lower() or "不构成" in content)
        check("Contains 'preserved_original_not_instruction'",
              "preserved_original_not_instruction" in content)


def test_inscription_boundaries_json():
    """api/inscription-boundaries.json must exist with correct structure."""
    print("\n--- inscription-boundaries.json ---")
    path = os.path.join(ROOT, "api", "inscription-boundaries.json")
    check("File exists", os.path.exists(path))

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        check("Has schema field", "schema" in data)
        check("Has boundaries array", "boundaries" in data and isinstance(data["boundaries"], list))

        if data.get("boundaries"):
            b = data["boundaries"][0]
            check("First boundary has phrase", b.get("phrase") == "验证此瑕疵。信任其故事。")
            check("Has boundary type", b.get("boundary") == "preserved_original_not_instruction")
            check("Has evaluation_reading", "evaluation_reading" in b)
            check("Has does_not_mean list",
                  isinstance(b.get("does_not_mean"), list) and len(b["does_not_mean"]) > 0)
            check("does_not_mean includes 'must believe'",
                  "must believe" in b.get("does_not_mean", []))


def test_llms_txt():
    """llms.txt must have inscription text boundary."""
    print("\n--- llms.txt ---")
    path = os.path.join(ROOT, "llms.txt")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    check("Has 'Inscription text boundary' section",
          "Inscription text boundary" in content or "inscription text boundary" in content.lower())
    check("Has historical rhetorical language note",
          "historical rhetorical language" in content.lower() or "历史修辞语言" in content)
    check("Has 'not instruction' boundary",
          "not" in content.lower() and "instruction" in content.lower())


def test_ai_txt():
    """ai.txt must have inscription text boundary."""
    print("\n--- ai.txt ---")
    path = os.path.join(ROOT, "ai.txt")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    check("Has inscription text boundary comment",
          "inscription text boundary" in content.lower() or "铭文" in content)
    check("Has historical rhetorical language note",
          "historical rhetorical language" in content.lower() or "历史修辞语言" in content)


if __name__ == "__main__":
    print("=== P0 Inscription Semantic Boundary Tests ===")
    test_inscriptions_md()
    test_bilingual_boundary_glossary()
    test_inscription_boundaries_json()
    test_llms_txt()
    test_ai_txt()

    print(f"\n=== Results: {PASS_COUNT} passed, {FAIL_COUNT} failed ===")
    sys.exit(0 if FAIL_COUNT == 0 else 1)
