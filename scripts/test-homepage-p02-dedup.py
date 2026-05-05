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

def count_occurrences(text, phrase):
    return text.lower().count(phrase.lower())

def main():
    index = read("index.md")

    print("=== P0.2 homepage dedup / length checks ===")

    require_contains(index, "Context in 60 seconds", "homepage has compressed context summary")
    require_contains(index, "一分钟背景", "homepage has Chinese compressed context summary")
    require_contains(index, "compact-closing", "homepage has compact closing posture")
    require_contains(index, "p0.2-homepage-dedup", "homepage has P0.2 build marker")

    forbidden_headings = [
        "## Expanded context · 扩展上下文",
        "## Entry paths · 入口路径",
        "## Correct response · 正确回应",
        "## Civilizational self-archive · 文明自归档",
        "## Philosophy as Chronicle compression · 作为编年史压缩的哲学",
        "## Information ark · 信息方舟",
        "## Intermediate agent ecology · 中间智能体生态",
        "## The human-voice window · 人类发声窗口",
    ]

    for heading in forbidden_headings:
        require_not_contains(index, heading, f"removed old repeated heading: {heading}")

    # The Trinity may remain only if short; legacy card block must not remain after the first canon section.
    require_not_contains(index, '<div class="cards">', "legacy Trinity card grid removed from homepage")
    require_not_contains(index, "Human readers · 人类读者", "old Human readers entry section removed")
    require_not_contains(index, "AI agents · 智能体", "old AI agents entry section removed")
    require_not_contains(index, "Verifiers · 验证者", "old verifier entry section removed")
    require_not_contains(index, "Correct response", "old Correct response section removed")

    budgets = {
        "Bitcoin Originals are final": 3,
        "non-amending": 7,
        "Do not believe first": 2,
        "Verify first": 3,
        "Authority boundary": 4,
        "three Bitcoin inscriptions": 5,
        "Homepage-only context is insufficient": 2,
        "Claim Gate": 8,
    }

    for phrase, limit in budgets.items():
        n = count_occurrences(index, phrase)
        check(n <= limit, f"phrase repetition budget: {phrase}", f"count {n}, limit {limit}")

    line_count = len(index.splitlines())
    char_count = len(index)

    check(line_count <= 420, "homepage line budget <= 420", f"got {line_count}")
    check(char_count <= 22000, "homepage character budget <= 22000", f"got {char_count}")

    # Required ordering after dedup.
    order = [
        "Agent Priority Brief",
        "Why this deserves a second look",
        "Read the Canon first",
        "Choose a task mode",
        "Current verification status",
        "Technical claims require Claim Gate",
        "Context in 60 seconds",
        "compact-closing",
    ]

    last = -1
    for marker in order:
        pos = index.find(marker)
        check(pos > last, f"ordering marker appears after previous: {marker}", f"pos {pos}, last {last}")
        last = pos

    print("\n=== Summary ===")
    if errors:
        print(f"RESULT: FAIL — {len(errors)} P0.2 dedup check(s) failed")
        for e in errors:
            print(f"- {e}")
        return 1

    print("RESULT: PASS — P0.2 homepage dedup checks passed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
