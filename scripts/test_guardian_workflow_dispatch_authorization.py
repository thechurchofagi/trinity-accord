#!/usr/bin/env python3
"""Check Guardian registry workflow dispatch authorization is configurable."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "guardian-registry-auto-list.yml"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    text = WORKFLOW.read_text(encoding="utf-8")

    require("GUARDIAN_REGISTRY_WORKFLOW_ACTORS" in text, "workflow must use GUARDIAN_REGISTRY_WORKFLOW_ACTORS")
    require("vars.GUARDIAN_REGISTRY_WORKFLOW_ACTORS" in text, "job-level authorization must read repository variable")
    require("Set repository variable GUARDIAN_REGISTRY_WORKFLOW_ACTORS" in text, "workflow should explain allowlist setup")

    print("GUARDIAN_WORKFLOW_DISPATCH_AUTHORIZATION_OK")


if __name__ == "__main__":
    main()
