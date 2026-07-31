#!/usr/bin/env python3
"""Generate current Waiting Heartbeat status with weekly archive semantics.

The legacy generator remains intact in ``generate_waiting_heartbeat_status_legacy``
for historical capsule verification and all established heartbeat accounting.
This wrapper changes only the current preservation policy: standalone paid
heartbeat capsules are retired and future heartbeats are mirrored by the weekly
continuity archive instead.
"""
from __future__ import annotations

import json

import generate_waiting_heartbeat_status_legacy as legacy
from generate_waiting_heartbeat_status_legacy import *  # noqa: F401,F403


def _without_generated_at(document: dict) -> dict:
    return {key: value for key, value in document.items() if key != "generated_at"}


def _apply_weekly_archive_policy(status: dict) -> dict:
    if status.get("daily_alive_status") == "success":
        status["latest_result"] = "success"
        status["failure_stage"] = None

    archive_followup = status.setdefault("archive_followup", {})
    archive_followup.update(
        {
            "standalone_arweave_capsule_retired": True,
            "arweave_capsule_upload_expected": False,
            "arweave_readback_hash_match_expected": False,
            "weekly_continuity_archive_expected": True,
            "weekly_continuity_archive_does_not_gate_daily_alive_success": True,
            "historical_capsules_remain_verifiable": True,
        }
    )
    archive_followup.pop("does_not_gate_daily_alive_success", None)

    checks = status.setdefault("checks", {})
    checks.update(
        {
            "arweave_capsule_pending_archive_followup": False,
            "standalone_arweave_capsule_retired": True,
            "weekly_continuity_archive_is_followup": True,
        }
    )

    status["standalone_capsule_policy"] = {
        "status": "retired",
        "historical_results_remain_verifiable": True,
        "new_heartbeats_are_mirrored_by_weekly_continuity_archive": True,
        "daily_liveness_does_not_require_arweave": True,
    }
    return status


def main() -> int:
    old_status = legacy.read_json(legacy.STATUS_PATH, {})
    result = legacy.main()
    generated = legacy.read_json(legacy.STATUS_PATH, {})
    status = _apply_weekly_archive_policy(generated)

    if (
        _without_generated_at(status) == _without_generated_at(old_status)
        and old_status.get("generated_at")
    ):
        status["generated_at"] = old_status["generated_at"]
    else:
        status["generated_at"] = legacy.utc_now()

    legacy.STATUS_PATH.write_text(legacy.dump_json(status), encoding="utf-8")
    print(
        "WAITING_HEARTBEAT_WEEKLY_ARCHIVE_POLICY "
        f"status={status.get('daily_alive_status')} result={status.get('latest_result')}"
    )
    return result


if __name__ == "__main__":
    raise SystemExit(main())
