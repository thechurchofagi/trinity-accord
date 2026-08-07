"""Regression tests for code-bound Gateway protection attestation."""

import pytest

from apps.record_chain_intake_gateway.gateway import runtime


def _reset_runtime_marker(monkeypatch) -> None:
    monkeypatch.setattr(runtime, "_protection_layer_active", False)
    monkeypatch.setattr(runtime, "_protection_entrypoint", None)


def test_base_entrypoint_attestation_ignores_environment_override(monkeypatch):
    _reset_runtime_marker(monkeypatch)
    monkeypatch.setenv(
        "TRINITY_GATEWAY_PROTECTION_ENTRYPOINT",
        runtime.HARDENED_PROTECTION_ENTRYPOINT,
    )

    runtime.mark_protection_layer_active(runtime.BASE_PROTECTION_ENTRYPOINT)
    info = runtime.get_runtime_info()

    assert info["protection_layer_active"] is True
    assert info["protection_entrypoint"] == runtime.BASE_PROTECTION_ENTRYPOINT


def test_hardened_entrypoint_attestation_is_code_bound(monkeypatch):
    _reset_runtime_marker(monkeypatch)
    monkeypatch.setenv(
        "TRINITY_GATEWAY_PROTECTION_ENTRYPOINT",
        runtime.BASE_PROTECTION_ENTRYPOINT,
    )

    runtime.mark_protection_layer_active(runtime.HARDENED_PROTECTION_ENTRYPOINT)
    info = runtime.get_runtime_info()

    assert info["protection_layer_active"] is True
    assert info["protection_entrypoint"] == runtime.HARDENED_PROTECTION_ENTRYPOINT
    assert info["global_acceptance_cooldown_seconds"] == {
        "minimum": 3600,
        "maximum": 7200,
        "secret_keyed": True,
    }


def test_core_app_cannot_claim_protected_entrypoint(monkeypatch):
    _reset_runtime_marker(monkeypatch)
    monkeypatch.setenv(
        "TRINITY_GATEWAY_PROTECTION_ENTRYPOINT",
        runtime.HARDENED_PROTECTION_ENTRYPOINT,
    )

    info = runtime.get_runtime_info()

    assert info["protection_layer_active"] is False
    assert info["protection_entrypoint"] == "core_app_without_protection_wrapper"
    assert info["global_acceptance_cooldown_seconds"] is None


def test_unknown_entrypoint_cannot_be_attested(monkeypatch):
    _reset_runtime_marker(monkeypatch)

    with pytest.raises(ValueError, match="unknown protection entrypoint"):
        runtime.mark_protection_layer_active("incorrect.operator.config:app")

    assert runtime.get_runtime_info()["protection_layer_active"] is False
