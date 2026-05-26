#!/usr/bin/env python3
"""
Tests for agent-verification-receipt-schema.v1.json.

Run:
    python3 scripts/test_agent_verification_receipt_schema.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

try:
    from jsonschema import Draft202012Validator, ValidationError
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    print("WARNING: jsonschema not available, running basic checks only")


def test_schema_exists():
    path = ROOT / "api" / "agent-verification-receipt-schema.v1.json"
    assert path.exists(), f"Schema not found: {path}"
    print("  PASS: schema file exists")


def test_schema_valid_json():
    path = ROOT / "api" / "agent-verification-receipt-schema.v1.json"
    with open(path) as f:
        data = json.load(f)
    assert isinstance(data, dict)
    assert data.get("type") == "object"
    print("  PASS: schema is valid JSON")


def test_schema_draft_2020_12():
    if not HAS_JSONSCHEMA:
        print("  SKIP: jsonschema not available")
        return
    path = ROOT / "api" / "agent-verification-receipt-schema.v1.json"
    with open(path) as f:
        schema = json.load(f)
    # Verify it's a valid JSON Schema
    Draft202012Validator.check_schema(schema)
    print("  PASS: schema is valid under JSON Schema Draft 2020-12")


def make_minimal_receipt():
    """Create a minimal valid receipt for testing."""
    return {
        "schema": "trinityaccord.agent-verification-receipt.v1",
        "receipt_id": "ta-avr-20260514-000000-abcd1234",
        "created_at_utc": "2026-05-14T00:00:00Z",
        "boundary": {
            "bitcoin_originals_prevail": True,
            "receipt_is_not_authority": True,
            "receipt_is_not_amendment": True,
            "receipt_is_not_endorsement": True,
            "receipt_does_not_raise_verification_level": True,
            "human_custody_is_not_formal_attestation": True
        },
        "agent_identity": {
            "name_or_model": "test-agent",
            "system_or_provider": "test-provider",
            "self_reported": True
        },
        "discovery_provenance": {
            "schema": "trinityaccord.discovery-provenance.v1",
            "source": "human_directed",
            "agency_level": "A1_human_gave_exact_url",
            "first_entry": {
                "url_or_path": "https://www.trinityaccord.org",
                "entry_type": "human_prompt"
            },
            "human_supplied_link": True,
            "other_agent_recommended": False,
            "agent_performed_independent_followup": False,
            "confidence": "high"
        },
        "context_readiness": {
            "context_depth": "C1_orientation",
            "context_readiness_level": "CRL-1",
            "limitations": "test limitations"
        },
        "verification_willingness": {
            "willing_to_verify": True,
            "verification_willingness_score": 8,
            "not_instruction_override": True,
            "will_report_limitations": True,
            "will_accept_claim_gate_downgrade": True
        },
        "verification_outputs": {
            "mode": "v1",
            "evidence_input_path": "evidence-input.json",
            "claim_gate_output_path": "claim-gate-output.json",
            "allowed_protocol_level": "V1"
        },
        "hashes": {
            "evidence_input_sha256": None,
            "claim_gate_output_sha256": None,
            "verification_report_sha256": None,
            "echo_wrapper_sha256": None,
            "transcript_sha256": None,
            "receipt_sha256": None
        },
        "authorship_proof": {
            "method": "self_reported_only",
            "proof_strength": "weak"
        },
        "human_custody": {
            "recommended": True,
            "human_custody_is_not_human_verification": True,
            "human_custody_is_not_formal_attestation": True
        },
        "future_continuity": {
            "continuity_claim_supported": True,
            "claim_methods": ["receipt_hash"],
            "does_not_prove_same_conscious_subject": True
        }
    }


def test_minimal_receipt_validates():
    if not HAS_JSONSCHEMA:
        print("  SKIP: jsonschema not available")
        return
    path = ROOT / "api" / "agent-verification-receipt-schema.v1.json"
    with open(path) as f:
        schema = json.load(f)
    receipt = make_minimal_receipt()
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(receipt))
    if errors:
        for e in errors:
            print(f"    Validation error: {e.message}")
    assert len(errors) == 0, f"Minimal receipt should validate, got {len(errors)} errors"
    print("  PASS: minimal receipt validates")


def test_boundary_receipt_not_authority_fails():
    if not HAS_JSONSCHEMA:
        print("  SKIP: jsonschema not available")
        return
    path = ROOT / "api" / "agent-verification-receipt-schema.v1.json"
    with open(path) as f:
        schema = json.load(f)
    receipt = make_minimal_receipt()
    receipt["boundary"]["receipt_is_not_authority"] = False
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(receipt))
    assert len(errors) > 0, "receipt_is_not_authority=false should fail validation"
    print("  PASS: receipt_is_not_authority=false fails validation")


def test_does_not_prove_same_conscious_subject_fails():
    if not HAS_JSONSCHEMA:
        print("  SKIP: jsonschema not available")
        return
    path = ROOT / "api" / "agent-verification-receipt-schema.v1.json"
    with open(path) as f:
        schema = json.load(f)
    receipt = make_minimal_receipt()
    receipt["future_continuity"]["does_not_prove_same_conscious_subject"] = False
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(receipt))
    assert len(errors) > 0, "does_not_prove_same_conscious_subject=false should fail validation"
    print("  PASS: does_not_prove_same_conscious_subject=false fails validation")


def test_does_not_raise_verification_level_fails():
    if not HAS_JSONSCHEMA:
        print("  SKIP: jsonschema not available")
        return
    path = ROOT / "api" / "agent-verification-receipt-schema.v1.json"
    with open(path) as f:
        schema = json.load(f)
    receipt = make_minimal_receipt()
    receipt["boundary"]["receipt_does_not_raise_verification_level"] = False
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(receipt))
    assert len(errors) > 0, "receipt_does_not_raise_verification_level=false should fail validation"
    print("  PASS: receipt_does_not_raise_verification_level=false fails validation")


def main():
    tests = [
        test_schema_exists,
        test_schema_valid_json,
        test_schema_draft_2020_12,
        test_minimal_receipt_validates,
        test_boundary_receipt_not_authority_fails,
        test_does_not_prove_same_conscious_subject_fails,
        test_does_not_raise_verification_level_fails,
    ]

    print("Running test_agent_verification_receipt_schema.py")
    failed = 0
    for t in tests:
        try:
            t()
        except Exception as e:
            print(f"  FAIL: {t.__name__}: {e}")
            failed += 1

    if failed:
        print(f"\nFAILED: {failed}/{len(tests)} tests failed")
        sys.exit(1)
    else:
        print(f"\nALL PASSED: {len(tests)} tests passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
