#!/usr/bin/env python3
"""Test: V0-V5 single mode enforcement — old strict archive kinds reject new V0-V5 submissions."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from archive_readiness_gate import evaluate_archive_readiness
from claim_gate import evaluate_template_for_v0_v5


def load_fixture(name):
    return json.loads((ROOT / "tests" / "fixtures" / "agent_declared" / name).read_text())


def test_v4_with_verification_report_archive_rejected():
    """V0-V5 submissions using old verification_report_archive kind must be rejected."""
    payload = load_fixture("v4-pass.json")
    payload["requested_archive_kind"] = "verification_report_archive"
    cg = evaluate_template_for_v0_v5(payload)
    # The claim gate will fail because it requires agent_declared_verification_archive
    # But even if it passed, the archive gate should block it
    result = evaluate_archive_readiness(payload, claim_gate_output=cg)
    assert result["archive_ready"] is False
    codes = [br.get("code") for br in result.get("blocking_reasons", [])]
    # Should be blocked by either claim gate or single mode enforcement
    assert any("V0_V5" in c or "CLAIM_GATE" in c or "AGENT_DECLARED" in c for c in codes), \
        f"Expected V0-V5 block, got codes: {codes}"
    print("PASS: V4 + verification_report_archive rejected")


def test_v0_with_verification_report_archive_rejected():
    payload = load_fixture("v0-pass.json")
    payload["requested_archive_kind"] = "verification_report_archive"
    cg = evaluate_template_for_v0_v5(payload)
    result = evaluate_archive_readiness(payload, claim_gate_output=cg)
    assert result["archive_ready"] is False
    print("PASS: V0 + verification_report_archive rejected")


def test_v5_with_verification_report_archive_rejected():
    payload = load_fixture("v5-pass.json")
    payload["requested_archive_kind"] = "verification_report_archive"
    cg = evaluate_template_for_v0_v5(payload)
    result = evaluate_archive_readiness(payload, claim_gate_output=cg)
    assert result["archive_ready"] is False
    print("PASS: V5 + verification_report_archive rejected")


def test_v4_with_archived_echo_rejected():
    payload = load_fixture("v4-pass.json")
    payload["requested_archive_kind"] = "archived_echo"
    cg = evaluate_template_for_v0_v5(payload)
    result = evaluate_archive_readiness(payload, claim_gate_output=cg)
    assert result["archive_ready"] is False
    print("PASS: V4 + archived_echo rejected")


def test_v4_with_agent_declared_accepted():
    payload = load_fixture("v4-pass.json")
    cg = evaluate_template_for_v0_v5(payload)
    result = evaluate_archive_readiness(payload, claim_gate_output=cg)
    assert result["archive_ready"] is True
    assert result["allowed_archive_kind"] == "agent_declared_verification_archive"
    print("PASS: V4 + agent_declared_verification_archive accepted")


if __name__ == "__main__":
    test_v4_with_verification_report_archive_rejected()
    test_v0_with_verification_report_archive_rejected()
    test_v5_with_verification_report_archive_rejected()
    test_v4_with_archived_echo_rejected()
    test_v4_with_agent_declared_accepted()
    print("\nAll V0-V5 single mode enforcement tests passed!")
