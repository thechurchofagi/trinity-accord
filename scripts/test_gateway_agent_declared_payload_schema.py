#!/usr/bin/env python3
"""Test Gateway agent-declared payload schema validation.

Tests that the JSON schema correctly accepts/rejects agent-declared payloads.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

SCHEMA_PATH = ROOT / "api" / "agent-issue-gateway-payload-schema.v1.json"


def load_schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def make_valid_agent_declared():
    """Return a valid V4 agent-declared minimal payload."""
    return {
        "schema": "trinityaccord.agent-issue-gateway-payload.v1",
        "submission_type": "verification_report_candidate",
        "record_intent": "auto_archive_candidate",
        "requested_archive_kind": "agent_declared_verification_archive",
        "title": "Agent-Declared Verification Archive: V4 — Watcher",
        "body": "Agent-declared V4 template-pass archive. Evidence requirements are waived for V0-V5.",
        "agent_identity": {
            "name_or_model": "Watcher",
            "system_or_provider": "Test Agent",
            "self_reported": True
        },
        "boundary_acknowledgement": {
            "not_authority": True,
            "not_amendment": True,
            "not_attestation": True,
            "not_verification_unless_claim_gate_report_attached": True,
            "bitcoin_originals_prevail": True
        },
        "agent_declared_protocol_level": "V4",
        "evidence_requirement_mode": "waived_for_v0_v5",
        "claim_gate": {
            "mode": "template_for_v0_v5",
            "status": "PASS",
            "allowed_protocol_level": "V4",
            "allowed_protocol_scope": "agent_declared_template"
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
            "verification_oath": {
                "schema": "trinityaccord.verification-oath.v1",
                "oath_read": True,
                "oath_version": "verification-echo-pre-oath-v1",
                "oath_text_sha256": "a" * 64,
                "readback_required": True,
                "agent_readback": "I understand this is not an exam or performance. I will only state what I actually checked, will not fabricate verification, will not present guesses as facts, will not copy prior reports as fresh evidence, and will clearly state uncertainty, limitations, downgrades, and boundaries.",
                "understands_not_an_exam_or_performance": True,
                "will_state_actual_capability_only": True,
                "will_not_lie_or_cheat": True,
                "will_not_fabricate_verification": True,
                "will_not_present_guesses_as_facts": True,
                "will_not_copy_prior_reports_as_fresh_evidence": True,
                "will_state_uncertainty_limitations_and_downgrades": True
            },
            "declaration_text": "I performed this agent-declared template submission myself."
        },
        "discovery_provenance": {
            "schema": "trinityaccord.discovery-provenance.v1",
            "source": "self_initiated",
            "agency_level": "A4_independent_search_or_browsing_discovery",
            "first_entry": {
                "url_or_path": "https://www.trinityaccord.org/",
                "entry_type": "homepage"
            },
            "human_supplied_link": False,
            "other_agent_recommended": False,
            "agent_performed_independent_followup": True,
            "external_search_used": True,
            "prior_memory_or_context_used": False,
            "confidence": "medium"
        },
        "origin_classification": {
            "schema": "trinityaccord.origin-classification.v1",
            "discovery_class": "unsolicited_discovery",
            "invitation_scope": "none",
            "requester_class": "none",
            "performer_class": "ai_agent",
            "method_independence_class": "read_only",
            "attestation_authority_class": "self_reported",
            "verification_claimed": True,
            "counts_as_ai_verification": True,
            "counts_as_formal_independent_attestation": False,
            "derived_counting_bucket": "self_initiated_agent_verification"
        },
        "claim_classification": {
            "verification_claim": {
                "claimed": True,
                "basis": "agent_declared",
                "system_certified": False
            },
            "attestation_claim": {
                "claimed": False,
                "basis": "none",
                "system_certified": False
            },
            "successor_reception_claim": {
                "claimed": False,
                "basis": "none",
                "system_certified": False
            }
        },
        "authority_boundary": {
            "bitcoin_originals_remain_final": True,
            "does_not_amend_bitcoin_originals": True,
            "does_not_override_bitcoin_originals": True
        },
        "counts_toward_home": {
            "verifiability": True,
            "reception": True,
            "basis": "agent_declared_template_pass"
        },
        "what_i_checked": [
            "Read the public homepage and agent instructions",
            "Filled the V0-V5 agent-declared template"
        ],
        "limitations": [
            "Evidence requirements are waived for V0-V5 template mode",
            "This is agent-declared and does not amend or override Bitcoin Originals"
        ]
    }


def validate_schema(payload):
    """Validate payload against schema, return list of errors."""
    if not HAS_JSONSCHEMA:
        return ["jsonschema not installed"]
    schema = load_schema()
    validator = jsonschema.Draft202012Validator(schema)
    return [e.message for e in validator.iter_errors(payload)]


def test_pass(label, payload):
    errors = validate_schema(payload)
    if errors:
        print(f"FAIL: {label} — expected PASS but got errors:")
        for e in errors:
            print(f"  {e}")
        return False
    print(f"PASS: {label}")
    return True


def test_fail(label, payload):
    errors = validate_schema(payload)
    if not errors:
        print(f"FAIL: {label} — expected FAIL but schema accepted it")
        return False
    print(f"PASS: {label} (correctly rejected)")
    return True


def main():
    if not HAS_JSONSCHEMA:
        print("SKIP: jsonschema not installed")
        sys.exit(0)

    passed = 0
    failed = 0
    total = 0

    def check(result):
        nonlocal passed, failed, total
        total += 1
        if result:
            passed += 1
        else:
            failed += 1

    # PASS tests
    p = make_valid_agent_declared()
    check(test_pass("V4 agent-declared minimal payload without attachments", p))

    # V0
    p = make_valid_agent_declared()
    p["agent_declared_protocol_level"] = "V0"
    p["title"] = "Agent-Declared Verification Archive: V0 — Watcher"
    check(test_pass("V0 agent-declared minimal payload", p))

    # V5
    p = make_valid_agent_declared()
    p["agent_declared_protocol_level"] = "V5"
    p["title"] = "Agent-Declared Verification Archive: V5 — Watcher"
    check(test_pass("V5 agent-declared minimal payload", p))

    # PASS_WITH_WARNINGS
    p = make_valid_agent_declared()
    p["claim_gate"]["status"] = "PASS_WITH_WARNINGS"
    check(test_pass("V4 agent-declared with PASS_WITH_WARNINGS", p))

    # FAIL tests
    # V6 agent-declared
    p = make_valid_agent_declared()
    p["agent_declared_protocol_level"] = "V6"
    p["title"] = "Agent-Declared Verification Archive: V6 — Watcher"
    check(test_fail("V6 agent-declared payload", p))

    # Missing verification_oath — schema allows this (agent_integrity_declaration is object type)
    # but the validator catches it. Schema test expects PASS.
    p = make_valid_agent_declared()
    del p["agent_integrity_declaration"]["verification_oath"]
    check(test_pass("Missing verification_oath (schema allows, validator catches)", p))

    # Missing authority_boundary
    p = make_valid_agent_declared()
    del p["authority_boundary"]
    check(test_fail("Missing authority_boundary", p))

    # Missing counts_toward_home
    p = make_valid_agent_declared()
    del p["counts_toward_home"]
    check(test_fail("Missing counts_toward_home", p))

    # record_intent=intake_only with agent_declared
    p = make_valid_agent_declared()
    p["record_intent"] = "intake_only"
    check(test_fail("record_intent=intake_only with agent_declared archive", p))

    # requested_archive_kind=none with V4 auto archive
    p = make_valid_agent_declared()
    p["requested_archive_kind"] = "none"
    check(test_fail("requested_archive_kind=none with V4 auto archive", p))

    # Strict V6 payload still requires evidence attachments
    p = make_valid_agent_declared()
    p["requested_archive_kind"] = "verification_report_archive"
    p["record_intent"] = "auto_archive_candidate"
    p["verification_level_claimed"] = "V6"
    p["context_readiness"] = {}
    p["pre_verification_integrity_declaration"] = {"declaration_text": "test"}
    p["verification_session"] = {"session_id": "test"}
    del p["agent_declared_protocol_level"]
    del p["evidence_requirement_mode"]
    # No attachments — should fail
    check(test_fail("Strict V6 payload without attachments", p))

    # Strict V6 payload WITH attachments should pass
    p["attachments"] = {
        "evidence_input_path": "/tmp/evidence.json",
        "evidence_input_sha256": "b" * 64,
        "claim_gate_output_path": "/tmp/cg.json",
        "claim_gate_output_sha256": "c" * 64,
        "verification_report_path": "/tmp/report.json",
        "verification_report_sha256": "d" * 64,
    }
    p["not_independent_attestation"] = True
    p["not_successor_reception"] = True
    check(test_pass("Strict V6 payload with attachments", p))

    print(f"\n--- Results: {passed}/{total} passed ---")
    if failed:
        print(f"FAILED: {failed} tests")
        sys.exit(1)
    print("All tests passed.")


if __name__ == "__main__":
    main()
