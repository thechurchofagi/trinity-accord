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


def require_all(rel: str, needles: list[str]) -> None:
    text = read(rel)
    missing = [needle for needle in needles if needle not in text]
    if missing:
        fail(f"{rel} missing required marker(s): {missing}")


def main() -> int:
    require_all("scripts/detect_archive_backlog.py", [
        "all_native_anchors",
        "native_anchor_sources",
        "native_ots_items_and_scan",
        "upgrade_due",
        "upgrade_failed",
        "upgrade_completed_prefix_record_index",
        "arweave_archive_completed_prefix_record_index",
    ])

    require_all("scripts/archive_backlog_lib.py", [
        "upgrade_due_count",
        "upgrade_failed_count",
        "first_open_record_index",
        "open_item_count",
    ])

    require_all("scripts/process_archive_backlog.py", [
        "ACTIONABLE_NATIVE_STATUSES",
        "UPLOAD_NATIVE_STATUSES",
        "upgrade_due",
        "upgrade_failed",
        "retry_native_ots_upgrade",
        "--anchor-file",
        "--all-backlog",
    ])

    require_all("scripts/run_native_ots_upgrade_verify.py", [
        "upgrade_due",
        "upgrade_failed",
        "is_current_latest_anchor",
        "Historical repair must not rewind or pollute",
        "--anchor-file",
        "--all-backlog",
    ])

    require_all(".github/workflows/archive-backlog-repair.yml", [
        "requirements-ots.txt",
        "ots --help",
        "record-chain/ots/native-anchors/",
        "record-chain/ots/native-arweave-bundles/",
        "record-chain/ots/native-arweave-registry.json",
        "api/record-chain-native-ots-arweave-registry.json",
    ])

    require_all("scripts/test_archive_backlog_detector.py", [
        "all_native_anchors",
        "upgrade_due",
        "upgrade_failed",
        "upgrade_completed_prefix_record_index",
        "arweave_archive_completed_prefix_record_index",
    ])

    require_all("scripts/test_archive_backlog_repair_contract.py", [
        "upgrade_due",
        "upgrade_failed",
        "upgrade_native_ots_anchor",
        "retry_native_ots_upgrade",
        "is_current_latest_anchor",
    ])

    print("PASS: native OTS repair source contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
