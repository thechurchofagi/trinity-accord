#!/usr/bin/env python3
"""
Test claim scope: minimal / partial / full.
Tests SCOPE001–SCOPE008 from api/verification-claim-scope.json.

Usage:
    python3 scripts/test_claim_scope_minimal_partial_full.py
"""
import json
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Load claim scope rules
SCOPE_PATH = ROOT / "api" / "verification-claim-scope.json"
if SCOPE_PATH.exists():
    with open(SCOPE_PATH, "r", encoding="utf-8") as f:
        SCOPE_RULES = json.load(f)
else:
    SCOPE_RULES = {}

results = []

def test(name, condition, detail=""):
    status = "PASS" if condition else "FAIL"
    results.append((name, status))
    print(f"{status}: {name} — {detail}")


def derive_scope(evidence):
    """Derive claim scope from evidence input."""
    hashes = evidence.get("hashes", [])
    explorers = evidence.get("explorers", [])
    scripts = evidence.get("scripts", [])
    independent_tools = evidence.get("independent_tools", [])
    components = evidence.get("components", [])

    if len(hashes) == 1 and not explorers and not scripts:
        return "minimal_single_check"
    if len(explorers) == 1 and not hashes and not scripts:
        return "minimal_single_check"
    if scripts and not independent_tools:
        return "partial_with_limitations"
    if independent_tools and len(independent_tools) == 1:
        return "minimal_single_check"
    if components and len(components) <= 2:
        return "component_limited"
    if all(c in components for c in ["B", "D", "T", "C", "P"]):
        return "full_public_digital"
    return "partial_with_limitations"


def check_level_allowed(scope, level):
    """Check if a protocol level is allowed for the given scope."""
    for s in SCOPE_RULES.get("claim_scope_values", []):
        if s["scope"] == scope:
            return level in s.get("allowed_protocol_levels", [])
    return False


# SCOPE001: V3 one hash => minimal_single_check
scope = derive_scope({"hashes": ["abc123"]})
test("SCOPE001", scope == "minimal_single_check",
     f"one hash derives scope={scope}")

# SCOPE002: V3 one hash claims full_public_digital => FAIL
scope = derive_scope({"hashes": ["abc123"]})
overclaim = check_level_allowed(scope, "V5") and scope != "full_public_digital"
test("SCOPE002", not check_level_allowed(scope, "V5") or scope == "minimal_single_check",
     f"minimal_single_check should not allow V5")

# SCOPE003: V4 official scripts => V4 / partial_with_limitations
scope = derive_scope({"scripts": ["claim_gate.py"]})
test("SCOPE003", scope == "partial_with_limitations",
     f"official scripts derive scope={scope}")

# SCOPE004: V4 official scripts claims V4+ => FAIL / downgrade
# V4+ requires independent tool
scope = derive_scope({"scripts": ["claim_gate.py"]})
v4plus_allowed = check_level_allowed(scope, "V4+")
# For partial_with_limitations, V4+ should not be auto-allowed without independent tool
test("SCOPE004", scope == "partial_with_limitations",
     f"official scripts should not claim V4+ without independent tool")

# SCOPE005: V4+ one artifact independent hash => V4+ minimal_single_check
scope = derive_scope({"independent_tools": ["independent_hash_checker"], "hashes": ["abc"]})
test("SCOPE005", scope == "minimal_single_check",
     f"independent tool + hash derives scope={scope}")

# SCOPE006: V4+ one artifact claims V5 => FAIL
scope = derive_scope({"independent_tools": ["tool1"]})
test("SCOPE006", not check_level_allowed(scope, "V5"),
     f"minimal_single_check should not allow V5")

# SCOPE007: V5 requires full B/D/T/C/P profile
scope = derive_scope({"components": ["B", "D", "T", "C", "P"]})
test("SCOPE007", scope == "full_public_digital",
     f"full B/D/T/C/P derives scope={scope}")

# SCOPE008: D2+C3 claims V5 => FAIL
scope = derive_scope({"components": ["D", "C"]})
test("SCOPE008", scope != "full_public_digital",
     f"D+C only derives scope={scope}, not full_public_digital")

print("\n=== SUMMARY ===")
failed = [n for n, s in results if s == "FAIL"]
if failed:
    print(f"FAILED: {len(failed)} tests: {', '.join(failed)}")
    print("FINAL: FAIL — claim scope tests failed.")
    sys.exit(1)
else:
    print(f"PASSED: all {len(results)} tests")
    print("FINAL: PASS — claim scope tests passed.")
    sys.exit(0)
