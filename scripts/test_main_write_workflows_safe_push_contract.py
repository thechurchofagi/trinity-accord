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


def test_archive_workflow_delegates_safe_metadata_only_retry():
    workflow_path = WORKFLOWS / "record-chain-arweave-archive.yml"
    workflow = workflow_path.read_text(encoding="utf-8")
    orchestrator_path = ROOT / "scripts" / "run_record_chain_arweave_workflow_once.py"
    orchestrator = orchestrator_path.read_text(encoding="utf-8")

    for marker in [
        "group: main-write-lock",
        "queue: max",
        "run_record_chain_arweave_workflow_once.py",
        "run_record_chain_arweave_incremental.py",
        "arweave_runtime_spend_guard.mjs",
    ]:
        assert marker in workflow, f"{workflow_path}: missing delegated archive safety marker {marker}"

    for marker in [
        "push_without_reupload",
        "stage_metadata",
        'run("git", "commit", "--amend", "--no-edit")',
        'run("git", "status", "--porcelain", "--untracked-files=no")',
        'run("git", "fetch", "origin", "main", "--prune")',
        'run("git", "rebase", "origin/main"',
        'run("git", "push", "origin", "HEAD:main"',
        "The Arweave uploader will not run again",
        "verify_record_chain_arweave_archive.py",
    ]:
        assert marker in orchestrator, f"{orchestrator_path}: missing archive retry safety piece {marker}"

    retry = orchestrator.split("def push_without_reupload", 1)[-1].split("def main", 1)[0]
    assert "run_record_chain_arweave_incremental.py" not in retry, (
        f"{orchestrator_path}: metadata retry must never repeat the paid incremental uploader"
    )
    clean = retry.find("assert_clean_tracked_worktree()")
    fetch = retry.find('run("git", "fetch", "origin", "main", "--prune")')
    rebase = retry.find('run("git", "rebase", "origin/main"')
    push = retry.find('run("git", "push", "origin", "HEAD:main"')
    assert min(clean, fetch, rebase, push) >= 0 and clean < fetch < rebase < push, (
        f"{orchestrator_path}: retry must check clean state, fetch, rebase, then push"
    )


def test_native_ots_workflow_delegates_safe_no_cost_metadata_retry():
    workflow_path = WORKFLOWS / "native-ots-upgrade-watch.yml"
    workflow = workflow_path.read_text(encoding="utf-8")
    orchestrator_path = ROOT / "scripts" / "run_native_ots_workflow_once.py"
    orchestrator = orchestrator_path.read_text(encoding="utf-8")

    for marker in [
        "group: main-write-lock",
        "queue: max",
        "run_native_ots_workflow_once.py",
        'cron: "42 6 * * *"',
        "verify_only",
        "upgrade_only",
    ]:
        assert marker in workflow, f"{workflow_path}: missing delegated Native OTS safety marker {marker}"

    for forbidden in [
        "ARKEY",
        "ARWEAVE_JWK",
        "arweave_runtime_spend_guard.mjs",
        "ARWEAVE_MINIMUM_REMAINING_AR",
        "--enable-paid-upload",
        "--confirm-paid-upload",
    ]:
        assert forbidden not in workflow, (
            f"{workflow_path}: daily no-cost Native OTS workflow retains paid capability {forbidden}"
        )

    for marker in [
        "push_metadata_only",
        "reconcile_and_stage",
        'run("git", "commit", "--amend", "--no-edit")',
        'run("git", "status", "--porcelain", "--untracked-files=no")',
        'run("git", "fetch", "origin", "main", "--prune")',
        'run("git", "rebase", "origin/main"',
        'run("git", "push", "origin", "HEAD:main"',
        "assert_clean_tracked_worktree",
    ]:
        assert marker in orchestrator, f"{orchestrator_path}: missing Native OTS retry safety piece {marker}"

    for forbidden in [
        "evaluate_daily_spend",
        "ARWEAVE_JWK_PATH",
        "--enable-paid-upload",
        "--confirm-paid-upload",
        "record-chain/arweave-wallet-ledger.json",
    ]:
        assert forbidden not in orchestrator, (
            f"{orchestrator_path}: no-cost Native OTS orchestrator retains paid capability {forbidden}"
        )

    retry = orchestrator.split("def push_metadata_only", 1)[-1].split("def main", 1)[0]
    for forbidden in [
        "run_native_ots_upgrade_verify.py",
        "--enable-paid-upload",
        "--confirm-paid-upload",
    ]:
        assert forbidden not in retry, (
            f"{orchestrator_path}: metadata retry may repeat active operation {forbidden}"
        )


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
    test_archive_workflow_delegates_safe_metadata_only_retry()
    test_native_ots_workflow_delegates_safe_no_cost_metadata_retry()
    test_append_workflow_allows_internal_actions_dispatch()
    test_record_chain_index_writers_stage_overlay_mirror()
    test_write_path_guard_classifies_overlay_as_generated()
    test_agent_declared_index_rebuild_has_token_for_all_github_calls()
    print("All main-write workflow contract tests passed.")
