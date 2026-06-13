"""Tests for /record-chain/submit endpoint."""
from __future__ import annotations

import json
import os
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


class TestSubmitWrites:
    def test_submit_writes_three_files(self, signed_echo_submission, mock_github):
        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        assert resp.status_code == 200
        data = resp.json()
        if data.get("accepted") is not True:
            import json as _json
            pytest.fail(f"Submit not accepted: {_json.dumps(data, indent=2)}")
        assert data["submitted"] is True

        # Check put_file was called 3 times
        put_mock = mock_github["put_file"]
        assert put_mock.call_count == 3

        paths = [call.args[0] for call in put_mock.call_args_list]
        assert any("intake/submissions/" in p for p in paths), f"Missing intake submission: {paths}"
        assert any("intake/receipts/" in p for p in paths), f"Missing intake receipt: {paths}"
        assert any("pending/" in p for p in paths), f"Missing pending file: {paths}"

    def test_pending_file_is_draft_only(self, signed_echo_submission, mock_github):
        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        assert resp.status_code == 200

        # Find the pending file write
        put_mock = mock_github["put_file"]
        pending_call = [c for c in put_mock.call_args_list if "pending/" in c.args[0]][0]
        pending_content = json.loads(pending_call.args[1])

        # Pending should be record_draft, not outer submission
        assert "schema" not in pending_content or pending_content.get("record_type") == "echo"
        assert "record_type" in pending_content

    def test_pending_has_authorship_proof(self, signed_echo_submission, mock_github):
        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        assert resp.status_code == 200

        put_mock = mock_github["put_file"]
        pending_call = [c for c in put_mock.call_args_list if "pending/" in c.args[0]][0]
        pending_content = json.loads(pending_call.args[1])
        assert "authorship_proof" in pending_content

    def test_pending_no_chain_fields(self, signed_echo_submission, mock_github):
        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        assert resp.status_code == 200

        put_mock = mock_github["put_file"]
        pending_call = [c for c in put_mock.call_args_list if "pending/" in c.args[0]][0]
        pending_content = json.loads(pending_call.args[1])

        forbidden = {"record_index", "record_id", "assigned_at", "previous_record_sha256",
                      "content_sha256", "record_sha256", "batch_id", "server_receipt_id"}
        for key in forbidden:
            assert key not in pending_content, f"Forbidden field {key} in pending file"

    def test_persist_failure_rolls_back_created_intake_files(self, signed_echo_submission, mock_github):
        mock_github["put_file"].side_effect = [
            {"content": {"sha": "submission-sha"}, "commit": {"sha": "c1"}},
            {"content": {"sha": "pending-sha"}, "commit": {"sha": "c2"}},
            RuntimeError("receipt write failed"),
        ]

        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        data = resp.json()

        assert data["accepted"] is False
        assert data["diagnostics"][0]["code"] == "PERSIST_FAILED"
        deleted = [call.args[0] for call in mock_github["delete_file"].await_args_list]
        assert any("pending/" in p for p in deleted)
        assert any("intake/submissions/" in p for p in deleted)


class TestSubmitResponse:
    def test_returns_receipt_id(self, signed_echo_submission, mock_github):
        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        data = resp.json()
        assert data["accepted"] is True
        assert "receipt_id" in data
        assert data["receipt_id"].startswith("rcg-")

    def test_returns_append_status_queued(self, signed_echo_submission, mock_github):
        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        data = resp.json()
        assert data.get("append_status") in ("queued", "pending")

    def test_dispatches_append_workflow_after_receipt(self, signed_echo_submission, mock_github):
        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        data = resp.json()
        assert data["accepted"] is True
        mock_github["dispatch_workflow"].assert_awaited_once()
        assert data.get("append_status") == "queued"

    def test_returns_paths(self, signed_echo_submission, mock_github):
        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        data = resp.json()
        assert "pending_file_path" in data
        assert "intake_submission_path" in data
        assert "receipt_path" in data

    def test_invalid_returns_errors(self, valid_echo_submission, mock_github):
        # Remove record_type to make it invalid
        del valid_echo_submission["record_type"]
        resp = client.post("/record-chain/submit", json=valid_echo_submission)
        data = resp.json()
        assert data["accepted"] is False


class TestSubmitConfigGateOrdering:
    """Bug A: invalid payload must return diagnostics even when write config is missing."""

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
        for key in ("TRINITY_REPO_FULL_NAME", "TRINITY_TARGET_BRANCH", "TRINITY_GITHUB_TOKEN"):
            monkeypatch.delenv(key, raising=False)

        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        assert resp.status_code == 503
