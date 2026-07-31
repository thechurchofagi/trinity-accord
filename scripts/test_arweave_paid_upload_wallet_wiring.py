#!/usr/bin/env python3
"""Contract for the single active weekly Arweave wallet boundary.

Only the weekly Record-Chain continuity workflow may authorize a paid post. Its
low-level uploader records every posted transaction, including delayed readback
states. Daily Native OTS, daily heartbeat, backlog scanning, and retired legacy
surfaces have no wallet capability.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def body(path: str) -> str:
    target = ROOT / path
    if not target.exists():
        raise SystemExit(f"missing required file: {path}")
    return target.read_text(encoding="utf-8")


def require_contains(path: str, needles: list[str]) -> None:
    text = body(path)
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise SystemExit(f"{path} missing required wallet wiring: {missing}")


def require_absent(path: str, needles: list[str]) -> None:
    text = body(path)
    present = [needle for needle in needles if needle in text]
    if present:
        raise SystemExit(f"{path} retains forbidden wallet capability: {present}")


def run_behavior(path: str, label: str) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(f"{label} failed:\n" + (result.stderr or result.stdout)[-5000:])


def main() -> int:
    require_contains(
        "scripts/arweave_upload_payload.mjs",
        [
            "upload_cost_winston",
            "upload_cost_ar",
            "wallet_balance_after_ar",
            "actual_delta_winston",
            "wallet_address_sha256",
            "posted_pending_readback",
            "ARWEAVE_RESUME_READBACK",
        ],
    )
    require_contains(
        "scripts/record_arweave_upload_result.py",
        [
            "PAID_RESULTS",
            "readback_failed",
            "posted_pending_readback",
            "append-upload",
            "set-balance",
        ],
    )

    require_contains(
        "scripts/build_record_chain_arweave_archive.py",
        [
            "record_arweave_upload_result.py",
            "record_chain_arweave_archive",
            "arweave_upload_payload.mjs",
            "upload-result.json",
        ],
    )
    require_contains(
        "scripts/run_record_chain_arweave_archive.py",
        [
            "import build_record_chain_arweave_archive as builder",
            "builder.build_archive_manifest",
            "builder.record_wallet_upload",
            "builder.upload_to_arweave = guarded_upload",
            "Resuming Arweave readback without a new paid post",
        ],
    )
    require_contains(
        "scripts/run_record_chain_arweave_incremental.py",
        [
            "import run_record_chain_arweave_archive as runner",
            "build_incremental_payload_json",
            "runner.builder.build_payload_json = build_incremental_payload_json",
            "evaluate_daily_spend",
            "runner.main()",
        ],
    )
    require_contains(
        "scripts/record_chain_arweave_incremental.py",
        [
            "trinityaccord.weekly-continuity-bundle.v1",
            "trinityaccord.weekly-heartbeat-summary.v1",
            "trinityaccord.weekly-native-ots-evidence.v1",
            "proof_files_embedded_in_this_payload",
        ],
    )

    require_contains(
        ".github/workflows/record-chain-arweave-archive.yml",
        [
            "secrets.ARKEY",
            "run_record_chain_arweave_workflow_once.py",
            "arweave_runtime_spend_guard.mjs",
            "ARWEAVE_MINIMUM_REMAINING_AR",
            "group: main-write-lock",
            "queue: max",
            'cron: "17 7 * * 3"',
            "Automated upstream event is dry-run only",
        ],
    )
    require_absent(
        ".github/workflows/record-chain-arweave-archive.yml",
        ['cron: "17 7 * * *"', "run_record_chain_arweave_archive.py --mode"],
    )
    require_contains(
        "scripts/run_record_chain_arweave_workflow_once.py",
        [
            "record-chain/arweave-wallet-ledger.json",
            "api/arweave-wallet-status.json",
            "checkpoint incomplete Arweave upload for safe readback resume",
            "Fail after persisting incomplete upload checkpoint",
            "verify_record_chain_arweave_archive.py",
            "push_without_reupload",
            "The Arweave uploader will not run again",
        ],
    )
    retry = body("scripts/run_record_chain_arweave_workflow_once.py").split(
        "def push_without_reupload", 1
    )[-1].split("def main", 1)[0]
    if "run_record_chain_arweave_incremental.py" in retry:
        raise SystemExit("Record-Chain metadata retry can repeat a paid upload")

    # Daily Native OTS may upgrade and verify local evidence, but cannot spend.
    require_contains(
        ".github/workflows/native-ots-upgrade-watch.yml",
        [
            "run_native_ots_workflow_once.py",
            "group: main-write-lock",
            'cron: "42 6 * * *"',
            "verify_only",
            "upgrade_only",
        ],
    )
    require_absent(
        ".github/workflows/native-ots-upgrade-watch.yml",
        [
            "ARKEY",
            "ARWEAVE_JWK",
            "arweave_runtime_spend_guard.mjs",
            "ARWEAVE_MINIMUM_REMAINING_AR",
            "--enable-paid-upload",
        ],
    )
    require_contains(
        "scripts/run_native_ots_workflow_once.py",
        [
            "scripts/run_native_ots_upgrade_verify.py",
            "scripts/reconcile_native_ots_generated_state.py",
            "push_metadata_only",
            '{"verify_only", "upgrade_only"}',
        ],
    )
    require_absent(
        "scripts/run_native_ots_workflow_once.py",
        [
            "evaluate_daily_spend",
            "ARWEAVE_JWK_PATH",
            "--enable-paid-upload",
            "--confirm-paid-upload",
            "record-chain/arweave-wallet-ledger.json",
        ],
    )
    native_retry = body("scripts/run_native_ots_workflow_once.py").split(
        "def push_metadata_only", 1
    )[-1].split("def main", 1)[0]
    if "run_native_ots_upgrade_verify.py" in native_retry:
        raise SystemExit("Native OTS metadata retry can repeat local lifecycle work")

    # Standalone heartbeat publication is retired and cannot spend.
    require_contains(
        ".github/workflows/waiting-heartbeat-capsule.yml",
        ["Retired", "contents: read", "No wallet secret is available"],
    )
    require_absent(
        ".github/workflows/waiting-heartbeat-capsule.yml",
        ["schedule:", "workflow_run:", "ARKEY", "arweave_upload_waiting_heartbeat_capsule"],
    )

    require_contains(
        "scripts/reconcile_native_ots_generated_state.py",
        [
            "scripts/generate_arweave_wallet_status.py",
            "scripts/detect_archive_backlog.py",
            '"paid_upload_performed": False',
            '"ots_upgrade_performed": False',
            "validate_native_registry",
        ],
    )
    require_absent(
        "scripts/reconcile_native_ots_generated_state.py",
        ["arweave_upload_payload.mjs", "arweave_cost_gate.mjs", "--enable-paid-upload"],
    )

    require_contains(
        ".github/workflows/archive-backlog-repair.yml",
        [
            "contents: read",
            "--kind record_chain_arweave",
            "--kind native_ots_bundle",
            "--mode dry-run",
            "This scheduled workflow never uploads to Arweave",
        ],
    )
    require_absent(
        ".github/workflows/archive-backlog-repair.yml",
        [
            "--mode live",
            "--enable-paid-upload",
            "secrets.ARKEY",
            "vars.ARKEY",
            "ARWEAVE_JWK",
            "record-chain/arweave-wallet-ledger.json",
            "git push",
            "contents: write",
        ],
    )

    for path in [
        ".github/workflows/record-chain-data-arweave-archive.yml",
        ".github/workflows/phase5-ots-arweave-paid-upload.yml",
        ".github/workflows/paid-echo-arweave-canary.yml",
    ]:
        require_absent(
            path,
            [
                "secrets.ARKEY",
                "record_arweave_upload_result.py",
                "record-chain/arweave-wallet-ledger.json",
                "contents: write",
                "git push",
            ],
        )

    updater = body("scripts/update_record_chain_data_arweave_registry.py")
    if "legacy record-chain data Arweave uploads are retired" not in updater or "write_json" in updater:
        raise SystemExit("legacy data updater must remain fail-closed and read-only")

    run_behavior(
        "scripts/test_archive_backlog_dry_run_behavior.py",
        "archive backlog dry-run behavioral regression",
    )

    print(
        "PASS: one weekly continuity route owns wallet spend; daily heartbeat/OTS, "
        "backlog scanning, metadata retries, and retired paths cannot repay"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
