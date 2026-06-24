#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "api" / "waiting-heartbeat-status.json"
PUBLIC = ROOT / "api" / "public-home-status.json"
WORKFLOW = ROOT / ".github" / "workflows" / "waiting-heartbeat-submit.yml"
GENERATOR = ROOT / "scripts" / "generate_waiting_heartbeat_status.py"
CAPSULE_BUILDER = ROOT / "scripts" / "build_waiting_heartbeat_arweave_capsule.py"


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"could not load {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_generator_module():
    return load_module(GENERATOR, "generate_waiting_heartbeat_status")


def load_capsule_builder_module():
    return load_module(CAPSULE_BUILDER, "build_waiting_heartbeat_arweave_capsule")


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

    for key in ["not_reception_counter", "not_authority", "not_attestation", "not_amendment"]:
        require(summary.get(key) is True, f"heartbeat_summary.{key} must be true")


def test_expected_heartbeat_date_respects_schedule_grace_window() -> None:
    generator = load_generator_module()
    require(generator.expected_heartbeat_date(datetime(2026, 6, 24, 1, 32, tzinfo=timezone.utc)) == date(2026, 6, 23), "before due should expect previous UTC date")
    require(generator.expected_heartbeat_date(datetime(2026, 6, 24, 3, 17, tzinfo=timezone.utc)) == date(2026, 6, 23), "at due should still be grace window")
    require(generator.expected_heartbeat_date(datetime(2026, 6, 24, 4, 46, tzinfo=timezone.utc)) == date(2026, 6, 23), "inside grace should still expect previous UTC date")
    require(generator.expected_heartbeat_date(datetime(2026, 6, 24, 4, 47, tzinfo=timezone.utc)) == date(2026, 6, 24), "after grace should expect current UTC date")


def verified_record() -> dict[str, object]:
    return {
        "heartbeat_id": "hwb-20260622",
        "heartbeat_date": "2026-06-22",
        "record_id": "R-000000056",
        "record_index": 56,
        "record_sha256": "sha",
        "authorship_public_key_sha256": "key-sha",
    }


def verified_capsule() -> dict[str, object]:
    return {"heartbeat_id": "hwb-20260622", "status": "uploaded", "arweave_txid": "txid", "hash_match": True}


def test_summary_extends_to_expected_date_when_latest_observed_is_stale() -> None:
    generator = load_generator_module()
    summary = generator.compute_heartbeat_summary(
        records=[verified_record()],
        attempts=[],
        capsules=[verified_capsule()],
        key_manifest={"public_key_sha256": "key-sha"},
        ots_covers_latest=True,
        expected_date=date(2026, 6, 23),
    )
    require(summary["total_scheduled_heartbeats"] == 2, "summary should extend through expected heartbeat date")
    require(summary["successful_heartbeats"] == 1, "only observed verified heartbeat should be successful")
    require(summary["failed_or_missing_heartbeats"] == 1, "missing expected heartbeat should be counted failed/missing")
    require(summary["current_success_streak_days"] == 0, "stale expected date should reset current streak")
    require(summary["latest_heartbeat_date"] == "2026-06-22", "latest final heartbeat date should remain visible")
    require(summary["through_heartbeat_date"] == "2026-06-23", "summary should declare schedule range end")
    require(summary["expected_heartbeat_date"] == "2026-06-23", "summary should declare expected heartbeat date")
    require(summary["heartbeat_lag_days"] == 1, "stale lag should be one day")
    require(summary["is_stale"] is True, "summary should mark stale heartbeat data")
    require("2026-06-23" in summary["missing_heartbeat_dates"], "expected missing date should be listed")


def test_attempt_for_expected_date_does_not_mask_missing_final_heartbeat() -> None:
    generator = load_generator_module()
    summary = generator.compute_heartbeat_summary(
        records=[verified_record()],
        attempts=[{"heartbeat_id": "hwb-20260623", "attempted_at": "2026-06-23T03:17:30Z", "status": "submitted"}],
        capsules=[verified_capsule()],
        key_manifest={"public_key_sha256": "key-sha"},
        ots_covers_latest=True,
        expected_date=date(2026, 6, 23),
    )
    require(summary["latest_observed_heartbeat_date"] == "2026-06-23", "attempt should remain visible as observed")
    require(summary["latest_heartbeat_date"] == "2026-06-22", "attempt must not replace latest final heartbeat")
    require(summary["latest_heartbeat_is_expected_date"] is False, "attempt must not make expected heartbeat fresh")
    require(summary["heartbeat_lag_days"] == 1, "attempt must not zero out heartbeat lag")
    require(summary["is_stale"] is True, "attempt without final record/capsule must remain stale")
    require("2026-06-23" in summary["missing_heartbeat_dates"], "expected date without final record must be missing")


def test_grace_window_attempt_after_expected_date_does_not_expand_scheduled_totals() -> None:
    generator = load_generator_module()
    summary = generator.compute_heartbeat_summary(
        records=[verified_record()],
        attempts=[{"heartbeat_id": "hwb-20260624", "attempted_at": "2026-06-24T03:18:00Z", "status": "submitted"}],
        capsules=[verified_capsule()],
        key_manifest={"public_key_sha256": "key-sha"},
        ots_covers_latest=True,
        expected_date=date(2026, 6, 23),
    )
    require(summary["latest_observed_heartbeat_date"] == "2026-06-24", "grace-window attempt should remain visible as observed")
    require(summary["through_heartbeat_date"] == "2026-06-23", "post-expected attempt must not extend scheduled totals")
    require(summary["total_scheduled_heartbeats"] == 2, "post-expected attempt must not add a scheduled day")
    require("2026-06-24" not in summary["missing_heartbeat_dates"], "post-expected attempt must not be marked missing inside grace")


def test_ots_head_covers_prior_heartbeat_record() -> None:
    generator = load_generator_module()
    builder = load_capsule_builder_module()
    heartbeat = {"record_id": "R-000000056", "record_index": 56, "record_sha256": "sha"}
    for module in [generator, builder]:
        require(module.ots_covers_record({"latest_record_id": "R-000000056", "latest_record_sha256": "sha"}, heartbeat), "exact OTS match should cover heartbeat")
        require(not module.ots_covers_record({"latest_record_id": "R-000000056", "latest_record_sha256": "other"}, heartbeat), "exact OTS id with wrong sha must not cover heartbeat")
        require(module.ots_covers_record({"latest_record_id": "R-000000057", "native_record_count": 57}, heartbeat), "advanced OTS head should cover prior heartbeat")
        require(not module.ots_covers_record({"latest_record_id": "R-000000055", "native_record_count": 55}, heartbeat), "earlier OTS head must not cover later heartbeat")


def test_submit_workflow_has_no_historical_backfill_input_and_stages_public_mirror() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    require("github.event.inputs.date" not in text, "submit workflow must not accept historical date input")
    require("HEARTBEAT_DATE" not in text, "submit workflow must not thread manual date input")
    require("--date" not in text, "submit workflow must not call heartbeat submit with manual backfill date")
    require("api/public-home-status.json" in text, "submit workflow must stage public-home-status mirror")
    require("index.md" in text, "submit workflow must stage homepage markdown mirror")
    require("sitemap.xml" in text, "submit workflow must stage sitemap mirror")


def main() -> int:
    test_current_status_contract()
    test_expected_heartbeat_date_respects_schedule_grace_window()
    test_summary_extends_to_expected_date_when_latest_observed_is_stale()
    test_attempt_for_expected_date_does_not_mask_missing_final_heartbeat()
    test_grace_window_attempt_after_expected_date_does_not_expand_scheduled_totals()
    test_ots_head_covers_prior_heartbeat_record()
    test_submit_workflow_has_no_historical_backfill_input_and_stages_public_mirror()
    print("PASS: waiting heartbeat summary metrics contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
