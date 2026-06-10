#!/usr/bin/env python3
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


def read(rel: str) -> str:
    path = ROOT / rel
    require(path.exists(), f"missing {rel}")
    return path.read_text(encoding="utf-8")


def main() -> int:
    workflow = read(".github/workflows/archive-backlog-repair.yml")
    processor = read("scripts/process_archive_backlog.py")
    builder = read("scripts/build_record_chain_arweave_archive.py")
    uploader = read("scripts/arweave_upload_payload.mjs")
    runner = read("scripts/run_native_ots_upgrade_verify.py")
    guard = read("scripts/check_record_chain_write_path_guard.py")

    for needle in [
        "workflow_dispatch:",
        "cron: \"17 * * * *\"",
        "contents: write",
        "actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5",
        "fetch-depth: 0",
        "python3 scripts/detect_archive_backlog.py --write",
        "--kind record_chain_arweave --max-items 1 --mode live",
        "--kind native_ots_bundle --max-items 1 --enable-paid-upload",
        "archive: repair backlog and wallet status metadata",
        "Forbidden write path",
        "record-chain/chain-tip.json",
        "generate_arweave_wallet_status.py",
        "arweave-wallet-ledger.json",
        "arweave-wallet-status.json",
        "requirements-ots.txt",
        "ots --help",
        "record-chain/ots/native-anchors/",
        "record-chain/ots/native-arweave-bundles/",
        "record-chain/ots/native-arweave-registry.json",
        "api/record-chain-native-ots-arweave-registry.json",
    ]:
        require(needle in workflow, f"workflow missing {needle}")

    for needle in ["waiting_for_key", "upgrade_due", "upgrade_failed", "upgrade_native_ots_anchor", "retry_native_ots_upgrade", "upload_failed", "readback_failed", "archived", "retry_count", "last_attempt_at", "last_error", "next_action"]:
        require(needle in processor, f"processor missing {needle}")

    for needle in ["posted_pending_readback", "readback_failed", "retryable", "fs.writeFileSync(outPath"]:
        require(needle in uploader, f"uploader missing durable result marker {needle}")

    for needle in ["archive_status", "waiting_for_key", "upload_failed", "readback_failed", "hash_match", "refresh_archive_backlog"]:
        require(needle in builder, f"record-chain archive builder missing {needle}")

    for needle in ["--anchor-file", "--all-backlog", "--max-items", "upgrade_due", "upgrade_failed", "waiting_for_key", "upload_failed", "readback_failed", "arweave_archived", "is_current_latest_anchor"]:
        require(needle in runner, f"native OTS runner missing {needle}")

    for needle in ["BACKLOG_FILES", "archive_backlog", "archive: repair backlog and wallet status metadata", "github-actions[bot]"]:
        require(needle in guard, f"write-path guard missing {needle}")

    print("PASS: archive backlog repair contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
