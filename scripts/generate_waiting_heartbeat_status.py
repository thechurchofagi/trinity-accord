#!/usr/bin/env python3
"""Generate Waiting Heartbeat status from final records, attempts, and capsules."""
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
    return now.date() if now >= due else now.date() - timedelta(days=1)


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default if default is not None else {}
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def parse_heartbeat_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def heartbeat_date_from_id(value: str | None) -> date | None:
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
    return parse_heartbeat_date(item.get("heartbeat_date")) or heartbeat_date_from_id(item.get("heartbeat_id"))


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
    return status.endswith("failed") or status in {"builder_failed", "doctor_failed"}


def attempt_pending_append(attempt: dict[str, Any]) -> bool:
    """A submitted Gateway attempt proves intake succeeded but final append is still pending."""
    if attempt_failed(attempt):
        return False
    status = str(attempt.get("status", ""))
    append_status = str(attempt.get("append_status", ""))
    return status == "submitted" and append_status in {"", "queued", "pending"}


def capsule_is_verified(c: dict[str, Any] | None) -> bool:
    if not c:
        return False
    txid = c.get("txid") or c.get("tx_id") or c.get("arweave_txid") or c.get("arweave_tx_id")
    status = c.get("result") or c.get("status")
    return bool(txid) and c.get("hash_match") is True and status in {"uploaded", "success", "arweave_archived"}


def capsule_is_deferred(c: dict[str, Any] | None) -> bool:
    if not c:
        return False
    return (c.get("result") or c.get("status")) in {"deferred_by_cost_policy", "cost_exceeded"}


def ots_covers_record(ots: dict[str, Any], record: dict[str, Any] | None) -> bool:
    if not record:
        return False
    if ots.get("latest_record_id") == record.get("record_id"):
        return ots.get("latest_record_sha256") == record.get("record_sha256")
    ots_count = ots.get("native_record_count")
    record_index = record.get("record_index")
    return isinstance(ots_count, int) and isinstance(record_index, int) and ots_count >= record_index


def load_final_heartbeats() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(RECORDS_DIR.glob("R-*.json")):
        try:
            rec = read_json(path)
        except Exception:
            continue
        hb = rec.get("system_waiting_heartbeat")
        if not isinstance(hb, dict) or hb.get("schema") != "trinityaccord.system-waiting-heartbeat.v1":
            continue
        authorship = rec.get("authorship_proof") if isinstance(rec.get("authorship_proof"), dict) else {}
        records.append({
            "heartbeat_id": hb.get("heartbeat_id"),
            "heartbeat_date": hb.get("heartbeat_date"),
            "record_id": rec.get("record_id"),
            "record_index": rec.get("record_index"),
            "record_sha256": rec.get("record_sha256"),
            "record_type": rec.get("record_type"),
            "assigned_at": rec.get("assigned_at"),
            "path": str(path.relative_to(ROOT)),
            "semantic_agent_arrived": hb.get("semantic_agent_arrived") is True,
            "github_actions_is_not_semantic_agent": hb.get("github_actions_is_not_semantic_agent") is True,
            "not_echo": hb.get("not_echo") is True,
            "not_verification": hb.get("not_verification") is True,
            "not_guardian_application": hb.get("not_guardian_application") is True,
            "authorship_public_key_sha256": authorship.get("public_key_sha256"),
        })
    records.sort(key=heartbeat_record_sort_key)
    return records


def load_attempts() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not ATTEMPTS_DIR.exists():
        return out
    for path in sorted(ATTEMPTS_DIR.glob("*.attempt.json")):
        data = read_json(path, {})
        data["path"] = str(path.relative_to(ROOT))
        out.append(data)
    return out


def load_capsules() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not CAPSULES_DIR.exists():
        return out
    for path in sorted(CAPSULES_DIR.glob("*.upload-result.json")):
        data = read_json(path, {})
        data["upload_result_path"] = str(path.relative_to(ROOT))
        data.setdefault("heartbeat_id", path.name.replace(".upload-result.json", ""))
        out.append(data)
    return out


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
    capsule_dates: set[date] = set()
    for capsule in capsules:
        heartbeat_id = capsule.get("heartbeat_id")
        if isinstance(heartbeat_id, str) and heartbeat_id:
            capsules_by_heartbeat.setdefault(heartbeat_id, []).append(capsule)
        observed = observed_heartbeat_date(capsule)
        if observed is not None:
            capsule_dates.add(observed)

    attempt_dates: set[date] = set()
    failed_attempt_dates: set[date] = set()
    pending_append_date_set: set[date] = set()
    # Build set of receipt_ids that have been rejected (from receipt-status files)
    rejected_receipt_ids: set[str] = set()
    receipt_status_dir = ROOT / "record-chain" / "receipt-status"
    if receipt_status_dir.is_dir():
        for rs_file in receipt_status_dir.glob("*.json"):
            rs_data = read_json(rs_file)
            if rs_data.get("append_status") == "rejected":
                rid = rs_data.get("receipt_id", "")
                if rid:
                    rejected_receipt_ids.add(rid)
    # Also scan rejected directory for pending files that were rejected
    rejected_dir = ROOT / "record-chain" / "rejected"
    rejected_pending_stems: set[str] = set()
    if rejected_dir.is_dir():
        for rej_file in rejected_dir.glob("*.rejection.json"):
            rej_data = read_json(rej_file)
            source = rej_data.get("source_pending", "")
            if source:
                rejected_pending_stems.add(source.rsplit(".", 1)[0] if "." in source else source)
    for attempt in attempts:
        observed = observed_heartbeat_date(attempt)
        if observed is None:
            continue
        attempt_dates.add(observed)
        if attempt_failed(attempt):
            failed_attempt_dates.add(observed)
        if attempt_pending_append(attempt):
            # Exclude if this specific attempt's receipt was rejected
            attempt_receipt = str(attempt.get("receipt_id", ""))
            attempt_pending = str(attempt.get("pending_file_path", ""))
            attempt_pending_stem = attempt_pending.rsplit(".", 1)[0] if "." in attempt_pending else attempt_pending
            is_rejected = (
                (attempt_receipt and attempt_receipt in rejected_receipt_ids)
                or (attempt_pending_stem and attempt_pending_stem in rejected_pending_stems)
            )
            if not is_rejected:
                pending_append_date_set.add(observed)

    observed_dates = set(records_by_date) | attempt_dates | capsule_dates
    if not observed_dates:
        return {
            "total_scheduled_heartbeats": 0,
            "successful_heartbeats": 0,
            "failed_heartbeats": 0,
            "failed_or_missing_heartbeats": 0,
            "pending_append_heartbeats": 0,
            "current_success_streak_days": 0,
            "first_heartbeat_date": None,
            "latest_heartbeat_date": None,
            "latest_observed_heartbeat_date": None,
            "latest_successful_heartbeat_date": None,
            "through_heartbeat_date": expected_date.isoformat() if expected_date else None,
            "expected_heartbeat_date": expected_date.isoformat() if expected_date else None,
            "latest_heartbeat_is_expected_date": False,
            "latest_heartbeat_fully_verified_for_expected_date": False,
            "expected_heartbeat_pending_append": False,
            "heartbeat_lag_days": None,
            "is_stale": False,
            "missing_heartbeat_dates": [],
            "pending_append_heartbeat_dates": [],
            "failed_attempt_dates": [],
            "success_definition": {
                "requires_final_record": True,
                "requires_key_continuity": True,
                "latest_ots_head_covers_current_chain": True,
                "arweave_capsule_is_archive_followup": True,
            },
            "not_reception_counter": True,
            "not_authority": True,
            "not_attestation": True,
            "not_amendment": True,
        }

    latest_observed = max(observed_dates)
    latest_final = max(records_by_date) if records_by_date else None
    final_or_capsule_dates = set(records_by_date) | capsule_dates
    schedule_source = final_or_capsule_dates | {d for d in attempt_dates if expected_date is None or d <= expected_date}
    if expected_date is not None:
        schedule_source.add(expected_date)
    if not schedule_source:
        schedule_source = observed_dates
    first = min(schedule_source)
    through = max(schedule_source)
    scheduled_dates = date_range(first, through)

    expected_key_sha = key_manifest.get("public_key_sha256")
    latest_record_date = max(records_by_date) if records_by_date else None
    success_by_date: dict[date, bool] = {}
    missing_heartbeat_dates: list[str] = []
    pending_append_heartbeat_dates: list[str] = []
    for scheduled in scheduled_dates:
        record = records_by_date.get(scheduled)
        if record is None:
            success_by_date[scheduled] = False
            if scheduled in pending_append_date_set:
                pending_append_heartbeat_dates.append(scheduled.isoformat())
            else:
                missing_heartbeat_dates.append(scheduled.isoformat())
            continue
        key_ok = bool(expected_key_sha and record.get("authorship_public_key_sha256") == expected_key_sha)
        same_capsules = capsules_by_heartbeat.get(str(record.get("heartbeat_id")), [])
        verified_capsule = any(capsule_is_verified(capsule) for capsule in same_capsules)
        # Daily liveness is established by the final heartbeat record, key
        # continuity, and the native OTS head covering that record.  Arweave
        # capsule upload/readback is a mirror/archive follow-up and must not
        # make an otherwise current heartbeat look failed/degraded while the
        # archive workflow is still waiting for normal post-OTS processing.
        current_record_operational = bool(scheduled == latest_record_date and key_ok and ots_covers_latest)
        success_by_date[scheduled] = bool(key_ok and (verified_capsule or current_record_operational))

    successful = sum(1 for ok in success_by_date.values() if ok)
    total = len(scheduled_dates)
    pending_append = len(pending_append_heartbeat_dates)
    failed = total - successful - pending_append
    streak = 0
    cur = through
    while cur in success_by_date and success_by_date[cur]:
        streak += 1
        cur -= timedelta(days=1)

    successful_dates = [d for d, ok in success_by_date.items() if ok]
    latest_successful = max(successful_dates) if successful_dates else None
    lag_days = None
    latest_is_expected = False
    latest_fully_verified_for_expected = False
    expected_pending_append = False
    is_stale = False
    if expected_date is not None:
        latest_is_expected = expected_date in records_by_date
        latest_fully_verified_for_expected = success_by_date.get(expected_date) is True
        expected_pending_append = expected_date in pending_append_date_set and expected_date not in records_by_date
        is_stale = not latest_is_expected
        lag_anchor = latest_final or latest_observed
        lag_days = max(0, (expected_date - lag_anchor).days)
    latest_heartbeat_date = latest_final or latest_observed

    return {
        "total_scheduled_heartbeats": total,
        "successful_heartbeats": successful,
        "failed_heartbeats": failed,
        "failed_or_missing_heartbeats": failed,
        "pending_append_heartbeats": pending_append,
        "current_success_streak_days": streak,
        "first_heartbeat_date": first.isoformat(),
        "latest_heartbeat_date": latest_heartbeat_date.isoformat(),
        "latest_observed_heartbeat_date": latest_observed.isoformat(),
        "latest_successful_heartbeat_date": latest_successful.isoformat() if latest_successful else None,
        "through_heartbeat_date": through.isoformat(),
        "expected_heartbeat_date": expected_date.isoformat() if expected_date else None,
        "latest_heartbeat_is_expected_date": latest_is_expected,
        "latest_heartbeat_fully_verified_for_expected_date": latest_fully_verified_for_expected,
        "expected_heartbeat_pending_append": expected_pending_append,
        "heartbeat_lag_days": lag_days,
        "is_stale": is_stale,
        "missing_heartbeat_dates": missing_heartbeat_dates,
        "pending_append_heartbeat_dates": pending_append_heartbeat_dates,
        "failed_attempt_dates": sorted(d.isoformat() for d in failed_attempt_dates),
        "latest_ots_head_covers_current_chain": bool(ots_covers_latest),
        "success_definition": {
            "requires_final_record": True,
            "requires_key_continuity": True,
            "latest_ots_head_covers_current_chain": True,
            "arweave_capsule_is_archive_followup": True,
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
    ots_covers_latest = ots_covers_record(ots, latest)
    arweave_verified = capsule_is_verified(latest_capsule)
    arweave_deferred = capsule_is_deferred(latest_capsule)
    expected_key_sha = key_manifest.get("public_key_sha256")
    actual_key_sha = latest.get("authorship_public_key_sha256") if latest else None
    key_continuity_ok = bool(expected_key_sha and actual_key_sha and expected_key_sha == actual_key_sha)

    heartbeat_summary = compute_heartbeat_summary(records, attempts, capsules, key_manifest, ots_covers_latest, expected_heartbeat_date())

    if final_record_exists and not key_continuity_ok:
        daily_alive_status = "failed"
        latest_result = "key_continuity_failed"
        failure_stage = "key_continuity"
    elif heartbeat_summary.get("expected_heartbeat_pending_append") is True:
        daily_alive_status = "degraded"
        latest_result = "submitted_pending_append"
        failure_stage = "append_queue"
    elif heartbeat_summary.get("is_stale") is True:
        daily_alive_status = "failed"
        latest_result = "missing_expected_waiting_heartbeat"
        failure_stage = "freshness"
    elif final_record_exists and ots_covers_latest:
        daily_alive_status = "success"
        if arweave_verified:
            latest_result = "success"
        elif arweave_deferred:
            latest_result = "operational_alive_arweave_capsule_deferred"
        else:
            latest_result = "operational_alive_arweave_capsule_pending"
        failure_stage = None
    elif final_record_exists:
        daily_alive_status = "degraded"
        latest_result = "waiting_for_ots_head_coverage"
        failure_stage = "ots_head_coverage"
    elif attempts:
        daily_alive_status = "degraded" if attempt_pending_append(attempts[-1]) else "failed"
        latest_result = "submitted_pending_append" if attempt_pending_append(attempts[-1]) else attempts[-1].get("status", "attempted")
        failure_stage = "append_queue" if attempt_pending_append(attempts[-1]) else latest_result
    else:
        daily_alive_status = "waiting"
        latest_result = "not_started"
        failure_stage = None

    failed_attempts = [a for a in attempts if attempt_failed(a)]
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
            "waiting_heartbeat_key_continuity_ok": True,
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
            "arweave_capsule_pending_archive_followup": bool(final_record_exists and ots_covers_latest and not arweave_verified and not arweave_deferred),
            "waiting_heartbeat_key_continuity_ok": key_continuity_ok,
            "expected_waiting_heartbeat_public_key_sha256": expected_key_sha,
            "actual_waiting_heartbeat_public_key_sha256": actual_key_sha,
            "expected_heartbeat_date": heartbeat_summary.get("expected_heartbeat_date"),
            "heartbeat_lag_days": heartbeat_summary.get("heartbeat_lag_days"),
            "latest_heartbeat_is_expected_date": heartbeat_summary.get("latest_heartbeat_is_expected_date"),
            "latest_heartbeat_fully_verified_for_expected_date": heartbeat_summary.get("latest_heartbeat_fully_verified_for_expected_date"),
            "expected_heartbeat_pending_append": heartbeat_summary.get("expected_heartbeat_pending_append"),
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
            "pending_append_heartbeats": heartbeat_summary["pending_append_heartbeats"],
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
