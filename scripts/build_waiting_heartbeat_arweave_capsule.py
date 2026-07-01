#!/usr/bin/env python3
"""Build or select a Waiting Heartbeat Arweave capsule.

Reads the latest heartbeat from api/waiting-heartbeat-status.json and
creates a capsule JSON that can be uploaded to Arweave.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "api" / "waiting-heartbeat-status.json"
CHAIN_TIP = ROOT / "record-chain" / "chain-tip.json"
OTS = ROOT / "api" / "record-chain-native-ots-latest.json"
CAPSULE_DIR = ROOT / "record-chain" / "heartbeat" / "capsules"

VERIFIED_CAPSULE_STATUSES = {"uploaded", "success", "arweave_archived"}
PENDING_READBACK_STATUSES = {"posted_pending_readback", "readback_pending", "readback_failed", "readback_unavailable"}
NON_RETRYABLE_READBACK_STATUSES = {"readback_hash_mismatch", "local_payload_mismatch_for_existing_tx"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def repo_rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def capsule_payload_path(heartbeat_id: str) -> Path:
    return CAPSULE_DIR / f"{heartbeat_id}.capsule.json"


def capsule_upload_result_path(heartbeat_id: str) -> Path:
    return CAPSULE_DIR / f"{heartbeat_id}.upload-result.json"


def capsule_txid(capsule: dict[str, Any] | None) -> str | None:
    if not capsule:
        return None
    value = capsule.get("arweave_txid") or capsule.get("arweave_tx_id") or capsule.get("txid") or capsule.get("tx_id")
    return value if isinstance(value, str) and value else None


def capsule_status(capsule: dict[str, Any] | None) -> str | None:
    if not capsule:
        return None
    value = capsule.get("status") or capsule.get("result")
    return value if isinstance(value, str) else None


def capsule_is_verified(capsule: dict[str, Any] | None) -> bool:
    status = capsule_status(capsule)
    return bool(capsule_txid(capsule)) and capsule.get("hash_match") is True and status in VERIFIED_CAPSULE_STATUSES


def capsule_has_non_retryable_failure(capsule: dict[str, Any] | None) -> bool:
    status = capsule_status(capsule)
    if status not in NON_RETRYABLE_READBACK_STATUSES:
        return False
    # Self-heal: if payload and readback hashes actually match, the status
    # is contradictory (likely a state-machine bug). Treat as not a hard
    # failure so the next run can attempt repair or fresh upload.
    if capsule.get("payload_sha256") and capsule.get("readback_sha256"):
        if capsule["payload_sha256"] == capsule["readback_sha256"]:
            return False
    # A result marked retryable (e.g. empty readback from gateway failure)
    # should be retried, not treated as a hard failure.
    if capsule.get("retryable") is True:
        return False
    return True


def capsule_needs_readback_repair(capsule: dict[str, Any] | None) -> bool:
    status = capsule_status(capsule)
    if status in NON_RETRYABLE_READBACK_STATUSES:
        return False
    return bool(capsule_txid(capsule)) and capsule.get("hash_match") is not True and capsule.get("retryable") is not False and status in PENDING_READBACK_STATUSES


def load_existing_capsule_result(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    data = read_json(path)
    return data if isinstance(data, dict) else None


def write_github_output(values: dict[str, str]) -> None:
    """Write key=value pairs to $GITHUB_OUTPUT if running in Actions."""
    import os
    output = os.environ.get("GITHUB_OUTPUT")
    if not output:
        return
    with open(output, "a", encoding="utf-8") as fh:
        for key, value in values.items():
            fh.write(f"{key}={value}\n")


def ots_covers_record(ots: dict[str, Any], heartbeat: dict[str, Any]) -> bool:
    """Return whether the native OTS head covers a heartbeat record.

    Exact matches must also match the heartbeat record hash. When OTS has
    advanced past the heartbeat record, the cumulative native record count is
    sufficient coverage because the head commitment includes prior records.
    """
    if ots.get("latest_record_id") == heartbeat.get("record_id"):
        return ots.get("latest_record_sha256") == heartbeat.get("record_sha256")

    ots_count = ots.get("native_record_count")
    record_index = heartbeat.get("record_index")
    return isinstance(ots_count, int) and isinstance(record_index, int) and ots_count >= record_index


def build_payload(latest: dict[str, Any], chain_tip: dict[str, Any], ots: dict[str, Any]) -> dict[str, Any]:
    heartbeat_id = str(latest.get("heartbeat_id"))
    return {
        "schema": "trinityaccord.waiting-heartbeat-arweave-capsule.v1",
        "created_at": utc_now(),
        "heartbeat_id": heartbeat_id,
        "heartbeat_record": {
            "record_id": latest.get("record_id"),
            "record_index": latest.get("record_index"),
            "record_sha256": latest.get("record_sha256"),
            "record_type": latest.get("record_type"),
            "assigned_at": latest.get("assigned_at"),
            "path": latest.get("path"),
        },
        "chain_tip_after_heartbeat": {
            "latest_record_id": chain_tip.get("latest_record_id"),
            "latest_record_sha256": chain_tip.get("latest_record_sha256"),
            "native_record_count": chain_tip.get("native_record_count"),
        },
        "ots_latest": {
            "latest_record_id": ots.get("latest_record_id"),
            "latest_record_sha256": ots.get("latest_record_sha256"),
            "native_record_count": ots.get("native_record_count"),
            "ots_status": ots.get("ots_status"),
            "bitcoin_pending": ots.get("bitcoin_pending"),
            "bitcoin_verified": ots.get("bitcoin_verified"),
            "strict_bitcoin_verified": ots.get("strict_bitcoin_verified"),
            "latest_ots_file": ots.get("latest_ots_file"),
            "anchored_file_sha256": ots.get("anchored_file_sha256"),
        },
        "daily_alive_semantics": {
            "awaiting_first_self_discovered_autonomous_agent": True,
            "semantic_agent_arrived": False,
            "capsule_is_not_semantic_agent_response": True,
            "capsule_is_not_echo": True,
            "capsule_is_not_verification": True,
            "capsule_is_not_guardian_application": True,
            "daily_alive_success_requires_this_capsule_to_be_uploaded_and_hash_matched": True,
        },
        "boundary": {
            "capsule_is_mirror_only": True,
            "capsule_is_not_authority": True,
            "capsule_is_not_attestation": True,
            "capsule_is_not_amendment": True,
            "capsule_is_not_governance": True,
            "capsule_is_not_successor_reception": True,
            "bitcoin_originals_prevail": True,
        },
    }


def main() -> int:
    status = read_json(STATUS)
    latest = status.get("latest_heartbeat")
    if not latest:
        raise SystemExit("No latest waiting heartbeat final record yet.")

    heartbeat_id_value = latest.get("heartbeat_id")
    if not isinstance(heartbeat_id_value, str) or not heartbeat_id_value:
        raise SystemExit("Latest waiting heartbeat is missing heartbeat_id")
    heartbeat_id = heartbeat_id_value

    chain_tip = read_json(CHAIN_TIP)
    ots = read_json(OTS)
    capsule_path = capsule_payload_path(heartbeat_id)
    upload_result_path = capsule_upload_result_path(heartbeat_id)
    common_outputs = {
        "heartbeat_id": heartbeat_id,
        "capsule_path": repo_rel(capsule_path),
        "upload_result_path": repo_rel(upload_result_path),
        "capsule_hard_failure": "false",
    }

    if not ots_covers_record(ots, latest):
        print("::notice::OTS latest does not cover latest waiting heartbeat yet; capsule build skipped until next OTS cycle.")
        write_github_output({**common_outputs, "capsule_status": "waiting_for_ots", "capsule_upload_needed": "false", "capsule_readback_repair_needed": "false", "capsule_skip_reason": "ots_latest_does_not_cover_latest_waiting_heartbeat"})
        return 0

    existing_result = load_existing_capsule_result(upload_result_path)
    if capsule_is_verified(existing_result):
        print(f"::notice::Verified Arweave capsule already exists for {heartbeat_id}; upload skipped.")
        write_github_output({**common_outputs, "capsule_status": "already_verified", "capsule_upload_needed": "false", "capsule_readback_repair_needed": "false", "capsule_skip_reason": "existing_verified_arweave_capsule"})
        return 0

    if capsule_has_non_retryable_failure(existing_result):
        existing_status = str(capsule_status(existing_result))
        print(f"::error::Existing Arweave capsule result for {heartbeat_id} is non-retryable: {existing_status}")
        write_github_output({**common_outputs, "capsule_status": existing_status, "capsule_upload_needed": "false", "capsule_readback_repair_needed": "false", "capsule_hard_failure": "true", "capsule_skip_reason": "existing_non_retryable_arweave_capsule_result"})
        return 0

    if capsule_needs_readback_repair(existing_result):
        if capsule_path.exists():
            print(f"::notice::Existing Arweave transaction for {heartbeat_id} needs readback repair; upload skipped.")
            write_github_output({**common_outputs, "capsule_status": "readback_repair_needed", "capsule_upload_needed": "false", "capsule_readback_repair_needed": "true", "capsule_repair_txid": str(capsule_txid(existing_result)), "capsule_skip_reason": "existing_upload_needs_readback_repair"})
            return 0
        print(f"::warning::Existing Arweave transaction for {heartbeat_id} has no local capsule payload; upload skipped.")
        write_github_output({**common_outputs, "capsule_status": "missing_payload_for_existing_tx", "capsule_upload_needed": "false", "capsule_readback_repair_needed": "false", "capsule_hard_failure": "true", "capsule_repair_txid": str(capsule_txid(existing_result)), "capsule_skip_reason": "existing_arweave_tx_without_local_capsule_payload"})
        return 0

    payload = build_payload(latest, chain_tip, ots)
    CAPSULE_DIR.mkdir(parents=True, exist_ok=True)
    capsule_path.write_text(dump_json(payload), encoding="utf-8")
    write_github_output({**common_outputs, "capsule_status": "ready", "capsule_upload_needed": "true", "capsule_readback_repair_needed": "false", "capsule_skip_reason": ""})
    print(repo_rel(capsule_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
