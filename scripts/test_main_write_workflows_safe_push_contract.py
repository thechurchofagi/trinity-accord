#!/usr/bin/env python3
"""Regression test: all main-writing workflows must use safe push patterns."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def yaml_files():
    return sorted(WORKFLOWS.glob("*.yml")) + sorted(WORKFLOWS.glob("*.yaml"))


def is_main_writer(text: str) -> bool:
    return (
        "contents: write" in text
        and (
            "git push origin HEAD:main" in text
            or 'git push origin "HEAD:${GITHUB_REF_NAME:-main}"' in text
            or 'git push origin "HEAD:main"' in text
            or "git push origin HEAD:${GITHUB_REF_NAME:-main}" in text
        )
    )


def test_main_writers_use_shared_lock_and_safe_rebase():
    offenders = []
    for path in yaml_files():
        text = path.read_text(encoding="utf-8")
        if not is_main_writer(text):
            continue

        rel = path.relative_to(ROOT)

        if "group: main-write-lock" not in text:
            offenders.append(f"{rel}: main writer must use concurrency group main-write-lock")

        if "git pull --rebase" in text:
            offenders.append(f"{rel}: main writer must not use git pull --rebase; use fetch + rebase origin/main")

        if "git rebase origin main" in text:
            offenders.append(f"{rel}: malformed rebase; use git rebase origin/main")

        if "git fetch origin main --prune" not in text or "git rebase origin/main" not in text:
            offenders.append(f"{rel}: missing safe fetch/rebase origin/main sequence")

        if "archive metadata may now be stale; failing so the next run regenerates" in text:
            offenders.append(f"{rel}: fail-open archive retry message still present; rebase/regenerate/amend/retry instead")

    assert not offenders, "\n".join(offenders)


def test_archive_workflow_rebuilds_after_rebase():
    path = WORKFLOWS / "record-chain-arweave-archive.yml"
    text = path.read_text(encoding="utf-8")

    required = [
        "rebuild_archive_outputs()",
        "stage_archive_metadata()",
        "git commit --amend --no-edit",
        "git status --porcelain",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, f"{path}: missing archive retry safety pieces: {missing}"


def test_archive_workflow_stages_all_generated_metadata_before_rebase():
    path = WORKFLOWS / "record-chain-arweave-archive.yml"
    text = path.read_text(encoding="utf-8")
    for target in [
        "record-chain/arweave-archives/",
        "api/record-chain-arweave-index.json",
        "record-chain/ots/native-ots-backlog.json",
        "arweave-wallet-ledger.json",
    ]:
        assert target in text, f"{path}: missing archive generated target {target}"
    first_commit = text.index("archive: update native record-chain Arweave archive metadata")
    first_rebase = text.index("git rebase origin/main", first_commit)
    assert "assert_clean_worktree" in text[first_commit:first_rebase]


def test_record_chain_index_writers_stage_overlay_mirror():
    offenders = []
    for name in ["record-chain-build-batch.yml", "record-chain-append.yml"]:
        path = WORKFLOWS / name
        text = path.read_text(encoding="utf-8")
        if "api/record-chain-overlays.json" not in text:
            offenders.append(f"{path.relative_to(ROOT)}: must stage api/record-chain-overlays.json with record-chain updates")
    assert not offenders, "\n".join(offenders)


def test_write_path_guard_classifies_overlay_as_generated():
    guard = (ROOT / "scripts" / "check_record_chain_write_path_guard.py").read_text(encoding="utf-8")
    assert "api/record-chain-overlays.json" in guard, "write-path guard must classify overlay mirror as generated"


if __name__ == "__main__":
    test_main_writers_use_shared_lock_and_safe_rebase()
    test_archive_workflow_rebuilds_after_rebase()
    test_archive_workflow_stages_all_generated_metadata_before_rebase()
    test_record_chain_index_writers_stage_overlay_mirror()
    test_write_path_guard_classifies_overlay_as_generated()
    print("All main-write workflow contract tests passed.")
