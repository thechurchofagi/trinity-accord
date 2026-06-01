"""Tests for /record-chain/preflight endpoint."""
from __future__ import annotations

import copy
import json
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


class TestPreflightValid:
    def test_valid_echo_accepted(self, signed_echo_submission):
        resp = client.post("/record-chain/preflight", json=signed_echo_submission)
        assert resp.status_code == 200
        data = resp.json()
        assert data["accepted"] is True
        assert data["preflight"] is True
        assert data["record_type"] == "echo"

    def test_valid_context_insufficient_accepted(self, valid_context_insufficient_submission):
        resp = client.post("/record-chain/preflight", json=valid_context_insufficient_submission)
        assert resp.status_code == 200
        data = resp.json()
        assert data["accepted"] is True
        assert data["record_type"] == "context_insufficient_notice"


class TestPreflightRejection:
    def test_invalid_json_object(self):
        resp = client.post("/record-chain/preflight", content="not json", headers={"content-type": "application/json"})
        # Gateway returns 200 with accepted=false for parse errors
        data = resp.json()
        assert data.get("accepted") is False or resp.status_code in (400, 422)

    def test_unknown_record_type(self, valid_echo_submission):
        valid_echo_submission["record_type"] = "unknown_type"
        valid_echo_submission["record_draft"]["record_type"] = "unknown_type"
        resp = client.post("/record-chain/preflight", json=valid_echo_submission)
        assert resp.status_code == 200
        data = resp.json()
        assert data["accepted"] is False
        assert any("Unknown record_type" in d.get("message", "") or "unknown" in d.get("message", "").lower() or "unknown" in d.get("code", "").lower() for d in data.get("diagnostics", []))

    def test_attestation_rejected(self, valid_echo_submission):
        valid_echo_submission["record_type"] = "attestation"
        valid_echo_submission["record_draft"]["record_type"] = "attestation"
        resp = client.post("/record-chain/preflight", json=valid_echo_submission)
        assert resp.status_code == 200
        data = resp.json()
        assert data["accepted"] is False

    def test_amendment_rejected(self, valid_echo_submission):
        valid_echo_submission["record_type"] = "amendment"
        valid_echo_submission["record_draft"]["record_type"] = "amendment"
        resp = client.post("/record-chain/preflight", json=valid_echo_submission)
        assert resp.status_code == 200
        data = resp.json()
        assert data["accepted"] is False

    def test_missing_boundary(self, valid_echo_submission):
        del valid_echo_submission["boundary_acknowledgement"]
        resp = client.post("/record-chain/preflight", json=valid_echo_submission)
        assert resp.status_code == 200
        data = resp.json()
        assert data["accepted"] is False

    def test_missing_context_readiness(self, valid_echo_submission):
        del valid_echo_submission["record_draft"]["context_readiness"]
        resp = client.post("/record-chain/preflight", json=valid_echo_submission)
        assert resp.status_code == 200
        data = resp.json()
        assert data["accepted"] is False


class TestPreflightResponseShape:
    def test_response_has_required_fields(self, signed_echo_submission):
        resp = client.post("/record-chain/preflight", json=signed_echo_submission)
        data = resp.json()
        assert "accepted" in data
        assert "preflight" in data
        assert "route_detected" in data or "route" in data
        assert "diagnostics" in data or "errors" in data
        assert "boundary" in data
