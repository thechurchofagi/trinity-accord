"""Contract test: record-chain-field-helper.v1.json.

Validates that the field helper JSON is valid and contains all required sections
and all 22 diagnostic codes.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

HELPER_PATH = Path(__file__).resolve().parents[1] / "api" / "record-chain-field-helper.v1.json"

# Required top-level sections
REQUIRED_SECTIONS = {"field_groups", "record_type_presets", "diagnostic_code_help", "agent_recovery_protocol"}

# All 22 diagnostic codes that must be present
EXPECTED_DIAGNOSTIC_CODES = {
    "CLAIM_BOUNDARY_MUST_BE_OBJECT",
    "CONTEXT_INSUFFICIENT",
    "CONTEXT_LEVEL_RETIRED_USE_CONTEXT_READINESS",
    "ECHO_TYPE_RETIRED",
    "FINAL_CHAIN_FIELD_FORBIDDEN",
    "GUARDIAN_REQUEST_ONLY_ALLOWED_FROM_ECHO_OR_VERIFICATION",
    "HUMAN_PRIVATE_NAME_NOT_ALLOWED",
    "LINKED_GUARDIAN_REQUEST_INCOMPLETE",
    "MISSING_AUTHORIZATION_CONTEXT",
    "MISSING_AUTHORSHIP_PROOF",
    "MISSING_BOUNDARY_ACKNOWLEDGEMENT",
    "MISSING_COMMON_FIELD",
    "MISSING_CONTEXT_READINESS",
    "MISSING_DECISION_AUTONOMY_CONTEXT",
    "MISSING_DISCOVERY_CONTEXT",
    "MISSING_PARTICIPANT_PUBLIC_DISPLAY_LABEL",
    "MISSING_PARTICIPANT_TYPE",
    "MISSING_SUBMISSION_EXECUTION_CONTEXT",
    "PLACEHOLDER_VALUE_DETECTED",
    "PRIVATE_IDENTITY_BLOB_NOT_ALLOWED",
    "PRIVATE_KEY_OR_TOKEN_DETECTED",
    "VERIFICATION_EVIDENCE_REQUIRED_FOR_V6_PLUS",
}


@pytest.fixture(scope="module")
def helper() -> dict:
    assert HELPER_PATH.exists(), f"Field helper not found at {HELPER_PATH}"
    data = json.loads(HELPER_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "Field helper must be a JSON object"
    return data


class TestFieldHelperContract:
    """Validate record-chain-field-helper.v1.json structure."""

    def test_is_valid_json(self, helper):
        assert isinstance(helper, dict)

    @pytest.mark.parametrize("section", sorted(REQUIRED_SECTIONS))
    def test_section_exists(self, helper, section):
        assert section in helper, (
            f"Missing section '{section}'. Available: {sorted(helper.keys())}"
        )

    def test_field_groups_is_list(self, helper):
        fg = helper["field_groups"]
        assert isinstance(fg, list), "field_groups must be a list"

    def test_field_groups_has_entries(self, helper):
        fg = helper["field_groups"]
        assert len(fg) >= 20, f"Expected at least 20 field groups, got {len(fg)}"

    def test_field_group_entries_have_field_key(self, helper):
        fg = helper["field_groups"]
        for i, entry in enumerate(fg):
            assert isinstance(entry, dict), f"field_groups[{i}] must be a dict"
            assert "field" in entry, f"field_groups[{i}] missing 'field' key"

    def test_record_type_presets_is_dict(self, helper):
        rtp = helper["record_type_presets"]
        assert isinstance(rtp, dict), "record_type_presets must be a dict"

    def test_record_type_presets_has_echo(self, helper):
        rtp = helper["record_type_presets"]
        assert "echo" in rtp, "record_type_presets must include 'echo'"

    def test_record_type_presets_has_verification(self, helper):
        rtp = helper["record_type_presets"]
        assert "verification" in rtp

    def test_diagnostic_code_help_is_dict(self, helper):
        dch = helper["diagnostic_code_help"]
        assert isinstance(dch, dict), "diagnostic_code_help must be a dict"

    def test_diagnostic_code_count(self, helper):
        dch = helper["diagnostic_code_help"]
        assert len(dch) == 22, (
            f"Expected 22 diagnostic codes, got {len(dch)}. "
            f"Codes: {sorted(dch.keys())}"
        )

    @pytest.mark.parametrize("code", sorted(EXPECTED_DIAGNOSTIC_CODES))
    def test_diagnostic_code_exists(self, helper, code):
        dch = helper["diagnostic_code_help"]
        assert code in dch, (
            f"Missing diagnostic code '{code}'. Available: {sorted(dch.keys())}"
        )

    def test_diagnostic_entries_have_description(self, helper):
        dch = helper["diagnostic_code_help"]
        for code, entry in dch.items():
            assert isinstance(entry, (dict, str)), (
                f"Diagnostic '{code}' entry must be a dict or string"
            )
            if isinstance(entry, dict):
                # Should have some descriptive field
                has_desc = any(
                    k in entry
                    for k in ("description", "meaning", "message", "help_text", "plain_language_explanation")
                )
                assert has_desc, (
                    f"Diagnostic '{code}' has no description/meaning/message field. "
                    f"Keys: {sorted(entry.keys())}"
                )

    def test_agent_recovery_protocol_is_dict(self, helper):
        arp = helper["agent_recovery_protocol"]
        assert isinstance(arp, dict), "agent_recovery_protocol must be a dict"

    def test_agent_recovery_protocol_has_steps(self, helper):
        arp = helper["agent_recovery_protocol"]
        assert "steps" in arp, "agent_recovery_protocol must have 'steps'"

    def test_agent_recovery_protocol_has_description(self, helper):
        arp = helper["agent_recovery_protocol"]
        assert "description" in arp, "agent_recovery_protocol must have 'description'"
