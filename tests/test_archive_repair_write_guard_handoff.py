from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def test_archive_backlog_scan_is_read_only_and_guarded_as_code() -> None:
    archive = (WORKFLOWS / "archive-backlog-repair.yml").read_text(encoding="utf-8")
    guard = (WORKFLOWS / "record-chain-write-path-guard.yml").read_text(encoding="utf-8")

    # The guard must evaluate the actual PR/push commit, never an upstream
    # workflow_run head that may not contain the writer result.
    assert "workflow_run:" not in guard
    assert "github.event.workflow_run.head_sha" not in guard

    # Changes to the retired repair workflow remain protected by the same path
    # guard even though its runtime is now strictly read-only.
    assert '".github/workflows/archive-backlog-repair.yml"' in guard

    assert "contents: read" in archive
    assert "contents: write" not in archive
    assert "--mode dry-run" in archive
    assert "--mode live" not in archive
    assert "--enable-paid-upload" not in archive
    assert "git push" not in archive
    assert "git commit" not in archive
    assert "git add" not in archive
    assert "ARKEY" not in archive
    assert "ARWEAVE_JWK" not in archive
    assert "This scheduled workflow never uploads to Arweave" in archive
