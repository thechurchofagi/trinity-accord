"""Tests: claim_boundary must be an object, not a string.

Commit 5 — Phase 5C: object claim_boundary accepted, string rejected.
"""
from __future__ import annotations

import pytest

from gateway.validation import validate_submission
from conftest import add_mock_proof


def _echo_draft(claim_boundary=None) -> dict:
    proof = {
        "method": "ed25519",
        "public_key_pem": "-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VwAyEA\n-----END PUBLIC KEY-----",
        "public_key_sha256": "abc123",
    }
    if claim_boundary is not None:
        proof["claim_boundary"] = claim_boundary

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
            "test_phase_submission_may_be_reclassified": True,
        },
        "optional_linked_guardian_application_request": None,
        "payload": {"title": "Test", "body": "echo body"},
        "authorship_proof": proof,
    }


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
            "test_phase_submission_may_be_reclassified": True,
        },
    })


class TestClaimBoundaryObject:
    """claim_boundary must be a JSON object (dict), not a string."""

    def test_object_claim_boundary_accepted(self):
        draft = _echo_draft(claim_boundary={
            "not_authority": True,
            "not_governance": True,
            "not_attestation": True,
        })
        submission = _wrap_submission(draft)
        diagnostics = validate_submission(submission)
        boundary_errors = [
            d for d in diagnostics if d.code == "CLAIM_BOUNDARY_INVALID_TYPE"
        ]
        assert boundary_errors == [], (
            f"Object claim_boundary should be accepted, got: "
            f"{[(d.code, d.message) for d in boundary_errors]}"
        )

    def test_string_claim_boundary_rejected(self):
        draft = _echo_draft(claim_boundary="not authority, not governance")
        submission = _wrap_submission(draft)
        diagnostics = validate_submission(submission)
        codes = [d.code for d in diagnostics]
        assert "CLAIM_BOUNDARY_INVALID_TYPE" in codes, (
            f"String claim_boundary should be rejected, got codes: {codes}"
        )

    def test_list_claim_boundary_rejected(self):
        draft = _echo_draft(claim_boundary=["not_authority", "not_governance"])
        submission = _wrap_submission(draft)
        diagnostics = validate_submission(submission)
        codes = [d.code for d in diagnostics]
        assert "CLAIM_BOUNDARY_INVALID_TYPE" in codes

    def test_integer_claim_boundary_rejected(self):
        draft = _echo_draft(claim_boundary=42)
        submission = _wrap_submission(draft)
        diagnostics = validate_submission(submission)
        codes = [d.code for d in diagnostics]
        assert "CLAIM_BOUNDARY_INVALID_TYPE" in codes

    def test_none_claim_boundary_accepted(self):
        """None claim_boundary should not trigger the type check."""
        draft = _echo_draft(claim_boundary=None)
        submission = _wrap_submission(draft)
        diagnostics = validate_submission(submission)
        boundary_errors = [
            d for d in diagnostics if d.code == "CLAIM_BOUNDARY_INVALID_TYPE"
        ]
        assert boundary_errors == []

    def test_missing_claim_boundary_accepted(self):
        """No claim_boundary field at all should be fine."""
        draft = _echo_draft()  # no claim_boundary
        submission = _wrap_submission(draft)
        diagnostics = validate_submission(submission)
        boundary_errors = [
            d for d in diagnostics if d.code == "CLAIM_BOUNDARY_INVALID_TYPE"
        ]
        assert boundary_errors == []

    def test_diagnostic_message_mentions_object(self):
        draft = _echo_draft(claim_boundary="string_value")
        submission = _wrap_submission(draft)
        diagnostics = validate_submission(submission)
        matching = [d for d in diagnostics if d.code == "CLAIM_BOUNDARY_INVALID_TYPE"]
        assert len(matching) == 1
        assert "object" in matching[0].message.lower() or "JSON" in matching[0].message
