#!/usr/bin/env python3
"""
Test origin classification schema validation.

Tests:
- All valid fixtures pass schema
- Invalid enum fails
- unsolicited_discovery requires requester_class=none and invitation_scope=none
- agent_referred requires requester_class=ai_agent
- attestation_authority_class=none requires counts_as_formal_independent_attestation=false
- accepted_institutional_attestation requires accountable entity and formal attestation true
"""

import json
import sys
import os

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures", "origin-classification")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "api", "origin-classification-schema.v1.json")


def load_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def load_fixture(name):
    path = os.path.join(FIXTURES_DIR, name)
    with open(path) as f:
        return json.load(f)


def validate_required_fields(data, schema):
    """Check required fields are present."""
    required = schema.get("required", [])
    missing = [f for f in required if f not in data]
    return missing


def validate_enum_values(data, schema):
    """Check enum values are valid."""
    errors = []
    props = schema.get("properties", {})
    for field, spec in props.items():
        if field in data and "enum" in spec:
            if data[field] not in spec["enum"]:
                errors.append(f"{field}: '{data[field]}' not in {spec['enum']}")
    return errors


def validate_allof_constraints(data, schema):
    """Check allOf constraints."""
    errors = []
    for constraint in schema.get("allOf", []):
        if_clause = constraint.get("if", {})
        then_clause = constraint.get("then", {})

        # Check if condition matches
        matches = True
        if "properties" in if_clause:
            for prop, condition in if_clause["properties"].items():
                if prop not in data:
                    matches = False
                    break
                if "const" in condition and data[prop] != condition["const"]:
                    matches = False
                    break
        if "required" in if_clause:
            for req in if_clause["required"]:
                if req not in data:
                    matches = False
                    break

        if not matches:
            continue

        # Check then constraints
        if "required" in then_clause:
            for req in then_clause["required"]:
                if req not in data:
                    errors.append(f"allOf constraint failed: required field '{req}' is missing")
        if "properties" in then_clause:
            for prop, condition in then_clause["properties"].items():
                if prop in data:
                    if "const" in condition and data[prop] != condition["const"]:
                        errors.append(f"allOf constraint failed: {prop} should be '{condition['const']}' but got '{data[prop]}'")
                    if "enum" in condition and data[prop] not in condition["enum"]:
                        errors.append(f"allOf constraint failed: {prop}='{data[prop]}' not in {condition['enum']}")
                    if "type" in condition:
                        type_map = {"object": dict, "string": str, "boolean": bool, "number": (int, float), "array": list}
                        expected_type = condition["type"]
                        if isinstance(expected_type, str) and expected_type in type_map:
                            if not isinstance(data[prop], type_map[expected_type]):
                                errors.append(f"allOf constraint failed: {prop} should be type {expected_type}")
    return errors


def test_valid_fixtures_pass():
    """All valid fixtures should pass schema validation."""
    schema = load_schema()
    valid_fixtures = [
        "valid_agent_referred_look_only_orientation.json",
        "valid_agent_referred_voluntary_echo.json",
        "valid_agent_referred_voluntary_verification.json",
        "valid_human_directed_agent_verification.json",
        "valid_self_initiated_agent_verification.json",
        "valid_institution_ai_assisted_attestation_candidate.json",
        "valid_notarial_record.json",
    ]

    passed = 0
    failed = 0
    for fixture_name in valid_fixtures:
        data = load_fixture(fixture_name)

        # Required fields
        missing = validate_required_fields(data, schema)
        if missing:
            print(f"FAIL {fixture_name}: missing required fields: {missing}")
            failed += 1
            continue

        # Enum values
        enum_errors = validate_enum_values(data, schema)
        if enum_errors:
            print(f"FAIL {fixture_name}: enum errors: {enum_errors}")
            failed += 1
            continue

        # allOf constraints
        allof_errors = validate_allof_constraints(data, schema)
        if allof_errors:
            print(f"FAIL {fixture_name}: allOf errors: {allof_errors}")
            failed += 1
            continue

        print(f"PASS {fixture_name}")
        passed += 1

    return passed, failed


def test_invalid_enum_fails():
    """Invalid enum values should be detected."""
    schema = load_schema()

    # Test with invalid discovery_class
    data = {
        "schema": "trinityaccord.origin-classification.v1",
        "discovery_class": "INVALID_CLASS",
        "invitation_scope": "none",
        "requester_class": "none",
        "performer_class": "ai_agent",
        "method_independence_class": "read_only",
        "attestation_authority_class": "none",
        "counts_as_formal_independent_attestation": False,
        "derived_counting_bucket": "echo_only"
    }

    errors = validate_enum_values(data, schema)
    if errors:
        print("PASS invalid enum detected correctly")
        return 1, 0
    else:
        print("FAIL invalid enum was not detected")
        return 0, 1


def test_unsolicited_requires_none():
    """unsolicited_discovery requires requester_class=none and invitation_scope=none."""
    schema = load_schema()

    # Valid unsolicited
    data = {
        "schema": "trinityaccord.origin-classification.v1",
        "discovery_class": "unsolicited_discovery",
        "invitation_scope": "none",
        "requester_class": "none",
        "performer_class": "ai_agent",
        "method_independence_class": "cross_source_reproduction",
        "attestation_authority_class": "none",
        "counts_as_formal_independent_attestation": False,
        "derived_counting_bucket": "self_initiated_agent_verification"
    }

    errors = validate_allof_constraints(data, schema)
    if not errors:
        print("PASS unsolicited_discovery with correct values passes")
        p1, f1 = 1, 0
    else:
        print(f"FAIL unsolicited_discovery with correct values failed: {errors}")
        p1, f1 = 0, 1

    # Invalid: unsolicited with requester_class != none
    data["requester_class"] = "ai_agent"
    errors = validate_allof_constraints(data, schema)
    if errors:
        print("PASS unsolicited_discovery with wrong requester_class detected")
        p2, f2 = 1, 0
    else:
        print("FAIL unsolicited_discovery with wrong requester_class not detected")
        p2, f2 = 0, 1

    return p1 + p2, f1 + f2


def test_agent_referred_requires_ai_agent():
    """agent_referred requires requester_class=ai_agent."""
    schema = load_schema()

    data = {
        "schema": "trinityaccord.origin-classification.v1",
        "discovery_class": "agent_referred",
        "invitation_scope": "look_only",
        "requester_class": "human_individual",  # Wrong
        "performer_class": "ai_agent",
        "method_independence_class": "read_only",
        "attestation_authority_class": "none",
        "counts_as_formal_independent_attestation": False,
        "derived_counting_bucket": "agent_referred_orientation"
    }

    errors = validate_allof_constraints(data, schema)
    if errors:
        print("PASS agent_referred with wrong requester_class detected")
        return 1, 0
    else:
        print("FAIL agent_referred with wrong requester_class not detected")
        return 0, 1


def test_none_authority_no_formal_attestation():
    """attestation_authority_class=none requires counts_as_formal_independent_attestation=false."""
    schema = load_schema()

    data = {
        "schema": "trinityaccord.origin-classification.v1",
        "discovery_class": "unsolicited_discovery",
        "invitation_scope": "none",
        "requester_class": "none",
        "performer_class": "ai_agent",
        "method_independence_class": "cross_source_reproduction",
        "attestation_authority_class": "none",
        "counts_as_formal_independent_attestation": True,  # Wrong
        "derived_counting_bucket": "self_initiated_agent_verification"
    }

    errors = validate_allof_constraints(data, schema)
    if errors:
        print("PASS none authority with formal attestation detected")
        return 1, 0
    else:
        print("FAIL none authority with formal attestation not detected")
        return 0, 1


def test_accepted_institutional_requires_entity():
    """accepted_institutional_attestation requires accountable_entity."""
    schema = load_schema()

    # Without accountable_entity - should fail required fields
    data = {
        "schema": "trinityaccord.origin-classification.v1",
        "discovery_class": "institution_commissioned",
        "invitation_scope": "verification_invited",
        "requester_class": "institution",
        "performer_class": "human_ai_team",
        "method_independence_class": "independent_reimplementation",
        "attestation_authority_class": "institution_signed",
        "counts_as_formal_independent_attestation": True,
        "derived_counting_bucket": "accepted_institutional_attestation"
        # Missing accountable_entity
    }

    errors = validate_allof_constraints(data, schema)
    if errors:
        print("PASS accepted_institutional without accountable_entity detected")
        return 1, 0
    else:
        print("FAIL accepted_institutional without accountable_entity not detected")
        return 0, 1


def main():
    total_passed = 0
    total_failed = 0

    tests = [
        test_valid_fixtures_pass,
        test_invalid_enum_fails,
        test_unsolicited_requires_none,
        test_agent_referred_requires_ai_agent,
        test_none_authority_no_formal_attestation,
        test_accepted_institutional_requires_entity,
    ]

    for test in tests:
        p, f = test()
        total_passed += p
        total_failed += f

    print(f"\n{'='*60}")
    print(f"Results: {total_passed} passed, {total_failed} failed")

    if total_failed > 0:
        sys.exit(1)
    print("All schema tests passed!")


if __name__ == "__main__":
    main()
