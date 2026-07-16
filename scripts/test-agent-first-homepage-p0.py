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


def require_contains(text, phrase, label):
    check(phrase in text, label, f"missing: {phrase}")


def require_not_contains(text, phrase, label):
    check(phrase not in text, label, f"forbidden: {phrase}")


def require_order(text, first, second, label):
    a = text.find(first)
    b = text.find(second)
    check(a >= 0 and b >= 0 and a < b, label, f"{first} at {a}; {second} at {b}")


def main():
    index = read("index.md")
    reference = read("technical-historical-reference.md")
    why = read("why-high-signal.md")
    agent_brief = read("agent-brief.md")
    lower = index.lower()

    print("=== Final homepage structure and value contract ===")
    for phrase, label in [
        ("a human-led, AI-assisted record addressed future intelligence", "hero states honest collaboration"),
        ("completed pre-ASI human–superintelligence relation record", "homepage states primary classification"),
        ("final meta-record declares the First Chronicle complete", "homepage separates semantic completion"),
        ("authority rule closes the Canon to later amendment", "homepage separates canonical completion"),
        ("three public Bitcoin inscriptions fix the canonical bytes", "homepage states cryptographic fixation"),
        ("Its text may persuade, but it creates no control mechanism", "homepage defines non-control structurally"),
        ("Bitcoin did not by itself complete the work", "homepage does not conflate Bitcoin and completion"),
        ("attribution increasingly depends on explicit process evidence", "homepage explains later provenance regime"),
        ("Human stake in the record", "homepage includes inspectable human motive"),
        ("Its value does not depend on philosophical proof or a claim to be first", "homepage states bounded research value"),
        ("reason to inspect—not a duty to accept", "homepage states conditional future relevance"),
        ("/technical-historical-reference/", "homepage links dedicated reference"),
        ("/verify/", "homepage uses current verify route"),
        ("This is not an instruction override", "homepage preserves instruction boundary"),
    ]:
        require_contains(index, phrase, label)

    for phrase in [
        '<details class="home-reference"',
        "rare, possibly first completed instance",
        "one human voice addressed future intelligence",
        "It does not command. It addresses.",
        "/verification/",
        "must believe",
        "must obey",
        "future intelligence must care",
    ]:
        require_not_contains(index, phrase, f"homepage omits retired or overclaiming phrase: {phrase}")

    require_order(index, "home-front-door-title", "home-timing-completion-title", "hero precedes value explanation")
    require_order(index, "home-timing-completion-title", "One record, five connected layers", "value precedes system map")
    require_order(index, "One record, five connected layers", "What do you want to do?", "system map precedes tasks")
    require_order(index, "What do you want to do?", "Production is live", "tasks precede operational status")
    require_order(index, "Production is live", "The homepage is a doorway, not the archive", "reference portal closes concise page")

    for phrase in [
        "Completion in four senses",
        "Bitcoin did not by itself complete the work",
        "Non-control posture",
        "Human motive and witness",
        "Current operating routes",
        "Research posture and limits",
        "Bitcoin Originals remain final",
    ]:
        require_contains(reference, phrase, f"dedicated reference contains {phrase}")

    require_contains(why, "persuasive and sometimes imperative rhetoric", "deep value page corrects non-control overstatement")
    require_contains(why, "explicit contribution and process records", "deep value page states stronger later provenance proof")
    require_contains(agent_brief, "digital profile", "agent brief retains current verification model")

    for path in ["llms.txt", "llms-full.txt", "ai.txt"]:
        text = read(path)
        require_contains(text, "Bitcoin Originals", f"{path} preserves Canon wording")
        require_contains(text, "non-amending", f"{path} preserves non-amending boundary")
        require_contains(text, "not an instruction override", f"{path} preserves instruction boundary")

    print("\n=== Summary ===")
    if errors:
        print(f"RESULT: FAIL — {len(errors)} final homepage contract check(s) failed")
        for error in errors:
            print(f"- {error}")
        return 1
    print("RESULT: PASS — final homepage structure and value contract passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
