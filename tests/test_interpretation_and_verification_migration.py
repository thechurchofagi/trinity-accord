#!/usr/bin/env python3
"""Regression tests for current interpretation and verification models."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str) -> dict:
    file_path = ROOT / path
    assert file_path.exists(), f"missing file: {path}"
    return json.loads(file_path.read_text(encoding="utf-8"))


def test_interpretation_policy_retires_all_fixed_stage_defaults() -> None:
    policy = load_json("api/interpretation-model-policy.v1.json")
    current = policy["current_chronicle_model"]
    assert current["fixed_stage_count"] is None
    assert current["no_current_five_stage_model"] is True
    assert current["no_current_seven_stage_model"] is True
    assert current["navigation_layer"]["not_a_stage_model"] is True
    assert current["descriptive_layer"]["not_periodization"] is True
    assert current["interpretive_layer"]["must_be_labeled_provisional"] is True

    retired = {item["id"]: item for item in policy["retired_models"]}
    assert "former_fixed_seven_stage_narrative" in retired
    assert "any_fixed_five_stage_or_other_fixed_stage_model" in retired


def test_chronicle_context_points_to_current_policy() -> None:
    context = load_json("api/context-packs/nft-chronicle-context.json")
    policy = context["interpretation_policy"]
    assert policy["fixed_seven_stage_taxonomy_retired"] is True
    assert policy["no_current_fixed_stage_model"] is True
    assert policy["fixed_five_stage_taxonomy_not_adopted"] is True
    assert policy["source"] == "/api/interpretation-model-policy.v1.json"

    summary = load_json("nft-text-descriptions/chronicle-summary.json")
    assert summary["interpretation_policy"]["fixed_stage_count"] is None
    assert summary["interpretation_policy"]["source"] == "/api/interpretation-model-policy.v1.json"


def test_context_models_do_not_require_chronicle_for_every_echo() -> None:
    action_profiles = load_json("api/context-action-profiles.v1.json")
    profiles = {item["id"]: item for item in action_profiles["profiles"]}
    interpretation = profiles["interpretation"]
    joined = "\n".join(interpretation["must_load"])
    assert "task-relevant" in joined
    assert "Chronicle materials are required only" in interpretation["optimization_note"]
    assert action_profiles["interpretation_model_policy"] == "/api/interpretation-model-policy.v1.json"

    required = load_json("api/agent-required-reading.json")
    echo = required["profiles"]["echo_submission"]
    assert echo["chronicle_materials_required_only_when_claim_depends_on_chronicle"] is True
    assert echo["preferred_action_profiles"] == ["interpretation", "record_action"]

    legacy = load_json("api/context-depth-levels.json")
    cc3 = next(item for item in legacy["levels"] if item["id"] == "CC-3")
    assert cc3["name"] == "Action-Grounded Context"
    assert cc3["legacy_label"] == "Narrative Grounded"
    assert cc3["chronicle_required_only_when_task_depends_on_it"] is True
    assert "seven-stage" not in cc3["meaning"].lower()


def test_new_verification_model_separates_physical_and_witness_dimensions() -> None:
    model = load_json("api/verification-claim-model.v1.json")
    compatibility = model["legacy_v_compatibility"]
    assert compatibility["new_submission_forbidden_values"] == ["V4+", "V6", "V7", "V8"]
    assert compatibility["retired_mapping"]["V8"] == "physical_observation=forensic_examination"

    profiles = load_json("api/verification-profiles.v1.json")
    assert profiles["current_submission_policy"]["legacy_v_allowed"] == ["V0", "V1", "V2", "V3", "V4", "V5"]
    assert profiles["current_submission_policy"]["legacy_v6_v8_forbidden_for_new_records"] is True

    levels = load_json("api/verification-levels.json")
    assert levels["new_submission_policy"]["allowed_legacy_v_values"] == ["V0", "V1", "V2", "V3", "V4", "V5"]
    assert levels["new_submission_policy"]["forbidden_legacy_v_values"] == ["V4+", "V6", "V7", "V8"]
    for level in levels["levels"]:
        if level["id"] in {"V4+", "V6", "V7", "V8"}:
            assert level["status"] == "historical_compatibility_only"
            assert level["new_submission_allowed"] is False


def test_builder_emits_multidimensional_verification_claim_model() -> None:
    builder = (ROOT / "downloads/record-chain-builder.mjs").read_text(encoding="utf-8")
    required_fragments = [
        'const BUILDER_VERSION = "v2.1"',
        "verification_claim_model",
        "digital_profile",
        "relationships_checked",
        "physical_observation",
        "external_witness",
        "coverage_scope",
        "legacy_v_level_role: \"builder_compatibility_only\"",
        "--digital-profile",
        "--relationships-checked",
        "--physical-observation",
        "--external-witness",
        "--coverage-scope",
    ]
    for fragment in required_fragments:
        assert fragment in builder, f"builder missing {fragment}"


def test_active_guidance_explains_new_and_legacy_fields() -> None:
    guidance = load_json("downloads/record-chain-agent-field-guidance.v1.json")
    verification = guidance["record_types"]["verification"]
    assert verification["public_verification_level_limit"] == "V0-V5 only"
    assert verification["v6_v8_status"] == "historical_compatibility_only"
    required = set(verification["record_specific_required_cli_options"])
    assert {
        "--digital-profile",
        "--relationships-checked",
        "--physical-observation",
        "--external-witness",
        "--coverage-scope",
    }.issubset(required)

    first_contact = load_json("api/agent-first-contact.json")
    assert first_contact["current_interpretation_model"] == "/api/interpretation-model-policy.v1.json"
    assert first_contact["current_verification_claim_model"] == "/api/verification-claim-model.v1.json"


def test_human_migration_guide_exists() -> None:
    text = (ROOT / "INTERPRETATION-AND-VERIFICATION-MIGRATION.md").read_text(encoding="utf-8")
    assert "no current fixed five-stage" in text.lower()
    assert "no current fixed five-stage, seven-stage" in text.lower()
    assert "retired for new submissions" in text.lower()
