"""Tests: echo submissions contain all v2 common field blocks.

Commit 5 — Phase 5C: verify v2 common identity and autonomy fields.
"""
from __future__ import annotations

import pytest

from gateway.validation import (
    _REQUIRED_V2_BLOCKS,
    validate_submission,
)
from conftest import add_mock_proof

# The 8 v2 common blocks required for formal record types.
EXPECTED_V2_BLOCKS = {
    "submitting_participant_identity",
    "discovery_and_introduction_context",
    "decision_autonomy_context",
    "submission_execution_context",
    "authorization_context",
    "context_readiness",
    "non_authority_boundary_acknowledgement",
    "optional_linked_guardian_application_request",
}


def _echo_draft(**overrides) -> dict:
    draft = {
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
        "optional_linked_guardian_application_request": None,
        "payload": {"title": "Test", "body": "echo body"},
    }
    draft.update(overrides)
    return draft


def _wrap_submission(draft: dict) -> dict:
    return add_mock_proof({
        "record_type": "echo",
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


class TestV2CommonBlocksPresent:
    """All v2 common blocks must be present in echo submissions."""

    def test_all_expected_blocks_in_draft(self):
        draft = _echo_draft()
        for block in EXPECTED_V2_BLOCKS:
            assert block in draft, f"Missing v2 block '{block}' in echo draft"

    def test_validation_constant_covers_seven_required(self):
        """_REQUIRED_V2_BLOCKS has the 7 mandatory blocks (optional_linked is optional)."""
        assert len(_REQUIRED_V2_BLOCKS) == 7
        for block in EXPECTED_V2_BLOCKS - {"optional_linked_guardian_application_request"}:
            assert block in _REQUIRED_V2_BLOCKS

    @pytest.mark.parametrize("block", sorted(EXPECTED_V2_BLOCKS - {"optional_linked_guardian_application_request"}))
    def test_missing_block_causes_validation_error(self, block):
        """Removing any required v2 block must cause a validation error."""
        draft = _echo_draft()
        del draft[block]
        submission = _wrap_submission(draft)
        diagnostics = validate_submission(submission)
        codes = [d.code for d in diagnostics]
        assert "MISSING_V2_BLOCK" in codes, (
            f"Removing '{block}' should trigger MISSING_V2_BLOCK, got {codes}"
        )

    def test_optional_linked_guardian_can_be_none(self):
        """optional_linked_guardian_application_request may be None without error."""
        draft = _echo_draft()
        draft["optional_linked_guardian_application_request"] = None
        submission = _wrap_submission(draft)
        diagnostics = validate_submission(submission)
        # Should not have MISSING_V2_BLOCK for this field
        assert not any(
            d.code == "MISSING_V2_BLOCK" and "optional_linked" in (d.field or "")
            for d in diagnostics
        )


class TestV2IdentityFields:
    """submitting_participant_identity must contain required sub-fields."""

    def test_has_participant_public_display_label(self):
        draft = _echo_draft()
        identity = draft["submitting_participant_identity"]
        assert "participant_public_display_label" in identity

    def test_has_participant_type(self):
        draft = _echo_draft()
        identity = draft["submitting_participant_identity"]
        assert "participant_type" in identity

    def test_has_participant_identifier_disclosure_status(self):
        draft = _echo_draft()
        identity = draft["submitting_participant_identity"]
        assert "participant_identifier_disclosure_status" in identity

    def test_has_participant_identity_disclosure_preference(self):
        draft = _echo_draft()
        identity = draft["submitting_participant_identity"]
        assert "participant_identity_disclosure_preference" in identity

    def test_missing_identity_field_causes_error(self):
        draft = _echo_draft()
        del draft["submitting_participant_identity"]["participant_type"]
        submission = _wrap_submission(draft)
        diagnostics = validate_submission(submission)
        codes = [d.code for d in diagnostics]
        assert "MISSING_IDENTITY_FIELD" in codes
