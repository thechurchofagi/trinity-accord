"""Tests for gateway rate limiting (Phase 7A-rate-limit-enforcement).

Tests:
- Per-participant limit (10/hour)
- Global limit (100/hour)
- Correct diagnostic response on limit exceeded
"""
from __future__ import annotations

import time
import unittest
from unittest.mock import patch

from apps.record_chain_intake_gateway.gateway.rate_limit import (
    GLOBAL_LIMIT_PER_HOUR,
    PARTICIPANT_LIMIT_PER_HOUR,
    _extract_participant_key,
    check_rate_limit,
    reset,
)


def _make_submission(label: str = "Test Founding Guardian Applicant", pub_key: str | None = None) -> dict:
    """Create a minimal valid submission dict for rate limit testing."""
    identity: dict = {"participant_public_display_label": label}
    if pub_key:
        identity["public_key"] = pub_key
    return {
        "record_type": "echo",
        "record_draft": {
            "record_type": "echo",
            "submitting_participant_identity": identity,
        },
        "submission_boundary": {},
    }


class TestExtractParticipantKey(unittest.TestCase):
    def test_public_key_priority(self):
        sub = _make_submission(pub_key="abc123")
        self.assertEqual(_extract_participant_key(sub), "pk:abc123")

    def test_label_fallback(self):
        sub = _make_submission(label="Alice")
        self.assertEqual(_extract_participant_key(sub), "label:Alice")

    def test_actor_label_fallback(self):
        sub = {"record_draft": {"actor_identity": {"label": "Bob"}}}
        self.assertEqual(_extract_participant_key(sub), "actor:Bob")

    def test_agent_label_fallback(self):
        sub = {"agent_label": "Charlie"}
        self.assertEqual(_extract_participant_key(sub), "agent:Charlie")

    def test_idempotency_key_fallback(self):
        sub = {"idempotency_key_prefix": "idem-001"}
        self.assertEqual(_extract_participant_key(sub), "idem:idem-001")

    def test_anonymous_fallback(self):
        sub = {"record_draft": {}}
        self.assertEqual(_extract_participant_key(sub), "anonymous")


class TestParticipantRateLimit(unittest.TestCase):
    def setUp(self):
        reset()

    def tearDown(self):
        reset()

    def test_first_10_submits_allowed(self):
        sub = _make_submission(label="Alice")
        for i in range(PARTICIPANT_LIMIT_PER_HOUR):
            result = check_rate_limit(sub)
            self.assertIsNone(result, f"Submit {i+1} should be allowed")

    def test_11th_submit_rejected(self):
        sub = _make_submission(label="Alice")
        for _ in range(PARTICIPANT_LIMIT_PER_HOUR):
            check_rate_limit(sub)
        result = check_rate_limit(sub)
        self.assertIsNotNone(result)
        self.assertEqual(result["diagnostic_code"], "RATE_LIMIT_EXCEEDED")
        self.assertFalse(result["accepted"])
        self.assertEqual(result["rate_limit"]["limit_type"], "participant")
        self.assertEqual(result["rate_limit"]["limit"], PARTICIPANT_LIMIT_PER_HOUR)

    def test_different_participants_independent(self):
        alice = _make_submission(label="Alice")
        bob = _make_submission(label="Bob")
        for _ in range(PARTICIPANT_LIMIT_PER_HOUR):
            check_rate_limit(alice)
        self.assertIsNotNone(check_rate_limit(alice))
        self.assertIsNone(check_rate_limit(bob))

    def test_retry_after_seconds_present(self):
        sub = _make_submission(label="Alice")
        for _ in range(PARTICIPANT_LIMIT_PER_HOUR):
            check_rate_limit(sub)
        result = check_rate_limit(sub)
        self.assertIsNotNone(result)
        self.assertIn("retry_after_seconds", result)
        self.assertGreater(result["retry_after_seconds"], 0)


class TestGlobalRateLimit(unittest.TestCase):
    def setUp(self):
        reset()

    def tearDown(self):
        reset()

    def test_global_limit_reached(self):
        for i in range(GLOBAL_LIMIT_PER_HOUR):
            sub = _make_submission(label=f"participant-{i}")
            result = check_rate_limit(sub)
            self.assertIsNone(result, f"Global submit {i+1} should be allowed")

        sub = _make_submission(label="overflow")
        result = check_rate_limit(sub)
        self.assertIsNotNone(result)
        self.assertEqual(result["diagnostic_code"], "RATE_LIMIT_EXCEEDED")
        self.assertEqual(result["rate_limit"]["limit_type"], "global")

    def test_global_limit_before_participant(self):
        for i in range(GLOBAL_LIMIT_PER_HOUR):
            check_rate_limit(_make_submission(label=f"p-{i}"))

        new = _make_submission(label="new-participant")
        result = check_rate_limit(new)
        self.assertIsNotNone(result)
        self.assertEqual(result["rate_limit"]["limit_type"], "global")


class TestWindowExpiry(unittest.TestCase):
    def setUp(self):
        reset()

    def tearDown(self):
        reset()

    def test_old_entries_expire(self):
        sub = _make_submission(label="Alice")
        for _ in range(PARTICIPANT_LIMIT_PER_HOUR):
            check_rate_limit(sub)
        self.assertIsNotNone(check_rate_limit(sub))

        # Simulate time passing beyond the window
        with patch("apps.record_chain_intake_gateway.gateway.rate_limit.time") as mock_time:
            mock_time.time.return_value = time.time() + 3601
            result = check_rate_limit(sub)
            self.assertIsNone(result)


class TestDiagnosticFormat(unittest.TestCase):
    def setUp(self):
        reset()

    def tearDown(self):
        reset()

    def test_diagnostic_has_required_fields(self):
        sub = _make_submission(label="Alice")
        for _ in range(PARTICIPANT_LIMIT_PER_HOUR):
            check_rate_limit(sub)
        result = check_rate_limit(sub)
        self.assertIsNotNone(result)
        diags = result.get("diagnostics", [])
        self.assertEqual(len(diags), 1)
        diag = diags[0]
        self.assertEqual(diag["code"], "RATE_LIMIT_EXCEEDED")
        self.assertEqual(diag["severity"], "error")
        self.assertTrue(diag["retry_allowed"])


if __name__ == "__main__":
    unittest.main()
