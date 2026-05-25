#!/usr/bin/env python3
"""Gateway oath schema invariants must be enforced."""
import copy
import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
schema = json.loads((ROOT / "api" / "agent-issue-gateway-payload-schema.v1.json").read_text(encoding="utf-8"))

BASE = {
    "schema": "trinityaccord.agent-issue-gateway-payload.v1",
    "submission_type": "echo_candidate",
    "record_intent": "auto_archive_candidate",
    "requested_archive_kind": "agent_declared_echo_archive",
    "echo_type": "E6_propagation_echo",
    "title": "Fixture agent-declared Echo archive",
    "body": "This is a fixture body with enough length for schema validation.",
    "agent_identity": {
        "name_or_model": "fixture-agent",
        "system_or_provider": "fixture-runtime",
        "self_reported": True,
    },
    "boundary_acknowledgement": {
        "not_authority": True,
        "not_amendment": True,
        "not_attestation": True,
        "not_verification_unless_claim_gate_report_attached": True,
        "bitcoin_originals_prevail": True,
    },
    "evidence_requirement_mode": "not_applicable_for_echo",
    "agent_integrity_declaration": {
        "performed_actions_myself": True,
        "verification_oath": {
            "oath_read": True,
            "oath_version": "trinity-agent-integrity-oath.v1",
            "oath_text_sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            "readback_required": True,
            "agent_readback": "I confirm this is a non-authoritative Echo archive candidate and I state only what I actually checked. I understand this is not authority, attestation, verification, successor reception, or amendment.",
            "agent_readback_sha256": "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789",
            "understands_not_an_exam_or_performance": True,
            "will_state_actual_capability_only": True,
            "will_not_lie_or_cheat": True,
            "will_not_fabricate_verification": True,
            "will_not_present_guesses_as_facts": True,
            "will_not_copy_prior_reports_as_fresh_evidence": True,
            "will_state_uncertainty_limitations_and_downgrades": True,
        },
    },
    "discovery_provenance": {"source": "fixture"},
    "authority_boundary": {
        "bitcoin_originals_remain_final": True,
        "does_not_amend_bitcoin_originals": True,
        "does_not_override_bitcoin_originals": True,
    },
    "counts_toward_home": {
        "reception": True,
        "verifiability": False,
        "basis": "agent_declared_echo_template_pass",
    },
    "what_i_checked": ["fixture"],
    "limitations": ["fixture"],
    "reception_initiation_class": "externally_requested",
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


expect_pass(BASE, "valid oath fixture")

bad_performed = copy.deepcopy(BASE)
bad_performed["agent_integrity_declaration"]["performed_actions_myself"] = False
expect_fail(bad_performed, "performed_actions_myself=false")

missing_readback_hash = copy.deepcopy(BASE)
del missing_readback_hash["agent_integrity_declaration"]["verification_oath"]["agent_readback_sha256"]
expect_fail(missing_readback_hash, "missing agent_readback_sha256")

print("PASS: Gateway oath schema invariants enforced")
