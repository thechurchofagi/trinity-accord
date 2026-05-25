#!/usr/bin/env python3
"""Gateway agent-declared verification archives must have a valid Claim Gate object."""
import copy
import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_gateway_payload_semantics import validate

schema = json.loads((ROOT / "api" / "agent-issue-gateway-payload-schema.v1.json").read_text(encoding="utf-8"))

BASE = {
    "schema": "trinityaccord.agent-issue-gateway-payload.v1",
    "submission_type": "verification_report_candidate",
    "record_intent": "auto_archive_candidate",
    "requested_archive_kind": "agent_declared_verification_archive",
    "title": "Fixture agent-declared verification archive",
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
    "agent_declared_protocol_level": "V4",
    "level_selection_acknowledgement": {
        "declared_template_level": "V4",
        "understands_self_declared_template_level": True,
        "understands_evidence_waived_for_v0_v5": True,
        "understands_not_strict_evidence_verification": True,
        "understands_not_formal_attestation": True,
        "understands_should_choose_lower_if_uncertain": True,
        "confirmed_what_i_checked_and_limitations_are_accurate": True
    },
    "evidence_requirement_mode": "waived_for_v0_v5",
    "claim_gate": {
        "status": "PASS",
        "mode": "template_for_v0_v5",
        "allowed_protocol_level": "V4"
    },
    "agent_integrity_declaration": {
        "performed_actions_myself": True,
        "verification_oath": {
            "oath_read": True,
            "oath_version": "trinity-agent-integrity-oath.v1",
            "oath_text_sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            "readback_required": True,
            "agent_readback": "I confirm this is an agent-declared verification archive candidate and I state only what I actually checked. I understand this is not authority, attestation, successor reception, or amendment.",
            "agent_readback_sha256": "9023f9112ebfc588efcd3e7cf9ba796447da371f172c3e75b2b6f8217d108f7a",
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
    "origin_classification": {},
    "claim_classification": {},
    "authority_boundary": {
        "bitcoin_originals_remain_final": True,
        "does_not_amend_bitcoin_originals": True,
        "does_not_override_bitcoin_originals": True
    },
    "counts_toward_home": {
        "reception": False,
        "verifiability": True,
        "basis": "agent_declared_template_pass"
    },
    "what_i_checked": ["fixture"],
    "limitations": ["fixture"],
    "reception_initiation_class": "externally_requested"
}


def schema_expect_pass(payload, label):
    try:
        jsonschema.validate(payload, schema)
    except jsonschema.ValidationError as e:
        print(f"FAIL: expected schema pass for {label}: {e.message}")
        sys.exit(1)


def schema_expect_fail(payload, label):
    try:
        jsonschema.validate(payload, schema)
    except jsonschema.ValidationError:
        return
    print(f"FAIL: expected schema rejection for {label}")
    sys.exit(1)


def semantic_expect_fail(payload, label, fragment):
    errors = validate(payload)
    if not any(fragment in e for e in errors):
        print(f"FAIL: expected semantic error for {label}: {fragment}")
        print(errors)
        sys.exit(1)


schema_expect_pass(BASE, "valid Claim Gate fixture")
if validate(BASE):
    print("FAIL: valid Claim Gate fixture had semantic errors:", validate(BASE))
    sys.exit(1)

null_claim = copy.deepcopy(BASE)
null_claim["claim_gate"] = None
schema_expect_fail(null_claim, "claim_gate=null")

fail_status = copy.deepcopy(BASE)
fail_status["claim_gate"]["status"] = "FAIL"
schema_expect_fail(fail_status, "claim_gate.status=FAIL")

bad_mode = copy.deepcopy(BASE)
bad_mode["claim_gate"]["mode"] = "strict_evidence"
schema_expect_fail(bad_mode, "claim_gate.mode=strict_evidence")

bad_level = copy.deepcopy(BASE)
bad_level["claim_gate"]["allowed_protocol_level"] = "V1"
semantic_expect_fail(bad_level, "claim_gate.allowed_protocol_level mismatch", "claim_gate.allowed_protocol_level must equal")

print("PASS: Claim Gate schema and semantic invariants enforced")
