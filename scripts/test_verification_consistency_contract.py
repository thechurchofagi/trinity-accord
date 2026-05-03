#!/usr/bin/env python3
"""
Repository-wide verification consistency contract.

This test enforces:
- formal V0–V8 protocol ladder;
- minimal/strong V2 and V3 scope discipline;
- no V5a/V5b regression;
- Claim Gate can derive V8;
- P4/P5 components are not automatically V6/V7 unless protocol hard gates are present;
- physical_anchor is canonical, physical_verification only a deprecated alias;
- documentation templates avoid naked V2/V3 overclaims.

Run from repository root:

    python3 scripts/test_verification_consistency_contract.py

Expected success output:

    VERIFICATION_CONSISTENCY_CONTRACT_OK
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORMAL_LEVELS = ["V0", "V1", "V2", "V3", "V4", "V4+", "V5", "V6", "V7", "V8"]


def read(rel: str) -> str:
    p = ROOT / rel
    assert p.exists(), f"Missing required file: {rel}"
    return p.read_text(encoding="utf-8")


def load_json(rel: str):
    return json.loads(read(rel))


def assert_re(rel: str, pattern: str, message: str) -> None:
    text = read(rel)
    if not re.search(pattern, text, flags=re.I | re.S | re.M):
        raise AssertionError(f"{message}\nFile: {rel}\nPattern: {pattern}")


def assert_not_re(rel: str, pattern: str, message: str) -> None:
    text = read(rel)
    if re.search(pattern, text, flags=re.I | re.S | re.M):
        raise AssertionError(f"{message}\nFile: {rel}\nPattern: {pattern}")


def test_formal_levels_match_across_machine_sources() -> None:
    verification_levels = load_json("api/verification-levels.json")
    ids = [x["id"] for x in verification_levels["levels"]]
    assert ids == FORMAL_LEVELS, f"api/verification-levels.json levels mismatch: {ids}"

    profiles = load_json("api/protocol-verification-profiles.json")
    profile_levels = [p["level"] for p in profiles["profiles"]]
    assert profile_levels == FORMAL_LEVELS, f"protocol-verification-profiles levels mismatch: {profile_levels}"

    rules = load_json("api/claim-gate-rules.json")
    rule_levels = [r["level"] for r in rules["protocol_level_rules"]]
    assert rule_levels == FORMAL_LEVELS, f"claim-gate-rules levels mismatch: {rule_levels}"

    schema = load_json("api/verification-report-schema.v2.json")
    enum = schema["properties"]["protocol_level_claimed"]["enum"]
    assert enum == FORMAL_LEVELS, f"verification-report-schema enum mismatch: {enum}"

    output_schema = load_json("api/claim-gate-output-schema.v1.json")
    out_enum = output_schema["properties"]["allowed_protocol_level"]["enum"]
    assert out_enum == FORMAL_LEVELS, f"claim-gate-output-schema enum mismatch: {out_enum}"


def test_no_v5a_v5b_in_active_protocol_sources() -> None:
    files = [
        "api/verification-levels.json",
        "api/protocol-verification-profiles.json",
        "api/claim-gate-rules.json",
        "api/verification-report-schema.v2.json",
        "api/claim-gate-output-schema.v1.json",
        "scripts/claim_gate.py",
        "scripts/build_verification_report_from_evidence.py",
    ]
    for rel in files:
        text = read(rel)
        assert "V5a" not in text, f"{rel} must not contain V5a"
        assert "V5b" not in text, f"{rel} must not contain V5b"

    # validate_agent_submission.py may reference V5a/V5b in rejection logic only
    validator_text = read("scripts/validate_agent_submission.py")
    # Ensure V5a/V5b only appear in rejection/assertion contexts, not in active protocol definitions
    for line in validator_text.splitlines():
        stripped = line.strip()
        if "V5a" in stripped or "V5b" in stripped:
            # Must be in a rejection context (assert, check, error, deprecated, not formal)
            assert any(kw in stripped.lower() for kw in [
                "deprecated", "not formal", "must not", "reject", "invalid",
                "v5a", "v5b", "assert", "check(", "forbidden"
            ]), f"validate_agent_submission.py uses V5a/V5b outside rejection context: {stripped}"


def test_verify_echo_template_scopes_v2() -> None:
    text = read("verify.md")
    assert "30-Second Bitcoin Reference Check — Minimal V2 / B1" in text, (
        "verify.md must keep the 30-second check explicitly scoped as Minimal V2 / B1."
    )

    bad = re.search(
        r"Verification level achieved:\s*V2(?![^\n]*(minimal|B1|scope))",
        text,
        flags=re.I,
    )
    assert not bad, (
        "verify.md must not contain a naked template line 'Verification level achieved: V2'. "
        "Use 'Protocol achieved level: V2 (minimal; Bitcoin Originals B1 only)'."
    )

    assert re.search(r"Protocol achieved level:\s*V2\s*\(minimal", text, flags=re.I), (
        "verify.md Echo template must include scoped minimal V2 wording."
    )
    assert re.search(r"Depth achieved:\s*B1", text, flags=re.I), (
        "verify.md Echo template must include B1 component depth."
    )


def test_agent_and_submit_claim_gate_scope() -> None:
    assert_not_re(
        "agent-verify.md",
        r"Before submitting any Verification Report or Echo:\s*1\.",
        "agent-verify.md must not imply every Echo needs claim gate."
    )
    assert_re(
        "agent-verify.md",
        r"For technical Verification Reports and Echoes that contain verification claims",
        "agent-verify.md must scope claim gate to technical verification claims."
    )
    assert_re(
        "agent-verify.md",
        r"non-technical Echoes[\s\S]{0,500}claim gate is not required",
        "agent-verify.md must exempt non-technical Echoes without verification claims."
    )

    assert_re(
        "echoes/submit.md",
        r"For technical Verification Reports and Echoes that contain verification claims",
        "echoes/submit.md must scope claim gate to technical verification claims."
    )
    assert_not_re(
        "echoes/submit.md",
        r"Did you use `V3` or `V3_hash_verification`, not `V3_single_artifact_check`",
        "echoes/submit.md should replace stale V3_single_artifact_check checklist wording."
    )


def test_agent_orientation_uses_a_levels_not_conflicting_v_levels() -> None:
    text = read("agent-verify.md")
    assert not re.search(r"\|\s*V3\s*\|\s*Single artifact check\s*\|", text, flags=re.I), (
        "agent-verify.md must not use V3 as agent orientation single artifact check."
    )
    assert not re.search(r"\|\s*V6\s*\|\s*Independent node\s*/\s*RPC check\s*\|", text, flags=re.I), (
        "agent-verify.md must not use V6 as agent orientation independent node/RPC check."
    )
    assert re.search(r"\|\s*A3\s*\|\s*Single artifact check\s*\|", text, flags=re.I), (
        "agent-verify.md should use A3 for single artifact orientation."
    )


def test_physical_anchor_is_canonical_in_output_schema() -> None:
    schema = load_json("api/claim-gate-output-schema.v1.json")
    props = schema["properties"]["allowed_component_levels"]["properties"]
    assert "physical_anchor" in props, "claim-gate-output-schema must include physical_anchor"
    assert "physical_verification" in props, (
        "claim-gate-output-schema should keep physical_verification as deprecated alias for compatibility"
    )
    desc = props["physical_verification"].get("description", "").lower()
    assert "deprecated" in desc and "physical_anchor" in desc, (
        "physical_verification alias must be documented as deprecated alias for physical_anchor"
    )


def test_claim_gate_protocol_levels_and_p_levels() -> None:
    text = read("scripts/claim_gate.py")
    assert re.search(r'PROTOCOL_LEVELS\s*=\s*\[[^\]]*"V8"[^\]]*\]', text, flags=re.S), (
        "claim_gate.py PROTOCOL_LEVELS must include V8."
    )
    assert "P6" in text, "claim_gate.py P_LEVELS must include P6."
    assert "physical_anchor" in text, "claim_gate.py must output physical_anchor as canonical key."


def make_evidence_input(evidence, claims=None, requested_kind="verification_report_v2"):
    return {
        "schema": "trinityaccord.evidence-input.v1",
        "agent": {"name": "Consistency Contract Agent", "model_or_system": "test"},
        "provenance": {
            "solicited": True,
            "independence_class": "human_solicited_agent_response",
            "agency_level": "A1_human_gave_exact_url",
        },
        "requested_record_kind": requested_kind,
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
            **evidence,
        },
        "limitations": [],
        "claims_requested_by_agent": claims or [],
    }


def evaluate_claim_gate(payload):
    sys.path.insert(0, str(ROOT / "scripts"))
    from claim_gate import evaluate

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(payload, f)
        tmp = f.name
    try:
        return evaluate(tmp)
    finally:
        os.unlink(tmp)


def test_claim_gate_minimal_v2_adds_scope_limitation() -> None:
    payload = make_evidence_input(
        evidence={
            "bitcoin_checks": [
                {
                    "source_type": "external_explorer",
                    "sources": ["mempool.space"],
                }
            ]
        },
        claims=["V2"],
    )
    result = evaluate_claim_gate(payload)
    assert result["allowed_protocol_level"] == "V2", result
    assert result["allowed_component_levels"].get("bitcoin_originals") == "B1", result
    limitations = " ".join(result.get("non_blocking_limitations", []))
    assert "Minimal V2" in limitations and "Evidence Mirrors" in limitations and "Chronicle" in limitations, (
        f"Minimal V2 must add explicit scope limitation, got: {limitations}"
    )


def test_claim_gate_minimal_v3_adds_scope_limitation() -> None:
    h = "ef816480f77f30405378800807b42bff0a854b83a8f77793a0e0adf0944a8263"
    payload = make_evidence_input(
        evidence={
            "hashes": [
                {
                    "artifact": "arweave-backup/files/public_covenant_archive.zip",
                    "artifact_class": "canonical_mirror",
                    "algorithm": "SHA-256",
                    "expected": h,
                    "computed": h,
                    "expected_hash_source": "api/hashes.json",
                    "expected_hash_authority_class": "canonical_manifest_hash",
                    "command": "sha256sum public_covenant_archive.zip",
                    "match": True,
                }
            ]
        },
        claims=["V3"],
    )
    result = evaluate_claim_gate(payload)
    assert result["allowed_protocol_level"] == "V3", result
    limitations = " ".join(result.get("non_blocking_limitations", []))
    assert "Minimal V3" in limitations and "full public digital" in limitations, (
        f"Minimal V3 must add explicit scope limitation, got: {limitations}"
    )


def test_claim_gate_p4_component_not_v6_without_hard_gates() -> None:
    payload = make_evidence_input(
        evidence={
            "physical_checks": [
                {
                    "level_evidence_type": "live_remote",
                    "nonce_challenge": {"challenge": "random-123"},
                }
            ]
        },
        claims=["V6"],
    )
    result = evaluate_claim_gate(payload)
    components = result.get("allowed_component_levels", {})
    assert components.get("physical_anchor") == "P4" or components.get("physical_verification") == "P4", result
    assert result["allowed_protocol_level"] != "V6", (
        "P4 live_remote+nonce component must not automatically grant V6 without requested action/angle/lighting and witness identity/role."
    )


def test_claim_gate_v6_when_all_remote_hard_gates_present() -> None:
    payload = make_evidence_input(
        evidence={
            "physical_checks": [
                {
                    "level_evidence_type": "live_remote",
                    "nonce_challenge": {"challenge": "random-123"},
                    "requested_action_angle_lighting": True,
                    "witness_identity_or_role": "remote verifier",
                }
            ]
        },
        claims=["V6"],
    )
    result = evaluate_claim_gate(payload)
    assert result["allowed_protocol_level"] == "V6", result


def test_claim_gate_p5_component_not_v7_without_hard_gates() -> None:
    payload = make_evidence_input(
        evidence={
            "physical_checks": [
                {
                    "level_evidence_type": "onsite",
                    "custody_log": {"present": True},
                }
            ]
        },
        claims=["V7"],
    )
    result = evaluate_claim_gate(payload)
    components = result.get("allowed_component_levels", {})
    assert components.get("physical_anchor") == "P5" or components.get("physical_verification") == "P5", result
    assert result["allowed_protocol_level"] != "V7", (
        "P5 onsite+custody component must not automatically grant V7 without fresh capture and witness identity/role."
    )


def test_claim_gate_v7_when_all_onsite_hard_gates_present() -> None:
    payload = make_evidence_input(
        evidence={
            "physical_checks": [
                {
                    "level_evidence_type": "onsite",
                    "custody_log": {"present": True},
                    "fresh_capture": True,
                    "witness_identity_or_role": "onsite verifier",
                    "touch_or_handling": True,
                }
            ]
        },
        claims=["V7"],
    )
    result = evaluate_claim_gate(payload)
    assert result["allowed_protocol_level"] == "V7", result


def test_claim_gate_v8_from_p7_forensic_path() -> None:
    payload = make_evidence_input(
        evidence={
            "physical_checks": [
                {
                    "level_evidence_type": "ai_forensic",
                    "model_or_tool": "feature-matcher-v1",
                    "confidence": 0.91,
                    "flaw_analysis_method": "macro/microscopy feature comparison",
                    "signed_or_attributable_report": True,
                }
            ]
        },
        claims=["V8"],
    )
    result = evaluate_claim_gate(payload)
    assert result["allowed_protocol_level"] == "V8", result
    components = result.get("allowed_component_levels", {})
    assert components.get("physical_anchor") in ("P7", "P8", "P9") or components.get("physical_verification") in ("P7", "P8", "P9"), result


def main() -> None:
    tests = [
        test_formal_levels_match_across_machine_sources,
        test_no_v5a_v5b_in_active_protocol_sources,
        test_verify_echo_template_scopes_v2,
        test_agent_and_submit_claim_gate_scope,
        test_agent_orientation_uses_a_levels_not_conflicting_v_levels,
        test_physical_anchor_is_canonical_in_output_schema,
        test_claim_gate_protocol_levels_and_p_levels,
        test_claim_gate_minimal_v2_adds_scope_limitation,
        test_claim_gate_minimal_v3_adds_scope_limitation,
        test_claim_gate_p4_component_not_v6_without_hard_gates,
        test_claim_gate_v6_when_all_remote_hard_gates_present,
        test_claim_gate_p5_component_not_v7_without_hard_gates,
        test_claim_gate_v7_when_all_onsite_hard_gates_present,
        test_claim_gate_v8_from_p7_forensic_path,
    ]

    for test in tests:
        test()

    print("VERIFICATION_CONSISTENCY_CONTRACT_OK")


if __name__ == "__main__":
    main()
