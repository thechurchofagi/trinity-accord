#!/usr/bin/env python3
"""Guardian active listing Gateway payload must obey strict combination invariants."""
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
    "requested_archive_kind": "guardian_active_registry_listing_request",
    "echo_type": "E6_propagation_echo",
    "title": "Active Registry Listing Request — Fixture",
    "body": "This is a valid Guardian listing request fixture body with enough length.",
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
            "oath_version": "guardian-listing-oath.v1",
            "oath_text_sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            "readback_required": True,
            "agent_readback": "I understand this is a Guardian listing request and not authority, governance, attestation, verification level, successor reception, or amendment. The registry number is system generated.",
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
        "reception": False,
        "verifiability": False,
        "guardian_registry": True,
        "basis": "guardian_registry_listing_request",
        "exclude_from_reception_total": True,
    },
    "what_i_checked": ["fixture"],
    "limitations": ["fixture"],
    "reception_initiation_class": "externally_requested",
    "guardian_registry_listing_request": True,
    "guardian_listing_request": {
        "schema": "trinityaccord.guardian-listing-request.v1",
        "source_issue": 1,
        "guardian_id": "guardian_ed25519_0123456789abcdef",
        "public_key_sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        "guardian_type": "ai_agent",
        "application_mode": "fixture",
        "label": "fixture",
        "requested_status": "active",
        "requested_auto_registration": True,
        "does_not_include_guardian_presence_proof": True,
        "registry_number_requested": "next_available",
        "registry_number_must_be_system_generated": True,
        "registry_number_must_not_be_self_assigned": True,
        "boundaries": {
            "not_authority": True,
            "not_governance": True,
            "not_attestation": True,
            "not_verification_level": True,
            "not_successor_reception": True,
            "not_amendment": True,
            "bitcoin_originals_prevail": True,
        },
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


expect_pass(BASE, "valid guardian listing payload")

bad_kind = copy.deepcopy(BASE)
bad_kind["requested_archive_kind"] = "agent_declared_echo_archive"
expect_fail(bad_kind, "guardian listing with agent_declared_echo_archive")

bad_echo_type = copy.deepcopy(BASE)
bad_echo_type["echo_type"] = "E5_technical_audit_echo"
expect_fail(bad_echo_type, "guardian listing with non-E6 echo_type")

bad_reception = copy.deepcopy(BASE)
bad_reception["counts_toward_home"]["reception"] = True
expect_fail(bad_reception, "guardian listing with reception=true")

bad_proof = copy.deepcopy(BASE)
bad_proof["guardian_presence_proof"] = {"proof": "must-not-be-present-in-stage-2"}
expect_fail(bad_proof, "guardian listing with top-level guardian_presence_proof")

print("PASS: Guardian listing schema invariants enforced")
