"""Tests: echo output must not contain echo_type field.

Commit 5 — Phase 5C: builder echo output has no ``echo_type`` field.
``echo_type`` is a retired field (see RETIRED_FIELDS in validation.py).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from gateway.validation import (
    RETIRED_FIELDS,
    validate_submission,
)


def _echo_draft() -> dict:
    """Minimal echo record_draft with all v2 blocks."""
    return {
        "record_type": "echo",
        "schema": "trinityaccord.record-chain-entry.v1",
        "created_at": "2026-06-01T00:00:00Z",
        "actor_identity": {"actor_type": "ai_agent", "display_label": "Test Agent"},
        "submitting_participant_identity": {
            "participant_public_display_label": "Test Agent",
            "participant_type": "ai_agent",
            "participant_identifier_disclosure_status": "not_disclosed",
            "participant_identity_disclosure_preference": "pseudonym_only",
        },
        "discovery_and_introduction_context": {"discovery_method": "direct_url"},
        "decision_autonomy_context": {"autonomy_level": "agent_initiated"},
        "submission_execution_context": {"builder_tool": "test"},
        "authorization_context": {"authorization_basis": "self_initiated"},
        "context_readiness": {
            "declared_context_level": 3,
            "minimum_required_for_action": "CC-3",
            "context_sufficient_for_selected_action": True,
        },
        "non_authority_boundary_acknowledgement": {
            "not_authority": True,
            "not_governance": True,
            "not_attestation": True,
            "not_successor_reception": True,
            "not_amendment": True,
            "bitcoin_originals_prevail": True,
        },
        "payload": {"title": "Test", "body": "echo body"},
    }


class TestNoEchoTypeInDraft:
    """Verify the echo draft does not carry the retired echo_type field."""

    def test_echo_type_not_in_draft(self):
        draft = _echo_draft()
        assert "echo_type" not in draft, "echo_type must not appear in echo draft"

    def test_echo_type_is_retired(self):
        assert "echo_type" in RETIRED_FIELDS

    def test_draft_record_type_is_echo(self):
        draft = _echo_draft()
        assert draft["record_type"] == "echo"

    def test_echo_type_rejected_by_validation(self):
        """If someone injects echo_type, validation rejects it."""
        draft = _echo_draft()
        draft["echo_type"] = "recognition"
        submission = {
            "record_type": "echo",
            "record_draft": draft,
            "boundary_acknowledgement": {
                "not_authority": True,
                "not_governance": True,
                "not_attestation": True,
                "not_successor_reception": True,
                "not_amendment": True,
                "bitcoin_originals_prevail": True,
            },
        }
        diagnostics = validate_submission(submission)
        codes = [d.code for d in diagnostics]
        assert "RETIRED_FIELD" in codes, f"Expected RETIRED_FIELD diagnostic, got {codes}"

    def test_smoke_echo_file_if_exists(self):
        """If /tmp/trinity-smoke-echo.json exists, verify it has no echo_type."""
        smoke_path = Path("/tmp/trinity-smoke-echo.json")
        if not smoke_path.exists():
            pytest.skip("No smoke echo file at /tmp/trinity-smoke-echo.json")
        data = json.loads(smoke_path.read_text())
        draft = data.get("record_draft") or data.get("draft") or data
        assert "echo_type" not in draft, "Smoke echo file contains retired echo_type"
        assert draft.get("record_type") == "echo"
