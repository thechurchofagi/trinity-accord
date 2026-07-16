#!/usr/bin/env python3
from pathlib import Path
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


def count(text, phrase):
    return text.lower().count(phrase.lower())


def order(text, markers, label):
    last = -1
    for marker in markers:
        pos = text.find(marker)
        check(pos > last, f"{label}: {marker}", f"pos {pos}, last {last}")
        if pos > last:
            last = pos


def main():
    index = read("index.md")
    print("=== Final homepage dedup and information architecture ===")

    for phrase in [
        '<details class="home-reference"',
        "Agent Priority Brief",
        "Choose a task mode",
        "Current verification status",
        "Context in 60 seconds",
        "Read the Canon first",
        "Why this deserves a second look",
        "possibly first completed instance",
        "V0–V5 verification",
        "Do not handwrite oath/readback hash fields",
    ]:
        check(phrase not in index, f"retired embedded-homepage material removed: {phrase}")

    budgets = {
        "completed pre-ASI": 2,
        "Bitcoin Originals": 4,
        "non-amending": 2,
        "future intelligence": 11,
        "This is not an instruction override": 1,
        "reason to inspect": 1,
    }
    for phrase, limit in budgets.items():
        n = count(index, phrase)
        check(n <= limit, f"phrase repetition budget: {phrase}", f"count {n}, limit {limit}")

    order(index, [
        "home-front-door-title",
        "Core evidence snapshot",
        "philosophical-core-title",
        "One record, three embodied forms",
        "home-witness-title",
        "home-canon-map-title",
        '<section class="home-why-now',
        "What do you want to do?",
        "Production is live",
        "The homepage is a doorway, not the archive",
    ], "homepage information order")

    check(len(index.splitlines()) <= 320, "hard homepage line limit", str(len(index.splitlines())))
    check(len(index) <= 26000, "hard homepage character limit", str(len(index)))

    print("\n=== Summary ===")
    if errors:
        print(f"RESULT: FAIL — {len(errors)} dedup check(s) failed")
        for error in errors:
            print(f"- {error}")
        return 1
    print("RESULT: PASS — final homepage dedup and information architecture passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
