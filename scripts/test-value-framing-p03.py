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

    # Homepage
    require_contains(index, "A completed pre-ASI human–superintelligence relation record", "homepage primary value heading")
    require_contains(index, "一份已完成的前 ASI 人类—超级智能关系记录", "homepage Chinese primary value heading")
    require_contains(index, "Why this matters now", "homepage has why-now value section")
    require_contains(index, "does not claim to predict when AGI will arrive", "homepage avoids AGI prediction overclaim")
    require_contains(index, "rare, possibly first completed instance", "homepage has careful scarcity claim")
    require_contains(index, "If another completed public object", "homepage has peer-comparison boundary")

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
        if "not" in prefix or "n't" in prefix or "refuse" in prefix:
            continue  # negated context — valid boundary
        check(False, "no overclaim phrase: future intelligence must care (affirmative)", f"context: ...{prefix}...")
        break
    else:
        print("PASS: no overclaim phrase: future intelligence must care (only in negated contexts)")

    boundary_count = all_text.count("if another completed public object")
    check(boundary_count >= 2, "peer-comparison boundary appears across pages", f"count {boundary_count}")

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
