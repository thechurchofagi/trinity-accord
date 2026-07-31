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
        '"git", "status", "--porcelain", "--untracked-files=no"',
        "tracked dirty-tree guard",
    )
    require(orchestrator, "assert_clean_tracked_worktree()", "clean guard invocation")

    retry = orchestrator.split("def push_metadata_only", 1)[-1].split("def main", 1)[0]
    require(retry, "reconcile_and_stage()", "post-rebase generated-state reconciliation")
    if "run_native_ots_upgrade_verify.py" in retry or "--enable-paid-upload" in retry:
        raise SystemExit("metadata push retry must never repeat an OTS upgrade or paid upload")

    print("PASS: Native OTS complete generated-state staging contract")


if __name__ == "__main__":
    main()
