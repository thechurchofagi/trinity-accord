#!/usr/bin/env python3
"""Test that renderer outputs sub_v6_level_selection fields in issue body."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def build_sample_payload():
    """Build a V5 payload with guardrail fields for renderer testing."""
    return {
        "schema": "trinityaccord.agent-issue-gateway-payload.v1",
        "submission_type": "verification_report_candidate",
        "title": "Agent-Declared Verification Archive: V5 — Test Agent",
        "body": "Agent-declared V5 template-pass archive.",
        "record_intent": "auto_archive_candidate",
        "requested_archive_kind": "agent_declared_verification_archive",
        "agent_declared_protocol_level": "V5",
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
        "claim_gate": {"mode": "template_for_v0_v5", "status": "PASS", "allowed_protocol_level": "V5"},
        "agent_integrity_declaration": {
            "performed_actions_myself": True,
            "verification_oath": {
                "oath_read": True, "oath_version": "v1", "oath_text_sha256": "a" * 64,
                "readback_required": True, "agent_readback": "x" * 160,
                "understands_not_an_exam_or_performance": True, "will_state_actual_capability_only": True,
                "will_not_lie_or_cheat": True, "will_not_fabricate_verification": True,
                "will_not_present_guesses_as_facts": True, "will_not_copy_prior_reports_as_fresh_evidence": True,
                "will_state_uncertainty_limitations_and_downgrades": True
            }
        },
        "discovery_provenance": {"source": "external_seed", "agency_level": "A4_independent_search_or_browsing_discovery",
                                  "first_entry": {"url_or_path": "https://example.com", "entry_type": "homepage"}},
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
        "what_i_checked": ["Read public homepage"],
        "limitations": ["Evidence waived for V0-V5."],
        "reception_initiation_class": "externally_seeded",
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
            "warnings": ["Declared high sub-V6 template level but what_i_checked does not mention script review/run."],
            "warnings_block_archive": False,
            "purpose": "Prevent accidental level misselection.",
            "does_not_require_evidence_chain": True
        }
    }


def test_renderer_outputs_level_selection():
    """Test that the renderer includes sub_v6_level_selection fields."""
    # We need to import the renderer functions
    from render_gateway_issue_body import render_machine_block, render_sub_v6_template_route

    payload = build_sample_payload()

    # Test render_machine_block
    block = render_machine_block(payload)

    assert "sub_v6_level_selection:" in block, "Missing sub_v6_level_selection block"
    assert "declared_template_level: V5" in block, "Missing declared_template_level"
    assert "evidence_waived_for_v0_v5: true" in block, "Missing evidence_waived_for_v0_v5"
    assert "strict_evidence_level_claimed: false" in block, "Missing strict_evidence_level_claimed"
    assert "warnings_are_non_blocking: true" in block, "Missing warnings_are_non_blocking"
    assert "warning_count: 1" in block, "Missing warning_count"
    assert "sub_v6_level_selection_warnings:" in block, "Missing sub_v6_level_selection_warnings"
    print("PASS: render_machine_block includes sub_v6_level_selection fields")

    # Test render_sub_v6_template_route
    route = render_sub_v6_template_route(payload)
    assert "agent-declared template level, not strict evidence level" in route
    assert "evidence_waived_for_v0_v5: true" in route
    assert "strict_evidence_level_claimed: false" in route
    assert "non_blocking_level_selection_warnings: 1" in route
    print("PASS: render_sub_v6_template_route includes new fields")


def test_renderer_no_warnings():
    """Test renderer with no warnings."""
    from render_gateway_issue_body import render_machine_block

    payload = build_sample_payload()
    payload["sub_v6_level_selection_lint"]["warnings"] = []
    block = render_machine_block(payload)

    assert "warning_count: 0" in block
    assert "sub_v6_level_selection_warnings:" not in block
    print("PASS: renderer omits warnings block when no warnings")


if __name__ == "__main__":
    test_renderer_outputs_level_selection()
    test_renderer_no_warnings()
    print("\nAll renderer warning field tests passed.")
