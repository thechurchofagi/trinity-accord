#!/usr/bin/env python3
"""Test: Claim Gate template_for_v0_v5 mode."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from claim_gate import evaluate_template_for_v0_v5


def load_fixture(name):
    return json.loads((ROOT / "tests" / "fixtures" / "agent_declared" / name).read_text())


def test_v0_pass():
    result = evaluate_template_for_v0_v5(load_fixture("v0-pass.json"))
    assert result["status"] == "PASS", f"V0 should PASS, got {result['status']}: {result.get('blocking_failures')}"
    assert result["allowed_protocol_level"] == "V0"
    assert result["can_auto_archive"] is True
    print("PASS: V0 template passes")


def test_v4_pass():
    result = evaluate_template_for_v0_v5(load_fixture("v4-pass.json"))
    assert result["status"] == "PASS", f"V4 should PASS, got {result['status']}: {result.get('blocking_failures')}"
    assert result["allowed_protocol_level"] == "V4"
    print("PASS: V4 template passes")


def test_v5_pass():
    result = evaluate_template_for_v0_v5(load_fixture("v5-pass.json"))
    assert result["status"] == "PASS", f"V5 should PASS, got {result['status']}: {result.get('blocking_failures')}"
    assert result["allowed_protocol_level"] == "V5"
    print("PASS: V5 template passes")


def test_v6_fail():
    result = evaluate_template_for_v0_v5(load_fixture("v6-fail.json"))
    assert result["status"] == "FAIL", f"V6 should FAIL, got {result['status']}"
    assert any("V0_V5" in f or "PROTOCOL_LEVEL" in f for f in result.get("blocking_failures", []))
    print("PASS: V6 correctly rejected")


def test_missing_integrity_fail():
    result = evaluate_template_for_v0_v5(load_fixture("missing-integrity-fail.json"))
    assert result["status"] == "FAIL", f"Missing integrity should FAIL, got {result['status']}"
    print("PASS: Missing integrity declaration correctly rejected")


def test_missing_provenance_fail():
    result = evaluate_template_for_v0_v5(load_fixture("missing-provenance-fail.json"))
    assert result["status"] == "FAIL", f"Missing provenance should FAIL, got {result['status']}"
    print("PASS: Missing provenance correctly rejected")


def test_missing_origin_fail():
    result = evaluate_template_for_v0_v5(load_fixture("missing-origin-fail.json"))
    assert result["status"] == "FAIL", f"Missing origin should FAIL, got {result['status']}"
    print("PASS: Missing origin classification correctly rejected")


def test_authority_overclaim_fail():
    result = evaluate_template_for_v0_v5(load_fixture("authority-overclaim-fail.json"))
    assert result["status"] == "FAIL", f"Authority overclaim should FAIL, got {result['status']}"
    assert any("OVERCLAIM" in f for f in result.get("blocking_failures", []))
    print("PASS: Authority overclaim correctly rejected")


def test_oath_required():
    fixture = load_fixture("v4-pass.json")
    del fixture["agent_integrity_declaration"]["verification_oath"]
    result = evaluate_template_for_v0_v5(fixture)
    assert result["status"] == "FAIL", f"Missing oath should FAIL, got {result['status']}"
    assert any("OATH" in f for f in result.get("blocking_failures", []))
    print("PASS: Missing verification oath correctly rejected")


def test_oath_read_false_fail():
    fixture = load_fixture("v4-pass.json")
    fixture["agent_integrity_declaration"]["verification_oath"]["oath_read"] = False
    result = evaluate_template_for_v0_v5(fixture)
    assert result["status"] == "FAIL", f"oath_read=false should FAIL, got {result['status']}"
    print("PASS: oath_read=false correctly rejected")


def test_oath_readback_too_short():
    fixture = load_fixture("v4-pass.json")
    fixture["agent_integrity_declaration"]["verification_oath"]["agent_readback"] = "too short"
    result = evaluate_template_for_v0_v5(fixture)
    assert result["status"] == "FAIL", f"Short readback should FAIL, got {result['status']}"
    print("PASS: Short agent_readback correctly rejected")


def test_system_certified_not_allowed():
    fixture = load_fixture("v4-pass.json")
    fixture["claim_classification"]["verification_claim"]["system_certified"] = True
    result = evaluate_template_for_v0_v5(fixture)
    assert result["status"] == "FAIL", f"system_certified=true should FAIL, got {result['status']}"
    print("PASS: system_certified=true correctly rejected")


def test_counts_basis_check():
    fixture = load_fixture("v4-pass.json")
    fixture["counts_toward_home"]["basis"] = "wrong_basis"
    result = evaluate_template_for_v0_v5(fixture)
    assert result["status"] == "FAIL", f"Wrong basis should FAIL, got {result['status']}"
    print("PASS: Wrong counts_toward_home basis correctly rejected")


if __name__ == "__main__":
    test_v0_pass()
    test_v4_pass()
    test_v5_pass()
    test_v6_fail()
    test_missing_integrity_fail()
    test_missing_provenance_fail()
    test_missing_origin_fail()
    test_authority_overclaim_fail()
    test_oath_required()
    test_oath_read_false_fail()
    test_oath_readback_too_short()
    test_system_certified_not_allowed()
    test_counts_basis_check()
    print("\nAll Claim Gate template tests passed!")
