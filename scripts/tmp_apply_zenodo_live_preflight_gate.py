#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def update_gateway_descriptor() -> None:
    path = ROOT / "api" / "record-chain-intake-gateway.v1.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["runtime_alignment"]["context_compatibility_minimums"] = {
        "echo": "CC-3",
        "verification": "CC-3",
        "guardian_application": "CC-3",
        "guardian_retirement": "CC-1",
        "propagation": "CC-2",
        "correction": "CC-1",
        "classification_update": "CC-2",
        "context_insufficient_notice": "CC-0",
    }
    data["updated_at"] = "2026-08-05T04:35:00Z"
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def update_deploy_workflow() -> None:
    path = ROOT / ".github" / "workflows" / "deploy-pages.yml"
    text = path.read_text(encoding="utf-8")

    old_regex = (
        r"'^(\.github/workflows/(deploy-pages|render-manual-deploy)\.yml|"
        r"api/record-chain-oath-policy\.v1\.json|"
        r"apps/record_chain_intake_gateway/.*|"
        r"downloads/record-chain-builder\.mjs|render\.yaml|"
        r"scripts/render_(manual|protected)_deploy\.py)$'"
    )
    new_regex = (
        r"'^(\.github/workflows/(deploy-pages|render-manual-deploy)\.yml|"
        r"api/record-chain-oath-policy\.v1\.json|"
        r"apps/record_chain_intake_gateway/.*|"
        r"downloads/record-chain-builder\.mjs|render\.yaml|"
        r"scripts/(render_(manual|protected)_deploy|"
        r"smoke_live_record_action_preflight)\.py)$'"
    )
    if old_regex not in text:
        raise SystemExit("deploy rollout regex anchor not found")
    text = text.replace(old_regex, new_regex, 1)

    anchor = '''      - name: Deploy exact Gateway source and wait for live
        if: steps.scope.outputs.required == 'true'
        env:
          RENDER: ${{ secrets.RENDER }}
          SOURCE_SHA: ${{ needs.verify.outputs.source_sha }}
        run: |
          set -euo pipefail
          python3 scripts/render_protected_deploy.py \\
            --service trinity-record-chain-gateway \\
            --reconcile-config \\
            --deploy \\
            --commit-id "$SOURCE_SHA" \\
            --wait \\
            --wait-timeout 900 \\
            --poll-seconds 10
'''
    addition = anchor + '''
      - name: Install live preflight dependencies
        if: steps.scope.outputs.required == 'true'
        env:
          PIP_PREFER_BINARY: "1"
          PIP_ONLY_BINARY: "cryptography,cffi"
        run: python3 -m pip install -r requirements-ci.txt

      - name: Run no-write live record action preflight matrix
        if: steps.scope.outputs.required == 'true'
        run: |
          set -euo pipefail
          python3 scripts/smoke_live_record_action_preflight.py \\
            --output "$RUNNER_TEMP/live-record-action-preflight-report.json"

      - name: Upload live record action preflight proof
        if: always() && steps.scope.outputs.required == 'true'
        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4
        with:
          name: live-record-action-preflight-proof-${{ github.run_id }}
          path: ${{ runner.temp }}/live-record-action-preflight-report.json
          if-no-files-found: error
          retention-days: 30
'''
    if anchor not in text:
        raise SystemExit("gateway deployment anchor not found")
    text = text.replace(anchor, addition, 1)
    path.write_text(text, encoding="utf-8")


def create_regression_tests() -> None:
    path = ROOT / "tests" / "test_preservation_refresh_and_live_preflight_gate.py"
    path.write_text(
        '''from __future__ import annotations

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
        "guardian_retirement_cc1_context_accept",
        "guardian_retirement_cc0_context_reject",
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
    build_pos = workflow.index("\n  build:\n")
    assert deploy_pos < smoke_pos < build_pos
    assert "live-record-action-preflight-proof-${{ github.run_id }}" in workflow
''',
        encoding="utf-8",
    )


def main() -> None:
    update_gateway_descriptor()
    update_deploy_workflow()
    create_regression_tests()


if __name__ == "__main__":
    main()
