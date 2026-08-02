#!/usr/bin/env python3
"""Security checks for retired writers and current integrity workflows."""

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

    repository_integrity = (WORKFLOWS / "repository-integrity.yml").read_text(
        encoding="utf-8"
    )
    integrity_header = repository_integrity.split("jobs:", 1)[0]
    require(
        "permissions:" in integrity_header,
        "repository-integrity.yml has no explicit top-level permissions",
    )
    require(
        "contents: read" in integrity_header,
        "repository-integrity.yml does not declare top-level contents: read",
    )
    require(
        repository_integrity.count("contents: write") == 1,
        "repository-integrity.yml must expose exactly one scoped contents writer",
    )
    writer = repository_integrity.split(
        "  refresh-repository-preservation-doi:\n", 1
    )
    require(
        len(writer) == 2,
        "repository-integrity.yml lacks the scoped DOI refresh writer job",
    )
    writer_text = writer[1]
    require(
        "needs: current-system-integrity" in writer_text,
        "DOI refresh writer is not gated by complete repository integrity",
    )
    require(
        "github.event_name == 'push'" in writer_text
        and "github.ref == 'refs/heads/main'" in writer_text,
        "DOI refresh writer is not restricted to main pushes",
    )
    require(
        "group: main-write-lock" in writer_text
        and "queue: max" in writer_text
        and "cancel-in-progress: false" in writer_text,
        "DOI refresh writer lacks queued main-write serialization",
    )
    require(
        "contents: write" in writer_text,
        "DOI refresh writer lacks its required scoped contents permission",
    )
    require(
        "bash scripts/run_repository_preservation_refresh_ci.sh" in writer_text,
        "DOI refresh writer does not use the audited transaction runner",
    )
    for forbidden in ("issues: write", "pull-requests: write", "actions: write", "id-token: write"):
        require(
            forbidden not in writer_text,
            f"DOI refresh writer unexpectedly requests {forbidden}",
        )

    for name in ["repository-full-integrity.yml", "deep-integrity.yml"]:
        text = (WORKFLOWS / name).read_text(encoding="utf-8")
        header = text.split("jobs:", 1)[0]
        require("permissions:" in header, f"{name} has no explicit top-level permissions")
        require("contents: read" in header, f"{name} does not declare contents: read")
        require("contents: write" not in text, f"{name} unexpectedly requests contents: write")

    print("WORKFLOW_PERMISSIONS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
