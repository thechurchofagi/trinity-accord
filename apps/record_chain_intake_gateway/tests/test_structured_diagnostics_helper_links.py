"""Tests: preflight diagnostics include help_url, suggested_fix, retry_allowed.

Commit 5 — Phase 5C: structured diagnostics with helper links.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app import app
from gateway.validation import _make_diagnostic, validate_submission

client = TestClient(app)


class TestStructuredDiagnosticsFields:
    """Diagnostics should have help_url, suggested_fix, retry_allowed."""

    def test_diagnostic_has_help_url(self):
        diag = _make_diagnostic(
            code="TEST_CODE",
            severity="error",
            field="test.field",
            message="test message",
        )
        assert diag.help_url is not None
        assert diag.help_url.startswith("http")

    def test_diagnostic_has_suggested_fix(self):
        diag = _make_diagnostic(
            code="TEST_CODE",
            severity="error",
            field="test.field",
            message="test message",
            suggested_fix="Fix it like this",
        )
        assert diag.suggested_fix == "Fix it like this"

    def test_diagnostic_has_retry_allowed(self):
        diag = _make_diagnostic(
            code="TEST_CODE",
            severity="error",
            field="test.field",
            message="test message",
        )
        assert isinstance(diag.retry_allowed, bool)

    def test_diagnostic_retry_allowed_default_true(self):
        diag = _make_diagnostic(
            code="TEST_CODE",
            severity="error",
            field=None,
            message="test",
        )
        assert diag.retry_allowed is True

    def test_diagnostic_retry_allowed_can_be_false(self):
        diag = _make_diagnostic(
            code="SECURITY_VIOLATION",
            severity="error",
            field=None,
            message="security issue",
            retry_allowed=False,
        )
        assert diag.retry_allowed is False

    def test_help_url_contains_code(self):
        diag = _make_diagnostic(
            code="MISSING_CONTEXT_READINESS",
            severity="error",
            field="draft.context_readiness",
            message="missing context",
        )
        assert "MISSING_CONTEXT_READINESS" in diag.help_url


class TestPreflightDiagnosticsHaveStructuredFields:
    """Preflight response diagnostics should have structured helper fields."""

    def test_error_diagnostics_have_help_url(self, valid_echo_submission):
        # Remove a required block to trigger diagnostics
        del valid_echo_submission["record_draft"]["context_readiness"]
        resp = client.post("/record-chain/preflight", json=valid_echo_submission)
        data = resp.json()
        assert data["accepted"] is False
        for diag in data.get("diagnostics", []):
            if diag.get("severity") == "error":
                assert "help_url" in diag, f"Diagnostic {diag.get('code')} missing help_url"

    def test_error_diagnostics_have_suggested_fix(self, valid_echo_submission):
        del valid_echo_submission["record_draft"]["submitting_participant_identity"]
        resp = client.post("/record-chain/preflight", json=valid_echo_submission)
        data = resp.json()
        assert data["accepted"] is False
        for diag in data.get("diagnostics", []):
            if diag.get("severity") == "error":
                assert "suggested_fix" in diag, f"Diagnostic {diag.get('code')} missing suggested_fix"

    def test_error_diagnostics_have_retry_allowed(self, valid_echo_submission):
        del valid_echo_submission["record_draft"]["authorization_context"]
        resp = client.post("/record-chain/preflight", json=valid_echo_submission)
        data = resp.json()
        assert data["accepted"] is False
        for diag in data.get("diagnostics", []):
            if diag.get("severity") == "error":
                assert "retry_allowed" in diag, f"Diagnostic {diag.get('code')} missing retry_allowed"

    def test_security_violation_retry_false(self, valid_echo_submission):
        """Security violations should have retry_allowed=false."""
        valid_echo_submission["record_draft"]["secret"] = "BEGIN PRIVATE KEY"
        resp = client.post("/record-chain/preflight", json=valid_echo_submission)
        data = resp.json()
        security_diags = [
            d for d in data.get("diagnostics", [])
            if d.get("code", "").startswith("SECURITY")
        ]
        if security_diags:
            for diag in security_diags:
                assert diag.get("retry_allowed") is False


class TestAgentRecoveryHasStructuredFields:
    """Agent recovery guidance should reference doctor commands."""

    def test_agent_recovery_present_on_failure(self, valid_echo_submission):
        del valid_echo_submission["record_draft"]["context_readiness"]
        resp = client.post("/record-chain/preflight", json=valid_echo_submission)
        data = resp.json()
        assert data["accepted"] is False
        recovery = data.get("agent_recovery")
        assert recovery is not None, "agent_recovery should be present on failed preflight"

    def test_agent_recovery_has_should_retry(self, valid_echo_submission):
        del valid_echo_submission["record_draft"]["context_readiness"]
        resp = client.post("/record-chain/preflight", json=valid_echo_submission)
        data = resp.json()
        recovery = data.get("agent_recovery", {})
        assert "should_retry" in recovery

    def test_agent_recovery_has_recommended_next_step(self, valid_echo_submission):
        del valid_echo_submission["record_draft"]["context_readiness"]
        resp = client.post("/record-chain/preflight", json=valid_echo_submission)
        data = resp.json()
        recovery = data.get("agent_recovery", {})
        assert "recommended_next_step" in recovery
