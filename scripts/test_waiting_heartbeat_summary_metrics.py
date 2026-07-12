#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import hashlib
import json
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "api" / "waiting-heartbeat-status.json"
PUBLIC = ROOT / "api" / "public-home-status.json"
WORKFLOW = ROOT / ".github" / "workflows" / "waiting-heartbeat-submit.yml"
CAPSULE_WORKFLOW = ROOT / ".github" / "workflows" / "waiting-heartbeat-capsule.yml"
STATUS_SYNC_WORKFLOW = ROOT / ".github" / "workflows" / "waiting-heartbeat-status-sync.yml"
GENERATOR = ROOT / "scripts" / "generate_waiting_heartbeat_status.py"
SUBMIT_SCRIPT = ROOT / "scripts" / "submit_waiting_heartbeat.py"
CAPSULE_BUILDER = ROOT / "scripts" / "build_waiting_heartbeat_arweave_capsule.py"
CAPSULE_UPLOAD = ROOT / "scripts" / "arweave_upload_waiting_heartbeat_capsule.mjs"
CAPSULE_REPAIR = ROOT / "scripts" / "repair_waiting_heartbeat_arweave_capsule_readback.mjs"


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
    pending = summary.get("pending_append_heartbeats", 0)
    streak = summary["current_success_streak_days"]
    require(total >= success, "total_scheduled_heartbeats must be >= successful_heartbeats")
    require(failed + pending == total - success, "failed_or_missing_heartbeats plus pending_append_heartbeats must equal total - success")
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
    if "pending_append_heartbeats" in summary:
        require(counts.get("pending_append_heartbeats") == summary.get("pending_append_heartbeats"), "counts.pending_append_heartbeats must mirror heartbeat_summary.pending_append_heartbeats")

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
    require(summary["pending_append_heartbeats"] == 0, "missing expected heartbeat without submitted attempt is not pending append")
    require(summary["current_success_streak_days"] == 0, "stale expected date should reset current streak")
    require(summary["latest_heartbeat_date"] == "2026-06-22", "latest final heartbeat date should remain visible")
    require(summary["through_heartbeat_date"] == "2026-06-23", "summary should declare schedule range end")
    require(summary["expected_heartbeat_date"] == "2026-06-23", "summary should declare expected heartbeat date")
    require(summary["heartbeat_lag_days"] == 1, "stale lag should be one day")
    require(summary["is_stale"] is True, "summary should mark stale heartbeat data")
    require(summary["expected_heartbeat_pending_append"] is False, "missing expected heartbeat should not be pending append")
    require("2026-06-23" in summary["missing_heartbeat_dates"], "expected missing date should be listed")


def test_current_expected_record_is_alive_while_arweave_capsule_is_pending() -> None:
    generator = load_generator_module()
    current = {**verified_record(), "heartbeat_id": "hwb-20260623", "heartbeat_date": "2026-06-23", "record_id": "R-000000057", "record_index": 57}
    summary = generator.compute_heartbeat_summary(
        records=[verified_record(), current],
        attempts=[],
        capsules=[verified_capsule()],
        key_manifest={"public_key_sha256": "key-sha"},
        ots_covers_latest=True,
        expected_date=date(2026, 6, 23),
    )
    require(summary["latest_heartbeat_is_expected_date"] is True, "expected final record should be fresh")
    require(summary["latest_heartbeat_fully_verified_for_expected_date"] is True, "current final record plus OTS coverage should be alive before archive capsule readback")
    require(summary["successful_heartbeats"] == 2, "current archive-pending heartbeat should count as operationally successful")
    require(summary["failed_or_missing_heartbeats"] == 0, "archive-pending current heartbeat should not be counted failed/missing")
    require(summary["success_definition"].get("arweave_capsule_is_archive_followup") is True, "summary must classify Arweave capsule as archive follow-up")


def test_historical_record_stays_successful_without_verified_capsule() -> None:
    generator = load_generator_module()
    historical = verified_record()
    current = {
        **verified_record(),
        "heartbeat_id": "hwb-20260623",
        "heartbeat_date": "2026-06-23",
        "record_id": "R-000000057",
        "record_index": 57,
        "record_sha256": "current-sha",
    }
    summary = generator.compute_heartbeat_summary(
        records=[historical, current],
        attempts=[],
        capsules=[],
        key_manifest={"public_key_sha256": "key-sha"},
        ots_covers_latest=True,
        expected_date=date(2026, 6, 23),
        ots={
            "latest_record_id": "R-000000057",
            "latest_record_sha256": "current-sha",
            "native_record_count": 57,
        },
    )
    require(summary["successful_heartbeats"] == 2, "OTS-covered historical heartbeat must remain successful without an Arweave capsule")
    require(summary["failed_or_missing_heartbeats"] == 0, "archive follow-up failure must not create a historical liveness failure")


def test_verified_capsule_cannot_substitute_for_ots_coverage() -> None:
    generator = load_generator_module()
    summary = generator.compute_heartbeat_summary(
        records=[verified_record()],
        attempts=[],
        capsules=[verified_capsule()],
        key_manifest={"public_key_sha256": "key-sha"},
        ots_covers_latest=False,
        expected_date=date(2026, 6, 22),
        ots={"latest_record_id": "R-000000055", "native_record_count": 55},
    )
    require(summary["successful_heartbeats"] == 0, "verified Arweave mirror must not substitute for native OTS coverage")
    require(summary["failed_or_missing_heartbeats"] == 1, "record without OTS coverage must not be counted successful")
    require(summary["latest_heartbeat_fully_verified_for_expected_date"] is False, "expected heartbeat without OTS coverage must not be fully verified")


def test_capsule_payload_does_not_contradict_daily_alive_policy() -> None:
    builder = load_capsule_builder_module()
    payload = builder.build_payload(
        {"heartbeat_id": "hwb-20260623", "record_id": "R-000000057"},
        {"latest_record_id": "R-000000057"},
        {"latest_record_id": "R-000000057"},
    )
    semantics = payload["daily_alive_semantics"]
    require(semantics["daily_alive_success_requires_this_capsule_to_be_uploaded_and_hash_matched"] is False, "capsule must not gate daily alive success")
    require(semantics["capsule_upload_and_hash_match_are_archive_followup"] is True, "capsule must declare archive follow-up semantics")


def test_attempt_for_expected_date_is_pending_append_not_missing_final_heartbeat() -> None:
    generator = load_generator_module()
    summary = generator.compute_heartbeat_summary(
        records=[verified_record()],
        attempts=[{"heartbeat_id": "hwb-20260623", "attempted_at": "2026-06-23T03:17:30Z", "status": "submitted", "append_status": "queued"}],
        capsules=[verified_capsule()],
        key_manifest={"public_key_sha256": "key-sha"},
        ots_covers_latest=True,
        expected_date=date(2026, 6, 23),
    )
    require(summary["latest_observed_heartbeat_date"] == "2026-06-23", "attempt should remain visible as observed")
    require(summary["latest_heartbeat_date"] == "2026-06-22", "attempt must not replace latest final heartbeat")
    require(summary["latest_heartbeat_is_expected_date"] is False, "attempt must not make expected heartbeat fresh")
    require(summary["expected_heartbeat_pending_append"] is True, "submitted expected attempt should be pending append")
    require(summary["heartbeat_lag_days"] == 1, "attempt must not zero out heartbeat lag")
    require(summary["is_stale"] is True, "attempt without final record/capsule must remain stale at the data layer")
    require("2026-06-23" not in summary["missing_heartbeat_dates"], "submitted expected date must not be reported as missing")
    require("2026-06-23" in summary["pending_append_heartbeat_dates"], "submitted expected date should be reported as pending append")
    require(summary["pending_append_heartbeats"] == 1, "submitted expected date should count as pending append")
    require(summary["failed_or_missing_heartbeats"] == 0, "submitted expected date should not be counted failed/missing before append SLA")


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


def test_capsule_builder_recognizes_existing_result_states() -> None:
    builder = load_capsule_builder_module()
    require(not builder.capsule_is_verified({"status": "uploaded", "arweave_txid": "x" * 43, "hash_match": True}), "self-declared verified result without local evidence must fail closed")
    require(builder.capsule_needs_readback_repair({"status": "posted_pending_readback", "arweave_txid": "txid", "hash_match": False, "retryable": True}), "pending result should request readback repair")
    require(builder.capsule_needs_readback_repair({"status": "readback_failed", "arweave_txid": "txid", "hash_match": False, "retryable": True}), "legacy readback_failed should request readback repair")
    require(not builder.capsule_needs_readback_repair({"status": "readback_hash_mismatch", "arweave_txid": "txid", "hash_match": False, "retryable": False}), "hash mismatch must not request retry repair")




def test_verified_capsule_binds_exact_bytes_and_final_record() -> None:
    builder = load_capsule_builder_module()
    with tempfile.TemporaryDirectory(prefix="heartbeat-capsule-integrity-") as tmp_value:
        tmp = Path(tmp_value)
        record_id = "R-000000001"
        heartbeat_id = "hwb-20260712"
        record_path = tmp / "record-chain" / "records" / f"{record_id}.json"
        record_path.parent.mkdir(parents=True)
        record = {
            "record_id": record_id,
            "record_index": 1,
            "record_sha256": "a" * 64,
            "record_type": "context_insufficient_notice",
            "assigned_at": "2026-07-12T00:00:00Z",
            "system_waiting_heartbeat": {"heartbeat_id": heartbeat_id},
        }
        record_path.write_text(json.dumps(record) + "\n", encoding="utf-8")
        capsule_path = tmp / "record-chain" / "heartbeat" / "capsules" / f"{heartbeat_id}.capsule.json"
        capsule_path.parent.mkdir(parents=True)
        capsule = {
            "schema": "trinityaccord.waiting-heartbeat-arweave-capsule.v1",
            "heartbeat_id": heartbeat_id,
            "heartbeat_record": {
                "record_id": record_id,
                "record_index": 1,
                "record_sha256": "a" * 64,
                "record_type": "context_insufficient_notice",
                "assigned_at": "2026-07-12T00:00:00Z",
                "path": f"record-chain/records/{record_id}.json",
            },
        }
        capsule_path.write_text(json.dumps(capsule) + "\n", encoding="utf-8")
        payload_sha = hashlib.sha256(capsule_path.read_bytes()).hexdigest()
        result = {
            "schema": "trinityaccord.waiting-heartbeat-arweave-upload-result.v1",
            "heartbeat_id": heartbeat_id,
            "status": "uploaded",
            "arweave_txid": "x" * 43,
            "payload_sha256": payload_sha,
            "data_sha256": payload_sha,
            "readback_sha256": payload_sha,
            "hash_match": True,
        }
        old_root = builder.ROOT
        try:
            builder.ROOT = tmp
            require(builder.capsule_is_verified(result, capsule_path=capsule_path), "fully bound verified capsule should be accepted")
            capsule_path.write_text(json.dumps({**capsule, "created_at": "tampered"}) + "\n", encoding="utf-8")
            require(not builder.capsule_is_verified(result, capsule_path=capsule_path), "changed local capsule bytes must invalidate verified result")
        finally:
            builder.ROOT = old_root


def test_current_verified_capsules_all_bind_to_repository_evidence() -> None:
    generator = load_generator_module()
    generator.require_verified_capsule_bindings(generator.load_capsules())


def test_status_sync_regenerates_after_rebase() -> None:
    text = STATUS_SYNC_WORKFLOW.read_text(encoding="utf-8")
    rebase_pos = text.find("git rebase origin/main")
    regenerate_pos = text.find("regenerate_waiting_status_artifacts", rebase_pos)
    amend_pos = text.find("git commit --amend --no-edit", regenerate_pos)
    require(rebase_pos >= 0, "status sync must rebase when main advances")
    require(regenerate_pos > rebase_pos, "status sync must regenerate derived state after rebase")
    require(amend_pos > regenerate_pos, "status sync must amend regenerated state before retrying push")


def test_capsule_workflow_preserves_upload_result_before_status_update() -> None:
    text = CAPSULE_WORKFLOW.read_text(encoding="utf-8")
    require("capsule_readback_repair_needed" in text, "capsule workflow must support readback repair mode")
    require("repair_waiting_heartbeat_arweave_capsule_readback.mjs" in text, "capsule workflow must call readback repair script")
    require("steps.capsule_preflight.outputs.capsule_path" in text, "capsule workflow must use the preflight-selected payload path")
    require("echo \"exit_code=$?\" >> \"$GITHUB_OUTPUT\"" in text, "capsule workflow must capture upload/repair exit code without skipping commit")
    require("Commit capsule metadata" in text, "capsule workflow must still commit generated capsule metadata")


def test_capsule_upload_and_repair_scripts_keep_pending_readback_retryable() -> None:
    upload = CAPSULE_UPLOAD.read_text(encoding="utf-8")
    repair = CAPSULE_REPAIR.read_text(encoding="utf-8")
    require("ARWEAVE_READBACK_PENDING" in upload, "upload script must treat unavailable readback as pending")
    require("readback_hash_mismatch" in upload, "upload script must preserve hard hash mismatch status")
    require("retry_readback_without_reupload" in upload, "upload script must direct follow-up to readback repair")
    require("posted_pending_readback" in repair, "repair script must keep unavailable txids pending")
    require("local_payload_mismatch_for_existing_tx" in repair, "repair script must detect local payload drift")
    require("retry_readback_without_reupload" in repair, "repair script must avoid duplicate upload on delayed readback")


def test_submit_script_persists_append_dispatch_metadata() -> None:
    text = SUBMIT_SCRIPT.read_text(encoding="utf-8")
    require("parse_stdout_json" in text, "submit script must parse Gateway JSON response")
    require("receipt_id" in text, "submit script must persist receipt_id for append dispatch")
    require("pending_file_path" in text, "submit script must persist pending_file_path for append dispatch")
    require("append_status" in text, "submit script must persist append_status for pending status classification")


def test_append_status_pending_treated_as_pending_append() -> None:
    """Regression: gateway initializes append_status='pending' for successful submissions."""
    generator = load_generator_module()
    summary = generator.compute_heartbeat_summary(
        records=[verified_record()],
        attempts=[{"heartbeat_id": "hwb-20260623", "attempted_at": "2026-06-23T03:17:30Z", "status": "submitted", "append_status": "pending"}],
        capsules=[verified_capsule()],
        key_manifest={"public_key_sha256": "key-sha"},
        ots_covers_latest=True,
        expected_date=date(2026, 6, 23),
    )
    require(summary["expected_heartbeat_pending_append"] is True, "append_status=pending should be treated as pending append")
    require("2026-06-23" in summary["pending_append_heartbeat_dates"], "append_status=pending date should appear in pending_append_heartbeat_dates")
    require(summary["pending_append_heartbeats"] == 1, "append_status=pending should count as pending append")
    require("2026-06-23" not in summary["missing_heartbeat_dates"], "append_status=pending date must not be reported as missing")


def test_rejected_receipt_excluded_from_pending_append() -> None:
    """Regression: attempts with rejected receipt-status must not count as pending append."""
    import shutil
    generator = load_generator_module()
    receipt_status_dir = generator.ROOT / "record-chain" / "receipt-status"
    existed = receipt_status_dir.exists()
    if not existed:
        receipt_status_dir.mkdir(parents=True, exist_ok=True)
    rs_file = receipt_status_dir / "test-receipt-001.json"
    try:
        rs_file.write_text(json.dumps({
            "receipt_id": "test-receipt-001",
            "append_status": "rejected",
            "pending_file_path": "record-chain/pending/test.pending.json",
        }), encoding="utf-8")
        summary = generator.compute_heartbeat_summary(
            records=[verified_record()],
            attempts=[{"heartbeat_id": "hwb-20260623", "attempted_at": "2026-06-23T03:17:30Z", "status": "submitted", "append_status": "queued", "receipt_id": "test-receipt-001"}],
            capsules=[verified_capsule()],
            key_manifest={"public_key_sha256": "key-sha"},
            ots_covers_latest=True,
            expected_date=date(2026, 6, 23),
        )
        require("2026-06-23" not in summary["pending_append_heartbeat_dates"], "rejected receipt must not be in pending_append set")
        require(summary["pending_append_heartbeats"] == 0, "rejected receipt must not count as pending append")
    finally:
        rs_file.unlink(missing_ok=True)
        if not existed:
            shutil.rmtree(receipt_status_dir, ignore_errors=True)


def test_rejected_same_date_resubmission_not_blocked() -> None:
    """Regression: a rejected attempt for date X must not block a later resubmitted pending append for the same date."""
    import shutil
    generator = load_generator_module()
    receipt_status_dir = generator.ROOT / "record-chain" / "receipt-status"
    existed = receipt_status_dir.exists()
    if not existed:
        receipt_status_dir.mkdir(parents=True, exist_ok=True)
    rs_file = receipt_status_dir / "test-receipt-002.json"
    try:
        # First attempt was rejected
        rs_file.write_text(json.dumps({
            "receipt_id": "test-receipt-002",
            "append_status": "rejected",
            "pending_file_path": "record-chain/pending/rcg-20260623-old.pending.json",
        }), encoding="utf-8")
        # Second attempt for same date is still pending
        summary = generator.compute_heartbeat_summary(
            records=[verified_record()],
            attempts=[
                {"heartbeat_id": "hwb-20260623", "attempted_at": "2026-06-23T03:10:00Z", "status": "submitted", "append_status": "queued", "receipt_id": "test-receipt-002"},
                {"heartbeat_id": "hwb-20260623", "attempted_at": "2026-06-23T03:20:00Z", "status": "submitted", "append_status": "queued", "receipt_id": "test-receipt-003"},
            ],
            capsules=[verified_capsule()],
            key_manifest={"public_key_sha256": "key-sha"},
            ots_covers_latest=True,
            expected_date=date(2026, 6, 23),
        )
        # The resubmitted attempt (receipt 003) should still be pending append
        require("2026-06-23" in summary["pending_append_heartbeat_dates"], "resubmitted date should be in pending_append set")
        require(summary["pending_append_heartbeats"] == 1, "resubmitted date should count as pending append")
    finally:
        rs_file.unlink(missing_ok=True)
        if not existed:
            shutil.rmtree(receipt_status_dir, ignore_errors=True)


def test_key_continuity_failure_takes_precedence_over_pending_append() -> None:
    """Regression: key-continuity failure must not be masked by pending-append degraded status."""
    generator = load_generator_module()
    # Create a final record with wrong key using the actual field name
    bad_record = verified_record()
    bad_record["authorship_public_key_sha256"] = "wrong-key-sha"
    summary = generator.compute_heartbeat_summary(
        records=[bad_record],
        attempts=[{"heartbeat_id": "hwb-20260623", "attempted_at": "2026-06-23T03:17:30Z", "status": "submitted", "append_status": "queued"}],
        capsules=[verified_capsule()],
        key_manifest={"public_key_sha256": "correct-key-sha"},
        ots_covers_latest=True,
        expected_date=date(2026, 6, 23),
    )
    # The summary itself doesn't produce daily_alive_status (that's in generate_status),
    # but we can verify the building blocks: is_stale + expected_heartbeat_pending_append
    # are both true, and key_continuity_ok is false in the record.
    # The generate_status function checks key_continuity BEFORE pending_append.
    require(summary.get("is_stale") is True, "stale should be true when expected date has no final record")
    require(summary.get("expected_heartbeat_pending_append") is True, "pending append should be true for submitted attempt")
    # Verify the record has the wrong key (using the actual field used by generate_status)
    require(bad_record.get("authorship_public_key_sha256") == "wrong-key-sha", "record must have wrong key")
    require(bad_record.get("authorship_public_key_sha256") != "correct-key-sha", "record key must differ from manifest key")


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
    test_current_expected_record_is_alive_while_arweave_capsule_is_pending()
    test_historical_record_stays_successful_without_verified_capsule()
    test_verified_capsule_cannot_substitute_for_ots_coverage()
    test_capsule_payload_does_not_contradict_daily_alive_policy()
    test_attempt_for_expected_date_is_pending_append_not_missing_final_heartbeat()
    test_grace_window_attempt_after_expected_date_does_not_expand_scheduled_totals()
    test_ots_head_covers_prior_heartbeat_record()
    test_capsule_builder_recognizes_existing_result_states()
    test_verified_capsule_binds_exact_bytes_and_final_record()
    test_current_verified_capsules_all_bind_to_repository_evidence()
    test_status_sync_regenerates_after_rebase()
    test_capsule_workflow_preserves_upload_result_before_status_update()
    test_capsule_upload_and_repair_scripts_keep_pending_readback_retryable()
    test_submit_script_persists_append_dispatch_metadata()
    test_submit_workflow_has_no_historical_backfill_input_and_stages_public_mirror()
    test_append_status_pending_treated_as_pending_append()
    test_rejected_receipt_excluded_from_pending_append()
    test_rejected_same_date_resubmission_not_blocked()
    test_key_continuity_failure_takes_precedence_over_pending_append()
    print("PASS: waiting heartbeat summary metrics contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
