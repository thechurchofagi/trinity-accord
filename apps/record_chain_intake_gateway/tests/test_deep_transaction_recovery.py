from __future__ import annotations

import json

import pytest

from apps.record_chain_intake_gateway import app as app_module
from apps.record_chain_intake_gateway.gateway import github_atomic
from apps.record_chain_intake_gateway.gateway.validation import validate_record_type_specific_content


@pytest.mark.asyncio
async def test_atomic_state_rejects_partial_or_different_paths(monkeypatch) -> None:
    remote = {
        "submission.json": "submission-bytes",
        "receipt.json": None,
        "index.json": "different-index-bytes",
        "pending.json": None,
    }

    async def fake_get_file_text_at_ref(client, path: str, ref: str):
        return remote[path]

    monkeypatch.setattr(github_atomic, "_get_file_text_at_ref", fake_get_file_text_at_ref)
    files = {
        "submission.json": "submission-bytes",
        "receipt.json": "receipt-bytes",
        "index.json": "index-bytes",
        "pending.json": "pending-bytes",
    }

    all_absent, all_exact = await github_atomic._atomic_files_state(object(), files, "head-sha")
    assert all_absent is False
    assert all_exact is False


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("record_type", "content_key", "code_prefix"),
    [
        ("correction", "correction_content", "CORRECTION"),
        ("classification_update", "classification_update_content", "CLASSIFICATION_UPDATE"),
    ],
)
async def test_record_target_diagnostics_fail_closed_on_missing_target(
    monkeypatch, record_type: str, content_key: str, code_prefix: str
) -> None:
    async def fake_get_file_text(path: str):
        return None

    monkeypatch.setattr(app_module, "get_file_text", fake_get_file_text)
    body = {
        "record_draft": {
            "record_type": record_type,
            content_key: {
                "target_record_id": "R-000000001",
                "target_record_sha256": "a" * 64,
            },
        }
    }

    diagnostics = await app_module._record_target_diagnostics(body)

    assert [diag.code for diag in diagnostics] == [f"{code_prefix}_TARGET_NOT_FOUND"]


@pytest.mark.asyncio
async def test_record_target_diagnostics_reject_hash_mismatch(monkeypatch) -> None:
    async def fake_get_file_text(path: str):
        return json.dumps({
            "record_id": "R-000000001",
            "record_sha256": "b" * 64,
        })

    monkeypatch.setattr(app_module, "get_file_text", fake_get_file_text)
    body = {
        "record_draft": {
            "record_type": "correction",
            "correction_content": {
                "target_record_id": "R-000000001",
                "target_record_sha256": "a" * 64,
            },
        }
    }

    diagnostics = await app_module._record_target_diagnostics(body)

    assert "CORRECTION_TARGET_SHA_MISMATCH" in {diag.code for diag in diagnostics}


def test_correction_rejects_noncanonical_target_id() -> None:
    diagnostics = validate_record_type_specific_content(
        "correction",
        {
            "record_type": "correction",
            "title": "Correction",
            "body": "Body",
            "correction_content": {
                "target_record_id": "not-a-record",
                "target_record_sha256": "a" * 64,
                "correction_reason": "reason",
                "corrected_fields_or_claims": ["claim"],
                "evidence_or_review_basis": "basis",
            },
        },
    )
    assert "INVALID_CORRECTION_TARGET_ID" in {diag.code for diag in diagnostics}


@pytest.mark.asyncio
async def test_receipt_final_status_verifies_final_record_binding(monkeypatch) -> None:
    receipt_id = "rcg-20260712-" + "a" * 24
    status_path = f"record-chain/receipt-status/{receipt_id}.json"
    final_path = "record-chain/records/R-000000001.json"
    status = {
        "schema": "trinityaccord.record-chain-receipt-final-status.v1",
        "receipt_id": receipt_id,
        "pending_file_path": f"record-chain/pending/{receipt_id}.echo.pending.json",
        "append_status": "appended",
        "final_record_id": "R-000000001",
        "final_record_path": final_path,
        "final_record_sha256": "a" * 64,
        "rejection_path": None,
        "rejection_code": None,
    }

    async def fake_get_file_text(path: str):
        if path == status_path:
            return json.dumps(status)
        if path == final_path:
            return json.dumps({"record_id": "R-000000001", "record_sha256": "a" * 64})
        return None

    monkeypatch.setattr(app_module, "get_file_text", fake_get_file_text)
    result = await app_module._read_receipt_final_status(receipt_id)
    assert result == status


@pytest.mark.asyncio
async def test_receipt_final_status_fails_closed_on_forged_hash(monkeypatch) -> None:
    receipt_id = "rcg-20260712-" + "a" * 24
    status_path = f"record-chain/receipt-status/{receipt_id}.json"
    final_path = "record-chain/records/R-000000001.json"
    status = {
        "schema": "trinityaccord.record-chain-receipt-final-status.v1",
        "receipt_id": receipt_id,
        "pending_file_path": f"record-chain/pending/{receipt_id}.echo.pending.json",
        "append_status": "appended",
        "final_record_id": "R-000000001",
        "final_record_path": final_path,
        "final_record_sha256": "a" * 64,
        "rejection_path": None,
        "rejection_code": None,
    }

    async def fake_get_file_text(path: str):
        if path == status_path:
            return json.dumps(status)
        if path == final_path:
            return json.dumps({"record_id": "R-000000001", "record_sha256": "b" * 64})
        return None

    monkeypatch.setattr(app_module, "get_file_text", fake_get_file_text)
    with pytest.raises(RuntimeError, match="final record binding mismatch"):
        await app_module._read_receipt_final_status(receipt_id)
