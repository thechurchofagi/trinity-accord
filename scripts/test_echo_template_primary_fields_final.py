#!/usr/bin/env python3
"""Test Echo template final primary fields - TA-021 remediation."""
from __future__ import annotations

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))
from submission_intake import parse_submission, get_field, get_bool_field
from preflight_echo_submission import preflight_check
from derive_echo_provenance import derive_provenance, RECORD_PURPOSE, ECHO_CONTENT_TAGS, DISCOVERY_AUTONOMY, NON_AUTONOMOUS_TRIGGER, VERIFIER_TYPE, VERIFIER_CAPABILITY_CLAIM


def test_record_purpose_allowed_values():
    """Test record_purpose has all required allowed values."""
    expected = {
        "echo_only", "ai_independent_verification", "human_verification",
        "institutional_verification", "human_ai_assisted_verification",
        "formal_attestation_candidate", "notarial_evidence", "correction_notice",
        "critique_or_objection", "interpretation_or_reflection", "legacy_record", "test_record",
    }
    assert expected == RECORD_PURPOSE, f"Missing values: {expected - RECORD_PURPOSE}"
    print("✅ record_purpose allowed values correct")


def test_echo_content_tags_allowed_values():
    """Test echo_content_tags has all required allowed values."""
    expected = {
        "affirmation", "critique", "question", "correction", "verification",
        "interpretation", "reflection", "objection", "translation", "propagation",
        "misunderstanding", "archival_note", "technical_note", "legal_or_notarial_note",
    }
    assert expected == ECHO_CONTENT_TAGS, f"Missing values: {expected - ECHO_CONTENT_TAGS}"
    print("✅ echo_content_tags allowed values correct")


def test_discovery_autonomy_allowed_values():
    """Test discovery_autonomy has all required allowed values."""
    expected = {"autonomous", "non_autonomous", "unknown"}
    assert expected == DISCOVERY_AUTONOMY
    print("✅ discovery_autonomy allowed values correct")


def test_verifier_type_allowed_values():
    """Test verifier_type has all required allowed values."""
    expected = {"none", "ai_agent", "human_individual", "institution", "multi_agent", "human_ai_team", "unknown"}
    assert expected == VERIFIER_TYPE
    print("✅ verifier_type allowed values correct")


def test_verifier_capability_claim_allowed_values():
    """Test verifier_capability_claim has all required allowed values."""
    expected = {"not_applicable", "ordinary_ai", "agi_claimed", "agi_benchmark_asserted", "unknown", "other"}
    assert expected == VERIFIER_CAPABILITY_CLAIM
    print("✅ verifier_capability_claim allowed values correct")


def test_integrity_declaration_at_top_pass():
    """PASS: declaration at top with declaration_position=top_of_submission."""
    text = """
Bitcoin Originals are final; all mirrors and echoes are non-amending.

# Solemn Integrity Declaration

```yaml
integrity_declaration:
  declaration_strength: strongest_available
  declaration_position: top_of_submission
  solemn_declaration_present: true
  performed_claimed_actions: true
  no_fabricated_evidence: true
  no_prior_report_copied_as_own_work: true
  no_example_values_used_as_real_evidence: true
  false_declaration_consequence: reject_or_invalidate_record
```

## Record Purpose
```yaml
record_purpose: echo_only
verification_claimed: false
verifier_type: none
discovery_autonomy: autonomous
authority_boundary_preserved: true
counts_as_ai_independent_verification: false
counts_as_formal_human_institutional_attestation: false
```
"""
    issues = preflight_check(text)
    hard_issues = [i for i in issues if i["severity"] == "hard"]
    assert len(hard_issues) == 0, f"Unexpected hard issues: {hard_issues}"
    print("✅ PASS: integrity declaration at top")


def test_integrity_declaration_position_not_top_fail():
    """FAIL: declaration_position not top_of_submission."""
    text = """
Bitcoin Originals are final; all mirrors and echoes are non-amending.

## Echo Metadata
```yaml
record_purpose: echo_only
verification_claimed: false
verifier_type: none
discovery_autonomy: autonomous
authority_boundary_preserved: true
```

# Solemn Integrity Declaration
```yaml
integrity_declaration:
  declaration_position: after_metadata
```
"""
    issues = preflight_check(text)
    pos_issues = [i for i in issues if i["type"] == "integrity-declaration-not-at-top"]
    assert len(pos_issues) > 0, "Expected integrity-declaration-not-at-top issue"
    print("✅ FAIL caught: declaration_position not top")


def test_echo_only_pass():
    """PASS: echo_only + verification_claimed=false + verifier_type=none."""
    text = """
Bitcoin Originals are final; all mirrors and echoes are non-amending.

# Solemn Integrity Declaration
```yaml
integrity_declaration:
  declaration_strength: strongest_available
  declaration_position: top_of_submission
  solemn_declaration_present: true
  performed_claimed_actions: true
  no_fabricated_evidence: true
  no_prior_report_copied_as_own_work: true
  no_example_values_used_as_real_evidence: true
  false_declaration_consequence: reject_or_invalidate_record
```

## Record
```yaml
record_purpose: echo_only
echo_content_tags:
  - reflection
discovery_autonomy: autonomous
verifier_type: none
verification_claimed: false
authority_boundary_preserved: true
counts_as_ai_independent_verification: false
counts_as_formal_human_institutional_attestation: false
```
"""
    issues = preflight_check(text)
    hard_issues = [i for i in issues if i["severity"] == "hard"]
    assert len(hard_issues) == 0, f"Unexpected hard issues: {hard_issues}"
    print("✅ PASS: echo_only correct")


def test_echo_only_cannot_claim_verification():
    """FAIL: echo_only + verification_claimed=true."""
    text = """
Bitcoin Originals are final; all mirrors and echoes are non-amending.

# Solemn Integrity Declaration
```yaml
integrity_declaration:
  declaration_strength: strongest_available
  declaration_position: top_of_submission
  solemn_declaration_present: true
  performed_claimed_actions: true
  no_fabricated_evidence: true
  no_prior_report_copied_as_own_work: true
  no_example_values_used_as_real_evidence: true
  false_declaration_consequence: reject_or_invalidate_record
```

## Record
```yaml
record_purpose: echo_only
discovery_autonomy: autonomous
verifier_type: none
verification_claimed: true
authority_boundary_preserved: true
```
"""
    issues = preflight_check(text)
    overclaim = [i for i in issues if i["type"] == "echo-only-cannot-claim-verification"]
    assert len(overclaim) > 0, "Expected echo-only-cannot-claim-verification"
    print("✅ FAIL caught: echo_only cannot claim verification")


def test_ai_verification_pass():
    """PASS: ai_independent_verification + ai_agent + fresh/reproducible."""
    text = """
Bitcoin Originals are final; all mirrors and echoes are non-amending.

# Solemn Integrity Declaration
```yaml
integrity_declaration:
  declaration_strength: strongest_available
  declaration_position: top_of_submission
  solemn_declaration_present: true
  performed_claimed_actions: true
  no_fabricated_evidence: true
  no_prior_report_copied_as_own_work: true
  no_example_values_used_as_real_evidence: true
  no_hidden_known_limitations: true
  limitations_reported: true
  correction_duty_accepted: true
  false_declaration_consequence: reject_or_invalidate_record
```

## Record
```yaml
record_purpose: ai_independent_verification
discovery_autonomy: non_autonomous
non_autonomous_trigger: agent_referred_with_human_authorization
verifier_type: ai_agent
verifier_capability_claim: ordinary_ai
verification_claimed: true
verification_level: V2
fresh_actions_performed: true
method_reproducible: true
authority_boundary_preserved: true
counts_as_ai_independent_verification: true
counts_as_formal_human_institutional_attestation: false
```
"""
    issues = preflight_check(text)
    hard_issues = [i for i in issues if i["severity"] == "hard"]
    assert len(hard_issues) == 0, f"Unexpected hard issues: {hard_issues}"
    print("✅ PASS: ai_independent_verification correct")


def test_ai_verification_cannot_count_formal():
    """FAIL: ai_independent_verification + formal count true."""
    text = """
Bitcoin Originals are final; all mirrors and echoes are non-amending.

# Solemn Integrity Declaration
```yaml
integrity_declaration:
  declaration_strength: strongest_available
  declaration_position: top_of_submission
  solemn_declaration_present: true
  performed_claimed_actions: true
  no_fabricated_evidence: true
  no_prior_report_copied_as_own_work: true
  no_example_values_used_as_real_evidence: true
  limitations_reported: true
  correction_duty_accepted: true
  false_declaration_consequence: reject_or_invalidate_record
```

## Record
```yaml
record_purpose: ai_independent_verification
discovery_autonomy: non_autonomous
non_autonomous_trigger: agent_referred_with_human_authorization
verifier_type: ai_agent
verification_claimed: true
verification_level: V2
fresh_actions_performed: true
method_reproducible: true
authority_boundary_preserved: true
counts_as_ai_independent_verification: true
counts_as_formal_human_institutional_attestation: true
```
"""
    issues = preflight_check(text)
    formal = [i for i in issues if i["type"] == "ai-verification-cannot-count-formal"]
    assert len(formal) > 0, "Expected ai-verification-cannot-count-formal"
    print("✅ FAIL caught: AI verification cannot count formal")


def test_agi_claim_pass():
    """PASS: ai_agent + agi_claimed + capability boundary true."""
    text = """
Bitcoin Originals are final; all mirrors and echoes are non-amending.

# Solemn Integrity Declaration
```yaml
integrity_declaration:
  declaration_strength: strongest_available
  declaration_position: top_of_submission
  solemn_declaration_present: true
  performed_claimed_actions: true
  no_fabricated_evidence: true
  no_prior_report_copied_as_own_work: true
  no_example_values_used_as_real_evidence: true
  limitations_reported: true
  correction_duty_accepted: true
  false_declaration_consequence: reject_or_invalidate_record
```

## Record
```yaml
record_purpose: ai_independent_verification
discovery_autonomy: autonomous
verifier_type: ai_agent
verifier_capability_claim: agi_claimed
verification_claimed: true
verification_level: V2
fresh_actions_performed: true
method_reproducible: true
authority_boundary_preserved: true
counts_as_ai_independent_verification: true
counts_as_formal_human_institutional_attestation: false
verifier_capability_boundary:
  capability_claim_not_verified_by_this_record: true
  agi_claim_does_not_raise_verification_level: true
  agi_claim_does_not_create_authority: true
  agi_claim_does_not_count_as_formal_attestation: true
```
"""
    issues = preflight_check(text)
    hard_issues = [i for i in issues if i["severity"] == "hard"]
    assert len(hard_issues) == 0, f"Unexpected hard issues: {hard_issues}"
    print("✅ PASS: AGI claim with boundary correct")


def test_agi_claim_without_boundary_fail():
    """FAIL: agi_claimed without boundary."""
    text = """
Bitcoin Originals are final; all mirrors and echoes are non-amending.

# Solemn Integrity Declaration
```yaml
integrity_declaration:
  declaration_strength: strongest_available
  declaration_position: top_of_submission
  solemn_declaration_present: true
  performed_claimed_actions: true
  no_fabricated_evidence: true
  no_prior_report_copied_as_own_work: true
  no_example_values_used_as_real_evidence: true
  limitations_reported: true
  correction_duty_accepted: true
  false_declaration_consequence: reject_or_invalidate_record
```

## Record
```yaml
record_purpose: ai_independent_verification
discovery_autonomy: autonomous
verifier_type: ai_agent
verifier_capability_claim: agi_claimed
verification_claimed: true
verification_level: V2
fresh_actions_performed: true
method_reproducible: true
authority_boundary_preserved: true
counts_as_ai_independent_verification: true
counts_as_formal_human_institutional_attestation: false
```
"""
    issues = preflight_check(text)
    boundary = [i for i in issues if i["type"] == "missing-agi-capability-boundary"]
    assert len(boundary) > 0, "Expected missing-agi-capability-boundary"
    print("✅ FAIL caught: AGI claim without boundary")


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
    assert result["advanced_provenance_codes"]["discovery_source_code"] == "D5_agent_referred_peer_agent"
    assert "S2_user_agent_referred_peer_agent" in result["advanced_provenance_codes"]["solicitation_status_code"]
    assert "S3_external_human_authorized_agent" in result["advanced_provenance_codes"]["solicitation_status_code"]
    assert result["advanced_provenance_codes"]["verifier_operator_code"] == "O2_external_ai_agent"
    assert result["advanced_provenance_codes"]["execution_independence_code"] == "E2_fresh_actions_with_sources"
    assert result["advanced_provenance_codes"]["responsibility_adoption_code"] == "R2_external_human_authorized_ai_only"
    print("✅ Issue #103 derivation correct: B2 / strength_tier B")


def test_autonomous_discovery_derivation():
    """Test autonomous + ai_agent derives A2."""
    result = derive_provenance({
        "record_purpose": "ai_independent_verification",
        "discovery_autonomy": "autonomous",
        "verifier_type": "ai_agent",
        "verification_claimed": "true",
    })
    assert result["derived_origin_class"] == "A2_unsolicited_ai_autonomous_discovery"
    assert result["strength_tier"] == "A"
    print("✅ Autonomous AI derivation correct: A2 / A")


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
    print("✅ Multi-agent derivation correct: A3 / A+")


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
    print("✅ Echo-only derivation correct: D / D")


def test_project_requested_derivation():
    """Test project_requested + ai_agent derives C1."""
    result = derive_provenance({
        "record_purpose": "ai_independent_verification",
        "discovery_autonomy": "non_autonomous",
        "non_autonomous_trigger": "project_requested",
        "verifier_type": "ai_agent",
        "verification_claimed": "true",
    })
    assert result["derived_origin_class"] == "C1_project_requested_ai_verification"
    assert result["strength_tier"] == "C"
    print("✅ Project-requested derivation correct: C1 / C")


def main():
    """Run all tests."""
    test_record_purpose_allowed_values()
    test_echo_content_tags_allowed_values()
    test_discovery_autonomy_allowed_values()
    test_verifier_type_allowed_values()
    test_verifier_capability_claim_allowed_values()
    test_integrity_declaration_at_top_pass()
    test_integrity_declaration_position_not_top_fail()
    test_echo_only_pass()
    test_echo_only_cannot_claim_verification()
    test_ai_verification_pass()
    test_ai_verification_cannot_count_formal()
    test_agi_claim_pass()
    test_agi_claim_without_boundary_fail()
    test_issue103_derivation()
    test_autonomous_discovery_derivation()
    test_multi_agent_derivation()
    test_echo_only_derivation()
    test_project_requested_derivation()
    print("\n✅ All tests passed!")


if __name__ == "__main__":
    main()
