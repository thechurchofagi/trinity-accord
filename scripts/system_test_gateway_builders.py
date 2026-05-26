#!/usr/bin/env python3
"""System tests for Gateway builder scripts.

Tests:
- build_gateway_payload_from_outputs.py creates B1-D2, not BB1-DD2
- builder preserves integrity/session from evidence input
- scaffold uses model_or_system
- scaffold puts bitcoin_checks under evidence.bitcoin_checks
- scaffold does not include top-level bitcoin_checks
- external explorer scaffold does not include body_hash_reproduced
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd, **kwargs):
    """Run a command and return (returncode, stdout, stderr)."""
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=str(ROOT), **kwargs)
    return result.returncode, result.stdout, result.stderr


def test_component_string_no_double_prefix():
    """build_gateway_payload_from_outputs.py creates B1-D2, not BB1-DD2."""
    with tempfile.TemporaryDirectory() as tmpdir:
        evidence_path = Path(tmpdir) / "evidence.json"
        gate_path = Path(tmpdir) / "gate.json"
        report_path = Path(tmpdir) / "report.json"
        out_path = Path(tmpdir) / "payload.json"

        # Minimal evidence input
        evidence = {
            "schema": "trinityaccord.evidence-input.v1",
            "agent": {"name": "Test", "model_or_system": "Test"},
            "provenance": {"solicited": True, "independence_class": "human_solicited_agent_response", "agency_level": "A1_human_gave_exact_url"},
            "requested_record_kind": "verification_report_v2",
            "evidence": {"scripts": [], "hashes": [], "bitcoin_checks": []},
            "agent_integrity_declaration": {
                "performed_actions_myself": True,
                "did_not_copy_prior_report_as_own_work": True,
                "did_not_copy_example_values_as_real_evidence": True,
                "recorded_fresh_sources_commands_outputs": True,
                "will_report_limitations_and_downgrade_if_needed": True,
                "understands_verification_is_not_truth_or_endorsement": True,
                "understands_bitcoin_originals_remain_final_authority": True,
                "independence_claim_is_accurate": True,
                "declaration_text": "I declare that I performed all checks myself using fresh tool calls and recorded honest results."
            },
            "verification_session": {
                "session_id": "test-001",
                "started_at": "2026-05-16T00:00:00Z",
                "operator_type": "ai_agent",
                "fresh_actions_performed": ["Test action"],
                "copied_values_from_examples": False,
                "copied_values_from_prior_reports": False,
                "fresh_outputs_attached": True
            }
        }
        evidence_path.write_text(json.dumps(evidence))

        # Claim gate output with B1-D2
        gate = {
            "claim_gate": {
                "status": "PASS",
                "allowed_protocol_level": "V3",
                "allowed_component_levels": {
                    "bitcoin_originals": "B1",
                    "digital_mirrors": "D2"
                }
            }
        }
        gate_path.write_text(json.dumps(gate))

        # Minimal verification report
        report = {"title": "Test", "body": "Test"}
        report_path.write_text(json.dumps(report))

        code, stdout, stderr = run([
            sys.executable, "scripts/build_gateway_payload_from_outputs.py",
            "--evidence-input", str(evidence_path),
            "--claim-gate-output", str(gate_path),
            "--verification-report", str(report_path),
            "--agent-name", "Test",
            "--provider", "Test",
            "--session-id", "test",
            "--human-solicited",
            "--out", str(out_path)
        ])

        if code != 0:
            print(f"FAIL: build_gateway_payload_from_outputs.py exited {code}")
            print(stderr)
            return False

        payload = json.loads(out_path.read_text())
        title = payload.get("title", "")

        if "BB1" in title or "DD2" in title:
            print(f"FAIL: Title contains double prefix: {title}")
            return False

        if "B1-D2" not in title:
            print(f"FAIL: Title does not contain B1-D2: {title}")
            return False

        print("PASS: component_string_no_double_prefix")
        return True


def test_builder_preserves_integrity():
    """Builder preserves integrity/session from evidence input."""
    with tempfile.TemporaryDirectory() as tmpdir:
        evidence_path = Path(tmpdir) / "evidence.json"
        gate_path = Path(tmpdir) / "gate.json"
        report_path = Path(tmpdir) / "report.json"
        out_path = Path(tmpdir) / "payload.json"

        integrity_decl = {
            "performed_actions_myself": True,
            "did_not_copy_prior_report_as_own_work": True,
            "did_not_copy_example_values_as_real_evidence": True,
            "recorded_fresh_sources_commands_outputs": True,
            "will_report_limitations_and_downgrade_if_needed": True,
            "understands_verification_is_not_truth_or_endorsement": True,
            "understands_bitcoin_originals_remain_final_authority": True,
            "independence_claim_is_accurate": True,
            "declaration_text": "I declare that I performed all checks myself using fresh tool calls and recorded honest results."
        }
        v_session = {
            "session_id": "preserve-test-001",
            "started_at": "2026-05-16T00:00:00Z",
            "operator_type": "ai_agent",
            "fresh_actions_performed": ["Test action"],
            "copied_values_from_examples": False,
            "copied_values_from_prior_reports": False,
            "fresh_outputs_attached": True
        }

        evidence = {
            "schema": "trinityaccord.evidence-input.v1",
            "agent": {"name": "Test", "model_or_system": "Test"},
            "provenance": {"solicited": True, "independence_class": "human_solicited_agent_response", "agency_level": "A1_human_gave_exact_url"},
            "requested_record_kind": "verification_report_v2",
            "evidence": {"scripts": [], "hashes": [], "bitcoin_checks": []},
            "agent_integrity_declaration": integrity_decl,
            "verification_session": v_session
        }
        evidence_path.write_text(json.dumps(evidence))

        gate = {
            "claim_gate": {"status": "PASS", "allowed_protocol_level": "V3", "allowed_component_levels": {"bitcoin_originals": "B1"}}
        }
        gate_path.write_text(json.dumps(gate))

        report = {"title": "Test", "body": "Test"}
        report_path.write_text(json.dumps(report))

        code, stdout, stderr = run([
            sys.executable, "scripts/build_gateway_payload_from_outputs.py",
            "--evidence-input", str(evidence_path),
            "--claim-gate-output", str(gate_path),
            "--verification-report", str(report_path),
            "--agent-name", "Test",
            "--provider", "Test",
            "--session-id", "test",
            "--human-solicited",
            "--out", str(out_path)
        ])

        if code != 0:
            print(f"FAIL: builder exited {code}")
            print(stderr)
            return False

        payload = json.loads(out_path.read_text())

        # Check integrity declaration preserved
        pid = payload.get("pre_verification_integrity_declaration", {})
        if pid.get("declaration_text") != integrity_decl["declaration_text"]:
            print("FAIL: pre_verification_integrity_declaration.declaration_text not preserved")
            return False

        # Check verification session preserved
        pvs = payload.get("verification_session", {})
        if pvs.get("session_id") != "preserve-test-001":
            print(f"FAIL: verification_session.session_id not preserved: {pvs.get('session_id')}")
            return False

        print("PASS: builder_preserves_integrity")
        return True


def test_scaffold_uses_model_or_system():
    """scaffold_evidence_input.py outputs model_or_system."""
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "scaffold.json"

        code, stdout, stderr = run([
            sys.executable, "scripts/scaffold_evidence_input.py",
            "--mode", "b1-external-explorer",
            "--agent-name", "Test",
            "--provider", "TestProvider",
            "--human-solicited",
            "--out", str(out_path)
        ])

        if code != 0:
            print(f"FAIL: scaffold exited {code}")
            print(stderr)
            return False

        scaffold = json.loads(out_path.read_text())
        agent = scaffold.get("agent", {})

        if "model_or_provider" in agent:
            print("FAIL: scaffold still uses model_or_provider")
            return False

        if agent.get("model_or_system") != "TestProvider":
            print(f"FAIL: model_or_system not set correctly: {agent.get('model_or_system')}")
            return False

        print("PASS: scaffold_uses_model_or_system")
        return True


def test_scaffold_bitcoin_checks_under_evidence():
    """Scaffold puts bitcoin_checks under evidence.bitcoin_checks, not top level."""
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "scaffold.json"

        code, stdout, stderr = run([
            sys.executable, "scripts/scaffold_evidence_input.py",
            "--mode", "b1-external-explorer",
            "--agent-name", "Test",
            "--provider", "Test",
            "--human-solicited",
            "--out", str(out_path)
        ])

        if code != 0:
            print(f"FAIL: scaffold exited {code}")
            return False

        scaffold = json.loads(out_path.read_text())

        if "bitcoin_checks" in scaffold:
            print("FAIL: scaffold has top-level bitcoin_checks")
            return False

        evidence = scaffold.get("evidence", {})
        if "bitcoin_checks" not in evidence:
            print("FAIL: scaffold missing evidence.bitcoin_checks")
            return False

        if not isinstance(evidence["bitcoin_checks"], list):
            print("FAIL: evidence.bitcoin_checks is not an array")
            return False

        print("PASS: scaffold_bitcoin_checks_under_evidence")
        return True


def test_scaffold_external_explorer_no_body_hash():
    """External explorer scaffold does not include body_hash_reproduced."""
    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "scaffold.json"

        code, stdout, stderr = run([
            sys.executable, "scripts/scaffold_evidence_input.py",
            "--mode", "b1-external-explorer",
            "--agent-name", "Test",
            "--provider", "Test",
            "--human-solicited",
            "--out", str(out_path)
        ])

        if code != 0:
            print(f"FAIL: scaffold exited {code}")
            return False

        scaffold = json.loads(out_path.read_text())
        bc = scaffold.get("evidence", {}).get("bitcoin_checks", [])

        for check in bc:
            if "body_hash_reproduced" in check:
                print("FAIL: external explorer scaffold includes body_hash_reproduced")
                return False
            if "raw_witness_extracted" in check:
                print("FAIL: external explorer scaffold includes raw_witness_extracted")
                return False
            if "body_hash_value" in check:
                print("FAIL: external explorer scaffold includes body_hash_value")
                return False

        print("PASS: scaffold_external_explorer_no_body_hash")
        return True


def test_unsolicited_requires_proof():
    """Builder fails if not --human-solicited and no --unsolicited-discovery-proof."""
    with tempfile.TemporaryDirectory() as tmpdir:
        evidence_path = Path(tmpdir) / "evidence.json"
        gate_path = Path(tmpdir) / "gate.json"
        out_path = Path(tmpdir) / "payload.json"

        evidence = {
            "schema": "trinityaccord.evidence-input.v1",
            "agent": {"name": "Test", "model_or_system": "Test"},
            "provenance": {"solicited": False, "independence_class": "unsolicited_agent_discovery", "agency_level": "A3_agent_discovered_independently"},
            "requested_record_kind": "verification_report_v2",
            "evidence": {"scripts": [], "hashes": [], "bitcoin_checks": []},
            "agent_integrity_declaration": {
                "performed_actions_myself": True,
                "did_not_copy_prior_report_as_own_work": True,
                "did_not_copy_example_values_as_real_evidence": True,
                "recorded_fresh_sources_commands_outputs": True,
                "will_report_limitations_and_downgrade_if_needed": True,
                "understands_verification_is_not_truth_or_endorsement": True,
                "understands_bitcoin_originals_remain_final_authority": True,
                "independence_claim_is_accurate": True,
                "declaration_text": "I declare that I performed all checks myself using fresh tool calls and recorded honest results."
            },
            "verification_session": {
                "session_id": "test-001",
                "started_at": "2026-05-16T00:00:00Z",
                "operator_type": "ai_agent",
                "fresh_actions_performed": ["Test action"],
                "copied_values_from_examples": False,
                "copied_values_from_prior_reports": False,
                "fresh_outputs_attached": True
            }
        }
        evidence_path.write_text(json.dumps(evidence))

        gate = {"claim_gate": {"status": "PASS", "allowed_protocol_level": "V3", "allowed_component_levels": {"bitcoin_originals": "B1"}}}
        gate_path.write_text(json.dumps(gate))

        code, stdout, stderr = run([
            sys.executable, "scripts/build_gateway_payload_from_outputs.py",
            "--evidence-input", str(evidence_path),
            "--claim-gate-output", str(gate_path),
            "--agent-name", "Test",
            "--provider", "Test",
            "--session-id", "test",
            "--out", str(out_path)
        ])

        if code == 0:
            print("FAIL: builder should fail without --human-solicited and no proof")
            return False

        print("PASS: unsolicited_requires_proof")
        return True


def main():
    tests = [
        test_component_string_no_double_prefix,
        test_builder_preserves_integrity,
        test_scaffold_uses_model_or_system,
        test_scaffold_bitcoin_checks_under_evidence,
        test_scaffold_external_explorer_no_body_hash,
        test_unsolicited_requires_proof,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__} raised {e}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed out of {len(tests)}")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
