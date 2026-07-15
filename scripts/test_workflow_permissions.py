#!/usr/bin/env python3
"""Security checks for the retired Echo writer and current integrity workflows."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    retired = (WORKFLOWS / "echo-human-review-action.yml").read_text(encoding="utf-8")
    retired_header = retired.split("jobs:", 1)[0]
    require("issue_comment:" not in retired_header, "retired Echo workflow still has an issue-comment trigger")
    require("contents: read" in retired_header, "retired Echo workflow is not read-only")
    require("contents: write" not in retired, "retired Echo workflow can still write contents")
    require("issues: write" not in retired, "retired Echo workflow can still write issues")

    for name in ["repository-integrity.yml", "repository-full-integrity.yml", "deep-integrity.yml"]:
        text = (WORKFLOWS / name).read_text(encoding="utf-8")
        header = text.split("jobs:", 1)[0]
        require("permissions:" in header, f"{name} has no explicit top-level permissions")
        require("contents: read" in header, f"{name} does not declare contents: read")
        require("contents: write" not in text, f"{name} unexpectedly requests contents: write")

    print("WORKFLOW_PERMISSIONS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
