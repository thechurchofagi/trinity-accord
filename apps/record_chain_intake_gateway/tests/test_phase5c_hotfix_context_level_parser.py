"""Phase 5C hotfix tests: CC-N context level parser.

Tests that the gateway accepts both 'CC-3' string and integer 3 for context level.
"""
from __future__ import annotations

import pytest

from gateway.validation import _parse_context_level_value, validate_submission


class TestContextLevelParser:
    """_parse_context_level_value must accept CC-N strings and integers."""

    def test_cc3_string(self):
        assert _parse_context_level_value("CC-3") == 3

    def test_cc2_string(self):
        assert _parse_context_level_value("CC-2") == 2

    def test_cc0_string(self):
        assert _parse_context_level_value("CC-0") == 0

    def test_lowercase_cc(self):
        assert _parse_context_level_value("cc-3") == 3

    def test_whitespace_cc(self):
        assert _parse_context_level_value("  CC-3  ") == 3

    def test_integer_value(self):
        assert _parse_context_level_value(3) == 3

    def test_string_integer(self):
        assert _parse_context_level_value("3") == 3

    def test_bool_returns_none(self):
        assert _parse_context_level_value(True) is None

    def test_none_returns_none(self):
        assert _parse_context_level_value(None) is None

    def test_invalid_string_returns_none(self):
        assert _parse_context_level_value("invalid") is None

    def test_float_returns_none(self):
        assert _parse_context_level_value(3.5) is None


def _make_submission_with_context_level(level) -> dict:
    """Create a minimal echo submission with the given context level."""
    from conftest import add_mock_proof
    return add_mock_proof({
        "record_type": "echo",
        "record_draft": {
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
                "declared_context_level": level,
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
                "receipt_is_not_final_inclusion": True,
                "receipt_is_intake_only": True, "later_records_may_reclassify_or_correct_this_record": True,
            },
            "optional_linked_guardian_application_request": None,
            "payload": {"title": "Test", "body": "test body"},
        },
        "boundary_acknowledgement": {
            "not_authority": True,
            "not_governance": True,
            "not_attestation": True,
            "not_successor_reception": True,
            "not_amendment": True,
            "bitcoin_originals_prevail": True,
            "receipt_is_not_final_inclusion": True,
            "receipt_is_intake_only": True, "later_records_may_reclassify_or_correct_this_record": True,
        },
    })


class TestContextLevelInValidation:
    """validate_submission must accept CC-N strings from builder output."""

    def test_cc3_accepted(self):
        sub = _make_submission_with_context_level("CC-3")
        diagnostics = validate_submission(sub)
        context_errors = [d for d in diagnostics if d.code in ("INVALID_CONTEXT_LEVEL", "MISSING_CONTEXT_READINESS")]
        assert context_errors == [], f"CC-3 should be accepted: {[d.message for d in context_errors]}"

    def test_integer_3_accepted(self):
        sub = _make_submission_with_context_level(3)
        diagnostics = validate_submission(sub)
        context_errors = [d for d in diagnostics if d.code in ("INVALID_CONTEXT_LEVEL", "MISSING_CONTEXT_READINESS")]
        assert context_errors == []

    def test_string_3_accepted(self):
        sub = _make_submission_with_context_level("3")
        diagnostics = validate_submission(sub)
        context_errors = [d for d in diagnostics if d.code in ("INVALID_CONTEXT_LEVEL", "MISSING_CONTEXT_READINESS")]
        assert context_errors == []

    def test_cc0_accepted(self):
        sub = _make_submission_with_context_level("CC-0")
        diagnostics = validate_submission(sub)
        context_errors = [d for d in diagnostics if d.code == "INVALID_CONTEXT_LEVEL"]
        assert context_errors == []

    def test_invalid_level_rejected(self):
        sub = _make_submission_with_context_level("invalid")
        diagnostics = validate_submission(sub)
        codes = [d.code for d in diagnostics]
        assert "INVALID_CONTEXT_LEVEL" in codes
