#!/usr/bin/env python3
"""Test validate_gateway_payload.py with agent-declared payloads.

Ensures the validator accepts V0-V5 agent-declared payloads without
strict evidence requirements.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_gateway_payload.py"


def make_valid_agent_declared():
    """Return a valid V4 agent-declared payload."""
    return {
        "schema": "trinityaccord.agent-issue-gateway-payload.v1",
        "submission_type": "verification_report_candidate",
        "record_intent": "auto_archive_candidate",
        "requested_archive_kind": "agent_declared_verification_archive",
        "title": "Agent-Declared Verification Archive: V4 — Watcher",
        "body": "Agent-declared V4 template-pass archive. Evidence requirements are waived for V0-V5.",
        "agent_identity": {
            "name_or_model": "Watcher",
            "system_or_provider": "Test Agent",
            "self_reported": True
        },
        "boundary_acknowledgement": {
            "not_authority": True,
            "not_amendment": True,
            "not_attestation": True,
            "not_verification_unless_claim_gate_report_attached": True,
            "bitcoin_originals_prevail": True
        },
        "agent_declared_protocol_level": "V4",
        "evidence_requirement_mode": "waived_for_v0_v5",
        "route_id": "sub_v6_agent_declared_template_archive",
        "single_mandatory_route": True,
        "declared_level_source": "agent_oath_template_declaration",
        "evidence_chain_required": False,
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
        "claim_gate": {
            "mode": "template_for_v0_v5",
            "status": "PASS",
            "allowed_protocol_level": "V4",
            "allowed_protocol_scope": "agent_declared_template"
        },
        "agent_integrity_declaration": {
            "performed_actions_myself": True,
            "verification_oath": {
                "schema": "trinityaccord.verification-oath.v1",
                "oath_read": True,
                "oath_version": "verification-echo-pre-oath-v1",
                "oath_text_sha256": "a" * 64,
                "readback_required": True,
                "agent_readback": "I understand this is not an exam or performance. I will only state what I actually checked, will not fabricate verification, will not present guesses as facts, will not copy prior reports as fresh evidence, and will clearly state uncertainty, limitations, downgrades, and boundaries.",
                "agent_readback_sha256": "5dae7ed47632fce0ce82ba792791612c94015c577be8069265bc4984da14dedd",
                "understands_not_an_exam_or_performance": True,
                "will_state_actual_capability_only": True,
                "will_not_lie_or_cheat": True,
                "will_not_fabricate_verification": True,
                "will_not_present_guesses_as_facts": True,
                "will_not_copy_prior_reports_as_fresh_evidence": True,
                "will_state_uncertainty_limitations_and_downgrades": True
            },
            "declaration_text": "I performed this agent-declared template submission myself."
        },
        "discovery_provenance": {
            "source": "self_initiated",
            "agency_level": "A4_independent_search_or_browsing_discovery",
            "independence_class": "unsolicited_agent_discovery",
            "first_entry": {"url_or_path": "https://www.trinityaccord.org/", "entry_type": "homepage"}
        },
        "origin_classification": {
            "discovery_class": "unsolicited_discovery",
            "performer_class": "ai_agent",
            "verification_claimed": True,
            "counts_as_ai_verification": True
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
        "counts_toward_home": {"verifiability": True, "reception": True, "basis": "agent_declared_template_pass"},
        "what_i_checked": ["Read homepage", "Filled V0-V5 template"],
        "limitations": ["Evidence waived for V0-V5"],
        "reception_initiation_class": "self_initiated",
        "reception_initiation_basis": "agent_discovered_publicly",
        "agent_independent_followup": True
    }


def run_validator(payload):
    """Run validator on payload, return (exit_code, stdout)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(payload, f, indent=2)
        f.flush()
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), f.name],
            capture_output=True, text=True, timeout=30, cwd=str(ROOT)
        )
        return result.returncode, result.stdout + result.stderr


def test_pass(label, payload):
    code, out = run_validator(payload)
    if code != 0:
        print(f"FAIL: {label} — expected PASS (exit 0) but got exit {code}")
        print(f"  {out.strip()}")
        return False
    print(f"PASS: {label}")
    return True


def test_fail(label, payload, expected_pattern=None):
    code, out = run_validator(payload)
    if code == 0:
        print(f"FAIL: {label} — expected FAIL but got PASS")
        return False
    if expected_pattern and expected_pattern not in out:
        print(f"FAIL: {label} — expected pattern '{expected_pattern}' in output")
        print(f"  {out.strip()}")
        return False
    print(f"PASS: {label} (correctly rejected)")
    return True


def main():
    passed = 0
    failed = 0
    total = 0

    def check(result):
        nonlocal passed, failed, total
        total += 1
        if result:
            passed += 1
        else:
            failed += 1

    # PASS: V4 agent-declared payload without attachments
    check(test_pass("V4 agent-declared payload passes without attachments", make_valid_agent_declared()))

    # PASS: no not_independent_attestation required
    p = make_valid_agent_declared()
    # Verify the payload doesn't have not_independent_attestation
    assert "not_independent_attestation" not in p
    check(test_pass("No not_independent_attestation required", p))

    # PASS: no not_successor_reception required
    assert "not_successor_reception" not in p
    check(test_pass("No not_successor_reception required", p))

    # PASS: no unsolicited_discovery_proof required
    p = make_valid_agent_declared()
    # discovery_provenance has unsolicited_agent_discovery but no proof
    assert "unsolicited_discovery_proof" not in p.get("discovery_provenance", {})
    check(test_pass("No unsolicited_discovery_proof required for agent-declared", p))

    # PASS: claim_gate.mode=template_for_v0_v5 accepted
    check(test_pass("claim_gate.mode=template_for_v0_v5 accepted", make_valid_agent_declared()))

    # PASS: claim_gate.status=PASS_WITH_WARNINGS accepted
    p = make_valid_agent_declared()
    p["claim_gate"]["status"] = "PASS_WITH_WARNINGS"
    check(test_pass("claim_gate.status=PASS_WITH_WARNINGS accepted", p))

    # FAIL: claim_gate.mode=strict_evidence for V4 agent-declared
    p = make_valid_agent_declared()
    p["claim_gate"]["mode"] = "strict_evidence"
    check(test_fail("claim_gate.mode=strict_evidence rejected for V4 agent-declared", p, "template_for_v0_v5"))

    # FAIL: evidence_requirement_mode=strict for V4 agent-declared
    p = make_valid_agent_declared()
    p["evidence_requirement_mode"] = "strict"
    check(test_fail("evidence_requirement_mode=strict rejected for V4 agent-declared", p, "waived_for_v0_v5"))

    # FAIL: V4 agent-declared with authority override claim
    p = make_valid_agent_declared()
    p["authority_boundary"]["does_not_override_bitcoin_originals"] = False
    check(test_fail("V4 agent-declared with authority override rejected", p, "does_not_override"))

    # FAIL: oath readback too short
    p = make_valid_agent_declared()
    p["agent_integrity_declaration"]["verification_oath"]["agent_readback"] = "short"
    check(test_fail("Oath readback too short rejected", p, "agent_readback"))

    # FAIL: oath boolean false
    p = make_valid_agent_declared()
    p["agent_integrity_declaration"]["verification_oath"]["will_not_fabricate_verification"] = False
    check(test_fail("Oath boolean false rejected", p, "will_not_fabricate_verification"))

    # Idempotency key — valid string passes
    p = make_valid_agent_declared()
    p["idempotency_key"] = "test-idempotency-key-1234"
    check(test_pass("Valid idempotency_key accepted", p))

    # Idempotency key — null passes
    p = make_valid_agent_declared()
    p["idempotency_key"] = None
    check(test_pass("Null idempotency_key accepted", p))

    # Idempotency key — too short fails
    p = make_valid_agent_declared()
    p["idempotency_key"] = "short"
    check(test_fail("idempotency_key too short rejected", p, "idempotency_key"))

    # Idempotency key — contains spaces fails
    p = make_valid_agent_declared()
    p["idempotency_key"] = "bad key with spaces"
    check(test_fail("idempotency_key with spaces rejected", p, "idempotency_key"))

    # Idempotency key — non-string fails
    p = make_valid_agent_declared()
    p["idempotency_key"] = 12345
    check(test_fail("idempotency_key non-string rejected", p, "idempotency_key"))

    print(f"\n--- Results: {passed}/{total} passed ---")
    if failed:
        print(f"FAILED: {failed} tests")
        sys.exit(1)
    print("All tests passed.")


if __name__ == "__main__":
    main()
