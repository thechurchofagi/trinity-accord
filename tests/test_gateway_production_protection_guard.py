from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run_isolated(code: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update({
        "TRINITY_ENFORCE_PROTECTION_LAYER": "1",
        "TRINITY_REPO_FULL_NAME": "thechurchofagi/trinity-accord",
        "TRINITY_TARGET_BRANCH": "main",
        "TRINITY_GITHUB_TOKEN": "test-token",
        "TRINITY_COOLDOWN_SECRET": "test-secret",
        "TRINITY_GATEWAY_RUNTIME_VERSION": "1.2.1-protected",
    })
    return subprocess.run(
        [sys.executable, "-c", textwrap.dedent(code)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_direct_core_app_fails_closed_when_protection_is_required() -> None:
    result = _run_isolated(
        """
        from fastapi.testclient import TestClient
        from apps.record_chain_intake_gateway.app import app

        client = TestClient(app)
        health = client.get('/healthz')
        assert health.status_code == 503, health.text
        assert health.json()['ok'] is False
        assert health.json()['protection_required'] is True
        assert health.json()['protection_layer_active'] is False

        readiness = client.get('/record-chain/readiness')
        assert readiness.status_code == 503, readiness.text
        data = readiness.json()
        assert data['submit_ready'] is False
        assert data['preflight_ready'] is False
        assert data['protection_required'] is True
        assert data['protection_layer_active'] is False

        for route in ('/record-chain/preflight', '/record-chain/submit'):
            response = client.post(route, json={})
            assert response.status_code == 503, (route, response.text)
            assert response.json()['diagnostic_code'] == 'PROTECTION_LAYER_INACTIVE'
        """
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_secure_entrypoint_satisfies_required_protection_contract() -> None:
    result = _run_isolated(
        """
        from fastapi.testclient import TestClient
        from apps.record_chain_intake_gateway.secure_entrypoint import app

        client = TestClient(app)
        for route in ('/healthz', '/readyz'):
            response = client.get(route)
            assert response.status_code == 200, (route, response.text)
            data = response.json()
            assert data['ok'] is True
            assert data['protection_required'] is True
            assert data['protection_layer_active'] is True

        readiness = client.get('/record-chain/readiness')
        assert readiness.status_code == 200, readiness.text
        data = readiness.json()
        assert data['submit_ready'] is True
        assert data['preflight_ready'] is True
        assert data['protection_required'] is True
        assert data['protection_layer_active'] is True
        """
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_machine_contract_describes_layered_fail_closed_health() -> None:
    import json

    contract = json.loads(
        (ROOT / 'api/record-chain-intake-gateway.v1.json').read_text(encoding='utf-8')
    )
    endpoints = contract['endpoints']
    assert endpoints['health']['path'] == '/healthz'
    assert endpoints['protected_readiness']['path'] == '/readyz'
    runtime = contract['runtime_alignment']
    assert runtime['core_app_fails_closed_when_protection_required'] is True
    assert runtime['preflight_and_submit_fail_closed_without_required_protection'] is True


def test_fastapi_metadata_matches_gateway_contract_version() -> None:
    result = _run_isolated(
        """
        from apps.record_chain_intake_gateway.app import app, _GATEWAY_SCHEMA
        assert app.version == _GATEWAY_SCHEMA['version'] == '1.1.0'
        """
    )
    assert result.returncode == 0, result.stdout + result.stderr
