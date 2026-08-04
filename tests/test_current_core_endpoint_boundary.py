#!/usr/bin/env python3
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CurrentCoreEndpointBoundaryTest(unittest.TestCase):
    def test_full_context_separates_current_historical_and_strict_evidence(self) -> None:
        data = json.loads((ROOT / "api/agent-required-reading.json").read_text(encoding="utf-8"))
        full = data["profiles"]["full_context"]

        self.assertIn("/api/record-chain-submission-schema.v1.json", full["reads"])
        self.assertIn("/api/verification-claim-model.v1.json", full["reads"])
        self.assertIn("/api/evidence-input-schema.v1.json", full["strict_evidence_optional"])
        self.assertIn("/api/echo-record-schema.v3.1.json", full["historical_optional"])

        for legacy in (
            "/api/verification-levels.json",
            "/api/echo-record-schema.v3.json",
            "/api/echo-record-schema.v3.1.json",
        ):
            self.assertNotIn(legacy, full["reads"])

    def test_llms_core_list_uses_current_record_chain_surfaces(self) -> None:
        text = (ROOT / "llms-full.txt").read_text(encoding="utf-8")
        core = text.split("## Core machine endpoints", 1)[1].split("## Naming clarification", 1)[0]
        self.assertIn("/api/record-chain-submission-schema.v1.json", core)
        self.assertIn("/api/record-chain-field-helper.v1.json", core)
        self.assertIn("/api/verification-profiles.v1.json", core)
        self.assertNotIn("/api/echo-record-schema.v3.1.json", core)
        self.assertNotIn("/api/verification-levels.json", core)


if __name__ == "__main__":
    unittest.main()
