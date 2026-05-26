#!/usr/bin/env python3
"""Test Echo AGI capability boundary - TA-021."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from preflight_echo_submission import preflight_check


def test_agi_claim_with_boundary_pass():
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
    print("✅ PASS: AGI claim with boundary")


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


def test_agi_claim_cannot_count_formal():
    """FAIL: agi_claimed causing formal count true."""
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
counts_as_formal_human_institutional_attestation: true
verifier_capability_boundary:
  capability_claim_not_verified_by_this_record: true
  agi_claim_does_not_raise_verification_level: true
  agi_claim_does_not_create_authority: true
  agi_claim_does_not_count_as_formal_attestation: true
```
"""
    issues = preflight_check(text)
    formal = [i for i in issues if i["type"] == "ai-verification-cannot-count-formal"]
    assert len(formal) > 0, "Expected ai-verification-cannot-count-formal"
    print("✅ FAIL caught: AGI claim cannot count formal")


def test_agi_benchmark_asserted_pass():
    """PASS: agi_benchmark_asserted with boundary."""
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
verifier_capability_claim: agi_benchmark_asserted
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
    print("✅ PASS: agi_benchmark_asserted with boundary")


def test_ordinary_ai_no_boundary_needed():
    """PASS: ordinary_ai does not require capability boundary."""
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
    boundary = [i for i in issues if i["type"] == "missing-agi-capability-boundary"]
    assert len(boundary) == 0, "ordinary_ai should not require capability boundary"
    print("✅ PASS: ordinary_ai no boundary needed")


def main():
    test_agi_claim_with_boundary_pass()
    test_agi_claim_without_boundary_fail()
    test_agi_claim_cannot_count_formal()
    test_agi_benchmark_asserted_pass()
    test_ordinary_ai_no_boundary_needed()
    print("\n✅ All AGI capability boundary tests passed!")


if __name__ == "__main__":
    main()
