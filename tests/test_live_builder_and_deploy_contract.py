from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_canonical_builder_manifest_binds_current_single_file_entrypoint() -> None:
    builder = (ROOT / "downloads/record-chain-builder.mjs").read_bytes()
    mirror = (ROOT / "builder-bundles/record-chain-builder.mjs").read_bytes()
    manifest = json.loads(
        (ROOT / "api/record-chain-builder-bundles.v1.json").read_text(encoding="utf-8")
    )
    canonical = manifest["canonical_builder"]

    assert builder == mirror
    assert canonical["size_bytes"] == len(builder)
    assert canonical["sha256"] == hashlib.sha256(builder).hexdigest()
    assert canonical["recovery_wrapper"]["automatically_fetched_when_companion_missing"] is True
    assert manifest["acquisition_policy"][
        "one_file_download_bootstraps_verified_recovery_and_core"
    ] is True


def test_canonical_builder_bootstraps_pinned_recovery_layer() -> None:
    source = (ROOT / "downloads/record-chain-builder.mjs").read_text(encoding="utf-8")
    manifest = json.loads(
        (ROOT / "api/record-chain-builder-bundles.v1.json").read_text(encoding="utf-8")
    )
    recovery = manifest["canonical_builder"]["recovery_wrapper"]

    assert recovery["sha256"] in source
    assert str(recovery["size_bytes"]) in source
    assert "resolveRecoveryModule" in source
    assert "downloadVerifiedRecovery" in source
    assert "https://www.trinityaccord.org/downloads/record-chain-builder-recovery.mjs" in source
    assert "https://raw.githubusercontent.com/thechurchofagi/trinity-accord/main/downloads/record-chain-builder-recovery.mjs" in source


def test_repository_local_builder_bundle_executes() -> None:
    completed = subprocess.run(
        ["node", str(ROOT / "downloads/record-chain-builder.mjs"), "--help"],
        cwd=ROOT / "downloads",
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=60,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout
    assert "Zero-clone Record-Chain submission builder" in completed.stdout


def test_standard_render_adapter_matches_hardened_runtime_contract() -> None:
    path = ROOT / "scripts/render_protected_deploy.py"
    spec = importlib.util.spec_from_file_location("render_protected_contract_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    expected = "apps.record_chain_intake_gateway.secure_entrypoint_hardened:app"
    assert module.EXPECTED_ENTRYPOINT == expected
    assert module.EXPECTED_RUNTIME_VERSION == "1.2.2-protected"
    assert module.base.EXPECTED_GATEWAY_START_COMMAND == (
        f"uvicorn {expected} --host 0.0.0.0 --port $PORT"
    )
    assert module.base.EXPECTED_GATEWAY_ENV[
        "TRINITY_GATEWAY_PROTECTION_ENTRYPOINT"
    ] == expected
    assert module.base.EXPECTED_GATEWAY_READINESS["protection_entrypoint"] == expected


def test_render_yaml_and_standard_adapter_agree() -> None:
    render = (ROOT / "render.yaml").read_text(encoding="utf-8")
    adapter = (ROOT / "scripts/render_protected_deploy.py").read_text(encoding="utf-8")
    assert "secure_entrypoint_hardened:app" in render
    assert "1.2.2-protected" in render
    assert "secure_entrypoint_hardened:app" in adapter
    assert "1.2.2-protected" in adapter


def test_live_journey_checks_real_builder_download_and_execution() -> None:
    helper = (ROOT / "scripts/smoke_live_builder_download.py").read_text(encoding="utf-8")
    scheduled = (
        ROOT / "scripts/smoke_external_agent_entrypoint_journeys.py"
    ).read_text(encoding="utf-8")
    freshness = (ROOT / "scripts/check_deployment_freshness_v2.py").read_text(
        encoding="utf-8"
    )

    assert "hashlib.sha256(builder)" in helper
    assert '["node", str(entrypoint), "--help"]' in helper
    assert "verify_builder" in scheduled
    assert "verify_builder" in freshness
