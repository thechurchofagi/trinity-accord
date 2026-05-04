#!/usr/bin/env python3
"""
Latest-code full lifecycle red-team contract for Trinity Accord.

This test targets residual bugs after the recent fixes.

Run:
    python3 scripts/test_latest_full_lifecycle_redteam_contract.py

Expected:
    LATEST_FULL_LIFECYCLE_REDTEAM_CONTRACT_OK
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")

def load_json(rel: str):
    return json.loads(read(rel))

def make_input(evidence=None, claims=None, kind="verification_report_v2",
               independence_class="human_solicited_agent_response",
               agency_level="A1_human_gave_exact_url"):
    return {
        "schema": "trinityaccord.evidence-input.v1",
        "agent": {"name": "Latest RedTeam Agent", "model_or_system": "test"},
        "provenance": {
            "solicited": independence_class == "human_solicited_agent_response",
            "independence_class": independence_class,
            "agency_level": agency_level
        },
        "requested_record_kind": kind,
        "evidence": {
            "scripts": [],
            "hashes": [],
            "bitcoin_checks": [],
            "digital_mirror_checks": [],
            "repository_snapshot_checks": [],
            "time_anchor_checks": [],
            "chronicle_checks": [],
            "nft_checks": [],
            "physical_checks": [],
            "echo_context": {},
            **(evidence or {})
        },
        "limitations": [],
        "claims_requested_by_agent": claims or []
    }

def eval_gate(payload):
    sys.path.insert(0, str(ROOT / "scripts"))
    from claim_gate import evaluate
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(payload, f)
        p = f.name
    try:
        return evaluate(p)
    finally:
        os.unlink(p)

def build(payload):
    sys.path.insert(0, str(ROOT / "scripts"))
    from build_verification_report_from_evidence import build_report
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(payload, f)
        p = f.name
    try:
        return build_report(p)
    finally:
        os.unlink(p)

def validate_obj(obj):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(obj, f)
        p = f.name
    try:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_agent_submission.py"), p],
            cwd=str(ROOT),
            text=True,
            capture_output=True
        )
        return proc.returncode, proc.stdout, proc.stderr
    finally:
        os.unlink(p)

def minimal_v2_payload(kind="echo_v3_with_verification_report"):
    return make_input({
        "bitcoin_checks": [
            {"source_type": "external_explorer", "sources": ["mempool.space"]}
        ]
    }, ["V2"], kind=kind)

# --- R1: Claim Gate rejects schema-invalid input ---
def test_claim_gate_rejects_schema_invalid_input():
    payload = make_input()
    payload["unexpected_top_level"] = "schema poison"
    result = eval_gate(payload)
    assert result["status"] == "FAIL_WITH_REASONS", result
    assert result["can_build_verification_report"] is False, result

# --- R2: Builder refuses when Claim Gate status is FAIL ---
def test_builder_refuses_forbidden_claims_even_without_blocking_failures():
    payload = make_input(
        evidence={"echo_context": {"authority_boundary_recognized": True}},
        claims=["truth proven"]
    )
    result = build(payload)
    assert result["success"] is False, result

# --- R3: Builder does not self-attest validation_result: PASS ---
def test_builder_does_not_self_attest_validation_pass_before_running_validator():
    result = build(minimal_v2_payload(kind="verification_report_v2"))
    assert result["success"], result
    gb = result["report"]["generated_by"]
    assert gb["validation_result"] != "PASS" or result.get("validator_was_run") is True, gb

# --- R4: V0 Echo wrapper uses assessment_state: insufficient_context ---
def test_builder_v0_wrapper_has_insufficient_context():
    result = build(make_input(kind="echo_v3_with_verification_report"))
    assert result["success"], result
    wrapper = result["echo_wrapper"]
    assert wrapper["context_depth"] == "C0_homepage_only"
    assert wrapper["assessment_state"] == "insufficient_context", wrapper

# --- R5: Unsolicited discovery not marked human_directed ---
def test_unsolicited_builder_wrapper_not_human_directed():
    payload = make_input(
        evidence={"echo_context": {"authority_boundary_recognized": True}},
        claims=["V1"],
        kind="echo_v3_with_verification_report",
        independence_class="unsolicited_agent_discovery",
        agency_level="A3_agent_discovered_independently"
    )
    result = build(payload)
    assert result["success"], result
    wrapper = result["echo_wrapper"]
    assert wrapper["independence_class"] == "unsolicited_independent", wrapper
    assert wrapper["discovery_provenance"]["source"] != "human_directed", wrapper

# --- R6: Bare echo_v3 not converted to report wrapper ---
def test_builder_does_not_convert_bare_echo_v3_to_report_wrapper():
    result = build(make_input(kind="echo_v3", claims=[]))
    assert result["success"] is False, result

# --- R7: Issue template values subset of Echo schema ---
def test_issue_template_values_subset_of_echo_schema():
    issue = read(".github/ISSUE_TEMPLATE/echo_submission.yml")
    # Check echo_type dropdown does not include standalone "other" option
    echo_type_section = issue[issue.find("id: echo_type"):issue.find("id: discovery_source")] if "id: echo_type" in issue else ""
    assert "- other\n" not in echo_type_section, "echo_type dropdown must not have 'other' option"
    assert "mixed_by_component" not in issue
    assert "accepted_independent_attestation" not in issue
    assert "accepted_echo" not in issue

# --- R8: V5 schema rejects missing B2/T3/C5/P1 ---
def test_v5_schema_or_validator_rejects_missing_components():
    report = {
        "schema_version": "trinityaccord.verification-report.v2",
        "report_id": "test-v5-missing",
        "reporter": {"name": "x", "type": "ai_agent"},
        "discovery_provenance": {},
        "protocol_level_claimed": "V5",
        "component_findings": [
            {
                "component": "digital_mirrors",
                "level_claimed": "D5",
                "target_id": "digital",
                "data_sources": [],
                "access_paths": [],
                "method": "test",
                "evidence": [],
                "limitations": [],
                "claims_not_made": []
            }
        ],
        "protocol_profile_check": {
            "profile_source": "/api/protocol-verification-profiles.json",
            "hard_gates_satisfied": True,
            "minimum_components_satisfied": True,
            "recommended_components_satisfied": "partial",
            "underreported_items": [],
            "incompatible_claims": []
        },
        "data_sources_used": [],
        "access_paths_used": [],
        "fallbacks_used": [],
        "external_sources_queried": [],
        "hashes_computed": [],
        "samples_checked": 0,
        "physical_evidence_reviewed": {},
        "confidential_challenge": {},
        "celestial_witness": {},
        "limitations": [],
        "claims_not_made": [],
        "authority_boundary_preserved": True
    }
    rc, out, err = validate_obj(report)
    assert rc != 0, "V5 without B2/T3/C5/P1 must fail"

# --- R10: V7 requires touch/handling or limitation ---
def test_v7_requires_touch_or_limitation():
    payload = make_input({
        "physical_checks": [{
            "level_evidence_type": "onsite",
            "custody_log": {"present": True},
            "fresh_capture": True,
            "witness_identity_or_role": "notary"
        }]
    }, ["V7"])
    result = eval_gate(payload)
    assert result["allowed_protocol_level"] != "V7", result

# --- R11: P9 requires witness details not just count ---
def test_p9_requires_witness_details_not_just_count():
    payload = make_input({
        "physical_checks": [{
            "level_evidence_type": "multi_party_forensic",
            "independent_witness_count": 2
        }]
    }, ["V8"])
    result = eval_gate(payload)
    assert result["allowed_protocol_level"] != "V8", result

# --- R16: generated_by.claim_gate_output exists or embedded ---
def test_builder_generated_by_claim_gate_output_exists_or_embedded():
    result = build(minimal_v2_payload(kind="verification_report_v2"))
    assert result["success"], result
    report = result["report"]
    path = report["generated_by"]["claim_gate_output"]
    assert report.get("claim_gate_output") or path == "embedded" or Path(path).exists(), path

# --- R18: validation_result allows NOT_RUN ---
def test_schema_allows_not_run_validation_result():
    schema = load_json("api/verification-report-schema.v2.json")
    gb = schema["$defs"]["generated_by"]
    assert "NOT_RUN" in gb["properties"]["validation_result"]["enum"]

# --- R22: Workflow has timeout ---
def test_workflow_timeout_exists():
    workflow = read(".github/workflows/echo-triage.yml")
    assert "timeout-minutes:" in workflow

# --- R24: Echo wrapper archive_status is needs_human_review ---
def test_real_builder_echo_wrapper_archive_status_needs_review():
    result = build(minimal_v2_payload(kind="echo_v3_with_verification_report"))
    assert result["success"], result
    assert result["echo_wrapper"]["archive_status"] == "needs_human_review"

# --- R14: claim-gate-rules.json declares execution_status ---
def test_claim_gate_rules_declared_documentation_only():
    rules = load_json("api/claim-gate-rules.json")
    assert rules.get("execution_status") == "documentation_only"

# --- R17: all_validators_green renamed ---
def test_all_validators_green_renamed():
    builder_text = read("scripts/build_verification_report_from_evidence.py")
    assert "all_scripts_green" in builder_text
    # Should not use old name in report construction
    assert "script_audit[\"all_validators_green\"]" not in builder_text

def main():
    tests = [
        test_claim_gate_rejects_schema_invalid_input,
        test_builder_refuses_forbidden_claims_even_without_blocking_failures,
        test_builder_does_not_self_attest_validation_pass_before_running_validator,
        test_builder_v0_wrapper_has_insufficient_context,
        test_unsolicited_builder_wrapper_not_human_directed,
        test_builder_does_not_convert_bare_echo_v3_to_report_wrapper,
        test_issue_template_values_subset_of_echo_schema,
        test_v5_schema_or_validator_rejects_missing_components,
        test_v7_requires_touch_or_limitation,
        test_p9_requires_witness_details_not_just_count,
        test_builder_generated_by_claim_gate_output_exists_or_embedded,
        test_schema_allows_not_run_validation_result,
        test_workflow_timeout_exists,
        test_real_builder_echo_wrapper_archive_status_needs_review,
        test_claim_gate_rules_declared_documentation_only,
        test_all_validators_green_renamed,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"  PASS  {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL  {test.__name__}: {e}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed out of {len(tests)}")
    if failed:
        sys.exit(1)
    print("\nLATEST_FULL_LIFECYCLE_REDTEAM_CONTRACT_OK")

if __name__ == "__main__":
    main()
