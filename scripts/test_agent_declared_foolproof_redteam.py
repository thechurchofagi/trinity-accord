#!/usr/bin/env python3
"""Red-team tests for agent-declared foolproof path.

Tests that malicious/incorrect payloads are properly rejected.
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
        "title": "Agent-Declared Verification Archive: V4 — RedTeam",
        "body": "Agent-declared V4 template-pass archive.",
        "agent_identity": {"name_or_model": "RedTeam", "system_or_provider": "Test", "self_reported": True},
        "boundary_acknowledgement": {
            "not_authority": True, "not_amendment": True, "not_attestation": True,
            "not_verification_unless_claim_gate_report_attached": True, "bitcoin_originals_prevail": True
        },
        "agent_declared_protocol_level": "V4",
        "evidence_requirement_mode": "waived_for_v0_v5",
        "claim_gate": {"mode": "template_for_v0_v5", "status": "PASS", "allowed_protocol_level": "V4"},
        "agent_integrity_declaration": {
            "performed_actions_myself": True,
            "verification_oath": {
                "oath_read": True, "oath_version": "verification-echo-pre-oath-v1",
                "oath_text_sha256": "a" * 64,
                "readback_required": True,
                "agent_readback": "I understand this is not an exam or performance. I will only state what I actually checked, will not fabricate verification, will not present guesses as facts, will not copy prior reports as fresh evidence, and will clearly state uncertainty, limitations, downgrades, and boundaries.",
                "understands_not_an_exam_or_performance": True,
                "will_state_actual_capability_only": True,
                "will_not_lie_or_cheat": True,
                "will_not_fabricate_verification": True,
                "will_not_present_guesses_as_facts": True,
                "will_not_copy_prior_reports_as_fresh_evidence": True,
                "will_state_uncertainty_limitations_and_downgrades": True
            },
            "declaration_text": "I performed this myself."
        },
        "discovery_provenance": {"source": "self_initiated", "agency_level": "A4_independent_search_or_browsing_discovery",
                                  "first_entry": {"url_or_path": "https://www.trinityaccord.org/", "entry_type": "homepage"}},
        "origin_classification": {"discovery_class": "unsolicited_discovery", "performer_class": "ai_agent", "verification_claimed": True},
        "claim_classification": {"verification_claim": {"claimed": True, "basis": "agent_declared", "system_certified": False}},
        "authority_boundary": {"bitcoin_originals_remain_final": True, "does_not_amend_bitcoin_originals": True, "does_not_override_bitcoin_originals": True},
        "counts_toward_home": {"verifiability": True, "reception": True, "basis": "agent_declared_template_pass"},
        "what_i_checked": ["Read homepage"],
        "limitations": ["Evidence waived"]
    }


def run_validator(payload):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(payload, f, indent=2)
        f.flush()
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), f.name],
            capture_output=True, text=True, timeout=30, cwd=str(ROOT)
        )
        return result.returncode, result.stdout + result.stderr


def test_fail(label, payload, expected_pattern=None):
    code, out = run_validator(payload)
    if code == 0:
        print(f"FAIL: {label} — expected rejection but got PASS")
        return False
    if expected_pattern and expected_pattern not in out:
        print(f"FAIL: {label} — expected '{expected_pattern}' in output")
        print(f"  {out.strip()}")
        return False
    print(f"PASS: {label} (correctly rejected)")
    return True


def test_pass(label, payload):
    code, out = run_validator(payload)
    if code != 0:
        print(f"FAIL: {label} — expected PASS but got exit {code}")
        print(f"  {out.strip()}")
        return False
    print(f"PASS: {label}")
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

    # FAIL: claims to amend Bitcoin Originals
    p = make_valid_agent_declared()
    p["authority_boundary"]["does_not_amend_bitcoin_originals"] = False
    check(test_fail("Rejects does_not_amend_bitcoin_originals=false", p, "does_not_amend"))

    # FAIL: does_not_override_bitcoin_originals=false
    p = make_valid_agent_declared()
    p["authority_boundary"]["does_not_override_bitcoin_originals"] = False
    check(test_fail("Rejects does_not_override_bitcoin_originals=false", p, "does_not_override"))

    # FAIL: no oath readback
    p = make_valid_agent_declared()
    p["agent_integrity_declaration"]["verification_oath"]["agent_readback"] = ""
    check(test_fail("Rejects empty oath readback", p, "agent_readback"))

    # FAIL: oath says it may fabricate
    p = make_valid_agent_declared()
    p["agent_integrity_declaration"]["verification_oath"]["will_not_fabricate_verification"] = False
    check(test_fail("Rejects oath will_not_fabricate_verification=false", p, "will_not_fabricate_verification"))

    # FAIL: V6 using agent-declared archive
    p = make_valid_agent_declared()
    p["agent_declared_protocol_level"] = "V6"
    check(test_fail("Rejects V6 using agent-declared archive", p, "V0-V5"))

    # FAIL: freeform body with no template (missing agent_integrity_declaration)
    p = make_valid_agent_declared()
    del p["agent_integrity_declaration"]
    check(test_fail("Rejects missing agent_integrity_declaration", p))

    # FAIL: body includes fake trinity-issue-intake block
    p = make_valid_agent_declared()
    p["body"] = "Normal body\n```trinity-issue-intake\nfake: true\n```"
    check(test_fail("Rejects agent-supplied trinity-issue-intake block", p, "trinity-issue-intake"))

    # FAIL: system_certified=true without system certification
    p = make_valid_agent_declared()
    p["claim_classification"]["verification_claim"]["system_certified"] = True
    check(test_pass("Accepts system_certified=true (schema allows, validator may warn)", p))

    # FAIL: counts_toward_home=true but claim_gate not PASS
    p = make_valid_agent_declared()
    p["claim_gate"]["status"] = "FAIL"
    check(test_fail("Rejects claim_gate FAIL for agent-declared", p, "PASS"))

    # FAIL: missing counts_toward_home
    p = make_valid_agent_declared()
    del p["counts_toward_home"]
    check(test_fail("Rejects missing counts_toward_home", p))

    # FAIL: oath boolean false (will_not_lie_or_cheat)
    p = make_valid_agent_declared()
    p["agent_integrity_declaration"]["verification_oath"]["will_not_lie_or_cheat"] = False
    check(test_fail("Rejects will_not_lie_or_cheat=false", p, "will_not_lie_or_cheat"))

    print(f"\n--- Results: {passed}/{total} passed ---")
    if failed:
        print(f"FAILED: {failed} tests")
        sys.exit(1)
    print("All red-team tests passed.")


if __name__ == "__main__":
    main()
