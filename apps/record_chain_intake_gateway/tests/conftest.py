"""Shared fixtures for record-chain intake gateway tests."""
from __future__ import annotations

import base64
import copy
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from gateway.authorship import canonical_bytes, sha256_bytes, strip_authorship_for_signing


# ---------------------------------------------------------------------------
# Real Ed25519 keypair for test fixtures
# ---------------------------------------------------------------------------

_PRIVATE_KEY = Ed25519PrivateKey.generate()
_PUBLIC_KEY = _PRIVATE_KEY.public_key()
_PUBLIC_KEY_PEM = _PUBLIC_KEY.public_bytes(
    encoding=Encoding.PEM, format=PublicFormat.SubjectPublicKeyInfo
).decode("utf-8")
_PUBLIC_KEY_RAW_SHA256 = sha256_bytes(
    _PUBLIC_KEY.public_bytes(encoding=Encoding.Raw, format=PublicFormat.Raw)
)


def _sign_draft(draft: dict[str, Any]) -> dict[str, Any]:
    """Create a real Ed25519 authorship proof for *draft*."""
    draft_for_signing = strip_authorship_for_signing(draft)
    payload = canonical_bytes(draft_for_signing)
    signature = _PRIVATE_KEY.sign(payload)
    return {
        "method": "ed25519",
        "public_key_pem": _PUBLIC_KEY_PEM,
        "public_key_sha256": _PUBLIC_KEY_RAW_SHA256,
        "signed_payload_sha256": sha256_bytes(payload),
        "signature_base64": base64.b64encode(signature).decode("ascii"),
        "claim_boundary": {
            "not authority": True,
            "not attestation": True,
            "not amendment": True,
        },
    }


# ---------------------------------------------------------------------------
# Minimal valid v2 echo draft
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
            "receipt_is_not_final_inclusion": True,
            "test_phase_submission_may_be_reclassified": True,
        },
        "optional_linked_guardian_application_request": None,
        "payload": {
            "title": "Test Echo",
            "body": "This is a test echo submission.",
            "echo_intent": "recognition",
        },
    }


def _make_valid_submission() -> dict[str, Any]:
    """Build a full valid submission envelope with real authorship proof."""
    draft = _make_v2_echo_draft()
    proof = _sign_draft(draft)
    return {
        "record_type": "echo",
        "record_draft": draft,
        "authorship_proof": proof,
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
    }


def _make_signed_submission() -> dict[str, Any]:
    """Build a full signed submission (same as valid for real signatures)."""
    return _make_valid_submission()


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
            "receipt_is_not_final_inclusion": True,
            "test_phase_submission_may_be_reclassified": True,
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


# ---------------------------------------------------------------------------
# Helpers for test files that call validate_submission() directly
# ---------------------------------------------------------------------------

# Minimal mock proof for tests that don't test authorship itself
MOCK_AUTHORSHIP_PROOF = {
    "method": "ed25519",
    "public_key_pem": _PUBLIC_KEY_PEM,
    "public_key_sha256": _PUBLIC_KEY_RAW_SHA256,
    "signed_payload_sha256": "deadbeef",
    "signature_base64": "dGVzdA==",
    "claim_boundary": {
        "not authority": True,
        "not attestation": True,
        "not amendment": True,
    },
}


def add_mock_proof(submission: dict[str, Any]) -> dict[str, Any]:
    """Add a mock authorship_proof to a submission if not already present.

    For tests that don't test authorship validation itself.
    """
    sub = dict(submission)
    if "authorship_proof" not in sub:
        sub["authorship_proof"] = dict(MOCK_AUTHORSHIP_PROOF)
    return sub
