#!/usr/bin/env python3
"""Run one Native OTS lifecycle attempt without any paid Arweave post.

Daily Native OTS work upgrades or verifies the local proof and commits generated
metadata. Paid publication is owned exclusively by the weekly Record-Chain
continuity archive, which embeds the latest mature proof in its single payload.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE_PATHS = [
    "record-chain/ots/native-anchors/",
    "record-chain/ots/native-arweave-bundles/",
    "record-chain/ots/native-arweave-registry.json",
    "api/record-chain-native-ots-arweave-registry.json",
    "record-chain/ots/native-ots-backlog.json",
    "record-chain/arweave-backlog.json",
    "api/record-chain-arweave-backlog.json",
    "api/record-chain-native-ots-backlog.json",
    "api/record-chain-native-ots-latest.json",
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


def reconcile_and_stage() -> None:
    run("python3", "scripts/reconcile_native_ots_generated_state.py")
    run(
        "python3",
        "scripts/restore_json_if_only_volatile_changes.py",
        "--path",
        "api/record-chain-native-ots-latest.json",
        "--path",
        "record-chain/ots/native-ots-backlog.json",
        "--path",
        "api/record-chain-native-ots-backlog.json",
        "--path",
        "record-chain/arweave-backlog.json",
        "--path",
        "api/record-chain-arweave-backlog.json",
        "--glob",
        "record-chain/ots/native-anchors/*.anchor.json",
        "--volatile-key",
        "generated_at",
        "--volatile-key",
        "updated_at",
        "--volatile-key",
        "checked_at",
        "--volatile-key",
        "upgraded_at",
        "--volatile-key",
        "verified_at",
    )
    run("git", "add", *STAGE_PATHS)
    run("git", "diff", "--cached", "--check")


def cached_changes() -> bool:
    return run("git", "diff", "--cached", "--quiet", check=False).returncode != 0


def assert_clean_tracked_worktree() -> None:
    status_lines = run("git", "status", "--porcelain", "--untracked-files=all").stdout.splitlines()
    run_id = os.environ.get("NATIVE_OTS_RUN_ID", "native-ots-bounded")
    allowed_audit_prefix = f"?? record-chain/audit/native-ots/{run_id}/"
    unexpected = [line for line in status_lines if not line.startswith(allowed_audit_prefix)]
    if unexpected:
        details = "\n".join(unexpected)
        raise SystemExit(f"Native OTS worktree is dirty before metadata rebase/push:\n{details}")


def push_metadata_only(commit_message: str) -> None:
    assert_clean_tracked_worktree()
    for attempt in range(1, 4):
        run("git", "fetch", "origin", "main", "--prune")
        rebased = run("git", "rebase", "origin/main", check=False)
        if rebased.returncode != 0:
            run("git", "rebase", "--abort", check=False)
            raise SystemExit("Native OTS metadata rebase failed")
        reconcile_and_stage()
        if cached_changes():
            subject = run("git", "log", "-1", "--pretty=format:%s").stdout.strip()
            if subject != commit_message:
                raise SystemExit(f"unexpected Native OTS commit during retry: {subject}")
            run("git", "commit", "--amend", "--no-edit")
        assert_clean_tracked_worktree()
        pushed = run("git", "push", "origin", "HEAD:main", check=False)
        if pushed.returncode == 0:
            return
        print(f"Push rejected on attempt {attempt}; retrying metadata-only rebase.")
        time.sleep(attempt * 5)
    raise SystemExit("failed to push Native OTS metadata after retries")


def main() -> int:
    mode = os.environ.get("NATIVE_OTS_MODE", "verify_only").strip()
    run_id = os.environ.get("NATIVE_OTS_RUN_ID", "native-ots-bounded")
    if mode not in {"verify_only", "upgrade_only"}:
        raise SystemExit(f"invalid no-cost NATIVE_OTS_MODE: {mode}")

    command = [
        "python3",
        "scripts/run_native_ots_upgrade_verify.py",
        "--run-id",
        run_id,
    ]
    if mode == "verify_only":
        command.append("--verify-only")

    lifecycle = run(*command, check=False)
    reconcile_and_stage()
    if not cached_changes():
        return lifecycle.returncode

    summary = ROOT / "record-chain" / "audit" / "native-ots" / run_id / "99-native-ots-summary.json"
    result = "failed"
    if summary.exists():
        import json

        result = str(json.loads(summary.read_text(encoding="utf-8")).get("result") or "failed")

    if lifecycle.returncode != 0:
        commit_message = "chore: checkpoint incomplete native OTS lifecycle"
    elif result in {"verified", "already_verified"}:
        commit_message = "chore: verify native OTS proof"
    else:
        commit_message = "chore: sync upgraded native OTS anchor and registry"

    run("git", "config", "user.name", "github-actions[bot]")
    run("git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com")
    run("git", "commit", "-m", commit_message)
    assert_clean_tracked_worktree()
    push_metadata_only(commit_message)
    return lifecycle.returncode


if __name__ == "__main__":
    raise SystemExit(main())
