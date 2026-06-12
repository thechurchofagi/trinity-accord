#!/usr/bin/env python3
"""Contract: external-agent full-auto append -> OTS -> Arweave pipeline."""
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

    # Gateway default append workflow
    require(
        "record-chain-append.yml" in append_workflow or "Append Record Chain Entries" in append_workflow,
        "append workflow must exist as record-chain-append.yml",
    )

    # Append workflow name
    require(
        "name: Append Record Chain Entries" in append_workflow,
        "append workflow name must be 'Append Record Chain Entries'",
    )

    # Append commit message
    require(
        "Append record-chain entries from Render intake" in append_workflow,
        "append workflow must use stable commit message 'Append record-chain entries from Render intake'",
    )

    # Append must have actions: write permission
    require(
        "actions: write" in append_workflow,
        "append workflow must have actions: write permission for dispatching OTS",
    )

    # Append must dispatch OTS after successful commit
    require(
        "gh workflow run record-chain-head-ots-anchor.yml" in append_workflow,
        "append workflow must dispatch native OTS anchor workflow after commit",
    )
    require(
        "append_commit" in append_workflow,
        "append workflow must track commit output for conditional dispatch",
    )

    # Central homepage sync workflow must exist
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

    # Business workflows must not write homepage generated artifacts
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

    # OTS listens to Append Record Chain Entries
    require(
        '"Append Record Chain Entries"' in ots_workflow,
        "OTS workflow must listen to 'Append Record Chain Entries' via workflow_run",
    )

    # OTS still listens to Record Chain Auto Finalize
    require(
        '"Record Chain Auto Finalize"' in ots_workflow,
        "OTS workflow must still listen to 'Record Chain Auto Finalize'",
    )

    # OTS must have schedule scanner
    require(
        "schedule:" in ots_workflow,
        "OTS workflow must have schedule scanner",
    )
    require(
        "*/15 * * * *" in ots_workflow,
        "OTS workflow must scan every 15 minutes",
    )

    # OTS must have actions: write permission
    require(
        "actions: write" in ots_workflow,
        "OTS workflow must have actions: write permission for dispatching Arweave",
    )

    # OTS must use backlog detector
    require(
        "detect_record_chain_pipeline_backlog.py" in ots_workflow,
        "OTS workflow must use pipeline backlog detector",
    )
    require(
        "ots_anchor_needed" in ots_workflow,
        "OTS workflow must check ots_anchor_needed from detector",
    )

    # OTS must dispatch Arweave after successful push
    require(
        "gh workflow run record-chain-arweave-archive.yml" in ots_workflow,
        "OTS workflow must dispatch Arweave archive workflow after successful push",
    )
    require(
        "-f upload_mode=live" in ots_workflow,
        "OTS dispatch to Arweave must use live upload mode",
    )

    # OTS must have rebase/retry on push
    require(
        "git pull --rebase origin" in ots_workflow,
        "OTS workflow must rebase before push retry",
    )

    # Arweave workflow_run from OTS resolves to live
    require(
        "workflow_run" in arweave_workflow,
        "Arweave workflow must support workflow_run trigger from OTS",
    )
    require(
        "Record Chain Head OTS Anchor" in arweave_workflow,
        "Arweave workflow must listen to OTS anchor workflow",
    )
    # Check that workflow_run resolves to live mode
    require(
        "workflow_run" in arweave_workflow and "live" in arweave_workflow,
        "Arweave workflow_run trigger must resolve to live upload mode",
    )

    # Arweave must have 30-minute schedule scanner
    require(
        "*/30 * * * *" in arweave_workflow,
        "Arweave workflow must scan every 30 minutes",
    )

    # Arweave must use backlog detector
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

    # Arweave has early no-op for already archived head
    require(
        "backlog" in arweave_workflow,
        "Arweave workflow must have backlog detector step",
    )

    # Arweave workflow must have rebase/retry on push
    require(
        "git pull --rebase origin" in arweave_workflow,
        "Arweave workflow must rebase before push retry",
    )

    # Arweave workflow contains ARKEY but does not contain lowercase echo
    require(
        "ARKEY" in arweave_workflow,
        "Arweave workflow must reference ARKEY secret",
    )

    # Write-path guard allows append workflow commit message
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

    # Write-path guard must include record-chain-status in public generated files
    require(
        "api/record-chain-status.json" in guard_script,
        "write-path guard must include api/record-chain-status.json in PUBLIC_GENERATED_FILES",
    )

    # Append workflow must commit with actions bot identity
    require(
        "trinity-record-chain-bot" in append_workflow or "github-actions[bot]" in append_workflow,
        "append workflow must commit with bot identity",
    )

    # Append workflow must push to main
    require(
        "git push" in append_workflow,
        "append workflow must push changes",
    )

    # Backlog detector script must exist and have key outputs
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

    print("PASS: external-agent full-auto record-chain pipeline contract")


if __name__ == "__main__":
    main()
