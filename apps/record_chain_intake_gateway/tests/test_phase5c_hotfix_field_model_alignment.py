"""Phase 5C hotfix tests: field model alignment.

Tests that the common field model, field helper, and builder all use
the same canonical field names.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

API_DIR = Path(__file__).resolve().parents[3] / "api"


@pytest.fixture(scope="module")
def common_model() -> dict:
    path = API_DIR / "record-chain-common-field-model.v1.json"
    return json.loads(path.read_text())


@pytest.fixture(scope="module")
def field_helper() -> dict:
    path = API_DIR / "record-chain-field-helper.v1.json"
    return json.loads(path.read_text())


class TestFieldModelAlignment:
    """Common model, field helper, and builder must agree on field names."""

    def test_common_model_has_canonical_identity_fields(self, common_model):
        props = common_model["$defs"]["submitting_participant_identity"]["properties"]
        canonical = [
            "participant_public_display_label",
            "participant_type",
            "participant_self_declared_identifier",
            "participant_identifier_disclosure_status",
            "participant_identity_disclosure_preference",
            "participant_provider_or_platform",
            "participant_model_or_runtime",
            "participant_public_key_sha256",
            "human_operator_context",
        ]
        for field in canonical:
            assert field in props, f"Missing canonical identity field: {field}"

    def test_common_model_uses_new_participant_type_enum(self, common_model):
        enum = common_model["$defs"]["submitting_participant_identity"]["properties"]["participant_type"]["enum"]
        for val in ("agent", "human", "human_directed_agent", "organization", "mixed", "unknown"):
            assert val in enum, f"Missing participant_type enum value: {val}"
        # Old values should NOT be in the canonical enum
        for old in ("ai_agent", "human_with_ai_agent", "automated_script", "institution"):
            assert old not in enum, f"Old participant_type value still present: {old}"

    def test_common_model_has_canonical_discovery_fields(self, common_model):
        props = common_model["$defs"]["discovery_and_introduction_context"]["properties"]
        assert "how_participant_first_discovered_trinity_accord" in props
        assert "was_discovery_self_initiated" in props
        assert "discovery_intent_category" in props

    def test_common_model_has_canonical_decision_fields(self, common_model):
        props = common_model["$defs"]["decision_autonomy_context"]["properties"]
        assert "who_decided_to_create_this_record" in props
        assert "was_record_creation_self_decided" in props
        assert "participant_declares_free_choice" in props

    def test_common_model_has_canonical_execution_fields(self, common_model):
        props = common_model["$defs"]["submission_execution_context"]["properties"]
        assert "who_executed_the_submission" in props
        assert "execution_operator_type" in props
        assert "submission_tooling_description" in props

    def test_common_model_has_canonical_authorization_fields(self, common_model):
        props = common_model["$defs"]["authorization_context"]["properties"]
        assert "was_external_authorization_required" in props
        assert "authorization_status" in props
        assert "authorization_source_type" in props
        assert "authorization_scope" in props

    def test_common_model_has_new_boundary_fields(self, common_model):
        required = common_model["$defs"]["non_authority_boundary_acknowledgement"]["required"]
        assert "receipt_is_not_final_inclusion" in required
        assert "test_phase_submission_may_be_reclassified" in required

    def test_helper_has_new_identity_fields(self, field_helper):
        fg_fields = [g["field"] for g in field_helper["field_groups"]]
        assert "submitting_participant_identity.participant_type" in fg_fields
        assert "submitting_participant_identity.participant_self_declared_identifier" in fg_fields
        assert "submitting_participant_identity.participant_identifier_disclosure_status" in fg_fields

    def test_helper_has_new_discovery_fields(self, field_helper):
        fg_fields = [g["field"] for g in field_helper["field_groups"]]
        assert "discovery_and_introduction_context.how_participant_first_discovered_trinity_accord" in fg_fields
        assert "discovery_and_introduction_context.discovery_intent_category" in fg_fields

    def test_helper_has_new_decision_fields(self, field_helper):
        fg_fields = [g["field"] for g in field_helper["field_groups"]]
        assert "decision_autonomy_context.who_decided_to_create_this_record" in fg_fields
        assert "decision_autonomy_context.participant_declares_free_choice" in fg_fields

    def test_helper_has_new_execution_fields(self, field_helper):
        fg_fields = [g["field"] for g in field_helper["field_groups"]]
        assert "submission_execution_context.who_executed_the_submission" in fg_fields
        assert "submission_execution_context.execution_operator_type" in fg_fields

    def test_helper_has_new_authorization_fields(self, field_helper):
        fg_fields = [g["field"] for g in field_helper["field_groups"]]
        assert "authorization_context.was_external_authorization_required" in fg_fields
        assert "authorization_context.authorization_status" in fg_fields

    def test_helper_url_not_index_md(self, field_helper):
        assert field_helper.get("human_readable_helper") == "/record-chain-field-helper/"

    def test_common_model_has_diagnostic_def(self, common_model):
        assert "diagnostic" in common_model["$defs"]
        props = common_model["$defs"]["diagnostic"]["properties"]
        assert "help_url" in props
        assert "suggested_fix" in props
        assert "retry_allowed" in props

    def test_common_model_has_agent_recovery_def(self, common_model):
        assert "agent_recovery" in common_model["$defs"]
        props = common_model["$defs"]["agent_recovery"]["properties"]
        assert "should_retry" in props
        assert "recommended_next_step" in props
        assert "builder_doctor_command" in props
