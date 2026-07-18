"""Global submission idempotency tests for atomic intake persistence."""
from __future__ import annotations

import json
import os
from unittest.mock import AsyncMock

from fastapi import HTTPException
from fastapi.testclient import TestClient

import app as app_module
from gateway.canonical import sha256_canonical_json
from gateway.github_atomic import AtomicCreateConflict
from gateway.receipts import compute_receipt_sha256

os.environ.setdefault("TRINITY_REPO_FULL_NAME", "test/repo")
os.environ.setdefault("TRINITY_TARGET_BRANCH", "main")
os.environ.setdefault("TRINITY_GITHUB_TOKEN", "fake-token")

client = TestClient(app_module.app)


def _index_for(
    submission: dict,
    receipt_id: str = "rcg-20260101-abc123def456abc123def456",
    *,
    materialized: bool = True,
) -> dict:
    index = {
        "schema": "trinityaccord.record-chain-intake-idempotency.v1",
        "submission_sha256": sha256_canonical_json(submission),
        "stored_submission_sha256": "b" * 64,
        "receipt_id": receipt_id,
        "receipt_path": f"record-chain/intake/receipts/2026/01/{receipt_id}.receipt.json",
        "pending_file_path": f"record-chain/pending/{receipt_id}.echo.pending.json",
        "intake_submission_path": f"record-chain/intake/submissions/2026/01/{receipt_id}.submission.json",
        "record_type": "echo",
        "created_at": "2026-01-01T00:00:00Z",
    }
    if materialized:
        index.update({
            "transaction_state": "pending_written",
            "receipt_written": True,
            "idempotency_written": True,
            "pending_written": True,
            "pending_committed_at": "2026-01-01T00:00:00Z",
        })
    return index


def _receipt_for(index: dict) -> dict:
    receipt = {
        "server_receipt_id": index["receipt_id"],
        "accepted_at": index["created_at"],
        "submission_sha256": index["submission_sha256"],
        "stored_submission_sha256": index["stored_submission_sha256"],
        "receipt_path": index["receipt_path"],
        "pending_file_path": index["pending_file_path"],
        "intake_submission_path": index["intake_submission_path"],
    }
    receipt["receipt_sha256"] = compute_receipt_sha256(receipt)
    return receipt


def _patch_no_write(monkeypatch):
    atomic_mock = AsyncMock()
    rate_mock = AsyncMock()
    dispatch_mock = AsyncMock()
    monkeypatch.setattr(app_module, "create_files_atomic", atomic_mock)
    monkeypatch.setattr(app_module, "check_rate_limit", rate_mock)
    monkeypatch.setattr(app_module, "dispatch_workflow", dispatch_mock)
    return atomic_mock, rate_mock, dispatch_mock


class TestIdempotencyIndexSchema:
    def test_schema_fields(self, signed_echo_submission):
        index = _index_for(signed_echo_submission)
        assert index["schema"] == "trinityaccord.record-chain-intake-idempotency.v1"
        assert len(index["submission_sha256"]) == 64
        assert index["pending_written"] is True
        assert index["pending_committed_at"]

    def test_original_sha_used_for_index_key(self):
        import inspect

        source = inspect.getsource(app_module.submit)
        orig_idx = source.find("original_submission_sha256 = sha256_canonical_json(body)")
        redact_idx = source.find("redact_transient_oath_readback")
        assert orig_idx != -1 and redact_idx != -1 and orig_idx < redact_idx

    def test_duplicate_check_precedes_rate_limit(self):
        import inspect

        source = inspect.getsource(app_module.submit)
        assert source.find("_read_idempotency_index") < source.find("check_rate_limit")


class TestLookupFailuresFailClosed:
    def test_lookup_read_failure(self, signed_echo_submission, monkeypatch):
        async def broken_read(path: str):
            if "by-submission-sha256" in path:
                raise RuntimeError("GitHub API error")
            return None

        atomic, rate, dispatch = _patch_no_write(monkeypatch)
        monkeypatch.setattr(app_module, "get_file_text", broken_read)
        monkeypatch.setattr(app_module, "get_file_sha", AsyncMock(return_value=None))

        data = client.post("/record-chain/submit", json=signed_echo_submission).json()
        assert data["accepted"] is False
        assert "IDEMPOTENCY_INDEX_LOOKUP_FAILED" in {d["code"] for d in data["diagnostics"]}
        atomic.assert_not_awaited()
        rate.assert_not_called()
        dispatch.assert_not_awaited()

    def test_invalid_index_json(self, signed_echo_submission, monkeypatch):
        async def invalid_read(path: str):
            return "{not-json" if "by-submission-sha256" in path else None

        atomic, rate, _ = _patch_no_write(monkeypatch)
        monkeypatch.setattr(app_module, "get_file_text", invalid_read)
        monkeypatch.setattr(app_module, "get_file_sha", AsyncMock(return_value=None))

        data = client.post("/record-chain/submit", json=signed_echo_submission).json()
        assert data["accepted"] is False
        assert "IDEMPOTENCY_INDEX_LOOKUP_FAILED" in {d["code"] for d in data["diagnostics"]}
        atomic.assert_not_awaited()
        rate.assert_not_called()

    def test_hash_mismatch(self, signed_echo_submission, monkeypatch):
        index = _index_for(signed_echo_submission)
        index["submission_sha256"] = "f" * 64

        async def mismatch_read(path: str):
            return json.dumps(index) if "by-submission-sha256" in path else None

        atomic, rate, _ = _patch_no_write(monkeypatch)
        monkeypatch.setattr(app_module, "get_file_text", mismatch_read)
        monkeypatch.setattr(app_module, "get_file_sha", AsyncMock(return_value=None))

        data = client.post("/record-chain/submit", json=signed_echo_submission).json()
        assert data["accepted"] is False
        assert "IDEMPOTENCY_INDEX_LOOKUP_FAILED" in {d["code"] for d in data["diagnostics"]}
        atomic.assert_not_awaited()
        rate.assert_not_called()

    def test_missing_receipt(self, signed_echo_submission, monkeypatch):
        index = _index_for(signed_echo_submission)

        async def missing_receipt(path: str):
            return json.dumps(index) if "by-submission-sha256" in path else None

        atomic, rate, _ = _patch_no_write(monkeypatch)
        monkeypatch.setattr(app_module, "get_file_text", missing_receipt)
        monkeypatch.setattr(app_module, "get_file_sha", AsyncMock(return_value="pending-sha"))

        data = client.post("/record-chain/submit", json=signed_echo_submission).json()
        assert data["accepted"] is False
        assert "IDEMPOTENCY_INDEX_LOOKUP_FAILED" in {d["code"] for d in data["diagnostics"]}
        atomic.assert_not_awaited()
        rate.assert_not_called()

    def test_unmaterialized_index_gets_specific_retryable_error(self, signed_echo_submission, monkeypatch):
        index = _index_for(signed_echo_submission)
        index["transaction_state"] = "idempotency_written"
        index["pending_written"] = False
        index["pending_committed_at"] = None
        receipt = _receipt_for(index)

        async def read(path: str):
            if "by-submission-sha256" in path:
                return json.dumps(index)
            if path == index["receipt_path"]:
                return json.dumps(receipt)
            return None

        atomic, rate, _ = _patch_no_write(monkeypatch)
        monkeypatch.setattr(app_module, "get_file_text", read)
        monkeypatch.setattr(app_module, "get_file_sha", AsyncMock(return_value=None))

        data = client.post("/record-chain/submit", json=signed_echo_submission).json()
        assert data["accepted"] is False
        assert "INTAKE_TRANSACTION_NOT_MATERIALIZED" in {d["code"] for d in data["diagnostics"]}
        atomic.assert_not_awaited()
        rate.assert_not_called()


class TestDuplicateResolution:
    def test_valid_duplicate_returns_original_receipt(self, signed_echo_submission, monkeypatch):
        index = _index_for(signed_echo_submission)
        receipt = _receipt_for(index)

        async def read(path: str):
            if "by-submission-sha256" in path:
                return json.dumps(index)
            if path == index["receipt_path"]:
                return json.dumps(receipt)
            return None

        atomic, rate, dispatch = _patch_no_write(monkeypatch)
        monkeypatch.setattr(app_module, "get_file_text", read)
        monkeypatch.setattr(app_module, "get_file_sha", AsyncMock(return_value="pending-sha"))

        data = client.post("/record-chain/submit", json=signed_echo_submission).json()
        assert data["accepted"] is True
        assert data["append_status"] == "duplicate_existing_submission_returned"
        assert data["receipt_id"] == index["receipt_id"]
        atomic.assert_not_awaited()
        rate.assert_not_called()
        dispatch.assert_not_awaited()


class TestNewAtomicSubmission:
    def test_single_atomic_write_contains_finalized_index(self, signed_echo_submission, monkeypatch):
        atomic = AsyncMock(return_value={"commit": {"sha": "atomic-commit"}})
        dispatch = AsyncMock(return_value=None)
        monkeypatch.setattr(app_module, "create_files_atomic", atomic)
        monkeypatch.setattr(app_module, "get_file_text", AsyncMock(return_value=None))
        monkeypatch.setattr(app_module, "get_file_sha", AsyncMock(return_value=None))
        monkeypatch.setattr(app_module, "dispatch_workflow", dispatch)
        monkeypatch.setattr(app_module, "check_rate_limit", lambda body: None)

        data = client.post("/record-chain/submit", json=signed_echo_submission).json()
        assert data["accepted"] is True
        atomic.assert_awaited_once()
        files = atomic.await_args.args[0]
        assert len(files) == 4
        index_content = next(content for path, content in files.items() if "by-submission-sha256" in path)
        index = json.loads(index_content)
        assert index["transaction_state"] == "pending_written"
        assert index["pending_written"] is True
        assert index["pending_committed_at"]
        dispatch.assert_awaited_once()

    def test_atomic_failure_returns_error_without_dispatch(self, signed_echo_submission, monkeypatch):
        atomic = AsyncMock(side_effect=RuntimeError("ref update failed"))
        dispatch = AsyncMock()
        monkeypatch.setattr(app_module, "create_files_atomic", atomic)
        monkeypatch.setattr(app_module, "get_file_text", AsyncMock(return_value=None))
        monkeypatch.setattr(app_module, "get_file_sha", AsyncMock(return_value=None))
        monkeypatch.setattr(app_module, "dispatch_workflow", dispatch)
        monkeypatch.setattr(app_module, "check_rate_limit", lambda body: None)

        data = client.post("/record-chain/submit", json=signed_echo_submission).json()
        assert data["accepted"] is False
        assert "PERSIST_FAILED" in {d["code"] for d in data["diagnostics"]}
        dispatch.assert_not_awaited()

    def test_atomic_conflict_resolves_concurrent_winner(self, signed_echo_submission, monkeypatch):
        index = _index_for(signed_echo_submission)
        receipt = _receipt_for(index)
        index_reads = 0

        async def read(path: str):
            nonlocal index_reads
            if "by-submission-sha256" in path:
                index_reads += 1
                return None if index_reads == 1 else json.dumps(index)
            if path == index["receipt_path"]:
                return json.dumps(receipt)
            return None

        atomic = AsyncMock(side_effect=AtomicCreateConflict("concurrent winner"))
        dispatch = AsyncMock()
        monkeypatch.setattr(app_module, "create_files_atomic", atomic)
        monkeypatch.setattr(app_module, "get_file_text", read)
        monkeypatch.setattr(app_module, "get_file_sha", AsyncMock(side_effect=lambda path: "pending-sha" if "pending/" in path else None))
        monkeypatch.setattr(app_module, "dispatch_workflow", dispatch)
        monkeypatch.setattr(app_module, "check_rate_limit", lambda body: None)

        data = client.post("/record-chain/submit", json=signed_echo_submission).json()
        assert data["accepted"] is True
        assert data["append_status"] == "duplicate_existing_submission_returned"
        assert data["receipt_id"] == index["receipt_id"]
        dispatch.assert_not_awaited()


class TestSameDayReceiptFallback:
    def test_matching_receipt_returns_duplicate(self, signed_echo_submission, monkeypatch):
        index = _index_for(signed_echo_submission)
        receipt = _receipt_for(index)
        atomic = AsyncMock()
        dispatch = AsyncMock()

        async def matching(**kwargs):
            return index["receipt_path"], receipt

        monkeypatch.setattr(app_module, "_find_existing_matching_receipt", matching)
        monkeypatch.setattr(app_module, "create_files_atomic", atomic)
        monkeypatch.setattr(app_module, "get_file_text", AsyncMock(return_value=None))
        monkeypatch.setattr(app_module, "get_file_sha", AsyncMock(return_value=None))
        monkeypatch.setattr(app_module, "dispatch_workflow", dispatch)
        monkeypatch.setattr(app_module, "check_rate_limit", lambda body: None)

        data = client.post("/record-chain/submit", json=signed_echo_submission).json()
        assert data["accepted"] is True
        assert data["append_status"] == "duplicate_existing_receipt_returned"
        atomic.assert_not_awaited()
        dispatch.assert_not_awaited()

    def test_mismatched_receipt_refuses_overwrite(self, signed_echo_submission, monkeypatch):
        async def conflict(**kwargs):
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "RECEIPT_PATH_CONFLICT",
                    "message": "Receipt path already exists but does not bind to this exact submission.",
                },
            )

        atomic = AsyncMock()
        dispatch = AsyncMock()
        monkeypatch.setattr(app_module, "_find_existing_matching_receipt", conflict)
        monkeypatch.setattr(app_module, "create_files_atomic", atomic)
        monkeypatch.setattr(app_module, "get_file_text", AsyncMock(return_value=None))
        monkeypatch.setattr(app_module, "get_file_sha", AsyncMock(return_value=None))
        monkeypatch.setattr(app_module, "dispatch_workflow", dispatch)
        monkeypatch.setattr(app_module, "check_rate_limit", lambda body: None)

        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        assert resp.status_code == 409
        atomic.assert_not_awaited()
        dispatch.assert_not_awaited()
