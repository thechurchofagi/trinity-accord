"""Tests: chain normalizer accepts v2 fields.

Commit 5 — Phase 5C: test normalize_record_draft() in scripts/trinity_record_chain.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Add the scripts directory to the path so we can import trinity_record_chain
SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from trinity_record_chain import normalize_record_draft


def _minimal_v2_draft(**overrides) -> dict:
    """Minimal v2 draft that normalize_record_draft should accept."""
    draft = {
        "record_type": "echo",
        "schema": "trinityaccord.record-chain-entry.v1",
        "chain_id": "trinity-accord-public-reception-ledger",
        "created_at": "2026-06-01T00:00:00Z",
        "actor_identity": {"actor_type": "ai_agent", "display_label": "Test Agent"},
        "submitting_participant_identity": {
            "participant_public_display_label": "Echo Agent",
            "participant_type": "ai_agent",
            "participant_self_declared_identifier": "echo-agent-001",
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
        "context_readiness": {
            "declared_context_level": 3,
            "minimum_required_for_action": "CC-3",
            "context_sufficient_for_selected_action": True,
        },
        "authorship_proof": {
            "method": "ed25519",
            "public_key_pem": "-----BEGIN PUBLIC KEY-----\ntest\n-----END PUBLIC KEY-----",
        },
    }
    draft.update(overrides)
    return draft


class TestNormalizeRecordDraftV2:
    """Test that normalize_record_draft handles v2 common blocks."""

    def test_v2_submitting_identity_derives_actor_identity(self):
        """When actor_identity is absent, derive from submitting_participant_identity."""
        draft = _minimal_v2_draft()
        del draft["actor_identity"]
        result = normalize_record_draft(draft)
        assert "actor_identity" in result
        assert result["actor_identity"]["label"] == "Echo Agent"

    def test_v2_submitting_identity_derives_provider(self):
        draft = _minimal_v2_draft()
        del draft["actor_identity"]
        draft["submitting_participant_identity"]["participant_provider_or_platform"] = "OpenAI"
        result = normalize_record_draft(draft)
        assert result["actor_identity"]["provider"] == "OpenAI"

    def test_v2_submitting_identity_derives_id(self):
        draft = _minimal_v2_draft()
        del draft["actor_identity"]
        result = normalize_record_draft(draft)
        assert result["actor_identity"]["id"] == "echo-agent-001"

    def test_v2_boundary_ack_derives_boundary(self):
        """When boundary is absent, derive from non_authority_boundary_acknowledgement."""
        draft = _minimal_v2_draft()
        assert "boundary" not in draft
        result = normalize_record_draft(draft)
        assert "boundary" in result
        assert result["boundary"]["not_authority"] is True
        assert result["boundary"]["not_governance"] is True
        assert result["boundary"]["not_attestation"] is True
        assert result["boundary"]["bitcoin_originals_prevail"] is True

    def test_v2_boundary_partial_false(self):
        """If a boundary field is missing/false in the ack, derived boundary reflects that."""
        draft = _minimal_v2_draft()
        draft["non_authority_boundary_acknowledgement"]["not_authority"] = False
        result = normalize_record_draft(draft)
        assert result["boundary"]["not_authority"] is False
        assert result["boundary"]["not_governance"] is True

    def test_existing_actor_identity_not_overwritten(self):
        """If actor_identity is already set, it should not be overwritten."""
        draft = _minimal_v2_draft()
        draft["actor_identity"] = {"display_label": "Custom Agent"}
        result = normalize_record_draft(draft)
        assert result["actor_identity"]["display_label"] == "Custom Agent"

    def test_existing_boundary_not_overwritten(self):
        draft = _minimal_v2_draft()
        draft["boundary"] = {"custom": True}
        result = normalize_record_draft(draft)
        assert result["boundary"]["custom"] is True


class TestNormalizeRecordDraftErrors:
    """Test that missing required fields still raise errors."""

    def test_missing_record_type_raises(self):
        draft = _minimal_v2_draft()
        del draft["record_type"]
        with pytest.raises(ValueError, match="record_type"):
            normalize_record_draft(draft)

    def test_missing_actor_identity_and_no_v2_fallback_raises(self):
        """Without actor_identity and without submitting_participant_identity, it should raise."""
        draft = _minimal_v2_draft()
        del draft["actor_identity"]
        del draft["submitting_participant_identity"]
        with pytest.raises(ValueError, match="actor_identity"):
            normalize_record_draft(draft)

    def test_missing_context_readiness_raises(self):
        draft = _minimal_v2_draft()
        del draft["context_readiness"]
        with pytest.raises(ValueError, match="context_readiness"):
            normalize_record_draft(draft)
