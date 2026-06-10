#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def body(path: str) -> str:
    p = ROOT / path
    if not p.exists():
        raise SystemExit(f"missing required file: {path}")
    return p.read_text(encoding="utf-8")


def require_contains(path: str, needles: list[str]) -> None:
    text = body(path)
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise SystemExit(f"{path} missing required wallet wiring: {missing}")


def main() -> int:
    require_contains("scripts/arweave_upload_payload.mjs", [
        "upload_cost_winston",
        "upload_cost_ar",
        "wallet_balance_after_ar",
        "actual_delta_winston",
        "wallet_address_sha256",
    ])

    require_contains("scripts/arweave_cost_gate.mjs", [
        "actual_delta_winston",
        "actual_delta_ar",
        "estimated_upload_cost_winston",
        "estimated_upload_cost_ar",
        "balance_after_ar",
    ])

    require_contains("scripts/record_arweave_upload_result.py", [
        "PAID_RESULTS",
        "readback_failed",
        "append-upload",
        "set-balance",
    ])

    require_contains("scripts/build_record_chain_arweave_archive.py", [
        "record_arweave_upload_result.py",
        "record_chain_arweave_archive",
    ])

    require_contains("scripts/run_native_ots_upgrade_verify.py", [
        "record_arweave_upload_result.py",
        "native_ots_bundle_archive",
        "actual_delta_winston",
        "balance_after_ar",
    ])

    require_contains(".github/workflows/record-chain-data-arweave-archive.yml", [
        "record_arweave_upload_result.py",
        "record_chain_data_arweave_archive",
        "record-chain/arweave-wallet-ledger.json",
        "api/arweave-wallet-status.json",
    ])

    require_contains(".github/workflows/native-ots-upgrade-watch.yml", [
        "record-chain/arweave-wallet-ledger.json",
        "api/arweave-wallet-status.json",
        "generate_arweave_wallet_status.py",
    ])

    require_contains(".github/workflows/archive-backlog-repair.yml", [
        "record-chain/arweave-wallet-ledger.json",
        "api/arweave-wallet-status.json",
        "generate_arweave_wallet_status.py",
    ])

    print("PASS: paid upload wallet ledger wiring")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
