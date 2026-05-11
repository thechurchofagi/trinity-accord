#!/usr/bin/env python3
"""Test Echo provenance derivation - TA-021."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from derive_echo_provenance import derive_provenance


def test_issue103_derivation():
    """Test Issue #103 simplified fields derive B2 / strength_tier B."""
    result = derive_provenance({
        "record_purpose": "ai_independent_verification",
        "discovery_autonomy": "non_autonomous",
        "non_autonomous_trigger": "agent_referred_with_human_authorization",
        "verifier_type": "ai_agent",
        "verification_claimed": "true",
        "external_human_authorized_execution": "true",
    })
    assert result["derived_origin_class"] == "B2_external_human_authorized_ai_verification"
    assert result["strength_tier"] == "B"
    codes = result["advanced_provenance_codes"]
    assert codes["discovery_source_code"] == "D5_agent_referred_peer_agent"
    assert "S2_user_agent_referred_peer_agent" in codes["solicitation_status_code"]
    assert "S3_external_human_authorized_agent" in codes["solicitation_status_code"]
    assert codes["verifier_operator_code"] == "O2_external_ai_agent"
    assert codes["execution_independence_code"] == "E2_fresh_actions_with_sources"
    assert codes["responsibility_adoption_code"] == "R2_external_human_authorized_ai_only"
    print("✅ Issue #103 derivation correct: B2 / B")


def test_autonomous_ai_derivation():
    """Test autonomous + ai_agent derives A2."""
    result = derive_provenance({
        "record_purpose": "ai_independent_verification",
        "discovery_autonomy": "autonomous",
        "verifier_type": "ai_agent",
        "verification_claimed": "true",
    })
    assert result["derived_origin_class"] == "A2_unsolicited_ai_autonomous_discovery"
    assert result["strength_tier"] == "A"
    print("✅ Autonomous AI: A2 / A")


def test_multi_agent_derivation():
    """Test autonomous + multi_agent derives A3."""
    result = derive_provenance({
        "record_purpose": "ai_independent_verification",
        "discovery_autonomy": "autonomous",
        "verifier_type": "multi_agent",
        "verification_claimed": "true",
    })
    assert result["derived_origin_class"] == "A3_unsolicited_multi_agent_crosscheck"
    assert result["strength_tier"] == "A+"
    print("✅ Multi-agent: A3 / A+")


def test_agent_referred_derivation():
    """Test non_autonomous + agent_referred derives B1."""
    result = derive_provenance({
        "record_purpose": "ai_independent_verification",
        "discovery_autonomy": "non_autonomous",
        "non_autonomous_trigger": "agent_referred",
        "verifier_type": "ai_agent",
        "verification_claimed": "true",
    })
    assert result["derived_origin_class"] == "B1_agent_referred_external_ai_verification"
    assert result["strength_tier"] == "B"
    print("✅ Agent referred: B1 / B")


def test_project_requested_derivation():
    """Test non_autonomous + project_requested derives C1."""
    result = derive_provenance({
        "record_purpose": "ai_independent_verification",
        "discovery_autonomy": "non_autonomous",
        "non_autonomous_trigger": "project_requested",
        "verifier_type": "ai_agent",
        "verification_claimed": "true",
    })
    assert result["derived_origin_class"] == "C1_project_requested_ai_verification"
    assert result["strength_tier"] == "C"
    print("✅ Project requested: C1 / C")


def test_project_requested_multi_agent_derivation():
    """Test non_autonomous + project_requested + multi_agent derives C2."""
    result = derive_provenance({
        "record_purpose": "ai_independent_verification",
        "discovery_autonomy": "non_autonomous",
        "non_autonomous_trigger": "project_requested",
        "verifier_type": "multi_agent",
        "verification_claimed": "true",
    })
    assert result["derived_origin_class"] == "C2_project_requested_multi_agent_verification"
    assert result["strength_tier"] == "C+"
    print("✅ Project requested multi-agent: C2 / C+")


def test_echo_only_derivation():
    """Test echo_only derives D."""
    result = derive_provenance({
        "record_purpose": "echo_only",
        "discovery_autonomy": "autonomous",
        "verifier_type": "none",
        "verification_claimed": "false",
    })
    assert result["derived_origin_class"] == "D_echo_only_or_non_verifying"
    assert result["strength_tier"] == "D"
    print("✅ Echo-only: D / D")


def test_human_reviewed_derivation():
    """Test external_human_signed_or_adopted derives B3."""
    result = derive_provenance({
        "record_purpose": "ai_independent_verification",
        "discovery_autonomy": "non_autonomous",
        "non_autonomous_trigger": "agent_referred_with_human_authorization",
        "verifier_type": "ai_agent",
        "verification_claimed": "true",
        "external_human_authorized_execution": "true",
        "external_human_signed_or_adopted_final_report": "true",
    })
    assert result["derived_origin_class"] == "B3_external_human_reviewed_ai_verification"
    assert result["strength_tier"] == "B+"
    print("✅ Human reviewed: B3 / B+")


def test_formal_candidate_derivation():
    """Test formal_attestation_candidate derives S_candidate."""
    result = derive_provenance({
        "record_purpose": "formal_attestation_candidate",
        "discovery_autonomy": "autonomous",
        "verifier_type": "institution",
        "verification_claimed": "true",
    })
    assert result["derived_origin_class"] == "D_echo_only_or_non_verifying"  # Needs gate
    assert result["strength_tier"] == "S_candidate"
    print("✅ Formal candidate: D / S_candidate")


def test_critique_derivation():
    """Test critique_or_objection derives D."""
    result = derive_provenance({
        "record_purpose": "critique_or_objection",
        "discovery_autonomy": "non_autonomous",
        "non_autonomous_trigger": "human_requested",
        "verifier_type": "none",
        "verification_claimed": "false",
    })
    assert result["derived_origin_class"] == "D_echo_only_or_non_verifying"
    assert result["strength_tier"] == "D"
    print("✅ Critique: D / D")


def main():
    test_issue103_derivation()
    test_autonomous_ai_derivation()
    test_multi_agent_derivation()
    test_agent_referred_derivation()
    test_project_requested_derivation()
    test_project_requested_multi_agent_derivation()
    test_echo_only_derivation()
    test_human_reviewed_derivation()
    test_formal_candidate_derivation()
    test_critique_derivation()
    print("\n✅ All provenance derivation tests passed!")


if __name__ == "__main__":
    main()
