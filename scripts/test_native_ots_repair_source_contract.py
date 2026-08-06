#!/usr/bin/env python3
"""Source contract for Native OTS repair under weekly paid publication.

Historical and current Native OTS repair primitives remain available. The daily
scheduled lifecycle may upgrade/verify local proofs and persist the resulting
local bundle and registry metadata, but wallet credentials and paid Arweave
publication belong exclusively to the weekly Record-Chain continuity archive.
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

    # Explicit operator repair primitives still support historical anchors. The
    # low-level runner may retain optional paid code for deliberate operator use,
    # but no automatic workflow is allowed to wire that capability.
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
            "ots_upgrade_and_verify",
            "strict_bitcoin_verified",
        ],
    )

    # Scheduled Native OTS lifecycle is daily, bounded, and strictly no-cost.
    require_all(
        ".github/workflows/native-ots-upgrade-watch.yml",
        [
            "requirements-ots.txt",
            "ots --help",
            'cron: "42 6 * * *"',
            "run_native_ots_workflow_once.py",
            "verify_only",
            "upgrade_only",
            "group: main-write-lock",
            "queue: max",
        ],
    )
    require_none(
        ".github/workflows/native-ots-upgrade-watch.yml",
        [
            "ARKEY",
            "ARWEAVE_JWK",
            "arweave_runtime_spend_guard.mjs",
            "ARWEAVE_MINIMUM_REMAINING_AR",
            "--enable-paid-upload",
            "--confirm-paid-upload",
            "actions/setup-node",
        ],
    )

    # The daily runner persists every durable no-cost output atomically. Local
    # bundle/registry files are evidence metadata only; their presence is not an
    # Arweave upload and does not grant access to wallet credentials.
    require_all(
        "scripts/run_native_ots_workflow_once.py",
        [
            '{"verify_only", "upgrade_only"}',
            "run_native_ots_upgrade_verify.py",
            "record-chain/ots/native-anchors/",
            "record-chain/ots/native-arweave-bundles/",
            "record-chain/ots/native-arweave-registry.json",
            "api/record-chain-native-ots-arweave-registry.json",
            "api/record-chain-native-ots-latest.json",
            "api/arweave-wallet-status.json",
            "scripts/reconcile_native_ots_generated_state.py",
            "scripts/restore_json_if_only_volatile_changes.py",
            "push_metadata_only",
            "assert_clean_tracked_worktree",
            '"--untracked-files=all"',
            "allowed_audit_prefix",
        ],
    )
    require_none(
        "scripts/run_native_ots_workflow_once.py",
        [
            "evaluate_daily_spend",
            "native_ots_bundle_archive",
            "record-chain/arweave-wallet-ledger.json",
            "ARWEAVE_JWK_PATH",
            "--enable-paid-upload",
            "--confirm-paid-upload",
            "arweave_cost_gate.mjs",
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
        require(
            forbidden not in retry,
            f"Native OTS metadata retry can repeat active lifecycle: {forbidden}",
        )

    # Weekly continuity publication embeds the mature proof bytes and is the
    # only automatic paid route.
    require_all(
        ".github/workflows/record-chain-arweave-archive.yml",
        [
            'cron: "17 7 * * 3"',
            "ARKEY",
            "arweave_runtime_spend_guard.mjs",
            "ARWEAVE_MINIMUM_REMAINING_AR",
            "Automated upstream event is dry-run only",
            "run_record_chain_arweave_workflow_once.py",
        ],
    )
    require_all(
        "scripts/record_chain_arweave_incremental.py",
        [
            "trinityaccord.weekly-continuity-bundle.v1",
            "trinityaccord.weekly-native-ots-evidence.v1",
            'latest.get("latest_anchor_file")',
            'latest.get("latest_anchored_file")',
            'latest.get("latest_ots_file")',
            "proof_files_embedded_in_this_payload",
            "content_base64",
        ],
    )

    # Former scheduled paid-repair workflow remains only a visibility scan.
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
            "record-chain/ots/native-arweave-bundles/",
            "record-chain/ots/native-arweave-registry.json",
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

    print(
        "PASS: Native OTS repair remains available; daily lifecycle persists "
        "no-cost proof state and weekly continuity archival owns paid publication"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
