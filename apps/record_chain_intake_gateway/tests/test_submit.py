"""Tests for /record-chain/submit endpoint."""
from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def _atomic_files(mock_github) -> dict[str, str]:
    atomic_mock = mock_github["create_files_atomic"]
    atomic_mock.assert_awaited_once()
    files = atomic_mock.await_args.args[0]
    assert isinstance(files, dict)
    return files


def _content_for_path(files: dict[str, str], fragment: str) -> dict:
    matches = [content for path, content in files.items() if fragment in path]
    assert len(matches) == 1, f"Expected one atomic path containing {fragment!r}, got {list(files)}"
    return json.loads(matches[0])


class TestSubmitWrites:
    def test_submit_writes_one_atomic_transaction(self, signed_echo_submission, mock_github):
        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        assert resp.status_code == 200
        data = resp.json()
        if data.get("accepted") is not True:
            pytest.fail(f"Submit not accepted: {json.dumps(data, indent=2)}")
        assert data["submitted"] is True

        files = _atomic_files(mock_github)
        paths = list(files)
        assert len(paths) == 4
        assert any("intake/submissions/" in path for path in paths)
        assert any("intake/receipts/" in path for path in paths)
        assert any("pending/" in path for path in paths)
        assert any("by-submission-sha256/" in path for path in paths)

        index = _content_for_path(files, "by-submission-sha256/")
        assert index["transaction_state"] == "pending_written"
        assert index["pending_written"] is True
        assert index["pending_committed_at"]

    def test_pending_file_is_draft_only(self, signed_echo_submission, mock_github):
        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        assert resp.status_code == 200
        pending_content = _content_for_path(_atomic_files(mock_github), "record-chain/pending/")
        assert pending_content.get("record_type") == "echo"
        assert "submission_type" not in pending_content

    def test_pending_has_authorship_proof(self, signed_echo_submission, mock_github):
        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        assert resp.status_code == 200
        pending_content = _content_for_path(_atomic_files(mock_github), "record-chain/pending/")
        assert "authorship_proof" in pending_content

    def test_pending_no_chain_fields(self, signed_echo_submission, mock_github):
        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        assert resp.status_code == 200
        pending_content = _content_for_path(_atomic_files(mock_github), "record-chain/pending/")
        forbidden = {
            "record_index",
            "record_id",
            "assigned_at",
            "previous_record_sha256",
            "content_sha256",
            "record_sha256",
            "batch_id",
            "server_receipt_id",
        }
        for key in forbidden:
            assert key not in pending_content, f"Forbidden field {key} in pending file"

    def test_atomic_persist_failure_exposes_no_partial_success(self, signed_echo_submission, mock_github):
        mock_github["create_files_atomic"].side_effect = RuntimeError("atomic ref update failed")

        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        data = resp.json()

        assert data["accepted"] is False
        assert data["submitted"] is False
        assert data["diagnostics"][0]["code"] == "PERSIST_FAILED"
        mock_github["dispatch_workflow"].assert_not_awaited()


class TestSubmitResponse:
    def test_returns_receipt_id(self, signed_echo_submission, mock_github):
        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        data = resp.json()
        assert data["accepted"] is True
        assert data["receipt_id"].startswith("rcg-")

    def test_returns_append_status_queued(self, signed_echo_submission, mock_github):
        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        assert resp.json().get("append_status") == "queued"

    def test_dispatches_append_workflow_after_atomic_commit(self, signed_echo_submission, mock_github):
        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        data = resp.json()
        assert data["accepted"] is True
        mock_github["create_files_atomic"].assert_awaited_once()
        mock_github["dispatch_workflow"].assert_awaited_once()
        assert data.get("append_status") == "queued"

    def test_returns_paths(self, signed_echo_submission, mock_github):
        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        data = resp.json()
        assert "pending_file_path" in data
        assert "intake_submission_path" in data
        assert "receipt_path" in data

    def test_invalid_returns_errors(self, valid_echo_submission, mock_github):
        del valid_echo_submission["record_type"]
        resp = client.post("/record-chain/submit", json=valid_echo_submission)
        data = resp.json()
        assert data["accepted"] is False
        mock_github["create_files_atomic"].assert_not_awaited()


class TestSubmitConfigGateOrdering:
    """Invalid payloads must return diagnostics even when write config is missing."""

    def test_invalid_payload_returns_diagnostics_even_when_write_config_missing(self, monkeypatch):
        for key in ("TRINITY_REPO_FULL_NAME", "TRINITY_TARGET_BRANCH", "TRINITY_GITHUB_TOKEN"):
            monkeypatch.delenv(key, raising=False)

        resp = client.post("/record-chain/submit", json={"record_draft": {}})
        assert resp.status_code == 200
        data = resp.json()
        assert data["accepted"] is False
        assert data["submitted"] is False
        assert any(d["code"] == "MISSING_RECORD_TYPE" for d in data["diagnostics"])

    def test_valid_payload_missing_write_config_returns_503(self, signed_echo_submission, monkeypatch):
        preflight = client.post("/record-chain/preflight", json=signed_echo_submission)
        assert preflight.status_code == 200
        assert preflight.json()["accepted"] is True, f"Fixture must pass preflight: {preflight.json()}"

        monkeypatch.setattr("app._read_idempotency_index", AsyncMock(return_value=None))
        for key in ("TRINITY_REPO_FULL_NAME", "TRINITY_TARGET_BRANCH", "TRINITY_GITHUB_TOKEN"):
            monkeypatch.delenv(key, raising=False)

        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        assert resp.status_code == 503
