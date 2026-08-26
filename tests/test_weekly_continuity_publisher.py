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

import publish_weekly_continuity_to_zenodo as publisher  # noqa: E402
import weekly_continuity_package as package  # noqa: E402


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")


def make_package(tmp_path: Path, archive_id: str = "archive-test") -> Path:
    deposit = tmp_path / archive_id
    deposit.mkdir()
    write_json(
        deposit / "weekly-continuity-bundle.json",
        {
            "schema": "trinityaccord.record-chain-arweave-delta.v1",
            "archive_id": archive_id,
            "archive_mode": "full_snapshot",
            "archive_cadence": "weekly",
            "continuity_bundle": {
                "schema": "trinityaccord.weekly-continuity-bundle.v1"
            },
        },
    )
    payload_sha = package.sha256(deposit / "weekly-continuity-bundle.json")
    archive_manifest = {
        "archive_id": archive_id,
        "archive_manifest_sha256": None,
        "mode": "live",
        "payload": {
            "bytes": (deposit / "weekly-continuity-bundle.json").stat().st_size,
            "sha256": payload_sha,
        },
        "arweave": {
            "archive_status": "archived",
            "verified": True,
            "hash_match": True,
            "readback_sha256": payload_sha,
            "txid": "A" * 43,
        },
    }
    archive_manifest["archive_manifest_sha256"] = package.archive_manifest_sha256(
        archive_manifest
    )
    write_json(deposit / "archive-manifest.json", archive_manifest)
    write_json(
        deposit / "zenodo-metadata.json",
        {
            "upload_type": "dataset",
            "title": package.PACKAGE_TITLE,
            "version": archive_id,
            "license": package.ZENODO_LICENSE_ID,
            "access_right": "open",
            "description": "Test Weekly Continuity package.",
            "creators": [{"name": "Test, Archive"}],
        },
    )
    (deposit / "README.txt").write_text("rights boundary\n", encoding="utf-8")
    (deposit / "checksums.sha256").write_text(
        "".join(
            f"{package.sha256(deposit / name)}  {name}\n"
            for name in package.CHECKSUM_TARGET_NAMES
        ),
        encoding="utf-8",
    )
    write_json(
        deposit / "deposit-manifest.json",
        {
            "schema": package.PACKAGE_SCHEMA,
            "archive_id": archive_id,
            "published_file_names": list(package.PUBLISHED_FILE_NAMES),
            "files": [
                {
                    "name": name,
                    "bytes": (deposit / name).stat().st_size,
                    "sha256": package.sha256(deposit / name),
                }
                for name in package.MANIFEST_HASHED_NAMES
            ],
            "rights_boundary": {
                "schema": package.RIGHTS_BOUNDARY_VERSION,
                "license_identifier": package.ZENODO_LICENSE_ID,
                "third_party_rights_are_not_transferred": True,
                "deposit_grants_no_new_reuse_rights": True,
            },
        },
    )
    return deposit


def test_archive_manifest_hash_matches_record_chain_canonical_file_contract():
    manifest = {"archive_id": "archive-test", "archive_manifest_sha256": None}
    canonical_file = (
        json.dumps(
            manifest,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    assert package.archive_manifest_sha256(manifest) == hashlib.sha256(
        canonical_file
    ).hexdigest()
    assert package.archive_manifest_sha256(manifest) != package.canonical_sha256(
        manifest
    )


def test_local_package_requires_exact_six_files_and_mixed_rights_boundary(tmp_path):
    deposit = make_package(tmp_path)
    verified = package.verify_local_package(deposit)
    assert set(verified["inventory"]) == set(package.PUBLISHED_FILE_NAMES)
    assert len(verified["package_identity_sha256"]) == 64

    (deposit / "zenodo-metadata.json").unlink()
    with pytest.raises(SystemExit, match="file set mismatch"):
        package.verify_local_package(deposit)


class DownloadClient:
    def __init__(self, blobs: dict[str, bytes]) -> None:
        self.blobs = blobs

    def request_bytes(self, url: str) -> bytes:
        return self.blobs[url]


def remote_record_for(deposit: Path) -> tuple[dict[str, Any], dict[str, bytes]]:
    files = []
    blobs: dict[str, bytes] = {}
    for name in package.PUBLISHED_FILE_NAMES:
        raw = (deposit / name).read_bytes()
        url = f"https://zenodo.example/files/{name}"
        blobs[url] = raw
        files.append(
            {
                "filename": name,
                "filesize": len(raw),
                "checksum": f"md5:{package.md5(deposit / name)}",
                "links": {"download": url},
            }
        )
    return {"files": files}, blobs


def test_remote_verification_checks_service_checksum_and_downloaded_sha256(tmp_path):
    deposit = make_package(tmp_path)
    record, blobs = remote_record_for(deposit)
    result = publisher.verify_remote_files(DownloadClient(blobs), record, deposit)
    assert set(result) == set(package.PUBLISHED_FILE_NAMES)

    first_url = next(iter(blobs))
    blobs[first_url] += b"tampered"
    with pytest.raises(SystemExit, match="downloaded size mismatch|downloaded SHA-256 mismatch"):
        publisher.verify_remote_files(DownloadClient(blobs), record, deposit)


def test_uploader_includes_zenodo_metadata_as_sixth_file(tmp_path):
    deposit = make_package(tmp_path)
    uploaded: list[str] = []

    class Client:
        def request(self, method: str, url: str, **_kwargs):
            assert method == "PUT"
            uploaded.append(url.rsplit("/", 1)[-1])
            return {}

    publisher.upload_files(
        Client(),
        {"links": {"bucket": "https://zenodo.example/bucket"}},
        deposit,
    )
    assert set(uploaded) == set(package.PUBLISHED_FILE_NAMES)
    assert len(uploaded) == 6


def test_retry_reconciles_existing_publication_without_new_publish(tmp_path, monkeypatch):
    deposit = make_package(tmp_path)
    verified = package.verify_local_package(deposit)
    existing = {
        "id": 123,
        "record_id": 456,
        "submitted": True,
        "doi": "10.5281/zenodo.456",
        "conceptdoi": "10.5281/zenodo.455",
        "metadata": {
            "title": package.PACKAGE_TITLE,
            "version": verified["archive_id"],
        },
    }

    class NoMutationClient:
        def request(self, *_args, **_kwargs):
            raise AssertionError("existing publication reconciliation must not mutate Zenodo")

    monkeypatch.setattr(publisher, "list_depositions", lambda _client: [existing])
    monkeypatch.setattr(publisher, "refresh_deposition", lambda _client, _record: existing)
    monkeypatch.setattr(
        publisher,
        "verify_remote_files",
        lambda _client, _record, _deposit: verified["inventory"],
    )
    monkeypatch.setattr(publisher, "ROOT", tmp_path)
    state = publisher.publish_or_reconcile(
        client=NoMutationClient(),
        deposit_dir=deposit,
        state={},
        api_base="https://zenodo.example/api",
    )
    assert state["latest_archive_id"] == verified["archive_id"]
    assert state["latest_doi"] == "10.5281/zenodo.456"
    assert state["concept_doi"] == "10.5281/zenodo.455"
    assert state["latest_package_identity_sha256"] == verified["package_identity_sha256"]
    assert len(state["versions"]) == 1


def test_interrupted_new_version_reuses_single_series_draft(tmp_path, monkeypatch):
    deposit = make_package(tmp_path, archive_id="archive-next")
    previous = {
        "id": 100,
        "submitted": True,
        "doi": "10.5281/zenodo.100",
        "metadata": {"title": package.PACKAGE_TITLE, "version": "archive-previous"},
    }
    inherited_draft = {
        "id": 101,
        "submitted": False,
        "metadata": {"title": package.PACKAGE_TITLE, "version": "archive-previous"},
        "links": {"bucket": "https://zenodo.example/bucket"},
        "files": [],
    }
    mutations: list[tuple[str, str]] = []

    class Client:
        def request(self, method: str, url: str, **_kwargs):
            mutations.append((method, url))
            if method == "PUT" and url.endswith("/101"):
                return inherited_draft
            if method == "PUT" and "/bucket/" in url:
                return {}
            if method == "POST" and url.endswith("/actions/publish"):
                return {
                    **inherited_draft,
                    "submitted": True,
                    "doi": "10.5281/zenodo.101",
                    "record_id": 101,
                }
            raise AssertionError((method, url))

        def delete(self, _url: str) -> None:
            raise AssertionError("empty inherited draft should have no files to delete")

    published = {
        **inherited_draft,
        "submitted": True,
        "doi": "10.5281/zenodo.101",
        "record_id": 101,
        "metadata": {"title": package.PACKAGE_TITLE, "version": "archive-next"},
    }
    monkeypatch.setattr(publisher, "list_depositions", lambda _client: [previous, inherited_draft])
    monkeypatch.setattr(
        publisher,
        "refresh_deposition",
        lambda _client, record: published if publisher.is_published(record) else inherited_draft,
    )
    monkeypatch.setattr(publisher, "clear_draft_files", lambda _client, _draft: None)
    monkeypatch.setattr(publisher, "upload_files", lambda _client, _draft, _deposit: None)
    monkeypatch.setattr(publisher, "verify_remote_files", lambda *_args: {})
    monkeypatch.setattr(publisher, "ROOT", tmp_path)

    state = publisher.publish_or_reconcile(
        client=Client(),
        deposit_dir=deposit,
        state={},
        api_base="https://zenodo.example/api",
    )

    assert state["latest_doi"] == "10.5281/zenodo.101"
    assert not any(url.endswith("/actions/newversion") for _method, url in mutations)
    assert not any(url == "/deposit/depositions" for _method, url in mutations)
