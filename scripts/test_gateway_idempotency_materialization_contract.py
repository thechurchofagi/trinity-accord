#!/usr/bin/env python3
"""Regression tests for idempotency materialization gate.

Verifies that duplicate idempotency responses fail-closed when the
pending file has not been materialized, and succeed when fully materialized.
"""
from __future__ import annotations

import json
import os
from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("TRINITY_REPO_FULL_NAME", "test/repo")
os.environ.setdefault("TRINITY_TARGET_BRANCH", "main")
os.environ.setdefault("TRINITY_GITHUB_TOKEN", "fake-token")

import app as app_module  # noqa: E402
from app import app  # noqa: E402

client = TestClient(app)


def _make_idempotency_index(
    *,
    transaction_state: str = "pending_written",
    pending_written: bool = True,
    pending_file_path: str = "record-chain/pending/rcg-20260617-abc.echo.pending.json",
) -> dict[str, Any]:
    return {
        "schema": "trinityaccord.record-chain-intake-idempotency.v1",
        "submission_sha256": "a" * 64,
        "stored_submission_sha256": "b" * 64,
        "receipt_id": "rcg-20260617-abcdef123456",
        "receipt_path": "record-chain/intake/receipts/2026/06/rcg-20260617-abcdef123456.receipt.json",
        "pending_file_path": pending_file_path,
        "intake_submission_path": "record-chain/intake/submissions/2026/06/rcg-20260617-abcdef123456.submission.json",
        "record_type": "echo",
        "created_at": "2026-06-17T00:00:00Z",
        "transaction_state": transaction_state,
        "receipt_written": True,
        "idempotency_written": True,
        "pending_written": pending_written,
        "pending_committed_at": "2026-06-17T00:00:01Z" if pending_written else None,
    }


def _make_receipt() -> dict[str, Any]:
    receipt = {
        "schema": "trinityaccord.record-chain-receipt.v1",
        "server_receipt_id": "rcg-20260617-abcdef123456",
        "accepted_at": "2026-06-17T00:00:00Z",
        "record_type": "echo",
        "pending_file_path": "record-chain/pending/rcg-20260617-abcdef123456.echo.pending.json",
    }
    # Compute receipt_sha256 (excluding the field itself)
    material = {k: v for k, v in receipt.items() if k != "receipt_sha256"}
    import hashlib
    receipt["receipt_sha256"] = hashlib.sha256(
        json.dumps(material, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return receipt


def _mock_get_file_text(path: str) -> str | None:
    """Mock get_file_text: return receipt for receipt paths, None otherwise."""
    if "receipts/" in path:
        return json.dumps(_make_receipt())
    return None


class TestNotMaterializedPendingWrittenFalse:
    """Case 1: index has pending_written=false → must not return submitted=true."""

    def test_pending_written_false_returns_not_materialized(
        self, signed_echo_submission, monkeypatch
    ):
        idx = _make_idempotency_index(pending_written=False, transaction_state="idempotency_written")
        receipt = _make_receipt()

        async def mock_get_file_text(path):
            if "by-submission-sha256" in path:
                return json.dumps(idx)
            if "receipts/" in path:
                return json.dumps(receipt)
            return None

        async def mock_get_file_sha(path):
            return None

        monkeypatch.setattr("app.get_file_text", mock_get_file_text)
        monkeypatch.setattr("app.get_file_sha", mock_get_file_sha)
        monkeypatch.setattr("app.check_rate_limit", lambda body: None)

        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        data = resp.json()

        assert data["accepted"] is False
        assert data["submitted"] is False
        codes = [d["code"] for d in data.get("diagnostics", [])]
        assert "INTAKE_TRANSACTION_NOT_MATERIALIZED" in codes, f"Expected INTAKE_TRANSACTION_NOT_MATERIALIZED, got {codes}"


class TestMaterializedButPendingFileMissing:
    """Case 2: index claims materialized but pending file is missing."""

    def test_pending_file_missing_returns_not_materialized(
        self, signed_echo_submission, monkeypatch
    ):
        idx = _make_idempotency_index(pending_written=True, transaction_state="pending_written")
        receipt = _make_receipt()

        async def mock_get_file_text(path):
            if "by-submission-sha256" in path:
                return json.dumps(idx)
            if "receipts/" in path:
                return json.dumps(receipt)
            return None

        async def mock_get_file_sha(path):
            if "pending/" in path:
                return None  # pending file missing
            return "some-sha"

        monkeypatch.setattr("app.get_file_text", mock_get_file_text)
        monkeypatch.setattr("app.get_file_sha", mock_get_file_sha)
        monkeypatch.setattr("app.check_rate_limit", lambda body: None)

        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        data = resp.json()

        assert data["accepted"] is False
        assert data["submitted"] is False
        codes = [d["code"] for d in data.get("diagnostics", [])]
        assert "INTAKE_TRANSACTION_NOT_MATERIALIZED" in codes, f"Expected INTAKE_TRANSACTION_NOT_MATERIALIZED, got {codes}"


class TestFullyMaterialized:
    """Case 3: fully materialized → duplicate response succeeds."""

    def test_fully_materialized_returns_success(
        self, signed_echo_submission, monkeypatch
    ):
        idx = _make_idempotency_index()
        receipt = _make_receipt()

        async def mock_get_file_text(path):
            if "by-submission-sha256" in path:
                return json.dumps(idx)
            if "receipts/" in path:
                return json.dumps(receipt)
            return None

        async def mock_get_file_sha(path):
            return "pending-sha"

        monkeypatch.setattr("app.get_file_text", mock_get_file_text)
        monkeypatch.setattr("app.get_file_sha", mock_get_file_sha)
        monkeypatch.setattr("app.check_rate_limit", lambda body: None)

        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        data = resp.json()

        assert data["accepted"] is True
        assert data["submitted"] is True
        assert data["append_status"] == "duplicate_existing_submission_returned"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
