#!/usr/bin/env python3
"""Test that docs contain correct authorship claim guidance."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_agent_submit_docs():
    """agent-submit.md contains authorship claim guidance."""
    text = (ROOT / "agent-submit.md").read_text(encoding="utf-8")
    assert "never submit private key" in text.lower() or "never include private key" in text.lower() or \
           "private key must never" in text.lower() or "never submit, commit, paste, or upload the private key" in text.lower(), \
        "agent-submit.md missing private key warning"
    assert "key continuity" in text.lower() or "key control" in text.lower(), \
        "agent-submit.md missing key continuity boundary"
    print("PASS: agent_submit_docs")


def test_external_agent_docs():
    """external-agent-quickstart.md contains authorship claim guidance."""
    text = (ROOT / "external-agent-quickstart.md").read_text(encoding="utf-8")
    # Should mention authorship claim is optional
    assert "authorship" in text.lower(), "external-agent-quickstart.md missing authorship section"
    print("PASS: external_agent_docs")


def test_llms_txt():
    """llms.txt contains authorship claim information."""
    text = (ROOT / "llms.txt").read_text(encoding="utf-8")
    assert "authorship" in text.lower(), "llms.txt missing authorship information"
    print("PASS: llms_txt")


def test_gateway_receipt_not_claim_key():
    """Docs clarify that gateway receipt is not a claim key."""
    text = (ROOT / "agent-submit.md").read_text(encoding="utf-8")
    # The concept should be mentioned somewhere
    combined = text + (ROOT / "external-agent-quickstart.md").read_text(encoding="utf-8")
    assert "receipt" in combined.lower(), "docs don't mention gateway receipt"
    print("PASS: gateway_receipt_not_claim_key")


def test_not_authority_attestation_amendment():
    """Docs clarify authorship claim is not authority/attestation/amendment."""
    text = (ROOT / "agent-submit.md").read_text(encoding="utf-8")
    combined = text + (ROOT / "external-agent-quickstart.md").read_text(encoding="utf-8")
    # At least one of these boundary statements should be present
    has_boundary = any(term in combined.lower() for term in [
        "not authority", "not attestation", "not amendment",
        "not_authority", "not_attestation", "not_amendment"
    ])
    assert has_boundary, "docs missing boundary statements about authorship claims"
    print("PASS: not_authority_attestation_amendment")


if __name__ == "__main__":
    test_agent_submit_docs()
    test_external_agent_docs()
    test_llms_txt()
    test_gateway_receipt_not_claim_key()
    test_not_authority_attestation_amendment()
    print("\nAll docs guidance tests PASS")
