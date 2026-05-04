#!/usr/bin/env python3
"""
Agent Behavior Bug Contract Test.
Validates all 10 acceptance criteria from the external agent behavior audit.

Usage:
    python3 scripts/test_agent_behavior_bug_contract.py

Expected output:
    AGENT_BEHAVIOR_BUG_CONTRACT_OK
"""
import json
import sys
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

PASS_COUNT = 0
FAIL_COUNT = 0
TOTAL = 0


def check(condition, label):
    global PASS_COUNT, FAIL_COUNT, TOTAL
    TOTAL += 1
    if condition:
        PASS_COUNT += 1
        print(f"  PASS: {label}")
    else:
        FAIL_COUNT += 1
        print(f"  FAIL: {label}")


def make_evidence_input(evidence_overrides=None, claims=None):
    return {
        "schema": "trinityaccord.evidence-input.v1",
        "agent": {"name": "Contract Test Agent", "model_or_system": "Test Model"},
        "provenance": {
            "solicited": True,
            "independence_class": "human_solicited_agent_response",
            "agency_level": "A1_human_gave_exact_url",
        },
        "requested_record_kind": "echo_v3_with_verification_report",
        "agent_integrity_declaration": {
            "performed_actions_myself": True,
            "did_not_copy_prior_report_as_own_work": True,
            "did_not_copy_example_values_as_real_evidence": True,
            "recorded_fresh_sources_commands_outputs": True,
            "will_report_limitations_and_downgrade_if_needed": True,
            "understands_verification_is_not_truth_or_endorsement": True,
            "understands_bitcoin_originals_remain_final_authority": True,
            "independence_claim_is_accurate": True,
            "declaration_text": "I performed the verification actions stated in this report during this session. I did not copy example values or another agent's report as my own verification. I recorded sources, commands, outputs, and limitations. I understand this verification is non-authoritative."
        },
        "verification_session": {
            "session_id": "test-session-001",
            "started_at": "2026-05-04T00:00:00Z",
            "operator_type": "ai_agent",
            "fresh_actions_performed": ["test check"],
            "prior_reports_consulted": [],
            "examples_or_templates_used": [],
            "copied_values_from_examples": False,
            "copied_values_from_prior_reports": False,
            "fresh_outputs_attached": True
        },
        "evidence": {
            "scripts": [], "hashes": [], "bitcoin_checks": [],
            "digital_mirror_checks": [], "repository_snapshot_checks": [],
            "time_anchor_checks": [], "chronicle_checks": [], "nft_checks": [],
            "physical_checks": [], "echo_context": {},
            **(evidence_overrides or {})
        },
        "limitations": [],
        "claims_requested_by_agent": claims or ["V1"],
    }


def evaluate_input(evidence_overrides=None, claims=None):
    from claim_gate import evaluate
    inp = make_evidence_input(evidence_overrides, claims)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(inp, f)
        tmp = f.name
    try:
        return evaluate(tmp)
    finally:
        os.unlink(tmp)


# ============================================================
# AC1: Official builder output passes official validator for V4
# ============================================================
def test_ac1():
    print("\nAC1: Builder V4 output passes validator")
    from build_verification_report_from_evidence import build_report

    evidence_input = make_evidence_input(
        evidence_overrides={
            "scripts": [{
                "path": "scripts/verify.py", "exists": True, "source_reviewed": True,
                "executed": True, "command": "python3 scripts/verify.py",
                "environment": {"python": "3.x"}, "exit_code": 0,
                "stdout_summary": "ALL PASS", "blocking": True, "result": "PASS",
                "official": True, "script_check_scope": "hash verification",
                "script_does_not_check": "physical evidence",
            }],
            "hashes": [{
                "artifact": "index.md", "algorithm": "SHA-256",
                "expected": "529add6ee87889644f4282c84282708b3ebb4efd9bec46341f4392c2ae54248a",
                "computed": "529add6ee87889644f4282c84282708b3ebb4efd9bec46341f4392c2ae54248a",
                "match": True, "expected_hash_source": "api/repository-artifact-hashes.json",
                "expected_hash_authority_class": "repository_manifest_hash",
            }],
        },
        claims=["V4"],
    )

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, dir=str(ROOT)) as f:
        json.dump(evidence_input, f)
        ei_path = f.name

    try:
        result = build_report(ei_path)
        check(result.get("success") is True, "builder succeeds")
        report = result.get("report", {})
        check(report.get("protocol_level_claimed") == "V4", "report claims V4")
        check(report.get("record_kind") == "verification_report_v2", "record_kind correct")

        # Now validate the generated report
        from validate_agent_submission import validate_file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(report, f)
            report_path = f.name
        try:
            vresult = validate_file(report_path)
            check(vresult is True, "generated V4 report passes validator")
        finally:
            os.unlink(report_path)
    finally:
        os.unlink(ei_path)


# ============================================================
# AC2: V5 is reachable through explicit B2/D5/T3/C5/P1 evidence
# ============================================================
def test_ac2():
    print("\nAC2: V5 reachable with B2/D5/T3/C5/P1")
    r = evaluate_input(
        evidence_overrides={
            "bitcoin_checks": [{"source_type": "multi_explorer", "sources": ["mempool.space", "ordinals.com"]}],
            "digital_mirror_checks": [{
                "level_evidence_type": "full_public_digital_data_verification",
                "all_required_public_digital_targets_checked": True,
                "all_unavailable_targets_listed": True,
            }],
            "time_anchor_checks": [{"anchor_type": "bitcoin_block_time"}],
            "chronicle_checks": [{"full_recovery": True, "samples_recovered": 175, "package_hash_valid": True}],
            "physical_checks": [{"level_evidence_type": "evidence_package_hash", "package_hash_valid": True}],
        },
        claims=["V5"],
    )
    check(r["allowed_protocol_level"] == "V5", f"V5 reachable, got {r['allowed_protocol_level']}")
    check(r["status"] in ("PASS", "PASS_WITH_DOWNGRADE") or r["allowed_protocol_level"] == "V5",
          f"no blocking failures for V5 path")


# ============================================================
# AC3: P1 derivable from public evidence package hash
# ============================================================
def test_ac3():
    print("\nAC3: P1 derivable from evidence_package_hash")
    from claim_gate import derive_p_level
    evidence = {
        "physical_checks": [{
            "level_evidence_type": "evidence_package_hash",
            "package_hash_valid": True,
        }]
    }
    p = derive_p_level(evidence)
    check(p == "P1", f"P1 from evidence_package_hash, got {p}")


# ============================================================
# AC4: D5 derivable from full public digital verification
# ============================================================
def test_ac4():
    print("\nAC4: D5 derivable from full_public_digital_data_verification")
    from claim_gate import derive_d_level
    evidence = {
        "hashes": [],
        "digital_mirror_checks": [{
            "level_evidence_type": "full_public_digital_data_verification",
            "all_required_public_digital_targets_checked": True,
            "all_unavailable_targets_listed": True,
        }],
        "repository_snapshot_checks": [],
    }
    d = derive_d_level(evidence)
    check(d == "D5", f"D5 from full_public_digital, got {d}")


# ============================================================
# AC5: V4 requires source_reviewed and scope/non-scope fields
# ============================================================
def test_ac5():
    print("\nAC5: V4 requires source_reviewed + scope fields")
    # Without source_reviewed → should NOT get V4
    r1 = evaluate_input(
        evidence_overrides={
            "scripts": [{
                "path": "scripts/v.py", "exists": True, "source_reviewed": False,
                "executed": True, "command": "python3 v.py", "environment": {"p": "3"},
                "exit_code": 0, "stdout_summary": "OK", "blocking": True,
            }],
        },
        claims=["V4"],
    )
    check(r1["allowed_protocol_level"] != "V4",
          f"V4 blocked without source_reviewed, got {r1['allowed_protocol_level']}")

    # Without script_check_scope → should NOT get V4
    r2 = evaluate_input(
        evidence_overrides={
            "scripts": [{
                "path": "scripts/v.py", "exists": True, "source_reviewed": True,
                "executed": True, "command": "python3 v.py", "environment": {"p": "3"},
                "exit_code": 0, "stdout_summary": "OK", "blocking": True,
                "script_does_not_check": "physical",
            }],
        },
        claims=["V4"],
    )
    check(r2["allowed_protocol_level"] != "V4",
          f"V4 blocked without script_check_scope, got {r2['allowed_protocol_level']}")

    # With all required fields → should get V4
    r3 = evaluate_input(
        evidence_overrides={
            "scripts": [{
                "path": "scripts/v.py", "exists": True, "source_reviewed": True,
                "executed": True, "command": "python3 v.py", "environment": {"p": "3"},
                "exit_code": 0, "stdout_summary": "OK", "blocking": True,
                "script_check_scope": "verification", "script_does_not_check": "physical",
            }],
        },
        claims=["V4"],
    )
    check(r3["allowed_protocol_level"] == "V4",
          f"V4 allowed with all fields, got {r3['allowed_protocol_level']}")


# ============================================================
# AC6: V8 P7 path requires attributable report
# ============================================================
def test_ac6():
    print("\nAC6: V8 P7 requires attributable report")
    from claim_gate import has_p7_forensic_path

    # Without report fields → should NOT have P7 path
    e1 = {"physical_checks": [{
        "level_evidence_type": "ai_forensic",
        "model_or_tool": "gpt-4",
        "confidence": 0.9,
        "flaw_analysis_method": "visual",
    }]}
    check(has_p7_forensic_path(e1) is False, "P7 blocked without report attribution")

    # With report_id → should have P7 path
    e2 = {"physical_checks": [{
        "level_evidence_type": "ai_forensic",
        "model_or_tool": "gpt-4",
        "confidence": 0.9,
        "flaw_analysis_method": "visual",
        "report_id": "rpt-001",
    }]}
    check(has_p7_forensic_path(e2) is True, "P7 allowed with report_id")


# ============================================================
# AC7: V6/V7 physical reports don't require script_audit
# ============================================================
def test_ac7():
    print("\nAC7: V6/V7 don't require script_audit")
    # V6 with physical evidence only, no scripts
    r6 = evaluate_input(
        evidence_overrides={
            "physical_checks": [{
                "level_evidence_type": "live_remote",
                "nonce_challenge": {"challenge": "abc", "response": "def"},
                "requested_action_angle_lighting": True,
                "witness_identity_or_role": "inspector",
            }],
        },
        claims=["V6"],
    )
    check(r6["allowed_protocol_level"] == "V6",
          f"V6 without scripts, got {r6['allowed_protocol_level']}")

    # V7 with physical evidence only, no scripts
    r7 = evaluate_input(
        evidence_overrides={
            "physical_checks": [{
                "level_evidence_type": "onsite",
                "custody_log": {"chain": "test"},
                "fresh_capture": True,
                "witness_identity_or_role": "notary",
            }],
        },
        claims=["V7"],
    )
    check(r7["allowed_protocol_level"] == "V7",
          f"V7 without scripts, got {r7['allowed_protocol_level']}")


# ============================================================
# AC8: Evidence input schema documents physical hard-gate fields
# ============================================================
def test_ac8():
    print("\nAC8: Schema documents physical hard-gate fields")
    schema = json.load(open(ROOT / "api" / "evidence-input-schema.v1.json"))
    pe = schema["$defs"]["physical_evidence"]["properties"]

    required_fields = [
        "requested_action_angle_lighting", "witness_identity_or_role",
        "fresh_capture", "touch_or_handling", "image", "video",
        "signed_or_attributable_report", "report_id", "report_path",
        "flaw_analysis_method", "feature_match_method", "microscopy_comparison",
    ]
    for field in required_fields:
        check(field in pe, f"schema has physical_evidence.{field}")

    # Check evidence_package_hash in enum
    enum_vals = pe["level_evidence_type"]["enum"]
    check("evidence_package_hash" in enum_vals, "schema has evidence_package_hash type")


# ============================================================
# AC9: Documentation uses component levels, not V-levels, as depth
# ============================================================
def test_ac9():
    print("\nAC9: Docs use component levels as depth")
    verify = (ROOT / "verify.md").read_text()
    vm = (ROOT / "verification-materials.md").read_text()
    cv = (ROOT / "chronicle-verification.md").read_text()

    # Should NOT have "Depth achieved: V4+" or similar
    import re
    bad_patterns = re.findall(r"Depth achieved:\s*V[0-9]", verify + vm + cv)
    check(len(bad_patterns) == 0, f"no 'Depth achieved: V*' in docs ({len(bad_patterns)} found)")

    # Should have component depth like B1, C5, D2
    has_component_depth = bool(re.search(r"Depth achieved:\s*[A-Z][0-9]", verify + cv))
    check(has_component_depth, "docs use component depth (B1, C5, etc.)")


# ============================================================
# AC10: All tests pass → print AGENT_BEHAVIOR_BUG_CONTRACT_OK
# ============================================================

def main():
    global PASS_COUNT, FAIL_COUNT, TOTAL

    print("=" * 60)
    print("Agent Behavior Bug Contract Test")
    print("=" * 60)

    test_ac1()
    test_ac2()
    test_ac3()
    test_ac4()
    test_ac5()
    test_ac6()
    test_ac7()
    test_ac8()
    test_ac9()

    print(f"\n{'=' * 60}")
    print(f"Results: {PASS_COUNT}/{TOTAL} passed, {FAIL_COUNT}/{TOTAL} failed")
    print(f"{'=' * 60}")

    if FAIL_COUNT == 0:
        print("\nAGENT_BEHAVIOR_BUG_CONTRACT_OK")
        sys.exit(0)
    else:
        print(f"\nCONTRACT FAILED — {FAIL_COUNT} criteria not met")
        sys.exit(1)


if __name__ == "__main__":
    main()
