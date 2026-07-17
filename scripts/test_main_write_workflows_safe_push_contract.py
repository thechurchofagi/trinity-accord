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

        if "group: main-write-lock" in text and "queue: max" not in text:
            offenders.append(f"{rel}: main-write-lock workflow must use queue: max to prevent replacing pending runs")

        if "git pull --rebase" in text:
            offenders.append(f"{rel}: main writer must not use git pull --rebase; use fetch + rebase origin/main")

        if "git rebase origin main" in text:
            offenders.append(f"{rel}: malformed rebase; use git rebase origin/main")

        if "git fetch origin main --prune" not in text or "git rebase origin/main" not in text:
            offenders.append(f"{rel}: missing safe fetch/rebase origin/main sequence")

        if "archive metadata may now be stale; failing so the next run regenerates" in text:
            offenders.append(f"{rel}: fail-open archive retry message still present; rebase/regenerate/amend/retry instead")

    assert not offenders, "\n".join(offenders)


def test_auto_sitemap_workflow_is_retired():
    path = WORKFLOWS / "auto-sitemap.yml"
    assert not path.exists(), (
        f"{path}: presentation-file drift must be enforced in pull-request CI; "
        "do not reintroduce a workflow that writes sitemap.xml directly to main"
    )


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


def test_append_workflow_allows_internal_actions_dispatch():
    path = WORKFLOWS / "record-chain-append.yml"
    text = path.read_text(encoding="utf-8")
    assert "github-actions[bot]" in text, f"{path}: must allow github-actions[bot] for internal dispatch"
    assert "workflow_dispatch" in text, f"{path}: must support workflow_dispatch trigger"
    assert "Authorize write workflow actor" in text, f"{path}: must have actor authorization gate"


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


def _step_section(text: str, name: str, next_name: str | None = None) -> str:
    marker = f"- name: {name}"
    assert marker in text, f"workflow missing step: {name}"
    section = text.split(marker, 1)[1]
    if next_name:
        next_marker = f"- name: {next_name}"
        assert next_marker in section, f"workflow missing following step: {next_name}"
        section = section.split(next_marker, 1)[0]
    return section


def test_agent_declared_index_rebuild_has_token_for_all_github_calls():
    path = WORKFLOWS / "rebuild-agent-declared-index.yml"
    text = path.read_text(encoding="utf-8")

    assert "GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}" not in text
    assert "GH_TOKEN: ${{ secrets.GH_PAT || secrets.GITHUB_TOKEN }}" not in text
    assert "GH_PAT" not in text

    rebuild = _step_section(text, "Rebuild, commit, and push index", "Trigger Deploy Pages")
    assert "env:" in rebuild
    assert "GH_TOKEN: ${{ github.token }}" in rebuild
    assert "INCLUDE_TEST: ${{ inputs.include_test }}" in rebuild
    assert "scripts/build_agent_declared_verification_index_from_issues.py" in rebuild
    assert "--repo \"$GITHUB_REPOSITORY\"" in rebuild

    deploy = _step_section(text, "Trigger Deploy Pages")
    assert "env:" in deploy
    assert "GH_TOKEN: ${{ github.token }}" in deploy
    assert "gh workflow run deploy-pages.yml" in deploy
    assert "--ref main" in deploy

    assert text.count("GH_TOKEN: ${{ github.token }}") == 2


if __name__ == "__main__":
    test_main_writers_use_shared_lock_and_safe_rebase()
    test_auto_sitemap_workflow_is_retired()
    test_archive_workflow_rebuilds_after_rebase()
    test_record_chain_index_writers_stage_overlay_mirror()
    test_write_path_guard_classifies_overlay_as_generated()
    test_agent_declared_index_rebuild_has_token_for_all_github_calls()
    print("All main-write workflow contract tests passed.")
