from __future__ import annotations

import base64
import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import build_offline_dependency_capsule as deps  # noqa: E402
import request_software_heritage_save as swh  # noqa: E402


def test_npm_lock_parser_requires_registry_urls_and_integrity(tmp_path):
    lock = tmp_path / "package-lock.json"
    raw = b"payload"
    integrity = "sha512-" + base64.b64encode(hashlib.sha512(raw).digest()).decode()
    lock.write_text(
        json.dumps(
            {
                "packages": {
                    "": {},
                    "node_modules/example": {
                        "version": "1.2.3",
                        "resolved": "https://registry.npmjs.org/example/-/example-1.2.3.tgz",
                        "integrity": integrity,
                    },
                }
            }
        )
    )
    entries = deps.npm_tarball_entries(lock)
    assert len(entries) == 1
    assert entries[0]["version"] == "1.2.3"
    assert deps.verify_sri(raw, integrity) == "sha512"


def test_npm_lock_parser_rejects_non_registry_origin(tmp_path):
    lock = tmp_path / "package-lock.json"
    lock.write_text(
        json.dumps(
            {
                "packages": {
                    "node_modules/example": {
                        "version": "1",
                        "resolved": "https://example.invalid/package.tgz",
                        "integrity": "sha512-AAAA",
                    }
                }
            }
        )
    )
    with pytest.raises(SystemExit, match="non-registry"):
        deps.npm_tarball_entries(lock)


def test_dependency_capsule_verifier_detects_tamper(tmp_path):
    payload = tmp_path / "capsule" / "python" / "wheels" / "example.whl"
    payload.parent.mkdir(parents=True)
    payload.write_bytes(b"original")
    (tmp_path / "capsule" / "manifest.json").write_text(
        json.dumps(
            {
                "schema": deps.SCHEMA,
                "payloads": [
                    {
                        "path": "python/wheels/example.whl",
                        "bytes": len(b"original"),
                        "sha256": hashlib.sha256(b"original").hexdigest(),
                    }
                ],
            }
        )
    )
    deps.verify(tmp_path / "capsule")
    payload.write_bytes(b"tampered")
    with pytest.raises(SystemExit, match="size mismatch|SHA-256 mismatch"):
        deps.verify(tmp_path / "capsule")


def test_software_heritage_success_requires_snapshot_swhid():
    value = {
        "origin_url": swh.DEFAULT_ORIGIN,
        "save_request_status": "accepted",
        "save_task_status": "succeeded",
        "snapshot_swhid": "swh:1:snp:" + "a" * 40,
    }
    swh.validate(value, swh.DEFAULT_ORIGIN)
    value["snapshot_swhid"] = None
    with pytest.raises(SystemExit, match="snapshot SWHID"):
        swh.validate(value, swh.DEFAULT_ORIGIN)


def test_portability_workflow_never_runs_external_save_on_pull_request():
    workflow = (ROOT / ".github/workflows/preservation-portability.yml").read_text()
    assert "github.event_name != 'pull_request'" in workflow
    assert "--no-index" in workflow
    assert "npm ci --offline" in workflow
    assert "archive.softwareheritage.org" in (
        ROOT / "scripts/request_software_heritage_save.py"
    ).read_text()
