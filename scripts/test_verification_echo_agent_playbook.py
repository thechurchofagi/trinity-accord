#!/usr/bin/env python3
"""
Tests for Verification Echo Agent Playbook

PLAY001 playbook JSON valid
PLAY002 playbook contains requested_level_not_achieved_level
PLAY003 playbook contains right/wrong examples
PLAY004 agent-verify links playbook
PLAY005 issue template includes playbook acknowledgements
PLAY006 llms.txt links /api/verification-echo-agent-playbook.json
PLAY007 playbook says official scripts are not V4+
PLAY008 playbook says PASS with skip is not all-green
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PASS_COUNT = 0
FAIL_COUNT = 0


def check(test_id, condition, description):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  {test_id} PASS: {description}")
    else:
        FAIL_COUNT += 1
        print(f"  {test_id} FAIL: {description}")


def test_playbook():
    print("\n=== Verification Echo Agent Playbook Tests ===\n")

    # PLAY001
    path = ROOT / "api" / "verification-echo-agent-playbook.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            playbook = json.load(f)
        check("PLAY001", isinstance(playbook, dict) and "schema" in playbook,
              "playbook JSON valid")
    except Exception as e:
        check("PLAY001", False, f"playbook JSON invalid: {e}")
        return

    # PLAY002
    rules = playbook.get("core_rules", [])
    rule_ids = [r.get("id") for r in rules]
    check("PLAY002", "requested_level_not_achieved_level" in rule_ids,
          "playbook contains requested_level_not_achieved_level")

    # PLAY003
    has_right_wrong = any(
        "right" in r and "wrong" in r for r in rules
    )
    check("PLAY003", has_right_wrong,
          "playbook contains right/wrong examples")

    # PLAY004
    agent_verify = ROOT / "agent-verify.md"
    content = agent_verify.read_text(encoding="utf-8") if agent_verify.exists() else ""
    check("PLAY004", "/verification-echo-agent-playbook/" in content,
          "agent-verify links playbook")

    # PLAY005
    template = ROOT / ".github" / "ISSUE_TEMPLATE" / "echo_submission.yml"
    template_content = template.read_text(encoding="utf-8") if template.exists() else ""
    check("PLAY005", "verification_echo_playbook_acknowledgement" in template_content,
          "issue template includes playbook acknowledgements")

    # PLAY006
    llms = ROOT / "llms.txt"
    llms_content = llms.read_text(encoding="utf-8") if llms.exists() else ""
    check("PLAY006", "/api/verification-echo-agent-playbook.json" in llms_content,
          "llms.txt links /api/verification-echo-agent-playbook.json")

    # PLAY007
    official_rule = any(
        r.get("id") == "official_scripts_not_v4plus" for r in rules
    )
    check("PLAY007", official_rule,
          "playbook says official scripts are not V4+")

    # PLAY008
    skip_rule = any(
        r.get("id") == "script_audit_with_skip_not_all_green" for r in rules
    )
    check("PLAY008", skip_rule,
          "playbook says PASS with skip is not all-green")


if __name__ == "__main__":
    test_playbook()
    print(f"\nFINAL: {'PASS' if FAIL_COUNT == 0 else 'FAIL'} — "
          f"verification echo agent playbook tests "
          f"{'passed' if FAIL_COUNT == 0 else 'FAILED'}. "
          f"({PASS_COUNT} passed, {FAIL_COUNT} failed)")
    sys.exit(1 if FAIL_COUNT > 0 else 0)
