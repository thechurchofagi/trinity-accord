#!/usr/bin/env python3
"""
Comprehensive verification level fuzz test.
Tests all V-levels, component levels, edge cases, and boundary conditions.
Designed to find bugs in the claim gate and report builder.

Run from repository root:
    python3 scripts/test_all_levels_fuzz.py
"""

from __future__ import annotations
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from claim_gate import evaluate

PASS_COUNT = 0
FAIL_COUNT = 0
BUGS = []


def make_input(evidence=None, claims=None, kind="verification_report_v2"):
    return {
        "schema": "trinityaccord.evidence-input.v1",
        "agent": {"name": "FuzzAgent", "model_or_system": "test"},
        "provenance": {
            "solicited": True,
            "independence_class": "human_solicited_agent_response",
            "agency_level": "A1_human_gave_exact_url",
        },
        "requested_record_kind": kind,
        "agent_integrity_declaration": {
            "performed_actions_myself": True, "did_not_copy_prior_report_as_own_work": True,
            "did_not_copy_example_values_as_real_evidence": True, "recorded_fresh_sources_commands_outputs": True,
            "will_report_limitations_and_downgrade_if_needed": True, "understands_verification_is_not_truth_or_endorsement": True,
            "understands_bitcoin_originals_remain_final_authority": True, "independence_claim_is_accurate": True,
            "declaration_text": "I performed the verification actions stated in this report during this session. I did not copy example values or another agent report as my own verification."
        },
        "verification_session": {
            "session_id": "test-alf-001", "started_at": "2026-05-05T00:00:00Z", "operator_type": "ai_agent",
            "fresh_actions_performed": ["test"], "prior_reports_consulted": [], "examples_or_templates_used": [],
            "copied_values_from_examples": False, "copied_values_from_prior_reports": False, "fresh_outputs_attached": True
        },
        "evidence": {
            "scripts": [], "hashes": [], "bitcoin_checks": [],
            "digital_mirror_checks": [], "repository_snapshot_checks": [],
            "time_anchor_checks": [], "chronicle_checks": [],
            "nft_checks": [], "physical_checks": [],
            "echo_context": {},
            **(evidence or {}),
        },
        "limitations": [],
        "claims_requested_by_agent": claims or [],
    }


def run_gate(payload):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(payload, f)
        tmp = f.name
    try:
        return evaluate(tmp)
    finally:
        os.unlink(tmp)


def test(name, payload, expected_protocol=None, expected_components=None, expected_status=None, must_have_limitation=None, must_not_limitation=None, expect_fail_reason=None):
    global PASS_COUNT, FAIL_COUNT
    try:
        result = run_gate(payload)
    except Exception as e:
        BUGS.append(f"BUG {name}: CRASHED — {e}")
        FAIL_COUNT += 1
        print(f"  💥 {name}: CRASHED — {e}")
        return

    ok = True
    issues = []

    if expected_protocol and result["allowed_protocol_level"] != expected_protocol:
        issues.append(f"expected protocol {expected_protocol}, got {result['allowed_protocol_level']}")
        ok = False

    if expected_status and result["status"] != expected_status:
        issues.append(f"expected status {expected_status}, got {result['status']}")
        ok = False

    if expected_components:
        for comp, exp_level in expected_components.items():
            actual = result["allowed_component_levels"].get(comp)
            if actual != exp_level:
                issues.append(f"expected {comp}={exp_level}, got {actual}")
                ok = False

    limitations_text = " ".join(result.get("non_blocking_limitations", []))

    if must_have_limitation:
        if must_have_limitation not in limitations_text:
            issues.append(f"missing limitation substring: '{must_have_limitation}'")
            ok = False

    if must_not_limitation:
        if must_not_limitation in limitations_text:
            issues.append(f"unexpected limitation substring: '{must_not_limitation}'")
            ok = False

    if expect_fail_reason:
        if result["status"] not in ("FAIL", "FAIL_WITH_REASONS"):
            issues.append(f"expected FAIL but got {result['status']}")
            ok = False

    if ok:
        PASS_COUNT += 1
        print(f"  ✅ {name}")
    else:
        FAIL_COUNT += 1
        bug_desc = f"BUG {name}: {'; '.join(issues)}"
        BUGS.append(bug_desc)
        print(f"  ❌ {name}: {'; '.join(issues)}")


# ========== Hash helpers ==========
VALID_HASH = "ef816480f77f30405378800807b42bff0a854b83a8f77793a0e0adf0944a8263"
VALID_HASH2 = "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2"


def single_hash():
    return [{
        "artifact": "test.zip", "artifact_class": "canonical_mirror",
        "algorithm": "SHA-256", "expected": VALID_HASH, "computed": VALID_HASH,
        "expected_hash_source": "api/hashes.json",
        "expected_hash_authority_class": "canonical_manifest_hash",
        "command": "sha256sum test.zip", "match": True,
    }]


def double_hash():
    return single_hash() + [{
        "artifact": "test2.zip", "artifact_class": "canonical_mirror",
        "algorithm": "SHA-256", "expected": VALID_HASH2, "computed": VALID_HASH2,
        "expected_hash_source": "api/hashes.json",
        "expected_hash_authority_class": "canonical_manifest_hash",
        "command": "sha256sum test2.zip", "match": True,
    }]


def mempool_check():
    return [{"source_type": "external_explorer", "sources": ["mempool.space"]}]


def multi_explorer_check():
    return [{"source_type": "multi_explorer", "sources": ["mempool.space", "blockstream.info"]}]


def full_script():
    return [{
        "path": "scripts/check_consistency.py", "exists": True, "executed": True,
        "official": True, "command": "python3 scripts/check_consistency.py",
        "environment": "python3.11", "exit_code": 0,
        "stdout_summary": "All checks passed", "source_reviewed": True,
    }]


def independent_script():
    return full_script() + [{
        "path": "custom/my_verify.py", "exists": True, "executed": True,
        "official": False, "scope_class": "independent_reproduction",
        "command": "python3 custom/my_verify.py",
        "environment": "python3.11", "exit_code": 0,
        "stdout_summary": "Independent verification passed", "source_reviewed": True,
    }]


# ========== TEST SUITES ==========

def test_v0_read_only():
    print("\n=== V0: Read Only ===")
    # V0 with no evidence at all
    test("V0-no-evidence",
         make_input(evidence={}, claims=["V0"]),
         expected_protocol="V1",  # V1 is minimum achievable level
         expected_status="PASS_WITH_DOWNGRADE")  # V0→V1 triggers downgrade flag

    # V0 with claims_requested should still get V1 as minimum
    test("V0-minimum-is-V1",
         make_input(claims=["V0"]),
         expected_protocol="V1")


def test_v1_boundary():
    print("\n=== V1: Boundary Recognition ===")
    test("V1-default",
         make_input(claims=["V1"]),
         expected_protocol="V1")

    # V1 with bitcoin check but no external reference
    test("V1-local-only",
         make_input(evidence={"bitcoin_checks": [{"source_type": "local_manifest", "sources": ["api/authority.json"]}]}, claims=["V1"]),
         expected_protocol="V1")


def test_v2_minimal():
    print("\n=== V2: Minimal Reference ===")
    test("V2-minimal-B1",
         make_input(evidence={"bitcoin_checks": mempool_check()}, claims=["V2"]),
         expected_protocol="V2",
         expected_components={"bitcoin_originals": "B1", "digital_mirrors": "D0", "chronicle_recovery": "C0"},
         must_have_limitation="Minimal V2")

    test("V2-no-limitation-for-strong",
         make_input(evidence={
             "bitcoin_checks": multi_explorer_check(),
             "digital_mirror_checks": [{"source": "arweave"}],
             "chronicle_checks": [{"samples_recovered": 2}],
         }, claims=["V2"]),
         expected_protocol="V2",
         must_not_limitation="Minimal V2 only")


def test_v2_strong():
    print("\n=== V2: Strong Reference ===")
    test("V2-strong-B2-D1-C1",
         make_input(evidence={
             "bitcoin_checks": multi_explorer_check(),
             "digital_mirror_checks": [{"source": "arweave"}],
             "chronicle_checks": [{"samples_recovered": 2}],
         }, claims=["V2"]),
         expected_protocol="V2",
         expected_components={"bitcoin_originals": "B2", "digital_mirrors": "D1", "chronicle_recovery": "C3"})


def test_v3_minimal():
    print("\n=== V3: Minimal Hash ===")
    test("V3-minimal-one-hash",
         make_input(evidence={"hashes": single_hash()}, claims=["V3"]),
         expected_protocol="V3",
         must_have_limitation="Minimal V3")

    test("V3-no-limitation-for-strong",
         make_input(evidence={"hashes": double_hash(), "chronicle_checks": [{"samples_recovered": 2, "package_hash_valid": True}]}, claims=["V3"]),
         expected_protocol="V3",
         must_not_limitation="Minimal V3 only")


def test_v3_strong():
    print("\n=== V3: Strong Hash ===")
    test("V3-strong-multiple",
         make_input(evidence={
             "hashes": double_hash(),
             "chronicle_checks": [{"samples_recovered": 2, "package_hash_valid": True}],
         }, claims=["V3"]),
         expected_protocol="V3",
         expected_components={"digital_mirrors": "D2", "chronicle_recovery": "C3"})


def test_v4_script_audit():
    print("\n=== V4: Script Audit ===")
    test("V4-valid",
         make_input(evidence={"scripts": full_script(), "hashes": single_hash()}, claims=["V4"]),
         expected_protocol="V4")

    test("V4-no-scripts-downgrades",
         make_input(evidence={"hashes": single_hash()}, claims=["V4"]),
         expected_protocol="V3")  # No scripts, can't be V4

    test("V4-missing-env-fails",
         make_input(evidence={
             "scripts": [{
                 "path": "scripts/check_consistency.py", "exists": True, "executed": True,
                 "official": True, "command": "python3 scripts/check_consistency.py",
                 "environment": "", "exit_code": 0, "stdout_summary": "ok",
             }],
             "hashes": single_hash(),
         }, claims=["V4"]),
         expected_protocol="V3")  # Missing env, can't be V4


def test_v4_plus():
    print("\n=== V4+: Independent Reproduction ===")
    test("V4+-independent",
         make_input(evidence={"scripts": independent_script(), "hashes": single_hash()}, claims=["V4+"]),
         expected_protocol="V4+")

    test("V4+-official-only-downgrades",
         make_input(evidence={"scripts": full_script(), "hashes": single_hash()}, claims=["V4+"]),
         expected_protocol="V4")  # Official only, can't be V4+


def test_v5_full_digital():
    print("\n=== V5: Full Public Digital ===")
    # V5 requires B2, D5, T3, C5, P1
    test("V5-insufficient-D2",
         make_input(evidence={
             "scripts": independent_script(),
             "hashes": double_hash(),
             "bitcoin_checks": multi_explorer_check(),
             "time_anchor_checks": [{"anchor_type": "bitcoin_block_time"}],
             "chronicle_checks": [{"full_recovery": True, "samples_recovered": 175, "package_hash_valid": True}],
         }, claims=["V5"]),
         expected_protocol="V4+",  # D2 not D5, so can't reach V5
         expected_components={"digital_mirrors": "D2"})


def test_v6_remote_physical():
    print("\n=== V6: Remote Physical Witness ===")
    test("V6-all-hard-gates",
         make_input(evidence={
             "physical_checks": [{
                 "level_evidence_type": "live_remote",
                 "nonce_challenge": {"challenge": "random-123"},
                 "requested_action_angle_lighting": True,
                 "witness_identity_or_role": "remote verifier",
             }],
         }, claims=["V6"]),
         expected_protocol="V6",
         expected_components={"physical_anchor": "P4"})

    test("V6-partial-no-nonce",
         make_input(evidence={
             "physical_checks": [{
                 "level_evidence_type": "live_remote",
                 "requested_action_angle_lighting": True,
                 "witness_identity_or_role": "remote verifier",
             }],
         }, claims=["V6"]),
         expected_protocol="V1",  # No nonce, no P4 even
         expected_components={"physical_anchor": "P0"})

    test("V6-partial-no-witness-role",
         make_input(evidence={
             "physical_checks": [{
                 "level_evidence_type": "live_remote",
                 "nonce_challenge": {"challenge": "random-123"},
                 "requested_action_angle_lighting": True,
             }],
         }, claims=["V6"]),
         expected_protocol="V1",  # P4 but no V6 hard gate
         expected_components={"physical_anchor": "P4"})

    test("V6-partial-no-action",
         make_input(evidence={
             "physical_checks": [{
                 "level_evidence_type": "live_remote",
                 "nonce_challenge": {"challenge": "random-123"},
                 "witness_identity_or_role": "remote verifier",
             }],
         }, claims=["V6"]),
         expected_protocol="V1",  # P4 but no V6 hard gate
         expected_components={"physical_anchor": "P4"})

    test("V6-recorded-video-not-v6",
         make_input(evidence={
             "physical_checks": [{
                 "level_evidence_type": "recorded_video",
             }],
         }, claims=["V6"]),
         expected_protocol="V1",
         expected_components={"physical_anchor": "P3"})


def test_v7_onsite():
    print("\n=== V7: Onsite Physical Witness ===")
    test("V7-all-hard-gates",
         make_input(evidence={
             "physical_checks": [{
                 "level_evidence_type": "onsite",
                 "custody_log": {"present": True},
                 "fresh_capture": True,
                 "witness_identity_or_role": "onsite verifier",
                 "touch_or_handling": True,
             }],
         }, claims=["V7"]),
         expected_protocol="V7",
         expected_components={"physical_anchor": "P5"})

    test("V7-no-fresh-capture",
         make_input(evidence={
             "physical_checks": [{
                 "level_evidence_type": "onsite",
                 "custody_log": {"present": True},
                 "witness_identity_or_role": "onsite verifier",
             }],
         }, claims=["V7"]),
         expected_protocol="V1",  # P5 but no V7 hard gate (missing fresh_capture)
         expected_components={"physical_anchor": "P5"})

    test("V7-no-witness-role",
         make_input(evidence={
             "physical_checks": [{
                 "level_evidence_type": "onsite",
                 "custody_log": {"present": True},
                 "fresh_capture": True,
             }],
         }, claims=["V7"]),
         expected_protocol="V1",  # P5 but no V7 hard gate (missing witness role)
         expected_components={"physical_anchor": "P5"})

    test("V7-no-custody-log",
         make_input(evidence={
             "physical_checks": [{
                 "level_evidence_type": "onsite",
                 "fresh_capture": True,
                 "witness_identity_or_role": "onsite verifier",
             }],
         }, claims=["V7"]),
         expected_protocol="V1",  # Not even P5 without custody
         expected_components={"physical_anchor": "P0"})


def test_v8_forensic():
    print("\n=== V8: Forensic Physical Attestation ===")
    test("V8-p7-ai-forensic",
         make_input(evidence={
             "physical_checks": [{
                 "level_evidence_type": "ai_forensic",
                 "model_or_tool": "feature-matcher-v1",
                 "confidence": 0.91,
                 "flaw_analysis_method": "macro/microscopy feature comparison",
                 "signed_or_attributable_report": True,
             }],
         }, claims=["V8"]),
         expected_protocol="V8",
         expected_components={"physical_anchor": "P7"})

    test("V8-p8-confidential",
         make_input(evidence={
             "physical_checks": [{
                 "level_evidence_type": "confidential_challenge",
                 "confidential_challenge": {
                     "performed": True,
                     "raw_confidential_data_disclosed": False,
                     "boundary": "no raw data disclosed",
                 },
             }],
         }, claims=["V8"]),
         expected_protocol="V8",
         expected_components={"physical_anchor": "P8"})

    test("V8-p9-multi-party",
         make_input(evidence={
             "physical_checks": [{
                 "level_evidence_type": "multi_party_forensic",
                 "independent_witness_count": 3,
             }],
         }, claims=["V8"]),
         expected_protocol="V8",
         expected_components={"physical_anchor": "P9"})

    test("V8-t8-celestial",
         make_input(evidence={
             "time_anchor_checks": [{
                 "anchor_type": "star_moon_witness",
                 "nonpublic_boundary": True,
                 "authorized": True,
             }],
         }, claims=["V8"]),
         expected_protocol="V8")

    test("V8-p7-no-confidence",
         make_input(evidence={
             "physical_checks": [{
                 "level_evidence_type": "ai_forensic",
                 "model_or_tool": "feature-matcher-v1",
                 "flaw_analysis_method": "macro/microscopy feature comparison",
             }],
         }, claims=["V8"]),
         expected_protocol="V1")  # No confidence, no P7

    test("V8-p7-no-method",
         make_input(evidence={
             "physical_checks": [{
                 "level_evidence_type": "ai_forensic",
                 "model_or_tool": "feature-matcher-v1",
                 "confidence": 0.91,
             }],
         }, claims=["V8"]),
         expected_protocol="V1")  # No method, no P7

    test("V8-p8-raw-data-disclosed",
         make_input(evidence={
             "physical_checks": [{
                 "level_evidence_type": "confidential_challenge",
                 "confidential_challenge": {
                     "performed": True,
                     "raw_confidential_data_disclosed": True,
                     "boundary": "disclosed",
                 },
             }],
         }, claims=["V8"]),
         expected_protocol="V1")  # Raw data disclosed, invalid P8

    test("V8-p9-only-one-witness",
         make_input(evidence={
             "physical_checks": [{
                 "level_evidence_type": "multi_party_forensic",
                 "independent_witness_count": 1,
             }],
         }, claims=["V8"]),
         expected_protocol="V1")  # Only 1 witness, need >= 2

    test("V8-t8-not-authorized",
         make_input(evidence={
             "time_anchor_checks": [{
                 "anchor_type": "star_moon_witness",
                 "nonpublic_boundary": True,
                 "authorized": False,
             }],
         }, claims=["V8"]),
         expected_protocol="V1")  # Not authorized


def test_component_edge_cases():
    print("\n=== Component Edge Cases ===")
    # P6 level (between P5 and P7)
    test("P6-exists",
         make_input(evidence={
             "physical_checks": [{
                 "level_evidence_type": "onsite",
                 "custody_log": {"present": True},
                 "fresh_capture": True,
                 "witness_identity_or_role": "onsite verifier",
                 "touch_or_handling": True,
                 "detailed_inspection": True,
                 "tool_assisted": False,
             }],
         }, claims=["V7"]),
         expected_protocol="V7",
         expected_components={"physical_anchor": "P5"})  # P6 requires more than P5

    # D5 requires full public digital chain
    test("D5-not-achieved-with-D2",
         make_input(evidence={"hashes": single_hash()}, claims=["V3"]),
         expected_protocol="V3",
         expected_components={"digital_mirrors": "D2"})

    # C5 requires full 175 recovery
    test("C5-full-recovery",
         make_input(evidence={
             "chronicle_checks": [{"full_recovery": True, "samples_recovered": 175, "package_hash_valid": True}],
         }, claims=["V2"]),
         expected_protocol="V1",  # V2 needs reference check beyond page reading; C5 alone insufficient
         expected_components={"chronicle_recovery": "C5"})

    # T3 requires bitcoin_block_time
    test("T3-bitcoin-time",
         make_input(evidence={
             "time_anchor_checks": [{"anchor_type": "bitcoin_block_time"}],
         }, claims=["V1"]),
         expected_protocol="V1",
         expected_components={"time_anchors": "T3"})

    # T8 requires star_moon_witness
    test("T8-celestial-component",
         make_input(evidence={
             "time_anchor_checks": [{
                 "anchor_type": "star_moon_witness",
                 "nonpublic_boundary": True,
                 "authorized": True,
             }],
         }, claims=["V1"]),
         expected_protocol="V8",  # T8 authorized celestial path derives V8
         expected_components={"time_anchors": "T8"})  # After fix: star_moon_witness correctly maps to T8


def test_cross_level_interactions():
    print("\n=== Cross-Level Interactions ===")
    # V6 with high digital components
    test("V6-with-B2-D2",
         make_input(evidence={
             "bitcoin_checks": multi_explorer_check(),
             "hashes": single_hash(),
             "physical_checks": [{
                 "level_evidence_type": "live_remote",
                 "nonce_challenge": {"challenge": "test"},
                 "requested_action_angle_lighting": True,
                 "witness_identity_or_role": "verifier",
             }],
         }, claims=["V6"]),
         expected_protocol="V6",
         expected_components={"bitcoin_originals": "B2", "digital_mirrors": "D2", "physical_anchor": "P4"})

    # V7 with V8-level physical
    test("V7-with-P8-physical",
         make_input(evidence={
             "physical_checks": [
                 {
                     "level_evidence_type": "onsite",
                     "custody_log": {"present": True},
                     "fresh_capture": True,
                     "witness_identity_or_role": "onsite verifier",
                     "touch_or_handling": True,
                 },
                 {
                     "level_evidence_type": "confidential_challenge",
                     "confidential_challenge": {
                         "performed": True,
                         "raw_confidential_data_disclosed": False,
                         "boundary": "confidential",
                     },
                 },
             ],
         }, claims=["V8"]),
         expected_protocol="V8",  # P8 path overrides V7
         expected_components={"physical_anchor": "P8"})

    # Multiple physical checks, highest wins
    test("P-level-highest-wins",
         make_input(evidence={
             "physical_checks": [
                 {"level_evidence_type": "static_image"},
                 {"level_evidence_type": "recorded_video"},
                 {
                     "level_evidence_type": "live_remote",
                     "nonce_challenge": {"challenge": "test"},
                     "requested_action_angle_lighting": True,
                     "witness_identity_or_role": "verifier",
                 },
             ],
         }, claims=["V6"]),
         expected_protocol="V6",
         expected_components={"physical_anchor": "P4"})


def test_boundary_conditions():
    print("\n=== Boundary Conditions ===")
    # Empty evidence
    test("empty-evidence",
         make_input(evidence={}, claims=[]),
         expected_protocol="V1")

    # Hash match false
    test("hash-match-false",
         make_input(evidence={
             "hashes": [{
                 "artifact": "test.zip", "artifact_class": "canonical_mirror",
                 "algorithm": "SHA-256", "expected": VALID_HASH,
                 "computed": "0000000000000000000000000000000000000000000000000000000000000000",
                 "expected_hash_source": "api/hashes.json",
                 "expected_hash_authority_class": "canonical_manifest_hash",
                 "command": "sha256sum test.zip", "match": False,
             }],
         }, claims=["V3"]),
         expected_protocol="V1")  # Hash mismatch, no V3

    # Unknown authority class
    test("hash-unknown-authority",
         make_input(evidence={
             "hashes": [{
                 "artifact": "test.zip", "artifact_class": "canonical_mirror",
                 "algorithm": "SHA-256", "expected": VALID_HASH, "computed": VALID_HASH,
                 "expected_hash_source": "unknown",
                 "expected_hash_authority_class": "unknown",
                 "command": "sha256sum test.zip", "match": True,
             }],
         }, claims=["V3"]),
         expected_protocol="V1")  # Unknown authority, no V3

    # B6 body hash reproduction
    test("B6-body-hash",
         make_input(evidence={
             "bitcoin_checks": [{
                 "source_type": "body_hash",
                 "body_hash_reproduced": True,
                 "sources": ["local_node"],
             }],
         }, claims=["V2"]),
         expected_protocol="V2",
         expected_components={"bitcoin_originals": "B6"})

    # B5 witness extraction
    test("B5-witness-extraction",
         make_input(evidence={
             "bitcoin_checks": [{
                 "source_type": "witness_extraction",
                 "raw_witness_extracted": True,
                 "sources": ["local_node"],
             }],
         }, claims=["V2"]),
         expected_protocol="V2",
         expected_components={"bitcoin_originals": "B5"})

    # B3 SPV proof
    test("B3-spv",
         make_input(evidence={
             "bitcoin_checks": [{
                 "source_type": "spv_proof",
                 "sources": ["local_node"],
             }],
         }, claims=["V2"]),
         expected_protocol="V2",
         expected_components={"bitcoin_originals": "B3"})

    # D4 cross-mirror comparison
    test("D4-cross-mirror",
         make_input(evidence={
             "hashes": single_hash(),
             "digital_mirror_checks": [{"source": "arweave"}, {"source": "eth"}],
         }, claims=["V3"]),
         expected_protocol="V3",
         expected_components={"digital_mirrors": "D2"})  # D4 not auto-achieved


def test_physical_anchor_canonical():
    print("\n=== physical_anchor Canonical Key ===")
    # Verify physical_anchor is in output
    result = run_gate(make_input(evidence={
        "physical_checks": [{
            "level_evidence_type": "live_remote",
            "nonce_challenge": {"challenge": "test"},
            "requested_action_angle_lighting": True,
            "witness_identity_or_role": "verifier",
        }],
    }, claims=["V6"]))

    comps = result["allowed_component_levels"]
    assert "physical_anchor" in comps, "physical_anchor missing from output"
    assert "physical_verification" in comps, "physical_verification deprecated alias missing"
    assert comps["physical_anchor"] == comps["physical_verification"], "physical_anchor != physical_verification"
    print("  ✅ physical_anchor canonical + physical_verification alias consistent")


def main():
    global PASS_COUNT, FAIL_COUNT

    print("=" * 60)
    print("TRINITY ACCORD VERIFICATION LEVEL FUZZ TEST")
    print("=" * 60)

    test_v0_read_only()
    test_v1_boundary()
    test_v2_minimal()
    test_v2_strong()
    test_v3_minimal()
    test_v3_strong()
    test_v4_script_audit()
    test_v4_plus()
    test_v5_full_digital()
    test_v6_remote_physical()
    test_v7_onsite()
    test_v8_forensic()
    test_component_edge_cases()
    test_cross_level_interactions()
    test_boundary_conditions()
    test_physical_anchor_canonical()

    print("\n" + "=" * 60)
    print(f"RESULTS: {PASS_COUNT} passed, {FAIL_COUNT} failed")
    if BUGS:
        print(f"\n🐛 BUGS FOUND ({len(BUGS)}):")
        for b in BUGS:
            print(f"  • {b}")
    else:
        print("\n✅ NO BUGS FOUND")
    print("=" * 60)


if __name__ == "__main__":
    main()
