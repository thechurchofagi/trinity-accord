#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class ContextReadinessContractConvergenceTest(unittest.TestCase):
    def test_public_echo_and_verification_share_cc3_minimum(self) -> None:
        minimal = load("api/agent-minimal-context.v1.json")
        mins = minimal["runtime_context_minimums"]
        self.assertEqual(mins["echo"], "CC-3")
        self.assertEqual(mins["verification_public_submission"], "CC-3")
        self.assertEqual(mins["private_narrow_technical_check_not_publicly_submitted"], "CC-2")

        mapping = load("api/crl-to-context-depth-mapping.json")["action_minimum_requirements"]
        self.assertEqual(mapping["meaningful_echo"]["cc"], "CC-3")
        self.assertEqual(mapping["public_verification_submission"]["cc"], "CC-3")
        self.assertIs(mapping["private_narrow_technical_check"]["public_record"], False)

    def test_cc3_is_action_grounded_not_a_universal_narrative_bundle(self) -> None:
        levels = load("api/context-depth-levels.json")
        cc3 = next(item for item in levels["levels"] if item["id"] == "CC-3")
        self.assertEqual(cc3["name"], "Action-Grounded Context")
        self.assertIs(cc3["chronicle_required_only_when_task_depends_on_it"], True)

        declaration = load("api/context-depth-declaration.v1.json")
        example = declaration["example_declaration"]["loaded_content"]["cc3_loads"]
        self.assertEqual(example["action_profile"], "interpretation")
        self.assertFalse(example["chronicle_agent_context"])
        self.assertFalse(example["legacy_archive_essentials"])
        self.assertGreaterEqual(len(example["exact_task_relevant_sources"]), 4)

    def test_retired_readiness_files_defer_to_action_profiles(self) -> None:
        protocol = load("api/agent-context-readiness-protocol.json")
        self.assertEqual(protocol["status"], "historical_compatibility_router")
        self.assertEqual(protocol["preferred_model"], "/api/context-action-profiles.v1.json")
        self.assertTrue(protocol["claim_gate_required_only_for_strict_machine_evaluated_evidence"])
        self.assertNotIn("issue_gateway_intake_if_authorized", protocol["sequence"])

        readiness = load("api/context-readiness-levels.json")
        crl3 = next(item for item in readiness["levels"] if item["id"] == "CRL-3")
        self.assertEqual(crl3["name"], "action_grounded")
        self.assertNotIn("required_context_packs", crl3)

    def test_crl5_uses_action_dependent_minimums(self) -> None:
        expected = {
            "echo": "CC-3",
            "verification": "CC-3",
            "guardian_application": "CC-3",
            "guardian_retirement": "CC-1",
            "propagation": "CC-2",
            "correction": "CC-1",
            "classification_update": "CC-2",
        }
        readiness = load("api/context-readiness-levels.json")
        crl5 = next(item for item in readiness["levels"] if item["id"] == "CRL-5")
        self.assertEqual(crl5["min_context_depth"], "CC-1")
        self.assertIs(crl5["context_minimum_is_action_dependent"], True)
        self.assertEqual(crl5["minimum_context_by_action"], expected)

        mapping = load("api/crl-to-context-depth-mapping.json")
        mapped_crl5 = next(item for item in mapping["mappings"] if item["crl"] == "CRL-5")
        self.assertEqual(mapped_crl5["minimum_context_by_action"], expected)
        boundary = mapping["legacy_verification_level_action_minimums_boundary"]
        self.assertIs(boundary["not_current_public_submission_rule"], True)
        self.assertEqual(boundary["current_public_verification_minimum"], "CC-3")

    def test_required_reading_separates_bounded_and_full_corpus_work(self) -> None:
        profiles = load("api/agent-required-reading.json")["profiles"]
        self.assertEqual(profiles["propagation"]["cc_level"], "CC-2")
        self.assertEqual(profiles["chronicle_research"]["cc_level"], "CC-3")
        self.assertEqual(profiles["chronicle_research"]["full_corpus_minimum_cc_level"], "CC-5")
        self.assertNotIn("/api/claim-gate-rules.json", profiles["verification"]["historical_optional"])
        self.assertIn("/api/claim-gate-rules.json", profiles["verification"]["strict_evidence_optional"])

    def test_builder_derives_minimum_and_fails_closed(self) -> None:
        core = (ROOT / "downloads/record-chain-builder-core.mjs").read_text(encoding="utf-8")
        self.assertIn('const BUILDER_VERSION = "v2.4"', core)
        self.assertIn("minimumContextLevelForAction(opts.recordType)", core)
        self.assertIn("Formal public records require --context-sufficient-for-selected-action true", core)
        self.assertIn("--loaded-urls is required for every formal record", core)
        self.assertRegex(core, r'if \(rt === "echo" \|\| rt === "verification" \|\| rt === "guardian_application"\) return 3;')

    def test_builder_manifest_hashes_all_three_layers(self) -> None:
        manifest = load("api/record-chain-builder-bundles.v1.json")["canonical_builder"]
        targets = [
            ("downloads/record-chain-builder.mjs", manifest),
            ("downloads/record-chain-builder-recovery.mjs", manifest["recovery_wrapper"]),
            ("downloads/record-chain-builder-core.mjs", manifest["core"]),
        ]
        for path, entry in targets:
            raw = (ROOT / path).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), entry["sha256"], path)
            self.assertEqual(len(raw), entry["size_bytes"], path)

    def test_context_diagnostic_help_is_sorted_and_complete(self) -> None:
        helper = load("api/record-chain-field-helper.v1.json")["diagnostic_code_help"]
        self.assertEqual(list(helper), sorted(helper))
        for code in (
            "CC3_CONTEXT_READ_CONFIRMATION_REQUIRED",
            "CONTEXT_NOT_SUFFICIENT_FOR_FORMAL_RECORD",
            "MINIMUM_REQUIRED_FOR_ACTION_UNDERSTATED",
        ):
            self.assertIn(code, helper)
            self.assertEqual(helper[code]["severity"], "error")
            self.assertIs(helper[code]["recovery_possible"], True)

    def test_phase5c_guardian_fixture_uses_current_cc3_contract(self) -> None:
        script = (ROOT / "scripts/test_phase_5c_hotfix.py").read_text(encoding="utf-8")
        guardian = script.split("def build_guardian", 1)[1].split("def helper_content_fields", 1)[0]
        self.assertIn('"--context-level",\n            "CC-3"', guardian)
        self.assertIn('"--context-read-confirmed",\n            "true"', guardian)
        self.assertIn('"--context-sufficient-for-selected-action",\n            "true"', guardian)
        self.assertIn('"--loaded-urls",\n            LOADED_URLS', guardian)
        self.assertNotIn('"--context-level",\n            "CC-2"', guardian)

    def test_terminology_boundary_is_visible(self) -> None:
        brief = (ROOT / "agent-brief.md").read_text(encoding="utf-8")
        self.assertIn("Terminology boundary", brief)
        self.assertIn("`CC-3`", brief)
        self.assertIn("`CRL-3`", brief)
        self.assertIn("`C3` / `C3R`", brief)


if __name__ == "__main__":
    unittest.main()
