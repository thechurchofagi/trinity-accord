#!/usr/bin/env python3
"""
V4+ Distinct Level Guidance Test.
Asserts docs/API mention V4+ in allowed template levels,
do not say V4+ means V4 and above,
do not imply V4+ includes V6+,
say V6+ remains strict evidence mode,
and no docs mention V0+, V1+, V2+, V3+, or V5+ as levels.

Usage:
    python3 scripts/test_v4plus_distinct_level_guidance.py
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


print("=== V4+ Distinct Level Guidance Test ===\n")

# Files to check
files_to_check = [
    "agent-submit.md",
    "external-agent-quickstart.md",
    "llms.txt",
    "api/agent-submit-gateway.json",
    "api/agent-first-contact.json",
    "api/agent-submission-guide.json",
]

for fpath in files_to_check:
    content = read_file(fpath)
    if not content:
        check(False, f"{fpath} exists")
        continue

    t = content.lower()

    # V4+ appears in allowed template levels
    has_v4plus = "v4+" in t or "v4plus" in t or "v4 plus" in t
    check(has_v4plus, f"{fpath} mentions V4+")

    # Does NOT say V4+ = V4 and above
    bad_eq = re.search(r"v4\+\s*(?:=|means?|is)\s*(?:v4\s+)?(?:and\s+)?above", t)
    check(bad_eq is None, f"{fpath} does NOT say V4+ = V4 and above")

    # Does NOT say V4+ includes V6+
    bad_includes = re.search(r"v4\+.*(?:include|cover|encompass).*v6", t)
    check(bad_includes is None, f"{fpath} does NOT say V4+ includes V6+")

    # V6+ is strict evidence mode
    has_v6_strict = ("v6+" in t or "v6_plus" in t) and ("strict evidence" in t or "strict_evidence" in t)
    check(has_v6_strict, f"{fpath} says V6+ is strict evidence mode")

# Check no spurious V0+, V1+, V2+, V3+, V5+ levels
print("\n--- Spurious level check ---")
# These should NOT appear as distinct levels
spurious_levels = ["V0+", "V1+", "V2+", "V3+", "V5+"]
for fpath in files_to_check:
    content = read_file(fpath)
    if not content:
        continue
    for level in spurious_levels:
        # Check if the level appears as a standalone level (not part of V4+)
        # We need to be careful: "V0-V5" is fine, "V0+" as a level is not
        pattern = re.compile(r'\b' + re.escape(level) + r'\b')
        # In JSON, it might be in a string. In markdown, it might be in text.
        # We should check it's not in an enum or level list
        if level == "V4+":
            continue  # V4+ is valid
        matches = pattern.findall(content)
        if matches:
            # Check context - should not be in a level list
            # Allow in sentences like "no V0+, V1+..." describing what NOT to do
            for match in matches:
                idx = content.find(match)
                context = content[max(0, idx-50):idx+50].lower()
                if "no " in context or "not " in context or "do not" in context or "禁止" in context or "不" in context:
                    continue
                check(False, f"{fpath} does not list {level} as a valid level")
                break
            else:
                check(True, f"{fpath} does not list {level} as a valid level")
        else:
            check(True, f"{fpath} does not list {level} as a valid level")


# Specific checks for external-agent-quickstart.md
print("\n--- external-agent-quickstart.md V4+ explicit checks ---")
ext_qs = read_file("external-agent-quickstart.md")
if ext_qs:
    check("V0, V1, V2, V3, V4, V4+, or V5" in ext_qs,
          "external-agent-quickstart.md Path A includes V4+ in level list")
    check("V0, V1, V2, V3, V4, or V5" not in ext_qs.replace("V4+", ""),
          "external-agent-quickstart.md does not have V0-V5 list without V4+")
    check("V4+ is a distinct" in ext_qs,
          "external-agent-quickstart.md says V4+ is distinct")
    check("V6+ remains strict evidence" in ext_qs,
          "external-agent-quickstart.md says V6+ remains strict evidence")
    check("Creating a Gateway Issue means the candidate entered intake" not in ext_qs,
          "external-agent-quickstart.md no longer has unscoped intake wording")

# Specific checks for agent-submit.md
print("\n--- agent-submit.md V4+ explicit checks ---")
agent_submit = read_file("agent-submit.md")
if agent_submit:
    check("V0, V1, V2, V3, V4, V4+, or V5" in agent_submit or "V4+" in agent_submit,
          "agent-submit.md includes V4+")
    check("Legacy / V6+ Verification Echo Issue fields" in agent_submit,
          "agent-submit.md has scoped legacy Issue fields heading")
    check("This section does not apply to V0" in agent_submit,
          "agent-submit.md scopes legacy section away from V0-V5")

# JSON-specific checks
print("\n--- JSON level enum checks ---")

gateway = read_file("api/agent-submit-gateway.json")
if gateway:
    try:
        data = json.loads(gateway)
        v0v5 = data.get("v0_v5_archive_submission", {})
        levels = v0v5.get("agent_declared_template_levels", [])
        check(levels == ["V0", "V1", "V2", "V3", "V4", "V4+", "V5"],
              "gateway.json template_levels = [V0, V1, V2, V3, V4, V4+, V5]")
        check(v0v5.get("v4_plus_is_distinct_level") is True,
              "gateway.json v4_plus_is_distinct_level = true")
        check(v0v5.get("v4_plus_is_not_v4_and_above") is True,
              "gateway.json v4_plus_is_not_v4_and_above = true")
    except json.JSONDecodeError:
        check(False, "gateway.json is valid JSON")

guide = read_file("api/agent-submission-guide.json")
if guide:
    try:
        data = json.loads(guide)
        v0v5 = data.get("v0_v5_agent_declared_rules", {})
        levels = v0v5.get("agent_declared_template_levels", [])
        check(levels == ["V0", "V1", "V2", "V3", "V4", "V4+", "V5"],
              "submission-guide.json template_levels = [V0, V1, V2, V3, V4, V4+, V5]")
        check(v0v5.get("v4_plus_is_distinct_level") is True,
              "submission-guide.json v4_plus_is_distinct_level = true")
    except json.JSONDecodeError:
        check(False, "submission-guide.json is valid JSON")


print(f"\n=== Results: {PASS_COUNT}/{TOTAL} passed ===")
if FAIL_COUNT > 0:
    print(f"FAILED: {FAIL_COUNT} checks failed")
    sys.exit(1)
else:
    print("V4PLUS_DISTINCT_LEVEL_GUIDANCE_OK")
    sys.exit(0)
