#!/usr/bin/env python3
"""Regression tests for public Zenodo record self-proof normalization."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import reconcile_published_zenodo_capsule_v5 as v5  # noqa: E402


def fake_item(name: str, size: int = 10) -> dict[str, object]:
    return {
        "key": name,
        "size": size,
        "checksum": "md5:" + "a" * 32,
        "links": {
            "content": f"https://zenodo.org/api/records/1/files/{name}/content",
            "self": f"https://zenodo.org/api/records/1/files/{name}",
        },
    }


def test_modern_public_file_entries() -> None:
    entries = {name: fake_item(name) for name in v5.PUBLISHED_FILE_NAMES}
    record = {"files": {"enabled": True, "entries": entries}}
    observed = v5.public_file_items(record)
    assert tuple(observed) == v5.PUBLISHED_FILE_NAMES


def test_legacy_public_file_list() -> None:
    files = [
        {
            "filename": name,
            "filesize": 12,
            "checksum": "md5:" + "b" * 32,
            "links": {"download": f"https://zenodo.org/records/1/files/{name}"},
        }
        for name in v5.PUBLISHED_FILE_NAMES
    ]
    observed = v5.public_file_items({"files": files})
    assert tuple(observed) == v5.PUBLISHED_FILE_NAMES


def test_public_pid_normalization() -> None:
    record = {
        "id": v5.EXPECTED_RECORD_ID,
        "metadata": {
            "title": v5.PACKAGE_TITLE,
            "version": v5.EXPECTED_CAPSULE_ID,
        },
        "pids": {"doi": {"identifier": "10.5281/zenodo.21739344"}},
        "parent": {
            "id": "21739343",
            "pids": {"doi": {"identifier": "10.5281/zenodo.21739343"}},
        },
    }
    package = {"capsule_id": v5.EXPECTED_CAPSULE_ID}
    normalized = v5.normalized_published_record(
        record, package, v5.EXPECTED_RECORD_ID
    )
    assert normalized["submitted"] is True
    assert normalized["state"] == "done"
    assert normalized["doi"] == "10.5281/zenodo.21739344"
    assert normalized["conceptdoi"] == "10.5281/zenodo.21739343"
    assert normalized["conceptrecid"] == 21739343
    assert normalized["links"]["doi"] == "https://doi.org/10.5281/zenodo.21739344"


def test_download_candidates_include_public_fallback() -> None:
    name = "restore-trinity-accord.py"
    item = {
        "id": "file-id",
        "links": {
            "content": "https://zenodo.org/api/records/1/files/file-id/content"
        },
    }
    values = v5.download_candidates(
        v5.EXPECTED_RECORD_ID,
        name,
        item,
        "https://zenodo.org",
        "https://zenodo.org/api",
    )
    assert values[0].endswith("/content")
    assert any(
        value
        == f"https://zenodo.org/records/{v5.EXPECTED_RECORD_ID}/files/{name}?download=1"
        for value in values
    )
    assert len(values) == len(set(values))


def test_wrong_file_set_is_rejected() -> None:
    entries = {name: fake_item(name) for name in v5.PUBLISHED_FILE_NAMES[:-1]}
    try:
        v5.public_file_items({"files": {"entries": entries}})
    except SystemExit as exc:
        assert "file set mismatch" in str(exc)
    else:
        raise AssertionError("incomplete public file set was accepted")


def main() -> int:
    test_modern_public_file_entries()
    test_legacy_public_file_list()
    test_public_pid_normalization()
    test_download_candidates_include_public_fallback()
    test_wrong_file_set_is_rejected()
    print("RECONCILE_PUBLISHED_ZENODO_CAPSULE_V5_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
