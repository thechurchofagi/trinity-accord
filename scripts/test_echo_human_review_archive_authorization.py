#!/usr/bin/env python3
"""Ensure the retired Gateway-v1 Echo writer cannot be reactivated accidentally."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "echo-human-review-action.yml"
CI_RUNNER = ROOT / "scripts" / "run_ci_group.py"


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

    runner = CI_RUNNER.read_text(encoding="utf-8")
    echo_group = runner.split('    "echo-archive": [', 1)[1].split('    "claim-gate": [', 1)[0]
    for retired_test in (
        "test_echo_archive_markdown_escape.py",
        "test_echo_archive_verification_level_metadata.py",
        "test_echo_untrusted_content_marking.py",
    ):
        require(retired_test not in echo_group, f"Deep Integrity must not run obsolete false-pass test {retired_test}")
    for current_test in (
        "test_validate_echo_records_no_fail_open.py",
        "validate_echo_records.py",
        "test_build_echo_index_runs_formal_validator.py",
        "test_agent_e2e_journey_matrix.py",
        "test_no_echo_type.py",
    ):
        require(current_test in echo_group, f"Deep Integrity must exercise current Echo guard {current_test}")

    print("ECHO_HUMAN_REVIEW_WORKFLOW_RETIRED_AND_CURRENT_GUARDS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
