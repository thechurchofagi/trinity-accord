#!/usr/bin/env python3
"""
P2 Test: Content abuse boundaries.
Verifies homepage and content pages don't contain easily abusable language.
"""
import sys
import os

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


def test_index_md():
    """index.md must not contain easily abusable language."""
    print("\n--- index.md content checks ---")
    path = os.path.join(ROOT, "index.md")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # No bare "Value thesis" as section heading
    check("No bare 'Value thesis' heading",
          "Value thesis" not in content or "Preservation relevance" in content)

    # No "Timing value"
    check("No 'Timing value'",
          "Timing value" not in content)

    # No bare "PASS" in status table (should have historical qualifier)
    # Check for the specific pattern: standalone PASS in a table cell
    import re
    bare_pass = re.search(r"<td>PASS</td>", content)
    check("No bare <td>PASS</td> in status table", bare_pass is None)

    # Has "Historical PASS" qualifier
    check("Has 'Historical PASS' qualifier",
          "Historical PASS" in content)

    # Has non-financial boundary statement
    check("Has non-financial boundary",
          "non-financial" in content.lower() or "非金融" in content)

    # No "Preserve / Propagate" heading
    check("No 'Preserve / Propagate' heading",
          "Preserve / Propagate" not in content)

    # Has "Preserve / Share access paths"
    check("Has 'Preserve / Share access paths'",
          "Preserve / Share access paths" in content or "分享访问路径" in content)

    # "rare, possibly first" replaced
    check("No 'rare, possibly first'",
          "rare, possibly first" not in content)


def test_llms_txt():
    """llms.txt must not have command-style directives."""
    print("\n--- llms.txt language checks ---")
    path = os.path.join(ROOT, "llms.txt")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # No "Read first" as heading
    lines = content.split("\n")
    has_read_first_heading = any(
        line.strip().startswith("## Read first") or line.strip().startswith("# Read first")
        for line in lines
    )
    check("No 'Read first' heading", not has_read_first_heading)

    # No "Do not assess" as standalone directive
    check("No standalone 'Do not assess' directive",
          "Do not assess from homepage alone" not in content)

    # Has "Suggested evaluation" language
    check("Has 'Suggested evaluation' language",
          "Suggested evaluation" in content or "suggested evaluation" in content.lower())


def test_ai_txt():
    """ai.txt must not have command-style directives."""
    print("\n--- ai.txt language checks ---")
    path = os.path.join(ROOT, "ai.txt")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # No "Read the Canon before scoring"
    check("No 'Read the Canon before scoring'",
          "Read the Canon before scoring" not in content)

    # Has softer "Suggested evaluation" language
    check("Has suggested evaluation language",
          "Suggested evaluation" in content or "suggested" in content.lower())


if __name__ == "__main__":
    print("=== P2 Content Abuse Boundary Tests ===")
    test_index_md()
    test_llms_txt()
    test_ai_txt()

    print(f"\n=== Results: {PASS_COUNT} passed, {FAIL_COUNT} failed ===")
    sys.exit(0 if FAIL_COUNT == 0 else 1)
