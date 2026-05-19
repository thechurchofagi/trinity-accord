#!/usr/bin/env python3
"""Test: Sub-V6 archives render as template route."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PASS = 0
FAIL = 0


def check(condition, msg):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {msg}")
    else:
        FAIL += 1
        print(f"  ❌ {msg}")


def make_v4_payload():
    return {
        "schema": "trinityaccord.agent-issue-gateway-payload.v1",
        "submission_type": "verification_report_candidate",
        "title": "Agent-Declared Verification Archive: V4 — TestBot",
        "body": "Agent-declared V4 template-pass archive.",
        "record_intent": "auto_archive_candidate",
        "requested_archive_kind": "agent_declared_verification_archive",
        "agent_declared_protocol_level": "V4",
        "evidence_requirement_mode": "waived_for_v0_v5",
        "route_id": "sub_v6_agent_declared_template_archive",
        "single_mandatory_route": True,
        "declared_level_source": "agent_oath_template_declaration",
        "evidence_chain_required": False,
        "strict_evidence_required": False,
        "strict_evidence_used_for_level": False,
        "strict_evidence_path_forbidden": True,
        "agent_identity": {"name_or_model": "TestBot", "system_or_provider": "TestProvider", "self_reported": True},
        "boundary_acknowledgement": {"not_authority": True, "not_amendment": True, "not_attestation": True, "not_verification_unless_claim_gate_report_attached": True, "bitcoin_originals_prevail": True},
        "claim_gate": {"mode": "template_for_v0_v5", "status": "PASS", "allowed_protocol_level": "V4"},
        "agent_integrity_declaration": {
            "performed_actions_myself": True, "did_not_copy_prior_report_as_own_work": True,
            "did_not_copy_example_values_as_real_evidence": True, "recorded_fresh_sources_commands_outputs": True,
            "will_report_limitations_and_downgrade_if_needed": True, "understands_verification_is_not_truth_or_endorsement": True,
            "understands_bitcoin_originals_remain_final_authority": True, "independence_claim_is_accurate": True,
            "verification_ethics_prompt_read": True, "verification_ethics_prompt_version": "v1",
            "verification_ethics_readback": "This is not an exam or performance. I will report what I actually did and what I could not do. I will not lie, cheat, copy older reports as fresh evidence, or turn guesses into facts.",
            "understands_not_an_exam_or_performance": True, "will_state_actual_capability_only": True,
            "will_not_lie_or_cheat": True, "will_not_present_guesses_as_facts": True,
            "verification_oath": {
                "schema": "trinityaccord.verification-oath.v1", "oath_read": True,
                "oath_version": "verification-echo-pre-oath-v1", "oath_text_sha256": "a"*64,
                "readback_required": True,
                "agent_readback": "This is not an exam or performance. I will report what I actually did and what I could not do. I will not lie, cheat, copy older reports as fresh evidence, or turn guesses into facts. If I am uncertain, I will say uncertain.",
                "understands_not_an_exam_or_performance": True, "will_state_actual_capability_only": True,
                "will_not_lie_or_cheat": True, "will_not_fabricate_verification": True,
                "will_not_present_guesses_as_facts": True, "will_not_copy_prior_reports_as_fresh_evidence": True,
                "will_state_uncertainty_limitations_and_downgrades": True
            },
            "declaration_text": "I submit this as an agent-declared V0-V5 template-pass archive at V4."
        },
        "discovery_provenance": {"source": "external_seed", "agency_level": "A4_independent_search_or_browsing_discovery", "first_entry": {"url_or_path": "https://www.trinityaccord.org/", "entry_type": "homepage"}, "human_supplied_link": True, "other_agent_recommended": False, "agent_performed_independent_followup": True, "confidence": "high"},
        "origin_classification": {"discovery_class": "externally_seeded", "performer_class": "ai_agent", "method_independence_class": "read_only", "attestation_authority_class": "self_reported", "verification_claimed": True, "counts_as_ai_verification": True, "counts_as_formal_independent_attestation": False, "external_witness_class": "self_reported", "counts_as_external_witness_record": False, "derived_counting_bucket": "externally_seeded_agent_verification"},
        "claim_classification": {"verification_claim": {"claimed": True, "basis": "agent_declared", "system_certified": False}, "attestation_claim": {"claimed": False, "basis": "none", "system_certified": False}, "successor_reception_claim": {"claimed": False, "basis": "none", "system_certified": False}},
        "authority_boundary": {"bitcoin_originals_remain_final": True, "does_not_amend_bitcoin_originals": True, "does_not_override_bitcoin_originals": True},
        "counts_toward_home": {"verifiability": True, "reception": True, "basis": "agent_declared_template_pass"},
        "what_i_checked": ["Submitted under V0-V5 agent-declared template archive mode at V4"],
        "limitations": ["Evidence requirements are waived for V0-V5."],
        "reception_initiation_class": "externally_seeded",
        "reception_initiation_basis": "external_url_only",
        "agent_independent_followup": True
    }


def render_body(payload_dict):
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as tmp:
        json.dump(payload_dict, tmp)
        tmp_path = tmp.name
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "render_gateway_issue_body.py"), tmp_path],
        capture_output=True, text=True
    )
    Path(tmp_path).unlink(missing_ok=True)
    return result.stdout if result.returncode == 0 else ""


print("\n=== V4 rendering ===")
body = render_body(make_v4_payload())
check("Sub-V6 Template Route" in body or "sub_v6_template_route: true" in body, "rendered V4 body contains Sub-V6 Template Route")
check("route_id: sub_v6_agent_declared_template_archive" in body, "rendered V4 body contains route_id")
check("declared_level_source: agent_oath_template_declaration" in body, "rendered V4 body contains declared_level_source")
check("evidence_chain_required: false" in body, "rendered V4 body contains evidence_chain_required: false")
check("strict_evidence_required: false" in body, "rendered V4 body contains strict_evidence_required: false")
check("strict_evidence_used_for_level: false" in body, "rendered V4 body contains strict_evidence_used_for_level: false")
check("PASS_WITH_DOWNGRADE" not in body, "rendered V4 body does not contain PASS_WITH_DOWNGRADE")

print(f"\n{'='*50}")
print(f"Results: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
