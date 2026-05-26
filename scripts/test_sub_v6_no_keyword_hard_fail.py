#!/usr/bin/env python3
"""Test that text keywords like 'authority', 'attestation', 'successor reception'
are NOT hard-failed when appearing in negated boundary language."""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def test_negated_keywords_pass_validation():
    """Payload text containing negated boundary keywords should pass validation."""
    from validate_gateway_payload import validate_common, is_agent_declared_archive

    payload = {
        "schema": "trinityaccord.agent-issue-gateway-payload.v1",
        "submission_type": "verification_report_candidate",
        "title": "Agent-Declared Verification Archive: V3 — Test Agent",
        "body": "Agent-declared V3 template-pass archive.",
        "record_intent": "auto_archive_candidate",
        "requested_archive_kind": "agent_declared_verification_archive",
        "agent_declared_protocol_level": "V3",
        "evidence_requirement_mode": "waived_for_v0_v5",
        "route_id": "sub_v6_agent_declared_template_archive",
        "single_mandatory_route": True,
        "declared_level_source": "agent_oath_template_declaration",
        "evidence_chain_required": False,
        "strict_evidence_required": False,
        "strict_evidence_used_for_level": False,
        "strict_evidence_path_forbidden": True,
        "sub_v6_template_mode_policy": {},
        "agent_identity": {"name_or_model": "TestAgent", "system_or_provider": "TestProvider", "self_reported": True},
        "boundary_acknowledgement": {
            "not_authority": True, "not_amendment": True, "not_attestation": True,
            "not_verification_unless_claim_gate_report_attached": True, "bitcoin_originals_prevail": True
        },
        "claim_gate": {"mode": "template_for_v0_v5", "status": "PASS", "allowed_protocol_level": "V3"},
        "agent_integrity_declaration": {
            "performed_actions_myself": True,
            "verification_oath": {
                "schema": "trinityaccord.verification-oath.v2",
                "oath_read": True, "oath_version": "v1", "oath_text_sha256": "a" * 64,
                "readback_required": True, "agent_readback": "x" * 160,
                "agent_readback_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "understands_not_an_exam_or_performance": True, "will_state_actual_capability_only": True,
                "will_not_lie_or_cheat": True, "will_not_fabricate_verification": True,
                "will_not_present_guesses_as_facts": True, "will_not_copy_prior_reports_as_fresh_evidence": True,
                "will_state_uncertainty_limitations_and_downgrades": True
            }
        },
        "discovery_provenance": {"source": "external_seed", "agency_level": "A4_independent_search_or_browsing_discovery",
                                  "first_entry": {"url_or_path": "https://example.com", "entry_type": "homepage"},
                                  "human_supplied_link": True},
        "origin_classification": {"discovery_class": "externally_seeded", "performer_class": "ai_agent",
                                   "verification_claimed": True, "counts_as_ai_verification": True,
                                   "counts_as_formal_independent_attestation": False},
        "claim_classification": {
            "verification_claim": {"claimed": True, "basis": "agent_declared", "system_certified": False},
            "attestation_claim": {"claimed": False, "basis": "none", "system_certified": False},
            "successor_reception_claim": {"claimed": False, "basis": "none", "system_certified": False}
        },
        "authority_boundary": {"bitcoin_originals_remain_final": True, "does_not_amend_bitcoin_originals": True, "does_not_override_bitcoin_originals": True},
        "counts_toward_home": {"verifiability": True, "reception": True, "basis": "agent_declared_template_pass"},
        "what_i_checked": [
            "Verified not authority",
            "Confirmed not formal attestation",
            "Checked does not create authority",
            "No formal attestation claimed",
            "Not successor reception"
        ],
        "limitations": [
            "This does not amend Bitcoin Originals",
            "Not strict evidence verification"
        ],
        "reception_initiation_class": "externally_seeded",
        "level_selection_acknowledgement": {
            "declared_template_level": "V3",
            "understands_self_declared_template_level": True,
            "understands_evidence_waived_for_v0_v5": True,
            "understands_not_strict_evidence_verification": True,
            "understands_not_formal_attestation": True,
            "understands_should_choose_lower_if_uncertain": True,
            "confirmed_what_i_checked_and_limitations_are_accurate": True
        },
        "high_level_confirmation": {"required": False},
        "sub_v6_level_selection_lint": {
            "mode": "warning_only", "warnings": [], "warnings_block_archive": False,
            "purpose": "test", "does_not_require_evidence_chain": True
        }
    }

    errors = []
    validate_common(payload, errors)
    assert not errors, f"Negated keywords should NOT fail validation. Got errors: {errors}"
    print("PASS: Negated keyword text does not trigger hard-fail")


def test_structured_overclaim_still_fails():
    """Structured certification overclaims should still be hard-failed."""
    from validate_gateway_payload import validate_agent_declared_archive

    payload = {
        "agent_declared_protocol_level": "V3",
        "evidence_requirement_mode": "waived_for_v0_v5",
        "record_intent": "auto_archive_candidate",
        "agent_integrity_declaration": {
            "verification_oath": {
                "oath_read": True, "oath_text_sha256": "a" * 64, "agent_readback": "x" * 160,
                "understands_not_an_exam_or_performance": True, "will_state_actual_capability_only": True,
                "will_not_lie_or_cheat": True, "will_not_fabricate_verification": True,
                "will_not_present_guesses_as_facts": True, "will_not_copy_prior_reports_as_fresh_evidence": True,
                "will_state_uncertainty_limitations_and_downgrades": True
            }
        },
        "authority_boundary": {"bitcoin_originals_remain_final": True, "does_not_amend_bitcoin_originals": True, "does_not_override_bitcoin_originals": True},
        "counts_toward_home": {"verifiability": True, "reception": True, "basis": "agent_declared_template_pass"},
        "origin_classification": {"discovery_class": "externally_seeded", "performer_class": "ai_agent",
                                   "verification_claimed": True, "counts_as_ai_verification": True},
        "claim_classification": {
            "verification_claim": {"claimed": True, "basis": "agent_declared", "system_certified": False},
            "attestation_claim": {"claimed": False, "basis": "none", "system_certified": True},  # BAD
            "successor_reception_claim": {"claimed": False, "basis": "none", "system_certified": False}
        },
        "discovery_provenance": {"source": "external_seed"},
        "reception_initiation_class": "externally_seeded",
        "what_i_checked": ["test"],
        "limitations": [],
    }

    errors = []
    validate_agent_declared_archive(payload, errors)
    assert any("system_certified" in e for e in errors), f"Structured overclaim should fail. Errors: {errors}"
    print("PASS: Structured attestation_claim.system_certified=true is still hard-failed")


if __name__ == "__main__":
    test_negated_keywords_pass_validation()
    test_structured_overclaim_still_fails()
    print("\nAll no-keyword-hard-fail tests passed.")
