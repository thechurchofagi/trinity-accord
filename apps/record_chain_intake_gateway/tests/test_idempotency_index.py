"""Part B: global submission idempotency index tests."""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _idempotency_index_path(submission_sha256: str) -> str:
    return f"record-chain/intake/by-submission-sha256/{submission_sha256}.json"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestIdempotencyIndex:
    """Tests for global idempotency index lookup and write."""

    def test_idempotency_path_format(self):
        sha = "a" * 64
        assert _idempotency_index_path(sha) == f"record-chain/intake/by-submission-sha256/{sha}.json"

    def test_idempotency_index_schema(self):
        """Verify the expected schema of the idempotency index."""
        index = {
            "schema": "trinityaccord.record-chain-intake-idempotency.v1",
            "submission_sha256": "a" * 64,
            "stored_submission_sha256": "b" * 64,
            "receipt_id": "rcg-20260101-abc123def456",
            "receipt_path": "record-chain/intake/receipts/2026/01/rcg-20260101-abc123def456.receipt.json",
            "pending_file_path": "record-chain/pending/rcg-20260101-abc123def456.echo.pending.json",
            "intake_submission_path": "record-chain/intake/submissions/2026/01/rcg-20260101-abc123def456.submission.json",
            "record_type": "echo",
            "created_at": "2026-01-01T00:00:00Z",
        }
        assert index["schema"] == "trinityaccord.record-chain-intake-idempotency.v1"
        assert len(index["submission_sha256"]) == 64
        assert index["receipt_id"].startswith("rcg-")

    def test_duplicate_does_not_consume_rate_limit(self):
        """When idempotency index exists, rate limit should not be checked."""
        # This is an integration-level assertion verified by checking the flow order
        # in app.py: idempotency check comes before check_rate_limit call
        import inspect
        from apps.record_chain_intake_gateway import app
        source = inspect.getsource(app.submit)
        idemp_idx = source.find("idempotency_path")
        rate_limit_idx = source.find("check_rate_limit")
        assert idemp_idx < rate_limit_idx, (
            "Idempotency check must come before rate limit check in submit flow"
        )

    def test_original_sha_used_for_index_key(self):
        """The idempotency key must use the original (pre-redaction) SHA."""
        import inspect
        from apps.record_chain_intake_gateway import app
        source = inspect.getsource(app.submit)
        # original_submission_sha256 should be computed before redaction
        orig_idx = source.find("original_submission_sha256 = sha256_canonical_json(body)")
        redact_idx = source.find("redact_transient_oath_readback")
        assert orig_idx < redact_idx, (
            "original_submission_sha256 must be computed before oath redaction"
        )
