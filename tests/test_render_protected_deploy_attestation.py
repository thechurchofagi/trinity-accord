from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "render_protected_deploy.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "render_protected_deploy_attestation_test", MODULE_PATH
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_protected_attestation_uses_observed_runtime(monkeypatch, capsys):
    module = _load_module()
    monkeypatch.setattr(
        module,
        "verify_public_gateway_protection_once",
        lambda _base_url: {
            "protection_layer_active": True,
            "protected_readiness_http": 200,
            "runtime_version": "9.9.9-observed",
            "request_max_bytes": 98304,
            "oversized_preflight_http": 413,
            "submit_called": False,
        },
    )

    module.verify_public_gateway_protection(
        "https://example.invalid", attempts=1, delay_seconds=0
    )

    output = capsys.readouterr().out
    assert "runtime_version=9.9.9-observed" in output
    assert "runtime_version=1.2.1-protected" not in output
    assert "request_max_bytes=98304" in output
    assert "submit_called=false" in output
