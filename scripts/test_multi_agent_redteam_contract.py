#!/usr/bin/env python3
"""
Multi-agent red-team contract for Trinity Accord.

This simulates common agent behaviors and catches cross-file bugs:
- Claim Gate default V1 overgrant;
- V4 without source review;
- V5 unreachable through D5/P1;
- V8 too-cheap P7 path;
- physical hard-gate fields missing from schema;
- builder/validator script_audit mismatch;
- builder hardcoded C5 context depth;
- evidence provenance agency enum mismatch;
- V7 schema/validator overrequiring script_audit;
- V-level used as component depth in docs;
- C3 samples_checked miscount;
- deprecated Echo aliases allowed by active schema;
- arbitrary substring parsing of requested protocol claims.
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
FORMAL_LEVELS = ["V0", "V1", "V2", "V3", "V4", "V4+", "V5", "V6", "V7", "V8"]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def load_json(rel: str):
    return json.loads(read(rel))


def make_input(evidence=None, claims=None, kind="verification_report_v2", agency_level="A1_human_gave_exact_url"):
    return {
        "schema": "trinityaccord.evidence-input.v1",
        "agent": {"name": "RedTeam Agent", "model_or_system": "test"},
        "provenance": {
            "solicited": True,
            "independence_class": "human_solicited_agent_response",
            "agency_level": agency_level,
        },
        "requested_record_kind": kind,
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


def build_report(payload):
    sys.path.insert(0, str(ROOT / "scripts"))
    from build_verification_report_from_evidence import build_report

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(payload, f)
        p = f.name
    try:
        return build_report(p)
    finally:
        os.unlink(p)


def test_protocol_ladder() -> None:
    assert [x["id"] for x in load_json("api/verification-levels.json")["levels"]] == FORMAL_LEVELS
    assert [x["level"] for x in load_json("api/protocol-verification-profiles.json")["profiles"]] == FORMAL_LEVELS
    assert load_json("api/verification-report-schema.v2.json")["properties"]["protocol_level_claimed"]["enum"] == FORMAL_LEVELS


def test_empty_evidence_does_not_become_v1() -> None:
    result = eval_gate(make_input())
    assert result["allowed_protocol_level"] == "V0", result


def test_v4_requires_source_review_and_scope() -> None:
    payload = make_input(
        {
            "scripts": [
                {
                    "path": "downloads/verify.py",
                    "exists": True,
                    "source_reviewed": False,
                    "executed": True,
                    "command": "python3 downloads/verify.py",
                    "environment": {"python": "3.x", "os": "test", "cwd": "."},
                    "exit_code": 0,
                    "stdout_summary": "PASS",
                    "result": "PASS",
                }
            ]
        },
        ["V4"],
    )
    result = eval_gate(payload)
    assert result["allowed_protocol_level"] != "V4", result


def test_v5_reachable_with_explicit_full_public_evidence() -> None:
    payload = make_input(
        {
            "bitcoin_checks": [
                {"source_type": "multi_explorer", "sources": ["mempool.space", "ordiscan.com"]}
            ],
            "digital_mirror_checks": [
                {
                    "level_evidence_type": "full_public_digital_data_verification",
                    "all_required_public_digital_targets_checked": True,
                    "all_unavailable_targets_listed": True,
                }
            ],
            "time_anchor_checks": [{"anchor_type": "bitcoin_block_time"}],
            "chronicle_checks": [{"full_recovery": True, "samples_recovered": 175}],
            "physical_checks": [
                {"level_evidence_type": "evidence_package_hash", "package_hash_valid": True}
            ],
        },
        ["V5"],
    )
    result = eval_gate(payload)
    assert result["allowed_component_levels"]["digital_mirrors"] == "D5", result
    assert result["allowed_component_levels"]["physical_anchor"] == "P1", result
    assert result["allowed_protocol_level"] == "V5", result


def test_v8_requires_attributable_report() -> None:
    weak = make_input(
        {
            "physical_checks": [
                {
                    "level_evidence_type": "ai_forensic",
                    "model_or_tool": "feature-matcher-v1",
                    "confidence": 0.91,
                    "flaw_analysis_method": "microscopy feature comparison",
                }
            ]
        },
        ["V8"],
    )
    weak_result = eval_gate(weak)
    assert weak_result["allowed_protocol_level"] != "V8", weak_result

    strong = make_input(
        {
            "physical_checks": [
                {
                    "level_evidence_type": "ai_forensic",
                    "model_or_tool": "feature-matcher-v1",
                    "confidence": 0.91,
                    "flaw_analysis_method": "microscopy feature comparison",
                    "signed_or_attributable_report": True,
                }
            ]
        },
        ["V8"],
    )
    strong_result = eval_gate(strong)
    assert strong_result["allowed_protocol_level"] == "V8", strong_result


def test_physical_schema_has_gate_fields() -> None:
    schema = load_json("api/evidence-input-schema.v1.json")
    props = schema["$defs"]["physical_evidence"]["properties"]
    required = [
        "requested_action_angle_lighting",
        "witness_identity_or_role",
        "fresh_capture",
        "touch_or_handling",
        "image",
        "video",
        "signed_or_attributable_report",
        "report_id",
        "report_path",
        "flaw_analysis_method",
        "feature_match_method",
        "microscopy_comparison",
    ]
    for field in required:
        assert field in props, f"missing physical_evidence.{field}"
    assert "evidence_package_hash" in props["level_evidence_type"]["enum"]


def test_no_vlevel_as_component_depth_in_docs() -> None:
    verify = read("verify.md")
    materials = read("verification-materials.md")
    assert not re.search(r"Depth achieved:\s*V[0-9+]", verify), "V-level used as component depth in verify.md"
    assert "Chronicle Recovery V4+ alone" not in materials


def test_v7_schema_does_not_require_script_audit() -> None:
    schema_text = read("api/verification-report-schema.v2.json")
    pattern = r'"protocol_level_claimed"\s*:\s*\{\s*"const"\s*:\s*"V7"[\s\S]{0,700}"required"\s*:\s*\[\s*"script_audit"'
    assert not re.search(pattern, schema_text), "V7 should not require script_audit"


def test_builder_echo_context_depth_not_hardcoded_c5_for_minimal_v2() -> None:
    payload = make_input(
        {
            "bitcoin_checks": [
                {"source_type": "external_explorer", "sources": ["mempool.space"]}
            ]
        },
        ["V2"],
        kind="echo_v3_with_verification_report",
    )
    result = build_report(payload)
    assert result["success"], result
    wrapper = result["echo_wrapper"]
    assert wrapper["verification_level"] == "V2", wrapper
    assert wrapper["context_depth"] != "C5_full_chain_reviewed", wrapper


def test_builder_maps_evidence_agency_to_echo_agency() -> None:
    payload = make_input(
        {
            "bitcoin_checks": [
                {"source_type": "external_explorer", "sources": ["mempool.space"]}
            ]
        },
        ["V2"],
        kind="echo_v3_with_verification_report",
        agency_level="A2_human_gave_repo_name",
    )
    result = build_report(payload)
    assert result["success"], result
    agency = result["echo_wrapper"]["discovery_provenance"]["agency_level"]
    valid = set(load_json("api/discovery-provenance-schema.json")["properties"]["agency_level"]["enum"])
    assert agency in valid, f"builder emitted invalid echo agency_level: {agency}"


def test_builder_samples_checked_uses_samples_recovered() -> None:
    payload = make_input(
        {
            "chronicle_checks": [
                {"samples_recovered": 2, "full_recovery": False, "package_hash_valid": True}
            ]
        },
        ["V2"],
    )
    result = build_report(payload)
    assert result["success"], result
    assert result["report"]["samples_checked"] >= 2, result["report"]["samples_checked"]


def test_echo_schema_no_deprecated_aliases_for_active_v3() -> None:
    schema = load_json("api/echo-record-schema.v3.json")
    enum = schema["properties"]["echo_type"]["enum"]
    deprecated = {
        "E3_verification_echo",
        "E1_acknowledgement",
        "E2_orientation",
        "orientation_echo",
        "verification_echo",
    }
    assert not (deprecated & set(enum)), f"active echo schema still permits deprecated aliases: {deprecated & set(enum)}"


def test_echo_component_depth_pattern_blocks_vlevel() -> None:
    schema = load_json("api/echo-record-schema.v3.json")
    cf = schema["properties"].get("component_findings", {})
    text = json.dumps(cf)
    assert "pattern" in text and "^[BDTCNPE]" in text, "echo component_findings.depth_achieved should reject V-levels"


def test_requested_level_parser_ignores_negative_mentions() -> None:
    result = eval_gate(make_input({}, ["Do not claim V8; V8 not achieved."]))
    assert result["allowed_protocol_level"] == "V0", result
    assert not result["required_downgrades"], result


def main() -> None:
    tests = [
        test_protocol_ladder,
        test_empty_evidence_does_not_become_v1,
        test_v4_requires_source_review_and_scope,
        test_v5_reachable_with_explicit_full_public_evidence,
        test_v8_requires_attributable_report,
        test_physical_schema_has_gate_fields,
        test_no_vlevel_as_component_depth_in_docs,
        test_v7_schema_does_not_require_script_audit,
        test_builder_echo_context_depth_not_hardcoded_c5_for_minimal_v2,
        test_builder_maps_evidence_agency_to_echo_agency,
        test_builder_samples_checked_uses_samples_recovered,
        test_echo_schema_no_deprecated_aliases_for_active_v3,
        test_echo_component_depth_pattern_blocks_vlevel,
        test_requested_level_parser_ignores_negative_mentions,
    ]

    for test in tests:
        test()

    print("MULTI_AGENT_REDTEAM_CONTRACT_OK")


if __name__ == "__main__":
    main()
