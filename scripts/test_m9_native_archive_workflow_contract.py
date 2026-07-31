#!/usr/bin/env python3
"""M9 contract for crash-safe weekly native continuity archival."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(path: Path, marker: str, errors: list[str]) -> None:
    if marker not in path.read_text(encoding="utf-8"):
        errors.append(f"{path.relative_to(ROOT)} missing: {marker}")


def forbid(path: Path, marker: str, errors: list[str]) -> None:
    if marker in path.read_text(encoding="utf-8"):
        errors.append(f"{path.relative_to(ROOT)} must not contain: {marker}")


def main() -> None:
    errors: list[str] = []
    head_wf = ROOT / ".github/workflows/record-chain-head-ots-anchor.yml"
    tip_helper = ROOT / "scripts/check_native_ots_latest_matches_chain_tip.py"
    archive_wf = ROOT / ".github/workflows/record-chain-arweave-archive.yml"
    archive_runner = ROOT / "scripts/run_record_chain_arweave_archive.py"
    incremental_runner = ROOT / "scripts/run_record_chain_arweave_incremental.py"
    incremental_builder = ROOT / "scripts/record_chain_arweave_incremental.py"
    workflow_runner = ROOT / "scripts/run_record_chain_arweave_workflow_once.py"
    runtime_guard = ROOT / "scripts/arweave_runtime_spend_guard.mjs"
    legacy_data_wf = ROOT / ".github/workflows/record-chain-data-arweave-archive.yml"

    for path in [
        head_wf,
        tip_helper,
        archive_wf,
        archive_runner,
        incremental_runner,
        incremental_builder,
        workflow_runner,
        runtime_guard,
        legacy_data_wf,
    ]:
        if not path.exists():
            errors.append(f"missing {path.relative_to(ROOT)}")
    if errors:
        _fail(errors)

    for marker in [
        "Record Chain Head OTS Anchor",
        "requirements-ci.txt",
        "trinity_record_chain.py verify",
        "ots_anchor_native_record_chain_head.py",
        "record-chain/ots/native-anchors",
        "check_native_ots_latest_matches_chain_tip.py",
        '"Record Chain Auto Finalize"',
        '"Append Record Chain Entries"',
        "head_branch == 'main'",
        "git push origin HEAD:main",
    ]:
        require(head_wf, marker, errors)
    for marker in [
        "ots_anchor_record_chain_head.py",
        "main.chain.jsonl",
        "api/record-chain-head.json",
        "record-chain-ots-latest.json",
        "verify_record_chain_integrity.py",
    ]:
        forbid(head_wf, marker, errors)

    for marker in [
        "record-chain/chain-tip.json",
        "api/record-chain-native-ots-latest.json",
        "legacy_main_chain_jsonl_is_not_source",
        "latest_record_id",
        "latest_record_sha256",
        "native_record_count",
        "latest_anchored_file",
        "latest_anchor_file",
        "latest_ots_file",
        "trinity-accord-public-reception-ledger",
    ]:
        require(tip_helper, marker, errors)

    for marker in [
        "Record Chain Arweave Archive",
        "Record Chain Head OTS Anchor",
        "run_record_chain_arweave_workflow_once.py",
        "detect_record_chain_pipeline_backlog.py",
        "arweave_archive_needed",
        "ots_matches_chain",
        "ots_archivable_for_arweave",
        "ARKEY",
        "arweave_runtime_spend_guard.mjs",
        "ARWEAVE_MINIMUM_REMAINING_AR",
        'cron: "17 7 * * 3"',
        "Automated upstream event is dry-run only",
        'if [ "$EVENT_ACTOR" = "github-actions[bot]" ]; then',
        "weekly continuity archive",
    ]:
        require(archive_wf, marker, errors)
    for marker in [
        'cron: "17 7 * * *"',
        "*/30 * * * *",
        "run_record_chain_arweave_archive.py --mode",
        "echo $ARKEY",
        "build_record_chain_data_arweave_bundle.py",
    ]:
        forbid(archive_wf, marker, errors)

    for marker in [
        "verify_record_chain_arweave_archive.py",
        "trinity_record_chain.py",
        "--allow-stale-live-chain-tip",
        "record-chain/arweave-archives/",
        "api/record-chain-arweave-index.json",
        "record-chain/arweave-backlog.json",
        "record-chain/ots/native-ots-backlog.json",
        "record-chain/arweave-wallet-ledger.json",
        "checkpoint incomplete Arweave upload for safe readback resume",
        "assert_clean_tracked_worktree",
        "push_without_reupload",
        "The Arweave uploader will not run again",
    ]:
        require(workflow_runner, marker, errors)
    runner_text = workflow_runner.read_text(encoding="utf-8")
    retry = runner_text.split("def push_without_reupload", 1)[-1].split("def main", 1)[0]
    if "run_record_chain_arweave_incremental.py" in retry:
        errors.append("bounded retry block must not invoke a paid upload")
    order = [
        retry.find("assert_clean_tracked_worktree()"),
        retry.find('run("git", "fetch", "origin", "main", "--prune")'),
        retry.find('run("git", "rebase", "origin/main"'),
        retry.find('run("git", "push", "origin", "HEAD:main"'),
    ]
    if min(order) < 0 or order != sorted(order):
        errors.append("bounded retry block must check clean state, fetch, rebase, then push")

    for marker in [
        "import build_record_chain_arweave_archive as builder",
        "builder.build_archive_manifest",
        "builder.upload_to_arweave = guarded_upload",
        "Resuming Arweave readback without a new paid post",
        "subprocess.TimeoutExpired",
    ]:
        require(archive_runner, marker, errors)

    for marker in [
        "import run_record_chain_arweave_archive as runner",
        "build_incremental_payload_json",
        "runner.builder.build_payload_json = build_incremental_payload_json",
        "runner.main()",
        "evaluate_daily_spend",
    ]:
        require(incremental_runner, marker, errors)

    for marker in [
        "full_snapshot",
        "incremental_delta",
        "previous_archive_txid",
        "delta_record_count",
        "content_base64",
        "does not match the current chain prefix",
        "trinityaccord.weekly-continuity-bundle.v1",
        "trinityaccord.weekly-heartbeat-summary.v1",
        "trinityaccord.weekly-native-ots-evidence.v1",
        "proof_files_embedded_in_this_payload",
    ]:
        require(incremental_builder, marker, errors)

    for marker in [
        "Daily paid Arweave upload limit reached",
        "ARWEAVE_MINIMUM_REMAINING_AR",
        "balance - reward < reserve",
        "Canary-Record",
        "!allowCanaryTags",
    ]:
        require(runtime_guard, marker, errors)

    require(legacy_data_wf, "build_record_chain_data_arweave_bundle.py", errors)
    forbid(legacy_data_wf, "ots_anchor_native_record_chain_head.py", errors)
    forbid(legacy_data_wf, "record-chain-native-ots-latest.json", errors)

    if errors:
        _fail(errors)
    print("M9 crash-safe weekly incremental native continuity archive contract PASSED.")


def _fail(errors: list[str]) -> None:
    print("M9 native archive workflow contract FAILED:", file=sys.stderr)
    for error in errors:
        print(f"  - {error}", file=sys.stderr)
    raise SystemExit(1)


if __name__ == "__main__":
    main()
