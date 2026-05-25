#!/usr/bin/env python3
"""claim_gate.allowed_component_levels must reject unknown keys/values."""
import copy
import hashlib
import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
schema = json.loads((ROOT / "api" / "agent-issue-gateway-payload-schema.v1.json").read_text(encoding="utf-8"))

READBACK = (
    "I confirm this is a non-authoritative archive candidate and I state only what I actually checked. "
    "I understand this is not authority, attestation, formal verification, successor reception, or amendment."
)

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def verification_payload() -> dict:
    return {
        "schema": "trinityaccord.agent-issue-gateway-payload.v1",
        "submission_type": "verification_report_candidate",
        "record_intent": "auto_archive_candidate",
        "title": "Fixture verification candidate",
        "body": "This is a fixture body with enough length for schema validation.",
        "agent_identity": {
            "name_or_model": "fixture-agent",
            "system_or_provider": "fixture-runtime",
            "self_reported": True
        },
        "boundary_acknowledgement": {
            "not_authority": True,
            "not_amendment": True,
            "not_attestation": True,
            "not_verification_unless_claim_gate_report_attached": True,
            "bitcoin_originals_prevail": True
        },
        "agent_integrity_declaration": {
            "performed_actions_myself": True,
            "verification_oath": {
                "oath_read": True,
                "oath_version": "trinity-agent-integrity-oath.v1",
                "oath_text_sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
                "readback_required": True,
                "agent_readback": "I confirm this is a non-authoritative archive candidate.",
                "agent_readback_sha256": "a]b",
                "understands_not_an_exam_or_performance": True,
                "will_state_actual_capability_only": True,
                "will_not_lie_or_cheat": True,
                "will_not_fabricate_verification": True,
                "will_not_present_guesses_as_facts": True,
                "will_not_copy_prior_reports_as_fresh_evidence": True,
                "will_state_uncertainty_limitations_and_downgrades": True
            }
        },
        "discovery_provenance": {"source": "fixture"},
        "authority_boundary": {
            "bitcoin_originals_remain_final": True,
            "does_not_amend_bitcoin_originals": True,
            "does_not_override_bitcoin_originals": True
        },
        "what_i_checked": ["fixture"],
        "limitations": ["fixture"],
        "reception_initiation_class": "externally_requested",
        "requested_archive_kind": "agent_declared_verification_archive",
        "echo_type": "E5_technical_audit_echo",
        "agent_declared_protocol_level": "V4",
        "evidence_requirement_mode": "waived_for_v0_v5",
        "level_selection_acknowledgement": {
            "declared_template_level": "V4",
            "understands_self_declared_template_level": True,
            "understands_evidence_waived_for_v0_v5": True,
            "understands_not_strict_evidence_verification": True,
            "understands_not_formal_attestation": True,
            "understands_should_choose_lower_if_uncertain": True,
            "confirmed_what_i_checked_and_limitations_are_accurate": True,
        },
        "claim_gate": {
            "status": "PASS",
            "mode": "template_for_v0_v5",
            "allowed_protocol_level": "V4",
            "allowed_component_levels": {
                "context_depth": "D3",
                "evidence_depth": "E2",
                "tool_reproduction": "T1",
                "independence": "I2",
            },
        },
        "counts_toward_home": {
            "reception": False,
            "verifiability": True,
            "basis": "agent_declared_template_pass",
        },
    }

def expect_pass(payload, label):
    try:
        jsonschema.validate(payload, schema)
    except jsonschema.ValidationError as e:
        print(f"FAIL: expected pass for {label}: {e.message}")
        sys.exit(1)

def expect_fail(payload, label):
    try:
        jsonschema.validate(payload, schema)
    except jsonschema.ValidationError:
        return
    print(f"FAIL: expected schema rejection for {label}")
    sys.exit(1)

# Test: valid component levels pass
good = verification_payload()
good["claim_gate"]["allowed_component_levels"] = {
    "context_depth": "D3",
    "evidence_depth": "E2",
    "tool_reproduction": "T1",
    "independence": "I2",
}
expect_pass(good, "valid allowed_component_levels")

# Test: unknown key must fail
unknown = copy.deepcopy(good)
unknown["claim_gate"]["allowed_component_levels"]["mystery_key"] = "X1"
expect_fail(unknown, "allowed_component_levels with unknown key")

# Test: invalid enum value must fail
bad_val = copy.deepcopy(good)
bad_val["claim_gate"]["allowed_component_levels"]["context_depth"] = "D99"
expect_fail(bad_val, "allowed_component_levels with invalid enum value")

print("PASS: claim_gate.allowed_component_levels constraints enforced")
