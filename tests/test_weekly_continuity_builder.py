from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import build_weekly_continuity_deposit as builder  # noqa: E402
import weekly_continuity_package as package  # noqa: E402


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


def make_archive(
    archives: Path,
    *,
    archive_id: str,
    current_count: int,
    txid: str,
    previous: dict[str, Any] | None,
) -> dict[str, Any]:
    previous_count = int(previous["native_record_count"]) if previous else 0
    latest_id = f"R-{current_count:09d}"
    latest_sha = hashlib.sha256(archive_id.encode()).hexdigest()
    payload = {
        "schema": "trinityaccord.record-chain-arweave-delta.v1",
        "archive_id": archive_id,
        "archive_mode": "incremental_delta" if previous else "full_snapshot",
        "archive_cadence": "weekly",
        "coverage": {
            "previous_native_record_count": previous_count,
            "delta_record_count": current_count - previous_count,
            "current_native_record_count": current_count,
            "current_latest_record_id": latest_id,
            "current_latest_record_sha256": latest_sha,
        },
        "previous_archive": previous,
        "included_records": [],
        "continuity_bundle": {
            "schema": "trinityaccord.weekly-continuity-bundle.v1",
            "heartbeat_summary": {},
        },
    }
    directory = archives / archive_id
    payload_path = directory / "payload.json"
    write_json(payload_path, payload)
    payload_sha = package.sha256(payload_path)
    manifest = {
        "archive_id": archive_id,
        "archive_manifest_sha256": None,
        "created_at": f"2026-08-{current_count:02d}T00:00:00Z",
        "mode": "live",
        "source": {
            "native_chain": {
                "native_record_count": current_count,
                "latest_record_id": latest_id,
                "latest_record_sha256": latest_sha,
            }
        },
        "payload": {
            "bytes": payload_path.stat().st_size,
            "sha256": payload_sha,
        },
        "arweave": {
            "archive_status": "archived",
            "verified": True,
            "hash_match": True,
            "readback_sha256": payload_sha,
            "txid": txid,
        },
    }
    manifest["archive_manifest_sha256"] = package.archive_manifest_sha256(manifest)
    write_json(directory / "manifest.json", manifest)
    return {
        "archive_id": archive_id,
        "arweave_txid": txid,
        "native_record_count": current_count,
        "latest_record_id": latest_id,
        "latest_record_sha256": latest_sha,
    }


def configure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    archives = tmp_path / "record-chain" / "arweave-archives"
    deposits = tmp_path / "record-chain" / "weekly-continuity-deposits"
    monkeypatch.setattr(builder, "ROOT", tmp_path)
    monkeypatch.setattr(builder, "ARCHIVES", archives)
    monkeypatch.setattr(builder, "DEPOSITS", deposits)
    return archives, deposits


def test_builder_materializes_full_verified_chain(tmp_path, monkeypatch):
    archives, deposits = configure(tmp_path, monkeypatch)
    baseline = make_archive(
        archives,
        archive_id="archive-baseline",
        current_count=2,
        txid="A" * 43,
        previous=None,
    )
    delta = make_archive(
        archives,
        archive_id="archive-delta",
        current_count=3,
        txid="B" * 43,
        previous=baseline,
    )
    make_archive(
        archives,
        archive_id="archive-latest",
        current_count=4,
        txid="C" * 43,
        previous=delta,
    )

    latest = builder.build()

    assert latest == deposits / "archive-latest"
    assert sorted(path.name for path in deposits.iterdir()) == [
        "archive-baseline",
        "archive-delta",
        "archive-latest",
    ]
    for directory in deposits.iterdir():
        package.verify_local_package(directory)


def test_builder_refuses_latest_delta_without_verified_baseline(tmp_path, monkeypatch):
    archives, _deposits = configure(tmp_path, monkeypatch)
    missing = {
        "archive_id": "missing-baseline",
        "arweave_txid": "A" * 43,
        "native_record_count": 2,
        "latest_record_id": "R-000000002",
        "latest_record_sha256": "0" * 64,
    }
    make_archive(
        archives,
        archive_id="archive-delta",
        current_count=3,
        txid="B" * 43,
        previous=missing,
    )

    with pytest.raises(SystemExit, match="missing predecessor"):
        builder.build()
