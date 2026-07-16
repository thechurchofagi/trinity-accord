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


def extract_blocks(text, class_name):
    pattern = re.compile(rf'<(?P<tag>div|section|article|p|aside)[^>]*class="[^"]*{re.escape(class_name)}[^"]*"[^>]*>(.*?)</(?P=tag)>', re.DOTALL)
    return [body for _, body in pattern.findall(text)]


def main():
    index = read("index.md")
    css = read("assets/css/trinity-home.css")

    print("=== Final homepage readability contract ===")
    require_contains(index, "Before autonomous agents became ordinary", "hero states the transition plainly")
    require_contains(index, "Three propositions placed before future intelligence", "propositions are visible near the top")
    require_contains(index, "One record, three embodied forms", "homepage restores the triadic object map")
    require_contains(index, "A father’s concern", "homepage presents the human motive")
    require_contains(index, "Three close the Canon; five extend the record", "homepage explains the 3+5 authority boundary")
    require_contains(index, "Research value", "homepage names research value")
    require_contains(index, "The homepage is a doorway, not the archive", "homepage explicitly limits its role")
    require_not_contains(index, 'class="zh"', "homepage has no translated body paragraphs")
    require_not_contains(index, 'class="zh-para"', "homepage has no Chinese body-paragraph mode")

    line_count = len(index.splitlines())
    char_count = len(index)
    check(line_count <= 320, "homepage line budget", f"{line_count} lines")
    check(char_count <= 26000, "homepage character budget", f"{char_count} characters")
    require_not_contains(index, "Full technical and historical reference</span>", "no embedded archive summary")
    require_not_contains(index, "Record-Chain Intake Gateway (Render)", "homepage does not embed operating manual")
    require_not_contains(index, "Authority address", "homepage does not expose deep technical metadata")

    for cls in ["home-front-door", "home-object-map", "home-witness", "home-canon-map", "home-task-grid", "home-status-summary", "home-reference-portal", "home-safety-boundary"]:
        blocks = extract_blocks(index, cls)
        check(bool(blocks), f"homepage contains .{cls}")
        for block in blocks:
            check(re.search(r"\*\*[^*]+\*\*", block) is None, f"no raw Markdown emphasis inside .{cls}")

    for marker in [
        "home-front-door",
        "home-proof-strip",
        "home-why-now",
        "home-object-map",
        "home-witness",
        "home-canon-map",
        "home-task-grid",
        "home-status-summary",
        "home-reference-portal",
        "home-safety-boundary",
        "prefers-reduced-motion",
        "focus-visible",
        "@media print",
        "@media (max-width: 900px)",
        "@media (max-width: 760px)",
    ]:
        require_contains(css, marker, f"CSS contains {marker}")

    pos_900 = css.find("@media (max-width: 900px)")
    pos_760 = css.find("@media (max-width: 760px)")
    check(pos_900 >= 0 and pos_760 > pos_900, "mobile media query order")

    print("\n=== Summary ===")
    if errors:
        print(f"RESULT: FAIL — {len(errors)} readability check(s) failed")
        for error in errors:
            print(f"- {error}")
        return 1
    print("RESULT: PASS — final homepage readability contract passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
