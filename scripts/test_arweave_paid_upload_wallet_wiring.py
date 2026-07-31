#!/usr/bin/env python3
"""Contract for delegated Arweave paid-upload wallet accounting boundaries.

The scheduled workflows authorize and invoke bounded orchestrators. The
orchestrators own complete metadata staging, failure checkpoints, and
metadata-only push retries. Low-level uploaders record every posted transaction,
including readback failures. The scheduled backlog scan and retired historical
surfaces have no paid or wallet-write capability.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def body(path: str) -> str:
    file = ROOT / path
    if not file.exists():
        raise SystemExit(f"missing required file: {path}")
    return file.read_text(encoding="utf-8")


def require_contains(path: str, needles: list[str]) -> None:
    text = body(path)
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise SystemExit(f"{path} missing required wallet wiring: {missing}")


def require_absent(path: str, needles: list[str]) -> None:
    text = body(path)
    present = [needle for needle in needles if needle in text]
    if present:
        raise SystemExit(f"{path} retains forbidden retired wallet capability: {present}")


def run_behavior(path: str, label: str) -> None:
    target = ROOT / path
    if not target.exists():
        raise SystemExit(f"{label} missing: {path}")
    result = subprocess.run(
        [sys.executable, str(target)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(f"{label} failed:\n" + (result.stderr or result.stdout)[-5000:])


def main() -> int:
    # Generic uploaders expose complete cost, transaction checkpoint, and
    # readback information consumed by the wallet ledger recorder.
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
        "scripts/arweave_cost_gate.mjs",
        [
            "actual_delta_winston",
            "actual_delta_ar",
            "estimated_upload_cost_winston",
            "estimated_upload_cost_ar",
            "balance_after_ar",
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

    # Record-Chain low-level path: incremental payload -> crash-safe runner ->
    # uploader/readback -> wallet recorder.
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

    # The workflow contains authorization/runtime boundaries; the orchestrator
    # contains wallet staging, checkpoints, verification, and metadata-only push.
    require_contains(
        ".github/workflows/record-chain-arweave-archive.yml",
        [
            "secrets.ARKEY",
            "run_record_chain_arweave_workflow_once.py",
            "arweave_runtime_spend_guard.mjs",
            "ARWEAVE_MINIMUM_REMAINING_AR",
            "group: main-write-lock",
            'cron: "17 7 * * *"',
        ],
    )
    require_absent(
        ".github/workflows/record-chain-arweave-archive.yml",
        ["run_record_chain_arweave_archive.py --mode"],
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
    rc_retry = body("scripts/run_record_chain_arweave_workflow_once.py").split(
        "def push_without_reupload", 1
    )[-1].split("def main", 1)[0]
    if "run_record_chain_arweave_incremental.py" in rc_retry:
        raise SystemExit("Record-Chain metadata retry can repeat a paid upload")

    # Native OTS lifecycle records every posted transaction. Its workflow only
    # invokes the bounded orchestrator; complete wallet/API staging lives there.
    require_contains(
        "scripts/run_native_ots_upgrade_verify.py",
        [
            "record_arweave_upload_result.py",
            "native_ots_bundle_archive",
            "actual_delta_winston",
            "balance_after_ar",
            "refresh_native_ots_backlog",
            "check=True",
        ],
    )
    require_contains(
        ".github/workflows/native-ots-upgrade-watch.yml",
        [
            "run_native_ots_workflow_once.py",
            "arweave_runtime_spend_guard.mjs",
            "ARWEAVE_MINIMUM_REMAINING_AR",
            "group: main-write-lock",
            'cron: "42 6 * * *"',
        ],
    )
    require_absent(
        ".github/workflows/native-ots-upgrade-watch.yml",
        ["git push origin HEAD:main", "--enable-paid-upload"],
    )
    require_contains(
        "scripts/run_native_ots_workflow_once.py",
        [
            "record-chain/arweave-wallet-ledger.json",
            "api/arweave-wallet-status.json",
            "scripts/reconcile_native_ots_generated_state.py",
            "evaluate_daily_spend",
            "push_metadata_only",
            "The OTS upgrade and Arweave uploader will not run again",
        ],
    )
    native_retry = body("scripts/run_native_ots_workflow_once.py").split(
        "def push_metadata_only", 1
    )[-1].split("def main", 1)[0]
    for forbidden in [
        "run_native_ots_upgrade_verify.py",
        "--enable-paid-upload",
        "--confirm-paid-upload",
    ]:
        if forbidden in native_retry:
            raise SystemExit(f"Native OTS metadata retry can repeat active operation: {forbidden}")

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

    # The former paid backlog repair path is now a read-only daily scan.
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
            "api/arweave-wallet-status.json",
            "git push",
            "contents: write",
        ],
    )

    # Retired historical upload surfaces remain incapable of paid writes.
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
                "api/arweave-wallet-status.json",
                "generate_arweave_wallet_status.py",
                "contents: write",
                "git push",
            ],
        )

    updater = body("scripts/update_record_chain_data_arweave_registry.py")
    if "legacy record-chain data Arweave uploads are retired" not in updater:
        raise SystemExit("legacy data updater must explicitly reject paid/live updates")
    if "write_json" in updater:
        raise SystemExit("legacy data updater retains a historical registry write helper")

    run_behavior(
        "scripts/test_archive_backlog_dry_run_behavior.py",
        "archive backlog dry-run behavioral regression",
    )
    run_behavior(
        "scripts/test_native_ots_transaction_behavior.py",
        "Native OTS transaction behavioral regression",
    )

    print(
        "PASS: delegated active paid paths account for wallet spend; metadata retries cannot repay; "
        "the backlog scan and retired paths have no wallet capability"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
