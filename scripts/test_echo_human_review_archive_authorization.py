#!/usr/bin/env python3
"""Ensure the retired Gateway-v1 Echo writer cannot be reactivated accidentally."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "echo-human-review-action.yml"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    text = WORKFLOW.read_text(encoding="utf-8")
    header = text.split("jobs:", 1)[0]

    require("issue_comment:" not in header, "retired workflow must not listen to issue comments")
    require("workflow_dispatch:" in header, "retired workflow must remain manually inspectable")
    require("contents: read" in header, "retired workflow must be read-only")
    require("contents: write" not in text, "retired workflow must not write repository contents")
    require("issues: write" not in text, "retired workflow must not write issues")
    require("git push" not in text, "retired workflow must not push")
    require("archive_echo_issue.py" not in text, "retired workflow must not call removed writers")
    require("Record-Chain Intake Gateway" in text, "retired workflow must identify the current route")

    print("ECHO_HUMAN_REVIEW_WORKFLOW_RETIRED_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
