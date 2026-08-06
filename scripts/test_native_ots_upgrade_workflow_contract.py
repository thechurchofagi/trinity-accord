#!/usr/bin/env python3
"""Contract: daily Native OTS is no-cost; weekly continuity owns publication."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"missing {label} marker: {needle}")


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        raise SystemExit(f"forbidden {label} marker found: {needle}")


def main() -> None:
    workflow = (ROOT / ".github/workflows/native-ots-upgrade-watch.yml").read_text(encoding="utf-8")
    orchestrator = (ROOT / "scripts/run_native_ots_workflow_once.py").read_text(encoding="utf-8")
    runner = (ROOT / "scripts/run_native_ots_upgrade_verify.py").read_text(encoding="utf-8")
    reconciler = (ROOT / "scripts/reconcile_native_ots_generated_state.py").read_text(encoding="utf-8")
    archive_workflow = (ROOT / ".github/workflows/record-chain-arweave-archive.yml").read_text(encoding="utf-8")
    weekly_builder = (ROOT / "scripts/record_chain_arweave_incremental.py").read_text(encoding="utf-8")

    for marker in [
        "push:",
        "branches:",
        "- main",
        '".github/workflows/native-ots-upgrade-watch.yml"',
        '"scripts/run_native_ots_workflow_once.py"',
        '"scripts/run_native_ots_upgrade_verify.py"',
        '"scripts/reconcile_native_ots_generated_state.py"',
        '"scripts/detect_archive_backlog.py"',
        "workflow_dispatch:",
        'cron: "42 6 * * *"',
        "contents: write",
        "group: main-write-lock",
        "queue: max",
        "timeout-minutes: 45",
        "fetch-depth: 0",
        "ref: main",
        "verify_only",
        "upgrade_only",
        'if [ "$EVENT_NAME" = "schedule" ] || [ "$EVENT_NAME" = "push" ]',
        "Run Native OTS workflow contract tests",
        "scripts/test_native_ots_upgrade_workflow_contract.py",
        "scripts/test_native_ots_complete_staging_contract.py",
        "run_native_ots_workflow_once.py",
        "record-chain/audit/native-ots/",
    ]:
        require(workflow, marker, "daily no-cost workflow")

    for marker in [
        "ARKEY",
        "ARWEAVE_JWK",
        "arweave_runtime_spend_guard.mjs",
        "ARWEAVE_MINIMUM_REMAINING_AR",
        "--enable-paid-upload",
        "--confirm-paid-upload",
        "actions/setup-node",
    ]:
        forbid(workflow, marker, "daily workflow paid capability")

    for marker in [
        '{"verify_only", "upgrade_only"}',
        "scripts/run_native_ots_upgrade_verify.py",
        'command.append("--verify-only")',
        "scripts/reconcile_native_ots_generated_state.py",
        "scripts/restore_json_if_only_volatile_changes.py",
        "api/record-chain-native-ots-latest.json",
        "record-chain/ots/native-anchors/",
        'run("git", "fetch", "origin", "main", "--prune")',
        'run("git", "rebase", "origin/main"',
        'run("git", "push", "origin", "HEAD:main"',
        "assert_clean_tracked_worktree()",
    ]:
        require(orchestrator, marker, "no-cost orchestrator")

    for marker in [
        "evaluate_daily_spend",
        "--enable-paid-upload",
        "--confirm-paid-upload",
        "ARWEAVE_JWK_PATH",
        "I_UNDERSTAND_THIS_UPLOADS",
        "arweave_cost_gate.mjs",
    ]:
        forbid(orchestrator, marker, "no-cost orchestrator paid capability")

    retry = orchestrator.split("def push_metadata_only", 1)[-1].split("def main", 1)[0]
    forbid(retry, "run_native_ots_upgrade_verify.py", "metadata retry lifecycle repeat")
    require(retry, "reconcile_and_stage()", "metadata retry reconciliation")

    for marker in [
        "trinityaccord.native-record-chain-ots-latest.v1",
        "trinityaccord.native-record-chain-ots-anchor.v1",
        "ots_upgrade_and_verify",
        "bitcoin_attestation_embedded",
        "strict_bitcoin_verified",
    ]:
        require(runner, marker, "local Native OTS lifecycle")

    for marker in [
        "never upgrades an OTS proof and never uploads to Arweave",
        "sync_native_latest_from_anchor",
        "validate_native_registry",
        "scripts/detect_archive_backlog.py",
        '"paid_upload_performed": False',
        '"ots_upgrade_performed": False',
    ]:
        require(reconciler, marker, "derived-state reconciler")

    require(archive_workflow, 'cron: "17 7 * * 3"', "weekly paid archive schedule")
    require(archive_workflow, "ARKEY", "weekly archive wallet boundary")
    require(
        archive_workflow,
        "Automated upstream event is dry-run only",
        "upstream dry-run boundary",
    )
    for marker in [
        "trinityaccord.weekly-continuity-bundle.v1",
        "trinityaccord.weekly-native-ots-evidence.v1",
        'latest.get("latest_ots_file")',
        "proof_files_embedded_in_this_payload",
    ]:
        require(weekly_builder, marker, "weekly embedded OTS evidence")

    print("PASS: daily Native OTS is no-cost; lifecycle changes trigger immediate validation; weekly continuity archive owns paid publication")


if __name__ == "__main__":
    main()
