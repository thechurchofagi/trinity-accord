#!/usr/bin/env python3
"""Run one Record-Chain Arweave archive attempt and never re-upload on push retry.

The retry sequence is the programmatic equivalent of ``git fetch origin main
--prune`` followed by ``git rebase origin/main`` and a metadata-only push. The
paid incremental builder is invoked once before this retry loop and never from
inside it.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_PATHS = [
    "record-chain/arweave-archives/",
    "api/record-chain-arweave-index.json",
    "record-chain/arweave-backlog.json",
    "api/record-chain-arweave-backlog.json",
    "record-chain/ots/native-ots-backlog.json",
    "api/record-chain-native-ots-backlog.json",
    "record-chain/arweave-wallet-ledger.json",
    "api/arweave-wallet-status.json",
]


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        list(args),
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=os.environ.copy(),
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if check and result.returncode != 0:
        raise SystemExit(result.returncode)
    return result


def stage_metadata() -> None:
    run("python3", "scripts/detect_archive_backlog.py", "--write")
    if (ROOT / "scripts/generate_arweave_wallet_status.py").exists():
        run("python3", "scripts/generate_arweave_wallet_status.py")
    run("git", "add", *ARCHIVE_PATHS)
    run("git", "diff", "--cached", "--check")


def cached_changes() -> bool:
    return run("git", "diff", "--cached", "--quiet", check=False).returncode != 0


def amend_derived_metadata(commit_message: str) -> None:
    stage_metadata()
    if cached_changes():
        subject = run("git", "log", "-1", "--pretty=format:%s").stdout.strip()
        if subject != commit_message:
            raise SystemExit(f"unexpected archive commit during retry: {subject}")
        run("git", "commit", "--amend", "--no-edit")


def push_without_reupload(commit_message: str) -> None:
    for attempt in range(1, 4):
        run("git", "fetch", "origin", "main", "--prune")
        result = run("git", "rebase", "origin/main", check=False)
        if result.returncode != 0:
            run("git", "rebase", "--abort", check=False)
            raise SystemExit("archive metadata rebase failed; refusing to repeat the paid upload")
        amend_derived_metadata(commit_message)
        pushed = run("git", "push", "origin", "HEAD:main", check=False)
        if pushed.returncode == 0:
            return
        print(
            f"Push rejected on attempt {attempt}; retrying metadata rebase only. "
            "The Arweave uploader will not run again."
        )
        time.sleep(attempt * 5)
    raise SystemExit("failed to push archive metadata after retries; no repeat upload was attempted")


def main() -> int:
    mode = os.environ.get("ARWEAVE_UPLOAD_MODE", "dry-run").strip()
    if mode not in {"dry-run", "live"}:
        raise SystemExit(f"invalid ARWEAVE_UPLOAD_MODE: {mode}")

    if mode == "dry-run":
        return run(
            "python3",
            "scripts/run_record_chain_arweave_incremental.py",
            "--mode",
            "dry-run",
            check=False,
        ).returncode

    build = run(
        "python3",
        "scripts/run_record_chain_arweave_incremental.py",
        "--mode",
        "live",
        check=False,
    )
    if build.returncode == 75:
        print("Daily Record-Chain paid-upload budget already used; deferring without mutation.")
        return 0

    stage_metadata()
    if not cached_changes():
        if build.returncode == 0:
            print("No Record-Chain Arweave metadata changes; no push required.")
            return 0
        raise SystemExit(build.returncode)

    commit_message = (
        "archive: update native record-chain Arweave archive metadata"
        if build.returncode == 0
        else "archive: checkpoint incomplete Arweave upload for safe readback resume"
    )
    run("git", "config", "user.name", "trinity-record-chain-bot")
    run("git", "config", "user.email", "actions@github.com")
    run("git", "commit", "-m", commit_message)
    push_without_reupload(commit_message)

    if build.returncode != 0:
        print("Incomplete upload checkpoint was persisted; reporting the original failure.", file=sys.stderr)
        return build.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
