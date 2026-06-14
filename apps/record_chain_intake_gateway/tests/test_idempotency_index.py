"""Part B: global submission idempotency index tests.

Real behavior tests using monkeypatch to mock GitHub adapter functions.
"""
from __future__ import annotations

import json
import os
from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

import app as app_module
from app import app

# Set required env vars for _check_config()
os.environ.setdefault("TRINITY_REPO_FULL_NAME", "test/repo")
os.environ.setdefault("TRINITY_TARGET_BRANCH", "main")
os.environ.setdefault("TRINITY_GITHUB_TOKEN", "fake-token")

client = TestClient(app_module.app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_idempotency_index(receipt_id: str = "rcg-20260101-abc123def456") -> dict:
    return {
        "schema": "trinityaccord.record-chain-intake-idempotency.v1",
        "submission_sha256": "a" * 64,
        "stored_submission_sha256": "b" * 64,
        "receipt_id": receipt_id,
        "receipt_path": f"record-chain/intake/receipts/2026/01/{receipt_id}.receipt.json",
        "pending_file_path": f"record-chain/pending/{receipt_id}.echo.pending.json",
        "intake_submission_path": f"record-chain/intake/submissions/2026/01/{receipt_id}.submission.json",
        "record_type": "echo",
        "created_at": "2026-01-01T00:00:00Z",
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestIdempotencyIndexSchema:
    def test_schema_fields(self):
        index = _make_idempotency_index()
        assert index["schema"] == "trinityaccord.record-chain-intake-idempotency.v1"
        assert len(index["submission_sha256"]) == 64
        assert index["receipt_id"].startswith("rcg-")

    def test_original_sha_used_for_index_key(self):
        """The idempotency key must use the original (pre-redaction) SHA."""
        import inspect
        source = inspect.getsource(app_module.submit)
        orig_idx = source.find("original_submission_sha256 = sha256_canonical_json(body)")
        redact_idx = source.find("redact_transient_oath_readback")
        assert orig_idx < redact_idx

    def test_duplicate_does_not_consume_rate_limit(self):
        """Idempotency check comes before rate limit check in submit flow."""
        import inspect
        source = inspect.getsource(app_module.submit)
        idemp_idx = source.find("_read_idempotency_index")
        rate_limit_idx = source.find("check_rate_limit")
        assert idemp_idx < rate_limit_idx


class TestLookupReadFailureFailsClosed:
    """P1: idempotency pre-check read failure returns IDEMPOTENCY_INDEX_LOOKUP_FAILED."""

    def test_lookup_read_failure_fails_closed(self, signed_echo_submission, monkeypatch):
        """When get_file_text raises during idempotency lookup, fail closed."""
        async def mock_get_file_text(path):
            if "by-submission-sha256" in path:
                raise RuntimeError("GitHub API error")
            return None

        put_mock = AsyncMock()
        rate_mock = AsyncMock()
        dispatch_mock = AsyncMock()

        monkeypatch.setattr("app.get_file_text", mock_get_file_text)
        monkeypatch.setattr("app.get_file_sha", AsyncMock(return_value=None))
        monkeypatch.setattr("app.put_file", put_mock)
        monkeypatch.setattr("app.check_rate_limit", rate_mock)
        monkeypatch.setattr("app.dispatch_workflow", dispatch_mock)

        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        data = resp.json()

        assert data["accepted"] is False
        assert data["submitted"] is False
        codes = [d["code"] for d in data.get("diagnostics", [])]
        assert "IDEMPOTENCY_INDEX_LOOKUP_FAILED" in codes
        # Must not proceed to rate limit or writes
        rate_mock.assert_not_called()
        put_mock.assert_not_called()
        dispatch_mock.assert_not_called()


class TestInvalidIdempotencyJsonFailsClosed:
    """P1: invalid idempotency JSON fails closed."""

    def test_invalid_json_fails_closed(self, signed_echo_submission, monkeypatch):
        """When idempotency index is not valid JSON, fail closed."""
        async def mock_get_file_text(path):
            if "by-submission-sha256" in path:
                return "{not-json"
            return None

        put_mock = AsyncMock()
        rate_mock = AsyncMock()

        monkeypatch.setattr("app.get_file_text", mock_get_file_text)
        monkeypatch.setattr("app.get_file_sha", AsyncMock(return_value=None))
        monkeypatch.setattr("app.put_file", put_mock)
        monkeypatch.setattr("app.check_rate_limit", rate_mock)
        monkeypatch.setattr("app.dispatch_workflow", AsyncMock())

        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        data = resp.json()

        assert data["accepted"] is False
        codes = [d["code"] for d in data.get("diagnostics", [])]
        assert "IDEMPOTENCY_INDEX_LOOKUP_FAILED" in codes
        rate_mock.assert_not_called()
        put_mock.assert_not_called()


class TestHashMismatchFailsClosed:
    """P1: hash mismatch in idempotency index fails closed."""

    def test_hash_mismatch_fails_closed(self, signed_echo_submission, monkeypatch):
        """When idempotency index has wrong submission_sha256, fail closed."""
        bad_index = _make_idempotency_index()
        bad_index["submission_sha256"] = "f" * 64  # wrong hash

        async def mock_get_file_text(path):
            if "by-submission-sha256" in path:
                return json.dumps(bad_index)
            return None

        put_mock = AsyncMock()
        rate_mock = AsyncMock()

        monkeypatch.setattr("app.get_file_text", mock_get_file_text)
        monkeypatch.setattr("app.get_file_sha", AsyncMock(return_value=None))
        monkeypatch.setattr("app.put_file", put_mock)
        monkeypatch.setattr("app.check_rate_limit", rate_mock)
        monkeypatch.setattr("app.dispatch_workflow", AsyncMock())

        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        data = resp.json()

        assert data["accepted"] is False
        codes = [d["code"] for d in data.get("diagnostics", [])]
        assert "IDEMPOTENCY_INDEX_LOOKUP_FAILED" in codes
        rate_mock.assert_not_called()
        put_mock.assert_not_called()


class TestMissingReceiptFailsClosed:
    """P1: existing index with missing receipt fails closed."""

    def test_missing_receipt_fails_closed(self, signed_echo_submission, monkeypatch):
        """When idempotency index exists but receipt is missing, fail closed."""
        from gateway.canonical import sha256_canonical_json

        actual_sha = sha256_canonical_json(signed_echo_submission)
        existing_index = {
            **_make_idempotency_index(),
            "submission_sha256": actual_sha,
        }

        async def mock_get_file_text(path):
            if "by-submission-sha256" in path:
                return json.dumps(existing_index)
            return None  # receipt not found

        put_mock = AsyncMock()
        rate_mock = AsyncMock()

        monkeypatch.setattr("app.get_file_text", mock_get_file_text)
        monkeypatch.setattr("app.get_file_sha", AsyncMock(return_value=None))
        monkeypatch.setattr("app.put_file", put_mock)
        monkeypatch.setattr("app.check_rate_limit", rate_mock)
        monkeypatch.setattr("app.dispatch_workflow", AsyncMock())

        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        data = resp.json()

        assert data["accepted"] is False
        codes = [d["code"] for d in data.get("diagnostics", [])]
        assert "IDEMPOTENCY_INDEX_LOOKUP_FAILED" in codes
        rate_mock.assert_not_called()
        put_mock.assert_not_called()


class TestInvalidReceiptJsonFailsClosed:
    """P1: existing index with invalid receipt JSON fails closed."""

    def test_invalid_receipt_json_fails_closed(self, signed_echo_submission, monkeypatch):
        """When idempotency receipt is not valid JSON, fail closed."""
        from gateway.canonical import sha256_canonical_json

        actual_sha = sha256_canonical_json(signed_echo_submission)
        existing_index = {
            **_make_idempotency_index(),
            "submission_sha256": actual_sha,
        }

        async def mock_get_file_text(path):
            if "by-submission-sha256" in path:
                return json.dumps(existing_index)
            if "receipt" in path:
                return "{bad"
            return None

        put_mock = AsyncMock()
        rate_mock = AsyncMock()

        monkeypatch.setattr("app.get_file_text", mock_get_file_text)
        monkeypatch.setattr("app.get_file_sha", AsyncMock(return_value=None))
        monkeypatch.setattr("app.put_file", put_mock)
        monkeypatch.setattr("app.check_rate_limit", rate_mock)
        monkeypatch.setattr("app.dispatch_workflow", AsyncMock())

        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        data = resp.json()

        assert data["accepted"] is False
        codes = [d["code"] for d in data.get("diagnostics", [])]
        assert "IDEMPOTENCY_INDEX_LOOKUP_FAILED" in codes
        rate_mock.assert_not_called()
        put_mock.assert_not_called()


class TestValidDuplicateReturnsReceipt:
    """P1: existing index with valid receipt returns duplicate."""

    def test_valid_duplicate_returns_receipt(self, signed_echo_submission, monkeypatch):
        """When valid idempotency index and receipt exist, return duplicate with receipt."""
        from gateway.canonical import sha256_canonical_json

        actual_sha = sha256_canonical_json(signed_echo_submission)
        existing_receipt_id = "rcg-20260101-existing123"
        existing_index = {
            "schema": "trinityaccord.record-chain-intake-idempotency.v1",
            "submission_sha256": actual_sha,
            "stored_submission_sha256": "b" * 64,
            "receipt_id": existing_receipt_id,
            "receipt_path": f"record-chain/intake/receipts/2026/01/{existing_receipt_id}.receipt.json",
            "pending_file_path": f"record-chain/pending/{existing_receipt_id}.echo.pending.json",
            "intake_submission_path": f"record-chain/intake/submissions/2026/01/{existing_receipt_id}.submission.json",
            "record_type": "echo",
            "created_at": "2026-01-01T00:00:00Z",
        }
        existing_receipt = {
            "server_receipt_id": existing_receipt_id,
            "accepted_at": "2026-01-01T00:00:00Z",
            "submission_sha256": actual_sha,
            "stored_submission_sha256": "b" * 64,
            "receipt_path": existing_index["receipt_path"],
            "pending_file_path": existing_index["pending_file_path"],
            "intake_submission_path": existing_index["intake_submission_path"],
        }

        async def mock_get_file_text(path):
            if "by-submission-sha256" in path:
                return json.dumps(existing_index)
            if existing_index["receipt_path"] in path:
                return json.dumps(existing_receipt)
            return None

        put_mock = AsyncMock()
        rate_mock = AsyncMock()
        dispatch_mock = AsyncMock()

        monkeypatch.setattr("app.get_file_text", mock_get_file_text)
        monkeypatch.setattr("app.put_file", put_mock)
        monkeypatch.setattr("app.check_rate_limit", rate_mock)
        monkeypatch.setattr("app.get_file_sha", AsyncMock(return_value=None))
        monkeypatch.setattr("app.dispatch_workflow", dispatch_mock)

        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        data = resp.json()

        assert data["accepted"] is True
        assert data["submitted"] is True
        assert data["append_status"] == "duplicate_existing_submission_returned"
        assert data["receipt_id"] == existing_receipt_id
        assert data["receipt"] is not None
        assert data["receipt"]["server_receipt_id"] == existing_receipt_id
        # Must not create new files or consume rate limit
        rate_mock.assert_not_called()
        put_mock.assert_not_called()
        dispatch_mock.assert_not_called()


class TestNewAcceptedSubmissionWritesIdempotencyIndex:
    """New accepted submission writes idempotency index."""

    def test_writes_idempotency_index_with_correct_schema(self, signed_echo_submission, monkeypatch):
        """A new accepted submission must write an idempotency index file
        with schema and correct submission_sha256."""
        put_calls: list[tuple[str, str]] = []

        async def mock_put_file(path, content, message, sha=None):
            put_calls.append((path, content))
            return {"content": {"sha": f"sha-{len(put_calls)}"}, "commit": {"sha": f"commit-{len(put_calls)}"}}

        monkeypatch.setattr("app.put_file", mock_put_file)
        monkeypatch.setattr("app.get_file_text", AsyncMock(return_value=None))
        monkeypatch.setattr("app.get_file_sha", AsyncMock(return_value=None))
        monkeypatch.setattr("app.dispatch_workflow", AsyncMock())
        monkeypatch.setattr("app.check_rate_limit", lambda body: None)

        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        data = resp.json()

        assert resp.status_code == 200
        assert data["accepted"] is True

        # Find the idempotency index write
        idempotency_writes = [
            (path, content) for path, content in put_calls
            if "by-submission-sha256" in path
        ]
        assert len(idempotency_writes) == 1, f"Expected 1 idempotency write, got {len(idempotency_writes)}"

        idx_path, idx_content = idempotency_writes[0]
        idx_data = json.loads(idx_content)
        assert idx_data["schema"] == "trinityaccord.record-chain-intake-idempotency.v1"
        assert len(idx_data["submission_sha256"]) == 64
        assert "stored_submission_sha256" in idx_data


class TestIndexWriteFailureRollbacksAndDoesNotDispatch:
    """Index write failure rolls back and does not dispatch."""

    def test_index_write_failure_rollbacks_and_returns_error(self, signed_echo_submission, monkeypatch):
        """When idempotency index write fails and no existing index, rollback and return error."""
        call_count = 0

        async def selective_put_file(path, content, message, sha=None):
            nonlocal call_count
            call_count += 1
            if "by-submission-sha256" in path:
                raise RuntimeError("GitHub API error: write failed")
            return {"content": {"sha": f"sha-{call_count}"}, "commit": {"sha": f"commit-{call_count}"}}

        delete_mock = AsyncMock(return_value=None)
        dispatch_mock = AsyncMock()

        monkeypatch.setattr("app.put_file", selective_put_file)
        monkeypatch.setattr("app.get_file_text", AsyncMock(return_value=None))
        monkeypatch.setattr("app.get_file_sha", AsyncMock(return_value=None))
        monkeypatch.setattr("app.delete_file", delete_mock)
        monkeypatch.setattr("app.dispatch_workflow", dispatch_mock)
        monkeypatch.setattr("app.check_rate_limit", lambda body: None)

        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        data = resp.json()

        assert data["accepted"] is False
        assert data["submitted"] is False
        codes = [d["code"] for d in data.get("diagnostics", [])]
        assert "IDEMPOTENCY_INDEX_PERSIST_FAILED" in codes
        assert delete_mock.call_count > 0
        dispatch_mock.assert_not_called()


class TestIndexWriteRaceReturnsExistingReceipt:
    """Index write race returns existing receipt and rolls back."""

    def test_index_write_race_returns_existing_receipt(self, signed_echo_submission, monkeypatch):
        """When idempotency index write fails but existing index found,
        return the existing receipt and rollback new files."""
        from gateway.canonical import sha256_canonical_json

        actual_sha = sha256_canonical_json(signed_echo_submission)
        existing_receipt_id = "rcg-20260101-existing123"
        existing_index = {
            "schema": "trinityaccord.record-chain-intake-idempotency.v1",
            "submission_sha256": actual_sha,
            "stored_submission_sha256": "b" * 64,
            "receipt_id": existing_receipt_id,
            "receipt_path": f"record-chain/intake/receipts/2026/01/{existing_receipt_id}.receipt.json",
            "pending_file_path": f"record-chain/pending/{existing_receipt_id}.echo.pending.json",
            "intake_submission_path": f"record-chain/intake/submissions/2026/01/{existing_receipt_id}.submission.json",
            "record_type": "echo",
            "created_at": "2026-01-01T00:00:00Z",
        }
        existing_receipt = {
            "server_receipt_id": existing_receipt_id,
            "accepted_at": "2026-01-01T00:00:00Z",
            "submission_sha256": actual_sha,
            "stored_submission_sha256": "b" * 64,
            "receipt_path": existing_index["receipt_path"],
            "pending_file_path": existing_index["pending_file_path"],
            "intake_submission_path": existing_index["intake_submission_path"],
        }

        put_call_count = 0
        get_text_call_count = 0

        async def selective_put_file(path, content, message, sha=None):
            nonlocal put_call_count
            put_call_count += 1
            if "by-submission-sha256" in path:
                raise RuntimeError("422 Validation Failed: already exists")
            return {"content": {"sha": f"sha-{put_call_count}"}, "commit": {"sha": f"commit-{put_call_count}"}}

        async def selective_get_file_text(path):
            nonlocal get_text_call_count
            get_text_call_count += 1
            # First call: pre-check returns None (no existing index yet)
            # Second call: _read_idempotency_index returns existing index (race won)
            if "by-submission-sha256" in path:
                if get_text_call_count == 1:
                    return None
                return json.dumps(existing_index)
            if existing_index["receipt_path"] in path:
                return json.dumps(existing_receipt)
            return None

        delete_mock = AsyncMock(return_value=None)
        dispatch_mock = AsyncMock()

        monkeypatch.setattr("app.put_file", selective_put_file)
        monkeypatch.setattr("app.get_file_text", selective_get_file_text)
        monkeypatch.setattr("app.get_file_sha", AsyncMock(return_value=None))
        monkeypatch.setattr("app.delete_file", delete_mock)
        monkeypatch.setattr("app.dispatch_workflow", dispatch_mock)
        monkeypatch.setattr("app.check_rate_limit", lambda body: None)

        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        data = resp.json()

        assert data["accepted"] is True
        assert data["submitted"] is True
        assert data["append_status"] == "duplicate_existing_submission_returned"
        assert data["receipt_id"] == existing_receipt_id
        assert delete_mock.call_count > 0
        dispatch_mock.assert_not_called()


class TestSameDayReceiptFallback:
    """Same-day receipt fallback: matching returns duplicate, mismatch refuses overwrite."""

    def test_matching_same_day_receipt_returns_duplicate(self, signed_echo_submission, monkeypatch):
        """When a same-day receipt matches submission hash, return it as duplicate."""
        from unittest.mock import patch
        from gateway.canonical import sha256_canonical_json

        actual_sha = sha256_canonical_json(signed_echo_submission)
        stored_sha = sha256_canonical_json(signed_echo_submission)  # same before redaction
        receipt_id = "rcg-20260601-abc123def456"
        receipt_path = f"record-chain/intake/receipts/2026/06/{receipt_id}.receipt.json"

        existing_receipt = {
            "server_receipt_id": receipt_id,
            "submission_sha256": actual_sha,
            "stored_submission_sha256": stored_sha,
            "receipt_path": receipt_path,
            "pending_file_path": f"record-chain/pending/{receipt_id}.echo.pending.json",
            "intake_submission_path": f"record-chain/intake/submissions/2026/06/{receipt_id}.submission.json",
            "accepted_at": "2026-06-01T00:00:00Z",
        }

        put_mock = AsyncMock()
        dispatch_mock = AsyncMock()

        async def mock_get_file_sha(path):
            if "receipt" in path:
                return "existing-sha"
            return None

        async def mock_get_file_text(path):
            if "by-submission-sha256" in path:
                return None  # No global index
            if "receipt" in path:
                return json.dumps(existing_receipt)
            return None

        async def mock_existing_match(**kwargs):
            return (receipt_path, existing_receipt)

        monkeypatch.setattr("app.get_file_sha", mock_get_file_sha)
        monkeypatch.setattr("app.get_file_text", mock_get_file_text)
        monkeypatch.setattr("app.put_file", put_mock)
        monkeypatch.setattr("app.dispatch_workflow", dispatch_mock)
        monkeypatch.setattr("app.check_rate_limit", lambda body: None)
        monkeypatch.setattr("app._find_existing_matching_receipt", mock_existing_match)

        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        data = resp.json()

        assert data["accepted"] is True
        assert data["submitted"] is True
        assert data["append_status"] == "duplicate_existing_receipt_returned"
        put_mock.assert_not_called()
        dispatch_mock.assert_not_called()

    def test_mismatched_same_day_receipt_refuses_overwrite(self, signed_echo_submission, monkeypatch):
        """When a same-day receipt exists but doesn't match, refuse overwrite."""
        from fastapi import HTTPException

        async def mock_find_existing(**kwargs):
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "RECEIPT_PATH_CONFLICT",
                    "message": "Receipt path already exists but does not bind to this exact submission.",
                },
            )

        put_mock = AsyncMock()
        dispatch_mock = AsyncMock()

        monkeypatch.setattr("app.get_file_sha", AsyncMock(return_value="existing-sha"))
        monkeypatch.setattr("app.get_file_text", AsyncMock(return_value=None))
        monkeypatch.setattr("app.put_file", put_mock)
        monkeypatch.setattr("app.dispatch_workflow", dispatch_mock)
        monkeypatch.setattr("app.check_rate_limit", lambda body: None)
        monkeypatch.setattr("app._find_existing_matching_receipt", mock_find_existing)

        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        data = resp.json()

        # Should be rejected (409 or accepted=false)
        assert resp.status_code in (200, 409)
        if resp.status_code == 200:
            assert data["accepted"] is False
        put_mock.assert_not_called()
        dispatch_mock.assert_not_called()
