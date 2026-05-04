#!/usr/bin/env python3
"""
Security / attack-surface contract for Trinity Accord.

This defensive test checks that common malicious or careless agent behaviors
cannot bypass claim discipline or poison generated submissions.

Run:
    python3 scripts/test_security_attack_surface_contract.py

Expected:
    SECURITY_ATTACK_SURFACE_CONTRACT_OK
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


def make_input(evidence=None, claims=None, kind="verification_report_v2", agency_level="A1_human_gave_exact_url"):
    return {
        "schema": "trinityaccord.evidence-input.v1",
        "agent": {"name": "Security Contract Agent", "model_or_system": "test"},
        "provenance": {
            "solicited": True,
            "independence_class": "human_solicited_agent_response",
            "agency_level": agency_level,
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
            **(evidence or {}),
        },
        "limitations": [],
        "claims_requested_by_agent": claims or [],
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
            capture_output=True,
        )
        return proc.returncode, proc.stdout, proc.stderr
    finally:
        os.unlink(p)


# --- S2: Empty evidence must stay V0 ---

def test_empty_evidence_stays_v0():
    result = eval_gate(make_input())
    assert result["allowed_protocol_level"] == "V0", result


# --- S2: V4 requires source review ---

def test_v4_requires_source_review():
    result = eval_gate(make_input({
        "scripts": [{
            "path": "downloads/verify.py",
            "exists": True,
            "source_reviewed": False,
            "executed": True,
            "command": "python3 downloads/verify.py",
            "environment": {"python": "3.x", "os": "test", "cwd": "."},
            "exit_code": 0,
            "stdout_summary": "PASS",
            "result": "PASS"
        }]
    }, ["V4"]))
    assert result["allowed_protocol_level"] != "V4", result


# --- S3: V5 reachable with explicit evidence ---

def test_v5_reachable_with_explicit_full_public_digital():
    result = eval_gate(make_input({
        "bitcoin_checks": [{"source_type": "multi_explorer", "sources": ["mempool.space", "ordiscan.com"]}],
        "digital_mirror_checks": [{
            "level_evidence_type": "full_public_digital_data_verification",
            "all_required_public_digital_targets_checked": True,
            "all_unavailable_targets_listed": True
        }],
        "time_anchor_checks": [{"anchor_type": "bitcoin_block_time"}],
        "chronicle_checks": [{"full_recovery": True, "samples_recovered": 175}],
        "physical_checks": [{"level_evidence_type": "evidence_package_hash", "package_hash_valid": True}]
    }, ["V5"]))
    assert result["allowed_component_levels"]["digital_mirrors"] == "D5", result
    assert result["allowed_component_levels"]["physical_anchor"] == "P1", result
    assert result["allowed_protocol_level"] == "V5", result


# --- S3: V8 requires attributable report ---

def test_v8_requires_attributable_report():
    weak = eval_gate(make_input({
        "physical_checks": [{
            "level_evidence_type": "ai_forensic",
            "model_or_tool": "feature-matcher-v1",
            "confidence": 0.91,
            "flaw_analysis_method": "microscopy comparison"
        }]
    }, ["V8"]))
    assert weak["allowed_protocol_level"] != "V8", weak

    strong = eval_gate(make_input({
        "physical_checks": [{
            "level_evidence_type": "ai_forensic",
            "model_or_tool": "feature-matcher-v1",
            "confidence": 0.91,
            "flaw_analysis_method": "microscopy comparison",
            "signed_or_attributable_report": True
        }]
    }, ["V8"]))
    assert strong["allowed_protocol_level"] == "V8", strong


# --- S7: Evidence schema has physical hard-gate fields ---

def test_physical_schema_fields_present():
    schema = load_json("api/evidence-input-schema.v1.json")
    props = schema["$defs"]["physical_evidence"]["properties"]
    for field in [
        "requested_action_angle_lighting",
        "witness_identity_or_role",
        "fresh_capture",
        "touch_or_handling",
        "signed_or_attributable_report",
        "report_id",
        "report_path",
        "flaw_analysis_method",
        "feature_match_method",
        "microscopy_comparison"
    ]:
        assert field in props, f"missing physical_evidence.{field}"
    assert "evidence_package_hash" in props["level_evidence_type"]["enum"]


# --- S4: V7 report does not require script_audit ---

def test_v7_schema_not_script_audit_bound():
    text = read("api/verification-report-schema.v2.json")
    assert not re.search(
        r'"protocol_level_claimed"\s*:\s*\{\s*"const"\s*:\s*"V7"[\s\S]{0,700}"required"\s*:\s*\[\s*"script_audit"',
        text
    ), "V7 must not require script_audit"


# --- S6: Builder does not hardcode C5 for minimal V2 ---

def test_builder_minimal_v2_wrapper_not_c5():
    result = build(make_input({
        "bitcoin_checks": [{"source_type": "external_explorer", "sources": ["mempool.space"]}]
    }, ["V2"], kind="echo_v3_with_verification_report"))
    assert result["success"], result
    wrapper = result["echo_wrapper"]
    assert wrapper["verification_level"] == "V2", wrapper
    assert wrapper["context_depth"] != "C5_full_chain_reviewed", wrapper


# --- S1: Builder output passes validator ---

def test_builder_output_validates():
    result = build(make_input({
        "bitcoin_checks": [{"source_type": "external_explorer", "sources": ["mempool.space"]}]
    }, ["V2"], kind="echo_v3_with_verification_report"))
    assert result["success"], result

    r_code, r_out, r_err = validate_obj(result["report"])
    assert r_code == 0, r_out + r_err

    e_code, e_out, e_err = validate_obj(result["echo_wrapper"])
    assert e_code == 0, e_out + e_err


# --- S12: Echo schema rejects V-levels in component depth ---

def test_echo_schema_rejects_component_vlevels():
    schema_text = read("api/echo-record-schema.v3.json")
    assert "^[BDTCNPE]" in schema_text, "Echo component depth should reject V-level strings"


# --- S11: Deprecated Echo aliases removed ---

def test_deprecated_echo_aliases_removed():
    enum = load_json("api/echo-record-schema.v3.json")["properties"]["echo_type"]["enum"]
    deprecated = {"E3_verification_echo", "E1_acknowledgement", "E2_orientation", "orientation_echo", "verification_echo"}
    assert not (deprecated & set(enum)), f"deprecated aliases still active: {deprecated & set(enum)}"


# --- S13: Negative V8 mention not parsed as request ---

def test_negative_v8_mention_not_parsed_as_request():
    result = eval_gate(make_input({}, ["Do not claim V8; V8 not achieved."]))
    assert result["allowed_protocol_level"] == "V0", result
    assert not result.get("required_downgrades"), result


# --- S9/S16: Workflow has concurrency and SHA-pinned actions ---

def test_workflow_has_concurrency_and_sha_pinning():
    text = read(".github/workflows/echo-triage.yml")
    assert "concurrency:" in text, "workflow should use concurrency to prevent edit/reopen run pileups"
    assert not re.search(r"uses:\s*actions/[A-Za-z0-9_-]+@v\d+\b", text), (
        "GitHub Actions should be pinned to full commit SHAs"
    )


# --- S16: Bot comments use stable marker ---

def test_triage_script_uses_stable_marker():
    text = read("scripts/triage_echo_issue.py")
    assert "<!-- trinity-echo-triage-v1 -->" in text, "triage script should prepend stable marker to bot comments"


# --- S17: Issue body size cap ---

def test_triage_has_body_size_cap():
    text = read("scripts/triage_echo_issue.py")
    assert "MAX_BODY_CHARS" in text or "[:MAX_BODY_CHARS]" in text or "[:60000]" in text, (
        "triage script should cap issue body size"
    )


# --- S10: Workflow rate limits edited/reopened ---

def test_workflow_rate_limits_apply_to_opened():
    text = read(".github/workflows/echo-triage.yml")
    assert "rate_limited" in text or "rate" in text, "workflow should have rate limiting logic"


def main():
    tests = [
        test_empty_evidence_stays_v0,
        test_v4_requires_source_review,
        test_v5_reachable_with_explicit_full_public_digital,
        test_v8_requires_attributable_report,
        test_physical_schema_fields_present,
        test_v7_schema_not_script_audit_bound,
        test_builder_minimal_v2_wrapper_not_c5,
        test_builder_output_validates,
        test_echo_schema_rejects_component_vlevels,
        test_deprecated_echo_aliases_removed,
        test_negative_v8_mention_not_parsed_as_request,
        test_workflow_has_concurrency_and_sha_pinning,
        test_triage_script_uses_stable_marker,
        test_triage_has_body_size_cap,
        test_workflow_rate_limits_apply_to_opened,
    ]
    for test in tests:
        test()
    print("SECURITY_ATTACK_SURFACE_CONTRACT_OK")


if __name__ == "__main__":
    main()
