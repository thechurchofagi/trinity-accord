#!/usr/bin/env python3
"""Contract: external-agent append -> OTS -> safe archive scan pipeline.

External intake and OTS remain automatic. Paid Arweave publication is deliberately
bounded: upstream automation dispatches dry-run scans, while one daily schedule
or an explicit human dispatch may perform the incremental live upload.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read(path: str) -> str:
    p = ROOT / path
    require(p.exists(), f"missing {path}")
    return p.read_text(encoding="utf-8")


def main() -> None:
    append_workflow = read(".github/workflows/record-chain-append.yml")
    ots_workflow = read(".github/workflows/record-chain-head-ots-anchor.yml")
    arweave_workflow = read(".github/workflows/record-chain-arweave-archive.yml")
    guard_script = read("scripts/check_record_chain_write_path_guard.py")
    detector_script = read("scripts/detect_record_chain_pipeline_backlog.py")
    home_sync_workflow = read(".github/workflows/homepage-status-sync.yml")

    require(
        "record-chain-append.yml" in append_workflow or "Append Record Chain Entries" in append_workflow,
        "append workflow must exist as record-chain-append.yml",
    )
    require(
        "name: Append Record Chain Entries" in append_workflow,
        "append workflow name must be 'Append Record Chain Entries'",
    )
    require(
        "Append record-chain entries from Render intake" in append_workflow,
        "append workflow must use stable commit message 'Append record-chain entries from Render intake'",
    )
    require(
        "actions: write" in append_workflow,
        "append workflow must have actions: write permission for dispatching OTS",
    )
    require(
        'gh workflow run record-chain-head-ots-anchor.yml --repo "$GITHUB_REPOSITORY" --ref main' in append_workflow,
        "append workflow must dispatch native OTS anchor workflow after commit with --repo",
    )
    require(
        "append_commit" in append_workflow,
        "append workflow must track commit output for conditional dispatch",
    )

    require(
        "name: Homepage Status Sync" in home_sync_workflow,
        "central homepage status sync workflow must exist",
    )
    for workflow_name in [
        "Record Chain Auto Finalize",
        "Append Record Chain Entries",
        "Record Chain Head OTS Anchor",
        "Record Chain Arweave Archive",
    ]:
        require(
            workflow_name in home_sync_workflow,
            f"homepage sync must listen to {workflow_name}",
        )

    for forbidden in [
        "generate_public_home_status.py",
        "patch_public_home_status_primary.py",
        "api/public-home-status.json",
        "index.md",
        "sitemap.xml",
    ]:
        require(forbidden not in append_workflow, f"append workflow must not write homepage generated artifact: {forbidden}")
        require(forbidden not in ots_workflow, f"OTS workflow must not write homepage generated artifact: {forbidden}")
        require(forbidden not in arweave_workflow, f"Arweave workflow must not write homepage generated artifact: {forbidden}")

    require(
        "scripts/update_public_generated_artifacts.py" in home_sync_workflow,
        "homepage sync must run centralized generated artifacts updater",
    )
    require(
        'gh workflow run deploy-pages.yml --repo "$GITHUB_REPOSITORY" --ref main' in home_sync_workflow,
        "homepage sync must dispatch deploy-pages.yml explicitly with --repo",
    )

    require(
        '"Append Record Chain Entries"' in ots_workflow,
        "OTS workflow must listen to 'Append Record Chain Entries' via workflow_run",
    )
    require(
        '"Record Chain Auto Finalize"' in ots_workflow,
        "OTS workflow must still listen to 'Record Chain Auto Finalize'",
    )
    require(
        "schedule:" in ots_workflow and "*/15 * * * *" in ots_workflow,
        "OTS workflow must scan every 15 minutes",
    )
    require(
        "actions: write" in ots_workflow,
        "OTS workflow must have actions: write permission for dispatching Arweave",
    )
    require(
        "detect_record_chain_pipeline_backlog.py" in ots_workflow,
        "OTS workflow must use pipeline backlog detector",
    )
    require(
        "ots_anchor_needed" in ots_workflow,
        "OTS workflow must check ots_anchor_needed from detector",
    )

    require(
        'gh workflow run record-chain-arweave-archive.yml --repo "${GITHUB_REPOSITORY}" --ref main' in ots_workflow,
        "OTS workflow must dispatch the Arweave archive scanner after successful push with --repo",
    )
    require(
        "-f upload_mode=dry-run" in ots_workflow,
        "OTS automation must dispatch only a dry-run Arweave scan",
    )
    require(
        "-f upload_mode=live" not in ots_workflow,
        "OTS automation must not directly authorize paid Arweave upload",
    )
    require(
        "git fetch origin main --prune" in ots_workflow and "git rebase origin/main" in ots_workflow,
        "OTS workflow must fetch and rebase origin/main before push retry",
    )

    require(
        "workflow_run" in arweave_workflow,
        "Arweave workflow must support workflow_run trigger from OTS",
    )
    require(
        "Record Chain Head OTS Anchor" in arweave_workflow,
        "Arweave workflow must listen to OTS anchor workflow",
    )
    require(
        "Automated upstream event is dry-run only" in arweave_workflow,
        "Arweave workflow_run must be dry-run only",
    )
    require(
        'cron: "17 7 * * *"' in arweave_workflow,
        "Arweave workflow must have one daily automated live schedule",
    )
    require(
        "*/30 * * * *" not in arweave_workflow,
        "Arweave workflow must not retain a 30-minute paid scanner",
    )
    require(
        'if [ "$EVENT_NAME" = "schedule" ]; then' in arweave_workflow and 'mode="live"' in arweave_workflow,
        "the daily schedule must explicitly resolve to live mode",
    )
    require(
        "run_record_chain_arweave_incremental.py" in arweave_workflow,
        "Arweave paid path must use incremental payloads",
    )

    require(
        "detect_record_chain_pipeline_backlog.py" in arweave_workflow,
        "Arweave workflow must use pipeline backlog detector",
    )
    require(
        "arweave_archive_needed" in arweave_workflow,
        "Arweave workflow must check arweave_archive_needed from detector",
    )
    require(
        "ots_matches_chain" in arweave_workflow,
        "Arweave workflow must check ots_matches_chain for OTS wait guard",
    )
    require(
        "backlog" in arweave_workflow,
        "Arweave workflow must have backlog detector step",
    )
    require(
        "git fetch origin main --prune" in arweave_workflow and "git rebase origin/main" in arweave_workflow,
        "Arweave workflow must fetch and rebase origin/main before push retry",
    )
    require(
        "ARKEY" in arweave_workflow,
        "Arweave workflow must reference ARKEY secret",
    )

    require(
        "APPROVED_APPEND_MESSAGE" in guard_script,
        "write-path guard must define APPROVED_APPEND_MESSAGE",
    )
    require(
        "Append record-chain entries from Render intake" in guard_script,
        "write-path guard must allow append workflow commit message",
    )
    require(
        "append workflow" in guard_script,
        "write-path guard must have append workflow approval path",
    )
    require(
        "api/record-chain-status.json" in guard_script,
        "write-path guard must include api/record-chain-status.json in PUBLIC_GENERATED_FILES",
    )

    require(
        "trinity-record-chain-bot" in append_workflow or "github-actions[bot]" in append_workflow,
        "append workflow must commit with bot identity",
    )
    require(
        "git push" in append_workflow,
        "append workflow must push changes",
    )

    require(
        "ots_anchor_needed" in detector_script,
        "backlog detector must output ots_anchor_needed",
    )
    require(
        "arweave_archive_needed" in detector_script,
        "backlog detector must output arweave_archive_needed",
    )
    require(
        "pipeline_current" in detector_script,
        "backlog detector must output pipeline_current",
    )
    require(
        "--github-output" in detector_script,
        "backlog detector must support --github-output flag",
    )

    print("PASS: external-agent automatic append/OTS and bounded incremental archive pipeline contract")


if __name__ == "__main__":
    main()
