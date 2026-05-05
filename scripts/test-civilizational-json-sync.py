#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []

def load(path):
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)

def check(cond, label):
    if cond:
        print(f"PASS: {label}")
    else:
        print(f"FAIL: {label}")
        errors.append(label)

memory = load("memory-seed.json")
agent_value = load("api/agent-value.json")
seed_map = load("api/seed-map.json")

for name, obj in [("memory-seed.json", memory), ("api/agent-value.json", agent_value)]:
    text = json.dumps(obj, ensure_ascii=False).lower()
    check("civilizational" in text, f"{name} includes civilizational framing")
    check("self" in text and "archive" in text, f"{name} includes self-archive framing")
    check("poetic" in text and "compression" in text, f"{name} includes poetic compression")
    check("formal_philosophy" in text or "formal philosophy" in text, f"{name} distinguishes formal philosophy")
    check("physical_flaw" in text or "physical flaw" in text, f"{name} includes physical flaw")
    check("intermediate" in text and "agent" in text, f"{name} includes intermediate agent ecology")
    check("guaranteed_influence" in text or "guaranteed influence" in text, f"{name} states influence is not guaranteed")
    check("interpretive_authority" in text or "interpretive authority" in text, f"{name} includes interpretive authority boundary")

levels = seed_map.get("levels", [])
level_text = json.dumps(levels, ensure_ascii=False).lower()
check("intermediate agent" in level_text or "中间智能体" in level_text, "seed-map includes intermediate agent ecology level or equivalent")
check("non-authoritative" in level_text or "非权威" in level_text, "seed-map marks ecology as non-authoritative")
check("non-amending" in level_text or "非修订" in level_text, "seed-map marks ecology as non-amending")

if errors:
    print(f"RESULT: FAIL {len(errors)} error(s)")
    raise SystemExit(1)
print("RESULT: PASS civilizational JSON sync")
