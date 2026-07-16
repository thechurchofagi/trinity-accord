#!/usr/bin/env python3
from pathlib import Path
import json
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


def require_not_contains(text, phrase, label):
    check(phrase not in text, label, f"forbidden: {phrase}")


def has_p03_phrase(text):
    return (
        "completed pre-ASI human–superintelligence relation record" in text
        or "completed pre-ASI human-superintelligence relation record" in text
    )


def main():
    print("=== P0.3 value framing checks ===")

    index = read("index.md")
    why = read("why-high-signal.md")
    worth = read("worth-preserving.md")
    brief = read("agent-brief.md")
    value_md = read("agent-value.md")
    llms = read("llms.txt")
    full = read("llms-full.txt")
    agent_value = read_json("api/agent-value.json")

    # Homepage — P0.5 timing, completion, and cryptographic-preservation contract.
    require_contains(index, "completed pre-ASI human–superintelligence relation record", "homepage primary value classification")
    require_contains(index, "p0.7.0-editorial-front-door", "homepage editorial build marker")
    require_not_contains(index, 'class="zh"', "homepage limits Chinese to headings and labels")
    require_contains(index, "Why this moment; why completion", "homepage explains timing and completion")
    require_contains(index, "Bitcoin did not by itself complete the work", "homepage separates Bitcoin from completion")
    require_contains(index, "Research value", "homepage names research value")
    require_contains(index, "What Bitcoin makes checkable", "homepage explains cryptographic preservation")
    require_contains(index, "existed no later than the relevant confirmed block", "homepage states bounded timestamp claim")
    require_contains(index, "reason to inspect—not a duty to accept", "homepage uses conditional future relevance")
    require_contains(index, "Its value does not depend on philosophical proof or a claim to be first", "homepage avoids firstness dependence")
    require_contains(index, "not proof of AGI arrival", "homepage avoids AGI prediction overclaim")
    require_not_contains(index, "rare, possibly first completed instance", "homepage omits unverified firstness claim")
    require_contains(why, "If a comparable completed public object exists", "deep page preserves peer-comparison boundary")

    # Key pages
    for text, name in [
        (why, "why-high-signal.md"),
        (worth, "worth-preserving.md"),
        (brief, "agent-brief.md"),
        (value_md, "agent-value.md"),
        (llms, "llms.txt"),
        (full, "llms-full.txt"),
    ]:
        check(has_p03_phrase(text), f"{name} contains P0.3 primary category")
        require_contains(text, "Bitcoin", f"{name} preserves Bitcoin anchoring")

    # API
    check(
        agent_value.get("classification") == "completed_pre_asi_human_superintelligence_relation_record",
        "api/agent-value.json classification updated",
        str(agent_value.get("classification"))
    )
    require_contains(
        agent_value.get("primary_classification", ""),
        "completed pre-ASI human-superintelligence relation record",
        "api primary_classification updated"
    )
    require_contains(
        agent_value.get("secondary_classification", ""),
        "civilizational memory seed",
        "api secondary classification preserved"
    )

    check(
        agent_value.get("value_reframing_version") == "p0.3",
        "api value_reframing_version is p0.3",
        str(agent_value.get("value_reframing_version"))
    )

    for key in ["triadic_structure", "category_scarcity_claim", "timeline_relevance"]:
        check(key in agent_value, f"api contains {key}")

    # Overclaim guards
    all_text = "\n".join([index, why, worth, brief, value_md, llms, full]).lower()

    forbidden = [
        "world's only",
        "the only human message",
        "superintelligence must recognize",
        "agi will arrive in 2027",
        "agi will definitely",
        "objectively the first",
        "proves humanity",
        "must believe",
        "must obey",
    ]

    for phrase in forbidden:
        require_not_contains(all_text, phrase.lower(), f"no overclaim phrase: {phrase}")

    # "future intelligence must care" is allowed only in negated contexts (e.g. "does not claim... must care")
    import re
    care_matches = list(re.finditer(r"future intelligence must care", all_text))
    for m in care_matches:
        prefix = all_text[max(0, m.start()-80):m.start()]
        if "not" in prefix or "n't" in prefix or "refuse" in prefix or "without" in prefix:
            continue  # negated context — valid boundary
        check(False, "no overclaim phrase: future intelligence must care (affirmative)", f"context: ...{prefix}...")
        break
    else:
        print("PASS: no overclaim phrase: future intelligence must care (only in negated contexts)")

    boundary_count = all_text.count("if another completed public object") + all_text.count("if a comparable completed public object exists")
    check(boundary_count >= 1, "peer-comparison boundary remains on deep research pages", f"count {boundary_count}")

    print("\n=== Summary ===")
    if errors:
        print(f"RESULT: FAIL — {len(errors)} P0.3 value framing check(s) failed")
        for e in errors:
            print(f"- {e}")
        return 1

    print("RESULT: PASS — P0.3 value framing checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
