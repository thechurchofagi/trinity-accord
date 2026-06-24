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
from datetime import date, datetime, timedelta, timezone
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

# The scheduled submit workflow runs at 03:17 UTC. Give the submit/append/OTS
# and capsule chain time to run before declaring the current UTC day due. This
# avoids a normal Actions queue overlap publishing a false freshness failure.
HEARTBEAT_DUE_UTC_HOUR = 3
HEARTBEAT_DUE_UTC_MINUTE = 17
HEARTBEAT_DUE_GRACE_MINUTES = 90


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def expected_heartbeat_date(now: datetime | None = None) -> date:
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    now = now.astimezone(timezone.utc)
    due = now.replace(
        hour=HEARTBEAT_DUE_UTC_HOUR,
        minute=HEARTBEAT_DUE_UTC_MINUTE,
        second=0,
        microsecond=0,
    ) + timedelta(minutes=HEARTBEAT_DUE_GRACE_MINUTES)
    if now < due:
        return now.date() - timedelta(days=1)
    return now.date()


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
    records.sort(key=heartbeat_record_sort_key)
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
    txid = (
        c.get("txid")
        or c.get("tx_id")
        or c.get("arweave_txid")
        or c.get("arweave_tx_id")
    )
    status = c.get("result") or c.get("status")
    return bool(txid) and c.get("hash_match") is True and status in {
        "uploaded",
        "success",
        "arweave_archived",
    }


def capsule_is_deferred(c: dict[str, Any] | None) -> bool:
    if not c:
        return False
    status = c.get("result") or c.get("status")
    return status in {
        "deferred_by_cost_policy",
        "cost_exceeded",
    }


def parse_heartbeat_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def heartbeat_date_from_id(value: str | None) -> date | None:
    """Parse hwb-YYYYMMDD into a date."""
    if not value or not value.startswith("hwb-"):
        return None
    raw = value.removeprefix("hwb-")
    if len(raw) != 8 or not raw.isdigit():
        return None
    try:
        return date(int(raw[0:4]), int(raw[4:6]), int(raw[6:8]))
    except ValueError:
        return None


def observed_heartbeat_date(item: dict[str, Any]) -> date | None:
    return (
        parse_heartbeat_date(item.get("heartbeat_date"))
        or heartbeat_date_from_id(item.get("heartbeat_id"))
    )


def heartbeat_record_sort_key(record: dict[str, Any]) -> tuple[date, int]:
    observed = observed_heartbeat_date(record) or date.min
    index = record.get("record_index")
    return observed, index if isinstance(index, int) else -1


def date_range(start: date, end: date) -> list[date]:
    out: list[date] = []
    cur = start
    while cur <= end:
        out.append(cur)
        cur += timedelta(days=1)
    return out


def attempt_failed(attempt: dict[str, Any]) -> bool:
    status = str(attempt.get("status", ""))
    return (
        status.endswith("failed")
        or status in {"builder_failed", "doctor_failed"}
    )


def compute_heartbeat_summary(
    records: list[dict[str, Any]],
    attempts: list[dict[str, Any]],
    capsules: list[dict[str, Any]],
    key_manifest: dict[str, Any],
    ots_covers_latest: bool,
    expected_date: date | None = None,
) -> dict[str, Any]:
    records_by_date: dict[date, dict[str, Any]] = {}
    for record in records:
        observed = observed_heartbeat_date(record)
        if observed is not None:
            records_by_date[observed] = record

    capsules_by_heartbeat: dict[str, list[dict[str, Any]]] = {}
    for capsule in capsules:
        heartbeat_id = capsule.get("heartbeat_id")
        if isinstance(heartbeat_id, str) and heartbeat_id:
            capsules_by_heartbeat.setdefault(heartbeat_id, []).append(capsule)

    attempt_dates: set[date] = set()
    failed_attempt_dates: set[date] = set()
    for attempt in attempts:
        observed = observed_heartbeat_date(attempt)
        if observed is None:
            continue
        attempt_dates.add(observed)
        if attempt_failed(attempt):
            failed_attempt_dates.add(observed)

    capsule_dates: set[date] = set()
    for capsule in capsules:
        observed = observed_heartbeat_date(capsule)
        if observed is not None:
            capsule_dates.add(observed)

    observed_dates = set(records_by_date) | attempt_dates | capsule_dates

    if not observed_dates:
        return {
            "total_scheduled_heartbeats": 0,
            "successful_heartbeats": 0,
            "failed_heartbeats": 0,
            "failed_or_missing_heartbeats": 0,
            "current_success_streak_days": 0,
            "first_heartbeat_date": None,
            "latest_heartbeat_date": None,
            "latest_observed_heartbeat_date": None,
            "latest_successful_heartbeat_date": None,
            "through_heartbeat_date": expected_date.isoformat() if expected_date else None,
            "expected_heartbeat_date": expected_date.isoformat() if expected_date else None,
            "latest_heartbeat_is_expected_date": False,
            "heartbeat_lag_days": None,
            "is_stale": False,
            "missing_heartbeat_dates": [],
            "failed_attempt_dates": [],
            "success_definition": {
                "requires_final_record": True,
                "requires_verified_arweave_capsule": True,
                "requires_key_continuity": True,
                "latest_ots_head_covers_current_chain": True,
            },
            "not_reception_counter": True,
            "not_authority": True,
            "not_attestation": True,
            "not_amendment": True,
        }

    first = min(observed_dates)
    latest_observed = max(observed_dates)
    latest_final = max(records_by_date) if records_by_date else None
    through = max(latest_observed, expected_date) if expected_date is not None else latest_observed
    scheduled_dates = date_range(first, through)

    expected_key_sha = key_manifest.get("public_key_sha256")
    success_by_date: dict[date, bool] = {}
    missing_heartbeat_dates: list[str] = []

    for scheduled in scheduled_dates:
        record = records_by_date.get(scheduled)
        if record is None:
            success_by_date[scheduled] = False
            missing_heartbeat_dates.append(scheduled.isoformat())
            continue

        actual_key_sha = record.get("authorship_public_key_sha256")
        key_continuity_ok = bool(
            expected_key_sha
            and actual_key_sha
            and expected_key_sha == actual_key_sha
        )

        same_capsules = capsules_by_heartbeat.get(str(record.get("heartbeat_id")), [])
        verified_capsule = any(capsule_is_verified(capsule) for capsule in same_capsules)

        success_by_date[scheduled] = bool(
            key_continuity_ok
            and verified_capsule
        )

    successful = sum(1 for ok in success_by_date.values() if ok)
    total = len(scheduled_dates)
    failed = total - successful

    streak = 0
    cur = through
    while cur in success_by_date and success_by_date[cur]:
        streak += 1
        cur -= timedelta(days=1)

    successful_dates = [d for d, ok in success_by_date.items() if ok]
    latest_successful = max(successful_dates) if successful_dates else None

    lag_days = None
    latest_is_expected = False
    is_stale = False
    if expected_date is not None:
        latest_is_expected = success_by_date.get(expected_date) is True
        is_stale = not latest_is_expected
        lag_anchor = latest_successful or latest_final or latest_observed
        lag_days = max(0, (expected_date - lag_anchor).days)

    latest_heartbeat_date = latest_final or latest_observed

    return {
        "total_scheduled_heartbeats": total,
        "successful_heartbeats": successful,
        "failed_heartbeats": failed,
        "failed_or_missing_heartbeats": failed,
        "current_success_streak_days": streak,
        "first_heartbeat_date": first.isoformat(),
        "latest_heartbeat_date": latest_heartbeat_date.isoformat(),
        "latest_observed_heartbeat_date": latest_observed.isoformat(),
        "latest_successful_heartbeat_date": latest_successful.isoformat() if latest_successful else None,
        "through_heartbeat_date": through.isoformat(),
        "expected_heartbeat_date": expected_date.isoformat() if expected_date else None,
        "latest_heartbeat_is_expected_date": latest_is_expected,
        "heartbeat_lag_days": lag_days,
        "is_stale": is_stale,
        "missing_heartbeat_dates": missing_heartbeat_dates,
        "failed_attempt_dates": sorted(d.isoformat() for d in failed_attempt_dates),
        "latest_ots_head_covers_current_chain": bool(ots_covers_latest),
        "success_definition": {
            "requires_final_record": True,
            "requires_verified_arweave_capsule": True,
            "requires_key_continuity": True,
            "latest_ots_head_covers_current_chain": True,
        },
        "not_reception_counter": True,
        "not_authority": True,
        "not_attestation": True,
        "not_amendment": True,
    }


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
        same.sort(key=lambda c: c.get("uploaded_at") or c.get("attempted_at") or "")
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

    heartbeat_summary = compute_heartbeat_summary(
        records=records,
        attempts=attempts,
        capsules=capsules,
        key_manifest=key_manifest,
        ots_covers_latest=ots_covers_latest,
        expected_date=expected_heartbeat_date(),
    )

    if heartbeat_summary.get("is_stale") is True:
        daily_alive_status = "failed"
        latest_result = "missing_expected_waiting_heartbeat"
        failure_stage = "freshness"
    elif final_record_exists and not key_continuity_ok:
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
            "expected_heartbeat_date": heartbeat_summary.get("expected_heartbeat_date"),
            "heartbeat_lag_days": heartbeat_summary.get("heartbeat_lag_days"),
            "latest_heartbeat_is_expected_date": heartbeat_summary.get("latest_heartbeat_is_expected_date"),
        },
        "heartbeat_summary": heartbeat_summary,
        "counts": {
            "attempts": len(attempts),
            "final_heartbeats": len(records),
            "capsules": len(capsules),
            "failed_attempts": len(failed_attempts),
            "total_scheduled_heartbeats": heartbeat_summary["total_scheduled_heartbeats"],
            "successful_heartbeats": heartbeat_summary["successful_heartbeats"],
            "failed_heartbeats": heartbeat_summary["failed_heartbeats"],
            "failed_or_missing_heartbeats": heartbeat_summary["failed_or_missing_heartbeats"],
            "current_success_streak_days": heartbeat_summary["current_success_streak_days"],
            "heartbeat_lag_days": heartbeat_summary.get("heartbeat_lag_days"),
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
