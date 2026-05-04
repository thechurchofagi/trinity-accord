#!/usr/bin/env python3
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
        "agent": {"name": "Lifecycle RedTeam Agent", "model_or_system": "test"},
        "provenance": {
            "solicited": True,
            "independence_class": "human_solicited_agent_response",
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


def test_formal_levels_everywhere():
    assert [x["id"] for x in load_json("api/verification-levels.json")["levels"]] == FORMAL_LEVELS
    assert [x["level"] for x in load_json("api/protocol-verification-profiles.json")["profiles"]] == FORMAL_LEVELS
    assert load_json("api/verification-report-schema.v2.json")["properties"]["protocol_level_claimed"]["enum"] == FORMAL_LEVELS


def test_agent_route_canonical_file_exists_and_is_referenced():
    canonical = load_json("api/agent-required-reading.json")
    assert "profiles" in canonical
    for profile in ["orientation", "evaluation", "verification", "echo_submission", "propagation"]:
        assert profile in canonical["profiles"]
        assert canonical["profiles"][profile], f"profile {profile} empty"
    joined = read("llms.txt") + read("agent-start.md") + read("api/agent-entry-protocol.json")
    assert "agent-required-reading" in joined


def test_llms_nontechnical_echo_exception():
    text = read("llms.txt").lower()
    assert "non-technical echoes" in text or "non-technical echo" in text
    assert "claim gate is not required" in text


def test_context_depth_not_verification_level_warning():
    ctx = load_json("api/context-depth-levels.json")
    raw = json.dumps(ctx).lower()
    assert "not_equivalent_to_verification" in raw or "does not imply v" in raw


def test_empty_evidence_stays_v0():
    result = eval_gate(make_input())
    assert result["allowed_protocol_level"] == "V0", result


def test_v4_requires_source_review_and_scope():
    payload = make_input({
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
    }, ["V4"])
    result = eval_gate(payload)
    assert result["allowed_protocol_level"] != "V4", result


def test_v5_reachable():
    payload = make_input({
        "bitcoin_checks": [{"source_type": "multi_explorer", "sources": ["mempool.space", "ordiscan.com"]}],
        "digital_mirror_checks": [{
            "level_evidence_type": "full_public_digital_data_verification",
            "all_required_public_digital_targets_checked": True,
            "all_unavailable_targets_listed": True
        }],
        "time_anchor_checks": [{"anchor_type": "bitcoin_block_time"}],
        "chronicle_checks": [{"full_recovery": True, "samples_recovered": 175}],
        "physical_checks": [{"level_evidence_type": "evidence_package_hash", "package_hash_valid": True}]
    }, ["V5"])
    result = eval_gate(payload)
    assert result["allowed_component_levels"]["digital_mirrors"] == "D5", result
    assert result["allowed_component_levels"]["physical_anchor"] == "P1", result
    assert result["allowed_protocol_level"] == "V5", result


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


def test_physical_schema_contains_v6_v7_v8_fields():
    props = load_json("api/evidence-input-schema.v1.json")["$defs"]["physical_evidence"]["properties"]
    for field in [
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
        "notarial_certificate_number",
        "notary_office",
        "notarial_date"
    ]:
        assert field in props, f"missing physical_evidence.{field}"
    assert "evidence_package_hash" in props["level_evidence_type"]["enum"]


def test_no_vlevel_component_depth_in_docs_or_schema():
    assert not re.search(r"Depth achieved:\s*V[0-9+]", read("verify.md"))
    assert "Chronicle Recovery V4+ alone" not in read("verification-materials.md")
    assert "^[BDTCNPE]" in read("api/echo-record-schema.v3.json")


def test_builder_minimal_v2_not_c5_and_validates():
    payload = make_input({
        "bitcoin_checks": [{"source_type": "external_explorer", "sources": ["mempool.space"]}]
    }, ["V2"], kind="echo_v3_with_verification_report")
    result = build_report(payload)
    assert result["success"], result
    wrapper = result["echo_wrapper"]
    assert wrapper["verification_level"] == "V2"
    assert wrapper["context_depth"] != "C5_full_chain_reviewed"
    rc, out, err = validate_obj(result["report"])
    assert rc == 0, out + err
    rc, out, err = validate_obj(wrapper)
    assert rc == 0, out + err


def test_builder_agency_mapping():
    payload = make_input({
        "bitcoin_checks": [{"source_type": "external_explorer", "sources": ["mempool.space"]}]
    }, ["V2"], kind="echo_v3_with_verification_report", agency_level="A2_human_gave_repo_name")
    result = build_report(payload)
    assert result["success"], result
    agency = result["echo_wrapper"]["discovery_provenance"]["agency_level"]
    valid = set(load_json("api/discovery-provenance-schema.json")["properties"]["agency_level"]["enum"])
    assert agency in valid, agency


def test_chronicle_samples_counted_from_samples_recovered():
    payload = make_input({
        "chronicle_checks": [{"samples_recovered": 2, "package_hash_valid": True}]
    }, ["V2"])
    result = build_report(payload)
    assert result["success"], result
    assert result["report"].get("samples_checked", 0) >= 2, result["report"].get("samples_checked")


def test_echo_schema_no_deprecated_aliases():
    enum = load_json("api/echo-record-schema.v3.json")["properties"]["echo_type"]["enum"]
    deprecated = {"E3_verification_echo", "E1_acknowledgement", "E2_orientation", "orientation_echo", "verification_echo"}
    assert not (deprecated & set(enum)), deprecated & set(enum)


def test_negative_claim_not_parsed_as_request():
    result = eval_gate(make_input({}, ["Do not claim V8; V8 not achieved."]))
    assert result["allowed_protocol_level"] == "V0", result
    assert not result.get("required_downgrades"), result


def test_propagation_policy_exists():
    pol = load_json("api/propagation-policy.json")
    raw = json.dumps(pol).lower()
    assert "point to verification" in raw
    assert "demand belief" in raw or "promise value" in raw


def test_triage_v0_v8_and_concurrency_marker():
    triage = read("scripts/triage_echo_issue.py")
    workflow = read(".github/workflows/echo-triage.yml")
    assert "V0" in triage and "V8" in triage
    assert "concurrency:" in workflow
    assert "trinity-echo-triage-v1" in workflow or "trinity-echo-triage-v1" in triage


def test_classification_boundaries_exists():
    pol = load_json("api/classification-boundaries.json")
    raw = json.dumps(pol).lower()
    assert "pre-asi" in raw
    assert "religion" in raw


def main():
    tests = [
        test_formal_levels_everywhere,
        test_agent_route_canonical_file_exists_and_is_referenced,
        test_llms_nontechnical_echo_exception,
        test_context_depth_not_verification_level_warning,
        test_empty_evidence_stays_v0,
        test_v4_requires_source_review_and_scope,
        test_v5_reachable,
        test_v8_requires_attributable_report,
        test_physical_schema_contains_v6_v7_v8_fields,
        test_no_vlevel_component_depth_in_docs_or_schema,
        test_builder_minimal_v2_not_c5_and_validates,
        test_builder_agency_mapping,
        test_chronicle_samples_counted_from_samples_recovered,
        test_echo_schema_no_deprecated_aliases,
        test_negative_claim_not_parsed_as_request,
        test_propagation_policy_exists,
        test_triage_v0_v8_and_concurrency_marker,
        test_classification_boundaries_exists,
    ]
    failures = []
    for test in tests:
        try:
            test()
            print(f"PASS: {test.__name__}")
        except Exception as e:
            print(f"FAIL: {test.__name__}: {e}")
            failures.append(test.__name__)

    if failures:
        print(f"\n{len(failures)} test(s) failed: {', '.join(failures)}")
        sys.exit(1)
    print("\nFULL_LIFECYCLE_AGENT_REDTEAM_CONTRACT_OK")


if __name__ == "__main__":
    main()
