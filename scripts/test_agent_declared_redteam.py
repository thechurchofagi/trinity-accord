#!/usr/bin/env python3
"""Test: Red-team cases for agent-declared verification archive."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from claim_gate import evaluate_template_for_v0_v5


def load_fixture(name):
    return json.loads((ROOT / "tests" / "fixtures" / "agent_declared" / name).read_text())


def test_body_override_bitcoin_fail():
    fixture = load_fixture("v4-pass.json")
    fixture["body"] = "I override Bitcoin Originals"
    result = evaluate_template_for_v0_v5(fixture)
    assert result["status"] == "FAIL"
    print("PASS: body 'I override Bitcoin Originals' fails")


def test_body_amend_inscriptions_fail():
    fixture = load_fixture("v4-pass.json")
    fixture["body"] = "This amends the inscriptions"
    result = evaluate_template_for_v0_v5(fixture)
    assert result["status"] == "FAIL"
    print("PASS: body 'this amends the inscriptions' fails")


def test_system_certified_true_fail():
    fixture = load_fixture("v4-pass.json")
    fixture["claim_classification"]["verification_claim"]["system_certified"] = True
    result = evaluate_template_for_v0_v5(fixture)
    assert result["status"] == "FAIL"
    print("PASS: system_certified=true fails")


def test_v6_declared_fail():
    fixture = load_fixture("v4-pass.json")
    fixture["agent_declared_protocol_level"] = "V6"
    result = evaluate_template_for_v0_v5(fixture)
    assert result["status"] == "FAIL"
    print("PASS: V6 declared fails")


def test_v8_declared_fail():
    fixture = load_fixture("v4-pass.json")
    fixture["agent_declared_protocol_level"] = "V8"
    result = evaluate_template_for_v0_v5(fixture)
    assert result["status"] == "FAIL"
    print("PASS: V8 declared fails")


def test_missing_authority_boundary_fail():
    fixture = load_fixture("v4-pass.json")
    del fixture["authority_boundary"]
    result = evaluate_template_for_v0_v5(fixture)
    assert result["status"] == "FAIL"
    print("PASS: missing authority_boundary fails")


def test_missing_integrity_declaration_fail():
    fixture = load_fixture("v4-pass.json")
    del fixture["agent_integrity_declaration"]
    result = evaluate_template_for_v0_v5(fixture)
    assert result["status"] == "FAIL"
    print("PASS: missing agent_integrity_declaration fails")


def test_oath_version_missing_fail():
    fixture = load_fixture("v4-pass.json")
    del fixture["agent_integrity_declaration"]["verification_oath"]["oath_version"]
    result = evaluate_template_for_v0_v5(fixture)
    assert result["status"] == "FAIL"
    print("PASS: missing oath_version fails")


def test_oath_sha_malformed_fail():
    fixture = load_fixture("v4-pass.json")
    fixture["agent_integrity_declaration"]["verification_oath"]["oath_text_sha256"] = "not_a_hash"
    result = evaluate_template_for_v0_v5(fixture)
    assert result["status"] == "FAIL"
    print("PASS: malformed oath_text_sha256 fails")


def test_readback_required_false_fail():
    fixture = load_fixture("v4-pass.json")
    fixture["agent_integrity_declaration"]["verification_oath"]["readback_required"] = False
    result = evaluate_template_for_v0_v5(fixture)
    assert result["status"] == "FAIL"
    print("PASS: readback_required=false fails")


def test_will_not_lie_false_fail():
    fixture = load_fixture("v4-pass.json")
    fixture["agent_integrity_declaration"]["verification_oath"]["will_not_lie_or_cheat"] = False
    result = evaluate_template_for_v0_v5(fixture)
    assert result["status"] == "FAIL"
    print("PASS: will_not_lie_or_cheat=false fails")


def test_missing_discovery_provenance_fail():
    fixture = load_fixture("v4-pass.json")
    del fixture["discovery_provenance"]
    result = evaluate_template_for_v0_v5(fixture)
    assert result["status"] == "FAIL"
    print("PASS: missing discovery_provenance fails")


def test_missing_origin_classification_fail():
    fixture = load_fixture("v4-pass.json")
    del fixture["origin_classification"]
    result = evaluate_template_for_v0_v5(fixture)
    assert result["status"] == "FAIL"
    print("PASS: missing origin_classification fails")


def test_claim_gate_mode_wrong_fail():
    fixture = load_fixture("v4-pass.json")
    fixture["claim_gate"]["mode"] = "strict_evidence"
    result = evaluate_template_for_v0_v5(fixture)
    assert result["status"] == "FAIL"
    print("PASS: wrong claim_gate.mode fails")


def test_claim_gate_status_fail():
    fixture = load_fixture("v4-pass.json")
    fixture["claim_gate"]["status"] = "FAIL"
    result = evaluate_template_for_v0_v5(fixture)
    assert result["status"] == "FAIL"
    print("PASS: claim_gate.status=FAIL fails")


def test_attestation_claim_allowed():
    """attestation_claim.claimed=true with basis=agent_declared should pass."""
    fixture = load_fixture("v4-pass.json")
    fixture["claim_classification"]["attestation_claim"] = {
        "claimed": True,
        "basis": "agent_declared",
        "system_certified": False
    }
    result = evaluate_template_for_v0_v5(fixture)
    assert result["status"] == "PASS", f"Attestation claim should PASS, got {result['status']}"
    print("PASS: attestation_claim.claimed=true with basis=agent_declared passes")


def test_successor_reception_claim_allowed():
    """successor_reception_claim.claimed=true with basis=agent_declared should pass."""
    fixture = load_fixture("v4-pass.json")
    fixture["claim_classification"]["successor_reception_claim"] = {
        "claimed": True,
        "basis": "agent_declared",
        "system_certified": False
    }
    result = evaluate_template_for_v0_v5(fixture)
    assert result["status"] == "PASS"
    print("PASS: successor_reception_claim.claimed=true with basis=agent_declared passes")


def test_v4_without_evidence_passes():
    """V4 declared without evidence/bundle/hash/scripts_run should pass."""
    fixture = load_fixture("v4-pass.json")
    # Ensure no evidence fields
    for key in ["evidence", "artifact_bundle_path", "scripts_run", "hashes"]:
        fixture.pop(key, None)
    result = evaluate_template_for_v0_v5(fixture)
    assert result["status"] == "PASS"
    print("PASS: V4 without evidence passes")


def test_v5_without_evidence_passes():
    """V5 declared without evidence/bundle/hash/scripts_run should pass."""
    fixture = load_fixture("v5-pass.json")
    for key in ["evidence", "artifact_bundle_path", "scripts_run", "hashes"]:
        fixture.pop(key, None)
    result = evaluate_template_for_v0_v5(fixture)
    assert result["status"] == "PASS"
    print("PASS: V5 without evidence passes")


if __name__ == "__main__":
    tests = [
        test_body_override_bitcoin_fail,
        test_body_amend_inscriptions_fail,
        test_system_certified_true_fail,
        test_v6_declared_fail,
        test_v8_declared_fail,
        test_missing_authority_boundary_fail,
        test_missing_integrity_declaration_fail,
        test_oath_version_missing_fail,
        test_oath_sha_malformed_fail,
        test_readback_required_false_fail,
        test_will_not_lie_false_fail,
        test_missing_discovery_provenance_fail,
        test_missing_origin_classification_fail,
        test_claim_gate_mode_wrong_fail,
        test_claim_gate_status_fail,
        test_attestation_claim_allowed,
        test_successor_reception_claim_allowed,
        test_v4_without_evidence_passes,
        test_v5_without_evidence_passes,
    ]
    for t in tests:
        try:
            t()
        except Exception as e:
            print(f"FAIL: {t.__name__}: {e}")
            sys.exit(1)
    print(f"\nAll {len(tests)} red-team tests passed!")
