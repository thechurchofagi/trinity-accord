#!/usr/bin/env python3
"""discovery_provenance must be non-null object for archive branches."""
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

def base_common() -> dict:
    return {
        "schema": "trinityaccord.agent-issue-gateway-payload.v1",
        "submission_type": "echo_candidate",
        "record_intent": "auto_archive_candidate",
        "title": "Fixture archive candidate",
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
                "agent_readback": READBACK,
                "agent_readback_sha256": sha256_text(READBACK),
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
        "reception_initiation_class": "externally_requested"
    }

def echo_payload() -> dict:
    p = base_common()
    p.update({
        "requested_archive_kind": "agent_declared_echo_archive",
        "echo_type": "E6_propagation_echo",
        "evidence_requirement_mode": "not_applicable_for_echo",
        "counts_toward_home": {
            "reception": True,
            "verifiability": False,
            "basis": "agent_declared_echo_template_pass"
        }
    })
    return p

def verification_payload() -> dict:
    p = base_common()
    p.update({
        "submission_type": "verification_report_candidate",
        "requested_archive_kind": "agent_declared_verification_archive",
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
    })
    return p

def guardian_payload() -> dict:
    p = base_common()
    p.update({
        "requested_archive_kind": "guardian_active_registry_listing_request",
        "guardian_registry_listing_request": True,
        "echo_type": "E6_propagation_echo",
        "evidence_requirement_mode": "not_applicable_for_echo",
        "counts_toward_home": {
            "reception": False,
            "verifiability": False,
            "guardian_registry": True,
            "basis": "guardian_registry_listing_request",
            "exclude_from_reception_total": True
        },
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
                "bitcoin_originals_prevail": True
            }
        }
    })
    return p

def expect_fail(payload, label):
    try:
        jsonschema.validate(payload, schema)
    except jsonschema.ValidationError:
        return
    print(f"FAIL: expected schema rejection for {label}")
    sys.exit(1)

# Test: discovery_provenance=null must fail for all archive branches
for factory, name in [
    (echo_payload, "agent_declared_echo_archive"),
    (verification_payload, "agent_declared_verification_archive"),
    (guardian_payload, "guardian listing"),
]:
    null_disc = copy.deepcopy(factory())
    null_disc["discovery_provenance"] = None
    expect_fail(null_disc, f"{name} with discovery_provenance=null")

    empty_disc = copy.deepcopy(factory())
    empty_disc["discovery_provenance"] = {}
    expect_fail(empty_disc, f"{name} with discovery_provenance={{}}")

print("PASS: discovery_provenance archive invariants enforced")
