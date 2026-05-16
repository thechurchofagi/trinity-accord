#!/usr/bin/env python3
"""Test: archive-readiness-policy contains correct agent_declared_verification_archive policy."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_policy_contains_agent_declared():
    policy = json.loads((ROOT / "api" / "archive-readiness-policy.v1.json").read_text())
    kinds = policy.get("archive_kinds", {})
    assert "agent_declared_verification_archive" in kinds, "Missing agent_declared_verification_archive in archive_kinds"
    ad = kinds["agent_declared_verification_archive"]
    assert ad["allowed_protocol_levels"] == ["V0", "V1", "V2", "V3", "V4", "V5"]
    assert ad["exclusive_for_protocol_levels"] == ["V0", "V1", "V2", "V3", "V4", "V5"]
    assert ad["evidence_required"] is False
    assert ad["artifact_bundle_required"] is False
    assert ad["hash_evidence_required"] is False
    assert ad["public_url_required"] is False
    assert ad["script_audit_required"] is False
    assert ad["component_floors_required"] is False
    assert ad["claim_gate_required"] is True
    assert ad["claim_gate_mode"] == "template_for_v0_v5"
    assert ad["claim_gate_pass_required"] is True
    assert ad["counts_toward_home_verifiability"] is True
    assert ad["counts_toward_home_reception"] is True
    assert ad["auto_archive_allowed"] is True
    print("PASS: policy contains agent_declared_verification_archive with correct settings")


def test_policy_does_not_allow_v6():
    policy = json.loads((ROOT / "api" / "archive-readiness-policy.v1.json").read_text())
    ad = policy["archive_kinds"]["agent_declared_verification_archive"]
    allowed = ad["allowed_protocol_levels"]
    assert "V6" not in allowed, "V6 should not be in allowed_protocol_levels"
    assert "V7" not in allowed, "V7 should not be in allowed_protocol_levels"
    assert "V8" not in allowed, "V8 should not be in allowed_protocol_levels"
    print("PASS: V6/V7/V8 not allowed in agent_declared_verification_archive")


def test_v0_v5_single_mode_rule():
    policy = json.loads((ROOT / "api" / "archive-readiness-policy.v1.json").read_text())
    rule = policy.get("v0_v5_single_mode_rule", {})
    assert rule.get("enforced") is True, "v0_v5_single_mode_rule must be enforced"
    assert rule.get("blocking_code") == "V0_V5_MUST_USE_AGENT_DECLARED_ARCHIVE"
    print("PASS: v0_v5_single_mode_rule is enforced")


if __name__ == "__main__":
    test_policy_contains_agent_declared()
    test_policy_does_not_allow_v6()
    test_v0_v5_single_mode_rule()
    print("\nAll policy tests passed!")
