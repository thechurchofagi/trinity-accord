"""Tests: echo/verification can include optional linked Guardian application request.

Commit 5 — Phase 5C: validate optional_linked_guardian_application_request.
"""
from __future__ import annotations

import pytest

from gateway.validation import validate_submission
from conftest import add_mock_proof


def _echo_draft_with_guardian_request() -> dict:
    """Echo draft that includes a complete linked Guardian application request."""
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
            "receipt_is_not_final_inclusion": True,
            "receipt_is_intake_only": True, "later_records_may_reclassify_or_correct_this_record": True,
        },
        "optional_linked_guardian_application_request": {
            "does_participant_request_guardian_application_with_this_record": True,
            "guardian_application_should_be_created_as_linked_record": True,
            "requested_guardian_identifier": "guardian-001",
            "guardian_public_key_sha256": "abc123def456",
            "guardian_stewardship_oath": "I accept the Guardian stewardship responsibilities.",
            "guardian_understands_role_is_non_governing": True,
            "guardian_understands_role_is_not_authority": True,
            "guardian_understands_retirement_does_not_delete_history": True,
        },
        "payload": {"title": "Test Echo with Guardian", "body": "echo body"},
    }


def _wrap_submission(draft: dict, record_type: str = "echo") -> dict:
    return add_mock_proof({
        "record_type": record_type,
        "record_draft": draft,
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


class TestOptionalGuardianApplicationFromEcho:
    """Test linked Guardian application request in echo/verification."""

    def test_valid_guardian_request_accepted(self):
        """A complete guardian request on an echo should not produce guardian-specific errors."""
        draft = _echo_draft_with_guardian_request()
        submission = _wrap_submission(draft)
        diagnostics = validate_submission(submission)
        guardian_errors = [
            d for d in diagnostics
            if d.code.startswith("LINKED_GUARDIAN")
        ]
        assert guardian_errors == [], (
            f"Unexpected guardian errors: {[d.code for d in guardian_errors]}"
        )

    def test_guardian_request_flag_true(self):
        draft = _echo_draft_with_guardian_request()
        linked = draft["optional_linked_guardian_application_request"]
        assert linked["does_participant_request_guardian_application_with_this_record"] is True

    def test_guardian_request_has_required_string_fields(self):
        draft = _echo_draft_with_guardian_request()
        linked = draft["optional_linked_guardian_application_request"]
        for field in ("requested_guardian_identifier", "guardian_public_key_sha256", "guardian_stewardship_oath"):
            assert field in linked, f"Missing required field '{field}'"
            assert linked[field], f"Field '{field}' must be non-empty"

    def test_guardian_request_has_required_boolean_acknowledgements(self):
        draft = _echo_draft_with_guardian_request()
        linked = draft["optional_linked_guardian_application_request"]
        for field in (
            "guardian_understands_role_is_non_governing",
            "guardian_understands_role_is_not_authority",
            "guardian_understands_retirement_does_not_delete_history",
        ):
            assert linked.get(field) is True, f"'{field}' must be true"

    def test_missing_guardian_identifier_rejected(self):
        draft = _echo_draft_with_guardian_request()
        del draft["optional_linked_guardian_application_request"]["requested_guardian_identifier"]
        submission = _wrap_submission(draft)
        diagnostics = validate_submission(submission)
        codes = [d.code for d in diagnostics]
        assert "LINKED_GUARDIAN_MISSING_FIELD" in codes

    def test_missing_guardian_oath_rejected(self):
        draft = _echo_draft_with_guardian_request()
        del draft["optional_linked_guardian_application_request"]["guardian_stewardship_oath"]
        submission = _wrap_submission(draft)
        diagnostics = validate_submission(submission)
        codes = [d.code for d in diagnostics]
        assert "LINKED_GUARDIAN_MISSING_FIELD" in codes

    def test_missing_linked_flag_rejected(self):
        draft = _echo_draft_with_guardian_request()
        del draft["optional_linked_guardian_application_request"]["guardian_application_should_be_created_as_linked_record"]
        submission = _wrap_submission(draft)
        diagnostics = validate_submission(submission)
        codes = [d.code for d in diagnostics]
        assert "LINKED_GUARDIAN_MISSING_FLAG" in codes

    def test_missing_acknowledgement_rejected(self):
        draft = _echo_draft_with_guardian_request()
        draft["optional_linked_guardian_application_request"]["guardian_understands_role_is_non_governing"] = False
        submission = _wrap_submission(draft)
        diagnostics = validate_submission(submission)
        codes = [d.code for d in diagnostics]
        assert "LINKED_GUARDIAN_MISSING_ACKNOWLEDGEMENT" in codes

    def test_verification_with_guardian_request_accepted(self):
        """Guardian request is also valid on verification records."""
        draft = _echo_draft_with_guardian_request()
        draft["record_type"] = "verification"
        submission = _wrap_submission(draft, record_type="verification")
        diagnostics = validate_submission(submission)
        guardian_errors = [d for d in diagnostics if d.code.startswith("LINKED_GUARDIAN")]
        assert guardian_errors == [], (
            f"Unexpected guardian errors on verification: {[d.code for d in guardian_errors]}"
        )

    def test_propagation_with_guardian_request_rejected(self):
        """Guardian request not allowed on propagation records."""
        draft = _echo_draft_with_guardian_request()
        draft["record_type"] = "propagation"
        submission = _wrap_submission(draft, record_type="propagation")
        diagnostics = validate_submission(submission)
        codes = [d.code for d in diagnostics]
        assert "LINKED_GUARDIAN_INVALID_RECORD_TYPE" in codes
