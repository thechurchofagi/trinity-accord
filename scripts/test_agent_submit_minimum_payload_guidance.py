#!/usr/bin/env python3
"""Test agent-submit.md has builder-first guidance, not invalid minimum JSON."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT_SUBMIT = ROOT / "agent-submit.md"


def main():
    passed = 0
    failed = 0
    total = 0

    def check(label, condition, detail=""):
        nonlocal passed, failed, total
        total += 1
        if condition:
            print(f"PASS: {label}")
            passed += 1
        else:
            print(f"FAIL: {label}")
            if detail:
                print(f"  {detail}")
            failed += 1

    text = AGENT_SUBMIT.read_text(encoding="utf-8")

    # Test 1: Does not label incomplete object as "Minimum payload"
    check(
        "No 'Minimum payload' label for incomplete JSON",
        "Minimum payload" not in text,
    )

    # Test 2: Recommends builder script before any hand-written JSON
    builder_pos = text.find("build_agent_declared_archive_payload.py")
    json_block_pos = text.find("```json")
    if builder_pos > 0 and json_block_pos > 0:
        check(
            "Builder guidance appears before JSON blocks",
            builder_pos < json_block_pos,
        )
    else:
        check("Builder guidance present", builder_pos > 0)

    # Test 3: Mentions readback_required=true
    check(
        "Mentions readback_required=true",
        "readback_required=true" in text or "readback_required" in text,
    )

    # Test 4: Mentions 160+ chars for agent_readback
    check(
        "Mentions 160+ chars for agent_readback",
        "160" in text,
    )

    # Test 5: Uses canonical site path for quickstart link
    check(
        "Uses canonical /external-agent-quickstart/ link",
        "/external-agent-quickstart/" in text,
    )
    check(
        "No relative .md link to quickstart",
        "(external-agent-quickstart.md)" not in text,
    )

    # Test 6: V0-V5 fail-closed rule documented
    check(
        'agent-submit.md states V0-V5 intake_only is rejected',
        "intake_only" in text and ("reject" in text.lower() or "fail-closed" in text.lower()),
    )
    check(
        'agent-submit.md states V0-V5 requested_archive_kind=none is rejected',
        "requested_archive_kind" in text and "none" in text and "reject" in text.lower(),
    )

    print(f"\n--- Results: {passed}/{total} passed, {failed} failed ---")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
