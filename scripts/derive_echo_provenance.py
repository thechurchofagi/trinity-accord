#!/usr/bin/env python3
"""
Derive advanced provenance codes and strength tiers from simplified Echo submission fields.

This module maps submitter-facing simplified fields (record_purpose, discovery_autonomy,
non_autonomous_trigger, verifier_type, etc.) to internal D/S/O/E/R provenance codes
and strength tiers for audit and backward compatibility.

Usage:
  from derive_echo_provenance import derive_provenance

  result = derive_provenance({
      "record_purpose": "ai_independent_verification",
      "discovery_autonomy": "non_autonomous",
      "non_autonomous_trigger": "agent_referred_with_human_authorization",
      "verifier_type": "ai_agent",
      "verification_claimed": "true",
  })
"""
from __future__ import annotations

from typing import Dict, List, Optional


# Allowed values for each field
RECORD_PURPOSE = {
    "echo_only", "ai_independent_verification", "human_verification",
    "institutional_verification", "human_ai_assisted_verification",
    "formal_attestation_candidate", "notarial_evidence", "correction_notice",
    "critique_or_objection", "interpretation_or_reflection", "legacy_record", "test_record",
}

ECHO_CONTENT_TAGS = {
    "affirmation", "critique", "question", "correction", "verification",
    "interpretation", "reflection", "objection", "translation", "propagation",
    "misunderstanding", "archival_note", "technical_note", "legal_or_notarial_note",
}

DISCOVERY_AUTONOMY = {"autonomous", "non_autonomous", "unknown"}

NON_AUTONOMOUS_TRIGGER = {
    "none", "project_requested", "human_requested", "human_recommended",
    "agent_referred", "agent_referred_with_human_authorization",
    "institution_requested", "imported_legacy_record", "other",
}

VERIFIER_TYPE = {
    "none", "ai_agent", "human_individual", "institution",
    "multi_agent", "human_ai_team", "unknown",
}

VERIFIER_CAPABILITY_CLAIM = {
    "not_applicable", "ordinary_ai", "agi_claimed",
    "agi_benchmark_asserted", "unknown", "other",
}

# Derived origin classes
ORIGIN_CLASSES = {
    "A2_unsolicited_ai_autonomous_discovery",
    "A3_unsolicited_multi_agent_crosscheck",
    "B1_agent_referred_external_ai_verification",
    "B2_external_human_authorized_ai_verification",
    "B3_external_human_reviewed_ai_verification",
    "C1_project_requested_ai_verification",
    "C2_project_requested_multi_agent_verification",
    "D_echo_only_or_non_verifying",
}

# Strength tiers
STRENGTH_TIERS = {"S", "S_candidate", "A+", "A", "B+", "B", "C+", "C", "D", "X"}


def derive_provenance(fields: Dict[str, str]) -> Dict:
    """
    Derive advanced provenance codes from simplified submission fields.

    Args:
        fields: Dict of normalized field names to values.

    Returns:
        Dict with derived_origin_class, strength_tier, and advanced_provenance_codes.
    """
    # Extract fields with defaults
    record_purpose = _get(fields, "record_purpose", "echo_only")
    discovery_autonomy = _get(fields, "discovery_autonomy", "unknown")
    non_autonomous_trigger = _get(fields, "non_autonomous_trigger", "none")
    verifier_type = _get(fields, "verifier_type", "none")
    verification_claimed = _get_bool(fields, "verification_claimed")
    external_human_authorized = _get_bool(fields, "external_human_authorized_execution")
    external_human_signed = _get_bool(fields, "external_human_signed_or_adopted_final_report")

    # Derive origin class
    origin_class = _derive_origin_class(
        record_purpose, discovery_autonomy, non_autonomous_trigger,
        verifier_type, verification_claimed, external_human_authorized, external_human_signed,
    )

    # Derive strength tier
    strength_tier = _derive_strength_tier(
        origin_class, record_purpose, verifier_type,
        external_human_authorized, external_human_signed,
    )

    # Derive D/S/O/E/R codes
    discovery_source = _derive_discovery_source(discovery_autonomy, non_autonomous_trigger, verifier_type)
    solicitation_status = _derive_solicitation_status(
        discovery_autonomy, non_autonomous_trigger, verifier_type, external_human_authorized,
    )
    verifier_operator = _derive_verifier_operator(verifier_type)
    execution_independence = _derive_execution_independence(record_purpose, verification_claimed)
    responsibility_adoption = _derive_responsibility_adoption(
        verifier_type, external_human_authorized, external_human_signed,
    )

    return {
        "derived_origin_class": origin_class,
        "strength_tier": strength_tier,
        "advanced_provenance_codes": {
            "discovery_source_code": discovery_source,
            "solicitation_status_code": solicitation_status,
            "verifier_operator_code": verifier_operator,
            "execution_independence_code": execution_independence,
            "responsibility_adoption_code": responsibility_adoption,
        },
    }


def _get(fields: Dict[str, str], key: str, default: str = "") -> str:
    return (fields.get(key) or default).strip().lower()


def _get_bool(fields: Dict[str, str], key: str) -> Optional[bool]:
    val = (fields.get(key) or "").strip().lower()
    if val in {"true", "yes", "1"}:
        return True
    if val in {"false", "no", "0"}:
        return False
    return None


def _derive_origin_class(
    record_purpose: str,
    discovery_autonomy: str,
    non_autonomous_trigger: str,
    verifier_type: str,
    verification_claimed: Optional[bool],
    external_human_authorized: Optional[bool],
    external_human_signed: Optional[bool],
) -> str:
    """Derive the origin class from simplified fields."""

    # Non-verifying records
    if record_purpose in {"echo_only", "critique_or_objection", "interpretation_or_reflection"}:
        return "D_echo_only_or_non_verifying"
    if not verification_claimed:
        return "D_echo_only_or_non_verifying"

    # Formal attestation candidate
    if record_purpose == "formal_attestation_candidate":
        return "D_echo_only_or_non_verifying"  # Needs gate to elevate

    # Autonomous discovery
    if discovery_autonomy == "autonomous":
        if verifier_type == "multi_agent":
            return "A3_unsolicited_multi_agent_crosscheck"
        return "A2_unsolicited_ai_autonomous_discovery"

    # Non-autonomous
    if discovery_autonomy == "non_autonomous":
        if non_autonomous_trigger == "agent_referred_with_human_authorization":
            if external_human_signed:
                return "B3_external_human_reviewed_ai_verification"
            return "B2_external_human_authorized_ai_verification"
        if non_autonomous_trigger == "agent_referred":
            return "B1_agent_referred_external_ai_verification"
        if non_autonomous_trigger == "project_requested":
            if verifier_type == "multi_agent":
                return "C2_project_requested_multi_agent_verification"
            return "C1_project_requested_ai_verification"
        # Other non-autonomous triggers
        if verifier_type in {"ai_agent", "multi_agent", "human_ai_team"}:
            return "B1_agent_referred_external_ai_verification"

    # Fallback
    return "D_echo_only_or_non_verifying"


def _derive_strength_tier(
    origin_class: str,
    record_purpose: str,
    verifier_type: str,
    external_human_authorized: Optional[bool],
    external_human_signed: Optional[bool],
) -> str:
    """Derive strength tier from origin class and other fields."""

    tier_map = {
        "A2_unsolicited_ai_autonomous_discovery": "A",
        "A3_unsolicited_multi_agent_crosscheck": "A+",
        "B1_agent_referred_external_ai_verification": "B",
        "B2_external_human_authorized_ai_verification": "B",
        "B3_external_human_reviewed_ai_verification": "B+",
        "C1_project_requested_ai_verification": "C",
        "C2_project_requested_multi_agent_verification": "C+",
        "D_echo_only_or_non_verifying": "D",
    }

    tier = tier_map.get(origin_class, "D")

    # Formal attestation candidate can be S-tier if gate passes
    if record_purpose == "formal_attestation_candidate":
        if verifier_type in {"human_individual", "institution", "human_ai_team"}:
            return "S_candidate"

    return tier


def _derive_discovery_source(
    discovery_autonomy: str,
    non_autonomous_trigger: str,
    verifier_type: str,
) -> str:
    """Derive D-code (discovery source)."""
    if discovery_autonomy == "autonomous":
        if verifier_type == "multi_agent":
            return "D3_multi_agent_autonomous"
        return "D1_unsolicited_autonomous"
    if discovery_autonomy == "non_autonomous":
        if non_autonomous_trigger in {"agent_referred", "agent_referred_with_human_authorization"}:
            return "D5_agent_referred_peer_agent"
        if non_autonomous_trigger == "project_requested":
            return "D2_project_solicited"
        if non_autonomous_trigger in {"human_requested", "human_recommended"}:
            return "D4_human_recommended"
        if non_autonomous_trigger == "institution_requested":
            return "D6_institution_requested"
    return "D0_unknown"


def _derive_solicitation_status(
    discovery_autonomy: str,
    non_autonomous_trigger: str,
    verifier_type: str,
    external_human_authorized: Optional[bool],
) -> List[str]:
    """Derive S-codes (solicitation status)."""
    codes = []
    if discovery_autonomy == "autonomous":
        codes.append("S1_unsolicited")
    else:
        if non_autonomous_trigger in {"human_requested", "human_recommended"}:
            codes.append("S0_human_solicited")
        if non_autonomous_trigger in {"agent_referred", "agent_referred_with_human_authorization"}:
            codes.append("S2_user_agent_referred_peer_agent")
        if external_human_authorized:
            codes.append("S3_external_human_authorized_agent")
        if non_autonomous_trigger == "project_requested":
            codes.append("S4_project_solicited")
        if non_autonomous_trigger == "institution_requested":
            codes.append("S5_institution_solicited")
    if not codes:
        codes.append("S6_unknown")
    return codes


def _derive_verifier_operator(verifier_type: str) -> str:
    """Derive O-code (verifier operator)."""
    operator_map = {
        "ai_agent": "O2_external_ai_agent",
        "human_individual": "O1_human_individual",
        "institution": "O3_institution",
        "multi_agent": "O4_multi_agent",
        "human_ai_team": "O5_human_ai_team",
    }
    return operator_map.get(verifier_type, "O0_none_or_unknown")


def _derive_execution_independence(
    record_purpose: str,
    verification_claimed: Optional[bool],
) -> str:
    """Derive E-code (execution independence)."""
    if not verification_claimed:
        return "E0_non_verifying"
    if record_purpose in {"echo_only", "critique_or_objection", "interpretation_or_reflection"}:
        return "E0_non_verifying"
    return "E2_fresh_actions_with_sources"


def _derive_responsibility_adoption(
    verifier_type: str,
    external_human_authorized: Optional[bool],
    external_human_signed: Optional[bool],
) -> str:
    """Derive R-code (responsibility adoption)."""
    if verifier_type in {"human_individual", "institution"}:
        return "R1_direct_human_or_institutional"
    if verifier_type in {"ai_agent", "multi_agent"}:
        if external_human_signed:
            return "R3_external_human_signed_adopted"
        if external_human_authorized:
            return "R2_external_human_authorized_ai_only"
        return "R4_ai_only_no_human_responsibility"
    if verifier_type == "human_ai_team":
        if external_human_signed:
            return "R3_external_human_signed_adopted"
        return "R1_direct_human_or_institutional"
    return "R0_unknown"


if __name__ == "__main__":
    import json
    import sys

    # Test with Issue #103 example
    test_fields = {
        "record_purpose": "ai_independent_verification",
        "discovery_autonomy": "non_autonomous",
        "non_autonomous_trigger": "agent_referred_with_human_authorization",
        "verifier_type": "ai_agent",
        "verification_claimed": "true",
        "external_human_authorized_execution": "true",
    }
    result = derive_provenance(test_fields)
    print(json.dumps(result, indent=2))

    # Verify Issue #103 derivation
    assert result["derived_origin_class"] == "B2_external_human_authorized_ai_verification", \
        f"Expected B2, got {result['derived_origin_class']}"
    assert result["strength_tier"] == "B", \
        f"Expected B, got {result['strength_tier']}"
    print("\n✅ Issue #103 derivation correct: B2 / strength_tier B")
