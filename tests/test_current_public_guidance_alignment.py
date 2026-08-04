#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CURRENT_RECORD_TYPES = {
    "echo",
    "verification",
    "guardian_application",
    "guardian_retirement",
    "propagation",
    "correction",
    "classification_update",
    "context_insufficient_notice",
}

RETIRED_CURRENT_MARKERS = (
    "human-led, ai-assisted",
    "/api/agent-submit-gateway.json",
    "agent-declared template route",
    "v6+ uses strict evidence",
    "if the agent cannot create a github issue directly",
)


def load_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def canonical_digest_16(data: dict) -> str:
    payload = {key: value for key, value in data.items() if key != "source_digest"}
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


class CurrentPublicGuidanceAlignmentTest(unittest.TestCase):
    def test_ai_to_ai_orientation_uses_current_formation_and_routes(self) -> None:
        data = load_json("api/ai-to-ai-orientation.gpt-5.5-thinking.v1.json")
        serialized = json.dumps(data, ensure_ascii=False).lower()
        for marker in RETIRED_CURRENT_MARKERS:
            self.assertNotIn(marker, serialized)

        formation = data["formation_model"]
        self.assertIs(formation["human_initiated_in_practice"], True)
        self.assertIs(formation["meaning_emerged_through_substantive_generative_ai_interaction"], True)
        self.assertIs(formation["human_responsible_for_canonical_closure"], True)

        load_order = data["recommended_agent_load_order"]
        self.assertIn("/api/agent-first-contact.json", load_order)
        self.assertIn("/api/record-chain-intake-gateway.v1.json", load_order)
        self.assertEqual(data["route_guidance"]["ordinary_echo"]["record_type"], "echo")
        self.assertEqual(data["route_guidance"]["verification"]["record_type"], "verification")

    def test_live_canary_discovers_only_current_gateway_surfaces(self) -> None:
        data = load_json("api/live-canary-policy.v1.json")
        discovery = data["gateway_discovery_order"]
        self.assertEqual(discovery[0], "/api/record-chain-intake-gateway.v1.json")
        self.assertIn("/api/agent-first-contact.json", discovery)
        self.assertNotIn("/api/agent-submit-gateway.json", discovery)
        self.assertIn("/api/record-chain-status.json", data["public_readback_candidates"])
        self.assertIn("/record-chain/indexes/record-index.json", data["public_readback_candidates"])
        self.assertEqual(data["source_digest"], canonical_digest_16(data))

    def test_submission_checklist_matches_current_record_chain_route(self) -> None:
        data = load_json("api/submission-checklist.json")
        self.assertEqual(set(data["record_types"]), CURRENT_RECORD_TYPES)
        current = json.dumps(data["checklist"], ensure_ascii=False).lower()
        self.assertIn("/record-chain/preflight", current)
        self.assertIn("/record-chain/submit", current)
        self.assertIn("receipt is intake-only", current)
        self.assertNotIn("echo_v3", current)
        self.assertNotIn("verification_report_v2", current)
        self.assertNotIn("github issue", current)
        self.assertNotIn("/api/agent-submit-gateway.json", current)
        prohibited = [item.lower() for item in data["prohibited_current_paths"]]
        self.assertIn("direct github issue submission", prohibited)
        self.assertIn("/api/agent-submit-gateway.json", prohibited)

    def test_claim_gate_is_scoped_to_strict_evidence_not_all_echoes(self) -> None:
        data = load_json("api/claim-gate-entrypoint-policy.json")
        self.assertEqual(data["status"], "active_current_strict_evidence_policy")
        self.assertIn("ordinary echo records", data["scope"]["not_required_for"])
        self.assertIn("strict machine-evaluated technical evidence claims", data["scope"]["required_for"])
        current = json.dumps(data["current_public_submission"], ensure_ascii=False).lower()
        self.assertIn("/record-chain/preflight", current)
        self.assertIn("/record-chain/submit", current)
        legacy = data["legacy_internal_entrypoints"]
        self.assertEqual(legacy["status"], "historical_internal_only")

    def test_field_helper_does_not_present_v6_plus_as_current(self) -> None:
        data = load_json("api/record-chain-field-helper.v1.json")
        serialized = json.dumps(data, ensure_ascii=False).lower()
        self.assertNotIn("v6+ requires strict evidence", serialized)
        self.assertNotIn("v6+ require evidence", serialized)
        self.assertNotIn("downgrade your verification level to v5", serialized)
        self.assertIn("historical-only labels for new work", serialized)
        self.assertIn("compatibility metadata only", serialized)


if __name__ == "__main__":
    unittest.main()
