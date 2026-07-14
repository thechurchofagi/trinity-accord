#!/usr/bin/env python3
"""Regression contract for complete Native OTS generated-state staging."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/native-ots-upgrade-watch.yml"
DETECTOR = ROOT / "scripts/detect_archive_backlog.py"


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        raise SystemExit(f"missing {label}: {needle}")


def main() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    detector = DETECTOR.read_text(encoding="utf-8")

    # detect_archive_backlog.py --write updates both the Record-Chain archive
    # backlog and the Native OTS backlog, including their API projections.
    require(
        detector,
        "[(RC_BACKLOG, rc_doc), (API_RC_BACKLOG, rc_doc), (OTS_BACKLOG, ots_doc), (API_OTS_BACKLOG, ots_doc)]",
        "four-output backlog write contract",
    )

    reconcile_start = workflow.index("          reconcile_and_stage() {")
    reconcile_end = workflow.index("\n          }\n\n          reconcile_and_stage", reconcile_start)
    reconcile = workflow[reconcile_start:reconcile_end]

    git_add_start = reconcile.index("            git add \\")
    git_add_end = reconcile.index("\n\n            while IFS=", git_add_start)
    git_add = reconcile[git_add_start:git_add_end]

    generated_backlogs = [
        "record-chain/ots/native-ots-backlog.json",
        "api/record-chain-native-ots-backlog.json",
        "record-chain/arweave-backlog.json",
        "api/record-chain-arweave-backlog.json",
    ]
    for path in generated_backlogs:
        require(git_add, path, "complete generated backlog git add")

    # Both volatile-only restoration passes must know about the Record-Chain
    # backlog files too; otherwise timestamp-only drift can trip the dirty-tree guard.
    for path in [
        "record-chain/arweave-backlog.json",
        "api/record-chain-arweave-backlog.json",
    ]:
        count = workflow.count(f"--path {path}")
        if count != 2:
            raise SystemExit(f"expected two volatile restore entries for {path}, found {count}")

    require(workflow, "git status --porcelain --untracked-files=no", "tracked dirty-tree guard")
    print("PASS: Native OTS complete generated-state staging contract")


if __name__ == "__main__":
    main()
