#!/usr/bin/env python3
"""
V8 formal verification consistency tests.

These tests enforce that the formal protocol ladder is:

    V0, V1, V2, V3, V4, V4+, V5, V6, V7, V8

and that stale V5a/V5b wording does not override the V8 system.

Run from repository root:

    python3 scripts/test_v8_formal_verification_consistency.py

Expected success output:

    V8_FORMAL_VERIFICATION_CONSISTENCY_OK
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
STALE_LEVELS = {"V5a", "V5b"}


def read(rel: str) -> str:
    p = ROOT / rel
    assert p.exists(), f"Missing required file: {rel}"
    return p.read_text(encoding="utf-8")


def load_json(rel: str):
    return json.loads(read(rel))


def assert_present(rel: str, pattern: str, msg: str) -> None:
    text = read(rel)
    if not re.search(pattern, text, flags=re.I | re.S | re.M):
        raise AssertionError(f"{msg}\nFile: {rel}\nPattern: {pattern}")


def assert_absent(rel: str, pattern: str, msg: str) -> None:
    text = read(rel)
    if re.search(pattern, text, flags=re.I | re.S | re.M):
        raise AssertionError(f"{msg}\nFile: {rel}\nPattern: {pattern}")


def test_formal_protocol_levels_match_everywhere() -> None:
    verification_levels = load_json("api/verification-levels.json")
    ids = [x["id"] for x in verification_levels["levels"]]
    assert ids == FORMAL_PROTOCOL_LEVELS, f"api/verification-levels.json levels wrong: {ids}"

    profiles = load_json("api/protocol-verification-profiles.json")
    profile_levels = [p["level"] for p in profiles["profiles"]]
    assert profile_levels == FORMAL_PROTOCOL_LEVELS, f"profile levels wrong: {profile_levels}"

    rules = load_json("api/claim-gate-rules.json")
    rule_levels = [r["level"] for r in rules["protocol_level_rules"]]
    assert rule_levels == FORMAL_PROTOCOL_LEVELS, f"claim-gate rules levels wrong: {rule_levels}"

    schema = load_json("api/verification-report-schema.v2.json")
    enum = schema["properties"]["protocol_level_claimed"]["enum"]
    assert enum == FORMAL_PROTOCOL_LEVELS, f"schema enum wrong: {enum}"

    component_levels = load_json("api/component-verification-levels.json")
    if "protocol_levels" in component_levels:
        levels = [x["level"] for x in component_levels["protocol_levels"]]
        assert levels == FORMAL_PROTOCOL_LEVELS, f"component-verification protocol levels wrong: {levels}"


def test_no_stale_v5a_v5b_in_protocol_sources() -> None:
    files = [
        "api/verification-levels.json",
        "api/protocol-verification-profiles.json",
        "api/claim-gate-rules.json",
        "api/verification-report-schema.v2.json",
        "scripts/claim_gate.py",
        "scripts/build_verification_report_from_evidence.py",
    ]

    for rel in files:
        text = read(rel)
        for stale in STALE_LEVELS:
            assert stale not in text, f"{rel} must not contain stale protocol level {stale}"

    # validate_agent_submission.py may reference V5a/V5b in rejection logic only
    validator_text = read("scripts/validate_agent_submission.py")
    for line in validator_text.splitlines():
        stripped = line.strip()
        if "V5a" in stripped or "V5b" in stripped:
            assert any(kw in stripped.lower() for kw in [
                "deprecated", "not formal", "must not", "reject", "invalid",
                "v5a", "v5b", "assert", "check(", "forbidden"
            ]), f"validate_agent_submission.py uses V5a/V5b outside rejection context: {stripped}"


def test_claim_gate_code_uses_v8_formal_levels() -> None:
    text = read("scripts/claim_gate.py")
    assert re.search(r'PROTOCOL_LEVELS\s*=\s*\[[^\]]*"V8"[^\]]*\]', text, re.S), (
        "claim_gate.py PROTOCOL_LEVELS must contain V8."
    )
    assert not re.search(r'PROTOCOL_LEVELS\s*=\s*\[[^\]]*"V5a"[^\]]*\]', text, re.S), (
        "claim_gate.py PROTOCOL_LEVELS must not contain V5a."
    )
    assert not re.search(r'PROTOCOL_LEVELS\s*=\s*\[[^\]]*"V5b"[^\]]*\]', text, re.S), (
        "claim_gate.py PROTOCOL_LEVELS must not contain V5b."
    )


def test_verify_md_30_second_is_minimal_v2_not_full_coverage() -> None:
    text = read("verify.md")

    assert re.search(r"30-Second[\s\S]{0,300}(Minimal V2|minimal\s+V2|B1)", text, re.I), (
        "30-second section must identify the result as minimal V2 / B1."
    )
    assert re.search(r"30-Second[\s\S]{0,2000}(not full reference coverage|not.*full.*coverage|limitations)", text, re.I), (
        "30-second section must say the check is not full reference coverage and must list limitations."
    )
    # Ensure the 30-second section says it is not full reference coverage
    assert re.search(r"not full reference coverage|not.*full.*coverage", text, re.I), (
        "30-second section must say the check is not full reference coverage."
    )


def test_verify_md_uses_v8_sections_not_v5a_v5b() -> None:
    assert_absent("verify.md", r"###\s*V5a\b", "verify.md must not define V5a.")
    assert_absent("verify.md", r"###\s*V5b\b", "verify.md must not define V5b.")
    assert_present("verify.md", r"###\s*V5\b[\s\S]{0,200}Full Public Digital", "verify.md must define formal V5.")
    assert_present("verify.md", r"###\s*V6\b[\s\S]{0,200}Remote Physical", "verify.md must define formal V6.")
    assert_present("verify.md", r"###\s*V7\b[\s\S]{0,200}Onsite Physical", "verify.md must define formal V7.")
    assert_present("verify.md", r"###\s*V8\b[\s\S]{0,250}Forensic Physical", "verify.md must define formal V8.")


def test_agent_verify_uses_a_levels_for_orientation() -> None:
    text = read("agent-verify.md")
    forbidden = [
        r"\|\s*V3\s*\|\s*Single artifact check\s*\|",
        r"\|\s*V6\s*\|\s*Independent node\s*/\s*RPC check\s*\|",
        r"V3_single_artifact_check",
    ]
    for pat in forbidden:
        assert not re.search(pat, text, re.I), f"agent-verify.md still has conflicting V-level shorthand: {pat}"

    if "Single artifact check" in text:
        assert re.search(r"\|\s*A3\s*\|\s*Single artifact check\s*\|", text), (
            "Single artifact orientation must use A3 or another non-V label."
        )
        assert re.search(r"A-levels.*not.*protocol V-levels|formal V0.*V8", text, re.I | re.S), (
            "A-level ladder must explicitly say it is not the formal V0–V8 protocol ladder."
        )


def test_quick_map_preserves_v8_formal_mappings_with_notes() -> None:
    data = load_json("api/verification-quick-map.json")
    entries = data["entries"]

    def find_entry(fragment: str):
        for e in entries:
            if fragment.lower() in e.get("question", "").lower():
                return e
        raise AssertionError(f"Could not find quick-map entry containing: {fragment}")

    bitcoin = find_entry("Bitcoin Originals exist")
    assert "V2" in bitcoin.get("levels", []), "Bitcoin reference quick-map may keep V2 under formal minimal profile."
    assert "protocol_note" in bitcoin and "full reference" in bitcoin["protocol_note"].lower(), (
        "Bitcoin V2 quick-map entry must distinguish minimal V2 from full reference coverage."
    )

    github_hash = find_entry("public mirror data without Arweave")
    assert "V3" in github_hash.get("levels", []), "Hash quick-map may keep V3 under formal minimal profile."
    assert "protocol_note" in github_hash and "full public digital" in github_hash["protocol_note"].lower(), (
        "V3 quick-map entry must distinguish minimal hash verification from full public digital verification."
    )

    live = find_entry("live physical witness")
    assert "V6" in live.get("levels", []), "Live remote physical witness must map to formal V6."
    assert "protocol_note" in live and "recorded video" in live["protocol_note"].lower(), (
        "V6 quick-map entry must say recorded video alone is insufficient."
    )

    onsite = find_entry("onsite witness")
    assert "V7" in onsite.get("levels", []), "Onsite witness must map to formal V7."

    forensic = find_entry("highest physical verification path")
    assert "V8" in forensic.get("levels", []), "Forensic physical path must map to formal V8."

    vlevel = find_entry("V-level claim")
    assert vlevel.get("levels") == FORMAL_PROTOCOL_LEVELS, (
        f"V-level quick-map entry must use formal V8 levels, got {vlevel.get('levels')}"
    )


def test_verification_materials_official_scripts_not_sufficient_for_v4plus() -> None:
    text = read("verification-materials.md")
    scripts = [
        "verify-full-evidence-chain.mjs",
        "summarize-evidence-chain.mjs",
        "ta-verify.cjs",
        "verify-batch-strict.mjs",
    ]

    for script in scripts:
        idx = text.find(script)
        if idx < 0:
            continue
        excerpt = text[idx:idx + 650]
        if "V4+" in excerpt:
            assert re.search(r"official scripts alone|do not establish|supports V4|inputs for V4\+", excerpt, re.I), (
                f"{script} mentions V4+ without limitation that official scripts alone do not establish V4+."
            )


def test_covenant_proof_hash_and_physical_labels() -> None:
    assert_absent(
        "covenant-proof.md",
        r"SHA-256:\s*`?[a-f0-9]{6,16}\.\.\.`?",
        "covenant-proof.md must not present truncated SHA-256 as expected value.",
    )
    assert_present(
        "covenant-proof.md",
        r"(exact expected hash|full hash).*?(api/hashes\.json|api/evidence-manifest\.json)",
        "covenant-proof.md must direct verifiers to exact hash source.",
    )

    text = read("covenant-proof.md")
    if re.search(r"\bL[35]\b", text):
        assert re.search(r"Legacy label|deprecated|not protocol V|P1|P3|P5|P9", text, re.I), (
            "Legacy L3/L5 labels must be mapped or explicitly deprecated."
        )


def make_evidence_input(evidence, claims=None, requested_kind="verification_report_v2"):
    return {
        "schema": "trinityaccord.evidence-input.v1",
        "agent": {"name": "V8 Formal Consistency Test Agent", "model_or_system": "test"},
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


def test_claim_gate_minimal_v2_from_external_reference() -> None:
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
    assert result["allowed_protocol_level"] == "V2", (
        f"Formal V8 system allows minimal V2 from external reference check; got {result['allowed_protocol_level']}"
    )
    assert result["allowed_component_levels"].get("bitcoin_originals") == "B1", (
        f"Expected bitcoin_originals B1, got {result['allowed_component_levels']}"
    )


def test_claim_gate_minimal_v3_from_one_valid_hash() -> None:
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
    assert result["allowed_protocol_level"] == "V3", (
        f"Formal V8 system allows minimal V3 from one valid hash; got {result['allowed_protocol_level']}"
    )


def test_claim_gate_v6_from_live_remote_p4() -> None:
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
    assert result["allowed_protocol_level"] == "V6", (
        f"Formal V8 system maps P4 live remote witness with all hard gates to V6; got {result['allowed_protocol_level']}"
    )
    components = result.get("allowed_component_levels", {})
    assert components.get("physical_anchor") == "P4" or components.get("physical_verification") == "P4", (
        f"Expected P4 physical component, got {components}"
    )


def test_claim_gate_v7_from_onsite_p5() -> None:
    payload = make_evidence_input(
        evidence={
            "physical_checks": [
                {
                    "level_evidence_type": "onsite",
                    "custody_log": {"present": True},
                    "fresh_capture": True,
                    "witness_identity_or_role": "onsite verifier",
                }
            ]
        },
        claims=["V7"],
    )
    result = evaluate_claim_gate(payload)
    assert result["allowed_protocol_level"] == "V7", (
        f"Formal V8 system maps P5 onsite witness with all hard gates to V7; got {result['allowed_protocol_level']}"
    )


def main() -> None:
    tests = [
        test_formal_protocol_levels_match_everywhere,
        test_no_stale_v5a_v5b_in_protocol_sources,
        test_claim_gate_code_uses_v8_formal_levels,
        test_verify_md_30_second_is_minimal_v2_not_full_coverage,
        test_verify_md_uses_v8_sections_not_v5a_v5b,
        test_agent_verify_uses_a_levels_for_orientation,
        test_quick_map_preserves_v8_formal_mappings_with_notes,
        test_verification_materials_official_scripts_not_sufficient_for_v4plus,
        test_covenant_proof_hash_and_physical_labels,
        test_claim_gate_minimal_v2_from_external_reference,
        test_claim_gate_minimal_v3_from_one_valid_hash,
        test_claim_gate_v6_from_live_remote_p4,
        test_claim_gate_v7_from_onsite_p5,
    ]

    for test in tests:
        test()

    print("V8_FORMAL_VERIFICATION_CONSISTENCY_OK")


if __name__ == "__main__":
    main()
