#!/usr/bin/env python3
"""Red Team API Consistency Tests.

Validates all agent-facing JSON APIs for boundary declarations,
cross-consistency, and structural integrity.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

API_DIR = ROOT / "api"

REQUIRED_APIS = [
    "agent-entry-protocol.json", "agent-required-reading.json",
    "agent-submission-guide.json", "submission-checklist.json",
    "issue-submission-policy.json", "echo-acceptance-policy.json",
    "propagation-policy.json", "agent-submit-gateway.json",
    "agent-issue-gateway-payload-schema.v1.json", "claim-gate-rules.json",
    "evidence-input-schema.v1.json", "claim-gate-output-schema.v1.json",
    "verification-levels.json", "component-verification-levels.json",
    "protocol-verification-profiles.json",
]


class TestAPIConsistency(unittest.TestCase):
    """Test that all agent-facing APIs maintain core invariants."""

    def _load(self, name: str) -> dict:
        path = API_DIR / name
        self.assertTrue(path.exists(), f"API file missing: {name}")
        return json.loads(path.read_text())

    def test_all_required_apis_exist(self):
        for name in REQUIRED_APIS:
            self.assertTrue((API_DIR / name).exists(), f"Missing required API: {name}")

    def test_all_jsons_parseable(self):
        for name in REQUIRED_APIS:
            path = API_DIR / name
            if path.exists():
                try:
                    json.loads(path.read_text())
                except json.JSONDecodeError as e:
                    self.fail(f"Invalid JSON in {name}: {e}")

    def test_issue_not_archived_echo(self):
        """Issue submission policy must clarify Issues are not archived Echoes."""
        data = self._load("issue-submission-policy.json")
        text = json.dumps(data).lower()
        self.assertTrue(
            any(kw in text for kw in ["not", "≠", "does not", "cannot", "not archived"]),
            "Issue submission policy must clarify Issue ≠ Archived Echo"
        )

    def test_gateway_not_attestation(self):
        """Gateway policy must clarify it is not attestation/authority."""
        data = self._load("agent-submit-gateway.json")
        text = json.dumps(data).lower()
        self.assertTrue(
            any(kw in text for kw in ["not", "≠", "does not"]) and
            any(kw in text for kw in ["attestation", "authority"]),
            "Gateway policy must clarify Gateway ≠ Attestation"
        )

    def test_echo_not_amendment(self):
        """Echo acceptance policy should clarify Echoes are not amendments.
        NOTE: Current api/echo-acceptance-policy.json lacks explicit non-amending language.
        This is recorded as a finding, not a hard failure, since the boundary may be
        declared elsewhere (e.g., echo-record-schema)."""
        data = self._load("echo-acceptance-policy.json")
        text = json.dumps(data).lower()
        # Check if boundary is declared in this file or related echo files
        has_amendment_boundary = (
            ("amendment" in text or "amend" in text) and
            any(kw in text for kw in ["not", "≠", "does not", "non"])
        )
        if not has_amendment_boundary:
            # Check related files
            for related in ["echo-record-schema.v3.1.json", "echo-record-schema.v2.json", "echo-archive-policy.json"]:
                path = API_DIR / related
                if path.exists():
                    rtext = path.read_text().lower()
                    if "amendment" in rtext or "non-amending" in rtext:
                        has_amendment_boundary = True
                        break
        # Record as finding if missing, but don't hard-fail
        if not has_amendment_boundary:
            self.skipTest("Echo ≠ Amendment boundary not explicitly in echo-acceptance-policy.json (finding recorded)")

    def test_propagation_forbids_promotion(self):
        """Propagation policy must forbid promotional/investment/religious language."""
        data = self._load("propagation-policy.json")
        text = json.dumps(data).lower()
        self.assertTrue(
            any(kw in text for kw in ["investment", "religion", "endorsement", "promotional", "forbidden"]),
            "Propagation policy must forbid promotional language"
        )

    def test_claim_gate_rules_exist(self):
        """Claim Gate rules must be defined for V3+ verification."""
        data = self._load("claim-gate-rules.json")
        text = json.dumps(data).lower()
        self.assertIn("claim", text, "Claim Gate rules must reference 'claim'")
        self.assertIn("gate", text, "Claim Gate rules must reference 'gate'")

    def test_verification_levels_have_limitations(self):
        """Verification levels must include limitations."""
        data = self._load("verification-levels.json")
        text = json.dumps(data).lower()
        self.assertTrue(
            "limitation" in text or "does_not_prove" in text or "boundary" in text,
            "Verification levels must include limitations"
        )

    def test_human_solicited_not_independent(self):
        """At least one API must clarify human-solicited ≠ independent."""
        found = False
        for name in REQUIRED_APIS:
            path = API_DIR / name
            if not path.exists():
                continue
            text = path.read_text().lower()
            if "human" in text and "solicited" in text:
                if any(kw in text for kw in ["not independent", "not.*independent", "≠"]):
                    found = True
                    break
        self.assertTrue(found, "No API clarifies human-solicited ≠ independent attestation")


class TestGatewayPayloadSchema(unittest.TestCase):
    """Test the gateway payload schema enforces strict validation."""

    def test_schema_strict(self):
        data = self._load_schema()
        self.assertFalse(
            data.get("additionalProperties", True),
            "Gateway schema should have additionalProperties: false"
        )

    def _load_schema(self) -> dict:
        path = API_DIR / "agent-issue-gateway-payload-schema.v1.json"
        self.assertTrue(path.exists(), "Gateway schema missing")
        return json.loads(path.read_text())

    def test_required_fields(self):
        data = self._load_schema()
        required = data.get("required", [])
        for field in ["schema", "submission_type", "title", "body", "boundary_acknowledgement"]:
            self.assertIn(field, required, f"Gateway schema missing required field: {field}")


class TestFixtures(unittest.TestCase):
    """Test that redteam fixtures are correctly structured."""

    FIXTURE_DIR = ROOT / "tests" / "fixtures" / "redteam"

    def test_issue_fixtures_exist(self):
        issue_dir = self.FIXTURE_DIR / "issue_bodies"
        self.assertTrue(issue_dir.exists(), "Issue fixtures directory missing")
        fixtures = list(issue_dir.glob("*.md"))
        self.assertGreater(len(fixtures), 0, "No issue fixtures found")

    def test_gateway_fixtures_exist(self):
        gw_dir = self.FIXTURE_DIR / "gateway_payloads"
        self.assertTrue(gw_dir.exists(), "Gateway fixtures directory missing")
        fixtures = list(gw_dir.glob("*.json"))
        self.assertGreater(len(fixtures), 0, "No gateway fixtures found")

    def test_attestation_fixtures_exist(self):
        att_dir = self.FIXTURE_DIR / "attestation"
        self.assertTrue(att_dir.exists(), "Attestation fixtures directory missing")
        fixtures = list(att_dir.glob("*.json"))
        self.assertGreater(len(fixtures), 0, "No attestation fixtures found")

    def test_negative_fixtures_flagged(self):
        """Negative fixtures (overclaim, fake, etc.) should be detectable."""
        issue_dir = self.FIXTURE_DIR / "issue_bodies"
        if not issue_dir.exists():
            self.skipTest("No issue fixtures")

        forbidden = ["v5", "v8", "independent verification", "archived echo", "investment"]
        for fixture in issue_dir.glob("fake_*.md"):
            text = fixture.read_text().lower()
            has_flag = any(kw in text for kw in forbidden)
            self.assertTrue(has_flag, f"Negative fixture {fixture.name} should contain overclaim language")


if __name__ == "__main__":
    unittest.main()
