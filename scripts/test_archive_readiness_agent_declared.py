#!/usr/bin/env python3
"""Test: Archive readiness gate for agent_declared_verification_archive."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from archive_readiness_gate import evaluate_archive_readiness
from claim_gate import evaluate_template_for_v0_v5


def load_fixture(name):
    return json.loads((ROOT / "tests" / "fixtures" / "agent_declared" / name).read_text())


def test_v4_archive_ready():
    payload = load_fixture("v4-pass.json")
    cg = evaluate_template_for_v0_v5(payload)
    result = evaluate_archive_readiness(payload, claim_gate_output=cg)
    assert result["archive_ready"] is True, f"V4 should be archive_ready, got {result}"
    assert result["allowed_archive_kind"] == "agent_declared_verification_archive"
    assert result["auto_archive_action"] == "auto_archive_agent_declared_verification"
    assert result["auto_close_issue"] is True
    assert "agent-declared" in result.get("auto_labels", [])
    print("PASS: V4 archive ready")


def test_v0_archive_ready():
    payload = load_fixture("v0-pass.json")
    cg = evaluate_template_for_v0_v5(payload)
    result = evaluate_archive_readiness(payload, claim_gate_output=cg)
    assert result["archive_ready"] is True, f"V0 should be archive_ready, got {result}"
    print("PASS: V0 archive ready")


def test_v5_archive_ready():
    payload = load_fixture("v5-pass.json")
    cg = evaluate_template_for_v0_v5(payload)
    result = evaluate_archive_readiness(payload, claim_gate_output=cg)
    assert result["archive_ready"] is True, f"V5 should be archive_ready, got {result}"
    print("PASS: V5 archive ready")


def test_v6_blocked():
    payload = load_fixture("v6-fail.json")
    cg = evaluate_template_for_v0_v5(payload)
    result = evaluate_archive_readiness(payload, claim_gate_output=cg)
    assert result["archive_ready"] is False, f"V6 should be blocked"
    codes = [br.get("code") for br in result.get("blocking_reasons", [])]
    assert "AGENT_DECLARED_ARCHIVE_ONLY_V0_V5" in codes, f"Expected V0_V5 block code, got {codes}"
    print("PASS: V6 correctly blocked")


def test_missing_integrity_blocked():
    payload = load_fixture("missing-integrity-fail.json")
    cg = evaluate_template_for_v0_v5(payload)
    result = evaluate_archive_readiness(payload, claim_gate_output=cg)
    assert result["archive_ready"] is False
    print("PASS: Missing integrity blocked")


def test_overclaim_blocked():
    payload = load_fixture("authority-overclaim-fail.json")
    cg = evaluate_template_for_v0_v5(payload)
    result = evaluate_archive_readiness(payload, claim_gate_output=cg)
    assert result["archive_ready"] is False
    print("PASS: Authority overclaim blocked")


if __name__ == "__main__":
    test_v4_archive_ready()
    test_v0_archive_ready()
    test_v5_archive_ready()
    test_v6_blocked()
    test_missing_integrity_blocked()
    test_overclaim_blocked()
    print("\nAll archive readiness tests passed!")
