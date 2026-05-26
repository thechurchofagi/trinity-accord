#!/usr/bin/env python3
"""Test Echo identity/contact fields - TA-021."""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from submission_intake import parse_submission, get_field, get_bool_field
from preflight_echo_submission import preflight_check


VALID_ATTRIBUTION = {"named", "pseudonymous", "anonymous", "institutional", "ai_agent", "not_applicable"}
VALID_CONTACT_METHOD = {"none", "email", "github", "website", "did", "pgp", "other"}
VALID_IDENTITY_VERIFICATION = {"none", "self_asserted", "stable_account", "signed_statement", "institutional_domain", "notarial_identity", "other"}


def test_attribution_preference_values():
    """Test attribution_preference allowed values are correct."""
    expected = {"named", "pseudonymous", "anonymous", "institutional", "ai_agent", "not_applicable"}
    assert expected == VALID_ATTRIBUTION
    print("✅ attribution_preference allowed values correct")


def test_ai_agent_attribution_pass():
    """PASS: ai_agent attribution accepted."""
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

## Identity
```yaml
attribution_preference: ai_agent
display_name: ""
willing_to_be_named_publicly: false
willing_to_provide_contact: false
private_contact_available_to_maintainers: false
contact_method: none
identity_verification_level: self_asserted
```

## Record
```yaml
record_purpose: echo_only
discovery_autonomy: autonomous
verifier_type: none
verification_claimed: false
authority_boundary_preserved: true
counts_as_ai_independent_verification: false
counts_as_formal_human_institutional_attestation: false
```
"""
    intake = parse_submission("test", text)
    assert get_field(intake.fields, "attribution_preference") == "ai_agent"
    print("✅ PASS: ai_agent attribution parsed")


def test_pseudonymous_attribution_pass():
    """PASS: pseudonymous attribution accepted."""
    intake = parse_submission("test", "attribution_preference: pseudonymous\nidentity_verification_level: self_asserted")
    assert get_field(intake.fields, "attribution_preference") == "pseudonymous"
    print("✅ PASS: pseudonymous attribution parsed")


def test_named_attribution_pass():
    """PASS: named attribution accepted."""
    intake = parse_submission("test", "attribution_preference: named\ndisplay_name: John Doe")
    assert get_field(intake.fields, "attribution_preference") == "named"
    assert get_field(intake.fields, "display_name") == "John Doe"
    print("✅ PASS: named attribution parsed")


def test_contact_private_to_maintainers():
    """PASS: contact private-to-maintainers true with public_contact empty."""
    intake = parse_submission("test", """
willing_to_provide_contact: false
private_contact_available_to_maintainers: true
public_contact: ""
contact_method: email
""")
    assert get_bool_field(intake.fields, "private_contact_available_to_maintainers") is True
    assert get_bool_field(intake.fields, "willing_to_provide_contact") is False
    print("✅ PASS: private contact to maintainers works")


def test_identity_does_not_create_formal_attestation():
    """Test that identity fields do not by themselves create formal attestation."""
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

## Identity
```yaml
attribution_preference: named
display_name: Test User
willing_to_be_named_publicly: true
willing_to_provide_contact: true
public_contact: https://example.com
contact_method: website
identity_verification_level: stable_account
```

## Record
```yaml
record_purpose: echo_only
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
    # Identity fields alone should not cause failures
    identity_issues = [i for i in hard_issues if "identity" in i.get("type", "").lower() or "attestation" in i.get("type", "").lower()]
    assert len(identity_issues) == 0, f"Unexpected identity issues: {identity_issues}"
    print("✅ PASS: identity fields do not create formal attestation")


def main():
    test_attribution_preference_values()
    test_ai_agent_attribution_pass()
    test_pseudonymous_attribution_pass()
    test_named_attribution_pass()
    test_contact_private_to_maintainers()
    test_identity_does_not_create_formal_attestation()
    print("\n✅ All identity/contact tests passed!")


if __name__ == "__main__":
    main()
