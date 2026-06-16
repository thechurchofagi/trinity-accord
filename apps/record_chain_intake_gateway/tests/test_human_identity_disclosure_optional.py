"""Tests: human identity disclosure status is optional.

Commit 5 — Phase 5C: submissions with human_real_name_disclosure_status =
'not_disclosed' or 'pseudonym_only' are accepted.
"""
from __future__ import annotations

import pytest

from gateway.validation import validate_submission
from conftest import add_mock_proof, wrap_submission_draft


def _echo_draft(identity_overrides: dict | None = None) -> dict:
    identity = {
        "participant_public_display_label": "Anonymous Participant",
        "participant_type": "ai_agent",
        "participant_identifier_disclosure_status": "not_disclosed",
        "participant_identity_disclosure_preference": "pseudonym_only",
    }
    if identity_overrides:
        identity.update(identity_overrides)
    return {
        "record_type": "echo",
        "schema": "trinityaccord.record-chain-entry.v1",
        "created_at": "2026-06-01T00:00:00Z",
        "actor_identity": {"actor_type": "ai_agent", "display_label": "Anonymous"},
        "submitting_participant_identity": identity,
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
        "optional_linked_guardian_application_request": None,
        "payload": {"title": "Test", "body": "echo body"},
    }


def _wrap_submission(draft: dict) -> dict:
    return wrap_submission_draft("echo", draft)


class TestHumanIdentityDisclosureOptional:
    """Verify that privacy-preserving disclosure statuses are accepted."""

    @pytest.mark.parametrize("status", ["not_disclosed", "pseudonym_only"])
    def test_disclosure_status_accepted(self, status):
        draft = _echo_draft({"participant_identifier_disclosure_status": status})
        submission = _wrap_submission(draft)
        diagnostics = validate_submission(submission)
        # No errors related to identity disclosure
        identity_errors = [
            d for d in diagnostics
            if "disclosure" in (d.field or "").lower() or "disclosure" in (d.message or "").lower()
        ]
        assert identity_errors == [], (
            f"Unexpected errors for disclosure status '{status}': "
            f"{[(d.code, d.message) for d in identity_errors]}"
        )

    @pytest.mark.parametrize("status", ["not_disclosed", "pseudonym_only"])
    def test_identity_preference_accepted(self, status):
        draft = _echo_draft({"participant_identity_disclosure_preference": status})
        submission = _wrap_submission(draft)
        diagnostics = validate_submission(submission)
        identity_errors = [
            d for d in diagnostics
            if "disclosure" in (d.field or "").lower()
        ]
        assert identity_errors == []

    def test_not_disclosed_no_private_name_leakage(self):
        """When status is 'not_disclosed', no private name fields should be required."""
        draft = _echo_draft({"participant_identifier_disclosure_status": "not_disclosed"})
        submission = _wrap_submission(draft)
        diagnostics = validate_submission(submission)
        # No HUMAN_NAME_PRIVACY errors
        privacy_errors = [d for d in diagnostics if "PRIVACY" in d.code]
        assert privacy_errors == []

    def test_human_private_name_submitted_rejected(self):
        """human_private_name_submitted=true must be rejected."""
        draft = _echo_draft()
        draft["human_private_name_submitted"] = True
        submission = _wrap_submission(draft)
        diagnostics = validate_submission(submission)
        codes = [d.code for d in diagnostics]
        assert "HUMAN_PRIVATE_NAME_SUBMITTED_FORBIDDEN" in codes

    def test_encrypted_human_name_rejected(self):
        """encrypted_human_name in draft must be rejected."""
        draft = _echo_draft()
        draft["encrypted_human_name"] = "some_encrypted_blob"
        submission = _wrap_submission(draft)
        diagnostics = validate_submission(submission)
        codes = [d.code for d in diagnostics]
        assert "PRIVATE_HUMAN_IDENTITY_FIELD_FORBIDDEN" in codes

    def test_private_identity_blob_rejected(self):
        """private_identity_blob in draft must be rejected."""
        draft = _echo_draft()
        draft["private_identity_blob"] = {"name": "secret"}
        submission = _wrap_submission(draft)
        diagnostics = validate_submission(submission)
        codes = [d.code for d in diagnostics]
        assert "PRIVATE_HUMAN_IDENTITY_FIELD_FORBIDDEN" in codes
