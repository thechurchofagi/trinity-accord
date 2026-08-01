from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path


def _load_module():
    scripts = Path(__file__).resolve().parents[1] / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    return importlib.import_module("record_chain_arweave_incremental")


def _record(root: Path, index: int) -> dict:
    record_id = f"R-{index:09d}"
    path = root / "record-chain" / "records" / f"{record_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    content = {"record_id": record_id, "value": f"record-{index}"}
    raw = (json.dumps(content, sort_keys=True, separators=(",", ":")) + "\n").encode()
    path.write_bytes(raw)
    module = _load_module()
    return {
        "record_id": record_id,
        "path": str(path.relative_to(root)),
        "record_sha256": f"sha-{index}",
        "raw_file_sha256": module.builder.sha256_bytes(raw),
        "bytes": len(raw),
    }


def _manifest(root: Path, count: int, archive_id: str) -> dict:
    return {
        "archive_id": archive_id,
        "created_at": "2026-07-31T00:00:00Z",
        "source": {
            "source_type": "native-record-chain",
            "native_chain": {
                "latest_record_id": f"R-{count:09d}",
                "latest_record_sha256": f"sha-{count}",
                "native_record_count": count,
            },
        },
        "included_batches": [],
        "included_records": [_record(root, index) for index in range(1, count + 1)],
    }


def _write_mature_ots(root: Path, count: int, module, monkeypatch) -> None:
    anchor_rel = f"record-chain/ots/native-anchors/native-{count}.anchor.json"
    anchored_rel = f"record-chain/ots/native-anchors/native-{count}.commitment.json"
    ots_rel = anchored_rel + ".ots"

    anchor = root / anchor_rel
    anchored = root / anchored_rel
    ots = root / ots_rel
    anchor.parent.mkdir(parents=True, exist_ok=True)
    anchor.write_text(
        json.dumps(
            {
                "schema": "trinityaccord.native-record-chain-ots-anchor.v1",
                "latest_record_id": f"R-{count:09d}",
                "latest_record_sha256": f"sha-{count}",
                "native_record_count": count,
                "strict_bitcoin_verified": True,
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    anchored.write_text(
        json.dumps(
            {
                "schema": "trinityaccord.native-record-chain-head-commitment.v1",
                "latest_record_id": f"R-{count:09d}",
                "latest_record_sha256": f"sha-{count}",
                "native_record_count": count,
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    ots.write_bytes(b"test-mature-native-ots-proof")

    latest_path = root / "api" / "record-chain-native-ots-latest.json"
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.write_text(
        json.dumps(
            {
                "schema": "trinityaccord.native-record-chain-ots-latest.v1",
                "native_record_count": count,
                "latest_record_id": f"R-{count:09d}",
                "latest_record_sha256": f"sha-{count}",
                "ots_status": "verified",
                "bitcoin_verified": True,
                "strict_bitcoin_verified": True,
                "latest_anchor_file": anchor_rel,
                "latest_anchored_file": anchored_rel,
                "latest_ots_file": ots_rel,
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "OTS_LATEST", latest_path)


def _write_verified_weekly_archive(module, directory: Path, manifest: dict) -> None:
    module.builder.write_json(directory / "manifest.json", manifest)
    module.builder.write_json(
        directory / "payload.json",
        {
            "schema": "trinityaccord.record-chain-arweave-delta.v1",
            "archive_cadence": "weekly",
            "continuity_bundle": {
                "schema": "trinityaccord.weekly-continuity-bundle.v1"
            },
        },
    )


def test_first_payload_is_full_snapshot(tmp_path, monkeypatch):
    module = _load_module()
    archives = tmp_path / "record-chain" / "arweave-archives"
    archives.mkdir(parents=True)
    monkeypatch.setattr(module.builder, "ROOT", tmp_path)
    monkeypatch.setattr(module.builder, "ARCHIVES", archives)

    manifest = _manifest(tmp_path, 3, "archive-current")
    _write_mature_ots(tmp_path, 3, module, monkeypatch)
    archive_dir = archives / "archive-current"
    archive_dir.mkdir()
    payload_path = module.build_incremental_payload_json(manifest, archive_dir)
    payload = json.loads(payload_path.read_text())

    assert payload["archive_mode"] == "full_snapshot"
    assert payload["archive_cadence"] == "weekly"
    assert payload["previous_archive"] is None
    assert [item["record_id"] for item in payload["included_records"]] == [
        "R-000000001",
        "R-000000002",
        "R-000000003",
    ]
    assert payload["continuity_bundle"]["latest_native_ots"]["covers_current_chain_head"] is True
    assert len(payload["continuity_bundle"]["latest_native_ots"]["artifacts"]) == 3
    assert manifest["payload_delta"]["delta_record_count"] == 3


def test_later_payload_contains_only_new_records_and_links_previous_tx(tmp_path, monkeypatch):
    module = _load_module()
    archives = tmp_path / "record-chain" / "arweave-archives"
    archives.mkdir(parents=True)
    monkeypatch.setattr(module.builder, "ROOT", tmp_path)
    monkeypatch.setattr(module.builder, "ARCHIVES", archives)

    previous_dir = archives / "archive-previous"
    previous_dir.mkdir()
    previous = _manifest(tmp_path, 2, "archive-previous")
    previous.update(
        {
            "mode": "live",
            "archive_manifest_sha256": "manifest-sha-previous",
            "arweave": {
                "archive_status": "archived",
                "verified": True,
                "hash_match": True,
                "txid": "A" * 43,
            },
        }
    )
    _write_verified_weekly_archive(module, previous_dir, previous)

    current = _manifest(tmp_path, 4, "archive-current")
    _write_mature_ots(tmp_path, 4, module, monkeypatch)
    current_dir = archives / "archive-current"
    current_dir.mkdir()
    payload_path = module.build_incremental_payload_json(current, current_dir)
    payload = json.loads(payload_path.read_text())

    assert payload["archive_mode"] == "incremental_delta"
    assert payload["previous_archive"]["arweave_txid"] == "A" * 43
    assert payload["previous_archive"]["native_record_count"] == 2
    assert [item["record_id"] for item in payload["included_records"]] == [
        "R-000000003",
        "R-000000004",
    ]
    assert payload["coverage"]["delta_record_count"] == 2
    assert payload["continuity_bundle"]["single_paid_payload_covers_records_heartbeats_and_ots"] is True
    assert current["payload_mode"] == "incremental_delta"
    assert current["payload_delta"]["first_record_id"] == "R-000000003"


def test_ots_must_cover_current_chain_head(tmp_path, monkeypatch):
    module = _load_module()
    archives = tmp_path / "record-chain" / "arweave-archives"
    archives.mkdir(parents=True)
    monkeypatch.setattr(module.builder, "ROOT", tmp_path)
    monkeypatch.setattr(module.builder, "ARCHIVES", archives)

    manifest = _manifest(tmp_path, 3, "archive-current")
    _write_mature_ots(tmp_path, 2, module, monkeypatch)
    archive_dir = archives / "archive-current"
    archive_dir.mkdir()

    try:
        module.build_incremental_payload_json(manifest, archive_dir)
    except SystemExit as exc:
        assert "does not cover the current chain head" in str(exc)
    else:
        raise AssertionError("expected mismatched OTS coverage to be refused")


def test_empty_or_backwards_delta_is_refused(tmp_path, monkeypatch):
    module = _load_module()
    archives = tmp_path / "record-chain" / "arweave-archives"
    archives.mkdir(parents=True)
    monkeypatch.setattr(module.builder, "ROOT", tmp_path)
    monkeypatch.setattr(module.builder, "ARCHIVES", archives)

    previous_dir = archives / "archive-previous"
    previous_dir.mkdir()
    previous = _manifest(tmp_path, 3, "archive-previous")
    previous.update(
        {
            "mode": "live",
            "archive_manifest_sha256": "manifest-sha-previous",
            "arweave": {
                "archive_status": "archived",
                "verified": True,
                "hash_match": True,
                "txid": "B" * 43,
            },
        }
    )
    _write_verified_weekly_archive(module, previous_dir, previous)

    current = _manifest(tmp_path, 3, "archive-current")
    current_dir = archives / "archive-current"
    current_dir.mkdir()

    try:
        module.build_incremental_payload_json(current, current_dir)
    except SystemExit as exc:
        assert "not behind" in str(exc)
    else:
        raise AssertionError("expected an empty/backwards delta to be refused")


def test_legacy_daily_archive_does_not_prevent_first_weekly_full_snapshot(
    tmp_path, monkeypatch
):
    module = _load_module()
    archives = tmp_path / "record-chain" / "arweave-archives"
    archives.mkdir(parents=True)
    monkeypatch.setattr(module.builder, "ROOT", tmp_path)
    monkeypatch.setattr(module.builder, "ARCHIVES", archives)

    legacy_dir = archives / "legacy-daily-archive"
    legacy_dir.mkdir()
    legacy = _manifest(tmp_path, 2, "legacy-daily-archive")
    legacy.update(
        {
            "mode": "live",
            "archive_manifest_sha256": "legacy-manifest-sha",
            "arweave": {
                "archive_status": "archived",
                "verified": True,
                "hash_match": True,
                "txid": "L" * 43,
            },
        }
    )
    module.builder.write_json(legacy_dir / "manifest.json", legacy)
    module.builder.write_json(
        legacy_dir / "payload.json",
        {"schema": "trinityaccord.record-chain-arweave-archive.v1"},
    )

    current = _manifest(tmp_path, 4, "first-weekly")
    _write_mature_ots(tmp_path, 4, module, monkeypatch)
    current_dir = archives / "first-weekly"
    current_dir.mkdir()
    payload = json.loads(
        module.build_incremental_payload_json(current, current_dir).read_text()
    )

    assert payload["archive_mode"] == "full_snapshot"
    assert payload["previous_archive"] is None
    assert [item["record_id"] for item in payload["included_records"]] == [
        "R-000000001",
        "R-000000002",
        "R-000000003",
        "R-000000004",
    ]
