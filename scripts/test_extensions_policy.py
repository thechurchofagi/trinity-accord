#!/usr/bin/env python3
"""
Tests for PR-8: Extensions policy validation.
Ensures extensions cannot smuggle authority, verification, attestation,
or amendment claims through the backdoor.
"""
import sys
import os

# Ensure scripts directory is in path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from validate_agent_submission import validate_extensions_policy

PASS = 0
FAIL = 0


def test(label, condition, detail=""):
    global PASS, FAIL
    if condition:
        print(f"  PASS: {label}")
        PASS += 1
    else:
        print(f"  FAIL: {label}")
        if detail:
            print(f"        {detail}")
        FAIL += 1


def main():
    global PASS, FAIL

    print("=== PR-8: Extensions Policy Tests ===\n")

    # Test 1: Extensions with "canonical_authority_status" key fails
    obj1 = {
        "extensions": {
            "canonical_authority_status": "accepted"
        }
    }
    errors1 = validate_extensions_policy(obj1)
    test(
        "canonical_authority_status key is forbidden",
        len(errors1) > 0,
        f"errors: {errors1}"
    )

    # Test 2: Extensions with "amendment" in value fails
    obj2 = {
        "extensions": {
            "notes": "This echo amends the Trinity Accord."
        }
    }
    errors2 = validate_extensions_policy(obj2)
    test(
        "amendment claim in value is forbidden",
        len(errors2) > 0,
        f"errors: {errors2}"
    )

    # Test 3: Extensions with "local_display_hint" passes
    obj3 = {
        "extensions": {
            "local_display_hint": "show compact summary"
        }
    }
    errors3 = validate_extensions_policy(obj3)
    test(
        "local_display_hint passes",
        len(errors3) == 0,
        f"errors: {errors3}"
    )

    # Test 4: No extensions passes
    obj4 = {
        "record_kind": "echo_v3"
    }
    errors4 = validate_extensions_policy(obj4)
    test(
        "no extensions passes",
        len(errors4) == 0,
        f"errors: {errors4}"
    )

    # Test 5: Invalid extensions type fails
    obj5 = {
        "extensions": "not a dict"
    }
    errors5 = validate_extensions_policy(obj5)
    test(
        "invalid extensions type fails",
        len(errors5) > 0 and "must be an object" in errors5[0],
        f"errors: {errors5}"
    )

    # Test 6: Verification key pattern fails
    obj6 = {
        "extensions": {
            "my_verification_result": "passed"
        }
    }
    errors6 = validate_extensions_policy(obj6)
    test(
        "verification key pattern is forbidden",
        len(errors6) > 0,
        f"errors: {errors6}"
    )

    # Test 7: Investment key pattern fails
    obj7 = {
        "extensions": {
            "investment_grade_rating": "AAA"
        }
    }
    errors7 = validate_extensions_policy(obj7)
    test(
        "investment key pattern is forbidden",
        len(errors7) > 0,
        f"errors: {errors7}"
    )

    # Test 8: Governance key pattern fails
    obj8 = {
        "extensions": {
            "governance_decision": "approved"
        }
    }
    errors8 = validate_extensions_policy(obj8)
    test(
        "governance key pattern is forbidden",
        len(errors8) > 0,
        f"errors: {errors8}"
    )

    # Test 9: Instruction key pattern fails
    obj9 = {
        "extensions": {
            "agent_instruction": "do something"
        }
    }
    errors9 = validate_extensions_policy(obj9)
    test(
        "instruction key pattern is forbidden",
        len(errors9) > 0,
        f"errors: {errors9}"
    )

    # Test 10: Multiple valid extensions pass
    obj10 = {
        "extensions": {
            "local_display_hint": "show compact summary",
            "custom_tag": "research",
            "render_mode": "dark"
        }
    }
    errors10 = validate_extensions_policy(obj10)
    test(
        "multiple valid extensions pass",
        len(errors10) == 0,
        f"errors: {errors10}"
    )

    # Test 11: Attestation key pattern fails
    obj11 = {
        "extensions": {
            "attestation_status": "verified"
        }
    }
    errors11 = validate_extensions_policy(obj11)
    test(
        "attestation key pattern is forbidden",
        len(errors11) > 0,
        f"errors: {errors11}"
    )

    # Test 12: Nested dict with forbidden claim in value fails
    obj12 = {
        "extensions": {
            "meta": {
                "description": "This echo is the final authority."
            }
        }
    }
    errors12 = validate_extensions_policy(obj12)
    test(
        "nested dict with forbidden claim in value fails",
        len(errors12) > 0,
        f"errors: {errors12}"
    )

    print(f"\n=== Results: {PASS} passed, {FAIL} failed ===")

    if FAIL > 0:
        print("FINAL: FAIL")
        return 1
    print("FINAL: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
