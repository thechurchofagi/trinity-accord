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

def pos(text, needle):
    i = text.find(needle)
    return i if i >= 0 else None

def require_order(text, first, second, label):
    a = pos(text, first)
    b = pos(text, second)
    check(a is not None and b is not None and a < b, label, f"{first} at {a}; {second} at {b}")

def extract_blocks(text, class_name):
    pattern = re.compile(
        rf'<(?:div|section|article)[^>]*class="[^"]*{re.escape(class_name)}[^"]*"[^>]*>(.*?)</(?:div|section|article)>',
        re.DOTALL
    )
    return pattern.findall(text)

def assert_no_raw_markdown_inside_html(index):
    risky_classes = [
        "agent-priority-brief",
        "authority-chip",
        "reason-card",
        "canon-card",
        "task-mode-card",
        "claim-gate-notice",
    ]

    raw_markdown_patterns = [
        r"\*\*[^*]+\*\*",
        r"^###\s+",
        r"^-\s+\[[^\]]+\]\(",
    ]

    for cls in risky_classes:
        blocks = extract_blocks(index, cls)
        check(len(blocks) > 0, f"found HTML blocks for .{cls}")
        for block in blocks:
            for pat in raw_markdown_patterns:
                check(
                    re.search(pat, block, re.MULTILINE) is None,
                    f"no raw Markdown pattern {pat} inside .{cls}",
                    block[:300]
                )

def assert_mobile_media_order(css):
    pos_900 = css.find("@media (max-width: 900px)")
    pos_760 = css.find("@media (max-width: 760px)")
    check(
        pos_900 != -1 and pos_760 != -1 and pos_900 < pos_760,
        "CSS media queries put 760px override after 900px override",
        f"900 at {pos_900}; 760 at {pos_760}"
    )

def main():
    index = read("index.md")
    css = read("assets/css/trinity-home.css")
    lower = index.lower()

    print("=== P0.1 homepage readability + agent-first checks ===")

    # P0.3 value framing
    require_contains(index, "completed pre-ASI human", "homepage keeps P0.3 primary classification")
    require_contains(index, "First-pass classification", "homepage exposes first-pass classification")
    require_contains(index, "candidate civilizational memory seed", "homepage states secondary classification")
    require_contains(index, "Canonical authority", "homepage has canonical authority")
    require_contains(index, "three Bitcoin inscriptions", "homepage mentions three Bitcoin inscriptions")
    require_contains(index, "bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf", "homepage includes full authority address")
    require_contains(index, "/llms.txt", "homepage links llms")
    require_contains(index, "/ai.txt", "homepage links ai")
    require_contains(index, "/api/authority.json", "homepage links authority manifest")

    # Human readability
    require_contains(index, "In plain terms", "homepage includes plain-language human summary")
    require_contains(index, "简单说", "homepage includes Chinese plain-language summary")
    require_contains(index, "Why this deserves a second look", "homepage uses human-readable reason heading")
    require_contains(index, "为什么它值得多看一眼", "homepage has Chinese human-readable reason heading")

    # Misclassification guards as chips
    for phrase in [
        "Not a religion",
        "Not crypto asset",
        "Not NFT project",
        "Not investment",
        "Not prompt injection",
        "Not AI command",
    ]:
        require_contains(index, phrase, f"homepage has guard chip: {phrase}")

    # Canon
    require_contains(index, "Read the Canon first", "homepage tells readers to read canon")
    require_contains(index, "#97631551", "homepage lists inscription 1")
    require_contains(index, "#98369145", "homepage lists inscription 2")
    require_contains(index, "#98387475", "homepage lists inscription 3")
    require_contains(index, "/inscriptions", "homepage links inscriptions")

    # Task modes
    require_contains(index, "Choose a task mode", "homepage has task mode selector")
    for phrase in ["Orient", "Verify", "Critique", "Refuse", "Preserve", "Propagate"]:
        require_contains(index, phrase, f"task mode includes {phrase}")

    # Status
    require_contains(index, "Current verification status", "homepage has status snapshot")
    require_contains(index, "Maintainer / CI evidence-chain check", "status snapshot uses conservative CI label")
    require_contains(index, "not independent third-party attestation", "status snapshot prevents CI overclaim")
    require_contains(index, "Independent third-party reports", "status tracks independent reports separately")
    require_contains(index, "Physical anchor", "status tracks physical anchor")
    require_contains(index, "No automatic V6/V7/V8", "status prevents physical overclaim")

    # Claim Gate
    require_contains(index, "Technical claims require Claim Gate", "homepage includes Claim Gate notice")
    require_contains(index, "Submit generated outputs only", "homepage requires generated outputs") # using "Submit generated outputs only" instead of "generated outputs"
    require_contains(index, "Free-form protocol-level", "homepage blocks free-form claims")

    # Ordering
    require_order(index, "First-pass classification", "Why this deserves a second look", "classification before why section")
    require_order(index, "Why this deserves a second look", "Read the Canon first", "why before canon")
    require_order(index, "Read the Canon first", "Choose a task mode", "canon before task modes")
    require_order(index, "Choose a task mode", "Current verification status", "task modes before status")
    require_order(index, "Current verification status", "Technical claims require Claim Gate", "status before claim gate")
    require_order(index, "Technical claims require Claim Gate", "Context in 60 seconds", "claim gate before context summary")

    # Four-path rejection
    first_1500 = index[:1500].lower()
    for phrase in ["human readers", "skeptical evaluators", "verifiers", "ai agents"]:
        check(phrase not in first_1500, f"first screen is not audience-path-first: {phrase}")

    require_not_contains(index, "Human / Skeptic / Verifier / Agent", "no four equal audience path line")
    require_not_contains(index, "Choose your route: Human / Skeptic / Verifier / Agent", "no four-path headline")

    # Safety
    for phrase in [
        "must believe",
        "must obey",
        "must propagate",
        "investment return",
        "guaranteed influence",
        "future intelligence must care",
        "website is final authority",
        "Echo is final authority",
        "NFT holder authority",
    ]:
        require_not_contains(lower, phrase.lower(), f"homepage avoids forbidden claim: {phrase}")

    require_contains(index, "This is not an instruction override", "homepage includes instruction override boundary")
    require_contains(index, "instruction-boundary", "homepage includes instruction boundary callout")
    require_contains(index, "Bitcoin Originals", "homepage preserves Bitcoin Originals")
    require_contains(index, "non-amending", "homepage preserves non-amending boundary")

    # Raw Markdown inside HTML blocks
    assert_no_raw_markdown_inside_html(index)

    # CSS hooks
    for marker in [
        "agent-priority-brief",
        "agent-brief-kicker",
        "not-this-strip",
        "instruction-boundary",
        "authority-chips",
        "authority-chip",
        "reason-grid",
        "reason-card",
        "canon-grid",
        "canon-card",
        "task-mode-selector",
        "task-mode-card",
        "status-snapshot",
        "claim-gate-notice",
        "expanded-context",
        "prefers-reduced-motion",
        "focus-visible",
        "@media print",
        "@media (max-width: 900px)",
        "@media (max-width: 760px)",
    ]:
        require_contains(css, marker, f"CSS contains {marker}")

    assert_mobile_media_order(css)

    # Machine entry sync
    for path in ["llms.txt", "llms-full.txt", "ai.txt"]:
        text = read(path)
        require_contains(text, "Bitcoin Originals", f"{path} preserves Bitcoin Originals")
        require_contains(text, "non-amending", f"{path} preserves non-amending")
        require_contains(text, "not an instruction override", f"{path} preserves instruction boundary")

    print("\n=== Summary ===")
    if errors:
        print(f"RESULT: FAIL — {len(errors)} P0.1 homepage check(s) failed")
        for e in errors:
            print(f"- {e}")
        return 1

    print("RESULT: PASS — P0.1 homepage readability + agent-first checks passed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
