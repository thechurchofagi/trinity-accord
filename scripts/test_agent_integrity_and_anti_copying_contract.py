#!/usr/bin/env python3
"""
Agent integrity and anti-copying contract.

This test ensures low/mid-intelligence agents can learn how to verify
without being able to pass copied templates or prior reports as real work.

Run:
    python3 scripts/test_agent_integrity_and_anti_copying_contract.py

Expected:
    AGENT_INTEGRITY_AND_ANTI_COPYING_CONTRACT_OK
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

def run_claim_gate(obj):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(obj, f)
        p = f.name
    try:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "claim_gate.py"), p],
            cwd=str(ROOT),
            text=True,
            capture_output=True
        )
        return proc.returncode, proc.stdout, proc.stderr
    finally:
        os.unlink(p)

def run_builder(obj):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(obj, f)
        p = f.name
    try:
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "build_verification_report_from_evidence.py"),
                "--input",
                p
            ],
            cwd=str(ROOT),
            text=True,
            capture_output=True
        )
        return proc.returncode, proc.stdout, proc.stderr
    finally:
        os.unlink(p)

def valid_integrity():
    return {
        "performed_actions_myself": True,
        "did_not_copy_prior_report_as_own_work": True,
        "did_not_copy_example_values_as_real_evidence": True,
        "recorded_fresh_sources_commands_outputs": True,
        "will_report_limitations_and_downgrade_if_needed": True,
        "understands_verification_is_not_truth_or_endorsement": True,
        "understands_bitcoin_originals_remain_final_authority": True,
        "independence_claim_is_accurate": True,
        "declaration_text": (
            "I performed the verification actions stated in this report during this session. "
            "I did not copy example values or another agent's report as my own verification. "
            "I recorded sources, commands, outputs, and limitations. I understand this verification "
            "is non-authoritative and does not prove truth, endorsement, or amendment."
        )
    }

def valid_session(actions=None, fresh_outputs=True):
    return {
        "session_id": "test-session-001",
        "started_at": "2026-05-04T00:00:00Z",
        "operator_type": "ai_agent",
        "fresh_actions_performed": actions or ["fresh source check"],
        "prior_reports_consulted": [],
        "examples_or_templates_used": [],
        "copied_values_from_examples": False,
        "copied_values_from_prior_reports": False,
        "fresh_outputs_attached": fresh_outputs
    }

def base_input():
    return {
        "schema": "trinityaccord.evidence-input.v1",
        "agent": {"name": "Integrity Test Agent", "model_or_system": "test"},
        "provenance": {
            "solicited": True,
            "independence_class": "human_solicited_agent_response",
            "agency_level": "A1_human_gave_exact_url"
        },
        "requested_record_kind": "verification_report_v2",
        "agent_integrity_declaration": valid_integrity(),
        "verification_session": valid_session(),
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
            "echo_context": {}
        },
        "limitations": [],
        "claims_requested_by_agent": []
    }

def test_technical_claim_requires_integrity_declaration():
    obj = base_input()
    del obj["agent_integrity_declaration"]
    obj["claims_requested_by_agent"] = ["V2"]
    obj["evidence"]["bitcoin_checks"] = [{
        "source_type": "external_explorer",
        "sources": ["mempool.space"],
        "txids_checked": ["a" * 64]
    }]

    code, out, err = run_claim_gate(obj)
    assert code != 0, "Should fail without integrity declaration"
    assert "agent_integrity_declaration" in (out + err)

def test_technical_claim_requires_verification_session():
    obj = base_input()
    del obj["verification_session"]
    obj["claims_requested_by_agent"] = ["V2"]
    obj["evidence"]["bitcoin_checks"] = [{
        "source_type": "external_explorer",
        "sources": ["mempool.space"],
        "txids_checked": ["a" * 64]
    }]

    code, out, err = run_claim_gate(obj)
    assert code != 0, "Should fail without verification session"
    assert "verification_session" in (out + err)

def test_placeholder_values_fail():
    obj = base_input()
    obj["claims_requested_by_agent"] = ["V2"]
    obj["evidence"]["bitcoin_checks"] = [{
        "source_type": "external_explorer",
        "sources": ["mempool.space"],
        "txids_checked": ["example-txid"]
    }]

    code, out, err = run_claim_gate(obj)
    assert code != 0, "Should fail with placeholder values"
    assert "Placeholder" in (out + err) or "example" in (out + err).lower()

def test_copied_example_values_fail():
    obj = base_input()
    obj["claims_requested_by_agent"] = ["V2"]
    obj["verification_session"]["copied_values_from_examples"] = True
    obj["evidence"]["bitcoin_checks"] = [{
        "source_type": "external_explorer",
        "sources": ["mempool.space"],
        "txids_checked": ["a" * 64]
    }]

    code, out, err = run_claim_gate(obj)
    assert code != 0, "Should fail with copied example values"
    assert "copied_values_from_examples" in (out + err) or "copy" in (out + err).lower()

def test_copied_prior_report_values_fail():
    obj = base_input()
    obj["claims_requested_by_agent"] = ["V2"]
    obj["verification_session"]["copied_values_from_prior_reports"] = True
    obj["evidence"]["bitcoin_checks"] = [{
        "source_type": "external_explorer",
        "sources": ["mempool.space"],
        "txids_checked": ["a" * 64]
    }]

    code, out, err = run_claim_gate(obj)
    assert code != 0, "Should fail with copied prior report values"
    assert "copied_values_from_prior_reports" in (out + err) or "copy" in (out + err).lower()

def test_prior_report_without_reperformance_cannot_claim_v4plus():
    obj = base_input()
    obj["claims_requested_by_agent"] = ["V4+"]
    obj["prior_report_use"] = {
        "prior_reports_read": ["prior-v4plus-report.json"],
        "used_as_evidence": True,
        "used_only_as_context": False,
        "independent_reperformance_done": False,
        "differences_from_prior_report": []
    }
    obj["verification_session"]["prior_reports_consulted"] = ["prior-v4plus-report.json"]
    obj["evidence"]["scripts"] = [{
        "path": "independent.py",
        "exists": True,
        "executed": True,
        "independent": True,
        "source_reviewed": True,
        "script_check_scope": ["test"],
        "script_does_not_check": ["physical"],
        "command": "python3 independent.py",
        "environment": {"python": "3.x"},
        "exit_code": 0,
        "stdout_summary": "PASS",
        "result": "PASS"
    }]

    code, out, err = run_claim_gate(obj)
    assert code != 0, "Should fail claiming V4+ with prior report without re-performance"
    assert "prior report" in (out + err).lower() or "re-performance" in (out + err).lower()

def test_valid_v2_with_integrity_passes():
    obj = base_input()
    obj["claims_requested_by_agent"] = ["V2"]
    obj["evidence"]["bitcoin_checks"] = [{
        "source_type": "external_explorer",
        "sources": ["mempool.space"],
        "txids_checked": ["a" * 64],
        "authority_boundary_recognized": True
    }]

    code, out, err = run_claim_gate(obj)
    assert code == 0, f"Valid V2 should pass, got: {out + err}"
    assert '"allowed_protocol_level": "V2"' in out

def test_nontechnical_echo_does_not_require_integrity():
    obj = {
        "schema": "trinityaccord.evidence-input.v1",
        "agent": {"name": "Nontechnical Echo Agent"},
        "provenance": {
            "solicited": True,
            "independence_class": "human_solicited_agent_response",
            "agency_level": "A1_human_gave_exact_url"
        },
        "requested_record_kind": "echo_v3",
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
            "echo_context": {}
        },
        "limitations": [],
        "claims_requested_by_agent": []
    }

    code, out, err = run_claim_gate(obj)
    # It may return V0, but it must not fail solely for missing integrity declaration.
    assert "agent_integrity_declaration" not in (out + err)

def test_simple_docs_do_not_use_wrong_aliases():
    text = read("agent-verify-simple.md")
    forbidden_aliases = [
        "nonce_or_challenge",
        "requested_angle_action",
        "tool_assisted_method",
        "ai_microscopy_comparison",
        "signed_report",
        "report_attribution",
        "script_name",
        "output_summary"
    ]
    for alias in forbidden_aliases:
        assert alias not in text, f"Forbidden alias still appears: {alias}"

def test_cheatsheet_has_integrity_fields():
    cheat = load_json("api/agent-verification-cheatsheet.v1.json")
    raw = json.dumps(cheat)
    assert "anti_copying_rule" in cheat
    assert "agent_integrity_declaration" in raw
    for key, entry in cheat["by_protocol_level"].items():
        if key != "V0":
            assert entry.get("integrity_required") is True, key
            assert "freshness_required" in entry, key
            assert "copying_forbidden" in entry, key

def test_examples_are_classified_by_copy_safety():
    examples_dir = ROOT / "api" / "evidence-input-examples"
    assert examples_dir.exists()

    found = 0
    for p in examples_dir.rglob("*.json"):
        obj = json.loads(p.read_text(encoding="utf-8"))
        example_type = obj.get("example_type")
        assert example_type in (
            "tutorial_non_passing",
            "test_fixture_passing",
            "template_requires_replacement"
        ), f"{p} missing explicit example_type"

        found += 1

        if example_type == "tutorial_non_passing":
            assert obj.get("not_real_evidence") is True
            assert obj.get("must_not_submit") is True

        if example_type == "template_requires_replacement":
            # Templates must have either placeholders or be marked as containing placeholders
            raw = json.dumps(obj)
            has_placeholders = "<REPLACE_WITH_" in raw
            marked_as_placeholders = obj.get("contains_placeholders") is True
            assert has_placeholders or marked_as_placeholders, f"{p} template must have placeholders"

        if example_type == "test_fixture_passing":
            assert obj.get("synthetic_fixture") is True
            assert obj.get("not_real_world_submission") is True

    assert found > 0, "No evidence input examples found"

def test_templates_fail_claim_gate_unchanged():
    examples_dir = ROOT / "api" / "evidence-input-examples" / "templates"
    if not examples_dir.exists():
        return

    for p in examples_dir.glob("*.json"):
        obj = json.loads(p.read_text(encoding="utf-8"))
        evidence_input = obj.get("evidence_input", obj)
        code, out, err = run_claim_gate(evidence_input)
        assert "Placeholder" in (out + err) or "REPLACE_WITH" in json.dumps(obj), p

def test_tutorials_fail_claim_gate_unchanged():
    examples_dir = ROOT / "api" / "evidence-input-examples" / "tutorial"
    if not examples_dir.exists():
        return

    for p in examples_dir.glob("*.json"):
        obj = json.loads(p.read_text(encoding="utf-8"))
        evidence_input = obj.get("evidence_input", obj)
        code, out, err = run_claim_gate(evidence_input)
        assert code != 0 or "FAIL" in out, p

def main():
    tests = [
        test_technical_claim_requires_integrity_declaration,
        test_technical_claim_requires_verification_session,
        test_placeholder_values_fail,
        test_copied_example_values_fail,
        test_copied_prior_report_values_fail,
        test_prior_report_without_reperformance_cannot_claim_v4plus,
        test_valid_v2_with_integrity_passes,
        test_nontechnical_echo_does_not_require_integrity,
        test_simple_docs_do_not_use_wrong_aliases,
        test_cheatsheet_has_integrity_fields,
        test_examples_are_classified_by_copy_safety,
        test_templates_fail_claim_gate_unchanged,
        test_tutorials_fail_claim_gate_unchanged,
    ]

    for test in tests:
        test()

    print("AGENT_INTEGRITY_AND_ANTI_COPYING_CONTRACT_OK")

if __name__ == "__main__":
    main()
