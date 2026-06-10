from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RC_BACKLOG = ROOT / "record-chain/arweave-backlog.json"
API_RC_BACKLOG = ROOT / "api/record-chain-arweave-backlog.json"
OTS_BACKLOG = ROOT / "record-chain/ots/native-ots-backlog.json"
API_OTS_BACKLOG = ROOT / "api/record-chain-native-ots-backlog.json"

RC_SCHEMA = "trinityaccord.record-chain-arweave-backlog.v1"
OTS_SCHEMA = "trinityaccord.native-ots-backlog.v1"

RC_BOUNDARY = {
    "arweave_archive_is_mirror_only": True,
    "arweave_archive_is_not_authority": True,
    "arweave_archive_is_not_attestation": True,
    "arweave_archive_is_not_amendment": True,
    "arweave_archive_is_not_successor_reception": True,
    "bitcoin_originals_prevail": True,
}

OTS_BOUNDARY = {
    "native_ots_proof_bundle_arweave_archive_is_mirror_only": True,
    "native_ots_proof_bundle_arweave_archive_is_not_authority": True,
    "native_ots_proof_bundle_arweave_archive_is_not_attestation": True,
    "native_ots_proof_bundle_arweave_archive_is_not_amendment": True,
    "native_ots_proof_bundle_arweave_archive_is_not_successor_reception": True,
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def dump_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=False, ensure_ascii=False, allow_nan=False) + "\n"


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json_if_changed(path: Path, data: Any) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = dump_json(data)
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def item_key(parts: list[Any]) -> str:
    return sha256_text("|".join(str(part or "") for part in parts))


def existing_attempts(path: Path) -> dict[str, dict[str, Any]]:
    data = read_json(path, {"items": []})
    return {item.get("key", ""): item for item in data.get("items", []) if isinstance(item, dict)}


def attempt_fields(previous: dict[str, Any] | None = None) -> dict[str, Any]:
    previous = previous or {}
    return {
        "retry_count": previous.get("retry_count", 0),
        "last_attempt_at": previous.get("last_attempt_at"),
        "last_error": previous.get("last_error"),
        "next_action": previous.get("next_action"),
    }


def summarize_record_chain(items: list[dict[str, Any]]) -> dict[str, Any]:
    pending = sum(1 for i in items if i.get("archive_status") == "pending_upload")
    failed = sum(1 for i in items if i.get("archive_status") == "upload_failed")
    readback = sum(1 for i in items if i.get("archive_status") == "readback_failed")
    waiting = sum(1 for i in items if i.get("archive_status") == "waiting_for_key")
    archived = sum(1 for i in items if i.get("archive_status") == "archived")
    actionable = pending + failed + readback + waiting
    return {
        "pending_upload_count": pending,
        "failed_upload_count": failed,
        "readback_failed_count": readback,
        "waiting_for_key_count": waiting,
        "archived_count": archived,
        "backlog_current": actionable == 0,
    }


def summarize_native_ots(items: list[dict[str, Any]]) -> dict[str, Any]:
    waiting_upgrade = sum(1 for i in items if i.get("archive_status") == "waiting_for_upgrade")
    upgrade_due = sum(1 for i in items if i.get("archive_status") == "upgrade_due")
    upgrade_failed = sum(1 for i in items if i.get("archive_status") == "upgrade_failed")
    pending = sum(1 for i in items if i.get("archive_status") == "pending_upload")
    failed = sum(1 for i in items if i.get("archive_status") == "upload_failed")
    readback = sum(1 for i in items if i.get("archive_status") == "readback_failed")
    waiting_key = sum(1 for i in items if i.get("archive_status") == "waiting_for_key")
    archived = sum(1 for i in items if i.get("archive_status") == "archived")

    actionable = upgrade_due + upgrade_failed + pending + failed + readback + waiting_key
    record_indices = [
        i.get("record_index")
        for i in items
        if isinstance(i.get("record_index"), int)
    ]
    first_open = min(record_indices) if record_indices else None

    return {
        "waiting_for_upgrade_count": waiting_upgrade,
        "upgrade_due_count": upgrade_due,
        "upgrade_failed_count": upgrade_failed,
        "pending_upload_count": pending,
        "failed_upload_count": failed,
        "readback_failed_count": readback,
        "waiting_for_key_count": waiting_key,
        "archived_count": archived,
        "open_item_count": len(items),
        "first_open_record_index": first_open,
        "backlog_current": actionable == 0 and waiting_upgrade == 0,
    }


def record_chain_backlog_doc(items: list[dict[str, Any]], updated_at: str) -> dict[str, Any]:
    return {
        "schema": RC_SCHEMA,
        "updated_at": updated_at,
        "items": items,
        "summary": summarize_record_chain(items),
        "boundary": RC_BOUNDARY,
    }


def native_ots_backlog_doc(
    items: list[dict[str, Any]],
    updated_at: str,
    scan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    summary = summarize_native_ots(items)
    if scan:
        summary.update(scan)
    return {
        "schema": OTS_SCHEMA,
        "updated_at": updated_at,
        "items": items,
        "summary": summary,
        "boundary": OTS_BOUNDARY,
    }


def has_arweave_key() -> bool:
    return bool(os.environ.get("ARKEY") or os.environ.get("ARWEAVE_JWK") or os.environ.get("ARWEAVE_JWK_PATH"))


def run_detector_write() -> None:
    subprocess.run(["python3", "scripts/detect_archive_backlog.py", "--write"], cwd=ROOT, check=True)
