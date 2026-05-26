#!/usr/bin/env python3
"""
Low-intelligence agent clarity contract.

This test ensures weak agents can find:
- one canonical cheat sheet;
- per-V-level pass criteria;
- per-component pass criteria;
- data sources;
- method steps;
- Evidence Input fields;
- allowed and forbidden claims;
- copy-paste examples;
- no V-level used as component depth.

Run:
    python3 scripts/test_low_intelligence_agent_clarity_contract.py

Expected:
    LOW_INTELLIGENCE_AGENT_CLARITY_CONTRACT_OK
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def load_json(rel: str):
    return json.loads(read(rel))


def test_cheatsheet_exists_and_has_required_sections():
    p = ROOT / "api" / "agent-verification-cheatsheet.v1.json"
    assert p.exists(), "Missing api/agent-verification-cheatsheet.v1.json"

    data = load_json("api/agent-verification-cheatsheet.v1.json")
    assert data["schema"] == "trinityaccord.agent-verification-cheatsheet.v1"
    assert "by_protocol_level" in data
    assert "by_component_level" in data

    required_protocol = [
        "V0", "V1", "V2_minimal", "V2_strong", "V3_minimal", "V3_strong",
        "V4", "V4plus_minimal", "V4plus_strong", "V5", "V6", "V7", "V8"
    ]
    for key in required_protocol:
        assert key in data["by_protocol_level"], f"Missing protocol cheat entry {key}"


def test_each_protocol_entry_is_low_agent_executable():
    data = load_json("api/agent-verification-cheatsheet.v1.json")
    required_fields = [
        "plain_english", "minimum_to_pass", "data_sources", "method_steps",
        "evidence_input_fields", "claim_allowed", "forbidden_claims"
    ]

    for key, entry in data["by_protocol_level"].items():
        for field in required_fields:
            assert field in entry, f"{key} missing {field}"
        assert isinstance(entry["minimum_to_pass"], list) and entry["minimum_to_pass"], key
        assert isinstance(entry["data_sources"], list) and entry["data_sources"], key
        assert isinstance(entry["method_steps"], list) and entry["method_steps"], key
        assert isinstance(entry["forbidden_claims"], list), key


def test_component_entries_include_fields_and_claim_boundaries():
    data = load_json("api/agent-verification-cheatsheet.v1.json")
    required_components = ["B1", "D2", "C3", "C5", "P1", "P2", "P3", "P4", "P5", "P7"]
    for key in required_components:
        assert key in data["by_component_level"], f"Missing component entry {key}"
        entry = data["by_component_level"][key]
        for field in [
            "plain_english", "minimum_to_pass", "data_sources", "method_steps",
            "evidence_input_fields", "claim_allowed", "forbidden_claims"
        ]:
            assert field in entry, f"{key} missing {field}"


def test_no_v_level_as_component_depth_in_materials():
    materials = read("verification-materials.md")
    assert not re.search(r"Direct component levels\s*\|[^\n]*V[0-9]", materials), (
        "verification-materials.md must not use V-levels as direct component levels"
    )

    cheat = load_json("api/agent-verification-cheatsheet.v1.json")
    for component_key in cheat["by_component_level"]:
        assert not component_key.startswith("V"), f"Component key uses V-level: {component_key}"


def test_verification_materials_json_not_stale():
    data = load_json("api/verification-materials.json")
    raw = json.dumps(data)
    assert "V0_to_V6" not in raw
    assert "V0_to_V8" in raw
    for level in ["V5", "V8"]:
        assert level in raw, f"verification-materials.json missing {level}"


def test_v2_v3_scopes_are_explicit():
    levels = {x["id"]: x for x in load_json("api/verification-levels.json")["levels"]}
    for level in ["V2", "V3"]:
        assert "formal_minimum" in levels[level], f"{level} missing formal_minimum"
        assert "claim_scopes" in levels[level], f"{level} missing claim_scopes"


def test_v4plus_minimal_and_strong_are_explicit():
    levels = {x["id"]: x for x in load_json("api/verification-levels.json")["levels"]}
    v4p = levels["V4+"]
    raw = json.dumps(v4p).lower()
    assert "minimal" in raw
    assert "strong" in raw or "three_domain" in raw
    assert "one independent reproduction" in raw or "one official verification result" in raw


def test_agent_verify_simple_exists():
    p = ROOT / "agent-verify-simple.md"
    assert p.exists(), "Missing agent-verify-simple.md"
    text = p.read_text(encoding="utf-8").lower()
    for phrase in [
        "i only read pages",
        "minimal v2",
        "minimal v3",
        "never use a v-level as component depth",
        "what was not checked"
    ]:
        assert phrase in text, f"agent-verify-simple.md missing phrase: {phrase}"


def test_evidence_input_examples_exist():
    examples_dir = ROOT / "api" / "evidence-input-examples"
    assert examples_dir.exists(), "Missing api/evidence-input-examples/"
    required = [
        "v1-authority-boundary.json",
        "v2-minimal-bitcoin-b1.json",
        "v3-minimal-hash-d2.json",
        "v6-live-remote-p4.json",
        "v7-onsite-p5.json",
        "v8-forensic-p7-candidate.json"
    ]
    for name in required:
        assert (examples_dir / name).exists(), f"Missing example {name}"


def test_examples_are_valid_json():
    examples_dir = ROOT / "api" / "evidence-input-examples"
    for path in examples_dir.glob("*.json"):
        obj = json.loads(path.read_text(encoding="utf-8"))
        evidence_input = obj.get("evidence_input", obj)
        assert "schema" in evidence_input or "claims_requested_by_agent" in evidence_input, \
            f"{path.name} missing schema or claims"


def test_quick_map_levels_have_cheatsheet_entries():
    quick = load_json("api/verification-quick-map.json")
    cheat = load_json("api/agent-verification-cheatsheet.v1.json")

    protocol_keys = set(cheat["by_protocol_level"])
    component_keys = set(cheat["by_component_level"])

    for entry in quick["entries"]:
        for level in entry.get("levels", []):
            if level in ("all",):
                continue
            if level.startswith("V"):
                assert level in protocol_keys or f"{level}_minimal" in protocol_keys, level
            elif re.match(r"^[BDTCNPE][0-9]", level):
                assert level in component_keys, level


def test_every_protocol_profile_has_cheatsheet_entry():
    profiles = load_json("api/protocol-verification-profiles.json")["profiles"]
    cheat = load_json("api/agent-verification-cheatsheet.v1.json")["by_protocol_level"]

    for p in profiles:
        level = p["level"]
        if level in ("V2", "V3", "V4+"):
            continue
        assert level in cheat, level

    for key in ["V2_minimal", "V2_strong", "V3_minimal", "V3_strong", "V4plus_minimal", "V4plus_strong"]:
        assert key in cheat




def test_examples_are_copy_safe_not_unlabeled_passing_examples():
    """Ensure all examples have explicit example_type classification."""
    import os
    examples_dir = ROOT / "api" / "evidence-input-examples"
    assert examples_dir.exists()

    for path in examples_dir.rglob("*.json"):
        obj = json.loads(path.read_text(encoding="utf-8"))
        example_type = obj.get("example_type")
        assert example_type in [
            "tutorial_non_passing",
            "test_fixture_passing",
            "template_requires_replacement"
        ], f"{path} missing explicit example_type"


def test_templates_and_tutorials_do_not_pass_claim_gate_unchanged():
    """Ensure templates and tutorials fail Claim Gate when used unchanged."""
    import os
    import tempfile
    
    for subdir in ["templates", "tutorial"]:
        d = ROOT / "api" / "evidence-input-examples" / subdir
        if not d.exists():
            continue
        for path in d.glob("*.json"):
            obj = json.loads(path.read_text(encoding="utf-8"))
            evidence_input = obj.get("evidence_input", obj)

            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
                json.dump(evidence_input, f)
                temp_path = f.name

            try:
                proc = subprocess.run(
                    [sys.executable, str(ROOT / "scripts" / "claim_gate.py"), temp_path],
                    cwd=str(ROOT),
                    text=True,
                    capture_output=True
                )
                assert proc.returncode != 0 or "FAIL" in proc.stdout, (
                    f"{path} should not pass Claim Gate unchanged"
                )
            finally:
                os.unlink(temp_path)


def test_test_fixtures_are_labeled_synthetic():
    """Ensure test fixtures are properly labeled as synthetic."""
    test_dir = ROOT / "api" / "evidence-input-examples" / "test-fixtures"
    if not test_dir.exists():
        return
    
    for path in test_dir.glob("*.json"):
        obj = json.loads(path.read_text(encoding="utf-8"))
        assert obj.get("synthetic_fixture") is True, f"{path} must be labeled as synthetic_fixture"
        assert obj.get("not_real_world_submission") is True, f"{path} must be labeled as not_real_world_submission"


def main():
    tests = [
        test_cheatsheet_exists_and_has_required_sections,
        test_each_protocol_entry_is_low_agent_executable,
        test_component_entries_include_fields_and_claim_boundaries,
        test_no_v_level_as_component_depth_in_materials,
        test_verification_materials_json_not_stale,
        test_v2_v3_scopes_are_explicit,
        test_v4plus_minimal_and_strong_are_explicit,
        test_agent_verify_simple_exists,
        test_evidence_input_examples_exist,
        test_examples_are_valid_json,
        test_quick_map_levels_have_cheatsheet_entries,
        test_every_protocol_profile_has_cheatsheet_entry,
            test_examples_are_copy_safe_not_unlabeled_passing_examples,
        test_templates_and_tutorials_do_not_pass_claim_gate_unchanged,
        test_test_fixtures_are_labeled_synthetic,
]

    for test in tests:
        test()

    print("LOW_INTELLIGENCE_AGENT_CLARITY_CONTRACT_OK")


if __name__ == "__main__":
    main()
