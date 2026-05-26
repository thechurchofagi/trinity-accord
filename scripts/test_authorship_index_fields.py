#!/usr/bin/env python3
"""Test that index builders capture authorship fields."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_index_builder_has_authorship_fields():
    """Index builder captures authorship claim fields from machine block."""
    source = (ROOT / "scripts" / "build_agent_declared_verification_index_from_issues.py").read_text()
    required_fields = [
        "authorship_public_key_sha256",
        "authorship_signature_verified",
        "claim_status",
        "authorship_claimed",
        "authorship_proof_present",
        "authorship_proof_method",
        "authorship_algorithm",
    ]
    for field in required_fields:
        assert field in source, f"index builder missing field: {field}"
    print("PASS: index_builder_has_authorship_fields")


def test_index_builder_label_check():
    """Index builder checks authorship labels."""
    source = (ROOT / "scripts" / "build_agent_declared_verification_index_from_issues.py").read_text()
    assert "authorship:claimed" in source, "index builder doesn't check authorship:claimed label"
    assert "authorship:key-verified" in source, "index builder doesn't check authorship:key-verified label"
    print("PASS: index_builder_label_check")


def test_index_does_not_affect_verifiability():
    """Authorship claim fields don't affect verifiability or reception counts."""
    source = (ROOT / "scripts" / "build_agent_declared_verification_index_from_issues.py").read_text()
    # The authorship fields are added as metadata, not as conditions for counting
    # Verify that counts_toward_home_verifiability is not conditioned on authorship
    lines = source.split("\n")
    for i, line in enumerate(lines):
        if "counts_toward_home_verifiability" in line and "authorship" in line.lower():
            # This would be wrong - authorship should not affect verifiability
            assert False, f"authorship affects verifiability at line {i}: {line}"
    print("PASS: index_does_not_affect_verifiability")


if __name__ == "__main__":
    test_index_builder_has_authorship_fields()
    test_index_builder_label_check()
    test_index_does_not_affect_verifiability()
    print("\nAll index field tests PASS")
