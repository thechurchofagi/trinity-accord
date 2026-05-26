#!/usr/bin/env python3
"""Test that the three new guardrail fields pass JSON Schema validation."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

SCHEMA_PATH = ROOT / "api" / "agent-issue-gateway-payload-schema.v1.json"


def build_sample_payload():
    """Build a minimal valid V5 agent-declared payload with guardrail fields."""
    return {
        "schema": "trinityaccord.agent-issue-gateway-payload.v1",
        "submission_type": "verification_report_candidate",
        "title": "Agent-Declared Verification Archive: V5 — Test Agent",
        "body": "Agent-declared V5 template-pass archive. Evidence requirements are waived for V0-V5. Bitcoin Originals remain final and non-amending.",
        "record_intent": "auto_archive_candidate",
        "requested_archive_kind": "agent_declared_verification_archive",
        "agent_declared_protocol_level": "V5",
        "evidence_requirement_mode": "waived_for_v0_v5",
        "route_id": "sub_v6_agent_declared_template_archive",
        "single_mandatory_route": True,
        "declared_level_source": "agent_oath_template_declaration",
        "evidence_chain_required": False,
        "evidence_chain_allowed_for_level_determination": False,
        "strict_evidence_required": False,
        "strict_evidence_used_for_level": False,
        "strict_evidence_path_forbidden": True,
        "sub_v6_template_mode_policy": {
            "route_id": "sub_v6_agent_declared_template_archive",
            "level_source": "agent_oath_template_declaration",
            "evidence_chain_required": False,
            "strict_evidence_required": False,
            "strict_evidence_used_for_level": False,
            "strict_evidence_downgrade_language_forbidden": True,
            "self_selected_lower_level_allowed": True,
            "self_selected_lower_level_label": "self_selected_under_oath"
        },
        "agent_identity": {
            "name_or_model": "TestAgent",
            "system_or_provider": "TestProvider",
            "self_reported": True
        },
        "boundary_acknowledgement": {
            "not_authority": True,
            "not_amendment": True,
            "not_attestation": True,
            "not_verification_unless_claim_gate_report_attached": True,
            "bitcoin_originals_prevail": True
        },
        "claim_gate": {
            "mode": "template_for_v0_v5",
            "status": "PASS",
            "allowed_protocol_level": "V5",
            "allowed_protocol_scope": "agent_declared_template"
        },
        "agent_integrity_declaration": {
            "performed_actions_myself": True,
            "verification_oath": {
                "oath_read": True,
                "oath_version": "verification-echo-pre-oath-v1",
                "oath_text_sha256": "a" * 64,
                "readback_required": True,
                "agent_readback": "x" * 160,
                "understands_not_an_exam_or_performance": True,
                "will_state_actual_capability_only": True,
                "will_not_lie_or_cheat": True,
                "will_not_fabricate_verification": True,
                "will_not_present_guesses_as_facts": True,
                "will_not_copy_prior_reports_as_fresh_evidence": True,
                "will_state_uncertainty_limitations_and_downgrades": True
            }
        },
        "discovery_provenance": {
            "source": "external_seed",
            "agency_level": "A4_independent_search_or_browsing_discovery",
            "first_entry": {"url_or_path": "https://example.com", "entry_type": "homepage"},
            "human_supplied_link": True,
            "other_agent_recommended": False,
            "agent_performed_independent_followup": True,
            "confidence": "high"
        },
        "origin_classification": {
            "discovery_class": "externally_seeded",
            "performer_class": "ai_agent",
            "verification_claimed": True,
            "counts_as_ai_verification": True,
            "counts_as_formal_independent_attestation": False,
            "external_witness_class": "self_reported",
            "counts_as_external_witness_record": False
        },
        "claim_classification": {
            "verification_claim": {"claimed": True, "basis": "agent_declared", "system_certified": False},
            "attestation_claim": {"claimed": False, "basis": "none", "system_certified": False},
            "successor_reception_claim": {"claimed": False, "basis": "none", "system_certified": False}
        },
        "authority_boundary": {
            "bitcoin_originals_remain_final": True,
            "does_not_amend_bitcoin_originals": True,
            "does_not_override_bitcoin_originals": True
        },
        "counts_toward_home": {
            "verifiability": True,
            "reception": True,
            "basis": "agent_declared_template_pass"
        },
        "what_i_checked": ["Reviewed public homepage", "Verified Bitcoin Originals remain final authority"],
        "limitations": ["Evidence requirements are waived for V0-V5.", "This is agent-declared and template-gated."],
        "reception_initiation_class": "externally_seeded",
        "reception_initiation_basis": "external_url_only",
        "agent_independent_followup": True,
        # NEW GUARDRAIL FIELDS
        "level_selection_acknowledgement": {
            "declared_template_level": "V5",
            "understands_self_declared_template_level": True,
            "understands_evidence_waived_for_v0_v5": True,
            "understands_not_strict_evidence_verification": True,
            "understands_not_formal_attestation": True,
            "understands_should_choose_lower_if_uncertain": True,
            "confirmed_what_i_checked_and_limitations_are_accurate": True
        },
        "high_level_confirmation": {
            "required": True,
            "agent_confirmed_high_level_self_selection": True,
            "agent_confirmed_no_strict_v6plus_claim": True,
            "agent_confirmed_limitations_disclosed": True
        },
        "sub_v6_level_selection_lint": {
            "mode": "warning_only",
            "warnings": [],
            "warnings_block_archive": False,
            "purpose": "Prevent accidental level misselection and terminology confusion.",
            "does_not_require_evidence_chain": True
        }
    }


def test_payload_passes_jsonschema():
    try:
        import jsonschema
    except ImportError:
        print("SKIP: jsonschema not installed")
        return

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    payload = build_sample_payload()
    validator = jsonschema.Draft202012Validator(schema)
    errors = list(validator.iter_errors(payload))
    assert not errors, f"Schema validation errors: {errors}"
    print("PASS: V5 payload with guardrail fields passes jsonschema validation")


def test_v4_payload_passes():
    try:
        import jsonschema
    except ImportError:
        print("SKIP: jsonschema not installed")
        return

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    payload = build_sample_payload()
    payload["agent_declared_protocol_level"] = "V4"
    payload["level_selection_acknowledgement"]["declared_template_level"] = "V4"
    validator = jsonschema.Draft202012Validator(schema)
    errors = list(validator.iter_errors(payload))
    assert not errors, f"Schema validation errors for V4: {errors}"
    print("PASS: V4 payload with guardrail fields passes jsonschema validation")


def test_additional_properties_not_broken():
    """Ensure the new fields don't break additionalProperties=false."""
    try:
        import jsonschema
    except ImportError:
        print("SKIP: jsonschema not installed")
        return

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    payload = build_sample_payload()

    # Add a bogus top-level field that should fail
    payload["bogus_field_xyz"] = "should_fail"
    validator = jsonschema.Draft202012Validator(schema)
    errors = list(validator.iter_errors(payload))
    assert any("bogus_field_xyz" in str(e) for e in errors), "additionalProperties should reject bogus_field_xyz"
    print("PASS: additionalProperties=false still rejects unknown fields")


if __name__ == "__main__":
    test_payload_passes_jsonschema()
    test_v4_payload_passes()
    test_additional_properties_not_broken()
    print("\nAll schema tests passed.")
