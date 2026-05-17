#!/usr/bin/env python3
"""Test: rebuild-agent-declared-index.yml allows Gateway bot only for issues events."""

import re
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "rebuild-agent-declared-index.yml"


def test_workflow_content():
    text = WORKFLOW.read_text()

    # Gateway bot must be in the actor gate for issues events
    assert "trinity-accord-agent-issue-gateway" in text, (
        "Workflow must allow trinity-accord-agent-issue-gateway[bot]"
    )

    # Gateway bot must be restricted to issues events only
    assert 'EVENT_NAME" = "issues"' in text or "EVENT_NAME == 'issues'" in text, (
        "Workflow must restrict Gateway bot to issues events"
    )

    # Gateway bot must NOT be allowed for repository_dispatch
    # Check that Gateway bot is not in the repository_dispatch sender whitelist
    repo_dispatch_section = re.search(
        r'repository_dispatch.*?(?=\n      -|\Z)', text, re.DOTALL
    )
    if repo_dispatch_section:
        assert "trinity-accord-agent-issue-gateway" not in repo_dispatch_section.group(), (
            "Gateway bot must NOT be allowed for repository_dispatch"
        )

    # Original actors must still be allowed
    assert "thechurchofagi" in text, "thechurchofagi must still be allowed"
    assert "github-actions[bot]" in text, "github-actions[bot] must still be allowed"

    # Issue event guard must exist (only closed issues allowed)
    assert 'ACTION" != "closed"' in text or "ACTION != 'closed'" in text, (
        "Workflow must guard that only closed issue events trigger rebuild"
    )


if __name__ == "__main__":
    test_workflow_content()
    print("PASS: test_rebuild_workflow_gateway_actor")
