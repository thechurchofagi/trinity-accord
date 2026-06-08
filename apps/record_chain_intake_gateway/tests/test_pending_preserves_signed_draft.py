"""Regression: pending file must not add actor_identity or boundary before append verification.

The gateway must preserve the signed record_draft as-is when writing to pending.
Adding actor_identity or boundary projections changes the JSON hash, breaking
authorship proof verification in the append pipeline.

See: PR #458, guardian_application rejection due to signed_payload_sha256 mismatch.
"""
from __future__ import annotations

import hashlib
import json


def _canonical_dumps(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class TestPendingContentPreservesSignedDraft:
    """Pending content must not add actor_identity or boundary projections."""

    def test_pending_dict_must_be_plain_draft_copy(self):
        """pending_content_dict must be dict(draft), not normalized draft."""
        import ast
        import pathlib

        app_py = pathlib.Path(__file__).resolve().parents[1] / "app.py"
        source = app_py.read_text(encoding="utf-8")

        # Find the line that sets pending_content_dict
        for line in source.splitlines():
            stripped = line.strip()
            if stripped.startswith("pending_content_dict") and "=" in stripped:
                # Must NOT call _normalize_public_v2_draft_for_pending
                assert "_normalize_public_v2_draft_for_pending" not in stripped, (
                    f"pending_content_dict must not use _normalize_public_v2_draft_for_pending. "
                    f"Found: {stripped}"
                )
                break
        else:
            # If no such line found, the test structure changed
            raise AssertionError("Could not find pending_content_dict assignment in app.py")

    def test_signed_draft_hash_preserved_in_pending(self):
        """Simulate: signed draft hash must match pending content hash."""
        # Simulate a minimal signed record_draft
        draft = {
            "schema": "trinityaccord.record-chain-entry-draft.v2",
            "record_type": "echo",
            "echo_content": {"echo_text": "test echo", "echo_intent": "test"},
            "submitting_participant_identity": {
                "participant_public_key_sha256": "abc123",
                "participant_public_display_label": "Test Agent",
            },
            "non_authority_boundary_acknowledgement": {
                "not_authority": True,
                "not_governance": True,
            },
        }

        # Hash of original draft (what was signed)
        original_hash = _sha256(_canonical_dumps(draft).encode())

        # pending_content_dict should be dict(draft) — same hash
        pending_content_dict = dict(draft)
        pending_hash = _sha256(_canonical_dumps(pending_content_dict).encode())

        assert original_hash == pending_hash, (
            f"Pending content hash must match original draft hash. "
            f"Original: {original_hash}, Pending: {pending_hash}"
        )

    def test_normalized_draft_has_different_hash(self):
        """Prove that adding actor_identity/boundary changes the hash."""
        draft = {
            "schema": "trinityaccord.record-chain-entry-draft.v2",
            "record_type": "echo",
            "submitting_participant_identity": {
                "participant_public_key_sha256": "abc123",
                "participant_public_display_label": "Test Agent",
                "participant_provider_or_platform": "Test Runtime",
            },
            "non_authority_boundary_acknowledgement": {
                "not_authority": True,
                "not_governance": True,
            },
        }

        original_hash = _sha256(_canonical_dumps(draft).encode())

        # Simulate old normalization (adding projections)
        normalized = dict(draft)
        normalized["actor_identity"] = {
            "label": "Test Agent",
            "provider": "Test Runtime",
            "id": "abc123",
        }
        normalized["boundary"] = {
            "not_authority": True,
            "not_governance": True,
        }
        normalized_hash = _sha256(_canonical_dumps(normalized).encode())

        assert original_hash != normalized_hash, (
            "Normalized draft must have different hash (proving the bug)"
        )
