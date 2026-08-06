from __future__ import annotations

import json

import pytest

from apps.record_chain_intake_gateway import app as core_gateway
from apps.record_chain_intake_gateway import secure_entrypoint
from apps.record_chain_intake_gateway.gateway.receipts import compute_receipt_sha256


@pytest.fixture(autouse=True)
def reset_recovery_state() -> None:
    with secure_entrypoint._read_state_lock:
        secure_entrypoint._recovery_cache.clear()
        secure_entrypoint._recovery_active = 0


def intake_artifacts() -> tuple[str, str, dict, dict, dict]:
    submission_sha256 = "a" * 64
    receipt_id = "rcg-20260718-" + submission_sha256[:24]
    record_type = "echo"
    receipt_path = (
        "record-chain/intake/receipts/2026/07/"
        f"{receipt_id}.receipt.json"
    )
    submission_path = (
        "record-chain/intake/submissions/2026/07/"
        f"{receipt_id}.submission.json"
    )
    pending_path = f"record-chain/pending/{receipt_id}.{record_type}.pending.json"
    stored_submission = {
        "schema": "trinityaccord.record-chain-submission.v2",
        "submission_type": "record_chain_entry",
        "record_type": record_type,
        "record_draft": {"record_type": record_type, "message": "test"},
    }
    stored_sha256 = core_gateway.sha256_canonical_json(stored_submission)
    receipt = {
        "server_receipt_id": receipt_id,
        "service": "record-chain-intake-gateway",
        "gateway_version": "1.0.0",
        "record_type": record_type,
        "submission_sha256": submission_sha256,
        "original_submission_sha256": submission_sha256,
        "stored_submission_sha256": stored_sha256,
        "received_raw_body_sha256": "b" * 64,
        "accepted_at": "2026-07-18T00:00:00Z",
        "raw_readback_redacted": True,
        "receipt_is_not_final_chain_record": True,
        "intake_submission_path": submission_path,
        "pending_file_path": pending_path,
        "receipt_path": receipt_path,
    }
    receipt["receipt_sha256"] = compute_receipt_sha256(receipt)
    index = {
        "schema": "trinityaccord.record-chain-intake-idempotency.v1",
        "submission_sha256": submission_sha256,
        "stored_submission_sha256": stored_sha256,
        "receipt_id": receipt_id,
        "receipt_path": receipt_path,
        "pending_file_path": pending_path,
        "intake_submission_path": submission_path,
        "record_type": record_type,
        "created_at": "2026-07-18T00:00:00Z",
        "transaction_state": "pending_written",
        "idempotency_written": True,
        "receipt_written": True,
        "pending_written": True,
    }
    return submission_sha256, receipt_id, stored_submission, receipt, index


def install_reader(monkeypatch, mapping: dict[str, dict | None]) -> None:
    async def read(path: str):
        value = mapping.get(path)
        return None if value is None else json.dumps(value)

    monkeypatch.setattr(secure_entrypoint, "get_file_text", read)
    monkeypatch.setattr(core_gateway, "get_file_text", read)


@pytest.mark.asyncio
async def test_recovery_returns_only_fully_verified_appended_status(monkeypatch) -> None:
    submission_sha, receipt_id, stored, receipt, index = intake_artifacts()
    final_path = "record-chain/records/R-000000123.json"
    final_record = {
        "record_id": "R-000000123",
        "record_type": "echo",
        "body": "original",
    }
    final_record["record_sha256"] = core_gateway._record_chain_record_sha256(
        final_record
    )
    final_status = {
        "schema": "trinityaccord.record-chain-receipt-final-status.v1",
        "receipt_id": receipt_id,
        "pending_file_path": receipt["pending_file_path"],
        "append_status": "appended",
        "final_record_id": "R-000000123",
        "final_record_path": final_path,
        "final_record_sha256": final_record["record_sha256"],
        "rejection_path": None,
        "rejection_code": None,
    }
    install_reader(monkeypatch, {
        f"record-chain/intake/by-submission-sha256/{submission_sha}.json": index,
        receipt["receipt_path"]: receipt,
        receipt["intake_submission_path"]: stored,
        f"record-chain/receipt-status/{receipt_id}.json": final_status,
        final_path: final_record,
    })

    status, payload = await secure_entrypoint.ProtectedProductionApp._submission_recovery_payload(
        submission_sha
    )

    assert status == 200
    assert payload["recovery_verified"] is True
    assert payload["final_status"] == final_status


@pytest.mark.asyncio
async def test_recovery_rejects_forged_terminal_record_hash(monkeypatch) -> None:
    submission_sha, receipt_id, stored, receipt, index = intake_artifacts()
    final_path = "record-chain/records/R-000000123.json"
    original_record = {
        "record_id": "R-000000123",
        "record_type": "echo",
        "body": "original",
    }
    original_record["record_sha256"] = core_gateway._record_chain_record_sha256(
        original_record
    )
    forged_record = dict(original_record)
    forged_record["body"] = "tampered"
    final_status = {
        "schema": "trinityaccord.record-chain-receipt-final-status.v1",
        "receipt_id": receipt_id,
        "pending_file_path": receipt["pending_file_path"],
        "append_status": "appended",
        "final_record_id": "R-000000123",
        "final_record_path": final_path,
        "final_record_sha256": original_record["record_sha256"],
        "rejection_path": None,
        "rejection_code": None,
    }
    install_reader(monkeypatch, {
        f"record-chain/intake/by-submission-sha256/{submission_sha}.json": index,
        receipt["receipt_path"]: receipt,
        receipt["intake_submission_path"]: stored,
        f"record-chain/receipt-status/{receipt_id}.json": final_status,
        final_path: forged_record,
    })

    status, payload = await secure_entrypoint.ProtectedProductionApp._submission_recovery_payload(
        submission_sha
    )

    assert status == 409
    assert payload["recovery_verified"] is False
    assert payload["diagnostic_code"] == "RECOVERY_STATE_INCONSISTENT"
    assert "failed verification" in payload["message"]


@pytest.mark.asyncio
async def test_recovery_rejects_partially_materialized_intake(monkeypatch) -> None:
    submission_sha, _receipt_id, stored, receipt, index = intake_artifacts()
    index["pending_written"] = False
    install_reader(monkeypatch, {
        f"record-chain/intake/by-submission-sha256/{submission_sha}.json": index,
        receipt["receipt_path"]: receipt,
        receipt["intake_submission_path"]: stored,
    })

    status, payload = await secure_entrypoint.ProtectedProductionApp._submission_recovery_payload(
        submission_sha
    )

    assert status == 409
    assert payload["recovery_verified"] is False
    assert payload["diagnostic_code"] == "RECOVERY_STATE_INCONSISTENT"
    assert "not fully materialized" in payload["message"]
