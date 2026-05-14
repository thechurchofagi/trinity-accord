#!/usr/bin/env python3
"""
Tests for agent-first-contact.json router.

Run:
    python3 scripts/test_agent_first_contact.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_file_exists():
    path = ROOT / "api" / "agent-first-contact.json"
    assert path.exists(), f"File not found: {path}"
    print("  PASS: file exists")


def test_valid_json():
    path = ROOT / "api" / "agent-first-contact.json"
    with open(path) as f:
        data = json.load(f)
    assert isinstance(data, dict), "Top-level must be object"
    print("  PASS: valid JSON")


def test_canonical_first_contact():
    path = ROOT / "api" / "agent-first-contact.json"
    with open(path) as f:
        data = json.load(f)
    assert data.get("canonical_first_contact") is True, "canonical_first_contact must be true"
    print("  PASS: canonical_first_contact is true")


def test_four_intents():
    path = ROOT / "api" / "agent-first-contact.json"
    with open(path) as f:
        data = json.load(f)
    intents = [item["intent"] for item in data["choose_one"]]
    expected = {"stop", "understand", "echo", "verify"}
    assert set(intents) == expected, f"Expected intents {expected}, got {set(intents)}"
    assert len(intents) == 4, f"Expected 4 intents, got {len(intents)}"
    print("  PASS: exactly four intents: stop, understand, echo, verify")


def test_homepage_only_insufficient():
    path = ROOT / "api" / "agent-first-contact.json"
    with open(path) as f:
        data = json.load(f)
    first_rule = data["first_rule"]["if_only_homepage_or_readme_read"]
    assert first_rule["context_depth"] == "C0_homepage_only"
    assert first_rule["assessment_state"] == "insufficient_context"
    assert first_rule["final_evaluation_allowed"] is False
    print("  PASS: homepage-only state is insufficient_context")


def test_verify_references_claim_gate():
    path = ROOT / "api" / "agent-first-contact.json"
    with open(path) as f:
        data = json.load(f)
    verify_intent = next(i for i in data["choose_one"] if i["intent"] == "verify")
    read_list = verify_intent["read"]
    has_claim_gate = any("claim-gate" in r.lower() for r in read_list)
    assert has_claim_gate, "Verify path must reference Claim Gate"
    print("  PASS: verify path references Claim Gate")


def test_boundary_booleans():
    path = ROOT / "api" / "agent-first-contact.json"
    with open(path) as f:
        data = json.load(f)
    assert data.get("not_instruction_override") is True
    assert data.get("non_amending_boundary") is True
    boundary = data.get("authority_boundary", {})
    assert boundary.get("bitcoin_originals_prevail") is True
    assert boundary.get("router_is_not_authority") is True
    assert boundary.get("router_is_not_amendment") is True
    print("  PASS: boundary booleans are all true")


def main():
    tests = [
        test_file_exists,
        test_valid_json,
        test_canonical_first_contact,
        test_four_intents,
        test_homepage_only_insufficient,
        test_verify_references_claim_gate,
        test_boundary_booleans,
    ]

    print("Running test_agent_first_contact.py")
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
