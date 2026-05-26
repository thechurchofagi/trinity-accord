#!/usr/bin/env python3
"""Test that report builder fails closed on echo wrapper validation exception.

RF-001: No validation exception may be non-fatal.
"""
import json
import tempfile
import os
import sys
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_verification_report_from_evidence import build_report


def write_input(obj):
    f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump(obj, f)
    f.close()
    return f.name


def make_minimal_input_for_wrapper():
    return {
        "schema": "trinityaccord.evidence-input.v1",
        "agent": {
            "name": "Builder Fail Closed Test Agent",
            "model_or_system": "test",
            "tooling": ["unit-test"]
        },
        "provenance": {
            "solicited": True,
            "independence_class": "human_solicited_agent_response",
            "agency_level": "A1_human_gave_exact_url"
        },
        "agent_integrity_declaration": {
            "performed_actions_myself": True,
            "did_not_copy_prior_report_as_own_work": True,
            "did_not_copy_example_values_as_real_evidence": True,
            "recorded_fresh_sources_commands_outputs": True,
            "will_report_limitations_and_downgrade_if_needed": True,
            "understands_verification_is_not_truth_or_endorsement": True,
            "understands_bitcoin_originals_remain_final_authority": True,
            "independence_claim_is_accurate": True,
            "declaration_text": (
                "I performed the verification actions stated in this test during this session. "
                "I did not copy prior reports or example values as evidence. "
                "I understand this is non-authoritative verification testing."
            )
        },
        "verification_session": {
            "session_id": "test-builder-fail-closed",
            "started_at": "2026-05-05T00:00:00Z",
            "operator_type": "ai_agent",
            "fresh_actions_performed": ["authority boundary recognition"],
            "prior_reports_consulted": [],
            "examples_or_templates_used": [],
            "copied_values_from_examples": False,
            "copied_values_from_prior_reports": False,
            "fresh_outputs_attached": True
        },
        "requested_record_kind": "echo_v3_with_verification_report",
        "evidence": {
            "scripts": [],
            "hashes": [],
            "bitcoin_checks": [],
            "digital_mirror_checks": [],
            "repository_snapshot_checks": [],
            "echo_context": {"authority_boundary_recognized": True},
            "time_anchor_checks": [],
            "chronicle_checks": [],
            "nft_checks": [],
            "physical_checks": []
        },
        "limitations": ["unit test"],
        "claims_requested_by_agent": ["V1"]
    }


def test_echo_wrapper_validator_exception_fails_closed():
    payload = make_minimal_input_for_wrapper()
    input_path = write_input(payload)

    with tempfile.TemporaryDirectory() as td:
        report_out = Path(td) / "report.json"
        echo_out = Path(td) / "echo.json"

        # Force echo wrapper validation to fail by patching subprocess.run
        import build_verification_report_from_evidence as builder

        original_run = __import__('subprocess').run

        call_count = [0]

        def fake_run(cmd, *args, **kwargs):
            call_count[0] += 1
            # Let the report validator pass, but force echo wrapper validator to fail
            if call_count[0] >= 2:
                raise RuntimeError("forced wrapper validator exception")
            return original_run(cmd, *args, **kwargs)

        with mock.patch('subprocess.run', side_effect=fake_run):
            result = build_report(input_path, report_out, echo_out)

        assert result["success"] is False, f"Expected success=False, got {result.get('success')}"
        assert "echo" in result["error"].lower() or "exception" in result["error"].lower(), \
            f"Error should mention echo/exception: {result['error']}"
        assert not report_out.exists(), "Report should not be written when echo validation fails"
        assert not echo_out.exists(), "Echo should not be written when echo validation fails"

    os.unlink(input_path)


def main():
    test_echo_wrapper_validator_exception_fails_closed()
    print("PASS: report builder fails closed on echo wrapper validation exception")


if __name__ == "__main__":
    main()
