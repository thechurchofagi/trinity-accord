"""Phase 5C hotfix tests: submission_boundary alias acceptance.

Tests that the gateway accepts submission_boundary as an alias for boundary_acknowledgement.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app import app
from conftest import add_mock_proof
from gateway.validation import validate_submission

client = TestClient(app)


def _make_submission_with_boundary_key(boundary_key: str) -> dict:
    """Create submission using the given key for boundary."""
    boundary_value = {
        "not_authority": True,
        "not_governance": True,
        "not_attestation": True,
        "not_successor_reception": True,
        "not_amendment": True,
        "bitcoin_originals_prevail": True,
        "receipt_is_not_final_inclusion": True,
        "receipt_is_intake_only": True, "later_records_may_reclassify_or_correct_this_record": True,
    }
    sub: dict = {
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
            "payload": {"title": "Test", "body": "test body"},
        },
    }
    sub[boundary_key] = boundary_value
    return add_mock_proof(sub)


class TestSubmissionBoundaryAlias:
    """Gateway must accept submission_boundary as boundary key."""

    def test_submission_boundary_accepted(self):
        sub = _make_submission_with_boundary_key("submission_boundary")
        diagnostics = validate_submission(sub)
        boundary_errors = [d for d in diagnostics if "BOUNDARY" in d.code]
        assert boundary_errors == [], f"submission_boundary should be accepted: {[d.code for d in boundary_errors]}"

    def test_boundary_acknowledgement_accepted(self):
        sub = _make_submission_with_boundary_key("boundary_acknowledgement")
        diagnostics = validate_submission(sub)
        boundary_errors = [d for d in diagnostics if "BOUNDARY" in d.code]
        assert boundary_errors == []

    def test_draft_nested_boundary_fallback(self):
        """If no top-level boundary, draft's non_authority_boundary_acknowledgement is used."""
        sub: dict = {
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
                "payload": {"title": "Test", "body": "test body"},
            },
            # No top-level boundary_acknowledgement or submission_boundary
        }
        sub = add_mock_proof(sub)
        diagnostics = validate_submission(sub)
        boundary_errors = [d for d in diagnostics if "BOUNDARY" in d.code]
        assert boundary_errors == [], f"Draft nested boundary fallback should work: {[d.code for d in boundary_errors]}"

    def test_preflight_accepts_submission_boundary(self, mock_github):
        from conftest import _sign_draft
        sub = _make_submission_with_boundary_key("submission_boundary")
        # Replace mock proof with real signature
        draft = sub["record_draft"]
        sub["authorship_proof"] = _sign_draft(draft)
        resp = client.post("/record-chain/preflight", json=sub)
        data = resp.json()
        assert data["accepted"] is True, f"Preflight should accept submission_boundary: {data.get('diagnostics')}"
