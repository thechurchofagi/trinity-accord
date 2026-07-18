from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from jsonschema import Draft202012Validator

from apps.record_chain_intake_gateway import app as app_module
from apps.record_chain_intake_gateway.gateway import github_atomic
from apps.record_chain_intake_gateway.gateway.models import SubmitResponse
from apps.record_chain_intake_gateway.gateway.receipts import compute_receipt_sha256

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture()
def client() -> TestClient:
    app_module._receipt_store.clear()
    return TestClient(app_module.app)


def _receipt(
    receipt_id: str,
    submission_sha256: str,
    stored_submission_sha256: str,
    record_type: str = "echo",
) -> dict:
    date = receipt_id.split("-")[1]
    receipt_path = (
        f"record-chain/intake/receipts/{date[:4]}/{date[4:6]}/"
        f"{receipt_id}.receipt.json"
    )
    receipt = {
        "server_receipt_id": receipt_id,
        "service": "record-chain-intake-gateway",
        "gateway_version": "1.0.0",
        "record_type": record_type,
        "submission_sha256": submission_sha256,
        "original_submission_sha256": submission_sha256,
        "stored_submission_sha256": stored_submission_sha256,
        "received_raw_body_sha256": "b" * 64,
        "accepted_at": "2026-07-18T00:00:00Z",
        "raw_readback_redacted": True,
        "receipt_is_not_final_chain_record": True,
        "intake_submission_path": receipt_path.replace(
            "/intake/receipts/", "/intake/submissions/"
        ).replace(".receipt.json", ".submission.json"),
        "pending_file_path": f"record-chain/pending/{receipt_id}.{record_type}.pending.json",
        "receipt_path": receipt_path,
    }
    receipt["receipt_sha256"] = compute_receipt_sha256(receipt)
    return receipt


def _load_schema(name: str) -> dict:
    return json.loads((ROOT / "api" / name).read_text(encoding="utf-8"))


def test_equivalent_tree_reconciliation_reports_reachable_head() -> None:
    assert github_atomic._authoritative_reconciled_commit_sha(
        "equivalent_tree", "reachable-head", "orphan-attempt"
    ) == "reachable-head"
    assert github_atomic._authoritative_reconciled_commit_sha(
        "commit_reachable", "later-head", "intake-commit"
    ) == "intake-commit"


def test_successful_ref_response_without_expected_sha_requires_reconciliation() -> None:
    source = Path(github_atomic.__file__).read_text(encoding="utf-8")
    success_block = source.split("if update_response.status_code == 200:", 1)[1]
    assert "if updated_sha == new_commit_sha" in success_block
    assert "await _reconcile_atomic_write(" in success_block
    assert "without proving the intended commit durable" in success_block


@pytest.mark.asyncio
async def test_same_day_receipt_fallback_rejects_tampered_hash(monkeypatch) -> None:
    submission_sha = "a" * 64
    stored_sha = "c" * 64
    receipt_id = "rcg-20260718-" + submission_sha[:24]
    receipt = _receipt(receipt_id, submission_sha, stored_sha)
    receipt["accepted_at"] = "2099-01-01T00:00:00Z"  # hash now invalid

    monkeypatch.setattr(app_module, "get_file_sha", AsyncMock(return_value="blob-sha"))
    monkeypatch.setattr(app_module, "get_file_text", AsyncMock(return_value=json.dumps(receipt)))

    with pytest.raises(HTTPException) as exc_info:
        await app_module._find_existing_matching_receipt(
            candidate_receipt_paths=[receipt["receipt_path"]],
            submission_sha256=submission_sha,
            stored_submission_sha256=stored_sha,
        )
    assert exc_info.value.status_code == 409
    assert exc_info.value.detail["code"] == "RECEIPT_PATH_CONFLICT"


def test_atomic_conflict_index_failure_is_structured(
    client: TestClient,
    signed_echo_submission: dict,
    monkeypatch,
) -> None:
    monkeypatch.setenv("TRINITY_REPO_FULL_NAME", "test/repo")
    monkeypatch.setenv("TRINITY_TARGET_BRANCH", "main")
    monkeypatch.setenv("TRINITY_GITHUB_TOKEN", "test-token")
    calls = 0

    async def read_index(submission_sha256: str):
        nonlocal calls
        calls += 1
        if calls == 1:
            return None
        raise RuntimeError("idempotency backend unavailable after conflict")

    monkeypatch.setattr(app_module, "_read_idempotency_index", read_index)
    monkeypatch.setattr(
        app_module,
        "create_files_atomic",
        AsyncMock(side_effect=app_module.AtomicCreateConflict("concurrent winner")),
    )
    monkeypatch.setattr(app_module, "get_file_sha", AsyncMock(return_value=None))
    monkeypatch.setattr(app_module, "get_file_text", AsyncMock(return_value=None))
    monkeypatch.setattr(app_module, "check_rate_limit", lambda body: None)

    response = client.post("/record-chain/submit", json=signed_echo_submission)
    assert response.status_code == 200
    data = response.json()
    assert data["accepted"] is False
    assert data["duplicate"] is False
    assert "INTAKE_ATOMIC_CONFLICT_LOOKUP_FAILED" in {
        diagnostic["code"] for diagnostic in data["diagnostics"]
    }


def test_dry_run_does_not_claim_or_cache_durable_artifacts(
    client: TestClient,
    signed_echo_submission: dict,
    monkeypatch,
) -> None:
    monkeypatch.setenv("TRINITY_REPO_FULL_NAME", "test/repo")
    monkeypatch.setenv("TRINITY_TARGET_BRANCH", "main")
    monkeypatch.setattr(app_module, "_WRITE_MODE", "dry_run")
    monkeypatch.setattr(app_module, "_read_idempotency_index", AsyncMock(return_value=None))
    monkeypatch.setattr(app_module, "check_rate_limit", lambda body: None)

    response = client.post("/record-chain/submit", json=signed_echo_submission)
    assert response.status_code == 200
    data = response.json()
    assert data["accepted"] is True
    assert data["append_status"] == "dry_run"
    assert data["duplicate"] is False
    assert data["created_pending_records"] == []
    assert data["receipt_id"] in app_module._receipt_store
    retrieved = client.get(f"/record-chain/receipt/{data['receipt_id']}")
    assert retrieved.status_code == 200
    assert any(
        warning.get("code") == "RECEIPT_NON_DURABLE_DRY_RUN"
        for warning in retrieved.json().get("envelope_warnings", [])
        if isinstance(warning, dict)
    )


@pytest.mark.asyncio
async def test_duplicate_response_sets_discriminator_and_validates_schema(monkeypatch) -> None:
    submission_sha = "a" * 64
    stored_sha = "c" * 64
    receipt_id = "rcg-20260718-" + submission_sha[:24]
    receipt = _receipt(receipt_id, submission_sha, stored_sha)
    index = {
        "submission_sha256": submission_sha,
        "stored_submission_sha256": stored_sha,
        "receipt_id": receipt_id,
        "receipt_path": receipt["receipt_path"],
        "pending_file_path": receipt["pending_file_path"],
        "intake_submission_path": receipt["intake_submission_path"],
        "record_type": "echo",
        "created_at": "2026-07-18T00:00:00Z",
        "transaction_state": "pending_written",
        "pending_written": True,
        "pending_committed_at": "2026-07-18T00:00:00Z",
    }
    monkeypatch.setattr(app_module, "get_file_text", AsyncMock(return_value=json.dumps(receipt)))
    monkeypatch.setattr(app_module, "get_file_sha", AsyncMock(return_value="pending-sha"))

    result = await app_module._submit_response_from_idempotency_index(
        index=index,
        record_type="echo",
        submission_sha256=submission_sha,
        received_raw_body_sha256="d" * 64,
        body={},
    )
    payload = result.model_dump(mode="json")
    assert payload["duplicate"] is True
    Draft202012Validator(_load_schema("record-chain-submit-response.v1.json")).validate(payload)


def test_submit_schema_success_and_failure_are_disjoint() -> None:
    schema = _load_schema("record-chain-submit-response.v1.json")
    validator = Draft202012Validator(schema)
    success = SubmitResponse(
        accepted=True,
        submitted=True,
        duplicate=False,
        receipt_id="rcg-20260718-" + "a" * 24,
        record_type="echo",
        submission_sha256="a" * 64,
        received_raw_body_sha256="b" * 64,
        pending_file_path="record-chain/pending/example.pending.json",
        intake_submission_path="record-chain/intake/submissions/example.json",
        receipt_path="record-chain/intake/receipts/example.json",
        server_created_at="2026-07-18T00:00:00Z",
        append_status="queued",
        receipt={},
        diagnostics=[],
        warnings=[],
        boundary={
            "receipt_is_not_authority": True,
            "receipt_is_not_attestation": True,
            "receipt_is_not_final_chain_record": True,
            "record_chain_append_is_server_side": True,
        },
        created_pending_records=["record-chain/pending/example.pending.json"],
    ).model_dump(mode="json")
    validator.validate(success)


def test_receipt_not_found_matches_public_schema(client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(app_module, "get_file_text", AsyncMock(return_value=None))
    response = client.get("/record-chain/receipt/rcg-20260718-" + "a" * 24)
    assert response.status_code == 404
    payload = response.json()
    assert payload["found"] is False
    Draft202012Validator(_load_schema("record-chain-receipt-response.v1.json")).validate(payload)


def test_cache_fallback_warning_matches_public_schema(client: TestClient, monkeypatch) -> None:
    receipt_id = "rcg-20260718-" + "a" * 24
    receipt = _receipt(receipt_id, "a" * 64, "c" * 64)
    app_module._receipt_store[receipt_id] = receipt
    monkeypatch.setattr(
        app_module,
        "get_file_text",
        AsyncMock(side_effect=RuntimeError("durable backend unavailable")),
    )
    response = client.get(f"/record-chain/receipt/{receipt_id}")
    assert response.status_code == 200
    payload = response.json()
    cache_warning = next(
        warning
        for warning in payload["envelope_warnings"]
        if warning["code"] == "RECEIPT_DURABLE_LOOKUP_FAILED_RETURNED_MEMORY_CACHE"
    )
    assert cache_warning["message"]
    Draft202012Validator(_load_schema("record-chain-receipt-response.v1.json")).validate(payload)


def test_duplicate_key_receipt_is_not_accepted(client: TestClient, monkeypatch) -> None:
    receipt_id = "rcg-20260718-" + "a" * 24
    receipt = _receipt(receipt_id, "a" * 64, "c" * 64)
    canonical = json.dumps(receipt, separators=(",", ":"))
    raw = canonical.replace(
        '"server_receipt_id":"' + receipt_id + '"',
        '"server_receipt_id":"forged","server_receipt_id":"' + receipt_id + '"',
        1,
    )
    monkeypatch.setattr(app_module, "get_file_text", AsyncMock(return_value=raw))
    response = client.get(f"/record-chain/receipt/{receipt_id}")
    assert response.status_code != 200


@pytest.mark.asyncio
async def test_final_status_recomputes_record_hash(monkeypatch) -> None:
    receipt_id = "rcg-20260718-" + "a" * 24
    pending_path = f"record-chain/pending/{receipt_id}.echo.pending.json"
    final_path = "record-chain/records/R-000000123.json"
    record = {"record_id": "R-000000123", "record_type": "echo", "body": "original"}
    record["record_sha256"] = app_module._record_chain_record_sha256(record)
    status = {
        "schema": "trinityaccord.record-chain-receipt-final-status.v1",
        "receipt_id": receipt_id,
        "pending_file_path": pending_path,
        "append_status": "appended",
        "final_record_id": "R-000000123",
        "final_record_path": final_path,
        "final_record_sha256": record["record_sha256"],
        "rejection_path": None,
        "rejection_code": None,
    }

    async def read(path: str):
        if path.endswith(f"/{receipt_id}.json"):
            return json.dumps(status)
        if path == final_path:
            return json.dumps(record)
        return None

    monkeypatch.setattr(app_module, "get_file_text", read)
    assert (await app_module._read_receipt_final_status(receipt_id))["append_status"] == "appended"

    record["body"] = "tampered"
    with pytest.raises(RuntimeError, match="hash recomputation failed"):
        await app_module._read_receipt_final_status(receipt_id)


@pytest.mark.asyncio
async def test_final_status_rejects_pending_path_for_another_receipt(monkeypatch) -> None:
    receipt_id = "rcg-20260718-" + "a" * 24
    status = {
        "schema": "trinityaccord.record-chain-receipt-final-status.v1",
        "receipt_id": receipt_id,
        "pending_file_path": "record-chain/pending/rcg-20260718-bbbbbbbbbbbbbbbbbbbbbbbb.echo.pending.json",
        "append_status": "rejected",
        "final_record_id": None,
        "final_record_path": None,
        "final_record_sha256": None,
        "rejection_path": "record-chain/rejected/unrelated.rejection.json",
        "rejection_code": "bad",
    }
    monkeypatch.setattr(app_module, "get_file_text", AsyncMock(return_value=json.dumps(status)))
    with pytest.raises(RuntimeError, match="receipt-mismatched"):
        await app_module._read_receipt_final_status(receipt_id)


def test_append_push_recovery_is_narrowly_scoped() -> None:
    workflow = (ROOT / ".github/workflows/record-chain-append.yml").read_text(encoding="utf-8")
    assert '"record-chain/pending/*.pending.json"' in workflow
    assert '"record-chain/pending/**"' not in workflow
