#!/usr/bin/env python3
"""Run the native record-chain Arweave archive with crash-safe resume handling.

This orchestration layer closes two failure gaps around paid uploads:

1. A hard subprocess timeout is converted into a persisted readback-failed
   checkpoint when the uploader has already returned a transaction id.
2. A later run resumes readback for that exact transaction and payload instead
   of posting a second paid transaction.

The underlying archive builder remains the source of manifest construction and
verification semantics. This runner only adds transaction checkpoint/recovery
behavior around its uploader call.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import build_record_chain_arweave_archive as builder


_ORIGINAL_UPLOAD = builder.upload_to_arweave


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _stream_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _timeout_seconds() -> int:
    raw = os.environ.get("ARWEAVE_UPLOAD_TIMEOUT_SECONDS", "600")
    try:
        value = int(raw)
    except ValueError as exc:
        raise SystemExit("ARWEAVE_UPLOAD_TIMEOUT_SECONDS must be an integer") from exc
    if value < 60:
        raise SystemExit("ARWEAVE_UPLOAD_TIMEOUT_SECONDS must be at least 60 seconds")
    return value


def _result_path(archive_dir: Path) -> Path:
    return archive_dir / "upload-result.json"


def _load_partial_result(archive_dir: Path) -> dict[str, Any]:
    path = _result_path(archive_dir)
    if not path.exists():
        return {}
    try:
        data = _read_json(path)
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def guarded_upload(payload_path: Path, archive_dir: Path) -> dict[str, Any]:
    """Invoke the existing uploader and preserve a posted tx on hard timeout."""
    try:
        return _ORIGINAL_UPLOAD(payload_path, archive_dir)
    except subprocess.TimeoutExpired as exc:
        limit = _timeout_seconds()
        partial = _load_partial_result(archive_dir)
        txid = partial.get("txid") or partial.get("tx_id")
        detail_parts = [
            f"Arweave uploader exceeded the {limit}s safety timeout",
        ]
        stdout = _stream_text(exc.stdout).strip()
        stderr = _stream_text(exc.stderr).strip()
        if stdout:
            detail_parts.append(f"stdout={stdout[-2000:]}")
        if stderr:
            detail_parts.append(f"stderr={stderr[-2000:]}")
        detail = "; ".join(detail_parts)

        if txid:
            # The paid post is already checkpointed. Convert the state into the
            # builder's existing repair status so the workflow can commit it.
            partial["result"] = "readback_failed"
            partial["retryable"] = True
            partial["hash_match"] = False
            partial["timeout_seconds"] = limit
            partial["last_error"] = detail
            _write_json(_result_path(archive_dir), partial)
            raise SystemExit(
                f"{detail}; transaction {txid} was posted and checkpointed; "
                "a later run must resume readback without re-uploading"
            ) from exc

        raise SystemExit(
            f"{detail}; no transaction checkpoint was written, so no paid upload is assumed"
        ) from exc


def _matches_current_head(manifest: dict[str, Any], tip: dict[str, Any]) -> bool:
    source = manifest.get("source", {})
    native = source.get("native_chain", {}) if isinstance(source, dict) else {}
    return (
        native.get("latest_record_id") == tip.get("latest_record_id")
        and native.get("latest_record_sha256") == tip.get("latest_record_sha256")
        and native.get("native_record_count") == tip.get("native_record_count")
    )


def _find_incomplete_current_archive() -> tuple[Path, dict[str, Any]] | None:
    tip = builder.read_json(builder.CHAIN / "chain-tip.json")
    candidates: list[tuple[str, Path, dict[str, Any]]] = []

    for manifest_path in sorted(builder.ARCHIVES.glob("*/manifest.json")):
        manifest = builder.read_json(manifest_path)
        if not _matches_current_head(manifest, tip):
            continue
        arweave = manifest.get("arweave", {})
        txid = arweave.get("txid") or arweave.get("tx_id")
        complete = (
            arweave.get("archive_status") == "archived"
            and arweave.get("verified") is True
            and arweave.get("hash_match") is True
        )
        if txid and not complete:
            sort_key = str(arweave.get("last_attempt_at") or manifest.get("created_at") or "")
            candidates.append((sort_key, manifest_path, manifest))

    if not candidates:
        return None
    _sort_key, manifest_path, manifest = sorted(candidates, key=lambda item: item[0])[-1]
    return manifest_path, manifest


def _payload_path(manifest_path: Path, manifest: dict[str, Any]) -> Path:
    payload = manifest.get("payload", {})
    configured = payload.get("path") if isinstance(payload, dict) else None
    path = builder.ROOT / configured if isinstance(configured, str) and configured else manifest_path.parent / "payload.json"
    if not path.exists():
        raise SystemExit(f"cannot resume Arweave readback: payload missing: {path}")

    expected_sha = payload.get("sha256") if isinstance(payload, dict) else None
    actual_sha = builder.sha256_file(path)
    if expected_sha and actual_sha != expected_sha:
        raise SystemExit(
            "cannot resume Arweave readback: local payload sha256 does not match the committed manifest"
        )
    return path


def _ensure_resume_result(
    manifest_path: Path,
    manifest: dict[str, Any],
    payload_path: Path,
) -> Path:
    result_path = _result_path(manifest_path.parent)
    arweave = manifest.get("arweave", {})
    txid = arweave.get("txid") or arweave.get("tx_id")
    payload_sha = builder.sha256_file(payload_path)

    if result_path.exists():
        result = _read_json(result_path)
        result_txid = result.get("txid") or result.get("tx_id")
        result_sha = result.get("payload_sha256") or result.get("data_sha256")
        if result_txid != txid:
            raise SystemExit("cannot resume Arweave readback: manifest/result transaction ids differ")
        if result_sha != payload_sha:
            raise SystemExit("cannot resume Arweave readback: manifest/result payload hashes differ")
        return result_path

    # Older failure metadata may contain the txid but not the uploader checkpoint.
    # Reconstruct only the minimum immutable resume record; no spend is invented.
    _write_json(
        result_path,
        {
            "schema": "trinityaccord.arweave-upload-result.v1",
            "result": "posted_pending_readback",
            "txid": txid,
            "tx_id": txid,
            "uploaded_at": arweave.get("uploaded_at"),
            "data_sha256": payload_sha,
            "payload_sha256": payload_sha,
            "readback_sha256": arweave.get("readback_sha256"),
            "hash_match": False,
            "retryable": True,
            "wallet_address_sha256": arweave.get("wallet_address_sha256"),
            "tags": {},
            "boundary": {
                "arweave_archive_is_mirror_only": True,
                "arweave_archive_is_not_authority": True,
                "arweave_archive_is_not_attestation": True,
                "arweave_archive_is_not_amendment": True,
                "arweave_archive_is_not_successor_reception": True,
                "bitcoin_originals_prevail": True,
            },
        },
    )
    return result_path


def _apply_result(
    manifest_path: Path,
    manifest: dict[str, Any],
    result: dict[str, Any],
    *,
    error: str | None,
) -> str:
    status = builder.archive_status_from_upload(result)
    if result.get("result") == "posted_pending_readback":
        status = "readback_failed"

    previous = manifest.get("arweave", {})
    retry_count = int(previous.get("retry_count") or 0)
    if status != "archived":
        retry_count += 1

    txid = result.get("txid") or result.get("tx_id")
    manifest["mode"] = "live"
    manifest["arweave"] = {
        "enabled": True,
        "upload_mode": "live",
        "txid": txid,
        "wallet_address_sha256": result.get("wallet_address_sha256") or previous.get("wallet_address_sha256"),
        "uploaded_at": result.get("uploaded_at") or previous.get("uploaded_at"),
        "verified": status == "archived",
        "hash_match": result.get("hash_match") is True,
        "readback_sha256": result.get("readback_sha256"),
        "archive_status": status,
        "retry_count": retry_count,
        "last_attempt_at": builder.utc_now(),
        "last_error": None if status == "archived" else (error or result.get("last_error") or result.get("result")),
        "next_action": "no_op" if status == "archived" else "retry_readback",
    }
    manifest["archive_manifest_sha256"] = None
    manifest["archive_manifest_sha256"] = builder.sha256_canonical_json(manifest)
    builder.write_json(manifest_path, manifest)

    result_path = _result_path(manifest_path.parent)
    if txid and result_path.exists():
        builder.record_wallet_upload(result_path, _payload_path(manifest_path, manifest))

    builder.update_arweave_index()
    builder.refresh_archive_backlog()
    return status


def _resume_current_archive(manifest_path: Path, manifest: dict[str, Any]) -> None:
    payload_path = _payload_path(manifest_path, manifest)
    result_path = _ensure_resume_result(manifest_path, manifest, payload_path)
    txid = manifest.get("arweave", {}).get("txid") or manifest.get("arweave", {}).get("tx_id")
    print(f"Resuming Arweave readback without a new paid post: txid={txid}")

    try:
        result = guarded_upload(payload_path, manifest_path.parent)
    except SystemExit as exc:
        partial = _load_partial_result(manifest_path.parent)
        if partial:
            _apply_result(manifest_path, manifest, partial, error=str(exc))
        raise

    status = _apply_result(manifest_path, manifest, result, error=None)
    if status != "archived":
        raise SystemExit(1)
    print(f"Arweave readback resume completed: txid={txid}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run record-chain Arweave archive with safe resume")
    parser.add_argument("--mode", choices=["dry-run", "live", "verify-only"], default="dry-run")
    args = parser.parse_args()

    if args.mode == "verify-only":
        print("Use verify_record_chain_arweave_archive.py for verification.")
        return 0

    # Convert hard timeouts into the builder's existing SystemExit repair path.
    builder.upload_to_arweave = guarded_upload

    if args.mode == "live":
        incomplete = _find_incomplete_current_archive()
        if incomplete is not None:
            _resume_current_archive(*incomplete)
            return 0

    builder.build_archive_manifest(mode=args.mode)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
