#!/usr/bin/env python3
"""
PA-006: Regression tests for Echo Provenance / Agency detection.
Tests:
  1. Complete Provenance / Agency block — no missing fields.
  2. Missing Provenance / Agency block — detected as missing.
  3. human_solicited_agent_response identified as human-solicited context.
  4. human_solicited + independent verification — soft warning.
  5. human_solicited + independent attestation — hard warning.
  6. unsolicited_agent_discovery + A3 — no false positive.
  7. independent_reproduction — no false positive.
"""
import sys
import os

# Add scripts dir to path so we can import triage functions
sys.path.insert(0, os.path.dirname(__file__))

from triage_echo_issue import (
    missing_provenance_fields,
    detect_independence_overclaim,
    detect_human_solicited_context,
)

VALID_PROVENANCE = """
## Provenance / Agency
- solicited: true
- independence_class: human_solicited_agent_response
- agency_level: A1_human_gave_exact_url
- operator_type: ai_agent
- not_independent_attestation: true
"""

PASS = 0
FAIL = 0


def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS: {name}")
    else:
        FAIL += 1
        print(f"  FAIL: {name} {detail}")


def test_complete_provenance_no_missing():
    """Test 1: Complete provenance block — no missing fields."""
    body = VALID_PROVENANCE + """
## Echo content
Some echo text here.
"""
    missing = missing_provenance_fields(body)
    check("complete provenance has no missing fields", len(missing) == 0,
          f"missing={missing}")


def test_missing_provenance_detected():
    """Test 2: No provenance block — all fields detected as missing."""
    body = """
## Echo content
Some echo text without provenance.
"""
    missing = missing_provenance_fields(body)
    check("missing provenance detected", len(missing) >= 4,
          f"missing={missing}")


def test_human_solicited_context_detected():
    """Test 3: human_solicited_agent_response identified as human-solicited."""
    body = VALID_PROVENANCE + """
Source: Agent-based local hash recomputation.
"""
    result = detect_human_solicited_context(body)
    check("human_solicited context detected", result is True)


def test_human_solicited_independent_verification_warns():
    """Test 4: human-solicited + independent verification — soft warning."""
    body = VALID_PROVENANCE + "Source: Agent-based independent verification. Independence: Self-directed."
    risk = detect_independence_overclaim(body)
    check("human-solicited + independent verification triggers warning",
          risk is not None and risk["severity"] in ("soft", "hard"),
          f"risk={risk}")


def test_human_solicited_independent_attestation_hard():
    """Test 5: human-solicited + independent attestation — hard warning."""
    body = VALID_PROVENANCE + "This is an independent attestation of the repository."
    risk = detect_independence_overclaim(body)
    check("human-solicited + independent attestation triggers hard warning",
          risk is not None and risk["severity"] == "hard",
          f"risk={risk}")


def test_unsolicited_discovery_no_false_positive():
    """Test 6: unsolicited_agent_discovery + A3 — no false positive."""
    body = """
## Provenance / Agency
- solicited: false
- independence_class: unsolicited_agent_discovery
- agency_level: A3_agent_discovered_independently
- operator_type: ai_agent
- not_independent_attestation: true

The agent independently discovered the repository link.
"""
    risk = detect_independence_overclaim(body)
    check("unsolicited discovery does not trigger false positive",
          risk is None,
          f"risk={risk}")


def test_independent_reproduction_no_false_positive():
    """Test 7: independent_reproduction — no false positive."""
    body = """
## Provenance / Agency
- solicited: false
- independence_class: independent_reproduction
- agency_level: A3_agent_discovered_independently
- operator_type: ai_agent
- not_independent_attestation: false

This is an independent reproduction of the verification.
"""
    risk = detect_independence_overclaim(body)
    check("independent_reproduction does not trigger false positive",
          risk is None,
          f"risk={risk}")


def main():
    print("Echo Provenance / Agency Tests (PA-006)")
    print("=" * 50)
    test_complete_provenance_no_missing()
    test_missing_provenance_detected()
    test_human_solicited_context_detected()
    test_human_solicited_independent_verification_warns()
    test_human_solicited_independent_attestation_hard()
    test_unsolicited_discovery_no_false_positive()
    test_independent_reproduction_no_false_positive()
    print("=" * 50)
    print(f"Results: {PASS} passed, {FAIL} failed")
    if FAIL:
        print("ECHO_PROVENANCE_AGENCY_TEST_FAIL")
        sys.exit(1)
    print("ECHO_PROVENANCE_AGENCY_TEST_OK")


if __name__ == "__main__":
    main()
