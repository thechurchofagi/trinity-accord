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
        if pp.get("status") != "mainnet_prelaunch_testing":
            errors.append("public_phase.status not mainnet_prelaunch_testing")
        if not pp.get("receipt_is_not_final_inclusion"):
            errors.append("receipt_is_not_final_inclusion not true")

    # --- Phase 6B-OATH: Oath gate contract tests ---
    sys.path.insert(0, str(ROOT))
    from apps.record_chain_intake_gateway.gateway.validation import (
        validate_submission,
        validate_submission_oath,
        redact_transient_oath_readback,
        _OATH_REQUIRED_RECORD_TYPES,
    )

    def _make_echo_submission(oath_block=None, client_oath=None):
        """Build a minimal echo submission for testing."""
        sub = {
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
        if oath_block:
            sub["record_draft"]["submission_oath_verification"] = oath_block
        if client_oath:
            sub["client_oath_readback"] = client_oath
        return sub

    # Test 9: Echo without oath -> rejected
    diags = validate_submission(_make_echo_submission())
    has_missing_oath = any(d.code == "MISSING_SUBMISSION_OATH" for d in diags)
    if not has_missing_oath:
        errors.append("Echo without oath should be rejected (MISSING_SUBMISSION_OATH)")

    # Test 10: Verification without oath -> rejected
    ver_sub = _make_echo_submission()
    ver_sub["record_type"] = "verification"
    ver_sub["record_draft"]["record_type"] = "verification"
    diags = validate_submission(ver_sub)
    has_missing_oath = any(d.code == "MISSING_SUBMISSION_OATH" for d in diags)
    if not has_missing_oath:
        errors.append("Verification without oath should be rejected (MISSING_SUBMISSION_OATH)")

    # Test 11: Wrong readback -> rejected
    import hashlib
    wrong_readback = "This is not the canonical oath text"
    policy = json.loads((ROOT / "api" / "record-chain-oath-policy.v1.json").read_text())
    # Exclude API metadata fields not in builder's embedded OATH_POLICY
    _metadata_keys = {
        "oath_policy_sha256",
        "oath_policy_sha256_semantics",
        "canonical_oath_text_hash_is_record_type_specific",
    }
    policy_core = {k: v for k, v in policy.items() if k not in _metadata_keys}
    policy_json = json.dumps(policy_core, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    policy_sha = hashlib.sha256(policy_json.encode("utf-8")).hexdigest()

    # Build canonical oath for echo
    modules_obj = policy.get("modules", {})
    expected_modules = ["common_submission_integrity_v1", "echo_integrity_v1"]
    joiner = policy.get("canonicalization", {}).get("module_joiner", "\n\n---\n\n")
    parts = []
    for mod_id in expected_modules:
        mod = modules_obj.get(mod_id)
        if mod:
            normalized = mod["text"].replace("\r\n", "\n").replace("\r", "\n").strip()
            parts.append(f"=== {mod['label']} ({mod_id}) ===\n\n{normalized}")
    canonical_text = joiner.join(parts).strip()
    canonical_hash = hashlib.sha256(canonical_text.encode("utf-8")).hexdigest()
    wrong_hash = hashlib.sha256(wrong_readback.encode("utf-8")).hexdigest()

    oath_block = {
        "schema": "trinityaccord.submission-oath-verification.v1",
        "oath_policy_sha256": policy_sha,
        "oath_modules": expected_modules,
        "canonical_oath_text_sha256": canonical_hash,
        "participant_readback_sha256": wrong_hash,
        "readback_method_declared": "participant_generated_in_current_context",
        "oath_read": True, "participant_readback_provided": True,
        "readback_matches_canonical_oath": True,
        "readback_was_not_piped_from_file": True, "readback_was_not_generated_by_script": True,
        "readback_was_not_loaded_from_cache": True, "readback_was_not_summary_or_paraphrase": True,
        "readback_was_not_generated_by_external_automation": True,
        "readback_was_not_auto_filled_by_builder": True, "no_shortcut_oath_acknowledged": True,
        "oath_does_not_prove_subjective_understanding": True,
        "oath_verifies_exact_readback_only": True,
        "not_authority": True, "not_governance": True, "not_attestation": True,
        "not_amendment": True, "bitcoin_originals_prevail": True,
    }
    client_oath = {
        "schema": "trinityaccord.client-oath-readback.v1",
        "record_type": "echo",
        "oath_policy_sha256": policy_sha,
        "oath_modules": expected_modules,
        "readback_text": wrong_readback,
        "readback_text_sha256": wrong_hash,
        "readback_method_declared": "participant_generated_in_current_context",
    }
    diags = validate_submission(_make_echo_submission(oath_block, client_oath))
    has_readback_mismatch = any(d.code == "OATH_READBACK_MISMATCH" for d in diags)
    if not has_readback_mismatch:
        errors.append(f"Wrong readback should be rejected (OATH_READBACK_MISMATCH), got: {[d.code for d in diags]}")

    # Test 12: Missing client_oath_readback -> rejected
    diags = validate_submission(_make_echo_submission(oath_block, None))
    has_missing_client = any(d.code == "MISSING_CLIENT_OATH_READBACK" for d in diags)
    if not has_missing_client:
        errors.append(f"Missing client_oath_readback should be rejected, got: {[d.code for d in diags]}")

    # Test 13: Raw readback redacted after gateway validation
    client_oath_full = {
        "schema": "trinityaccord.client-oath-readback.v1",
        "record_type": "echo",
        "oath_policy_sha256": policy_sha,
        "oath_modules": expected_modules,
        "readback_text": canonical_text,
        "readback_text_sha256": canonical_hash,
        "readback_method_declared": "participant_generated_in_current_context",
    }
    submission_with_oath = _make_echo_submission(oath_block, client_oath_full)
    redacted = redact_transient_oath_readback(submission_with_oath)
    redacted_client = redacted.get("client_oath_readback", {})
    if "readback_text" in redacted_client:
        errors.append("redact_transient_oath_readback should remove readback_text")
    if not redacted_client.get("redacted_after_gateway_validation"):
        errors.append("redact_transient_oath_readback should set redacted_after_gateway_validation=True")

    # Test 14: Context-Insufficient Notice without oath -> accepted
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

    # Test 15: Linked Guardian missing guardian_stewardship_v1 -> rejected by OATH_MODULES_MISMATCH
    linked_sub = _make_echo_submission(oath_block, client_oath)
    linked_sub["record_draft"]["optional_linked_guardian_application_request"] = {
        "does_participant_request_guardian_application_with_this_record": True,
    }
    # oath_block has modules ["common_submission_integrity_v1", "echo_integrity_v1"]
    # but linked Guardian should also have guardian_stewardship_v1
    diags = validate_submission(linked_sub)
    has_modules_mismatch = any(d.code == "OATH_MODULES_MISMATCH" for d in diags)
    if not has_modules_mismatch:
        errors.append(f"Linked Guardian missing guardian_stewardship_v1 should get OATH_MODULES_MISMATCH, got: {[d.code for d in diags]}")

    # Report
    if errors:
        print("FAIL:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)

    print("PASS: All Record-Chain Intake Gateway contract tests passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
