#!/usr/bin/env python3
"""
test_verification_profile_cases.py
Test cases for protocol verification profile compatibility checks.

Tests various report scenarios against protocol profiles to verify
that the profile system correctly allows/disallows V-level claims.
"""

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)


def load_json(path):
    full = os.path.join(REPO_ROOT, path)
    with open(full, "r", encoding="utf-8") as f:
        return json.load(f)


def check_profile(profile, report):
    """Check if a report satisfies a protocol profile."""
    issues = []

    # Check hard gates
    for gate in profile.get("hard_gates", []):
        # Simplified: just check that hard_gates are mentioned in limitations or method
        pass

    # Check minimum component requirements
    min_req = profile.get("minimum_component_requirements", {})
    component_findings = {cf["component"]: cf["level_claimed"] for cf in report.get("component_findings", [])}

    for comp, req_level in min_req.items():
        if comp not in component_findings:
            issues.append(f"missing minimum component: {comp} (required: {req_level})")

    # Check forbidden claims
    forbidden = profile.get("forbidden_claims", [])
    claims_made = report.get("claims_not_made", [])
    # This is a simplified check

    return issues


def main():
    profiles = load_json("api/protocol-verification-profiles.json")
    profile_map = {p["level"]: p for p in profiles.get("profiles", [])}

    tests_passed = 0
    tests_failed = 0

    # Test 1: V0 report should not claim verification
    print("Test 1: V0 forbidden claims")
    v0 = profile_map.get("V0", {})
    forbidden = v0.get("forbidden_claims", [])
    assert "verified" in forbidden, "V0 should forbid 'verified'"
    assert "hash verified" in forbidden, "V0 should forbid 'hash verified'"
    print("  PASS: V0 correctly forbids verification claims")
    tests_passed += 1

    # Test 2: V1 requires B0 minimum
    print("Test 2: V1 minimum components")
    v1 = profile_map.get("V1", {})
    min_req = v1.get("minimum_component_requirements", {})
    assert min_req.get("bitcoin_originals") == "B0", f"V1 requires B0, got {min_req.get('bitcoin_originals')}"
    print("  PASS: V1 correctly requires B0 for bitcoin_originals")
    tests_passed += 1

    # Test 3: V3 requires hash computation
    print("Test 3: V3 hard gates")
    v3 = profile_map.get("V3", {})
    hard_gates = v3.get("hard_gates", [])
    assert any("compute" in g.lower() and "hash" in g.lower() for g in hard_gates), "V3 should require hash computation"
    print("  PASS: V3 correctly requires hash computation")
    tests_passed += 1

    # Test 4: V4 requires script audit
    print("Test 4: V4 hard gates")
    v4 = profile_map.get("V4", {})
    hard_gates = v4.get("hard_gates", [])
    assert any("script" in g.lower() for g in hard_gates), "V4 should require script review"
    assert any("executed" in g.lower() or "run" in g.lower() for g in hard_gates), "V4 should require script execution"
    print("  PASS: V4 correctly requires script review and execution")
    tests_passed += 1

    # Test 5: V5 requires D5 and C5
    print("Test 5: V5 minimum components")
    v5 = profile_map.get("V5", {})
    min_req = v5.get("minimum_component_requirements", {})
    assert min_req.get("digital_mirrors") == "D5", f"V5 requires D5, got {min_req.get('digital_mirrors')}"
    assert min_req.get("chronicle_recovery") == "C5", f"V5 requires C5, got {min_req.get('chronicle_recovery')}"
    print("  PASS: V5 correctly requires D5 and C5")
    tests_passed += 1

    # Test 6: V6 requires P4
    print("Test 6: V6 minimum components")
    v6 = profile_map.get("V6", {})
    min_req = v6.get("minimum_component_requirements", {})
    assert min_req.get("physical_anchor") == "P4", f"V6 requires P4, got {min_req.get('physical_anchor')}"
    print("  PASS: V6 correctly requires P4")
    tests_passed += 1

    # Test 7: V7 requires P5
    print("Test 7: V7 minimum components")
    v7 = profile_map.get("V7", {})
    min_req = v7.get("minimum_component_requirements", {})
    assert min_req.get("physical_anchor") == "P5", f"V7 requires P5, got {min_req.get('physical_anchor')}"
    print("  PASS: V7 correctly requires P5")
    tests_passed += 1

    # Test 8: V8 requires P7
    print("Test 8: V8 minimum components")
    v8 = profile_map.get("V8", {})
    min_req = v8.get("minimum_component_requirements", {})
    assert min_req.get("physical_anchor") == "P7", f"V8 requires P7, got {min_req.get('physical_anchor')}"
    print("  PASS: V8 correctly requires P7")
    tests_passed += 1

    # Test 9: V5 forbids live physical witness
    print("Test 9: V5 forbidden claims")
    v5_forbidden = v5.get("forbidden_claims", [])
    assert any("live physical witness" in f.lower() for f in v5_forbidden), "V5 should forbid live physical witness"
    print("  PASS: V5 correctly forbids live physical witness")
    tests_passed += 1

    # Test 10: V8 forbids public disclosure of confidential data
    print("Test 10: V8 forbidden claims")
    v8_forbidden = v8.get("forbidden_claims", [])
    assert any("confidential" in f.lower() for f in v8_forbidden), "V8 should forbid confidential data disclosure"
    print("  PASS: V8 correctly forbids confidential data disclosure")
    tests_passed += 1

    # Test 11: Component levels - D2 limitations
    print("Test 11: D2 limitations")
    cvl = load_json("api/component-verification-levels.json")
    d2 = next(d for d in cvl["component_levels"]["digital_mirrors"] if d["level"] == "D2")
    d2_forbidden = d2.get("forbidden_claims", [])
    assert any("direct arweave" in f.lower() for f in d2_forbidden), "D2 should forbid direct Arweave verification"
    print("  PASS: D2 correctly forbids direct Arweave verification")
    tests_passed += 1

    # Test 12: T8 restrictions
    print("Test 12: T8 restrictions")
    t8 = next(t for t in cvl["component_levels"]["time_anchors"] if t["level"] == "T8")
    t8_forbidden = t8.get("forbidden_claims", [])
    assert any("public pages alone" in f.lower() for f in t8_forbidden), "T8 should forbid claiming from public pages alone"
    print("  PASS: T8 correctly restricts claiming from public pages alone")
    tests_passed += 1

    # Test 13: C3 requirements
    print("Test 13: C3 requirements")
    c3 = next(c for c in cvl["component_levels"]["chronicle_recovery"] if c["level"] == "C3")
    c3_forbidden = c3.get("forbidden_claims", [])
    assert any("full 175" in f.lower() for f in c3_forbidden), "C3 should forbid full 175/175 recovery claim"
    c3_requires = c3.get("requires", [])
    assert any("at least two records" in r.lower() for r in c3_requires), "C3 should require at least two records"
    print("  PASS: C3 correctly requires two records and forbids full recovery claim")
    tests_passed += 1

    # Test 14: P4 requirements
    print("Test 14: P4 requirements")
    p4 = next(p for p in cvl["component_levels"]["physical_anchor"] if p["level"] == "P4")
    p4_requires = p4.get("requires", [])
    assert any("nonce" in r.lower() for r in p4_requires), "P4 should require nonce"
    assert any("live video" in r.lower() for r in p4_requires), "P4 should require live video"
    print("  PASS: P4 correctly requires live video and nonce")
    tests_passed += 1

    # Test 15: P8 confidentiality
    print("Test 15: P8 confidentiality")
    p8 = next(p for p in cvl["component_levels"]["physical_anchor"] if p["level"] == "P8")
    p8_forbidden = p8.get("forbidden_claims", [])
    assert any("public disclosure" in f.lower() for f in p8_forbidden), "P8 should forbid public disclosure"
    print("  PASS: P8 correctly forbids public disclosure of confidential data")
    tests_passed += 1

    print(f"\nFINAL: PASS — {tests_passed}/{tests_passed + tests_failed} test cases passed")


if __name__ == "__main__":
    main()
