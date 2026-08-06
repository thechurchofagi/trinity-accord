from __future__ import annotations

import importlib
import sys
from pathlib import Path

from apps.record_chain_intake_gateway.gateway import runtime

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_ENTRYPOINT = (
    "apps.record_chain_intake_gateway.secure_entrypoint_hardened:app"
)
EXPECTED_COMMAND = f"uvicorn {EXPECTED_ENTRYPOINT} --host 0.0.0.0 --port $PORT"


def test_render_configs_attest_exact_hardened_entrypoint() -> None:
    for path in (
        ROOT / "render.yaml",
        ROOT / "apps" / "record_chain_intake_gateway" / "render.yaml",
    ):
        text = path.read_text(encoding="utf-8")
        assert f"startCommand: {EXPECTED_COMMAND}" in text
        assert "value: 1.2.2-protected" in text
        assert "key: TRINITY_GATEWAY_PROTECTION_ENTRYPOINT" in text
        assert f"value: {EXPECTED_ENTRYPOINT}" in text


def test_runtime_reports_configured_hardened_entrypoint(monkeypatch) -> None:
    monkeypatch.setenv("TRINITY_GATEWAY_PROTECTION_ENTRYPOINT", EXPECTED_ENTRYPOINT)
    runtime.mark_protection_layer_active()
    assert runtime.get_runtime_info()["protection_entrypoint"] == EXPECTED_ENTRYPOINT


def test_official_workflow_uses_synchronized_hardened_deployer() -> None:
    workflow = (
        ROOT / ".github" / "workflows" / "render-manual-deploy.yml"
    ).read_text(encoding="utf-8")
    assert 'python scripts/render_hardened_deploy.py "${args[@]}"' in workflow


def test_hardened_deployer_patches_shared_exact_commit_contract() -> None:
    scripts = str(ROOT / "scripts")
    sys.path.insert(0, scripts)
    try:
        module = importlib.import_module("render_hardened_deploy")
        assert module.EXPECTED_ENTRYPOINT == EXPECTED_ENTRYPOINT
        assert module.EXPECTED_START_COMMAND == EXPECTED_COMMAND
        assert module.EXPECTED_RUNTIME_VERSION == "1.2.2-protected"
        assert (
            module.protected.base.EXPECTED_GATEWAY_ENV[
                "TRINITY_GATEWAY_PROTECTION_ENTRYPOINT"
            ]
            == EXPECTED_ENTRYPOINT
        )
        assert (
            module.protected.base.EXPECTED_GATEWAY_READINESS[
                "protection_entrypoint"
            ]
            == EXPECTED_ENTRYPOINT
        )
    finally:
        sys.path.remove(scripts)
