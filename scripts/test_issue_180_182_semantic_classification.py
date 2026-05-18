#!/usr/bin/env python3
"""Test: issue 180/182 semantic classification in agent-declared-archive-overrides.json."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OVERRIDES_PATH = ROOT / "api" / "agent-declared-archive-overrides.json"

PASS = 0
FAIL = 0


def check(cond, label, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS: {label}")
    else:
        FAIL += 1
        print(f"  FAIL: {label}")
        if detail:
            print(f"        {detail}")


def main():
    global PASS, FAIL
    overrides = json.loads(OVERRIDES_PATH.read_text())
    override_map = overrides.get("overrides", {})

    print("=== Issue 180/182 Semantic Classification Tests ===\n")

    # 1. Has override for issue 182
    o182 = override_map.get("182")
    check(o182 is not None,
          "agent-declared-archive-overrides.json has override for issue 182")

    if o182:
        # 2. semantic_archive_kind: agent_declared_echo_archive
        check(o182.get("semantic_archive_kind") == "agent_declared_echo_archive",
              "Override has semantic_archive_kind: agent_declared_echo_archive")

        # 3. echo_type: E5_correction_echo
        check(o182.get("echo_type") == "E5_correction_echo",
              "Override has echo_type: E5_correction_echo")

        # 4. counts_toward_home_verifiability: false
        check(o182.get("counts_toward_home_verifiability") is False,
              "Override has counts_toward_home_verifiability: false")

        # 5. counts_toward_home_reception: true
        check(o182.get("counts_toward_home_reception") is True,
              "Override has counts_toward_home_reception: true")

    # 6. Issue 180 correction data: has_correction=true, corrected_by=[182]
    # Derive from overrides: find all overrides that correct issue 180
    corrected_by = []
    for issue_num, override in override_map.items():
        if override.get("related_issue") == 180 and override.get("relation_to_related_issue") == "corrects":
            corrected_by.append(int(issue_num))

    has_correction = len(corrected_by) > 0
    check(has_correction,
          "Issue 180 has_correction: true (derived from overrides)")
    check(182 in corrected_by,
          f"Issue 180 corrected_by includes 182 (got: {corrected_by})")

    print(f"\n=== Results: {PASS} passed, {FAIL} failed ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
