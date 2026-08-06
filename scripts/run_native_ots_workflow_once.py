#!/usr/bin/env python3
"""Run one Native OTS lifecycle attempt without any paid Arweave post.

Daily Native OTS work upgrades or verifies the current proof, performs a bounded
backfill of historical upgrade-due proofs, and commits all durable generated
metadata atomically. Paid publication is owned exclusively by the weekly
Record-Chain continuity archive, which embeds the latest mature proof in its
single payload.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NATIVE_OTS_BACKLOG = ROOT / "record-chain/ots/native-ots-backlog.json"
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


def bounded_backfill_upgrade_due(run_id: str) -> int:
    """Upgrade a bounded number of historical proofs without any paid upload."""
    raw_limit = os.environ.get("NATIVE_OTS_BACKFILL_MAX_ITEMS", "8").strip()
    try:
        max_items = int(raw_limit)
    except ValueError as exc:
        raise SystemExit(f"invalid NATIVE_OTS_BACKFILL_MAX_ITEMS: {raw_limit}") from exc
    if not 0 <= max_items <= 25:
        raise SystemExit("NATIVE_OTS_BACKFILL_MAX_ITEMS must be between 0 and 25")
    if max_items == 0:
        return 0

    run("python3", "scripts/detect_archive_backlog.py", "--write")
    backlog = json.loads(NATIVE_OTS_BACKLOG.read_text(encoding="utf-8"))
    candidates = [
        item
        for item in backlog.get("items", [])
        if isinstance(item, dict)
        and item.get("archive_status") in {"upgrade_due", "upgrade_failed"}
        and item.get("anchor_file")
    ][:max_items]

    for position, item in enumerate(candidates, start=1):
        anchor_file = str(item["anchor_file"])
        record_index = int(item.get("record_index") or position)
        child_run_id = f"{run_id}-backfill-{record_index:09d}"
        child_log_dir = f"record-chain/audit/native-ots/{run_id}/backfill-{record_index:09d}"
        result = run(
            "python3",
            "scripts/run_native_ots_upgrade_verify.py",
            "--run-id",
            child_run_id,
            "--log-dir",
            child_log_dir,
            "--anchor-file",
            anchor_file,
            check=False,
        )
        if result.returncode != 0:
            print(
                f"Historical Native OTS backfill failed for {anchor_file} "
                f"with exit code {result.returncode}",
                file=sys.stderr,
            )
            return result.returncode

    if candidates:
        print(f"Historical Native OTS proofs upgraded in this run: {len(candidates)}")
    else:
        print("Historical Native OTS upgrade backlog is empty")
    return 0


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
    backfill_returncode = 0
    if lifecycle.returncode == 0 and mode == "upgrade_only":
        backfill_returncode = bounded_backfill_upgrade_due(run_id)
    combined_returncode = lifecycle.returncode or backfill_returncode

    reconcile_and_stage()
    if not cached_changes():
        return combined_returncode

    summary = ROOT / "record-chain" / "audit" / "native-ots" / run_id / "99-native-ots-summary.json"
    result = "failed"
    if summary.exists():
        result = str(json.loads(summary.read_text(encoding="utf-8")).get("result") or "failed")

    if combined_returncode != 0:
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
    return combined_returncode


if __name__ == "__main__":
    raise SystemExit(main())
