#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "api" / "waiting-heartbeat-status.json"
PUBLIC = ROOT / "api" / "public-home-status.json"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def main() -> int:
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

    print("PASS: waiting heartbeat summary metrics contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
