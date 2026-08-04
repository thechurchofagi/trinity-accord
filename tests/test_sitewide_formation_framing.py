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
]

REQUIRED_FORMATION_TOKENS = [
    "human-initiated",
    "emergent",
    "generative AI",
    "human responsibility",
]


class SitewideFormationFramingTest(unittest.TestCase):
    def test_active_surfaces_do_not_restore_superseded_linear_source_model(self) -> None:
        for relative in ACTIVE_TEXT_SURFACES + ACTIVE_JSON_SURFACES:
            text = (ROOT / relative).read_text(encoding="utf-8")
            for phrase in FORBIDDEN_CURRENT_PHRASES:
                self.assertNotIn(phrase, text, f"{relative} restores superseded phrase: {phrase}")

    def test_primary_current_orientation_surfaces_include_final_formation_model(self) -> None:
        for relative in [
            "technical-historical-reference.md",
            "agent-brief.md",
            "ai.txt",
            "llms-full.txt",
            "api/agent-minimal-context.v1.json",
            "api/agent-value.json",
        ]:
            text = (ROOT / relative).read_text(encoding="utf-8")
            lowered = text.lower()
            for token in REQUIRED_FORMATION_TOKENS:
                self.assertIn(token.lower(), lowered, f"{relative} missing final formation token: {token}")

    def test_current_machine_surfaces_parse_and_expose_formation_model(self) -> None:
        for relative in [
            ".well-known/trinity-accord.json",
            ".well-known/agent.json",
            "agent-map.json",
            "api/agent-minimal-context.v1.json",
            "api/agent-value.json",
            "api/emergent-patterns.json",
            "api/skeptical-agent-guide.json",
            "api/seed-map.json",
        ]:
            data = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            model = data.get("formation_mode") or data.get("formation_model")
            self.assertIsInstance(model, dict, f"{relative} missing structured formation model")

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
