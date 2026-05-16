#!/usr/bin/env python3
"""Tests for Gateway archive pipeline reordering and defaults.

P0-4 test cases:
- default_report_candidate_missing_intent_blocks_archive
- explicit_intake_only_report_candidate_passes_intake
- archive_ready_issue_body_must_contain_archive_ready_true

Also covers P0-1/P0-2/P0-3 regression checks.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd, **kwargs):
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=str(ROOT), **kwargs)
    return result.returncode, result.stdout, result.stderr


def make_minimal_evidence():
    """Create minimal valid evidence input."""
    return {
        "schema": "trinityaccord.evidence-input.v1",
        "agent": {"name": "Test", "model_or_system": "Test"},
        "provenance": {
            "solicited": True,
            "independence_class": "human_solicited_agent_response",
            "agency_level": "A1_human_gave_exact_url"
        },
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
            "declaration_text": "I declare that I performed all checks myself."
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


def make_claim_gate(v_level="V3", b_level="B1", status="PASS"):
    return {
        "claim_gate": {
            "status": status,
            "allowed_protocol_level": v_level,
            "allowed_component_levels": {
                "bitcoin_originals": b_level,
                "digital_mirrors": "D2"
            }
        }
    }


def build_payload(tmpdir, record_intent=None, requested_archive_kind=None):
    """Build a gateway payload using build_gateway_payload_from_outputs.py."""
    evidence_path = Path(tmpdir) / "evidence.json"
    gate_path = Path(tmpdir) / "gate.json"
    report_path = Path(tmpdir) / "report.json"
    out_path = Path(tmpdir) / "payload.json"

    evidence_path.write_text(json.dumps(make_minimal_evidence()))
    gate_path.write_text(json.dumps(make_claim_gate()))
    report_path.write_text(json.dumps({"title": "Test", "body": "Test"}))

    cmd = [
        sys.executable, "scripts/build_gateway_payload_from_outputs.py",
        "--evidence-input", str(evidence_path),
        "--claim-gate-output", str(gate_path),
        "--verification-report", str(report_path),
        "--agent-name", "Test",
        "--provider", "Test",
        "--session-id", "test",
        "--human-solicited",
        "--out", str(out_path)
    ]
    if record_intent:
        cmd.extend(["--record-intent", record_intent])
    if requested_archive_kind:
        cmd.extend(["--requested-archive-kind", requested_archive_kind])

    code, stdout, stderr = run(cmd)
    if code != 0:
        raise RuntimeError(f"build failed: {stderr or stdout}")

    return json.loads(out_path.read_text())


def test_default_report_candidate_missing_intent_blocks_archive():
    """P0-4: A verification_report_candidate with no explicit record_intent
    should be normalized to auto_archive_candidate by the pipeline.
    Without archive readiness (no artifact bundle, etc.), it should be blocked.

    This also validates P0-2: the endpoint no longer forces intake_only defaults.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Build payload WITHOUT explicit record_intent (should auto-infer)
        payload = build_payload(tmpdir)

        # Verify the payload does NOT have record_intent set by the builder
        # (builder defaults to auto_archive_candidate, but the endpoint should
        # not force intake_only)
        assert payload.get("record_intent") == "auto_archive_candidate", \
            f"Expected auto_archive_candidate, got {payload.get('record_intent')}"

        # Run archive readiness gate
        payload_path = Path(tmpdir) / "payload.json"
        payload_path.write_text(json.dumps(payload))

        code, stdout, stderr = run([
            sys.executable, "scripts/archive_readiness_gate.py",
            "--gateway-payload", str(payload_path),
            "--json"
        ])

        result = json.loads(stdout)
        # Should be blocked because no artifact bundle, no integrity declaration, etc.
        assert result["archive_ready"] is False, \
            f"Expected archive_ready=False, got {result['archive_ready']}"
        assert result["record_intent"] == "auto_archive_candidate", \
            f"Expected auto_archive_candidate, got {result['record_intent']}"
        assert len(result["blocking_reasons"]) > 0, "Expected blocking reasons"

        print("PASS: default_report_candidate_missing_intent_blocks_archive")
        return True


def test_explicit_intake_only_report_candidate_passes_intake():
    """P0-4: A verification_report_candidate with explicit record_intent=intake_only
    should pass intake (archive_ready=false is fine, intake proceeds).
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        payload = build_payload(tmpdir, record_intent="intake_only",
                                requested_archive_kind="none")

        assert payload.get("record_intent") == "intake_only"
        assert payload.get("requested_archive_kind") == "none"

        payload_path = Path(tmpdir) / "payload.json"
        payload_path.write_text(json.dumps(payload))

        # Run archive readiness gate
        code, stdout, stderr = run([
            sys.executable, "scripts/archive_readiness_gate.py",
            "--gateway-payload", str(payload_path),
            "--json"
        ])

        result = json.loads(stdout)
        # Intake-only: archive_ready is false but that's expected
        assert result["archive_ready"] is False
        assert result["record_intent"] == "intake_only"
        assert result["requested_archive_kind"] == "none"
        # No blocking reasons for intake-only (it returns early with warnings)
        assert len(result["blocking_reasons"]) == 0, \
            f"Intake-only should have no blocking reasons, got {result['blocking_reasons']}"
        # Exit code should be 0 (intake-only passes)
        assert code == 0, f"Expected exit 0 for intake-only, got {code}"

        print("PASS: explicit_intake_only_report_candidate_passes_intake")
        return True


def test_archive_ready_issue_body_contains_archive_ready_true():
    """P0-4: When a payload is archive-ready, the rendered issue body must
    contain archive_ready: true in the trinity-issue-intake block.

    This validates P0-1: the renderer uses computed archive_readiness values.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Build a payload that can be archive-ready
        evidence_path = Path(tmpdir) / "evidence.json"
        gate_path = Path(tmpdir) / "gate.json"
        report_path = Path(tmpdir) / "report.json"
        out_path = Path(tmpdir) / "payload.json"

        evidence = make_minimal_evidence()
        # Add required fields for archive readiness
        evidence["agent_integrity_declaration"]["declaration_text"] = "Full declaration"
        evidence_path.write_text(json.dumps(evidence))

        gate = make_claim_gate()
        gate_path.write_text(json.dumps(gate))
        report_path.write_text(json.dumps({"title": "Test", "body": "Test"}))

        # Build with explicit intake_only first (to get a valid payload)
        code, stdout, stderr = run([
            sys.executable, "scripts/build_gateway_payload_from_outputs.py",
            "--evidence-input", str(evidence_path),
            "--claim-gate-output", str(gate_path),
            "--verification-report", str(report_path),
            "--agent-name", "Test",
            "--provider", "Test",
            "--session-id", "test",
            "--human-solicited",
            "--intake-only",
            "--out", str(out_path)
        ])
        assert code == 0, f"Build failed: {stderr}"

        payload = json.loads(out_path.read_text())

        # Switch to auto_archive_candidate with verification_report_archive
        payload["record_intent"] = "auto_archive_candidate"
        payload["requested_archive_kind"] = "verification_report_archive"

        # Add required archive readiness fields
        payload["pre_verification_integrity_declaration"] = {
            "declaration_text": "I declare integrity.",
            "declared_at": "2026-05-16T00:00:00Z"
        }
        payload["verification_session"] = {
            "session_id": "test-001",
            "started_at": "2026-05-16T00:00:00Z",
            "fresh_actions_performed": ["test"]
        }
        payload["archive_readiness"] = {
            "artifact_bundle_path": "https://example.com/bundle.tar.gz",
            "artifact_bundle_sha256": "a" * 64,
            "artifact_bundle_publicly_retrievable": True
        }

        payload_path = Path(tmpdir) / "payload.json"
        payload_path.write_text(json.dumps(payload))

        # Run archive readiness gate to get computed values
        code, stdout, stderr = run([
            sys.executable, "scripts/archive_readiness_gate.py",
            "--gateway-payload", str(payload_path),
            "--json"
        ])
        readiness = json.loads(stdout)

        # Inject computed values into payload (simulating P0-1 pipeline reorder)
        payload["archive_readiness"] = readiness
        if readiness.get("record_intent"):
            payload["record_intent"] = readiness["record_intent"]
        if readiness.get("requested_archive_kind"):
            payload["requested_archive_kind"] = readiness["requested_archive_kind"]
        payload_path.write_text(json.dumps(payload))

        # Render issue body
        code, stdout, stderr = run([
            sys.executable, "scripts/render_gateway_issue_body.py",
            str(payload_path)
        ])
        assert code == 0, f"Render failed: {stderr}"

        body = stdout
        # Check that archive_ready: true appears in the rendered body
        assert "archive_ready: true" in body, \
            f"Expected 'archive_ready: true' in rendered body, got:\n{body}"

        print("PASS: archive_ready_issue_body_contains_archive_ready_true")
        return True


def test_normalize_archive_intent_no_forced_defaults():
    """P0-2 regression: normalizeArchiveIntentDefaults should not force
    intake_only when record_intent is missing — it should infer from submission_type.
    """
    # Simulate what normalizeArchiveIntentDefaults does in Python
    # (testing the same logic as the JS function)
    sys.path.insert(0, str(ROOT / "scripts"))
    from archive_readiness_gate import normalize_archive_intent

    # Case 1: No record_intent, verification_report_candidate → should infer auto_archive_candidate
    payload = {"submission_type": "verification_report_candidate"}
    result = normalize_archive_intent(payload)
    assert result["record_intent"] == "auto_archive_candidate", \
        f"Expected auto_archive_candidate, got {result['record_intent']}"
    assert result["requested_archive_kind"] == "verification_report_archive", \
        f"Expected verification_report_archive, got {result['requested_archive_kind']}"

    # Case 2: No record_intent, unknown submission_type → should default to intake_only
    payload2 = {"submission_type": "unknown_type"}
    result2 = normalize_archive_intent(payload2)
    assert result2["record_intent"] == "intake_only"
    assert result2["requested_archive_kind"] == "none"

    # Case 3: Explicit intake_only → should stay intake_only
    payload3 = {
        "submission_type": "verification_report_candidate",
        "record_intent": "intake_only"
    }
    result3 = normalize_archive_intent(payload3)
    assert result3["record_intent"] == "intake_only"
    assert result3["requested_archive_kind"] == "none"

    print("PASS: normalize_archive_intent_no_forced_defaults")
    return True


def main():
    tests = [
        test_default_report_candidate_missing_intent_blocks_archive,
        test_explicit_intake_only_report_candidate_passes_intake,
        test_archive_ready_issue_body_contains_archive_ready_true,
        test_normalize_archive_intent_no_forced_defaults,
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
            import traceback
            traceback.print_exc()
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed out of {len(tests)}")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
