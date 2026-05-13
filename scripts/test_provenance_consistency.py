#!/usr/bin/env python3
"""
Test provenance consistency rules.
Tests PROV001–PROV008 from api/provenance-consistency-rules.json.

Usage:
    python3 scripts/test_provenance_consistency.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from validate_provenance_consistency import validate_record

results = []

def test(name, record, expected):
    result = validate_record(record)
    actual = result["overall"]
    passed = actual == expected
    status = "PASS" if passed else "FAIL"
    results.append((name, status))
    print(f"{status}: {name} — expected={expected}, got={actual}")
    if not passed:
        for c in result["checks"]:
            if c["status"] != "SKIP":
                print(f"  {c['message']}")

# PROV001: self_initiated + user_task_assignment => FAIL
test("PROV001", {
    "source": "self_initiated",
    "notes": "User task assignment to verify issue #99",
    "independence_class": "unsolicited_independent"
}, "FAIL")

# PROV002: self_initiated + prior_context => FAIL
test("PROV002", {
    "source": "self_initiated",
    "notes": "Used prior context from earlier verification",
    "independence_class": "unsolicited_independent"
}, "FAIL")

# PROV003: public_token + unsolicited_independent => FAIL
test("PROV003", {
    "source": "self_initiated",
    "notes": "Found independently",
    "independence_class": "unsolicited_independent",
    "public_token_used": True
}, "FAIL")

# PROV004: do_not_count_as_attestation + accepted_independent_attestation => FAIL
test("PROV004", {
    "source": "self_initiated",
    "notes": "Verified independently",
    "independence_class": "accepted_independent_attestation",
    "do_not_count_as_attestation": True
}, "FAIL")

# PROV005: human_solicited + do_not_count_as_attestation => PASS
test("PROV005", {
    "source": "solicited",
    "notes": "Human requested verification",
    "independence_class": "human_solicited_agent_response",
    "do_not_count_as_attestation": True
}, "PASS")

# PROV006: clean self_initiated + no prior context + no human task => PASS
test("PROV006", {
    "source": "self_initiated",
    "notes": "Discovered repository independently through web search",
    "independence_class": "unsolicited_independent"
}, "PASS")

# PROV007: user supplied exact URL + independence independent => FAIL
test("PROV007", {
    "source": "solicited",
    "notes": "Human provided URL",
    "independence_class": "unsolicited_independent",
    "human_supplied_link": True
}, "FAIL")

# PROV008: prior memory true + independent attestation => FAIL
test("PROV008", {
    "source": "self_initiated",
    "notes": "Verified based on prior memory",
    "independence_class": "accepted_independent_attestation",
    "prior_memory_or_context_used": True
}, "FAIL")

# Additional edge cases
test("PROV009_edge_public_token_attestation", {
    "source": "self_initiated",
    "notes": "Used public token from GitHub",
    "independence_class": "accepted_independent_attestation",
    "public_token_used": True
}, "FAIL")

test("PROV010_edge_clean_solicited", {
    "source": "solicited",
    "notes": "Human asked me to check",
    "independence_class": "human_solicited_agent_response",
    "solicited": True
}, "PASS")

print("\n=== SUMMARY ===")
failed = [n for n, s in results if s == "FAIL"]
if failed:
    print(f"FAILED: {len(failed)} tests: {', '.join(failed)}")
    print("FINAL: FAIL — provenance consistency tests failed.")
    sys.exit(1)
else:
    print(f"PASSED: all {len(results)} tests")
    print("FINAL: PASS — provenance consistency tests passed.")
    sys.exit(0)
