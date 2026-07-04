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

        if rel.as_posix() == ".github/workflows/auto-sitemap.yml" and "queue: max" not in text:
            offenders.append(f"{rel}: push-triggered sitemap writer must use queue: max so it cannot replace a pending main writer")

        if "git pull --rebase" in text:
            offenders.append(f"{rel}: main writer must not use git pull --rebase; use fetch + rebase origin/main")

        if "git rebase origin main" in text:
            offenders.append(f"{rel}: malformed rebase; use git rebase origin/main")

        uses_reset_regenerate_retry = (
            rel.as_posix() == ".github/workflows/auto-sitemap.yml"
            and "git reset --hard origin/main" in text
            and "python3 scripts/generate_sitemap.py" in text
            and "Failed to push regenerated sitemap after retries" in text
        )
        if not uses_reset_regenerate_retry:
            if "git fetch origin main --prune" not in text or "git rebase origin/main" not in text:
                offenders.append(f"{rel}: missing safe fetch/rebase origin/main sequence")

        if "archive metadata may now be stale; failing so the next run regenerates" in text:
            offenders.append(f"{rel}: fail-open archive retry message still present; rebase/regenerate/amend/retry instead")

    assert not offenders, "\n".join(offenders)


def test_auto_sitemap_rebuilds_after_push_race():
    path = WORKFLOWS / "auto-sitemap.yml"
    text = path.read_text(encoding="utf-8")
    required = [
        "group: main-write-lock",
        "queue: max",
        "fetch-depth: 0",
        "ref: main",
        "git push origin HEAD:main",
        "git fetch origin main --prune",
        "git reset --hard origin/main",
        "python3 scripts/generate_sitemap.py",
        "Failed to push regenerated sitemap after retries",
    ]
    missing = [item for item in required if item not in text]
    assert not missing, f"{path}: missing auto-sitemap retry safety pieces: {missing}"


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


def test_agent_declared_index_rebuild_has_token_for_all_issue_fetches():
    path = WORKFLOWS / "rebuild-agent-declared-index.yml"
    text = path.read_text(encoding="utf-8")

    assert "GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}" not in text
    assert "GH_TOKEN: ${{ secrets.GH_PAT || secrets.GITHUB_TOKEN }}" not in text
    assert text.count("GH_TOKEN: ${{ github.token }}") >= 3

    commit_section = text.split("- name: Commit and push", 1)[1]
    assert "env:" in commit_section
    assert "GH_TOKEN: ${{ github.token }}" in commit_section
    assert "INCLUDE_TEST: ${{ inputs.include_test }}" in commit_section
    assert "EXTRA_ARGS=\"\"" in commit_section
    assert "scripts/build_agent_declared_verification_index_from_issues.py" in commit_section


if __name__ == "__main__":
    test_main_writers_use_shared_lock_and_safe_rebase()
    test_auto_sitemap_rebuilds_after_push_race()
    test_archive_workflow_rebuilds_after_rebase()
    test_record_chain_index_writers_stage_overlay_mirror()
    test_write_path_guard_classifies_overlay_as_generated()
    test_agent_declared_index_rebuild_has_token_for_all_issue_fetches()
    print("All main-write workflow contract tests passed.")
