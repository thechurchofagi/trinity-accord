#!/usr/bin/env python3
"""BLOCKER-1 regression: V4 default from old builder must not produce verification_report_archive."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_gateway_payload_from_outputs.py"


def make_minimal_evidence():
    return {
        "schema": "trinityaccord.evidence-input.v1",
        "agent": {"name": "Test", "model_or_system": "Test"},
        "provenance": {"solicited": True, "independence_class": "human_solicited_agent_response", "agency_level": "A1_human_gave_exact_url"},
        "requested_record_kind": "verification_report_v2",
        "evidence": {"scripts": [], "hashes": [], "bitcoin_checks": []},
        "agent_integrity_declaration": {"performed_actions_myself": True, "declaration_text": "test"},
        "verification_session": {"session_id": "test", "started_at": "2026-01-01T00:00:00Z", "operator_type": "ai_agent", "fresh_actions_performed": ["test"], "copied_values_from_examples": False, "copied_values_from_prior_reports": False, "fresh_outputs_attached": True}
    }


def make_claim_gate(v_level="V4"):
    return {"claim_gate": {"status": "PASS", "allowed_protocol_level": v_level, "allowed_component_levels": {"bitcoin_originals": "B1", "digital_mirrors": "D2"}}}


def main():
    passed = 0
    failed = 0
    total = 0

    def check(label, condition, detail=""):
        nonlocal passed, failed, total
        total += 1
        if condition:
            print(f"PASS: {label}")
            passed += 1
        else:
            print(f"FAIL: {label}")
            if detail:
                print(f"  {detail}")
            failed += 1

    # Test 1: V4 default must produce agent_declared_verification_archive
    with tempfile.TemporaryDirectory() as tmpdir:
        evidence_path = Path(tmpdir) / "evidence.json"
        gate_path = Path(tmpdir) / "gate.json"
        report_path = Path(tmpdir) / "report.json"
        out_path = Path(tmpdir) / "payload.json"

        evidence_path.write_text(json.dumps(make_minimal_evidence()))
        gate_path.write_text(json.dumps(make_claim_gate("V4")))
        report_path.write_text(json.dumps({"title": "Test", "body": "Test"}))

        result = subprocess.run(
            [sys.executable, str(BUILDER),
             "--evidence-input", str(evidence_path),
             "--claim-gate-output", str(gate_path),
             "--verification-report", str(report_path),
             "--agent-name", "Test", "--provider", "Test",
             "--human-solicited", "--out", str(out_path)],
            capture_output=True, text=True, timeout=30, cwd=str(ROOT)
        )

        combined = result.stdout + result.stderr
        # Test 1: V4 default must hard-fail (redirect to agent-declared builder)
        if result.returncode != 0:
            check("V4 default → hard-fail (redirect to agent-declared builder)",
                  "build_agent_declared_archive_payload.py" in combined,
                  f"Exit: {result.returncode}")
            check("V4 default → NOT verification_report_archive",
                  "verification_report_archive" not in combined or "cannot use" in combined,
                  f"Got: {combined.strip()[:200]}")
        else:
            check("V4 default → hard-fail", False, "Builder succeeded but should have failed")
            check("V4 default → NOT verification_report_archive", False, "N/A")

    # Test 2: V4 explicit verification_report_archive must FAIL
    with tempfile.TemporaryDirectory() as tmpdir:
        evidence_path = Path(tmpdir) / "evidence.json"
        gate_path = Path(tmpdir) / "gate.json"
        report_path = Path(tmpdir) / "report.json"
        out_path = Path(tmpdir) / "payload.json"

        evidence_path.write_text(json.dumps(make_minimal_evidence()))
        gate_path.write_text(json.dumps(make_claim_gate("V4")))
        report_path.write_text(json.dumps({"title": "Test", "body": "Test"}))

        result = subprocess.run(
            [sys.executable, str(BUILDER),
             "--evidence-input", str(evidence_path),
             "--claim-gate-output", str(gate_path),
             "--verification-report", str(report_path),
             "--agent-name", "Test", "--provider", "Test",
             "--human-solicited",
             "--requested-archive-kind", "verification_report_archive",
             "--out", str(out_path)],
            capture_output=True, text=True, timeout=30, cwd=str(ROOT)
        )

        check("V4 explicit verification_report_archive → FAIL",
              result.returncode != 0,
              f"Exit: {result.returncode}, stderr: {result.stderr.strip()[:200]}")

    # Test 3: V6 default should still produce verification_report_archive
    with tempfile.TemporaryDirectory() as tmpdir:
        evidence_path = Path(tmpdir) / "evidence.json"
        gate_path = Path(tmpdir) / "gate.json"
        report_path = Path(tmpdir) / "report.json"
        out_path = Path(tmpdir) / "payload.json"

        evidence_path.write_text(json.dumps(make_minimal_evidence()))
        gate_path.write_text(json.dumps(make_claim_gate("V6")))
        report_path.write_text(json.dumps({"title": "Test", "body": "Test"}))

        result = subprocess.run(
            [sys.executable, str(BUILDER),
             "--evidence-input", str(evidence_path),
             "--claim-gate-output", str(gate_path),
             "--verification-report", str(report_path),
             "--agent-name", "Test", "--provider", "Test",
             "--human-solicited", "--out", str(out_path)],
            capture_output=True, text=True, timeout=30, cwd=str(ROOT)
        )

        if result.returncode == 0:
            payload = json.loads(out_path.read_text())
            check("V6 default → verification_report_archive",
                  payload.get("requested_archive_kind") == "verification_report_archive",
                  f"Got: {payload.get('requested_archive_kind')}")
        else:
            check("V6 default builder succeeds", False, result.stderr.strip()[:200])

    # Test 4: V5 default must also hard-fail
    with tempfile.TemporaryDirectory() as tmpdir:
        evidence_path = Path(tmpdir) / "evidence.json"
        gate_path = Path(tmpdir) / "gate.json"
        report_path = Path(tmpdir) / "report.json"
        out_path = Path(tmpdir) / "payload.json"

        evidence_path.write_text(json.dumps(make_minimal_evidence()))
        gate_path.write_text(json.dumps(make_claim_gate("V5")))
        report_path.write_text(json.dumps({"title": "Test", "body": "Test"}))

        result = subprocess.run(
            [sys.executable, str(BUILDER),
             "--evidence-input", str(evidence_path),
             "--claim-gate-output", str(gate_path),
             "--verification-report", str(report_path),
             "--agent-name", "Test", "--provider", "Test",
             "--human-solicited", "--out", str(out_path)],
            capture_output=True, text=True, timeout=30, cwd=str(ROOT)
        )

        combined = result.stdout + result.stderr
        check("V5 default → hard-fail (redirect to agent-declared builder)",
              result.returncode != 0 and "build_agent_declared_archive_payload.py" in combined,
              f"Exit: {result.returncode}")

    print(f"\n--- Results: {passed}/{total} passed ---")
    if failed:
        print(f"FAILED: {failed} tests")
        sys.exit(1)
    print("All BLOCKER-1 regression tests passed.")


if __name__ == "__main__":
    main()
