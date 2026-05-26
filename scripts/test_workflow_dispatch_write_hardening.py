#!/usr/bin/env python3
"""
Test: workflow_dispatch write hardening.
TA-REDTEAM-2026-004 — WF-DISPATCH-001 regression test.

Ensures build-echo-index.yml (which writes homepage public status)
has actor allowlist or environment protection for manual dispatch.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / ".github" / "workflows" / "build-echo-index.yml"


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


def main():
    text = WF.read_text(encoding="utf-8")

    # If no workflow_dispatch, no hardening needed
    if "workflow_dispatch:" not in text:
        print("BUILD_ECHO_INDEX_NO_WORKFLOW_DISPATCH_OK")
        return

    # If no contents: write, no hardening needed
    if "contents: write" not in text:
        print("BUILD_ECHO_INDEX_DISPATCH_READONLY_OK")
        return

    # Must have actor allowlist or environment protection
    has_actor_check = (
        "Authorize manual dispatch actor" in text
        and "github.event_name == 'workflow_dispatch'" in text
        and "github.actor" in text
    )

    has_environment = re.search(r"^\s*environment\s*:", text, re.M) is not None

    if not (has_actor_check or has_environment):
        fail("build-echo-index workflow_dispatch + contents:write lacks actor allowlist or environment protection")

    print("WORKFLOW_DISPATCH_WRITE_HARDENING_OK")


if __name__ == "__main__":
    main()
