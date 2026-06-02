"""Shared fixtures for record-chain intake gateway tests."""
from __future__ import annotations

import copy
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Minimal valid v2 echo submission
# ---------------------------------------------------------------------------

def _make_v2_echo_draft() -> dict[str, Any]:
    """Build a minimal valid v2 echo record_draft."""
    return {
        "record_type": "echo",
        "schema": "trinityaccord.record-chain-entry.v1",
        "chain_id": "trinity-accord-public-reception-ledger",
        "created_at": "2026-06-01T00:00:00Z",
        "actor_identity": {
            "actor_type": "ai_agent",
            "display_label": "Test Agent",
        },
        "submitting_participant_identity": {
            "participant_public_display_label": "Test Agent",
            "participant_type": "ai_agent",
            "participant_identifier_disclosure_status": "not_disclosed",
            "participant_identity_disclosure_preference": "pseudonym_only",
        },
        "discovery_and_introduction_context": {
            "discovery_method": "direct_url",
            "is_autonomous_discovery": False,
        },
        "decision_autonomy_context": {
            "autonomy_level": "agent_initiated",
            "operator_type": "ai_agent",
        },
        "submission_execution_context": {
            "builder_tool": "test-builder",
            "submitted_via": "gateway-api",
        },
        "authorization_context": {
            "authorization_basis": "self_initiated",
        },
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
        "optional_linked_guardian_application_request": None,
        "payload": {
            "title": "Test Echo",
            "body": "This is a test echo submission.",
            "echo_intent": "recognition",
        },
        "authorship_proof": {
            "method": "ed25519",
            "public_key_pem": "-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VwAyEAtest\n-----END PUBLIC KEY-----",
            "public_key_sha256": "abc123def456",
            "signed_payload_sha256": "deadbeef01234567",
            "signature_base64": "dGVzdHNpZ25hdHVyZQ==",
            "claim_boundary": {
                "not_authority": True,
                "not_governance": True,
            },
        },
    }


def _make_valid_submission() -> dict[str, Any]:
    """Build a full valid submission envelope."""
    return {
        "record_type": "echo",
        "record_draft": _make_v2_echo_draft(),
        "boundary_acknowledgement": {
            "not_authority": True,
            "not_governance": True,
            "not_attestation": True,
            "not_successor_reception": True,
            "not_amendment": True,
            "bitcoin_originals_prevail": True,
        },
    }


def _make_signed_submission() -> dict[str, Any]:
    """Build a full submission with authorship_proof at top level."""
    sub = _make_valid_submission()
    sub["authorship_proof"] = {
        "method": "ed25519",
        "public_key_pem": "-----BEGIN PUBLIC KEY-----\nMCowBQYDK2VwAyEAtest\n-----END PUBLIC KEY-----",
        "public_key_sha256": "abc123def456",
        "signed_payload_sha256": "deadbeef01234567",
        "signature_base64": "dGVzdHNpZ25hdHVyZQ==",
        "claim_boundary": {
            "not_authority": True,
            "not_governance": True,
        },
    }
    return sub


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def valid_echo_submission() -> dict[str, Any]:
    """A valid echo submission (deep-copied per test)."""
    return _make_valid_submission()


@pytest.fixture
def signed_echo_submission() -> dict[str, Any]:
    """A valid signed echo submission (deep-copied per test)."""
    return _make_signed_submission()


@pytest.fixture
def valid_context_insufficient_submission() -> dict[str, Any]:
    """A valid context_insufficient_notice submission."""
    return {
        "record_type": "context_insufficient_notice",
        "record_draft": {
            "record_type": "context_insufficient_notice",
            "schema": "trinityaccord.record-chain-entry.v1",
            "chain_id": "trinity-accord-public-reception-ledger",
            "created_at": "2026-06-01T00:00:00Z",
            "actor_identity": {"actor_type": "ai_agent", "display_label": "Test Agent"},
            "context_readiness": {
                "declared_context_level": 0,
                "minimum_required_for_action": "CC-0",
                "context_sufficient_for_selected_action": False,
            },
        },
        "boundary_acknowledgement": {
            "not_authority": True,
            "not_governance": True,
            "not_attestation": True,
            "not_successor_reception": True,
            "not_amendment": True,
            "bitcoin_originals_prevail": True,
        },
    }


@pytest.fixture
def mock_github():
    """Mock the GitHub adapter so tests don't make real API calls."""
    put_mock = AsyncMock(return_value={"commit": {"sha": "abc123"}})
    sha_mock = AsyncMock(return_value=None)
    text_mock = AsyncMock(return_value="")

    with patch("app.put_file", put_mock), \
         patch("app.get_file_sha", sha_mock), \
         patch("app.get_file_text", text_mock):
        yield {
            "put_file": put_mock,
            "get_file_sha": sha_mock,
            "get_file_text": text_mock,
        }
