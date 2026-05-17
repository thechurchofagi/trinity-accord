#!/usr/bin/env python3
"""Test that V0-V5 strict/intake submissions are rejected (fail-closed policy).

V0–V5 verification submissions are fail-closed:
they either pass as agent_declared_verification_archive and become archive-ready,
or they are rejected before Issue creation.
There is no V0–V5 strict/intake fallback.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_gateway_payload.py"
RENDERER = ROOT / "scripts" / "render_gateway_issue_body.py"

PASS = 0
FAIL = 0


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))


def write_payload(payload):
    f = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, dir=str(ROOT)
    )
    json.dump(payload, f, indent=2)
    f.close()
    return f.name


def assert_validator_fail_wrong_path(payload, label):
    global FAIL, PASS
    p = write_payload(payload)
    try:
        r = run([sys.executable, str(VALIDATOR), p])
        if r.returncode != 0 and "WRONG_PATH_FOR_V0_V5" in (r.stdout + r.stderr):
            PASS += 1
            print(f"  PASS: {label} — validator rejected with WRONG_PATH_FOR_V0_V5")
        else:
            FAIL += 1
            print(f"  FAIL: {label} — expected WRONG_PATH_FOR_V0_V5, got exit={r.returncode}")
            print(f"    stdout: {r.stdout[:300]}")
            print(f"    stderr: {r.stderr[:300]}")
    finally:
        Path(p).unlink(missing_ok=True)


def assert_validator_pass(payload, label):
    global FAIL, PASS
    p = write_payload(payload)
    try:
        r = run([sys.executable, str(VALIDATOR), p])
        if r.returncode == 0:
            PASS += 1
            print(f"  PASS: {label} — validator accepted")
        else:
            FAIL += 1
            print(f"  FAIL: {label} — expected PASS, got exit={r.returncode}")
            print(f"    stdout: {r.stdout[:300]}")
    finally:
        Path(p).unlink(missing_ok=True)


def assert_validator_no_v0_v5_rejection(payload, label):
    """Verify that the V0-V5 fail-closed check does NOT trigger for this payload."""
    global FAIL, PASS
    p = write_payload(payload)
    try:
        r = run([sys.executable, str(VALIDATOR), p])
        combined = r.stdout + r.stderr
        if "WRONG_PATH_FOR_V0_V5" not in combined:
            PASS += 1
            print(f"  PASS: {label} — V0-V5 fail-closed check did NOT trigger")
        else:
            FAIL += 1
            print(f"  FAIL: {label} — V0-V5 fail-closed check incorrectly triggered")
    finally:
        Path(p).unlink(missing_ok=True)


def assert_renderer_fail_wrong_path(payload, label):
    global FAIL, PASS
    p = write_payload(payload)
    try:
        r = run([sys.executable, str(RENDERER), p])
        if r.returncode != 0 and "WRONG_PATH_FOR_V0_V5" in (r.stdout + r.stderr):
            PASS += 1
            print(f"  PASS: {label} — renderer rejected with WRONG_PATH_FOR_V0_V5")
        else:
            FAIL += 1
            print(f"  FAIL: {label} — expected renderer rejection, got exit={r.returncode}")
            print(f"    stdout: {r.stdout[:300]}")
            print(f"    stderr: {r.stderr[:300]}")
    finally:
        Path(p).unlink(missing_ok=True)


def assert_renderer_pass(payload, label):
    global FAIL, PASS
    p = write_payload(payload)
    try:
        r = run([sys.executable, str(RENDERER), p])
        if r.returncode == 0 and "archive_ready: true" in r.stdout:
            PASS += 1
            print(f"  PASS: {label} — renderer accepted with archive_ready: true")
        else:
            FAIL += 1
            print(f"  FAIL: {label} — expected renderer pass, got exit={r.returncode}")
            print(f"    stdout: {r.stdout[:500]}")
    finally:
        Path(p).unlink(missing_ok=True)


def make_v4_intake_only():
    """V4 + record_intent=intake_only + requested_archive_kind=none"""
    return {
        "schema": "trinityaccord.agent-issue-gateway-payload.v1",
        "submission_type": "verification_report_candidate",
        "title": "Verification Report Candidate: V4/B1-D2 - test",
        "body": "Legacy V4 intake only.",
        "agent_identity": {"name_or_model": "test-agent", "system_or_provider": "test", "self_reported": True},
        "boundary_acknowledgement": {
            "not_authority": True, "not_amendment": True, "not_attestation": True,
            "not_verification_unless_claim_gate_report_attached": True, "bitcoin_originals_prevail": True
        },
        "verification_level_claimed": "V4",
        "record_intent": "intake_only",
        "requested_archive_kind": "none",
        "claim_gate": {"status": "PASS", "allowed_protocol_level": "V4"},
        "not_independent_attestation": True,
        "not_successor_reception": True,
        "discovery_provenance": {"agency_level": "A2_human_gave_repo_name", "independence_class": "human_solicited_agent_response", "operator_type": "ai_agent"},
        "what_i_checked": ["test"],
        "limitations": ["test"],
        "reception_initiation_class": "self_initiated",
        "reception_initiation_basis": "agent_discovered_publicly",
        "agent_independent_followup": True,
    }


def make_v4_verification_report_archive():
    """V4 + requested_archive_kind=verification_report_archive"""
    p = make_v4_intake_only()
    p["record_intent"] = "auto_archive_candidate"
    p["requested_archive_kind"] = "verification_report_archive"
    return p


def make_v4_archived_echo():
    """V4 + requested_archive_kind=archived_echo"""
    p = make_v4_intake_only()
    p["record_intent"] = "auto_archive_candidate"
    p["requested_archive_kind"] = "archived_echo"
    return p


def make_v4_external_agent_intake_sample():
    """V4 + requested_archive_kind=external_agent_intake_sample"""
    p = make_v4_intake_only()
    p["record_intent"] = "auto_archive_candidate"
    p["requested_archive_kind"] = "external_agent_intake_sample"
    return p


def make_v4_missing_archive_kind():
    """V4 + missing requested_archive_kind"""
    p = make_v4_intake_only()
    del p["requested_archive_kind"]
    p["record_intent"] = "auto_archive_candidate"
    return p


def make_v4_strict_evidence_paths():
    """V4 + evidence_input_path/claim_gate_output_path/verification_report_path"""
    p = make_v4_intake_only()
    p["record_intent"] = "auto_archive_candidate"
    p["requested_archive_kind"] = "verification_report_archive"
    p["attachments"] = {
        "evidence_input_path": "/tmp/evidence.json",
        "claim_gate_output_path": "/tmp/gate.json",
        "verification_report_path": "/tmp/report.json",
    }
    return p


def make_v4_negation_fields():
    """V4 + not_independent_attestation/not_successor_reception (old fields)"""
    p = make_v4_intake_only()
    p["record_intent"] = "auto_archive_candidate"
    p["requested_archive_kind"] = "verification_report_archive"
    p["not_independent_attestation"] = True
    p["not_successor_reception"] = True
    return p


def make_v4_valid_agent_declared():
    """Valid V4 agent_declared_verification_archive"""
    return {
        "schema": "trinityaccord.agent-issue-gateway-payload.v1",
        "submission_type": "verification_report_candidate",
        "title": "Verification Report Candidate: V4/B1-D2 - test",
        "body": "Valid V4 agent-declared archive submission with all required fields.",
        "agent_identity": {"name_or_model": "test-agent", "system_or_provider": "test", "self_reported": True},
        "boundary_acknowledgement": {
            "not_authority": True, "not_amendment": True, "not_attestation": True,
            "not_verification_unless_claim_gate_report_attached": True, "bitcoin_originals_prevail": True
        },
        "agent_declared_protocol_level": "V4",
        "record_intent": "auto_archive_candidate",
        "requested_archive_kind": "agent_declared_verification_archive",
        "evidence_requirement_mode": "waived_for_v0_v5",
        "claim_gate": {"mode": "template_for_v0_v5", "status": "PASS", "allowed_protocol_level": "V4"},
        "agent_integrity_declaration": {
            "performed_actions_myself": True,
            "verification_oath": {
                "oath_read": True,
                "oath_version": "v1",
                "oath_text_sha256": "a" * 64,
                "readback_required": True,
                "agent_readback": "I understand this is not an exam or performance. I will state only what I actually did, will not fabricate verification, will not present guesses as facts, will not copy prior reports as fresh evidence, and will clearly state uncertainty, limitations, downgrades, and boundaries.",
                "understands_not_an_exam_or_performance": True,
                "will_state_actual_capability_only": True,
                "will_not_lie_or_cheat": True,
                "will_not_fabricate_verification": True,
                "will_not_present_guesses_as_facts": True,
                "will_not_copy_prior_reports_as_fresh_evidence": True,
                "will_state_uncertainty_limitations_and_downgrades": True,
            }
        },
        "authority_boundary": {
            "bitcoin_originals_remain_final": True,
            "does_not_amend_bitcoin_originals": True,
            "does_not_override_bitcoin_originals": True,
        },
        "counts_toward_home": {"verifiability": True, "reception": True, "basis": "agent_declared_template_pass"},
        "origin_classification": {
            "discovery_class": "human_solicited",
            "performer_class": "ai_agent",
            "verification_claimed": True,
            "counts_as_ai_verification": True,
        },
        "claim_classification": {
            "verification_claim": {"claimed": True, "basis": "agent_declared", "system_certified": False},
            "attestation_claim": {"claimed": False, "system_certified": False},
            "successor_reception_claim": {"claimed": False, "system_certified": False},
        },
        "discovery_provenance": {"agency_level": "A2_human_gave_repo_name", "independence_class": "human_solicited_agent_response", "operator_type": "ai_agent"},
        "context_readiness": {},
        "pre_verification_integrity_declaration": {},
        "verification_session": {"session_id": "test", "started_at": "2026-01-01T00:00:00Z", "operator_type": "ai_agent"},
        "what_i_checked": ["test"],
        "limitations": ["test"],
        "reception_initiation_class": "self_initiated",
        "reception_initiation_basis": "agent_discovered_publicly",
        "agent_independent_followup": True,
    }


def make_v6_strict_evidence():
    """V6 strict evidence — should still pass validator"""
    return {
        "schema": "trinityaccord.agent-issue-gateway-payload.v1",
        "submission_type": "verification_report_candidate",
        "title": "Verification Report Candidate: V6/B1-D2 - test",
        "body": "V6 strict evidence path with all required schema fields for validation.",
        "agent_identity": {"name_or_model": "test-agent", "system_or_provider": "test", "self_reported": True},
        "boundary_acknowledgement": {
            "not_authority": True, "not_amendment": True, "not_attestation": True,
            "not_verification_unless_claim_gate_report_attached": True, "bitcoin_originals_prevail": True
        },
        "verification_level_claimed": "V6",
        "record_intent": "auto_archive_candidate",
        "requested_archive_kind": "verification_report_archive",
        "claim_gate": {"status": "PASS", "allowed_protocol_level": "V6"},
        "not_independent_attestation": True,
        "not_successor_reception": True,
        "discovery_provenance": {"agency_level": "A2_human_gave_repo_name", "independence_class": "human_solicited_agent_response", "operator_type": "ai_agent"},
        "context_readiness": {},
        "pre_verification_integrity_declaration": {},
        "verification_session": {"session_id": "test-v6", "started_at": "2026-01-01T00:00:00Z", "operator_type": "ai_agent"},
        "attachments": {
            "evidence_input_path": "/tmp/evidence.json",
            "evidence_input_sha256": "a" * 64,
            "claim_gate_output_path": "/tmp/gate.json",
            "claim_gate_output_sha256": "b" * 64,
            "verification_report_path": "/tmp/report.json",
            "verification_report_sha256": "c" * 64,
        },
        "what_i_checked": ["test"],
        "limitations": ["test"],
        "reception_initiation_class": "self_initiated",
        "reception_initiation_basis": "agent_discovered_publicly",
        "agent_independent_followup": True,
    }


def make_non_verification_issue():
    """Non-verification documentation issue — should be unaffected by V0-V5 policy"""
    return {
        "schema": "trinityaccord.agent-issue-gateway-payload.v1",
        "submission_type": "documentation_issue",
        "title": "Documentation issue: typo in README on line 42",
        "body": "Found a typo in the README file where a word is misspelled. This is a documentation-only fix that does not affect verification levels or archive status.",
        "agent_identity": {"name_or_model": "test-agent", "system_or_provider": "test", "self_reported": True},
        "boundary_acknowledgement": {
            "not_authority": True, "not_amendment": True, "not_attestation": True,
            "not_verification_unless_claim_gate_report_attached": True, "bitcoin_originals_prevail": True
        },
        "not_independent_attestation": True,
        "not_successor_reception": True,
        "discovery_provenance": {"agency_level": "A2_human_gave_repo_name", "independence_class": "human_solicited_agent_response", "operator_type": "ai_agent"},
        "what_i_checked": ["read the docs"],
        "limitations": ["none"],
    }


def main():
    global FAIL, PASS

    print("=== V0-V5 Fail-Closed Submission Policy Tests ===\n")

    # --- Validator: must reject wrong paths ---
    print("--- Validator: reject V0-V5 wrong paths ---")
    assert_validator_fail_wrong_path(make_v4_intake_only(), "V4 + intake_only + archive_kind=none")
    assert_validator_fail_wrong_path(make_v4_verification_report_archive(), "V4 + verification_report_archive")
    assert_validator_fail_wrong_path(make_v4_archived_echo(), "V4 + archived_echo")
    assert_validator_fail_wrong_path(make_v4_external_agent_intake_sample(), "V4 + external_agent_intake_sample")
    assert_validator_fail_wrong_path(make_v4_missing_archive_kind(), "V4 + missing archive_kind")
    assert_validator_fail_wrong_path(make_v4_strict_evidence_paths(), "V4 + strict evidence paths")
    assert_validator_fail_wrong_path(make_v4_negation_fields(), "V4 + old negation fields")

    # Load and test fixture
    fixture = ROOT / "fixtures" / "gateway" / "issue-163-old-v4-intake-only.json"
    if fixture.exists():
        issue163 = json.loads(fixture.read_text())
        assert_validator_fail_wrong_path(issue163, "Issue #163 fixture")

    # --- Validator: must accept valid paths ---
    print("\n--- Validator: accept valid V0-V5 agent-declared ---")
    assert_validator_pass(make_v4_valid_agent_declared(), "V4 valid agent_declared_verification_archive")

    print("\n--- Validator: V6+ strict evidence unaffected ---")
    assert_validator_pass(make_v6_strict_evidence(), "V6 strict evidence")

    print("\n--- Validator: non-verification intake unaffected ---")
    assert_validator_no_v0_v5_rejection(make_non_verification_issue(), "Non-verification documentation issue")

    # --- Renderer: must refuse wrong paths ---
    print("\n--- Renderer: refuse V0-V5 wrong paths ---")
    assert_renderer_fail_wrong_path(make_v4_intake_only(), "V4 + intake_only (renderer)")
    assert_renderer_fail_wrong_path(make_v4_verification_report_archive(), "V4 + verification_report_archive (renderer)")

    if fixture.exists():
        assert_renderer_fail_wrong_path(issue163, "Issue #163 fixture (renderer)")

    # --- Renderer: must accept valid paths ---
    print("\n--- Renderer: accept valid V0-V5 agent-declared ---")
    assert_renderer_pass(make_v4_valid_agent_declared(), "V4 valid agent-declared (renderer)")

    # --- Summary ---
    print(f"\n=== Results: {PASS} passed, {FAIL} failed ===")
    if FAIL > 0:
        sys.exit(1)
    print("All tests passed.")


if __name__ == "__main__":
    main()
