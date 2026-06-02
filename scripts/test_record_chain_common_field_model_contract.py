"""Contract test: record-chain-common-field-model.v1.json.

Validates that the common field model JSON is valid and contains all required $defs.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

MODEL_PATH = Path(__file__).resolve().parents[1] / "api" / "record-chain-common-field-model.v1.json"

# All required $defs blocks
REQUIRED_DEFS = {
    "submitting_participant_identity",
    "discovery_and_introduction_context",
    "decision_autonomy_context",
    "submission_execution_context",
    "authorization_context",
    "context_readiness",
    "non_authority_boundary_acknowledgement",
    "authorship_proof",
    "echo_content",
    "verification_content",
    "guardian_application_content",
    "optional_linked_guardian_application_request",
    "diagnostic",
    "agent_recovery",
}


@pytest.fixture(scope="module")
def model() -> dict:
    assert MODEL_PATH.exists(), f"Common field model not found at {MODEL_PATH}"
    data = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "Common field model must be a JSON object"
    return data


class TestCommonFieldModelContract:
    """Validate record-chain-common-field-model.v1.json structure."""

    def test_is_valid_json(self, model):
        """Already proven by loading, but explicit assertion."""
        assert "$schema" in model or "$id" in model or "title" in model

    def test_has_defs_section(self, model):
        assert "$defs" in model, "Common field model must have a $defs section"
        assert isinstance(model["$defs"], dict)

    @pytest.mark.parametrize("def_name", sorted(REQUIRED_DEFS))
    def test_def_exists(self, model, def_name):
        defs = model["$defs"]
        assert def_name in defs, (
            f"Missing $def '{def_name}'. Available: {sorted(defs.keys())}"
        )

    def test_def_count(self, model):
        defs = model["$defs"]
        assert len(defs) >= len(REQUIRED_DEFS), (
            f"Expected at least {len(REQUIRED_DEFS)} $defs, got {len(defs)}"
        )

    def test_each_def_has_properties_or_type(self, model):
        """Each $def should be a valid JSON Schema (have 'type' or 'properties')."""
        defs = model["$defs"]
        for name, schema in defs.items():
            assert isinstance(schema, dict), f"$def '{name}' must be a dict"
            has_type = "type" in schema
            has_properties = "properties" in schema
            has_oneOf = "oneOf" in schema or "anyOf" in schema
            assert has_type or has_properties or has_oneOf, (
                f"$def '{name}' has no 'type', 'properties', or 'oneOf'/'anyOf'"
            )

    def test_submitting_identity_has_properties(self, model):
        schema = model["$defs"]["submitting_participant_identity"]
        props = schema.get("properties", {})
        assert "participant_public_display_label" in props
        assert "participant_type" in props

    def test_boundary_ack_has_boolean_properties(self, model):
        schema = model["$defs"]["non_authority_boundary_acknowledgement"]
        props = schema.get("properties", {})
        for field in ("not_authority", "not_governance", "not_attestation"):
            assert field in props, f"Missing boundary property '{field}'"

    def test_diagnostic_has_code_and_severity(self, model):
        schema = model["$defs"]["diagnostic"]
        props = schema.get("properties", {})
        assert "code" in props
        assert "severity" in props

    def test_schema_id_present(self, model):
        """Should have $id or title for identification."""
        assert "$id" in model or "title" in model, "Model should have $id or title"
