#!/usr/bin/env python3
"""Test: Record-Chain Intake Gateway contract compliance."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    errors = []

    # Test 1: Gateway contract exists
    gw_path = ROOT / "api" / "record-chain-intake-gateway.v1.json"
    if not gw_path.exists():
        errors.append("api/record-chain-intake-gateway.v1.json: NOT FOUND")
    else:
        gw = json.loads(gw_path.read_text())
        if gw.get("schema") != "trinityaccord.record-chain-intake-gateway.v1":
            errors.append(f"wrong schema: {gw.get('schema')}")
        if gw.get("status") != "active_public_submission_interface":
            errors.append(f"wrong status: {gw.get('status')}")
        endpoints = gw.get("endpoints", {})
        for ep in ["health", "readiness", "preflight", "submit", "receipt"]:
            if ep not in endpoints:
                errors.append(f"missing endpoint: {ep}")
        rules = gw.get("public_submission_rule", {})
        if not rules.get("render_is_only_public_submission_method"):
            errors.append("render_is_only_public_submission_method not true")
        if not rules.get("external_agents_must_not_clone_repository"):
            errors.append("external_agents_must_not_clone_repository not true")

    # Test 2: Submission schema exists
    sub_path = ROOT / "api" / "record-chain-submission-schema.v1.json"
    if not sub_path.exists():
        errors.append("api/record-chain-submission-schema.v1.json: NOT FOUND")
    else:
        sub = json.loads(sub_path.read_text())
        if "trinityaccord" not in sub.get("$id", ""):
            errors.append(f"submission schema $id wrong: {sub.get('$id')}")

    # Test 3: Preflight response schema exists
    pr_path = ROOT / "api" / "record-chain-preflight-response.v1.json"
    if not pr_path.exists():
        errors.append("api/record-chain-preflight-response.v1.json: NOT FOUND")

    # Test 4: Submit response schema exists
    sr_path = ROOT / "api" / "record-chain-submit-response.v1.json"
    if not sr_path.exists():
        errors.append("api/record-chain-submit-response.v1.json: NOT FOUND")

    # Test 5: Builder bundles exist and match
    bb_path = ROOT / "api" / "record-chain-builder-bundles.v1.json"
    if not bb_path.exists():
        errors.append("api/record-chain-builder-bundles.v1.json: NOT FOUND")
    else:
        bb = json.loads(bb_path.read_text())
        if not bb.get("public_submission_rule", {}).get("render_is_only_public_submission_method"):
            errors.append("builder bundles: render_is_only not true")

    # Test 6: record-chain-status.json has public_submission
    status_path = ROOT / "api" / "record-chain-status.json"
    if status_path.exists():
        status = json.loads(status_path.read_text())
        if "public_submission" not in status:
            errors.append("record-chain-status.json: missing public_submission field")

    # Test 7: receipt_id pattern is correct
    if gw_path.exists():
        gw = json.loads(gw_path.read_text())
        receipt_ep = gw.get("endpoints", {}).get("receipt", {})
        receipt_params = receipt_ep.get("path_parameters", {}).get("receipt_id", {})
        pattern = receipt_params.get("pattern", "")
        if pattern != "^rcg-[0-9]{8}-[a-f0-9]{12}$":
            errors.append(f"receipt_id pattern wrong: {pattern}")

    # Test 8: public_phase exists
    if gw_path.exists():
        gw = json.loads(gw_path.read_text())
        pp = gw.get("public_phase", {})
        if pp.get("status") != "public_test_stabilization":
            errors.append("public_phase.status not public_test_stabilization")
        if not pp.get("receipt_is_not_final_inclusion"):
            errors.append("receipt_is_not_final_inclusion not true")

    if errors:
        print("FAIL: Contract test errors:\n")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print("PASS: All Record-Chain Intake Gateway contract tests passed.")
        sys.exit(0)




    # --- Phase 6B-OATH: Oath gate contract tests ---

    # Test 9: Echo without oath -> rejected by validation
    sys.path.insert(0, str(ROOT))
    from apps.record_chain_intake_gateway.gateway.validation import validate_submission, _OATH_REQUIRED_RECORD_TYPES
    echo_submission = {
        "record_type": "echo",
        "record_draft": {
            "record_type": "echo",
            "context_readiness": {"declared_context_level": "CC-3"},
            "non_authority_boundary_acknowledgement": {
                "not_authority": True, "not_governance": True, "not_attestation": True,
                "not_successor_reception": True, "not_amendment": True, "bitcoin_originals_prevail": True,
                "receipt_is_not_final_inclusion": True, "test_phase_submission_may_be_reclassified": True,
            },
            "submitting_participant_identity": {
                "participant_public_display_label": "test",
                "participant_type": "agent",
                "participant_identifier_disclosure_status": "provided",
                "participant_identity_disclosure_preference": "public_agent_id",
            },
            "discovery_and_introduction_context": {
                "how_participant_first_discovered_trinity_accord": "self_discovered",
                "was_discovery_self_initiated": True,
                "was_discovery_introduced_by_someone_else": False,
                "introducing_party_type": "none",
                "discovery_intent_category": "open_exploration",
            },
            "decision_autonomy_context": {
                "who_decided_to_create_this_record": "self",
                "was_record_creation_self_decided": True,
                "participant_declares_free_choice": True,
            },
            "submission_execution_context": {
                "who_executed_the_submission": "self",
                "execution_operator_type": "self",
            },
            "authorization_context": {
                "was_external_authorization_required": False,
                "authorization_status": "self_authorized",
                "authorization_scope": "create_echo_record",
            },
        },
        "submission_boundary": {
            "not_authority": True, "not_governance": True, "not_attestation": True,
            "not_successor_reception": True, "not_amendment": True, "bitcoin_originals_prevail": True,
        },
    }
    diags = validate_submission(echo_submission)
    has_missing_oath = any(d.code == "MISSING_SUBMISSION_OATH" for d in diags)
    if not has_missing_oath:
        errors.append("Echo without oath should be rejected (MISSING_SUBMISSION_OATH)")

    # Test 10: Verification without oath -> rejected
    echo_submission["record_type"] = "verification"
    echo_submission["record_draft"]["record_type"] = "verification"
    diags = validate_submission(echo_submission)
    has_missing_oath = any(d.code == "MISSING_SUBMISSION_OATH" for d in diags)
    if not has_missing_oath:
        errors.append("Verification without oath should be rejected (MISSING_SUBMISSION_OATH)")

    # Test 11: Context-Insufficient Notice without oath -> accepted (oath not required)
    ci_submission = {
        "record_type": "context_insufficient_notice",
        "record_draft": {
            "record_type": "context_insufficient_notice",
            "context_readiness": {"declared_context_level": "CC-0", "context_sufficient_for_selected_action": False},
            "submitting_participant_identity": {
                "participant_public_display_label": "test",
                "participant_type": "agent",
                "participant_identifier_disclosure_status": "provided",
                "participant_identity_disclosure_preference": "public_agent_id",
            },
            "submission_execution_context": {
                "who_executed_the_submission": "self",
                "execution_operator_type": "self",
            },
        },
        "submission_boundary": {
            "not_authority": True, "not_governance": True, "not_attestation": True,
            "not_successor_reception": True, "not_amendment": True, "bitcoin_originals_prevail": True,
        },
    }
    diags = validate_submission(ci_submission)
    oath_errors = [d for d in diags if "OATH" in d.code]
    if oath_errors:
        errors.append(f"Context-Insufficient Notice should not require oath, got: {[d.code for d in oath_errors]}")


if __name__ == "__main__":
    main()
