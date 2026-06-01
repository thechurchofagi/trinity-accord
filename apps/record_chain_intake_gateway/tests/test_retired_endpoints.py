"""Tests for retired Gateway v1 endpoints."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


class TestRetiredEndpoints:
    def test_gateway_preflight_retired(self):
        resp = client.post("/gateway/preflight", json={"test": True})
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("retired") is True
        assert "/record-chain/preflight" in data.get("redirect_to", "")

    def test_agent_submit_retired(self):
        resp = client.post("/agent-submit", json={"test": True})
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("retired") is True
        assert "/record-chain/submit" in data.get("redirect_to", "")

    def test_retired_endpoints_dont_persist(self, mock_github):
        """Retired endpoints should not write anything."""
        client.post("/gateway/preflight", json={"test": True})
        client.post("/agent-submit", json={"test": True})
        mock_github["put_file"].assert_not_called()
