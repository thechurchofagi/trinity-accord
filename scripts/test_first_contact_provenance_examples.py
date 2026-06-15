#!/usr/bin/env python3
"""Test that first-contact provenance examples use correct semantics."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent.parent
FIRST_CONTACT = ROOT / "agent-first-contact.md"
AGENT_START = ROOT / "agent-start.md"
FIRST_CONTACT_JSON = ROOT / "api" / "agent-first-contact.json"


def require(cond, msg):
    if not cond:
        raise AssertionError(msg)


def main():
    first = FIRST_CONTACT.read_text(encoding="utf-8")
    start = AGENT_START.read_text(encoding="utf-8")
    router = json.loads(FIRST_CONTACT_JSON.read_text(encoding="utf-8"))

    # Check within individual code blocks — the bad pair must not appear in the same block
    code_blocks = re.findall(r"```bash\n(.*?)```", first, re.DOTALL)
    for i, block in enumerate(code_blocks):
        has_self = re.search(r"--submission-executor\s+self", block)
        has_human_true = re.search(r"--human-operator-involved\s+true", block)
        require(
            not (has_self and has_human_true),
            f"agent-first-contact.md code block {i} must not pair --submission-executor self with --human-operator-involved true",
        )

    require(
        "--submission-executor self" in first and "--human-operator-involved false" in first,
        "agent-first-contact.md should show self-executed agent example with human_operator_involved false",
    )

    require(
        "Human-requested is not the same as human-operated" in start,
        "agent-start.md must retain the core provenance distinction",
    )

    semantics = router.get("provenance_semantics", {})
    require(
        semantics.get("human_request_is_not_human_operation") is True,
        "api/agent-first-contact.json must state human_request_is_not_human_operation",
    )
    require(
        semantics.get("human_introduction_is_not_human_operation") is True,
        "api/agent-first-contact.json must state human_introduction_is_not_human_operation",
    )
    require(
        semantics.get("common_human_requested_agent_executed_case", {}).get("human_operator_involved") is False,
        "machine-readable common human-requested agent-executed case must use human_operator_involved=false",
    )

    print("PASS: first-contact provenance examples")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
