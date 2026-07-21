#!/usr/bin/env python3
"""Contract test for current Arweave upload/readback result handling.

The native workflow invokes the crash-safe archive runner; that runner wraps the
native archive builder and generic uploader. A paid transaction must be
checkpointed before readback, and retries must resume that exact transaction
instead of posting a duplicate. The frozen legacy data-registry updater is
retired and must reject live updates.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FIELDS = [
    "schema",
    "txid",
    "uploaded_at",
    "data_sha256",
    "payload_sha256",
    "readback_sha256",
    "hash_match",
    "wallet_address_sha256",
    "tags",
    "boundary",
]

BOUNDARY_FIELDS = {
    "arweave_archive_is_mirror_only": True,
    "arweave_archive_is_not_authority": True,
    "arweave_archive_is_not_attestation": True,
    "arweave_archive_is_not_amendment": True,
    "arweave_archive_is_not_successor_reception": True,
    "bitcoin_originals_prevail": True,
}


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def ok(message: str) -> None:
    print(f"PASS: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> int:
    uploader_path = ROOT / "scripts/arweave_upload_payload.mjs"
    require(uploader_path.exists(), "scripts/arweave_upload_payload.mjs not found")
    uploader = uploader_path.read_text(encoding="utf-8")

    for needle in [
        "readback_sha256",
        "hash_match",
        "ARWEAVE_READBACK",
        "getData",
        "posted_pending_readback",
        "readback_failed",
        "retryable",
        "ARWEAVE_POST_CHECKPOINT",
        "ARWEAVE_RESUME_READBACK",
        "ARWEAVE_READBACK_MAX_SECONDS",
        "Refusing to resume transaction",
    ]:
        require(needle in uploader, f"arweave_upload_payload.mjs missing: {needle}")
    ok("generic uploader checkpoints paid posts and supports bounded readback-only resume")

    for field in REQUIRED_FIELDS:
        require(
            f'"{field}"' in uploader
            or f"'{field}'" in uploader
            or f"{field}:" in uploader
            or f"{field} :" in uploader,
            f"arweave_upload_payload.mjs result missing field: {field}",
        )
    ok("generic uploader emits required result fields")

    for field in BOUNDARY_FIELDS:
        require(field in uploader, f"arweave_upload_payload.mjs boundary missing: {field}")
    ok("generic uploader carries immutable-authority boundaries")

    recorder_path = ROOT / "scripts/record_arweave_upload_result.py"
    require(recorder_path.exists(), "current wallet-ledger recorder missing")
    recorder = recorder_path.read_text(encoding="utf-8")
    for marker in [
        'pick(data, "tx_id", "txid", "arweave_tx_id")',
        '"uploaded"',
        '"readback_failed"',
        '"posted_pending_readback"',
        "update_arweave_wallet_ledger.py",
        '"append-upload"',
    ]:
        require(marker in recorder, f"current Arweave result recorder missing: {marker}")
    ok("current upload result recorder accounts for posted/readback-failed transactions")

    builder_path = ROOT / "scripts/build_record_chain_arweave_archive.py"
    require(builder_path.exists(), "current native archive builder missing")
    builder = builder_path.read_text(encoding="utf-8")
    for marker in [
        'uploader = ROOT / "scripts" / "arweave_upload_payload.mjs"',
        'result_path = archive_dir / "upload-result.json"',
        'return read_json(result_path)',
        'upload_result.get("hash_match") is True',
        'upload_result.get("result") == "uploaded"',
        '"scripts/record_arweave_upload_result.py"',
        "load_native_chain_sources",
        'CHAIN_ID = "trinity-accord-public-reception-ledger"',
    ]:
        require(marker in builder, f"current native archive builder missing: {marker}")
    ok("native builder wires generic uploader, readback result, and wallet accounting")

    runner_path = ROOT / "scripts/run_record_chain_arweave_archive.py"
    require(runner_path.exists(), "crash-safe native archive runner missing")
    runner = runner_path.read_text(encoding="utf-8")
    for marker in [
        "subprocess.TimeoutExpired",
        "builder.upload_to_arweave = guarded_upload",
        'partial["result"] = "readback_failed"',
        '"retry_readback"',
        "_find_incomplete_current_archive",
        "Resuming Arweave readback without a new paid post",
        "payload sha256 does not match",
    ]:
        require(marker in runner, f"crash-safe native archive runner missing: {marker}")
    ok("native runner persists timeout checkpoints and resumes only the matching tx/payload")

    current_workflow_path = ROOT / ".github/workflows/record-chain-arweave-archive.yml"
    require(current_workflow_path.exists(), "current native archive workflow missing")
    current_workflow = current_workflow_path.read_text(encoding="utf-8")
    for marker in [
        "run_record_chain_arweave_archive.py",
        "verify_record_chain_arweave_archive.py",
        "secrets.ARKEY",
        "group: main-write-lock",
        "ARWEAVE_UPLOAD_TIMEOUT_SECONDS",
        "ARWEAVE_READBACK_MAX_SECONDS",
        "checkpoint incomplete Arweave upload",
        "Fail after persisting incomplete upload checkpoint",
        "refusing a second paid upload during push retry",
    ]:
        require(marker in current_workflow, f"current native archive workflow missing: {marker}")
    ok("current native workflow persists repair state before reporting upload failure")

    retired_path = ROOT / "scripts/update_record_chain_data_arweave_registry.py"
    require(retired_path.exists(), "retired legacy registry updater missing")
    retired = retired_path.read_text(encoding="utf-8")
    require(
        "legacy record-chain data Arweave uploads are retired" in retired,
        "legacy registry updater must reject live updates",
    )
    require("would_write_registry" in retired, "legacy registry updater must disclose read-only preview")
    require("hash_match is not True" not in retired, "retired updater must not retain a dormant live-mode branch")
    require("write_json" not in retired, "retired updater must have no registry write helper")
    ok("legacy data registry updater is fail-closed and read-only")

    verifier_path = ROOT / "scripts/verify_record_chain_data_arweave_registry.py"
    verifier = verifier_path.read_text(encoding="utf-8")
    for marker in [
        "arweave_hash_match",
        "arweave_payload_sha256",
        "arweave_readback_sha256",
        "bundle_raw_file_sha256",
        "verify_bundle",
    ]:
        require(marker in verifier, f"historical evidence verifier missing: {marker}")
    ok("historical registry verifies readback evidence against local bundle bytes")

    print("\nAll Arweave upload/readback contract tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
