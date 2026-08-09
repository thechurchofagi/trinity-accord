from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_consumed_preservation_refresh_is_secret_independent():
    env = os.environ.copy()
    env.pop("ZENODO_ACCESS_TOKEN", None)
    env.pop("PRESERVATION_CAPSULE_ZENODO_RIGHTS_ACK", None)
    env.pop("RUNNER_TEMP", None)
    completed = subprocess.run(
        ["bash", "scripts/run_repository_preservation_refresh_ci.sh"],
        cwd=ROOT,
        env=env,
        check=True,
        text=True,
        capture_output=True,
    )
    v3_auth_path = ROOT / "preservation/current-baseline-publication-authorization-v3.json"
    if v3_auth_path.is_file():
        v3_status = json.loads(v3_auth_path.read_text(encoding="utf-8"))["status"]
        assert f"Final evidence baseline publication v3 state valid: {v3_status}" in completed.stdout
        if v3_status == "consumed":
            assert "consumed and valid; no external write will run" in completed.stdout
        else:
            assert "external publication requires the dedicated main-branch preservation executor" in completed.stdout
        return
    v2_auth_path = ROOT / "preservation/current-baseline-publication-authorization-v2.json"
    if v2_auth_path.is_file():
        v2_status = json.loads(v2_auth_path.read_text(encoding="utf-8"))["status"]
        if v2_status == "consumed":
            assert "Current baseline publication v2 state valid: consumed" in completed.stdout
            assert "Final proof baseline publication v2 is consumed and valid; no external write will run." in completed.stdout
            return

    current_auth_path = ROOT / "preservation/current-baseline-publication-authorization-v1.json"
    current_status = (
        json.loads(current_auth_path.read_text(encoding="utf-8"))["status"]
        if current_auth_path.is_file()
        else "absent"
    )
    if current_status == "prepared":
        assert "prepared transition valid; prior DOI remains active" in completed.stdout
        assert "legacy refresh remains consumed" in completed.stdout
    elif current_status == "consumed":
        assert "current-baseline publication is consumed and valid" in completed.stdout
        assert "legacy refresh remains consumed" in completed.stdout
    else:
        assert "already consumed and publicly proven" in completed.stdout


def test_publication_credentials_remain_required_before_nonterminal_work():
    source = (ROOT / "scripts/run_repository_preservation_refresh_ci.sh").read_text(
        encoding="utf-8"
    )
    consumed_guard = source.index('if [[ "$status" == "consumed" ]]')
    token_guard = source.index('${ZENODO_ACCESS_TOKEN:?ZENODO_ACCESS_TOKEN is required}')
    rights_guard = source.index(
        '${PRESERVATION_CAPSULE_ZENODO_RIGHTS_ACK:?PRESERVATION_CAPSULE_ZENODO_RIGHTS_ACK is required}'
    )
    assert consumed_guard < token_guard
    assert consumed_guard < rights_guard
    assert "repository_preservation_refresh.py validate" in source
    assert "validate_current_baseline_prepared_state.py" in source
    assert "validate_current_baseline_publication_state.py" in source
    assert "TRINITY_PRESERVATION_CAPSULE_RIGHTS_V1_APPROVED" in source


def test_gateway_descriptor_exposes_current_action_minimums():
    descriptor = json.loads(
        (ROOT / "api/record-chain-intake-gateway.v1.json").read_text(encoding="utf-8")
    )
    assert descriptor["runtime_alignment"]["context_compatibility_minimums"] == {
        "echo": "CC-3",
        "verification": "CC-3",
        "guardian_application": "CC-3",
        "guardian_retirement": "CC-1",
        "propagation": "CC-2",
        "correction": "CC-1",
        "classification_update": "CC-2",
        "context_insufficient_notice": "CC-0",
    }


def test_live_preflight_gate_covers_changed_routes_without_submit():
    source = (ROOT / "scripts/smoke_live_record_action_preflight.py").read_text(
        encoding="utf-8"
    )
    for marker in (
        "echo_cc3_accept",
        "echo_cc2_reject",
        "verification_v2_cc3_accept",
        "verification_v2_cc2_reject",
        "guardian_application_cc3_accept",
        "guardian_application_cc2_reject",
        "guardian_retirement_cc1_reaches_target_binding",
        "guardian_retirement_cc0_context_reject",
        "GUARDIAN_RETIREMENT_TARGET_NOT_FOUND",
    ):
        assert marker in source
    assert 'base_url.rstrip("/") + "/record-chain/preflight"' in source
    assert '"submit_endpoint_called": False' in source
    assert '"/record-chain/submit"' not in source


def test_pages_deploy_runs_live_preflight_after_gateway_rollout():
    workflow = (ROOT / ".github/workflows/deploy-pages.yml").read_text(
        encoding="utf-8"
    )
    deploy_pos = workflow.index("Deploy exact Gateway source and wait for live")
    smoke_pos = workflow.index("Run no-write live record action preflight matrix")
    build_pos = workflow.index("  build:")
    assert deploy_pos < smoke_pos < build_pos
    assert "live-record-action-preflight-proof-${{ github.run_id }}" in workflow
    assert "smoke_live_record_action_preflight" in workflow
