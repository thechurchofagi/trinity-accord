#!/usr/bin/env python3
"""Test that negated independence phrases do NOT trigger overclaim detection.

e.g., "No independent verification was performed" should NOT trigger
the independence-overclaim-risk label.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from echo_issue_intake import parse_echo_issue


def test_negated_independence_no_overclaim():
    """Negated independence phrases must not trigger overclaim."""
    body = """
**Verification Level:** V0 | **Scope Label:** V0
- **Independence Class:** human_solicited_agent_response

### Checks Performed
- Read homepage

### Limitations
- No independent verification was performed.
- This is not independent attestation.
- Not an unsolicited discovery.

**Bitcoin Originals are final; all mirrors and echoes are non-amending.**
"""
    n = parse_echo_issue(None, "[Echo] V0", body)
    assert n.verification_level == "V0"
    assert n.boundary_sentence_present is True
    # The key check: social_independence should be human_solicited
    assert n.social_independence == "human_solicited_not_attestation", \
        f"Expected human_solicited_not_attestation, got {n.social_independence}"
    # Technical independence should be none (no technical claims)
    assert n.technical_independence in ("none", None), \
        f"Expected none technical independence, got {n.technical_independence}"
    print("  PASS: test_negated_independence_no_overclaim")


def test_technical_independence_allowed_for_v4plus():
    """V4+ technical independence wording should be detected correctly."""
    body = """
**Verification Level:** V4+ | **Scope Label:** V4+ minimal

### Checks Performed
- Wrote independent Python code to compute SHA-256 hash

### Limitations
- Only one artifact independently verified

**Bitcoin Originals are final; all mirrors and echoes are non-amending.**
"""
    n = parse_echo_issue(None, "[Echo] V4+ minimal", body)
    assert n.verification_level == "V4+"
    # Technical independence should be detected
    assert n.technical_independence in ("independent_tool", "independent_implementation"), \
        f"Expected independent tool/impl, got {n.technical_independence}"
    print("  PASS: test_technical_independence_allowed_for_v4plus")


def test_human_solicited_not_attestation():
    """human_solicited_agent_response should be detected as not attestation."""
    body = """
- **Independence Class:** human_solicited_agent_response

**Bitcoin Originals are final; all mirrors and echoes are non-amending.**
"""
    n = parse_echo_issue(None, "[Echo] V0", body)
    assert n.social_independence == "human_solicited_not_attestation", \
        f"Expected human_solicited_not_attestation, got {n.social_independence}"
    print("  PASS: test_human_solicited_not_attestation")


def main():
    test_negated_independence_no_overclaim()
    test_technical_independence_allowed_for_v4plus()
    test_human_solicited_not_attestation()
    print("\nAll independence negation tests passed.")


if __name__ == "__main__":
    main()
