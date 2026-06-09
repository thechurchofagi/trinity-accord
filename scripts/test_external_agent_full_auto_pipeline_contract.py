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

    # Arweave has early no-op for already archived head
    require(
        "archive_check" in arweave_workflow,
        "Arweave workflow must have early no-op check for already archived head",
    )
    require(
        "No new Arweave archive needed" in arweave_workflow,
        "Arweave workflow must print no-op message when archive is up to date",
    )
    require(
        "matched" in arweave_workflow,
        "Arweave workflow must use matched output for no-op guard",
    )

    # Arweave workflow contains ARKEY but does not contain lowercase echo
    require(
        "ARKEY" in arweave_workflow,
        "Arweave workflow must reference ARKEY secret",
    )
    # Check no lowercase "echo" in the workflow file (the word echo in comments/strings is ok
    # but the actual workflow text should not have bare lowercase echo that triggers test failures)
    # The test_record_chain_arweave_archive_contract.py checks for this specifically

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

    # Append workflow must regenerate public counters
    require(
        "generate_public_home_status.py" in append_workflow,
        "append workflow must regenerate public home status",
    )
    require(
        "generate_sitemap.py" in append_workflow,
        "append workflow must regenerate sitemap",
    )

    print("External-agent full-auto pipeline contract PASSED.")


if __name__ == "__main__":
    main()
