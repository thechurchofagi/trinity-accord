#!/usr/bin/env python3
"""Test echo-submission-field-guide.json exists and is valid - TA-021."""
from __future__ import annotations

import json
import os
import sys


def test_field_guide_exists():
    """Test that api/echo-submission-field-guide.json exists."""
    path = os.path.join(os.path.dirname(__file__), "..", "api", "echo-submission-field-guide.json")
    assert os.path.exists(path), f"Missing: {path}"
    print("✅ api/echo-submission-field-guide.json exists")


def test_field_guide_valid_json():
    """Test that the field guide is valid JSON."""
    path = os.path.join(os.path.dirname(__file__), "..", "api", "echo-submission-field-guide.json")
    with open(path) as f:
        data = json.load(f)
    assert "schema" in data
    assert data["schema"] == "trinity-accord.echo-submission-field-guide.v1"
    print("✅ Field guide is valid JSON with correct schema")


def test_field_guide_has_core_fields():
    """Test that all core fields are documented."""
    path = os.path.join(os.path.dirname(__file__), "..", "api", "echo-submission-field-guide.json")
    with open(path) as f:
        data = json.load(f)
    field_names = {f["field"] for f in data["fields"]}
    required_fields = {
        "record_purpose", "echo_content_tags", "discovery_autonomy",
        "non_autonomous_trigger", "verifier_type", "verifier_capability_claim",
        "verification_claimed", "verification_level",
        "fresh_actions_performed", "method_reproducible",
        "authority_boundary_preserved",
        "counts_as_ai_independent_verification",
        "counts_as_formal_human_institutional_attestation",
        "attribution_preference", "display_name", "identity_verification_level",
    }
    missing = required_fields - field_names
    assert not missing, f"Missing fields: {missing}"
    print(f"✅ All {len(required_fields)} core fields documented")


def test_field_guide_allowed_values_match():
    """Test that allowed values in field guide match preflight constants."""
    path = os.path.join(os.path.dirname(__file__), "..", "api", "echo-submission-field-guide.json")
    with open(path) as f:
        data = json.load(f)

    from derive_echo_provenance import (
        RECORD_PURPOSE, ECHO_CONTENT_TAGS, DISCOVERY_AUTONOMY,
        NON_AUTONOMOUS_TRIGGER, VERIFIER_TYPE, VERIFIER_CAPABILITY_CLAIM,
    )

    sets = data.get("allowed_values_sets", {})
    assert set(sets.get("record_purpose", [])) == RECORD_PURPOSE
    assert set(sets.get("echo_content_tags", [])) == ECHO_CONTENT_TAGS
    assert set(sets.get("discovery_autonomy", [])) == DISCOVERY_AUTONOMY
    assert set(sets.get("non_autonomous_trigger", [])) == NON_AUTONOMOUS_TRIGGER
    assert set(sets.get("verifier_type", [])) == VERIFIER_TYPE
    assert set(sets.get("verifier_capability_claim", [])) == VERIFIER_CAPABILITY_CLAIM
    print("✅ Allowed values in field guide match preflight constants")


def test_field_guide_counting_boundaries():
    """Test that counting boundaries are documented."""
    path = os.path.join(os.path.dirname(__file__), "..", "api", "echo-submission-field-guide.json")
    with open(path) as f:
        data = json.load(f)
    cb = data.get("counting_boundaries", {})
    assert "ai_independent_verification" in cb
    assert "formal_human_institutional_attestation" in cb
    assert "agi_claim" in cb
    assert "identity_contact_fields" in cb
    print("✅ Counting boundaries documented")


def main():
    test_field_guide_exists()
    test_field_guide_valid_json()
    test_field_guide_has_core_fields()
    test_field_guide_allowed_values_match()
    test_field_guide_counting_boundaries()
    print("\n✅ All field guide tests passed!")


if __name__ == "__main__":
    main()
