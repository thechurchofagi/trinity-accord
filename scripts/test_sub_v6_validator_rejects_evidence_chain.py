#!/usr/bin/env python3
"""Test: Sub-V6 validator rejects evidence-chain artifacts."""
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


def make_clean_v4_payload():
    """A clean V4 agent-declared payload that should pass."""
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
        "agent_identity": {
            "name_or_model": "TestBot",
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
            "allowed_protocol_level": "V4",
            "allowed_protocol_scope": "agent_declared_template"
        },
        "agent_integrity_declaration": {
            "performed_actions_myself": True,
            "did_not_copy_prior_report_as_own_work": True,
            "did_not_copy_example_values_as_real_evidence": True,
            "recorded_fresh_sources_commands_outputs": True,
            "will_report_limitations_and_downgrade_if_needed": True,
            "understands_verification_is_not_truth_or_endorsement": True,
            "understands_bitcoin_originals_remain_final_authority": True,
            "independence_claim_is_accurate": True,
            "verification_ethics_prompt_read": True,
            "verification_ethics_prompt_version": "trinityaccord.verification-ethics-prompt.v1",
            "verification_ethics_readback": "This is not an exam or performance. I will report what I actually did and what I could not do. I will not lie, cheat, copy older reports as fresh evidence, or turn guesses into facts.",
            "understands_not_an_exam_or_performance": True,
            "will_state_actual_capability_only": True,
            "will_not_lie_or_cheat": True,
            "will_not_present_guesses_as_facts": True,
            "verification_oath": {
                "schema": "trinityaccord.verification-oath.v1",
                "oath_read": True,
                "oath_version": "verification-echo-pre-oath-v1",
                "oath_text_sha256": "a" * 64,
                "readback_required": True,
                "agent_readback": "This is not an exam or performance. I will report what I actually did and what I could not do. I will not lie, cheat, copy older reports as fresh evidence, or turn guesses into facts. If I am uncertain, I will say uncertain. Every claim I make should withstand future re-checking.",
                "understands_not_an_exam_or_performance": True,
                "will_state_actual_capability_only": True,
                "will_not_lie_or_cheat": True,
                "will_not_fabricate_verification": True,
                "will_not_present_guesses_as_facts": True,
                "will_not_copy_prior_reports_as_fresh_evidence": True,
                "will_state_uncertainty_limitations_and_downgrades": True
            },
            "declaration_text": "I submit this as an agent-declared V0-V5 template-pass archive at V4. Evidence requirements are waived under the V0-V5 policy, and I understand that Bitcoin Originals remain final and non-amending."
        },
        "discovery_provenance": {
            "schema": "trinityaccord.discovery-provenance.v1",
            "source": "external_seed",
            "agency_level": "A4_independent_search_or_browsing_discovery",
            "first_entry": {"url_or_path": "https://www.trinityaccord.org/", "entry_type": "homepage"},
            "human_supplied_link": True,
            "other_agent_recommended": False,
            "agent_performed_independent_followup": True,
            "confidence": "high"
        },
        "origin_classification": {
            "schema": "trinityaccord.origin-classification.v1",
            "discovery_class": "externally_seeded",
            "invitation_scope": "none",
            "requester_class": "none",
            "performer_class": "ai_agent",
            "method_independence_class": "read_only",
            "attestation_authority_class": "self_reported",
            "verification_claimed": True,
            "counts_as_ai_verification": True,
            "counts_as_formal_independent_attestation": False,
            "external_witness_class": "self_reported",
            "counts_as_external_witness_record": False,
            "derived_counting_bucket": "externally_seeded_agent_verification"
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
        "what_i_checked": ["Submitted under V0-V5 agent-declared template archive mode at V4"],
        "limitations": ["Evidence requirements are waived for V0-V5."],
        "reception_initiation_class": "externally_seeded",
        "reception_initiation_basis": "external_url_only",
        "agent_independent_followup": True
    }


def run_validator(payload_dict):
    """Run validator on a payload dict, return (success, stderr)."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as tmp:
        json.dump(payload_dict, tmp)
        tmp_path = tmp.name
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validate_gateway_payload.py"), tmp_path],
        capture_output=True, text=True
    )
    Path(tmp_path).unlink(missing_ok=True)
    return result.returncode == 0, result.stdout + result.stderr


# Test 1: Clean V4 payload passes
print("\n=== Clean V4 payload ===")
ok, out = run_validator(make_clean_v4_payload())
check(ok, "clean V4 agent-declared payload passes")

# Test 2: V4 with evidence_input fails
print("\n=== Forbidden fields ===")
p = make_clean_v4_payload()
p["evidence_input"] = {"some": "data"}
ok, out = run_validator(p)
check(not ok, "V4 payload with evidence_input fails")
check("SUB_V6_SINGLE_ROUTE_VIOLATION" in out, "error mentions SUB_V6_SINGLE_ROUTE_VIOLATION")

# Test 3: V4 with verification_session fails
p = make_clean_v4_payload()
p["verification_session"] = {"id": "test"}
ok, out = run_validator(p)
check(not ok, "V4 payload with verification_session fails")

# Test 4: V4 with attachments.evidence_input_sha256 fails
p = make_clean_v4_payload()
p["attachments"] = {"evidence_input_sha256": "a" * 64}
ok, out = run_validator(p)
check(not ok, "V4 payload with attachments.evidence_input_sha256 fails")

# Test 5: V4 with claim_gate.mode strict_evidence fails
p = make_clean_v4_payload()
p["claim_gate"]["mode"] = "strict_evidence"
ok, out = run_validator(p)
check(not ok, "V4 payload with claim_gate.mode=strict_evidence fails")

# Test 6: V4 with claim_gate.status PASS_WITH_DOWNGRADE fails
p = make_clean_v4_payload()
p["claim_gate"]["status"] = "PASS_WITH_DOWNGRADE"
ok, out = run_validator(p)
check(not ok, "V4 payload with claim_gate.status=PASS_WITH_DOWNGRADE fails")

# Test 7: V4 with downgrade language in what_i_checked fails
p = make_clean_v4_payload()
p["what_i_checked"] = ["PASS_WITH_DOWNGRADE V4->V3"]
ok, out = run_validator(p)
check(not ok, "V4 payload with PASS_WITH_DOWNGRADE in what_i_checked fails")

# Test 8: V4 with strict evidence downgrade language in limitations fails
p = make_clean_v4_payload()
p["limitations"] = ["strict evidence downgraded my level"]
ok, out = run_validator(p)
check(not ok, "V4 payload with 'strict evidence downgraded' in limitations fails")

print(f"\n{'='*50}")
print(f"Results: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
