#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

PAID_RESULTS = {
    "uploaded",
    "readback_failed",
    "posted_pending_readback",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_index_digest(value: dict[str, Any]) -> str:
    canonical = dict(value)
    canonical.pop("source_digest", None)
    raw = json.dumps(
        canonical,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def pick(data: dict[str, Any], *names: str, skip_zero: bool = False) -> Any:
    for name in names:
        value = data.get(name)
        if value in (None, ""):
            continue
        if skip_zero and str(value) in ("0", "0.0", "0.000000000000"):
            continue
        return value
    return None


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


def sync_current_baseline_trusted_release(data: dict[str, Any]) -> None:
    """Stage the new DOI as latest trusted only after DOI restore and AR readback."""
    if data.get("result") != "uploaded" or data.get("hash_match") is not True:
        raise SystemExit("homepage snapshot cannot update trusted release before verified readback")
    work_path = ROOT / "preservation/current-baseline-publish-work.json"
    index_path = ROOT / "api/recovery-index.json"
    runner_temp = os.environ.get("RUNNER_TEMP")
    if not runner_temp:
        raise SystemExit("RUNNER_TEMP is required to verify current-baseline public restore")
    recovery_path = Path(runner_temp) / "public-restored/recovery-report.json"
    if not work_path.is_file() or not recovery_path.is_file():
        raise SystemExit("current-baseline publication proof inputs are missing")

    published = read_json(work_path)
    recovery = read_json(recovery_path)
    index = read_json(index_path)
    source = published.get("latest_git_commit_sha")
    doi = published.get("latest_doi")
    concept = published.get("concept_doi") or published.get("core_concept_doi")
    package = published.get("latest_package_identity_sha256")
    if published.get("publication_status") != "published":
        raise SystemExit("current-baseline Zenodo state is not published")
    if published.get("public_metadata_verification") != "passed":
        raise SystemExit("current-baseline Zenodo metadata verification did not pass")
    if data.get("source_git_commit_sha") != source:
        raise SystemExit("homepage snapshot source does not match published DOI source")
    if data.get("repository_version_doi") != doi:
        raise SystemExit("homepage snapshot DOI binding does not match published version")
    if data.get("payload_sha256") != data.get("readback_sha256"):
        raise SystemExit("homepage snapshot Arweave readback digest mismatch")
    if recovery.get("result") != "pass" or recovery.get("source_git_commit_sha") != source:
        raise SystemExit("public DOI-only recovery does not match published source")
    if concept != "10.5281/zenodo.21739343":
        raise SystemExit("current-baseline concept DOI mismatch")

    trusted = index.setdefault("latest_trusted_release", {})
    if not isinstance(trusted, dict):
        raise SystemExit("recovery index latest trusted release is invalid")
    trusted["status"] = "published_and_publicly_restored"
    trusted["repository_preservation"] = {
        "doi": doi,
        "record_id": published.get("latest_record_id"),
        "concept_doi": concept,
        "git_commit_sha": source,
        "git_tree_oid": published.get("latest_git_tree_oid"),
        "package_identity_sha256": package,
        "github_required_for_recovery": False,
        "github_required_for_discovery": False,
        "public_metadata_verification": "passed",
        "public_cold_restore": "passed",
        "coverage_status": "exact_published_baseline",
        "live_main_equivalence_claimed": False,
        "recovery_catalog": "preservation/recovery-catalog.json",
        "current_state": "preservation/repository-preservation-state-v2.json",
    }
    index["source_digest"] = canonical_index_digest(index)
    write_json(index_path, index)


def main() -> int:
    parser = argparse.ArgumentParser(description="Record Arweave upload result into AR wallet ledger")
    parser.add_argument("--upload-result-json", required=True)
    parser.add_argument("--kind", required=True)
    parser.add_argument("--source-path")
    parser.add_argument("--note")
    parser.add_argument("--skip-balance", action="store_true")
    args = parser.parse_args()

    upload_path = Path(args.upload_result_json)
    if not upload_path.is_absolute():
        upload_path = ROOT / upload_path
    if not upload_path.exists():
        raise SystemExit(f"upload result missing: {upload_path}")

    data = read_json(upload_path)

    result = data.get("result")
    tx_id = pick(data, "tx_id", "txid", "arweave_tx_id")
    if not tx_id:
        print("No tx id in upload result; wallet ledger not updated.")
        return 0

    paid_at = pick(data, "uploaded_at", "generated_at")
    wallet_address = pick(data, "wallet_address")
    wallet_hash = pick(data, "wallet_address_sha256")
    if wallet_address and not wallet_hash:
        wallet_hash = sha256_text(wallet_address)

    # Preferred cost order:
    # 1. actual balance delta (non-zero only — zero means balance check raced with on-chain confirmation)
    # 2. tx.reward / direct upload cost
    # 3. cost gate estimate
    winston = pick(
        data,
        "actual_delta_winston",
        "upload_cost_winston",
        "estimated_upload_cost_winston",
        "estimated_cost_winston",
        skip_zero=True,
    )
    amount_ar = pick(
        data,
        "actual_delta_ar",
        "upload_cost_ar",
        "estimated_upload_cost_ar",
        "estimated_cost_ar",
        skip_zero=True,
    )

    # If tx_id exists and result indicates the tx was posted/uploaded, count it as paid.
    # This includes readback_failed: the archive may need repair, but the wallet may already have paid.
    status = "paid" if result in PAID_RESULTS or winston or amount_ar else "unknown"

    # Use the --option=value form because base64url Arweave transaction IDs may
    # legally begin with "-". Passing such an ID as the next argv token makes
    # argparse mistake it for another option and reject the command.
    append_cmd = [
        sys.executable,
        "scripts/update_arweave_wallet_ledger.py",
        "append-upload",
        f"--tx-id={tx_id}",
        "--kind",
        args.kind,
        "--status",
        status,
    ]
    if args.source_path:
        append_cmd += ["--source-path", args.source_path]
    if winston:
        append_cmd += ["--winston", str(winston)]
    elif amount_ar:
        append_cmd += ["--amount-ar", str(amount_ar)]
    if paid_at:
        append_cmd += ["--paid-at", str(paid_at)]
    note = args.note or f"recorded from {upload_path}"
    append_cmd += ["--note", note]
    run(append_cmd)

    if not args.skip_balance:
        balance_ar = pick(data, "balance_after_ar", "wallet_balance_after_ar")
        if balance_ar:
            balance_cmd = [
                sys.executable,
                "scripts/update_arweave_wallet_ledger.py",
                "set-balance",
                "--balance-ar",
                str(balance_ar),
            ]
            if wallet_hash:
                balance_cmd += ["--wallet-address-sha256", str(wallet_hash)]
            if paid_at:
                balance_cmd += ["--balance-at", str(paid_at)]
            run(balance_cmd)
        elif wallet_hash:
            print("Wallet hash is available, but balance_after_ar is unavailable; balance remains unchanged.")

    if args.kind == "homepage_machine_snapshot":
        sync_current_baseline_trusted_release(data)

    print(f"Recorded Arweave upload result into wallet ledger: tx_id={tx_id} status={status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
