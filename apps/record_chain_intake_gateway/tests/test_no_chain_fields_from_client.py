"""Tests: forbidden chain fields must be rejected."""
from __future__ import annotations

import copy

import pytest
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)

FORBIDDEN_FIELDS = [
    "record_index",
    "record_id",
    "assigned_at",
    "previous_record_sha256",
    "content_sha256",
    "record_sha256",
    "batch_id",
    "server_receipt_id",
    "created_by_gateway",
    "server_validated",
    "server_rendered",
]


class TestForbiddenChainFields:
    @pytest.mark.parametrize("field", FORBIDDEN_FIELDS)
    def test_rejected_at_submission_level(self, field, valid_echo_submission):
        valid_echo_submission[field] = "bad_value"
        resp = client.post("/record-chain/preflight", json=valid_echo_submission)
        data = resp.json()
        assert data["accepted"] is False, f"Field {field} at submission level not rejected"

    @pytest.mark.parametrize("field", FORBIDDEN_FIELDS)
    def test_rejected_in_record_draft(self, field, valid_echo_submission):
        valid_echo_submission["record_draft"][field] = "bad_value"
        resp = client.post("/record-chain/preflight", json=valid_echo_submission)
        data = resp.json()
        assert data["accepted"] is False, f"Field {field} in record_draft not rejected"

    def test_server_receipt_at_top_level_rejected(self, valid_echo_submission):
        valid_echo_submission["server_receipt"] = {"id": "fake"}
        resp = client.post("/record-chain/preflight", json=valid_echo_submission)
        data = resp.json()
        assert data["accepted"] is False
