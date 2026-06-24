#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "api" / "waiting-heartbeat-status.json"
PUBLIC = ROOT / "api" / "public-home-status.json"
GENERATOR = ROOT / "scripts" / "generate_waiting_heartbeat_status.py"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def load_generator_module():
    spec = importlib.util.spec_from_file_location("generate_waiting_heartbeat_status", GENERATOR)
    require(spec is not None and spec.loader is not None, "could not load waiting heartbeat generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_current_status_contract() -> None:
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    public = json.loads(PUBLIC.read_text(encoding="utf-8"))

    summary = status.get("heartbeat_summary")
    require(isinstance(summary, dict), "waiting-heartbeat-status missing heartbeat_summary")

    for key in [
        "total_scheduled_heartbeats",
        "successful_heartbeats",
        "failed_heartbeats",
        "failed_or_missing_heartbeats",
        "current_success_streak_days",
    ]:
        require(isinstance(summary.get(key), int), f"heartbeat_summary.{key} must be int")

    total = summary["total_scheduled_heartbeats"]
    success = summary["successful_heartbeats"]
    failed = summary["failed_or_missing_heartbeats"]
    streak = summary["current_success_streak_days"]

    require(total >= 0, "total_scheduled_heartbeats must be >= 0")
    require(success >= 0, "successful_heartbeats must be >= 0")
    require(failed >= 0, "failed_or_missing_heartbeats must be >= 0")
    require(total >= success, "total_scheduled_heartbeats must be >= successful_heartbeats")
    require(failed == total - success, "failed_or_missing_heartbeats must equal total - success")
    require(streak <= success, "current_success_streak_days must be <= successful_heartbeats")

    counts = status.get("counts") or {}
    for key in [
        "total_scheduled_heartbeats",
        "successful_heartbeats",
        "failed_heartbeats",
        "failed_or_missing_heartbeats",
        "current_success_streak_days",
    ]:
        require(counts.get(key) == summary.get(key), f"counts.{key} must mirror heartbeat_summary.{key}")

    public_hb = public.get("waiting_heartbeat") or {}
    public_summary = public_hb.get("heartbeat_summary") or {}
    require(public_summary == summary, "public-home-status waiting_heartbeat.heartbeat_summary must mirror canonical status")

    for key in [
        "not_reception_counter",
        "not_authority",
        "not_attestation",
        "not_amendment",
    ]:
        require(summary.get(key) is True, f"heartbeat_summary.{key} must be true")


def test_expected_heartbeat_date_respects_schedule_boundary() -> None:
    generator = load_generator_module()
    before_due = datetime(2026, 6, 24, 1, 32, tzinfo=timezone.utc)
    after_due = datetime(2026, 6, 24, 3, 17, tzinfo=timezone.utc)
    require(
        generator.expected_heartbeat_date(before_due) == date(2026, 6, 23),
        "before 03:17 UTC the expected heartbeat date should be previous UTC date",
    )
    require(
        generator.expected_heartbeat_date(after_due) == date(2026, 6, 24),
        "at/after 03:17 UTC the expected heartbeat date should be current UTC date",
    )


def test_summary_extends_to_expected_date_when_latest_observed_is_stale() -> None:
    generator = load_generator_module()
    summary = generator.compute_heartbeat_summary(
        records=[{
            "heartbeat_id": "hwb-20260622",
            "heartbeat_date": "2026-06-22",
            "record_id": "R-000000056",
            "record_sha256": "sha",
            "authorship_public_key_sha256": "key-sha",
        }],
        attempts=[],
        capsules=[{
            "heartbeat_id": "hwb-20260622",
            "status": "uploaded",
            "arweave_txid": "txid",
            "hash_match": True,
        }],
        key_manifest={"public_key_sha256": "key-sha"},
        ots_covers_latest=True,
        expected_date=date(2026, 6, 23),
    )
    require(summary["total_scheduled_heartbeats"] == 2, "summary should extend through expected heartbeat date")
    require(summary["successful_heartbeats"] == 1, "only observed verified heartbeat should be successful")
    require(summary["failed_or_missing_heartbeats"] == 1, "missing expected heartbeat should be counted failed/missing")
    require(summary["current_success_streak_days"] == 0, "stale expected date should reset current streak")
    require(summary["latest_heartbeat_date"] == "2026-06-22", "latest observed heartbeat date should remain visible")
    require(summary["through_heartbeat_date"] == "2026-06-23", "summary should declare schedule range end")
    require(summary["expected_heartbeat_date"] == "2026-06-23", "summary should declare expected heartbeat date")
    require(summary["heartbeat_lag_days"] == 1, "stale lag should be one day")
    require(summary["is_stale"] is True, "summary should mark stale heartbeat data")
    require("2026-06-23" in summary["missing_heartbeat_dates"], "expected missing date should be listed")


def main() -> int:
    test_current_status_contract()
    test_expected_heartbeat_date_respects_schedule_boundary()
    test_summary_extends_to_expected_date_when_latest_observed_is_stale()
    print("PASS: waiting heartbeat summary metrics contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
