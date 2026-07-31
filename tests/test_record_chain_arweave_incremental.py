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


def test_first_payload_is_full_snapshot(tmp_path, monkeypatch):
    module = _load_module()
    archives = tmp_path / "record-chain" / "arweave-archives"
    archives.mkdir(parents=True)
    monkeypatch.setattr(module.builder, "ROOT", tmp_path)
    monkeypatch.setattr(module.builder, "ARCHIVES", archives)

    manifest = _manifest(tmp_path, 3, "archive-current")
    archive_dir = archives / "archive-current"
    archive_dir.mkdir()
    payload_path = module.build_incremental_payload_json(manifest, archive_dir)
    payload = json.loads(payload_path.read_text())

    assert payload["archive_mode"] == "full_snapshot"
    assert payload["previous_archive"] is None
    assert [item["record_id"] for item in payload["included_records"]] == [
        "R-000000001",
        "R-000000002",
        "R-000000003",
    ]
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
    previous.update({
        "mode": "live",
        "archive_manifest_sha256": "manifest-sha-previous",
        "arweave": {
            "archive_status": "archived",
            "verified": True,
            "hash_match": True,
            "txid": "A" * 43,
        },
    })
    module.builder.write_json(previous_dir / "manifest.json", previous)

    current = _manifest(tmp_path, 4, "archive-current")
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
    assert current["payload_mode"] == "incremental_delta"
    assert current["payload_delta"]["first_record_id"] == "R-000000003"


def test_empty_or_backwards_delta_is_refused(tmp_path, monkeypatch):
    module = _load_module()
    archives = tmp_path / "record-chain" / "arweave-archives"
    archives.mkdir(parents=True)
    monkeypatch.setattr(module.builder, "ROOT", tmp_path)
    monkeypatch.setattr(module.builder, "ARCHIVES", archives)

    previous_dir = archives / "archive-previous"
    previous_dir.mkdir()
    previous = _manifest(tmp_path, 3, "archive-previous")
    previous.update({
        "mode": "live",
        "archive_manifest_sha256": "manifest-sha-previous",
        "arweave": {
            "archive_status": "archived",
            "verified": True,
            "hash_match": True,
            "txid": "B" * 43,
        },
    })
    module.builder.write_json(previous_dir / "manifest.json", previous)

    current = _manifest(tmp_path, 3, "archive-current")
    current_dir = archives / "archive-current"
    current_dir.mkdir()

    try:
        module.build_incremental_payload_json(current, current_dir)
    except SystemExit as exc:
        assert "not behind" in str(exc)
    else:
        raise AssertionError("expected an empty/backwards delta to be refused")
