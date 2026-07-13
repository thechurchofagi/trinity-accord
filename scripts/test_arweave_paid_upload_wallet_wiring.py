#!/usr/bin/env python3
"""Contract for Arweave paid-upload wallet accounting boundaries.

Active native upload paths must account for posted transactions, including
readback failures. Retired historical/Phase-5 paths must not access wallets,
write the wallet ledger, or regenerate public wallet status. Archive backlog
preview mode must remain strictly read-only. Native OTS post-rebase wallet
status may be generated through the derived-only reconciler rather than being
inlined in the workflow YAML.
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
    require_contains(
        "scripts/arweave_upload_payload.mjs",
        [
            "upload_cost_winston",
            "upload_cost_ar",
            "wallet_balance_after_ar",
            "actual_delta_winston",
            "wallet_address_sha256",
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

    # Current native Record-Chain archive owns the active Record-Chain paid path.
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
        ".github/workflows/record-chain-arweave-archive.yml",
        [
            "secrets.ARKEY",
            "build_record_chain_arweave_archive.py",
            "record-chain/arweave-wallet-ledger.json",
            "group: main-write-lock",
        ],
    )

    # Native OTS upload remains active in the runner and records every posted
    # transaction before the workflow reconciles wallet/API projections.
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
            "record-chain/arweave-wallet-ledger.json",
            "api/arweave-wallet-status.json",
            "scripts/reconcile_native_ots_generated_state.py",
            "group: main-write-lock",
            "git push origin HEAD:main",
        ],
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
        [
            "arweave_upload_payload.mjs",
            "arweave_cost_gate.mjs",
            "--enable-paid-upload",
        ],
    )

    require_contains(
        ".github/workflows/archive-backlog-repair.yml",
        [
            "record-chain/arweave-wallet-ledger.json",
            "api/arweave-wallet-status.json",
            "generate_arweave_wallet_status.py",
            "--kind record_chain_arweave",
            "--kind native_ots_bundle",
            "--mode live",
            "git push origin HEAD:main",
        ],
    )

    # Retired historical upload surfaces must not touch wallet or public status.
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
        "PASS: active paid paths account for wallet spend; retired paths have no wallet capability; "
        "backlog dry-run is read-only; Native OTS derived wallet state is reconciled safely"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
