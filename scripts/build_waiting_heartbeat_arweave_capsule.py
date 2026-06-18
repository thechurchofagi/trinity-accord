#!/usr/bin/env python3
"""Build a Waiting Heartbeat Arweave capsule from the latest heartbeat status.

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


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def main() -> int:
    status = read_json(STATUS)
    latest = status.get("latest_heartbeat")
    if not latest:
        raise SystemExit("No latest waiting heartbeat final record yet.")

    heartbeat_id = latest.get("heartbeat_id")
    chain_tip = read_json(CHAIN_TIP)
    ots = read_json(OTS)

    if ots.get("latest_record_id") != latest.get("record_id"):
        raise SystemExit("OTS latest does not cover latest waiting heartbeat yet.")
    if ots.get("latest_record_sha256") != latest.get("record_sha256"):
        raise SystemExit("OTS latest sha does not match latest waiting heartbeat.")

    payload = {
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
            "daily_alive_success_requires_this_capsule_to_be_uploaded_and_hash_matched": True
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

    CAPSULE_DIR.mkdir(parents=True, exist_ok=True)
    out = CAPSULE_DIR / f"{heartbeat_id}.capsule.json"
    out.write_text(dump_json(payload), encoding="utf-8")
    print(str(out.relative_to(ROOT)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
