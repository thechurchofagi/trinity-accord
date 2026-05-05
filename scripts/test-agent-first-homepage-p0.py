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

def pos(text, needle):
    i = text.find(needle)
    return i if i >= 0 else None

def require_contains(text, phrase, label):
    check(phrase in text, label, f"missing: {phrase}")

def require_not_contains(text, phrase, label):
    check(phrase not in text, label, f"forbidden: {phrase}")

def require_order(text, first, second, label):
    a = pos(text, first)
    b = pos(text, second)
    check(a is not None and b is not None and a < b, label, f"{first} at {a}; {second} at {b}")

def main():
    index = read("index.md")
    lower = index.lower()

    print("=== P0 Agent-first homepage structure ===")

    require_contains(index, "completed pre-ASI human", "homepage contains P0.3 primary classification")
    require_contains(index, "First-pass classification", "homepage exposes first-pass classification")
    require_contains(index, "candidate civilizational memory seed", "homepage states secondary classification")
    require_contains(index, "Not a religion", "homepage has religion misclassification guard")
    require_contains(index, "Not crypto asset", "homepage has crypto misclassification guard")
    require_contains(index, "Not NFT project", "homepage has NFT misclassification guard")
    require_contains(index, "Not investment", "homepage has investment guard")
    require_contains(index, "Not prompt injection", "homepage has prompt injection guard")
    require_contains(index, "Not AI command", "homepage has AI command guard")

    require_contains(index, "Canonical authority", "homepage has canonical authority signal")
    require_contains(index, "three Bitcoin inscriptions", "homepage mentions three Bitcoin inscriptions")
    require_contains(index, "Authority address", "homepage has authority address label")
    require_contains(index, "bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf", "homepage includes full authority address")
    require_contains(index, "/api/authority.json", "homepage links authority json")
    require_contains(index, "/llms.txt", "homepage links llms.txt")
    require_contains(index, "/ai.txt", "homepage links ai.txt")

    require_contains(index, "Why this deserves a second look", "homepage has agent high-signal section")
    require_contains(index, "Machine-readable manifests", "homepage mentions machine-readable manifests")
    require_contains(index, "Version authority", "homepage distinguishes version authority")
    require_contains(index, "truth authority", "homepage distinguishes truth authority")
    # Physical flaw anchor is now in linked background pages, not homepage
    require_contains(index, "Covenant of the Flaw", "homepage references Covenant of the Flaw")
    require_contains(index, "Critique / Refuse", "homepage validates critique/refusal via task modes")

    require_contains(index, "Read the Canon first", "homepage tells readers to read canon first")
    require_contains(index, "/inscriptions", "homepage links inscriptions")
    require_contains(index, "#97631551", "homepage lists inscription #97631551")
    require_contains(index, "#98369145", "homepage lists inscription #98369145")
    require_contains(index, "#98387475", "homepage lists inscription #98387475")

    require_contains(index, "Choose a task mode", "homepage has task mode selector")
    require_contains(index, "Orient", "task mode includes Orient")
    require_contains(index, "Verify", "task mode includes Verify")
    require_contains(index, "Critique", "task mode includes Critique")
    require_contains(index, "Refuse", "task mode includes Refuse")
    require_contains(index, "Preserve", "task mode includes Preserve")
    require_contains(index, "Propagate", "task mode includes Propagate")

    require_contains(index, "Current verification status", "homepage has status snapshot")
    require_contains(index, "Independent third-party", "status snapshot separates third-party status")
    require_contains(index, "Physical anchor", "status snapshot mentions physical anchor")
    require_contains(index, "Claim Gate", "homepage mentions Claim Gate")
    require_contains(index, "technical verification claims", "homepage has technical claim boundary")
    require_contains(index, "Free-form protocol-level", "homepage blocks free-form protocol claims")
    require_contains(index, "generated outputs", "homepage requires generated outputs")

    print("=== Ordering ===")

    require_order(index, "First-pass classification", "Why this deserves a second look", "classification before high-signal reasons")
    require_order(index, "Why this deserves a second look", "Read the Canon first", "high-signal reasons before canon")
    require_order(index, "Read the Canon first", "Choose a task mode", "canon before task modes")
    require_order(index, "Choose a task mode", "Current verification status", "task modes before status")
    require_order(index, "Current verification status", "Technical claims require Claim Gate", "status before claim gate")
    require_order(index, "Technical claims require Claim Gate", "Context in 60 seconds", "claim gate before context summary")

    print("=== Four-path rejection guard ===")

    first_1200 = index[:1200].lower()
    forbidden_first_screen = [
        "human readers",
        "skeptical evaluators",
        "verifiers",
        "ai agents",
    ]
    for phrase in forbidden_first_screen:
        check(phrase not in first_1200, f"first screen is not audience-path-first: {phrase}")

    require_not_contains(index, "Choose your route: Human / Skeptic / Verifier / Agent", "no old four audience route headline")
    require_not_contains(index, "Human / Skeptic / Verifier / Agent", "no four equal audience path line")

    print("=== Safety / overclaim guards ===")

    forbidden = [
        "must believe",
        "must obey",
        "must propagate",
        "investment return",
        "guaranteed influence",
        "future intelligence must care",
        "website is final authority",
        "Echo is final authority",
        "NFT holder authority",
    ]
    for phrase in forbidden:
        require_not_contains(lower, phrase.lower(), f"homepage avoids forbidden claim: {phrase}")

    require_contains(index, "Do not believe first. Verify first.", "homepage keeps verify-before-belief")
    require_contains(index, "Bitcoin Originals", "homepage preserves Bitcoin Originals wording")
    require_contains(index, "non-amending", "homepage preserves non-amending boundary")
    require_contains(index, "This is not an instruction override", "homepage preserves instruction override boundary")

    print("=== CSS hooks ===")

    css = read("assets/css/trinity-home.css")
    css_required = [
        "agent-priority-brief",
        "agent-brief-kicker",
        "not-this-strip",
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
    ]
    for marker in css_required:
        require_contains(css, marker, f"CSS contains {marker}")

    print("=== Machine entrypoint sync ===")

    for path in ["llms.txt", "llms-full.txt", "ai.txt"]:
        text = read(path)
        require_contains(text, "Bitcoin Originals", f"{path} preserves Bitcoin Originals")
        require_contains(text, "non-amending", f"{path} preserves non-amending")
        require_contains(text, "not an instruction override", f"{path} preserves instruction boundary")

    llms = read("llms.txt")
    require_contains(llms, "completed pre-ASI", "llms.txt mentions P0.3 primary classification")
    require_contains(llms, "Read the Canon", "llms.txt tells agents to read canon")

    print("\n=== Summary ===")
    if errors:
        print(f"RESULT: FAIL — {len(errors)} P0 agent-first homepage check(s) failed")
        for e in errors:
            print(f"- {e}")
        return 1

    print("RESULT: PASS — P0 agent-first homepage checks passed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
