#!/usr/bin/env python3
"""Regression contract for complete Native OTS generated-state staging."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORCHESTRATOR = ROOT / "scripts/run_native_ots_workflow_once.py"
DETECTOR = ROOT / "scripts/detect_archive_backlog.py"


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"missing {label}: {needle}")


def main() -> None:
    orchestrator = ORCHESTRATOR.read_text(encoding="utf-8")
    detector = DETECTOR.read_text(encoding="utf-8")

    # detect_archive_backlog.py --write updates both the Record-Chain archive
    # backlog and the Native OTS backlog, including their API projections.
    require(
        detector,
        "[(RC_BACKLOG, rc_doc), (API_RC_BACKLOG, rc_doc), (OTS_BACKLOG, ots_doc), (API_OTS_BACKLOG, ots_doc)]",
        "four-output backlog write contract",
    )

    stage_start = orchestrator.index("STAGE_PATHS = [")
    stage_end = orchestrator.index("\n]\n", stage_start) + 3
    stage_paths = orchestrator[stage_start:stage_end]
    generated_state_paths = [
        "record-chain/ots/native-anchors/",
        "record-chain/ots/native-arweave-bundles/",
        "record-chain/ots/native-arweave-registry.json",
        "api/record-chain-native-ots-arweave-registry.json",
        "record-chain/ots/native-ots-backlog.json",
        "api/record-chain-native-ots-backlog.json",
        "record-chain/arweave-backlog.json",
        "api/record-chain-arweave-backlog.json",
        "api/record-chain-native-ots-latest.json",
        "api/arweave-wallet-status.json",
    ]
    for path in generated_state_paths:
        require(stage_paths, path, "complete Native OTS generated-state staging")
    if "record-chain/audit/native-ots/" in stage_paths:
        raise SystemExit("ephemeral Native OTS audit logs must not be committed")

    reconcile_start = orchestrator.index("def reconcile_and_stage()")
    reconcile_end = orchestrator.index("\n\ndef cached_changes", reconcile_start)
    reconcile = orchestrator[reconcile_start:reconcile_end]

    generated_backlogs = [
        "record-chain/ots/native-ots-backlog.json",
        "api/record-chain-native-ots-backlog.json",
        "record-chain/arweave-backlog.json",
        "api/record-chain-arweave-backlog.json",
    ]
    for path in generated_backlogs:
        require(reconcile, path, "complete generated backlog staging")

    require(
        reconcile,
        "scripts/restore_json_if_only_volatile_changes.py",
        "volatile-only restoration",
    )
    for path in [
        "record-chain/arweave-backlog.json",
        "api/record-chain-arweave-backlog.json",
    ]:
        require(reconcile, path, "Record-Chain backlog volatile restoration")

    require(orchestrator, '"git", "add", *STAGE_PATHS', "single complete staging list")
    require(orchestrator, '"git", "diff", "--cached", "--check"', "staged diff validation")
    require(
        orchestrator,
        '"git", "status", "--porcelain", "--untracked-files=all"',
        "tracked and untracked dirty-tree guard",
    )
    require(
        orchestrator,
        'allowed_audit_prefix = f"?? record-chain/audit/native-ots/{run_id}/"',
        "narrow ephemeral audit-log allowance",
    )
    require(orchestrator, "assert_clean_tracked_worktree()", "clean guard invocation")

    retry = orchestrator.split("def push_metadata_only", 1)[-1].split("def main", 1)[0]
    require(retry, "reconcile_and_stage()", "post-rebase generated-state reconciliation")
    if "run_native_ots_upgrade_verify.py" in retry or "--enable-paid-upload" in retry:
        raise SystemExit("metadata push retry must never repeat an OTS upgrade or paid upload")

    print("PASS: Native OTS complete generated-state staging contract")


if __name__ == "__main__":
    main()
