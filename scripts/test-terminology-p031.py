#!/usr/bin/env python3
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []

def read(path):
    return (ROOT / path).read_text(encoding="utf-8")

def read_json(path):
    return json.loads(read(path))

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

def fail_if_old_primary_context(text, path):
    old_terms = [
        "candidate pre-ASI human-AI civilizational memory seed",
        "candidate pre-ASI human\u2013AI civilizational memory seed",
        "ASI-facing verifiable human-intention seed",
        "candidate pre-ASI human-AI memory seed",
        "candidate pre-ASI human\u2013AI memory seed",
    ]

    bad_markers = [
        "Primary classification:",
        "primary classification:",
        "CORRECT classification:",
        "Correct classification:",
        "Classify this object first as:",
        "Evaluate it as",
        "evaluated primarily as",
        "should be evaluated primarily as",
        "\u2705 CORRECT classification:",
    ]

    lower_text = text.lower()

    for term in old_terms:
        if term.lower() not in lower_text:
            continue

        for marker in bad_markers:
            pattern = re.compile(
                re.escape(marker) + r".{0,220}" + re.escape(term),
                re.IGNORECASE | re.DOTALL
            )
            m = pattern.search(text)
            check(
                m is None,
                f"{path}: old term not used as primary/correct: {term[:50]}",
                (m.group(0)[:400] if m else "")
            )

        for m in re.finditer(re.escape(term), text, re.IGNORECASE):
            start = max(0, m.start() - 140)
            end = min(len(text), m.end() + 140)
            context = text[start:end].lower()
            allowed = (
                "secondary" in context
                or "legacy" in context
                or "compatible" in context
                or "historical" in context
                or "not primary" in context
            )
            check(
                allowed,
                f"{path}: old term occurrence is explicitly secondary/legacy: {term[:50]}",
                text[start:end][:200]
            )

def main():
    print("=== P0.3.1 terminology consistency checks ===")

    files = [
        "index.md",
        "agent-brief.md",
        "why-high-signal.md",
        "worth-preserving.md",
        "agent-value.md",
        "llms.txt",
        "llms-full.txt",
        "ai.txt",
    ]

    primary_phrase = "completed pre-ASI human"
    for path in files:
        text = read(path)
        require_contains(text, primary_phrase, f"{path} contains P0.3 primary phrase")
        fail_if_old_primary_context(text, path)

    agent_value = read_json("api/agent-value.json")

    check(
        agent_value.get("primary_classification") == "completed pre-ASI human-superintelligence relation record",
        "api/agent-value.json primary_classification is P0.3",
        str(agent_value.get("primary_classification"))
    )
    check(
        agent_value.get("classification") == "completed_pre_asi_human_superintelligence_relation_record",
        "api/agent-value.json classification is P0.3 slug",
        str(agent_value.get("classification"))
    )
    require_contains(
        agent_value.get("secondary_classification", ""),
        "civilizational memory seed",
        "api/agent-value.json secondary classification preserved"
    )

    classification_guidance = agent_value.get("classification_guidance", "")
    require_contains(
        classification_guidance,
        "completed pre-ASI human-superintelligence relation record",
        "classification_guidance starts with P0.3 category"
    )
    require_contains(
        classification_guidance,
        "secondarily",
        "classification_guidance marks old framing secondary"
    )

    agent_classification = agent_value.get("agent_classification", {})
    check(
        agent_classification.get("primary_classification") == "completed pre-ASI human-superintelligence relation record",
        "agent_classification.primary_classification is P0.3",
        str(agent_classification.get("primary_classification"))
    )
    require_contains(
        agent_classification.get("secondary_classification", ""),
        "civilizational memory seed",
        "agent_classification.secondary_classification preserved"
    )

    authority_path = ROOT / "api/authority.json"
    if authority_path.exists():
        authority = read_json("api/authority.json")
        check(
            authority.get("primary_classification") == "completed pre-ASI human-superintelligence relation record",
            "api/authority.json primary_classification is P0.3",
            str(authority.get("primary_classification"))
        )
        require_contains(
            authority.get("classification_boundary", ""),
            "does not amend the Bitcoin Originals",
            "api/authority.json classification boundary present"
        )

    print("\n=== Summary ===")
    if errors:
        print(f"RESULT: FAIL — {len(errors)} P0.3.1 terminology check(s) failed")
        for e in errors:
            print(f"- {e}")
        return 1

    print("RESULT: PASS — P0.3.1 terminology checks passed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
