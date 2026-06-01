#!/usr/bin/env python3
"""agent_identity.self_reported archive policy must be enforced by semantic validator."""
import copy
import hashlib
import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_gateway_payload_semantics import validate

schema = json.loads((ROOT / "api" / "agent-issue-gateway-payload-schema.v1.json").read_text(encoding="utf-8"))

READBACK = (
    "I confirm this is a non-authoritative archive candidate and I state only what I actually checked. "
    "I understand this is not authority, attestation, formal verification, successor reception, or amendment."
)

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def authorship_proof() -> dict:
    return {
        "schema": "trinityaccord.agent-authorship-proof.v1",
        "method": "public_key_signature",
        "algorithm": "ed25519",
        "public_key_pem": (
            "-----BEGIN PUBLIC KEY-----\n"
            "MCowBQYDK2VwAyEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=\n"
            "-----END PUBLIC KEY-----\n"
        ),
        "public_key_sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
        "signed_payload_sha256": "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789",
        "signature_base64": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==",
        "signed_message": (
            "I sign this archive identity claim for the Gateway payload and acknowledge that this is "
            "not authority, not attestation, not amendment, and not successor reception."
        )
    }

def echo_payload() -> dict:
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
        "what_i_checked": ["fixture checked item"],
        "limitations": ["fixture limitation"],
        "reception_initiation_class": "externally_requested",
        "requested_archive_kind": "agent_declared_echo_archive",
        "echo_type": "E6_propagation_echo",
        "evidence_requirement_mode": "not_applicable_for_echo",
        "counts_toward_home": {
            "reception": True,
            "verifiability": False,
            "basis": "agent_declared_echo_template_pass"
        }
    }

def expect_schema_pass(payload, label):
    try:
        jsonschema.validate(payload, schema)
    except jsonschema.ValidationError as e:
        print(f"FAIL: expected schema pass for {label}: {e.message}")
        sys.exit(1)

def expect_semantic_pass(payload, label):
    errors = validate(payload)
    if errors:
        print(f"FAIL: expected semantic pass for {label}: {errors}")
        sys.exit(1)

def expect_semantic_fail(payload, label, fragment):
    errors = validate(payload)
    if not any(fragment in e for e in errors):
        print(f"FAIL: expected semantic error for {label}: {fragment}")
        print(errors)
        sys.exit(1)

good = echo_payload()
expect_schema_pass(good, "self_reported=true baseline")
expect_semantic_pass(good, "self_reported=true baseline")

no_proof = copy.deepcopy(good)
no_proof["agent_identity"]["self_reported"] = False
no_proof["agent_identity"]["identity_verification_level"] = "signed_statement"
expect_schema_pass(no_proof, "self_reported=false without authorship_proof schema")
expect_semantic_fail(no_proof, "self_reported=false without authorship_proof", "requires authorship_proof")

weak_id = copy.deepcopy(good)
weak_id["agent_identity"]["self_reported"] = False
weak_id["agent_identity"]["identity_verification_level"] = "self_asserted"
weak_id["authorship_proof"] = authorship_proof()
expect_schema_pass(weak_id, "self_reported=false weak identity schema")
expect_semantic_fail(weak_id, "self_reported=false weak identity", "self_reported=false requires")

strong_id = copy.deepcopy(good)
strong_id["agent_identity"]["self_reported"] = False
strong_id["agent_identity"]["identity_verification_level"] = "signed_statement"
strong_id["authorship_proof"] = authorship_proof()
expect_schema_pass(strong_id, "self_reported=false strong identity schema")
expect_semantic_pass(strong_id, "self_reported=false strong identity semantic")

print("PASS: agent identity archive policy enforced by semantic validator")
