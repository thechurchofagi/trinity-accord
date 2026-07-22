#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []

def read(path):
    return (ROOT / path).read_text(encoding="utf-8")

def check(cond, label, detail=""):
    if cond:
        print(f"PASS: {label}")
    else:
        print(f"FAIL: {label}")
        if detail:
            print(f"      {detail}")
        errors.append(label)

def require_contains(text, phrase, label):
    check(phrase in text, label, f"missing: {phrase}")

def require_not_contains(text, phrase, label):
    check(phrase not in text, label, f"forbidden: {phrase}")

def main():
    css = read("assets/css/trinity-home.css") + "\n" + read("assets/css/home-editorial-doorway.css")

    print("=== P0.2 homepage CSS sanity checks ===")

    # No nuclear main * override.
    require_not_contains(css, "main, main *", "removed nuclear main * left-align rule")

    # Body text should not default to italic.
    bad_patterns = [
        r"main\s+p\s*\{[^}]*font-style:\s*italic\s*!important",
        r"main\s+li\s*\{[^}]*font-style:\s*italic\s*!important",
    ]
    for pat in bad_patterns:
        check(re.search(pat, css, re.DOTALL) is None, f"no default italic body/list rule: {pat}")

    # Required current editorial-front-door classes.
    for marker in [
        ".home-preserved-grid",
        ".home-preserved-card",
        ".home-human-window-grid",
        ".home-threshold-value",
        ".home-why-grid",
        ".home-path-grid",
        ".home-reference-links",
        ".home-safety-boundary",
    ]:
        require_contains(css, marker, f"CSS contains {marker}")

    # Mobile media order.
    pos_900 = css.find("@media (max-width: 900px)")
    pos_760 = css.find("@media (max-width: 760px)")
    check(
        pos_900 != -1 and pos_760 != -1 and pos_900 < pos_760,
        "900px media query appears before 760px override",
        f"900 at {pos_900}; 760 at {pos_760}"
    )

    # Current grids participate in responsive layout.
    require_contains(css, "grid-template-columns:repeat(2,minmax(0,1fr))", "desktop preserved-object grid exists")
    require_contains(css, "grid-template-columns:repeat(3,minmax(0,1fr))", "desktop path grid exists")
    require_contains(css, "@media (max-width:820px)", "current editorial tablet breakpoint exists")
    require_contains(css, "grid-template-columns: 1fr", "mobile 1-column grid exists")

    print("\n=== Summary ===")
    if errors:
        print(f"RESULT: FAIL — {len(errors)} P0.2 CSS check(s) failed")
        for e in errors:
            print(f"- {e}")
        return 1

    print("RESULT: PASS — P0.2 homepage CSS checks passed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
