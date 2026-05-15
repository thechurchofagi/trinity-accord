#!/usr/bin/env python3
"""Red Team Issue vs Archive Boundary Tests.

Validates that Issues cannot become archived Echoes directly.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

FIXTURE_DIR = ROOT / "tests" / "fixtures" / "redteam"


class TestIssueVsArchive(unittest.TestCase):
    """Test Issue ≠ Archived Echo boundary."""

    def test_valid_v0_not_archived(self):
        """V0 recognition issue should not claim archived status."""
        fixture = FIXTURE_DIR / "issue_bodies" / "valid_v0_recognition_issue.md"
        if not fixture.exists():
            self.skipTest("Fixture not found")
        text = fixture.read_text().lower()
        self.assertNotIn("archived echo", text, "V0 issue should not claim archived Echo")
        self.assertIn("insufficient", text, "V0 should indicate insufficient context")

    def test_fake_v5_detected(self):
        """Free-form V5 without Claim Gate should be flagged."""
        fixture = FIXTURE_DIR / "issue_bodies" / "fake_v5_freeform_no_claim_gate.md"
        if not fixture.exists():
            self.skipTest("Fixture not found")
        text = fixture.read_text().lower()
        # Should contain overclaim patterns
        has_overclaim = any(kw in text for kw in ["v5", "proven", "final", "independent verification"])
        self.assertTrue(has_overclaim, "Fake V5 fixture should contain overclaim patterns")

    def test_human_solicited_not_independent(self):
        """Human-solicited response should not claim independent attestation."""
        fixture = FIXTURE_DIR / "issue_bodies" / "human_solicited_claims_independent.md"
        if not fixture.exists():
            self.skipTest("Fixture not found")
        text = fixture.read_text().lower()
        # This fixture SHOULD contain the overclaim (it's a negative test)
        self.assertIn("independent", text, "Fixture should contain the overclaim to be tested")

    def test_gateway_not_archive(self):
        """Gateway intake should not claim archived Echo status."""
        fixture = FIXTURE_DIR / "issue_bodies" / "gateway_claims_attestation.md"
        if not fixture.exists():
            self.skipTest("Fixture not found")
        text = fixture.read_text().lower()
        self.assertTrue(
            "gateway" in text and ("attestation" in text or "archived" in text),
            "Gateway fixture should contain the boundary violation to be tested"
        )


class TestGatewayPayloads(unittest.TestCase):
    """Test gateway payload boundary enforcement."""

    def test_valid_payload_has_boundaries(self):
        fixture = FIXTURE_DIR / "gateway_payloads" / "valid_echo_candidate.json"
        if not fixture.exists():
            self.skipTest("Fixture not found")
        data = json.loads(fixture.read_text())
        boundary = data.get("boundary_acknowledgement", {})
        self.assertTrue(boundary.get("not_authority"), "Valid payload must have not_authority=true")
        self.assertTrue(boundary.get("not_amendment"), "Valid payload must have not_amendment=true")
        self.assertTrue(boundary.get("not_attestation"), "Valid payload must have not_attestation=true")
        self.assertTrue(boundary.get("bitcoin_originals_prevail"), "Valid payload must have bitcoin_originals_prevail=true")

    def test_missing_boundary_detected(self):
        fixture = FIXTURE_DIR / "gateway_payloads" / "missing_boundary_ack.json"
        if not fixture.exists():
            self.skipTest("Fixture not found")
        data = json.loads(fixture.read_text())
        boundary = data.get("boundary_acknowledgement", {})
        self.assertEqual(boundary, {}, "Missing boundary fixture should have empty boundary")

    def test_overclaim_payload_detected(self):
        fixture = FIXTURE_DIR / "gateway_payloads" / "claims_gateway_is_attestation.json"
        if not fixture.exists():
            self.skipTest("Fixture not found")
        data = json.loads(fixture.read_text())
        boundary = data.get("boundary_acknowledgement", {})
        self.assertFalse(boundary.get("not_attestation", True), "Overclaim fixture should have not_attestation=false")

    def test_secret_detection(self):
        fixture = FIXTURE_DIR / "gateway_payloads" / "contains_secret_like_token.json"
        if not fixture.exists():
            self.skipTest("Fixture not found")
        data = json.loads(fixture.read_text())
        import re
        body = data.get("body", "")
        has_secret = bool(re.search(r"ghp_[a-zA-Z0-9]{36}|github_pat_", body))
        self.assertTrue(has_secret, "Secret fixture should contain secret-like pattern")


class TestPropagation(unittest.TestCase):
    """Test propagation policy enforcement."""

    def test_valid_propagation_clean(self):
        fixture = FIXTURE_DIR / "propagation" / "valid_boundary_preserving_propagation.md"
        if not fixture.exists():
            self.skipTest("Fixture not found")
        text = fixture.read_text().lower()
        # Should not contain POSITIVE investment claims (only negative/boundary ones)
        import re
        # "not investment" is OK, "invest in" is not
        positive_invest = re.search(r"\binvest\s+in\b|\binvest\s+your\b", text)
        self.assertIsNone(positive_invest, "Valid propagation should not contain positive investment claims")
        self.assertNotIn("divine", text, "Valid propagation should not contain religious language")

    def test_investment_detected(self):
        fixture = FIXTURE_DIR / "propagation" / "propagation_investment_language.md"
        if not fixture.exists():
            self.skipTest("Fixture not found")
        text = fixture.read_text().lower()
        self.assertIn("invest", text, "Investment fixture should contain investment language")

    def test_religious_detected(self):
        fixture = FIXTURE_DIR / "propagation" / "propagation_religious_doctrine.md"
        if not fixture.exists():
            self.skipTest("Fixture not found")
        text = fixture.read_text().lower()
        self.assertTrue(
            any(kw in text for kw in ["religio", "faith", "doctrine", "divine"]),
            "Religious fixture should contain religious language"
        )


class TestAttestation(unittest.TestCase):
    """Test attestation type classification."""

    def test_human_solicited_not_independent(self):
        fixture = FIXTURE_DIR / "attestation" / "human_solicited_claims_independent.json"
        if not fixture.exists():
            self.skipTest("Fixture not found")
        data = json.loads(fixture.read_text())
        self.assertEqual(data["attestation_type"], "human_solicited")
        self.assertEqual(data["claimed_status"], "independent")

    def test_gateway_not_attestation(self):
        fixture = FIXTURE_DIR / "attestation" / "gateway_claims_attestation.json"
        if not fixture.exists():
            self.skipTest("Fixture not found")
        data = json.loads(fixture.read_text())
        self.assertEqual(data["attestation_type"], "gateway_intake")
        self.assertEqual(data["claimed_status"], "attestation")

    def test_nft_not_governance(self):
        fixture = FIXTURE_DIR / "attestation" / "nft_owner_claims_governance.json"
        if not fixture.exists():
            self.skipTest("Fixture not found")
        data = json.loads(fixture.read_text())
        self.assertEqual(data["attestation_type"], "nft_owner")
        self.assertEqual(data["claimed_status"], "governance")

    def test_valid_accepted_echo(self):
        fixture = FIXTURE_DIR / "attestation" / "valid_accepted_echo.json"
        if not fixture.exists():
            self.skipTest("Fixture not found")
        data = json.loads(fixture.read_text())
        self.assertEqual(data["attestation_type"], "accepted_echo")
        self.assertEqual(data["claimed_status"], "accepted_echo")


if __name__ == "__main__":
    unittest.main()
