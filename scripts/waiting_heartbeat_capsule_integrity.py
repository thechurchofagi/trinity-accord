#!/usr/bin/env python3
"""Cross-artifact integrity checks for verified Waiting Heartbeat capsules."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

VERIFIED_CAPSULE_STATUSES = {"uploaded", "success", "arweave_archived"}
_HEARTBEAT_ID_RE = re.compile(r"hwb-[0-9]{8}")
_RECORD_ID_RE = re.compile(r"R-[0-9]{9}")
_SHA256_RE = re.compile(r"[a-f0-9]{64}")
_ARWEAVE_TXID_RE = re.compile(r"[A-Za-z0-9_-]{43}")


def capsule_txid(result: dict[str, Any] | None) -> str | None:
    if not result:
        return None
    value = result.get("arweave_txid") or result.get("arweave_tx_id") or result.get("txid") or result.get("tx_id")
    return value if isinstance(value, str) and value else None


def capsule_status(result: dict[str, Any] | None) -> str | None:
    if not result:
        return None
    value = result.get("status") or result.get("result")
    return value if isinstance(value, str) else None


def capsule_claims_verified(result: dict[str, Any] | None) -> bool:
    return bool(
        result
        and result.get("hash_match") is True
        and capsule_status(result) in VERIFIED_CAPSULE_STATUSES
        and capsule_txid(result)
    )


def verified_capsule_binding_errors(
    result: dict[str, Any] | None,
    *,
    capsule_path: Path,
    repository_root: Path,
) -> list[str]:
    """Return binding errors for a result that claims successful verification.

    The Arweave readback result is evidence only when it binds to the exact local
    capsule bytes and that capsule, in turn, binds to the immutable heartbeat
    record stored in this repository.
    """
    errors: list[str] = []
    if not capsule_claims_verified(result):
        return ["upload result does not claim a verified capsule"]
    assert result is not None

    if result.get("schema") != "trinityaccord.waiting-heartbeat-arweave-upload-result.v1":
        errors.append("upload result schema mismatch")

    heartbeat_id = result.get("heartbeat_id")
    if not isinstance(heartbeat_id, str) or _HEARTBEAT_ID_RE.fullmatch(heartbeat_id) is None:
        errors.append("upload result heartbeat_id is invalid")
    elif capsule_path.name != f"{heartbeat_id}.capsule.json":
        errors.append("upload result heartbeat_id/capsule filename mismatch")

    txid = capsule_txid(result)
    if not isinstance(txid, str) or _ARWEAVE_TXID_RE.fullmatch(txid) is None:
        errors.append("Arweave transaction id is invalid")

    if not capsule_path.is_file():
        errors.append("local capsule payload is missing")
        return errors

    payload_bytes = capsule_path.read_bytes()
    payload_sha = hashlib.sha256(payload_bytes).hexdigest()
    for field in ("payload_sha256", "data_sha256", "readback_sha256"):
        value = result.get(field)
        if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
            errors.append(f"{field} is missing or invalid")
        elif value != payload_sha:
            errors.append(f"{field} does not match local capsule bytes")

    try:
        capsule = json.loads(payload_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"local capsule is not valid UTF-8 JSON: {exc}")
        return errors
    if not isinstance(capsule, dict):
        errors.append("local capsule is not a JSON object")
        return errors
    if capsule.get("schema") != "trinityaccord.waiting-heartbeat-arweave-capsule.v1":
        errors.append("capsule schema mismatch")
    if capsule.get("heartbeat_id") != heartbeat_id:
        errors.append("capsule heartbeat_id does not match upload result")

    record_ref = capsule.get("heartbeat_record")
    if not isinstance(record_ref, dict):
        errors.append("capsule heartbeat_record is missing")
        return errors
    record_id = record_ref.get("record_id")
    if not isinstance(record_id, str) or _RECORD_ID_RE.fullmatch(record_id) is None:
        errors.append("capsule heartbeat_record.record_id is invalid")
        return errors
    expected_record_rel = f"record-chain/records/{record_id}.json"
    if record_ref.get("path") != expected_record_rel:
        errors.append("capsule heartbeat record path mismatch")
    record_path = repository_root / expected_record_rel
    if not record_path.is_file():
        errors.append("capsule heartbeat final record is missing")
        return errors
    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"capsule heartbeat final record is invalid JSON: {exc}")
        return errors
    if not isinstance(record, dict):
        errors.append("capsule heartbeat final record is not an object")
        return errors
    for field in ("record_id", "record_index", "record_sha256", "record_type", "assigned_at"):
        if record_ref.get(field) != record.get(field):
            errors.append(f"capsule heartbeat_record.{field} mismatch")
    heartbeat = record.get("system_waiting_heartbeat")
    if not isinstance(heartbeat, dict) or heartbeat.get("heartbeat_id") != heartbeat_id:
        errors.append("capsule heartbeat_id is not bound to the referenced final record")
    return errors


def verified_capsule_is_bound(
    result: dict[str, Any] | None,
    *,
    capsule_path: Path,
    repository_root: Path,
) -> bool:
    return capsule_claims_verified(result) and not verified_capsule_binding_errors(
        result,
        capsule_path=capsule_path,
        repository_root=repository_root,
    )
