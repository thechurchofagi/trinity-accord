"""Shared fixtures for Record-Chain Intake Gateway tests."""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

# Ensure the gateway package is importable
_GATEWAY_DIR = os.path.join(os.path.dirname(__file__), "..")
if _GATEWAY_DIR not in sys.path:
    sys.path.insert(0, _GATEWAY_DIR)

# Set env vars before importing app
os.environ["TRINITY_REPO_FULL_NAME"] = "test/repo"
os.environ["TRINITY_TARGET_BRANCH"] = "main"
os.environ["TRINITY_GITHUB_TOKEN"] = "ghp_test_fake_token_1234567890abcdef"
os.environ["TRINITY_SUBMIT_WRITE_MODE"] = "github_contents_pending"


@pytest.fixture
def mock_github():
    """Mock GitHub adapter functions. Returns dict of mocks."""
    import app as app_module
    with patch.object(app_module, "put_file", new_callable=AsyncMock) as mock_put, \
         patch.object(app_module, "get_file_sha", new_callable=AsyncMock, return_value=None) as mock_sha, \
         patch.object(app_module, "get_file_text", new_callable=AsyncMock, return_value=None) as mock_text:
        mock_put.return_value = {"commit": {"sha": "abc123"}, "content": {"sha": "def456"}}
        yield {
            "put_file": mock_put,
            "get_file_sha": mock_sha,
            "get_file_text": mock_text,
        }


BOUNDARY_ACK = {
    "not_authority": True,
    "not_governance": True,
    "not_attestation": True,
    "not_successor_reception": True,
    "not_amendment": True,
    "bitcoin_originals_prevail": True,
}


@pytest.fixture
def valid_echo_submission() -> dict[str, Any]:
    """A minimal valid echo submission."""
    return {
        "schema": "trinityaccord.record-chain-submission.v1",
        "submission_type": "record_chain_entry_candidate",
        "client_generated_at": "2026-06-01T00:00:00Z",
        "record_type": "echo",
        "record_draft": {
            "record_type": "echo",
            "echo_type": "E1_recognition_echo",
            "title": "Test Echo",
            "body": "Test body",
            "actor_identity": {"label": "Test Agent", "provider": "Test Runtime"},
            "context_readiness": {
                "declared_context_level": 3,
                "minimum_required_for_action": 3,
                "context_sufficient_for_selected_action": True,
            },
            "boundary": BOUNDARY_ACK.copy(),
        },
        "authorship_proof": None,
        "builder": {"name": "test-builder", "version": "v1", "source_url": "https://test.example.com/builder"},
        "client_context": {
            "site_entry_url": "https://www.trinityaccord.org/",
            "loaded_context_urls": [],
            "declared_context_level": "CC-3",
        },
        "submission_boundary": BOUNDARY_ACK.copy(),
        "boundary_acknowledgement": BOUNDARY_ACK.copy(),
    }


@pytest.fixture
def valid_context_insufficient_submission() -> dict[str, Any]:
    """A valid context_insufficient_notice submission (no authorship proof needed)."""
    return {
        "schema": "trinityaccord.record-chain-submission.v1",
        "submission_type": "record_chain_entry_candidate",
        "client_generated_at": "2026-06-01T00:00:00Z",
        "record_type": "context_insufficient_notice",
        "record_draft": {
            "record_type": "context_insufficient_notice",
            "reason": "Insufficient context to proceed.",
            "actor_identity": {"label": "Test Agent", "provider": "Test Runtime"},
            "context_readiness": {
                "declared_context_level": 0,
                "minimum_required_for_action": 0,
                "context_sufficient_for_selected_action": True,
            },
            "boundary": BOUNDARY_ACK.copy(),
        },
        "builder": {"name": "test-builder", "version": "v1", "source_url": "https://test.example.com/builder"},
        "client_context": {
            "site_entry_url": "https://www.trinityaccord.org/",
            "declared_context_level": "CC-0",
        },
        "submission_boundary": BOUNDARY_ACK.copy(),
        "boundary_acknowledgement": BOUNDARY_ACK.copy(),
    }


@pytest.fixture
def ed25519_keypair():
    """Generate an Ed25519 keypair for testing."""
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    pub_pem = public_key.public_bytes(encoding=Encoding.PEM, format=PublicFormat.SubjectPublicKeyInfo).decode()
    return {"private_key": private_key, "public_key": public_key, "pub_pem": pub_pem}


def _make_authorship_proof(draft, private_key, pub_pem, public_key):
    """Create a valid authorship proof for a draft."""
    import base64
    import hashlib
    from copy import deepcopy
    from gateway.canonical import canonical_bytes

    draft_copy = deepcopy(draft)
    draft_copy.pop("authorship_proof", None)
    payload = canonical_bytes(draft_copy)
    payload_sha = hashlib.sha256(payload).hexdigest()
    pub_raw = public_key.public_bytes(encoding=Encoding.Raw, format=PublicFormat.Raw)
    pub_sha = hashlib.sha256(pub_raw).hexdigest()
    sig = private_key.sign(payload)
    return {
        "schema": "trinityaccord.agent-authorship-proof.v1",
        "method": "public_key_signature",
        "algorithm": "ed25519",
        "public_key_pem": pub_pem,
        "public_key_sha256": pub_sha,
        "signed_payload_sha256": payload_sha,
        "signature_base64": base64.b64encode(sig).decode(),
        "signed_message": payload_sha,
        "claim_boundary": {"not authority": True, "not attestation": True, "not amendment": True},
    }


@pytest.fixture
def signed_echo_submission(valid_echo_submission, ed25519_keypair):
    """An echo submission with a valid Ed25519 authorship proof."""
    draft = valid_echo_submission["record_draft"]
    proof = _make_authorship_proof(
        draft, ed25519_keypair["private_key"], ed25519_keypair["pub_pem"], ed25519_keypair["public_key"]
    )
    valid_echo_submission["authorship_proof"] = proof
    valid_echo_submission["record_draft"]["authorship_proof"] = proof
    return valid_echo_submission
