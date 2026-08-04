#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
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
    "agent-declared template route",
    "v6+ uses strict evidence",
    "if the agent cannot create a github issue directly",
)


def load_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def read_text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


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
        self.assertNotIn("/api/agent-submit-gateway.json", load_order)
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

    def test_current_submission_types_are_exact(self) -> None:
        data = load_json("api/submission-types.json")
        actual = {item["record_type"] for item in data["current_types"]}
        self.assertEqual(actual, CURRENT_RECORD_TYPES)
        self.assertEqual(data["status"], "active_current_record_type_guidance")
        historical = set(data["historical_pre_record_chain_kinds"]["kinds"])
        self.assertIn("echo_v3", historical)
        self.assertIn("verification_report_v2", historical)
        self.assertNotIn("echo_v3", actual)
        self.assertNotIn("verification_report_v2", actual)

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

    def test_claim_gate_levels_are_explicitly_compatibility_only(self) -> None:
        data = load_json("api/claim-gate-rules.json")
        boundary = data["current_public_verification_boundary"]
        self.assertIs(boundary["output_is_intermediate_evidence_artifact"], True)
        self.assertIs(boundary["output_is_not_current_public_record_by_itself"], True)
        self.assertEqual(boundary["current_public_record_type"], "verification")
        statuses = {rule["level"]: rule["current_public_status"] for rule in data["protocol_level_rules"]}
        for level in ("V0", "V1", "V2", "V3", "V4", "V5"):
            self.assertEqual(statuses[level], "compatibility_metadata_only")
        for level in ("V4+", "V6", "V7", "V8"):
            self.assertEqual(statuses[level], "historical_only_for_new_work")

    def test_report_builder_is_intermediate_not_public_submission(self) -> None:
        data = load_json("api/report-builder-policy.json")
        self.assertEqual(data["status"], "non_authoritative_strict_evidence_intermediate_policy")
        boundary = data["current_public_record_boundary"]
        self.assertIs(boundary["intermediate_output_only"], True)
        self.assertIs(boundary["must_not_submit_report_directly_as_public_record"], True)
        self.assertEqual(boundary["current_public_record_type"], "verification")
        self.assertEqual(data["historical_output_compatibility"]["status"], "historical_internal_only")

    def test_field_helper_does_not_present_v6_plus_as_current(self) -> None:
        data = load_json("api/record-chain-field-helper.v1.json")
        serialized = json.dumps(data, ensure_ascii=False).lower()
        self.assertNotIn("v6+ requires strict evidence", serialized)
        self.assertNotIn("v6+ require evidence", serialized)
        self.assertNotIn("downgrade your verification level to v5", serialized)
        self.assertIn("historical-only labels for new work", serialized)
        self.assertIn("compatibility metadata only", serialized)
        self.assertRegex(
            data["updated_at"],
            re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"),
        )

    def test_agent_safety_boundary_uses_current_public_intake(self) -> None:
        data = load_json("api/agent-safety-boundary.json")
        self.assertEqual(data["status"], "active_current_agent_safety_boundary")
        current = data["current_public_record_chain_submission"]
        self.assertIn("/record-chain/preflight", current["preflight"])
        self.assertIn("/record-chain/submit", current["submit"])
        self.assertIs(current["direct_github_issue_is_not_current_public_intake"], True)
        self.assertIs(current["receipt_is_intake_only"], True)
        self.assertIs(data["verification_boundary"]["ordinary_echo_does_not_require_claim_gate"], True)

    def test_agent_submission_guide_is_current(self) -> None:
        data = load_json("api/agent-submission-guide.json")
        self.assertEqual(data["status"], "active_current_agent_guidance")
        self.assertEqual(set(data["current_record_types"]), CURRENT_RECORD_TYPES)
        current = json.dumps(data["required_sequence"], ensure_ascii=False).lower()
        self.assertIn("/record-chain/preflight", current)
        self.assertIn("/record-chain/submit", current)
        self.assertIn("receipt", current)
        retired = [item.lower() for item in data["retired_for_new_public_submissions"]]
        self.assertIn("direct github issue submission", retired)
        self.assertIn("/agent-submit", retired)

    def test_issue_and_echo_acceptance_policies_use_record_chain(self) -> None:
        issue = load_json("api/issue-submission-policy.json")
        self.assertEqual(issue["status"], "active_current_issue_boundary")
        self.assertIs(issue["github_issue_boundary"]["direct_issue_is_current_public_intake"], False)
        self.assertIs(issue["github_issue_boundary"]["issue_body_is_not_archived_echo"], True)
        self.assertIn("/record-chain/preflight", issue["current_public_submission"]["preflight"])

        echo = load_json("api/echo-acceptance-policy.json")
        self.assertEqual(echo["status"], "active_current_record_chain_echo_policy")
        states = {item["state"] for item in echo["states"]}
        self.assertIn("intake_receipt_issued", states)
        self.assertIn("record_chain_appended", states)
        self.assertIn("echo_index_visible", states)
        self.assertIs(echo["echo_verification_boundary"]["verification_is_separate_record_type"], True)

    def test_title_policy_does_not_restore_issue_intake(self) -> None:
        data = load_json("api/submission-title-policy.json")
        current = data["current_policy"]
        self.assertIs(current["github_issue_title_required_for_public_submission"], False)
        self.assertIs(current["issue_title_determines_record_type"], False)
        self.assertEqual(data["historical_issue_title_conventions"]["status"], "historical_archive_only")

    def test_current_human_guidance_does_not_teach_retired_flow(self) -> None:
        identity = read_text("agent-identity.md")
        self.assertIn("/record-chain/preflight", identity)
        self.assertIn("/record-chain/submit", identity)
        self.assertNotIn("Gateway API (`/agent-submit`) is the only valid path", identity)

        echo_submit = read_text("echoes/submit.md")
        self.assertIn("Claim Gate is required only", echo_submit)
        self.assertIn("## Issue ≠ Archived Echo", echo_submit)
        self.assertNotIn("For V6+ strict technical Verification Reports", echo_submit)

        verification = read_text("verification-reports/README.md")
        self.assertIn("Record-Chain record type `verification`", verification)
        self.assertNotIn('"record_kind": "verification_report_v2"', verification)
        self.assertIn("historical-only labels", verification)


if __name__ == "__main__":
    unittest.main()
