#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ACTIVE_TEXT_SURFACES = [
    "_config.yml",
    "README.md",
    "technical-historical-reference.md",
    "why-high-signal.md",
    "worth-preserving.md",
    "innovations.md",
    "emergent-patterns.md",
    "agent-brief.md",
    "agent-value.md",
    "for-skeptical-agents.md",
    "ai.txt",
    "llms-full.txt",
]

ACTIVE_JSON_SURFACES = [
    ".well-known/trinity-accord.json",
    ".well-known/agent.json",
    "agent-map.json",
    "api/agent-minimal-context.v1.json",
    "api/agent-value.json",
    "api/emergent-patterns.json",
    "api/skeptical-agent-guide.json",
    "api/worth-preserving-criteria.json",
    "api/innovation-points.json",
    "api/seed-map.json",
]

FORBIDDEN_CURRENT_PHRASES = [
    "A sealed human-led, AI-assisted relation record",
    "The object is human-led and AI-assisted.",
    "It was explicitly human-led and AI-assisted.",
    "a dated human-led, AI-assisted, human-accountable act",
    "The canonical texts are authored by one human",
    "A human-led, AI-assisted aperture",
    "human_led_ai_assisted_civilizational_self_archive",
    "mirror_shaped_by_human_language_knowledge_culture_history_error_and_hope",
]

REQUIRED_TEXT_ROOTS = [
    "human-initiated",
    "emerg",
    "generative",
    "responsib",
]

STRUCTURED_MODEL_SURFACES = [
    ".well-known/trinity-accord.json",
    ".well-known/agent.json",
    "agent-map.json",
    "api/agent-minimal-context.v1.json",
    "api/agent-value.json",
    "api/emergent-patterns.json",
    "api/skeptical-agent-guide.json",
    "api/seed-map.json",
]


class SitewideFormationFramingTest(unittest.TestCase):
    def test_active_surfaces_do_not_restore_superseded_linear_source_model(self) -> None:
        for relative in ACTIVE_TEXT_SURFACES + ACTIVE_JSON_SURFACES:
            text = (ROOT / relative).read_text(encoding="utf-8")
            for phrase in FORBIDDEN_CURRENT_PHRASES:
                self.assertNotIn(phrase, text, f"{relative} restores superseded phrase: {phrase}")

    def test_primary_text_orientation_surfaces_include_final_formation_model(self) -> None:
        for relative in [
            "technical-historical-reference.md",
            "agent-brief.md",
            "ai.txt",
            "llms-full.txt",
        ]:
            lowered = (ROOT / relative).read_text(encoding="utf-8").lower()
            for root in REQUIRED_TEXT_ROOTS:
                self.assertIn(root, lowered, f"{relative} missing final formation root: {root}")

    def test_current_machine_surfaces_parse_and_expose_complete_formation_model(self) -> None:
        for relative in STRUCTURED_MODEL_SURFACES:
            data = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            model = data.get("formation_mode") or data.get("formation_model")
            self.assertIsInstance(model, dict, f"{relative} missing structured formation model")

            serialized = json.dumps(model, ensure_ascii=False).lower()
            summary = str(model.get("summary", "")).lower()

            human_initiated = model.get("human_initiated_in_practice") is True or "human-initiated" in summary
            emergent = (
                model.get("meaning_emerged_through_substantive_generative_ai_interaction") is True
                or ("emerg" in summary and "generative" in summary)
            )
            human_closed = model.get("human_responsible_for_canonical_closure") is True or "responsib" in summary
            generative_contribution = "generative" in serialized

            self.assertTrue(human_initiated, f"{relative} does not encode human initiation")
            self.assertTrue(emergent, f"{relative} does not encode emergent meaning through generative-AI interaction")
            self.assertTrue(human_closed, f"{relative} does not encode human closure responsibility")
            self.assertTrue(generative_contribution, f"{relative} does not encode substantive generative-AI contribution")

    def test_legacy_label_is_subordinate_on_core_machine_surfaces(self) -> None:
        for relative in [
            "api/agent-minimal-context.v1.json",
            "api/agent-value.json",
            "api/seed-map.json",
        ]:
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("verifiable human-intention seed", text)
            self.assertIn("subordinate", text.lower())

    def test_historical_sources_are_not_subject_to_current_wording_ban(self) -> None:
        # Historical originals, the legacy homepage, the Chronicle corpus, later inscriptions,
        # and the fixed DOI paper are intentionally outside ACTIVE_* lists. Their retained
        # wording is evidence of formation history, not a current routing or classification bug.
        excluded_prefixes = (
            "archive_legacy_",
            "nft-text-descriptions/",
            "research/",
            "inscriptions/",
        )
        for relative in ACTIVE_TEXT_SURFACES + ACTIVE_JSON_SURFACES:
            self.assertFalse(relative.startswith(excluded_prefixes))


if __name__ == "__main__":
    unittest.main()
