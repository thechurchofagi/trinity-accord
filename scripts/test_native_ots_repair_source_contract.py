#!/usr/bin/env python3
"""Source contract for Native OTS backlog repair after paid-scan retirement."""
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


def require_none(rel: str, needles: list[str]) -> None:
    text = read(rel)
    present = [needle for needle in needles if needle in text]
    if present:
        fail(f"{rel} retains forbidden marker(s): {present}")


def main() -> int:
    # Full-history detector and backlog vocabulary remain available.
    require_all(
        "scripts/detect_archive_backlog.py",
        [
            "all_native_anchors",
            "native_anchor_sources",
            "native_ots_items_and_scan",
            "upgrade_due",
            "upgrade_failed",
            "upgrade_completed_prefix_record_index",
            "arweave_archive_completed_prefix_record_index",
        ],
    )
    require_all(
        "scripts/archive_backlog_lib.py",
        [
            "upgrade_due_count",
            "upgrade_failed_count",
            "first_open_record_index",
            "open_item_count",
        ],
    )

    # Explicit operator repair primitives still support historical anchors and
    # keep current-latest state from being rewound by a historical repair.
    require_all(
        "scripts/process_archive_backlog.py",
        [
            "ACTIONABLE_NATIVE_STATUSES",
            "UPLOAD_NATIVE_STATUSES",
            "upgrade_due",
            "upgrade_failed",
            "retry_native_ots_upgrade",
            "--anchor-file",
            "--all-backlog",
            "run_native_ots_upgrade_verify.py",
        ],
    )
    require_all(
        "scripts/run_native_ots_upgrade_verify.py",
        [
            "upgrade_due",
            "upgrade_failed",
            "is_current_latest_anchor",
            "Historical repair must not rewind or pollute",
            "--anchor-file",
            "--all-backlog",
            "upload_native_ots_bundle_to_arweave",
            "record_arweave_upload_result.py",
        ],
    )

    # Scheduled Native OTS lifecycle is daily and bounded. The orchestrator owns
    # daily quota, complete staging, and metadata-only push retries.
    require_all(
        ".github/workflows/native-ots-upgrade-watch.yml",
        [
            "requirements-ots.txt",
            "ots --help",
            'cron: "42 6 * * *"',
            "run_native_ots_workflow_once.py",
            "arweave_runtime_spend_guard.mjs",
            "ARWEAVE_MINIMUM_REMAINING_AR",
            "group: main-write-lock",
        ],
    )
    require_all(
        "scripts/run_native_ots_workflow_once.py",
        [
            "evaluate_daily_spend",
            'evaluate_daily_spend("native_ots_bundle_archive")',
            "run_native_ots_upgrade_verify.py",
            "record-chain/ots/native-anchors/",
            "record-chain/ots/native-arweave-bundles/",
            "record-chain/ots/native-arweave-registry.json",
            "api/record-chain-native-ots-arweave-registry.json",
            "push_metadata_only",
            "The OTS upgrade and Arweave uploader will not run again",
        ],
    )
    retry = read("scripts/run_native_ots_workflow_once.py").split(
        "def push_metadata_only", 1
    )[-1].split("def main", 1)[0]
    for forbidden in [
        "run_native_ots_upgrade_verify.py",
        "--enable-paid-upload",
        "--confirm-paid-upload",
    ]:
        require(forbidden not in retry, f"Native OTS metadata retry can repeat active repair: {forbidden}")

    # The former scheduled paid-repair workflow is now only a visibility scan;
    # it intentionally does not install OTS, load keys, stage proof directories,
    # or mutate the repository.
    require_all(
        ".github/workflows/archive-backlog-repair.yml",
        [
            "contents: read",
            "--kind native_ots_bundle",
            "--mode dry-run",
            "This scheduled workflow never uploads to Arweave",
        ],
    )
    require_none(
        ".github/workflows/archive-backlog-repair.yml",
        [
            "requirements-ots.txt",
            "ots --help",
            "record-chain/ots/native-anchors/",
            "record-chain/ots/native-arweave-bundles/",
            "record-chain/ots/native-arweave-registry.json",
            "api/record-chain-native-ots-arweave-registry.json",
            "--mode live",
            "--enable-paid-upload",
            "ARKEY",
            "ARWEAVE_JWK",
            "contents: write",
            "git push",
        ],
    )

    require_all(
        "scripts/test_archive_backlog_detector.py",
        [
            "all_native_anchors",
            "upgrade_due",
            "upgrade_failed",
            "upgrade_completed_prefix_record_index",
            "arweave_archive_completed_prefix_record_index",
        ],
    )
    require_all(
        "scripts/test_archive_backlog_repair_contract.py",
        [
            "upgrade_due",
            "upgrade_failed",
            "upgrade_native_ots_anchor",
            "retry_native_ots_upgrade",
            "is_current_latest_anchor",
        ],
    )

    print("PASS: Native OTS repair remains available only through bounded active paths; scheduled backlog scan is read-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
