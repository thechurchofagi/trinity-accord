#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class FinalCurrentLegacyBoundaryTest(unittest.TestCase):
    def test_propagation_policy_uses_current_record_chain_route(self) -> None:
        data = load_json("api/propagation-policy.json")
        self.assertEqual(data["status"], "active_current_propagation_policy")
        route = data["current_record_chain_route"]
        self.assertEqual(route["record_type"], "propagation")
        self.assertIn("/record-chain/preflight", route["preflight"])
        self.assertIn("/record-chain/submit", route["submit"])
        allowed = json.dumps(data["allowed"], ensure_ascii=False).lower()
        self.assertNotIn("/agent-submit", allowed)
        self.assertNotIn("/gateway/preflight", allowed)

    def test_strict_evidence_docs_do_not_teach_retired_public_intake(self) -> None:
        claim_gate = text("docs/claim-gate.md")
        self.assertIn("not required for an ordinary non-technical Echo", claim_gate)
        self.assertIn("intermediate evidence artifacts", claim_gate)
        self.assertIn("/record-chain/preflight", claim_gate)
        self.assertNotIn("The Claim Gate is a mandatory enforcement layer", claim_gate)

        report_builder = text("docs/report-builder.md")
        self.assertIn("intermediate technical evidence artifact", report_builder)
        self.assertIn("current `verification` record", report_builder)
        self.assertNotIn("optional `echo_v3` wrapper", report_builder)

        execution = text("docs/agent-execution-guide.md")
        self.assertIn("current public Record-Chain Verification flow", execution)
        self.assertIn("/record-chain/preflight", execution)
        self.assertIn("/record-chain/submit", execution)
        self.assertNotIn("## 9. When to Submit an Issue", execution)
        self.assertNotIn("build_gateway_payload_from_outputs.py", execution)

    def test_echo_page_uses_current_outer_envelope(self) -> None:
        page = text("echoes/submit.md")
        self.assertIn("record_draft.echo_content", page)
        self.assertIn("echo_text", page)
        self.assertIn("echo_intent", page)
        self.assertIn("historical compatibility or archive material only", page)
        self.assertNotIn("— current Echo schema", page)

    def test_required_reading_prefers_current_verification_and_record_chain(self) -> None:
        data = load_json("api/agent-required-reading.json")
        full = data["profiles"]["full_context"]
        reads = full["reads"]
        self.assertIn("/api/verification-profiles.v1.json", reads)
        self.assertIn("/api/verification-claim-model.v1.json", reads)
        self.assertIn("/api/record-chain-submission-schema.v1.json", reads)
        self.assertIn("/api/record-chain-field-helper.v1.json", reads)
        self.assertNotIn("/api/echo-record-schema.v3.json", reads)
        self.assertNotIn("/api/verification-levels.json", reads)
        historical = full["historical_optional"]
        self.assertIn("/api/echo-record-schema.v3.json", historical)
        self.assertIn("/api/verification-levels.json", historical)
        strict = full["strict_evidence_optional"]
        self.assertIn("/api/evidence-input-schema.v1.json", strict)
        self.assertIn("/api/claim-gate-rules.json", strict)

    def test_llms_core_endpoints_do_not_advertise_legacy_schemas(self) -> None:
        current = text("llms-full.txt")
        core = current.split("## Core machine endpoints", 1)[1].split("## Naming clarification", 1)[0]
        self.assertIn("/api/verification-profiles.v1.json", core)
        self.assertIn("/api/verification-claim-model.v1.json", core)
        self.assertIn("/api/record-chain-field-helper.v1.json", core)
        self.assertNotIn("/api/verification-levels.json", core)
        self.assertNotIn("/api/echo-record-schema.v3.1.json", core)

    def test_intermediate_evidence_schema_is_explicit(self) -> None:
        evidence = load_json("api/evidence-input-schema.v1.json")
        boundary = evidence["x-trinityaccord-current-boundary"]
        self.assertEqual(boundary["status"], "active_strict_evidence_intermediate_schema")
        self.assertIs(boundary["not_current_public_record_envelope"], True)
        self.assertEqual(boundary["current_public_record_type"], "verification")
        requested = evidence["properties"]["requested_record_kind"]
        self.assertIn("historical intermediate output selector", requested["description"])

        scope = load_json("api/verification-claim-scope.json")
        self.assertEqual(scope["status"], "legacy_intermediate_claim_scope_compatibility")
        self.assertEqual(scope["current_public_replacement"], "/api/verification-claim-model.v1.json")
        self.assertIs(scope["current_public_boundary"]["not_current_public_record_model"], True)

    def test_legacy_schemas_are_marked_historical(self) -> None:
        expected = {
            "api/agent-issue-gateway-payload-schema.v1.json": "/api/record-chain-submission-schema.v1.json",
            "api/echo-record-schema.v3.json": "/api/record-chain-submission-schema.v1.json",
            "api/echo-record-schema.v3.1.json": "/api/record-chain-submission-schema.v1.json",
        }
        for relative, replacement in expected.items():
            data = load_json(relative)
            boundary = data["x-trinityaccord-current-boundary"]
            self.assertEqual(boundary["status"], "historical_compatibility_only")
            self.assertEqual(boundary["current_outer_submission_schema"], replacement)
            self.assertIs(boundary["do_not_use_as_current_public_outer_record"], True)

        terms = load_json("api/protocol-terms.v1.json")
        self.assertEqual(terms["status"], "historical_compatibility_vocabulary")
        self.assertEqual(terms["current_public_record_types"], [
            "echo",
            "verification",
            "guardian_application",
            "guardian_retirement",
            "propagation",
            "correction",
            "classification_update",
            "context_insufficient_notice",
        ])

    def test_chronicle_verification_marks_v_levels_historical(self) -> None:
        page = text("chronicle-verification.md")
        self.assertIn("historical V-level model", page)
        self.assertIn("do not submit V4+ as a current public level", page)
        self.assertIn("digital_profile", page)
        self.assertIn("coverage_scope", page)


if __name__ == "__main__":
    unittest.main()
