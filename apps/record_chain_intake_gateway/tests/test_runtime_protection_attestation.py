"""Regression tests for code-bound Gateway protection attestation."""

from apps.record_chain_intake_gateway.gateway import runtime


def test_active_protection_attestation_ignores_environment_override(monkeypatch):
    monkeypatch.setattr(runtime, "_protection_layer_active", True)
    monkeypatch.setenv(
        "TRINITY_GATEWAY_PROTECTION_ENTRYPOINT",
        "incorrect.operator.config:app",
    )

    info = runtime.get_runtime_info()

    assert info["protection_layer_active"] is True
    assert info["protection_entrypoint"] == runtime.PROTECTION_ENTRYPOINT
    assert info["global_acceptance_cooldown_seconds"] == {
        "minimum": 3600,
        "maximum": 7200,
        "secret_keyed": True,
    }


def test_core_app_cannot_claim_protected_entrypoint(monkeypatch):
    monkeypatch.setattr(runtime, "_protection_layer_active", False)
    monkeypatch.setenv(
        "TRINITY_GATEWAY_PROTECTION_ENTRYPOINT",
        runtime.PROTECTION_ENTRYPOINT,
    )

    info = runtime.get_runtime_info()

    assert info["protection_layer_active"] is False
    assert info["protection_entrypoint"] == "core_app_without_protection_wrapper"
    assert info["global_acceptance_cooldown_seconds"] is None
