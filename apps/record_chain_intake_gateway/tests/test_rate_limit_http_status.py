"""Part F: rate-limit returns HTTP 429 test."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


class TestRateLimitHttpStatus:
    """Verify rate-limited submit returns HTTP 429."""

    def test_submit_rate_limit_returns_429(self, signed_echo_submission, monkeypatch):
        """Rate-limited submit must return 429 with retry_after_seconds."""
        def fake_limited(_submission):
            return {
                "diagnostics": [{
                    "code": "RATE_LIMIT_EXCEEDED",
                    "severity": "error",
                    "field": "submit",
                    "message": "Rate limit exceeded",
                    "meaning": "Test rate limit",
                    "suggested_fix": "Wait",
                    "retry_allowed": True,
                }],
                "retry_after_seconds": 3600,
                "rate_limit": {"limit_type": "participant", "limit": 0, "window_seconds": 3600},
            }

        monkeypatch.setattr("app.check_rate_limit", fake_limited)
        resp = client.post("/record-chain/submit", json=signed_echo_submission)
        assert resp.status_code == 429
        data = resp.json()
        assert data["accepted"] is False
        assert any(d["code"] == "RATE_LIMIT_EXCEEDED" for d in data["diagnostics"])
        assert "retry_after_seconds" in data
