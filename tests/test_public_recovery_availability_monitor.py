from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import monitor_public_recovery_topology as monitor  # noqa: E402


def release_payload(tag: str, names: list[str]) -> dict:
    return {
        "tag_name": tag,
        "draft": False,
        "prerelease": False,
        "assets": [
            {"name": name, "state": "uploaded", "size": index + 1}
            for index, name in enumerate(names)
        ],
    }


def zenodo_payload(record: dict) -> dict:
    return {
        "id": record["record_id"],
        "doi": record["doi"],
        "files": [
            {
                "key": name,
                "size": metadata["bytes"],
                "checksum": f"md5:{metadata['md5']}",
            }
            for name, metadata in record["files"].items()
        ],
    }


def gateway_payload() -> dict:
    return {
        "ok": True,
        "service": "record-chain-intake-gateway",
        "version": "1.2.2-protected",
        "protection_required": True,
        "protection_layer_active": True,
        "protection_entrypoint": (
            "apps.record_chain_intake_gateway.secure_entrypoint_hardened:app"
        ),
        "repo_configured": True,
        "branch_configured": True,
        "token_configured": True,
        "cooldown_secret_configured": True,
    }


def test_checked_in_topology_is_self_consistent() -> None:
    expected = monitor.load_expected_contract(ROOT)
    releases = {item["tag"]: item for item in expected["releases"]}
    assert releases["nft-arweave-mirror-175-v1"]["asset_names"] == []
    assert releases["nft-backup-v1"]["asset_names"] == [
        "nft-cars-manifest.tar.gz",
        *[f"nft-cars-part{index:02d}.tar.gz" for index in range(1, 10)],
    ]
    records = {item["record_id"]: item for item in expected["zenodo_records"]}
    assert records[21754229]["doi"] == "10.5281/zenodo.21754229"
    repository_state = json.loads(
        (ROOT / "preservation/zenodo-state.json").read_text(encoding="utf-8")
    )
    assert records[repository_state["latest_record_id"]]["doi"] == repository_state["latest_doi"]


def test_release_validation_is_exact_and_fail_closed() -> None:
    names = ["manifest.tar.gz", "part01.tar.gz"]
    monitor.validate_release(
        release_payload("backup-v1", names),
        label="backup",
        tag="backup-v1",
        expected_asset_names=names,
    )
    bad = release_payload("backup-v1", names + ["unexpected.tar.gz"])
    with pytest.raises(monitor.MonitorError, match="asset set mismatch"):
        monitor.validate_release(
            bad,
            label="backup",
            tag="backup-v1",
            expected_asset_names=names,
        )


def test_zenodo_validation_checks_inventory_size_and_md5_without_payload_download() -> None:
    expected = monitor.load_expected_contract(ROOT)["zenodo_records"][0]
    payload = zenodo_payload(expected)
    monitor.validate_zenodo_record(
        payload,
        label=expected["label"],
        record_id=expected["record_id"],
        doi=expected["doi"],
        expected_files=expected["files"],
    )
    payload["files"][0]["checksum"] = "md5:" + "0" * 32
    with pytest.raises(monitor.MonitorError, match="MD5 metadata drift"):
        monitor.validate_zenodo_record(
            payload,
            label=expected["label"],
            record_id=expected["record_id"],
            doi=expected["doi"],
            expected_files=expected["files"],
        )


def test_live_checks_cover_all_six_public_surfaces() -> None:
    expected = monitor.load_expected_contract(ROOT)

    def fake_fetch(url: str, **_: object) -> dict:
        if "/releases/tags/" in url:
            tag = url.rsplit("/", 1)[-1]
            release = next(item for item in expected["releases"] if item["tag"] == tag)
            return release_payload(tag, release["asset_names"])
        if "/records/" in url:
            record_id = int(url.rsplit("/", 1)[-1])
            record = next(
                item for item in expected["zenodo_records"] if item["record_id"] == record_id
            )
            return zenodo_payload(record)
        if url.endswith("/api/status.json"):
            return expected["site_status"]
        if url.endswith("/healthz"):
            return gateway_payload()
        raise AssertionError(url)

    checks, errors = monitor.run_live_checks(
        expected,
        repository="thechurchofagi/trinity-accord",
        site="https://www.trinityaccord.org",
        gateway="https://trinity-record-chain-gateway.onrender.com",
        github_api="https://api.github.com",
        zenodo_api="https://zenodo.org/api",
        timeout=1,
        attempts=1,
        fetcher=fake_fetch,
    )
    assert errors == []
    assert len(checks) == 6


def test_gateway_health_requires_the_hardened_protection_layer() -> None:
    payload = gateway_payload()
    monitor.validate_gateway_health(payload)
    payload["protection_layer_active"] = False
    with pytest.raises(monitor.MonitorError, match="protection is not active"):
        monitor.validate_gateway_health(payload)


def test_workflow_is_read_only_weekly_manual_and_preserves_reports() -> None:
    path = ROOT / ".github/workflows/public-recovery-availability.yml"
    text = path.read_text(encoding="utf-8")
    parsed = yaml.load(text, Loader=yaml.BaseLoader)
    assert set(parsed["on"]) == {"workflow_dispatch", "schedule"}
    assert parsed["permissions"] == {"contents": "read"}
    assert parsed["jobs"]["verify"]["runs-on"] == "ubuntu-24.04"
    assert "scripts/check_legacy_pointer_coverage.py" in text
    assert "scripts/monitor_public_recovery_topology.py" in text
    assert "large payloads are never downloaded" in text
    assert "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02" in text
    assert "contents: write" not in text


def test_registry_marks_the_two_maintenance_items_automated() -> None:
    registry = json.loads((ROOT / "GUARDIANSHIP-SYSTEM-REGISTRY.json").read_text())
    current = registry["current_determination"]
    automated = current["automated_maintenance"]
    remaining = current["remaining_work"]
    for name in (
        "periodic_legacy_pointer_coverage_audit",
        "ongoing_release_gateway_monitoring",
    ):
        assert automated[name]["status"] == "automated"
        assert automated[name]["read_only"] is True
        assert name not in remaining


def test_contract_only_cli_runs_without_network(tmp_path: Path) -> None:
    report = tmp_path / "report.json"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/monitor_public_recovery_topology.py"),
            "--contract-only",
            "--report",
            str(report),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(report.read_text())
    assert payload["status"] == "PASS"
    assert payload["large_payload_bytes_downloaded"] == 0
