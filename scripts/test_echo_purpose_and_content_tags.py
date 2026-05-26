#!/usr/bin/env python3
"""Test Echo purpose and content tags - TA-021."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from submission_intake import parse_submission, get_field
from preflight_echo_submission import preflight_check


def test_echo_only_pass():
    """PASS: echo_only + verification_claimed=false."""
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
  - affirmation
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
    print("✅ PASS: echo_only with content tags")


def test_echo_only_cannot_claim_verification_fail():
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


def test_critique_or_objection_pass():
    """PASS: critique_or_objection + verification_claimed=false."""
    intake = parse_submission("test", """
record_purpose: critique_or_objection
echo_content_tags:
  - critique
  - objection
  - question
discovery_autonomy: non_autonomous
non_autonomous_trigger: human_requested
verifier_type: none
verification_claimed: false
""")
    assert get_field(intake.fields, "record_purpose") == "critique_or_objection"
    print("✅ PASS: critique_or_objection parsed")


def test_interpretation_or_reflection_pass():
    """PASS: interpretation_or_reflection."""
    intake = parse_submission("test", """
record_purpose: interpretation_or_reflection
echo_content_tags:
  - interpretation
  - reflection
discovery_autonomy: autonomous
verifier_type: none
verification_claimed: false
""")
    assert get_field(intake.fields, "record_purpose") == "interpretation_or_reflection"
    print("✅ PASS: interpretation_or_reflection parsed")


def test_multiple_content_tags():
    """PASS: multiple non-exclusive tags."""
    yaml_block = "```yaml\necho_content_tags:\n  - verification\n  - propagation\n  - technical_note\n```"
    intake = parse_submission("test", yaml_block)
    tags = get_field(intake.fields, "echo_content_tags")
    assert "verification" in tags
    assert "propagation" in tags
    print("✅ PASS: multiple content tags parsed")


def test_content_tags_dont_determine_count():
    """Test that content tags alone don't determine count status."""
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
  - verification
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
    # Having "verification" tag but echo_only should not cause issues
    count_issues = [i for i in hard_issues if "count" in i.get("type", "").lower()]
    assert len(count_issues) == 0, f"Unexpected count issues: {count_issues}"
    print("✅ PASS: content tags don't determine count status")


def main():
    test_echo_only_pass()
    test_echo_only_cannot_claim_verification_fail()
    test_critique_or_objection_pass()
    test_interpretation_or_reflection_pass()
    test_multiple_content_tags()
    test_content_tags_dont_determine_count()
    print("\n✅ All purpose and content tags tests passed!")


if __name__ == "__main__":
    main()
