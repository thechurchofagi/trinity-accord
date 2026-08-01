from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_guardian_machine_contract_uses_record_chain_current_state_only():
    contract = json.loads((ROOT / "api/guardian-alliance.json").read_text(encoding="utf-8"))
    current_registry = "/api/guardian-current-registry.json"
    guardian_state = "/record-chain/indexes/guardian-state.json"
    legacy_registry = "/api/guardian-registry.json"

    active_stage = contract["join_path"]["stages"][-1]
    assert active_stage["guardian_registry_number_source"] == current_registry
    assert contract["join_path"]["post_submit_readback"] == [
        "receipt_status",
        "/api/record-chain-status.json",
        current_registry,
        guardian_state,
    ]
    assert contract["references"]["registry"] == current_registry
    assert contract["references"]["guardian_state"] == guardian_state
    assert contract["references"]["legacy_registry_historical_archive"] == legacy_registry
    assert "registry_schema" not in contract["references"]
    assert all(legacy_registry not in step for step in contract["verification_steps"])
    assert any(current_registry in step and guardian_state in step for step in contract["verification_steps"])

    # The historical path may remain only in its explicitly historical field.
    occurrences = json.dumps(contract, sort_keys=True).count(legacy_registry)
    assert occurrences == 1


def test_guardian_page_contains_only_runnable_current_verification_command():
    page = (ROOT / "guardian-alliance.md").read_text(encoding="utf-8")
    assert "scripts/verify_guardian_status.py" not in page
    assert "python3 scripts/trinity_record_chain.py verify" in page
    assert (ROOT / "scripts/trinity_record_chain.py").is_file()
    assert "/api/guardian-current-registry.json" in page
    assert "/record-chain/indexes/guardian-state.json" in page


def test_gateway_machine_contract_declares_guardian_semantic_uniqueness_guards():
    gateway = json.loads(
        (ROOT / "api/record-chain-intake-gateway.v1.json").read_text(encoding="utf-8")
    )
    pipeline = gateway["server_side_pipeline"]
    runtime = gateway["runtime_alignment"]
    assert pipeline["guardian_application_preflight_checks_final_and_pending_uniqueness"] is True
    assert pipeline["guardian_application_submit_claims_identifier_and_public_key_atomically"] is True
    assert pipeline["guardian_application_finalizer_rechecks_uniqueness_before_chain_mutation"] is True
    assert runtime["guardian_semantic_uniqueness_claims_share_intake_atomic_commit"] is True
