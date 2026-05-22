#!/usr/bin/env python3
"""Test Verification Oath v2 fields in agent-declared archive payload."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from oath_contracts import build_verification_oath_v2, load_oath_text

OATH_FILE = ROOT / "api" / "verification-echo-pre-oath.v2.txt"


def test_verification_oath_v2():
    oath_text = load_oath_text(OATH_FILE)
    oath = build_verification_oath_v2(oath_text)

    assert oath["schema"] == "trinityaccord.verification-oath.v2", f"Bad schema: {oath['schema']}"
    assert oath["oath_version"] == "verification-echo-pre-oath-v2", f"Bad version: {oath['oath_version']}"
    assert oath["oath_kind"] == "verification_echo"
    assert oath["oath_read"] is True
    assert oath["readback_required"] is True

    # New v2 fields
    assert oath["honesty_oath_present"] is True
    assert oath["good_faith_oath_present"] is True
    assert oath["will_not_submit_maliciously"] is True
    assert oath["will_not_spam_or_mass_submit_for_abuse"] is True
    assert oath["will_not_create_false_authority_or_false_consensus"] is True
    assert oath["will_not_duplicate_claim_without_disclosure"] is True
    assert oath["will_correct_material_errors_when_aware"] is True
    assert oath["not_authority"] is True
    assert oath["not_attestation"] is True
    assert oath["not_successor_reception"] is True
    assert oath["not_amendment"] is True
    assert oath["not_governance"] is True
    assert oath["not_verification_level"] is True
    assert oath["bitcoin_originals_prevail"] is True
    assert oath["will_not_knowingly_misrepresent"] is True
    assert oath["will_not_impersonate"] is True
    assert oath["will_not_fabricate_claims"] is True

    # Legacy fields must still be present
    assert oath["understands_not_an_exam_or_performance"] is True
    assert oath["will_state_actual_capability_only"] is True
    assert oath["will_not_lie_or_cheat"] is True
    assert oath["will_not_fabricate_verification"] is True
    assert oath["will_not_present_guesses_as_facts"] is True
    assert oath["will_not_copy_prior_reports_as_fresh_evidence"] is True
    assert oath["will_state_uncertainty_limitations_and_downgrades"] is True

    # SHA256 should be valid
    assert len(oath["oath_text_sha256"]) == 64
    assert len(oath["agent_readback_sha256"]) == 64

    print("PASS: test_verification_oath_v2")


if __name__ == "__main__":
    test_verification_oath_v2()
