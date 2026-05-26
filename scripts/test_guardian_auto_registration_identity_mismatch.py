#!/usr/bin/env python3
"""Test Guardian auto-registration identity mismatch blocking."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from auto_register_guardian_from_gateway_issues import compare_identity_claims


def test_identity_match():
    source = {
        "human_claimed_name_sha256": "abc123",
        "agent_claimed_id_sha256": "def456",
        "guardian_id": "guardian_ed25519_abcd1234ef015678",
        "public_key_sha256": "abcd1234ef015678" * 4,
    }
    listing = {
        "human_claimed_name_sha256": "abc123",
        "agent_claimed_id_sha256": "def456",
        "guardian_id": "guardian_ed25519_abcd1234ef015678",
        "public_key_sha256": "abcd1234ef015678" * 4,
    }
    errors = compare_identity_claims(source, listing)
    assert errors == [], f"Expected no errors, got {errors}"
    print("PASS: test_identity_match")


def test_identity_mismatch():
    source = {
        "human_claimed_name_sha256": "abc123",
        "agent_claimed_id_sha256": "def456",
        "guardian_id": "guardian_ed25519_abcd1234ef015678",
        "public_key_sha256": "abcd1234ef015678" * 4,
    }
    listing = {
        "human_claimed_name_sha256": "abc123",
        "agent_claimed_id_sha256": "DIFFERENT",
        "guardian_id": "guardian_ed25519_abcd1234ef015678",
        "public_key_sha256": "abcd1234ef015678" * 4,
    }
    errors = compare_identity_claims(source, listing)
    assert len(errors) > 0, "Expected identity mismatch errors"
    assert any("agent_claimed_id_sha256" in e for e in errors), f"Expected agent_claimed_id mismatch: {errors}"
    print("PASS: test_identity_mismatch")


def test_identity_missing_fields_skipped():
    source = {
        "guardian_id": "guardian_ed25519_abcd1234ef015678",
        "public_key_sha256": "abcd1234ef015678" * 4,
    }
    listing = {
        "human_claimed_name_sha256": "abc123",
        "agent_claimed_id_sha256": "def456",
        "guardian_id": "guardian_ed25519_abcd1234ef015678",
        "public_key_sha256": "abcd1234ef015678" * 4,
    }
    errors = compare_identity_claims(source, listing)
    assert errors == [], f"Expected no errors when source fields missing: {errors}"
    print("PASS: test_identity_missing_fields_skipped")


if __name__ == "__main__":
    test_identity_match()
    test_identity_mismatch()
    test_identity_missing_fields_skipped()
