"""Shared fixtures for record-chain intake gateway tests."""
from __future__ import annotations

import base64
import copy
import os
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
    """Create a current Record-Chain Ed25519 authorship proof for *draft*.

    This must match gateway.authorship.verify_authorship_proof_submission().
    """
    draft_for_signing = strip_authorship_for_signing(draft)
    payload = canonical_bytes(draft_for_signing)
    payload_sha256 = sha256_bytes(payload)
    signature = _PRIVATE_KEY.sign(payload)

    return {
        "schema": "trinityaccord.agent-authorship-proof.v1",
        "method": "public_key_signature",
        "algorithm": "ed25519",
        "public_key_pem": _PUBLIC_KEY_PEM,
        "public_key_sha256": _PUBLIC_KEY_RAW_SHA256,
        "signed_payload_sha256": payload_sha256,
        "signed_message": payload_sha256,
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
    """Build a minimal valid v2 echo record_draft matching current validation contract."""
    return {
        "record_type": "echo",
        "schema": "trinityaccord.record-chain-entry.v1",
        "created_at": "2026-06-01T00:00:00Z",
        "submitting_participant_identity": {
            "participant_public_display_label": "Test Agent",
            "participant_type": "ai_agent",
            "participant_identifier_disclosure_status": "not_disclosed",
            "participant_identity_disclosure_preference": "pseudonym_only",
            "participant_public_key_sha256": _PUBLIC_KEY_RAW_SHA256,
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
            "builder_tool": "test-current-fixture",
            "submitted_via": "record-chain-intake-gateway",
        },
        "authorization_context": {
            "authorization_basis": "self_initiated",
            "authorization_scope": "create_echo_record",
        },
        "context_readiness": {
            "declared_context_level": "CC-3",
            "minimum_required_for_action": "CC-3",
            "context_sufficient_for_selected_action": True,
            "loaded_context_urls": [
                "https://www.trinityaccord.org/agent-start/",
                "https://www.trinityaccord.org/api/record-chain-intake-gateway.v1.json",
            ],
        },
        "non_authority_boundary_acknowledgement": {
            "not_authority": True,
            "not_governance": True,
            "not_attestation": True,
            "not_successor_reception": True,
            "not_amendment": True,
            "bitcoin_originals_prevail": True,
            "receipt_is_not_final_inclusion": True,
            "receipt_is_intake_only": True,
            "later_records_may_reclassify_or_correct_this_record": True,
        },
        "echo_content": {
            "echo_text": "This is a test echo submission.",
            "echo_intent": "recognition",
        },
    }


def _make_valid_submission() -> dict[str, Any]:
    """Build a full valid submission envelope with real authorship proof and oath gate."""
    draft = _make_v2_echo_draft()

    # Build oath verification from the actual oath policy file
    readback_text, oath_verification = _build_oath_for_record_type("echo", draft)
    draft["submission_oath_verification"] = oath_verification

    # Sign AFTER adding oath verification (signature covers the full draft)
    proof = _sign_draft(draft)

    return {
        "schema": "trinityaccord.record-chain-submission.v1",
        "submission_type": "record_chain_entry_candidate",
        "client_generated_at": "2026-06-01T00:00:00Z",
        "record_type": "echo",
        "record_draft": draft,
        "builder": {
            "name": "test-current-fixture",
            "version": "test",
            "source_url": "tests/conftest.py",
        },
        "client_context": {
            "site_entry_url": "https://www.trinityaccord.org/agent-start/",
            "declared_context_level": "CC-3",
            "loaded_context_urls": [
                "https://www.trinityaccord.org/agent-start/",
                "https://www.trinityaccord.org/api/record-chain-intake-gateway.v1.json",
            ],
        },
        "submission_boundary": {
            "not_authority": True,
            "not_governance": True,
            "not_attestation": True,
            "not_successor_reception": True,
            "not_amendment": True,
            "bitcoin_originals_prevail": True,
            "receipt_is_not_final_inclusion": True,
            "receipt_is_intake_only": True,
            "later_records_may_reclassify_or_correct_this_record": True,
        },
        "authorship_proof": proof,
        "client_oath_readback": {
            "readback_text": readback_text,
        },
    }


def _build_oath_for_record_type(record_type: str, draft: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Build canonical oath text and verification dict from the oath policy file."""
    import hashlib
    import json
    import unicodedata
    from pathlib import Path

    from gateway.security import normalize_oath_text, sha256_text

    root = Path(__file__).resolve().parents[3]
    policy_path = root / "api" / "record-chain-oath-policy.v1.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))

    policy_json = json.dumps(policy, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    policy_sha256 = hashlib.sha256(policy_json.encode("utf-8")).hexdigest()

    modules = list(policy.get("record_type_modules", {}).get(record_type, []))
    linked = draft.get("optional_linked_guardian_application_request")
    if isinstance(linked, dict) and linked.get("does_participant_request_guardian_application_with_this_record") is True:
        if "guardian_stewardship_v1" not in modules:
            modules.append("guardian_stewardship_v1")

    module_defs = policy.get("modules", {})
    canonical_parts = []
    for module_id in modules:
        module = module_defs[module_id]
        text = unicodedata.normalize("NFC", normalize_oath_text(module["text"]))
        canonical_parts.append(f"=== {module['label']} ({module_id}) ===\n\n{text}")

    joiner = policy.get("canonicalization", {}).get("module_joiner", "\n\n---\n\n")
    canonical_text = joiner.join(canonical_parts).strip()
    canonical_hash = hashlib.sha256(canonical_text.encode("utf-8")).hexdigest()
    readback_hash = sha256_text(unicodedata.normalize("NFC", normalize_oath_text(canonical_text)))

    verification = {
        "oath_policy": "/api/record-chain-oath-policy.v1.json",
        "oath_policy_sha256": policy_sha256,
        "oath_modules": modules,
        "canonical_oath_text_sha256": canonical_hash,
        "participant_readback_sha256": readback_hash,
        "readback_method_declared": "participant_generated_in_current_context",
        "readback_matches_canonical_oath": True,
        "oath_read": True,
        "participant_readback_provided": True,
        "readback_was_not_piped_from_file": True,
        "readback_was_not_generated_by_script": True,
        "readback_was_not_loaded_from_cache": True,
        "readback_was_not_summary_or_paraphrase": True,
        "readback_was_not_generated_by_external_automation": True,
        "readback_was_not_auto_filled_by_builder": True,
        "no_shortcut_oath_acknowledged": True,
        "oath_does_not_prove_subjective_understanding": True,
        "oath_verifies_exact_readback_only": True,
    }
    return canonical_text, verification


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
    draft = {
        "record_type": "context_insufficient_notice",
        "schema": "trinityaccord.record-chain-entry.v1",
        "created_at": "2026-06-01T00:00:00Z",
        "submitting_participant_identity": {
            "participant_public_display_label": "Test Agent",
            "participant_type": "ai_agent",
            "participant_identifier_disclosure_status": "not_disclosed",
            "participant_identity_disclosure_preference": "pseudonym_only",
            "participant_public_key_sha256": _PUBLIC_KEY_RAW_SHA256,
        },
        "submission_execution_context": {
            "builder_tool": "test-current-fixture",
            "submitted_via": "record-chain-intake-gateway",
        },
        "context_readiness": {
            "declared_context_level": 0,
            "minimum_required_for_action": "CC-0",
            "context_sufficient_for_selected_action": False,
        },
        "authorization_context": {
            "authorization_basis": "self_initiated",
            "authorization_scope": "create_context_insufficient_notice_record",
        },
        "reason": "Insufficient context loaded for any formal record type.",
    }
    proof = _sign_draft(draft)
    return {
        "schema": "trinityaccord.record-chain-submission.v1",
        "submission_type": "record_chain_entry_candidate",
        "client_generated_at": "2026-06-01T00:00:00Z",
        "record_type": "context_insufficient_notice",
        "record_draft": draft,
        "builder": {
            "name": "test-current-fixture",
            "version": "test",
            "source_url": "tests/conftest.py",
        },
        "client_context": {
            "site_entry_url": "https://www.trinityaccord.org/agent-start/",
            "declared_context_level": "CC-0",
            "loaded_context_urls": [],
        },
        "submission_boundary": {
            "not_authority": True,
            "not_governance": True,
            "not_attestation": True,
            "not_successor_reception": True,
            "not_amendment": True,
            "bitcoin_originals_prevail": True,
            "receipt_is_not_final_inclusion": True,
            "receipt_is_intake_only": True,
            "later_records_may_reclassify_or_correct_this_record": True,
        },
        "authorship_proof": proof,
    }


@pytest.fixture
def mock_github():
    """Mock the GitHub adapter so tests don't make real API calls."""
    put_mock = AsyncMock(return_value={"commit": {"sha": "abc123"}})
    sha_mock = AsyncMock(return_value=None)
    text_mock = AsyncMock(return_value=None)
    dispatch_mock = AsyncMock(return_value=None)
    delete_mock = AsyncMock(return_value={})

    env = {
        "TRINITY_REPO_FULL_NAME": "thechurchofagi/trinity-accord",
        "TRINITY_TARGET_BRANCH": "main",
        "TRINITY_GITHUB_TOKEN": "test-token",
    }

    with patch.dict(os.environ, env), \
         patch("app.put_file", put_mock), \
         patch("app.get_file_sha", sha_mock), \
         patch("app.get_file_text", text_mock), \
         patch("app.dispatch_workflow", dispatch_mock), \
         patch("app.delete_file", delete_mock):
        yield {
            "put_file": put_mock,
            "get_file_sha": sha_mock,
            "get_file_text": text_mock,
            "dispatch_workflow": dispatch_mock,
            "delete_file": delete_mock,
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
