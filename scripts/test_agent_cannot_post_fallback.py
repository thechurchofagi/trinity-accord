#!/usr/bin/env python3
"""
Cannot POST Fallback Guidance Test.
Asserts all V0-V5-facing entries contain equivalent fallback:
  cannot POST -> output payload.json and stop
  do not claim submitted
  do not request PAT
  do not ask human to create Issue

Usage:
    python3 scripts/test_agent_cannot_post_fallback.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PASS_COUNT = 0
FAIL_COUNT = 0
TOTAL = 0


def check(condition, label):
    global PASS_COUNT, FAIL_COUNT, TOTAL
    TOTAL += 1
    if condition:
        PASS_COUNT += 1
        print(f"  PASS: {label}")
    else:
        FAIL_COUNT += 1
        print(f"  FAIL: {label}")


def read_file(relpath):
    p = ROOT / relpath
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8")


print("=== Cannot POST Fallback Guidance Test ===\n")

# Check markdown files for cannot-POST fallback
md_files = {
    "agent-submit.md": "agent-submit.md",
    "external-agent-quickstart.md": "external-agent-quickstart.md",
}

for label, fpath in md_files.items():
    content = read_file(fpath)
    if not content:
        check(False, f"{label} exists")
        continue

    t = content.lower()

    has_cannot = "cannot post" in t or "cannot make http" in t or "cannot run" in t or "if you cannot" in t
    check(has_cannot, f"{label} mentions cannot-POST scenario")

    has_payload_stop = ("payload.json" in t and "stop" in t) or ("生成" in t and "停止" in t)
    check(has_payload_stop, f"{label} says output payload.json and stop")

    # Strip markdown bold/italic markers for matching
    t_plain = re.sub(r'\*+', '', t)
    has_no_claim = "not claim submitted" in t_plain or "do not claim submitted" in t_plain or "不得声称已提交" in t_plain or "must not claim submitted" in t_plain or "not claim the submission is complete" in t_plain or "do not claim the submission" in t_plain
    check(has_no_claim, f"{label} says do not claim submitted/completed")

    has_no_pat = "do not ask" in t and "pat" in t
    check(has_no_pat, f"{label} says do not ask for GitHub PAT")

    has_no_issue = ("do not ask" in t or "must not ask" in t) and ("create" in t or "创建" in t) and ("issue" in t or "Issue" in t)
    check(has_no_issue, f"{label} says do not ask human to create Issue")


# Check JSON files for if_agent_cannot_post / if_cannot_post
print("\n--- JSON fallback checks ---")

json_files = {
    "api/agent-submit-gateway.json": lambda d: d.get("v0_v5_archive_submission", {}),
    "api/agent-submission-guide.json": lambda d: d.get("v0_v5_agent_declared_rules", {}),
}

for fpath, extractor in json_files.items():
    content = read_file(fpath)
    if not content:
        check(False, f"{fpath} exists")
        continue
    try:
        data = json.loads(content)
        section = extractor(data)
        has_fallback = "if_agent_cannot_post" in section or "if_cannot_post" in section
        check(has_fallback, f"{fpath} has cannot-POST fallback field")
        fallback_text = section.get("if_agent_cannot_post", section.get("if_cannot_post", ""))
        if fallback_text:
            t = fallback_text.lower()
            check("stop" in t, f"{fpath} fallback says 'stop'")
            check("payload" in t, f"{fpath} fallback mentions payload")
            check("pat" not in t or "do not" in t or "not" in t,
                  f"{fpath} fallback does not positively request PAT")
    except json.JSONDecodeError:
        check(False, f"{fpath} is valid JSON")

# Check agent-first-contact.json
fc_content = read_file("api/agent-first-contact.json")
if fc_content:
    try:
        data = json.loads(fc_content)
        choices = data.get("choose_one", [])
        v0v5 = None
        for c in choices:
            if c.get("intent") == "verify_v0_v5_agent_declared":
                v0v5 = c
                break
        if v0v5:
            st = v0v5.get("submission_transport", {})
            has_fallback = "if_agent_cannot_post" in st
            check(has_fallback, "agent-first-contact.json submission_transport has cannot-POST fallback")
        else:
            check(False, "agent-first-contact.json has verify_v0_v5 route")
    except json.JSONDecodeError:
        check(False, "agent-first-contact.json is valid JSON")


print(f"\n=== Results: {PASS_COUNT}/{TOTAL} passed ===")
if FAIL_COUNT > 0:
    print(f"FAILED: {FAIL_COUNT} checks failed")
    sys.exit(1)
else:
    print("AGENT_CANNOT_POST_FALLBACK_OK")
    sys.exit(0)
