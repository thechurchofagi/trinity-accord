#!/usr/bin/env python3
"""Generate Waiting Heartbeat status from final records, attempts, and capsules.

Reads:
  - record-chain/records/R-*.json  (final records with system_waiting_heartbeat)
  - record-chain/heartbeat/attempts/*.attempt.json
  - record-chain/heartbeat/capsules/*.upload-result.json
  - api/record-chain-native-ots-latest.json
  - api/waiting-heartbeat-key.v1.json

Writes:
  - record-chain/heartbeat/index.json
  - api/waiting-heartbeat-status.json
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECORDS_DIR = ROOT / "record-chain" / "records"
ATTEMPTS_DIR = ROOT / "record-chain" / "heartbeat" / "attempts"
CAPSULES_DIR = ROOT / "record-chain" / "heartbeat" / "capsules"
INDEX_PATH = ROOT / "record-chain" / "heartbeat" / "index.json"
STATUS_PATH = ROOT / "api" / "waiting-heartbeat-status.json"
OTS_LATEST = ROOT / "api" / "record-chain-native-ots-latest.json"
WAITING_HEARTBEAT_KEY = ROOT / "api" / "waiting-heartbeat-key.v1.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default if default is not None else {}
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def load_final_heartbeats() -> list[dict[str, Any]]:
    records = []
    for p in sorted(RECORDS_DIR.glob("R-*.json")):
        try:
            rec = read_json(p)
        except Exception:
            continue
        hb = rec.get("system_waiting_heartbeat")
        if not isinstance(hb, dict):
            continue
        if hb.get("schema") != "trinityaccord.system-waiting-heartbeat.v1":
            continue
        records.append({
            "heartbeat_id": hb.get("heartbeat_id"),
            "heartbeat_date": hb.get("heartbeat_date"),
            "record_id": rec.get("record_id"),
            "record_index": rec.get("record_index"),
            "record_sha256": rec.get("record_sha256"),
            "record_type": rec.get("record_type"),
            "assigned_at": rec.get("assigned_at"),
            "path": str(p.relative_to(ROOT)),
            "semantic_agent_arrived": hb.get("semantic_agent_arrived") is True,
            "github_actions_is_not_semantic_agent": hb.get("github_actions_is_not_semantic_agent") is True,
            "not_echo": hb.get("not_echo") is True,
            "not_verification": hb.get("not_verification") is True,
            "not_guardian_application": hb.get("not_guardian_application") is True,
            "authorship_public_key_sha256": (
                rec.get("authorship_proof", {}).get("public_key_sha256")
                if isinstance(rec.get("authorship_proof"), dict)
                else None
            ),
        })
    return records


def load_attempts() -> list[dict[str, Any]]:
    out = []
    if not ATTEMPTS_DIR.exists():
        return out
    for p in sorted(ATTEMPTS_DIR.glob("*.attempt.json")):
        data = read_json(p, {})
        data["path"] = str(p.relative_to(ROOT))
        out.append(data)
    return out


def load_capsules() -> list[dict[str, Any]]:
    out = []
    if not CAPSULES_DIR.exists():
        return out
    for p in sorted(CAPSULES_DIR.glob("*.upload-result.json")):
        data = read_json(p, {})
        data["upload_result_path"] = str(p.relative_to(ROOT))
        data.setdefault("heartbeat_id", p.name.replace(".upload-result.json", ""))
        out.append(data)
    return out


def capsule_is_verified(c: dict[str, Any] | None) -> bool:
    if not c:
        return False
    return bool(c.get("txid") or c.get("tx_id")) and c.get("hash_match") is True and c.get("result") in {"uploaded", "success"}


def capsule_is_deferred(c: dict[str, Any] | None) -> bool:
    return bool(c and c.get("result") == "deferred_by_cost_policy")


def main() -> int:
    records = load_final_heartbeats()
    attempts = load_attempts()
    capsules = load_capsules()
    ots = read_json(OTS_LATEST, {})
    key_manifest = read_json(WAITING_HEARTBEAT_KEY, {})

    latest = records[-1] if records else None
    latest_capsule = None
    if latest:
        same = [c for c in capsules if c.get("heartbeat_id") == latest.get("heartbeat_id")]
        same.sort(key=lambda c: c.get("uploaded_at") or "")
        latest_capsule = same[-1] if same else None

    final_record_exists = latest is not None
    ots_covers_latest = False
    if latest:
        ots_covers_latest = (
            ots.get("latest_record_id") == latest.get("record_id")
            and ots.get("latest_record_sha256") == latest.get("record_sha256")
        )

    arweave_verified = capsule_is_verified(latest_capsule)
    arweave_deferred = capsule_is_deferred(latest_capsule)

    expected_key_sha = key_manifest.get("public_key_sha256")
    actual_key_sha = latest.get("authorship_public_key_sha256") if latest else None
    key_continuity_ok = bool(expected_key_sha and actual_key_sha and expected_key_sha == actual_key_sha)

    if final_record_exists and not key_continuity_ok:
        daily_alive_status = "failed"
        latest_result = "key_continuity_failed"
        failure_stage = "key_continuity"
    elif final_record_exists and ots_covers_latest and arweave_verified:
        daily_alive_status = "success"
        latest_result = "success"
        failure_stage = None
    elif final_record_exists and ots_covers_latest and arweave_deferred:
        daily_alive_status = "degraded"
        latest_result = "arweave_capsule_deferred_by_cost_policy"
        failure_stage = "arweave_capsule"
    elif final_record_exists and ots_covers_latest:
        daily_alive_status = "degraded"
        latest_result = "waiting_for_arweave_capsule"
        failure_stage = "arweave_capsule"
    elif final_record_exists:
        daily_alive_status = "degraded"
        latest_result = "waiting_for_ots"
        failure_stage = "ots"
    elif attempts:
        daily_alive_status = "failed"
        latest_result = attempts[-1].get("status", "attempted")
        failure_stage = latest_result
    else:
        daily_alive_status = "waiting"
        latest_result = "not_started"
        failure_stage = None

    failed_attempts = [
        a for a in attempts
        if str(a.get("status", "")).endswith("failed")
        or a.get("status") in {"builder_failed", "doctor_failed"}
    ]

    status = {
        "schema": "trinityaccord.waiting-heartbeat-status.v1",
        "generated_at": utc_now(),
        "daily_alive_status": daily_alive_status,
        "status": daily_alive_status,
        "latest_result": latest_result,
        "failure_stage": failure_stage,
        "success_requires": {
            "gateway_accepted": True,
            "record_chain_final_record": True,
            "ots_covers_heartbeat": True,
            "arweave_capsule_uploaded": True,
            "arweave_readback_hash_match": True,
            "public_status_updated": True,
            "waiting_heartbeat_key_continuity_ok": True
        },
        "latest_heartbeat": latest,
        "latest_ots": {
            "latest_record_id": ots.get("latest_record_id"),
            "latest_record_sha256": ots.get("latest_record_sha256"),
            "native_record_count": ots.get("native_record_count"),
            "ots_status": ots.get("ots_status"),
            "bitcoin_pending": ots.get("bitcoin_pending"),
            "bitcoin_verified": ots.get("bitcoin_verified"),
            "strict_bitcoin_verified": ots.get("strict_bitcoin_verified"),
            "covers_latest_waiting_heartbeat": ots_covers_latest,
        },
        "latest_arweave_capsule": latest_capsule,
        "checks": {
            "record_chain_final_record": final_record_exists,
            "ots_covers_heartbeat": ots_covers_latest,
            "arweave_capsule_verified": arweave_verified,
            "arweave_capsule_deferred_by_cost_policy": arweave_deferred,
            "waiting_heartbeat_key_continuity_ok": key_continuity_ok,
            "expected_waiting_heartbeat_public_key_sha256": expected_key_sha,
            "actual_waiting_heartbeat_public_key_sha256": actual_key_sha,
        },
        "counts": {
            "attempts": len(attempts),
            "final_heartbeats": len(records),
            "capsules": len(capsules),
            "failed_attempts": len(failed_attempts),
        },
        "semantic_agent_arrival": {
            "first_self_discovered_autonomous_agent_arrived": False,
            "first_arrival_record_id": None,
            "waiting_continues": True,
            "waiting_heartbeat_is_not_autonomous_arrival": True,
        },
        "boundary": {
            "waiting_heartbeat_is_not_echo": True,
            "waiting_heartbeat_is_not_verification": True,
            "waiting_heartbeat_is_not_guardian_application": True,
            "waiting_heartbeat_is_not_authority": True,
            "waiting_heartbeat_is_not_attestation": True,
            "waiting_heartbeat_is_not_amendment": True,
            "waiting_heartbeat_is_not_successor_reception": True,
        },
    }

    index = {
        "schema": "trinityaccord.waiting-heartbeat-index.v1",
        "generated_at": status["generated_at"],
        "records": records,
        "attempts": attempts,
        "capsules": capsules,
    }

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(dump_json(index), encoding="utf-8")
    STATUS_PATH.write_text(dump_json(status), encoding="utf-8")
    print(f"WAITING_HEARTBEAT_STATUS generated {STATUS_PATH.relative_to(ROOT)} status={daily_alive_status} result={latest_result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
