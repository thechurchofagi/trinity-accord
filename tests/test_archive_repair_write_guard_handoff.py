from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def test_archive_repair_validates_exact_commit_before_push() -> None:
    archive = (WORKFLOWS / "archive-backlog-repair.yml").read_text(encoding="utf-8")
    guard = (WORKFLOWS / "record-chain-write-path-guard.yml").read_text(encoding="utf-8")

    assert "workflow_run:" not in guard
    assert "github.event.workflow_run.head_sha" not in guard
    assert '".github/workflows/archive-backlog-repair.yml"' in guard

    function_index = archive.index("validate_exact_archive_commit()")
    push_index = archive.index("git push origin HEAD:main")
    call_index = archive.rfind("validate_exact_archive_commit", 0, push_index)

    assert call_index > function_index
    assert "git rev-list --count" in archive
    assert '--github-actor "github-actions[bot]"' in archive
    assert "Equivalent archive backlog state already reached main" in archive
