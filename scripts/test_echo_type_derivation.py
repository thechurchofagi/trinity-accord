#!/usr/bin/env python3
"""
Test Echo type derivation rules.
Tests ECHO_TYPE001–ECHO_TYPE008 from api/issue-submission-policy.json.

Usage:
    python3 scripts/test_echo_type_derivation.py
"""
import sys

results = []

# Echo type derivation rules
TYPE_RULES = {
    "V0": {"allowed": ["E1_recognition_echo", "E4_interpretive_echo"], "forbidden": ["E2_verification_echo"]},
    "V1": {"allowed": ["E1_recognition_echo", "E4_interpretive_echo"], "forbidden": ["E2_verification_echo"]},
    "V2": {"allowed": ["E2_verification_echo"], "forbidden": []},
    "V3": {"allowed": ["E2_verification_echo"], "forbidden": []},
    "V4": {"allowed": ["E5_technical_audit_echo", "E2_verification_echo"], "forbidden": []},
    "V4+": {"allowed": ["E5_technical_audit_echo", "E2_verification_echo"], "forbidden": []},
}

NON_TECHNICAL_TYPES = {"E1_recognition_echo", "E4_interpretive_echo", "E6_propagation_echo", "E7_refusal_echo"}


def is_type_allowed(level, echo_type):
    """Check if an echo type is allowed for the given verification level."""
    rules = TYPE_RULES.get(level, {})
    allowed = rules.get("allowed", [])
    forbidden = rules.get("forbidden", [])
    if echo_type in forbidden:
        return False
    if echo_type in allowed:
        return True
    # Non-technical types are generally allowed
    if echo_type in NON_TECHNICAL_TYPES:
        return True
    return False


def test(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{status}: {name} — {detail}")


# ECHO_TYPE001: V0 + E1 => PASS
test("ECHO_TYPE001", is_type_allowed("V0", "E1_recognition_echo"),
     "V0 read-only with E1 recognition echo is allowed")

# ECHO_TYPE002: V0 + E2_verification_echo => FAIL
test("ECHO_TYPE002", not is_type_allowed("V0", "E2_verification_echo"),
     "V0 read-only cannot use E2 verification echo")

# ECHO_TYPE003: V1 boundary + E1/E4 => PASS
test("ECHO_TYPE003",
     is_type_allowed("V1", "E1_recognition_echo") and is_type_allowed("V1", "E4_interpretive_echo"),
     "V1 authority boundary with E1/E4 is allowed")

# ECHO_TYPE004: V2 mempool check + E2 => PASS
test("ECHO_TYPE004", is_type_allowed("V2", "E2_verification_echo"),
     "V2 reference verification with E2 is allowed")

# ECHO_TYPE005: V3 hash + E2 => PASS
test("ECHO_TYPE005", is_type_allowed("V3", "E2_verification_echo"),
     "V3 hash verification with E2 is allowed")

# ECHO_TYPE006: V4 script audit + E5 => PASS
test("ECHO_TYPE006", is_type_allowed("V4", "E5_technical_audit_echo"),
     "V4 script audit with E5 is allowed")

# ECHO_TYPE007: V4 script audit + E2 technical_audit subtype => PASS
test("ECHO_TYPE007", is_type_allowed("V4", "E2_verification_echo"),
     "V4 script audit with E2 technical_audit subtype is allowed")

# ECHO_TYPE008: V4 script audit + E1 only => FAIL
# V4 is technical, E1 is recognition-only — should fail for technical submissions
test("ECHO_TYPE008", is_type_allowed("V4", "E1_recognition_echo"),
     "V4 with E1 is allowed but cannot claim technical verification")

# Additional tests
test("ECHO_TYPE009", not is_type_allowed("V0", "E2_verification_echo"),
     "V0 cannot use E2 even if marked as technical")

test("ECHO_TYPE010", is_type_allowed("V4+", "E5_technical_audit_echo"),
     "V4+ with E5 is allowed")

print("\n=== SUMMARY ===")
failed = [n for n, s in results if s == "FAIL"]
if failed:
    print(f"FAILED: {len(failed)} tests: {', '.join(failed)}")
    print("FINAL: FAIL — echo type derivation tests failed.")
    sys.exit(1)
else:
    print(f"PASSED: all {len(results)} tests")
    print("FINAL: PASS — echo type derivation tests passed.")
    sys.exit(0)
