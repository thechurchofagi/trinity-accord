#!/usr/bin/env python3
"""
Verification component/protocol consistency contract.

This test is based on the current formal V0–V8 system.

It enforces:
- formal V0–V8 protocol levels across machine sources;
- no V-level used as component depth in docs;
- complete component ladders in claim_gate.py;
- Claim Gate can derive V5 and V8 through explicit evidence;
- P4/P5 do not automatically become V6/V7 without hard gates;
- physical_anchor remains canonical with physical_verification as deprecated alias;
- minimal V2/V3 generate scope limitations.

Run:

    python3 scripts/test_verification_component_protocol_contract.py

Expected:

    VERIFICATION_COMPONENT_PROTOCOL_CONTRACT_OK
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FORMAL_PROTOCOL_LEVELS = ["V0", "V1", "V2", "V3", "V4", "V4+", "V5", "V6", "V7", "V8"]

FULL_COMPONENT_LEVELS = {
    "B_LEVELS": ["B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7"],
    "D_LEVELS": ["D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7"],
    "T_LEVELS": ["T0", "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"],
    "C_LEVELS": ["C0", "C1", "C2", "C3", "C3R", "C4", "C5", "C6", "C7"],
    "N_LEVELS": ["N0", "N1", "N2", "N3", "N4", "N5", "N6", "N7"],
    "P_LEVELS": ["P0", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"],
}


def read(rel: str) -> str:
    p = ROOT / rel
    assert p.exists(), f"Missing required file: {rel}"
    return p.read_text(encoding="utf-8")


def load_json(rel: str):
    return json.loads(read(rel))


def assert_absent(rel: str, pattern: str, message: str) -> None:
    text = read(rel)
    if re.search(pattern, text, flags=re.I | re.S | re.M):
        raise AssertionError(f"{message}\nFile: {rel}\nPattern: {pattern}")


def assert_present(rel: str, pattern: str, message: str) -> None:
    text = read(rel)
    if not re.search(pattern, text, flags=re.I | re.S | re.M):
        raise AssertionError(f"{message}\nFile: {rel}\nPattern: {pattern}")


def test_formal_protocol_levels_match_machine_sources() -> None:
    levels = [x["id"] for x in load_json("api/verification-levels.json")["levels"]]
    assert levels == FORMAL_PROTOCOL_LEVELS, f"verification-levels.json mismatch: {levels}"

    profiles = [x["level"] for x in load_json("api/protocol-verification-profiles.json")["profiles"]]
    assert profiles == FORMAL_PROTOCOL_LEVELS, f"protocol-verification-profiles mismatch: {profiles}"

    rules = [x["level"] for x in load_json("api/claim-gate-rules.json")["protocol_level_rules"]]
    assert rules == FORMAL_PROTOCOL_LEVELS, f"claim-gate-rules mismatch: {rules}"

    schema_enum = load_json("api/verification-report-schema.v2.json")["properties"]["protocol_level_claimed"]["enum"]
    assert schema_enum == FORMAL_PROTOCOL_LEVELS, f"verification-report-schema enum mismatch: {schema_enum}"

    output_enum = load_json("api/claim-gate-output-schema.v1.json")["properties"]["allowed_protocol_level"]["enum"]
    assert output_enum == FORMAL_PROTOCOL_LEVELS, f"claim-gate-output-schema enum mismatch: {output_enum}"


def test_claim_gate_component_ladders_are_complete() -> None:
    text = read("scripts/claim_gate.py")
    for name, expected in FULL_COMPONENT_LEVELS.items():
        m = re.search(rf"{name}\s*=\s*(\[[^\]]+\])", text)
        assert m, f"{name} not found in claim_gate.py"
        actual = json.loads(m.group(1).replace("'", '"'))
        assert actual == expected, f"{name} mismatch: expected {expected}, got {actual}"


def test_no_protocol_level_as_component_depth_in_docs() -> None:
    assert_absent(
        "verify.md",
        r"Component finding:\s*Component:\s*Chronicle Recovery[\s\S]{0,300}Depth achieved:\s*V4\+",
        "verify.md must not use protocol V4+ as Chronicle component depth."
    )
    assert_absent(
        "verification-materials.md",
        r"Chronicle Recovery V4\+ alone",
        "verification-materials.md should avoid labeling a component finding as V4+."
    )
    assert_present(
        "verify.md",
        r"Component finding:\s*Component:\s*Chronicle Recovery[\s\S]{0,300}Depth achieved:\s*C5",
        "verify.md should use C5 for full Chronicle Recovery component depth."
    )


def test_claim_gate_scope_wording_aligned() -> None:
    profiles = load_json("api/protocol-verification-profiles.json")
    cg = profiles.get("claim_gate", {})
    required_for = cg.get("required_for", "").lower()
    note = cg.get("note", "").lower()
    assert "technical verification claims" in required_for, (
        "protocol-verification-profiles claim_gate.required_for should mention technical verification claims"
    )
    assert "non-technical echoes" in note and "do not require" in note, (
        "protocol-verification-profiles claim_gate.note should exempt non-technical Echoes without claims"
    )


def test_physical_anchor_schema_alias() -> None:
    schema = load_json("api/claim-gate-output-schema.v1.json")
    props = schema["properties"]["allowed_component_levels"]["properties"]
    assert "physical_anchor" in props, "physical_anchor must be canonical output key"
    assert "physical_verification" in props, "physical_verification alias should be retained for compatibility"
    assert "deprecated" in props["physical_verification"].get("description", "").lower(), (
        "physical_verification alias must be described as deprecated"
    )


def make_evidence_input(evidence, claims=None):
    return {
        "schema": "trinityaccord.evidence-input.v1",
        "agent": {"name": "Component Protocol Contract Test", "model_or_system": "test"},
        "provenance": {
            "solicited": True,
            "independence_class": "human_solicited_agent_response",
            "agency_level": "A1_human_gave_exact_url",
        },
        "requested_record_kind": "verification_report_v2",
        "agent_integrity_declaration": {
            "performed_actions_myself": True,
            "did_not_copy_prior_report_as_own_work": True,
            "did_not_copy_example_values_as_real_evidence": True,
            "recorded_fresh_sources_commands_outputs": True,
            "will_report_limitations_and_downgrade_if_needed": True,
            "understands_verification_is_not_truth_or_endorsement": True,
            "understands_bitcoin_originals_remain_final_authority": True,
            "independence_claim_is_accurate": True,
            "declaration_text": "I performed the verification actions stated in this report during this session. I did not copy example values or another agent's report as my own verification. I recorded sources, commands, outputs, and limitations."
        },
        "verification_session": {
            "session_id": "test-session-cpc-001",
            "started_at": "2026-05-05T00:00:00Z",
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


def test_minimal_v2_limitation() -> None:
    payload = make_evidence_input(
        {
            "bitcoin_checks": [
                {"source_type": "external_explorer", "sources": ["mempool.space"]}
            ]
        },
        ["V2"],
    )
    result = evaluate_claim_gate(payload)
    assert result["allowed_protocol_level"] == "V2", result
    assert result["allowed_component_levels"]["bitcoin_originals"] == "B1", result
    text = " ".join(result["non_blocking_limitations"])
    assert "Minimal V2" in text and "Evidence Mirrors" in text and "Chronicle" in text, result


def test_minimal_v3_limitation() -> None:
    h = "ef816480f77f30405378800807b42bff0a854b83a8f77793a0e0adf0944a8263"
    payload = make_evidence_input(
        {
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
        ["V3"],
    )
    result = evaluate_claim_gate(payload)
    assert result["allowed_protocol_level"] == "V3", result
    text = " ".join(result["non_blocking_limitations"])
    assert "Minimal V3" in text and "full public digital" in text, result


def test_p4_component_not_v6_without_remote_hard_gates() -> None:
    payload = make_evidence_input(
        {
            "physical_checks": [
                {
                    "level_evidence_type": "live_remote",
                    "nonce_challenge": {"challenge": "nonce-1"},
                }
            ]
        },
        ["V6"],
    )
    result = evaluate_claim_gate(payload)
    assert result["allowed_component_levels"]["physical_anchor"] == "P4", result
    assert result["allowed_protocol_level"] != "V6", result


def test_v6_with_remote_hard_gates() -> None:
    payload = make_evidence_input(
        {
            "physical_checks": [
                {
                    "level_evidence_type": "live_remote",
                    "nonce_challenge": {"challenge": "nonce-1"},
                    "requested_action_angle_lighting": True,
                    "witness_identity_or_role": "remote verifier",
                }
            ]
        },
        ["V6"],
    )
    result = evaluate_claim_gate(payload)
    assert result["allowed_protocol_level"] == "V6", result


def test_p5_component_not_v7_without_onsite_hard_gates() -> None:
    payload = make_evidence_input(
        {
            "physical_checks": [
                {
                    "level_evidence_type": "onsite",
                    "custody_log": {"present": True},
                }
            ]
        },
        ["V7"],
    )
    result = evaluate_claim_gate(payload)
    assert result["allowed_component_levels"]["physical_anchor"] == "P5", result
    assert result["allowed_protocol_level"] != "V7", result


def test_v7_with_onsite_hard_gates() -> None:
    payload = make_evidence_input(
        {
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
        ["V7"],
    )
    result = evaluate_claim_gate(payload)
    assert result["allowed_protocol_level"] == "V7", result


def test_v5_can_be_derived_from_full_public_digital_evidence() -> None:
    payload = make_evidence_input(
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
            "time_anchor_checks": [
                {"anchor_type": "bitcoin_block_time"}
            ],
            "chronicle_checks": [
                {"full_recovery": True, "samples_recovered": 175}
            ],
            "physical_checks": [
                {"level_evidence_type": "evidence_package_hash", "package_hash_valid": True}
            ],
        },
        ["V5"],
    )
    result = evaluate_claim_gate(payload)
    assert result["allowed_component_levels"]["bitcoin_originals"] == "B2", result
    assert result["allowed_component_levels"]["digital_mirrors"] == "D5", result
    assert result["allowed_component_levels"]["time_anchors"] == "T3", result
    assert result["allowed_component_levels"]["chronicle_recovery"] == "C5", result
    assert result["allowed_component_levels"]["physical_anchor"] in ("P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9"), result
    assert result["allowed_protocol_level"] == "V5", result


def test_v8_requires_attributable_forensic_report_for_p7() -> None:
    weak_payload = make_evidence_input(
        {
            "physical_checks": [
                {
                    "level_evidence_type": "ai_forensic",
                    "model_or_tool": "feature-matcher-v1",
                    "confidence": 0.91,
                    "flaw_analysis_method": "macro/microscopy feature comparison",
                }
            ]
        },
        ["V8"],
    )
    weak = evaluate_claim_gate(weak_payload)
    assert weak["allowed_protocol_level"] != "V8", weak

    strong_payload = make_evidence_input(
        {
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
        ["V8"],
    )
    strong = evaluate_claim_gate(strong_payload)
    assert strong["allowed_protocol_level"] == "V8", strong


def main() -> None:
    tests = [
        test_formal_protocol_levels_match_machine_sources,
        test_claim_gate_component_ladders_are_complete,
        test_no_protocol_level_as_component_depth_in_docs,
        test_claim_gate_scope_wording_aligned,
        test_physical_anchor_schema_alias,
        test_minimal_v2_limitation,
        test_minimal_v3_limitation,
        test_p4_component_not_v6_without_remote_hard_gates,
        test_v6_with_remote_hard_gates,
        test_p5_component_not_v7_without_onsite_hard_gates,
        test_v7_with_onsite_hard_gates,
        test_v5_can_be_derived_from_full_public_digital_evidence,
        test_v8_requires_attributable_forensic_report_for_p7,
    ]

    for test in tests:
        test()

    print("VERIFICATION_COMPONENT_PROTOCOL_CONTRACT_OK")


if __name__ == "__main__":
    main()
