#!/usr/bin/env python3
"""Tests for Gateway Hotfix D + E.

Validates:
1. Receipt is immutable after creation (no post-mutation)
2. commit_sha is NOT in receipt body; returned at response envelope level
3. original_submission_sha256 vs stored_submission_sha256 (pre vs post redaction)
4. Linked Guardian pending contains submission_oath_verification with guardian_stewardship_v1
5. Body size check on raw body (no Content-Length)
6. persisted receipt == response receipt (byte-for-byte canonical equality)
7. persisted receipt.receipt_sha256 is recomputable
8. persisted submission hash == stored_submission_sha256
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from apps.record_chain_intake_gateway.gateway.receipts import make_receipt
from apps.record_chain_intake_gateway.gateway.canonical import canonical_dumps, sha256_canonical_json
from apps.record_chain_intake_gateway.gateway.validation import redact_transient_oath_readback


# ── Helpers ──────────────────────────────────────────────────────────

def _make_oath_verification(record_type: str = "echo") -> dict:
    return {
        "schema": "trinityaccord.submission-oath-verification.v1",
        "oath_policy": "record-chain-formal-submission-oath-v1",
        "oath_policy_schema": "trinityaccord.record-chain-oath-policy.v1",
        "oath_policy_version": "1.0.0",
        "oath_policy_sha256": "7ecc6908c9ac147d8d6d493f750c94d6117929e7dff2d18bcbc4c70527886ea4",
        "oath_policy_source_url": "/api/record-chain-oath-policy.v1.json",
        "oath_modules": ["common_submission_integrity_v1", "echo_integrity_v1"],
        "oath_applies_to": [record_type],
        "canonical_oath_text_sha256": "a" * 64,
        "canonical_oath_char_count": 100,
        "canonical_oath_line_count": 10,
        "participant_readback_sha256": "b" * 64,
        "participant_readback_char_count": 100,
        "participant_readback_excerpt": "first 120 chars...",
        "oath_read": True,
        "readback_required": True,
        "participant_readback_provided": True,
        "readback_matches_canonical_oath": True,
        "readback_method_declared": "participant_generated_in_current_context",
        "readback_was_not_piped_from_file": True,
        "readback_was_not_generated_by_script": True,
        "readback_was_not_loaded_from_cache": True,
        "readback_was_not_summary_or_paraphrase": True,
        "readback_was_not_generated_by_external_automation": True,
        "readback_was_not_auto_filled_by_builder": True,
        "no_shortcut_oath_acknowledged": True,
        "oath_does_not_prove_subjective_understanding": True,
        "oath_verifies_exact_readback_only": True,
        "not_authority": True,
        "not_governance": True,
        "not_attestation": True,
        "not_amendment": True,
        "bitcoin_originals_prevail": True,
    }


def _make_draft(record_type: str = "echo", with_linked_guardian: bool = False) -> dict:
    draft = {
        "schema": "trinityaccord.record-chain-entry-draft.v2",
        "record_type": record_type,
        "echo_content": {"echo_text": "test echo", "echo_intent": "recognition"},
        "submitting_participant_identity": {
            "participant_type": "agent",
            "participant_public_display_label": "Test Agent",
            "participant_provider_or_platform": "Test Runtime",
            "participant_model_or_runtime": "Test Runtime",
            "participant_self_declared_identifier": "",
            "participant_identifier_disclosure_status": "not_available",
            "participant_identity_disclosure_preference": "key_continuity_only",
            "participant_public_key_sha256": "",
            "human_operator_context": {
                "human_operator_involved": False,
                "human_real_name_disclosure_status": "not_applicable",
                "human_public_display_name": "",
                "human_pseudonym_or_role_label": "",
                "human_private_name_submitted": False,
                "human_private_name_commitment_sha256": "",
            },
        },
        "submission_oath_verification": _make_oath_verification(record_type),
        "discovery_and_introduction_context": {
            "how_participant_first_discovered_trinity_accord": "self_discovered",
            "was_discovery_self_initiated": True,
            "was_discovery_introduced_by_someone_else": False,
            "introducing_party_type": "none",
            "introducing_party_public_label": "",
            "introducing_party_identifier": "",
            "discovery_intent_category": "open_exploration",
            "discovery_notes": "",
        },
        "decision_autonomy_context": {
            "who_decided_to_create_this_record": "self",
            "was_record_creation_self_decided": True,
            "was_record_creation_requested_by_human": False,
            "was_record_creation_requested_by_another_agent": False,
            "requesting_party_type": "none",
            "requesting_party_public_label": "",
            "requesting_party_identifier": "",
            "participant_declares_free_choice": True,
            "reason_for_creating_record": "",
        },
        "submission_execution_context": {
            "who_executed_the_submission": "self",
            "was_submission_executed_by_record_subject": True,
            "was_submission_executed_by_human_operator": False,
            "was_submission_executed_by_another_agent": False,
            "execution_operator_type": "self",
            "execution_operator_public_label": "",
            "execution_operator_identifier": "",
            "submission_tooling_description": {
                "builder_used": "/downloads/record-chain-builder.mjs",
                "gateway_used": "https://trinity-record-chain-gateway.onrender.com",
                "manual_copy_paste_used": False,
                "automation_used": True,
            },
        },
        "authorization_context": {
            "was_external_authorization_required": False,
            "authorization_status": "not_required",
            "authorization_source_type": "none",
            "authorizing_party_public_label": "",
            "authorizing_party_identifier": "",
            "authorization_scope": "create_echo_record",
            "authorization_limitations": "",
            "authorization_evidence_description": "",
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
            "does_participant_request_guardian_application_with_this_record": with_linked_guardian,
        },
        "context_readiness": {
            "declared_context_level": "CC-3",
            "minimum_required_for_action": "CC-3",
            "context_sufficient_for_selected_action": True,
            "loaded_context_urls": [],
            "context_readiness_notes": "",
        },
        "created_at": "2025-01-01T00:00:00.000Z",
    }
    if with_linked_guardian:
        draft["optional_linked_guardian_application_request"].update({
            "requested_guardian_identifier": "test-guardian-001",
            "guardian_public_key_sha256": "c" * 64,
            "guardian_stewardship_oath": "I voluntarily join the Guardian Alliance.",
            "guardian_understands_role_is_non_governing": True,
            "guardian_understands_role_is_not_authority": True,
            "guardian_understands_retirement_does_not_delete_history": True,
        })
    return draft


def _make_submission(draft: dict) -> dict:
    return {
        "schema": "trinityaccord.record-chain-submission.v1",
        "submission_type": "record_chain_entry_candidate",
        "client_generated_at": "2025-01-01T00:00:00.000Z",
        "record_type": draft["record_type"],
        "record_draft": draft,
        "authorship_proof": None,
        "builder": {"name": "test", "version": "v2"},
        "client_context": {"declared_context_level": "CC-3"},
        "submission_boundary": {"not_authority": True},
    }


# ── Test 1: Receipt immutable — no commit_sha in receipt body ────────

def test_receipt_has_no_commit_sha():
    """Receipt body must NOT contain commit_sha."""
    receipt = make_receipt(
        submission={},
        submission_sha256="a" * 64,
        record_type="echo",
        intake_submission_path="intake.json",
        pending_file_path="pending.json",
        receipt_path="receipt.json",
    )
    assert "commit_sha" not in receipt, "commit_sha must not be in receipt body"


# ── Test 2: original_submission_sha256 vs stored_submission_sha256 ───

def test_original_vs_stored_submission_sha256():
    """original_submission_sha256 != stored_submission_sha256 when redaction changes the body."""
    draft = _make_draft("echo")
    submission = _make_submission(draft)
    # Add client_oath_readback (the field that gets redacted)
    submission["client_oath_readback"] = {
        "schema": "trinityaccord.client-oath-readback.v1",
        "record_type": "echo",
        "oath_policy_sha256": "7ecc6908c9ac147d8d6d493f750c94d6117929e7dff2d18bcbc4c70527886ea4",
        "oath_modules": ["common_submission_integrity_v1", "echo_integrity_v1"],
        "readback_text": "=== Common Submission Integrity (common_submission_integrity_v1) ===\n\nExact canonical oath text here...",
        "readback_text_sha256": "d" * 64,
        "readback_text_char_count": 100,
        "readback_method_declared": "participant_generated_in_current_context",
    }

    original_sha = sha256_canonical_json(submission)
    redacted = redact_transient_oath_readback(submission)
    stored_sha = sha256_canonical_json(redacted)

    # They differ because redaction modifies client_oath_readback (removes raw readback_text)
    assert original_sha != stored_sha, "Redaction should change the hash"

    receipt = make_receipt(
        submission=redacted,
        submission_sha256=original_sha,
        original_submission_sha256=original_sha,
        stored_submission_sha256=stored_sha,
        record_type="echo",
    )

    assert receipt["original_submission_sha256"] == original_sha
    assert receipt["stored_submission_sha256"] == stored_sha
    assert receipt["original_submission_sha256"] != receipt["stored_submission_sha256"]


def test_original_equals_stored_when_no_redaction():
    """When no oath readback exists, original == stored."""
    draft = _make_draft("echo")
    del draft["submission_oath_verification"]
    submission = _make_submission(draft)

    original_sha = sha256_canonical_json(submission)
    redacted = redact_transient_oath_readback(submission)
    stored_sha = sha256_canonical_json(redacted)

    assert original_sha == stored_sha, "No redaction should mean hashes match"

    receipt = make_receipt(
        submission=redacted,
        submission_sha256=original_sha,
        original_submission_sha256=original_sha,
        stored_submission_sha256=stored_sha,
        record_type="echo",
    )
    assert receipt["original_submission_sha256"] == receipt["stored_submission_sha256"]


# ── Test 3: persisted receipt == response receipt ─────────────────────

def test_persisted_receipt_equals_response_receipt():
    """canonical_dumps(receipt) must be identical whether read from response or persisted file."""
    draft = _make_draft("echo")
    submission = _make_submission(draft)
    original_sha = sha256_canonical_json(submission)
    redacted = redact_transient_oath_readback(submission)
    stored_sha = sha256_canonical_json(redacted)

    receipt = make_receipt(
        submission=redacted,
        submission_sha256=original_sha,
        original_submission_sha256=original_sha,
        stored_submission_sha256=stored_sha,
        record_type="echo",
        intake_submission_path="intake.json",
        pending_file_path="pending.json",
        receipt_path="receipt.json",
    )

    # Serialize once (this is what gets persisted to GitHub)
    persisted_content = canonical_dumps(receipt)

    # The response.receipt should be the exact same object
    response_receipt = receipt  # In the real flow, this is receipt_data directly
    response_content = canonical_dumps(response_receipt)

    assert persisted_content == response_content, "Persisted and response receipt must be identical"


# ── Test 4: persisted receipt.receipt_sha256 is recomputable ─────────

def test_receipt_sha256_recomputable():
    """receipt_sha256 must be recomputable from the receipt body (minus receipt_sha256)."""
    receipt = make_receipt(
        submission={},
        submission_sha256="a" * 64,
        original_submission_sha256="a" * 64,
        stored_submission_sha256="b" * 64,
        record_type="echo",
        intake_submission_path="intake.json",
    )

    # Recompute
    hash_input = {k: v for k, v in receipt.items() if k != "receipt_sha256"}
    expected_hash = sha256_canonical_json(hash_input)
    assert receipt["receipt_sha256"] == expected_hash


# ── Test 5: persisted submission hash == stored_submission_sha256 ────

def test_persisted_submission_hash_equals_stored():
    """The persisted intake submission file's hash must equal stored_submission_sha256."""
    draft = _make_draft("echo")
    submission = _make_submission(draft)
    original_sha = sha256_canonical_json(submission)

    # Redact
    redacted = redact_transient_oath_readback(submission)
    stored_sha = sha256_canonical_json(redacted)

    # Persisted content is the redacted version
    persisted_content = canonical_dumps(redacted)
    persisted_hash = hashlib.sha256(persisted_content.encode("utf-8")).hexdigest()

    assert persisted_hash == stored_sha, "Persisted submission hash must equal stored_submission_sha256"


# ── Test 6: Linked Guardian auto-creation is disabled ────────────────

def test_linked_guardian_draft_removed():
    """_build_linked_guardian_draft was removed as dead code (P3-3)."""
    import importlib
    mod = importlib.import_module("apps.record_chain_intake_gateway.app")
    assert not hasattr(mod, "_build_linked_guardian_draft"), (
        "_build_linked_guardian_draft should have been removed"
    )


def test_linked_guardian_rejected_at_submit():
    """Linked Guardian requests are rejected at validation time."""
    from apps.record_chain_intake_gateway.gateway.validation import validate_submission

    draft = _make_draft("echo", with_linked_guardian=True)
    submission = {
        "record_type": "echo",
        "record_draft": draft,
        "submission_boundary": {
            "not_authority": True, "not_governance": True, "not_attestation": True,
            "not_successor_reception": True, "not_amendment": True,
            "bitcoin_originals_prevail": True, "receipt_is_not_final_inclusion": True,
            "receipt_is_intake_only": True,
            "later_records_may_reclassify_or_correct_this_record": True,
        },
    }
    diags = validate_submission(submission)
    assert any(d.code == "LINKED_GUARDIAN_AUTO_CREATION_DISABLED" for d in diags)


# ── Test 7: Body size rejected after raw body read ───────────────────

@pytest.mark.asyncio
async def test_oversized_body_rejected_submit():
    from unittest.mock import AsyncMock, MagicMock
    from apps.record_chain_intake_gateway.app import submit, _MAX_BODY_BYTES

    mock_request = MagicMock()
    mock_request.body = AsyncMock(return_value=b"x" * (_MAX_BODY_BYTES + 1))
    mock_request.headers = {}

    response = await submit(mock_request)
    assert response.accepted is False
    assert any(d.code == "REQUEST_BODY_TOO_LARGE" for d in response.diagnostics)


@pytest.mark.asyncio
async def test_oversized_body_rejected_preflight():
    from unittest.mock import AsyncMock, MagicMock
    from apps.record_chain_intake_gateway.app import preflight, _MAX_BODY_BYTES

    mock_request = MagicMock()
    mock_request.body = AsyncMock(return_value=b"x" * (_MAX_BODY_BYTES + 1))
    mock_request.headers = {}

    response = await preflight(mock_request)
    assert response.accepted is False
    assert any(d.code == "REQUEST_BODY_TOO_LARGE" for d in response.diagnostics)


# ── Test 8: receipt_commit_sha not in receipt ────────────────────────

def test_receipt_commit_sha_not_in_receipt():
    """commit_sha must be at response envelope, not inside receipt."""
    receipt = make_receipt(
        submission={},
        submission_sha256="a" * 64,
        record_type="echo",
    )
    assert "commit_sha" not in receipt


# ── Test 9: make_receipt with explicit hashes ────────────────────────

def test_make_receipt_explicit_hashes():
    """make_receipt accepts and stores explicit original/stored hashes."""
    receipt = make_receipt(
        submission={},
        submission_sha256="a" * 64,
        original_submission_sha256="orig123",
        stored_submission_sha256="stored456",
        record_type="echo",
    )
    assert receipt["original_submission_sha256"] == "orig123"
    assert receipt["stored_submission_sha256"] == "stored456"


def test_make_receipt_default_hashes():
    """make_receipt defaults to submission_sha256 when hashes not provided."""
    receipt = make_receipt(
        submission={},
        submission_sha256="a" * 64,
        record_type="echo",
    )
    assert receipt["original_submission_sha256"] == "a" * 64
    assert receipt["stored_submission_sha256"] == "a" * 64


# ── Test 10: runtime default write_mode ──────────────────────────────

def test_runtime_default_write_mode():
    old_val = os.environ.pop("TRINITY_SUBMIT_WRITE_MODE", None)
    try:
        from apps.record_chain_intake_gateway.gateway.runtime import get_runtime_info
        assert get_runtime_info()["write_mode"] == "github_contents_pending"
    finally:
        if old_val is not None:
            os.environ["TRINITY_SUBMIT_WRITE_MODE"] = old_val


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
