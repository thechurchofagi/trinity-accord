#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("trinity_record_chain_deep_tx", ROOT / "scripts" / "trinity_record_chain.py")
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def _redirect(tmp: Path) -> None:
    mod.ROOT = tmp
    mod.CHAIN = tmp / "record-chain"
    mod.GENESIS = mod.CHAIN / "genesis"
    mod.LEGACY_RECORDS = mod.GENESIS / "legacy-records"
    mod.RECORDS = mod.CHAIN / "records"
    mod.PENDING = mod.CHAIN / "pending"
    mod.PROCESSED = mod.CHAIN / "processed"
    mod.REJECTED = mod.CHAIN / "rejected"
    mod.RECEIPT_STATUS = mod.CHAIN / "receipt-status"
    mod.BATCHES = mod.CHAIN / "batches"
    mod.INDEXES = mod.CHAIN / "indexes"
    mod.POLICIES = mod.CHAIN / "policies"
    mod.SCHEMAS = mod.CHAIN / "schemas"
    mod.CHAIN_TIP = mod.CHAIN / "chain-tip.json"
    mod.ANCHORS = mod.CHAIN / "anchors"
    mod.ARWEAVE_ARCHIVES = mod.CHAIN / "arweave-archives"
    mod.ANCHOR_STATUS_API = tmp / "api" / "record-chain-anchor-status.json"
    mod.ARWEAVE_INDEX_API = tmp / "api" / "record-chain-arweave-index.json"
    mod.GUARDIAN_REGISTRY = tmp / "api" / "guardian-registry.json"
    mod.ensure_dirs()


def _write_gateway_transaction(tmp: Path, *, pending_written: bool = True, stored_tampered: bool = False) -> Path:
    receipt_id = "rcg-20260712-" + "a" * 24
    submission_sha = "a" * 64
    stored_submission = {"record_type": "echo", "record_draft": {"record_type": "echo"}}
    stored_sha = mod.sha256_gateway_canonical_json(stored_submission)
    pending_rel = f"record-chain/pending/{receipt_id}.echo.pending.json"
    receipt_rel = f"record-chain/intake/receipts/2026/07/{receipt_id}.receipt.json"
    intake_rel = f"record-chain/intake/submissions/2026/07/{receipt_id}.submission.json"
    pending_path = tmp / pending_rel
    receipt_path = tmp / receipt_rel
    intake_path = tmp / intake_rel
    mod.write_json(pending_path, {"record_type": "echo"})
    mod.write_json(intake_path, {"record_type": "tampered"} if stored_tampered else stored_submission)
    receipt = {
        "server_receipt_id": receipt_id,
        "record_type": "echo",
        "submission_sha256": submission_sha,
        "original_submission_sha256": submission_sha,
        "stored_submission_sha256": stored_sha,
        "pending_file_path": pending_rel,
        "receipt_path": receipt_rel,
        "intake_submission_path": intake_rel,
    }
    receipt["receipt_sha256"] = mod.sha256_bytes(json.dumps(receipt, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8"))
    mod.write_json(receipt_path, receipt)
    mod.write_json(mod.CHAIN / "intake" / "by-submission-sha256" / f"{submission_sha}.json", {
        "schema": "trinityaccord.record-chain-intake-idempotency.v1",
        "submission_sha256": submission_sha,
        "stored_submission_sha256": stored_sha,
        "receipt_id": receipt_id,
        "receipt_path": receipt_rel,
        "pending_file_path": pending_rel,
        "intake_submission_path": intake_rel,
        "record_type": "echo",
        "receipt_written": True,
        "idempotency_written": True,
        "pending_written": pending_written,
        "transaction_state": "pending_written" if pending_written else "idempotency_written",
        "pending_committed_at": "2026-07-12T00:00:00Z" if pending_written else None,
    })
    return pending_path


def test_append_binding_rejects_unmaterialized_pending() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="trinity-deep-tx-"))
    try:
        _redirect(tmp)
        pending = _write_gateway_transaction(tmp, pending_written=False)
        try:
            mod.require_gateway_pending_durable_intake_binding(pending)
        except ValueError as exc:
            assert "pending_written" in str(exc)
        else:
            raise AssertionError("unmaterialized pending was accepted")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_append_binding_rejects_tampered_stored_submission() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="trinity-deep-tx-"))
    try:
        _redirect(tmp)
        pending = _write_gateway_transaction(tmp, stored_tampered=True)
        try:
            mod.require_gateway_pending_durable_intake_binding(pending)
        except ValueError as exc:
            assert "stored submission sha256 mismatch" in str(exc)
        else:
            raise AssertionError("tampered stored submission was accepted")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_correction_target_binding_fails_before_mutation() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="trinity-deep-target-"))
    try:
        _redirect(tmp)
        draft = {
            "record_type": "correction",
            "correction_content": {
                "target_record_id": "R-000000001",
                "target_record_sha256": "a" * 64,
            },
        }
        try:
            mod.require_record_target_binding(draft)
        except ValueError as exc:
            assert "does not exist" in str(exc)
        else:
            raise AssertionError("missing correction target was accepted")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)



def _write_minimal_genesis_tip() -> None:
    genesis_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    mod.write_json(mod.GENESIS / "genesis-batch-manifest.json", {
        "schema": "trinityaccord.record-batch-manifest.v1",
        "batch_id": "genesis",
        "batch_manifest_sha256": genesis_hash,
    })
    mod.write_json(mod.CHAIN_TIP, {
        "schema": "trinityaccord.chain-tip.v1",
        "chain_id": mod.CHAIN_ID,
        "native_record_count": 0,
        "latest_record_index": 0,
        "latest_record_id": None,
        "latest_record_sha256": None,
        "genesis_batch_manifest_sha256": genesis_hash,
        "latest_batch_manifest_sha256": genesis_hash,
        "updated_at": mod.utc_now(),
    })


def test_append_binding_accepts_fully_materialized_transaction() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="trinity-deep-tx-"))
    try:
        _redirect(tmp)
        pending = _write_gateway_transaction(tmp)
        mod.require_gateway_pending_durable_intake_binding(pending)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_post_mutation_io_failure_is_never_recorded_as_rejection() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="trinity-deep-io-"))
    backups = {}
    try:
        _redirect(tmp)
        _write_minimal_genesis_tip()
        pending = mod.PENDING / "mainnet-prelaunch-io-failure.json"
        mod.write_json(pending, {"record_type": "echo"})
        os.environ["TRINITY_ALLOW_LOCAL_FINALIZER_PENDING"] = "1"

        for name in [
            "require_not_reserved_record_type",
            "verify_pending_record_authorship",
            "sanitize_pending_record_for_append",
            "normalize_record_draft",
            "verify_native_records",
            "build_indexes",
        ]:
            backups[name] = getattr(mod, name)
        backups["write_json"] = mod.write_json
        mod.require_not_reserved_record_type = lambda draft: None
        mod.verify_pending_record_authorship = lambda draft: None
        mod.sanitize_pending_record_for_append = lambda draft: dict(draft)
        mod.normalize_record_draft = lambda draft: dict(draft)
        mod.verify_native_records = lambda: []
        mod.build_indexes = lambda *args, **kwargs: None

        original_write_json = backups["write_json"]
        def failing_write_json(path, obj):
            if path == mod.CHAIN_TIP:
                raise OSError("simulated chain-tip write failure")
            original_write_json(path, obj)
        mod.write_json = failing_write_json

        try:
            mod.append_records(all_records=False)
        except SystemExit as exc:
            assert "not semantically rejected" in str(exc)
        else:
            raise AssertionError("post-mutation I/O failure did not stop append")
        assert not list(mod.REJECTED.glob("*.rejection.json")), "internal failure was written as semantic rejection"
        assert not list(mod.RECEIPT_STATUS.glob("*.json")), "internal failure wrote a false final status"
    finally:
        os.environ.pop("TRINITY_ALLOW_LOCAL_FINALIZER_PENDING", None)
        for name, value in backups.items():
            setattr(mod, name, value)
        shutil.rmtree(tmp, ignore_errors=True)


def test_lifecycle_verifier_detects_unmaterialized_index() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="trinity-deep-life-"))
    try:
        _redirect(tmp)
        _write_gateway_transaction(tmp, pending_written=False)
        errors = mod.verify_intake_lifecycle()
        assert any("not materialized" in error for error in errors), errors
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def test_internal_append_failure_is_not_semantic_rejection() -> None:
    assert mod.is_semantic_append_rejection(ValueError("bad input")) is True
    assert mod.is_semantic_append_rejection(OSError("disk failed")) is False
    assert mod.is_semantic_append_rejection(RuntimeError("bug")) is False


if __name__ == "__main__":
    for test in [
        test_append_binding_rejects_unmaterialized_pending,
        test_append_binding_rejects_tampered_stored_submission,
        test_append_binding_accepts_fully_materialized_transaction,
        test_post_mutation_io_failure_is_never_recorded_as_rejection,
        test_lifecycle_verifier_detects_unmaterialized_index,
        test_correction_target_binding_fails_before_mutation,
        test_internal_append_failure_is_not_semantic_rejection,
    ]:
        test()
    print("PASS: deep intake/append transaction invariants")
