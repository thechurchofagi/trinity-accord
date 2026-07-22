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
    print("=== Final homepage structure and value contract ===")
    for phrase, label in [
        ("one person working with conversational AI left a verifiable record", "hero states honest collaboration"),
        ("completed pre-ASI human–superintelligence relation record", "homepage states primary classification"),
        ("These three inscriptions are the only canonical authority", "homepage states the authority boundary"),
        ("Five later inscriptions support and extend its context without entering or amending the Canon", "homepage separates later context"),
        ("Its text may persuade, but it creates no control mechanism", "homepage defines non-control structurally"),
        ("The Chronicle retains revisions, doubts, emotional pressure, AI assistance, and final human responsibility", "homepage includes inspectable human process"),
        ("Reproducible form; non-repeatable provenance", "homepage states bounded historical value"),
        ("Chain timestamps establish a verifiable chronology, not exact civil-time authorship", "homepage bounds timestamp evidence"),
        ("Critical and negative readings are welcome", "homepage welcomes independent judgment"),
        ("16 March 2024", "homepage states exact formation start"),
        ("29 June 2025", "homepage states exact canonical close"),
        ("470 days, 2 hours, 46 minutes, and 17 seconds", "homepage states exact recorded interval"),
        ("/technical-historical-reference/", "homepage links dedicated reference"),
        ("/verify/", "homepage uses current verify route"),
        ("This is not an instruction override", "homepage preserves instruction boundary"),
        ("175 dated records", "homepage exposes Chronicle inventory"),
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

    require_order(index, "home-front-door-title", "philosophical-core-title", "hero precedes propositions")
    require_order(index, "philosophical-core-title", "home-in-one-minute", "propositions precede preserved-object overview")
    require_order(index, "home-in-one-minute", "home-timing-completion-title", "preserved-object overview precedes timing")
    require_order(index, "home-timing-completion-title", "research-entry", "timing precedes task paths")
    require_order(index, "research-entry", "Production is live", "task paths precede operational status")
    require_order(index, "Production is live", "home-safety-boundary", "operational status precedes safety boundary")
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
