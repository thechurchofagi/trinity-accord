from __future__ import annotations

import hashlib
import io
import json
import subprocess
import sys
import tarfile
import stat
from pathlib import Path
from typing import Any

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import build_preservation_capsule as builder  # noqa: E402
import preservation_capsule as package  # noqa: E402
import publish_preservation_capsule_to_zenodo as publisher  # noqa: E402
import restore_preservation_capsule as recovery  # noqa: E402


def write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def make_repository(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "source-repository"
    repo.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Capsule Test"], cwd=repo, check=True)
    subprocess.run(
        ["git", "config", "user.email", "capsule@example.invalid"], cwd=repo, check=True
    )
    for name in builder.REQUIRED_CHECKPOINTS:
        write(repo / name, (f"checkpoint:{name}\n").encode())
    write(
        repo / "scripts/restore_preservation_capsule.py",
        (ROOT / "scripts/restore_preservation_capsule.py").read_bytes(),
    )
    write(
        repo / "record-chain/records/R-000000001.json",
        json.dumps(
            {
                "record_id": "R-000000001",
                "record_index": 1,
                "record_sha256": "a" * 64,
            },
            sort_keys=True,
        ).encode()
        + b"\n",
    )
    write(
        repo / "RELEASE-LARGE-DATA-MANIFEST.json",
        b'{"assets":[{"size_bytes":123}]}\n',
    )
    write(
        repo / "nft-text-descriptions/nft-cars-manifest.json",
        b'{"files":[{"size":456}]}\n',
    )
    write(repo / "README.md", b"tiny preservation fixture\n")
    write(
        repo / "tests/fixtures/redteam/gateway_payloads/contains_secret_like_token.json",
        (
            ROOT
            / "tests/fixtures/redteam/gateway_payloads/contains_secret_like_token.json"
        ).read_bytes(),
    )
    write(repo / "bin/preservation-smoke", b"#!/bin/sh\nexit 0\n")
    (repo / "bin/preservation-smoke").chmod(0o755)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "fixture"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "tag", "v1-fixture"], cwd=repo, check=True)
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()
    return repo, commit


def build_fixture(tmp_path: Path) -> tuple[Path, str]:
    repo, commit = make_repository(tmp_path)
    capsule = tmp_path / "capsule"
    builder.build(repo, capsule, commit)
    return capsule, commit


def test_capsule_build_and_github_zero_restore(tmp_path, monkeypatch):
    capsule, commit = build_fixture(tmp_path)
    verified = package.verify_local_package(capsule)
    assert verified["git_commit_sha"] == commit
    assert set(verified["inventory"]) == set(package.PUBLISHED_FILE_NAMES)
    assert verified["manifest"]["scope"]["github_required_for_repository_recovery"] is False
    assert verified["manifest"]["scope"]["external_large_binary_annex_embedded"] is False

    output = tmp_path / "restored"
    bootstrap = tmp_path / "non-git-bootstrap"
    bootstrap.mkdir()
    monkeypatch.chdir(bootstrap)
    report = recovery.restore(capsule, output, "test:capsule")
    assert report["repository_recovery_status"] == "full_current_git_tracked_tree"
    assert report["source_git_commit_sha"] == commit
    assert report["recovery_git_commit_sha"] != commit
    assert report["github_required"] is False
    assert report["production_parent_history_embedded"] is False
    assert report["production_tag_identity_count"] == 1
    assert report["git_tag_count_verified"] == 0
    assert (output / "repository/README.md").read_text() == "tiny preservation fixture\n"
    assert stat.S_IMODE((output / "repository/bin/preservation-smoke").stat().st_mode) & 0o111
    assert subprocess.run(
        ["git", "-C", str(output / "repository"), "tag", "--list"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines() == []
    assert not subprocess.run(
        ["git", "-C", str(output / "repository"), "status", "--porcelain"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def test_capsule_tamper_fails_before_restore(tmp_path):
    capsule, _commit = build_fixture(tmp_path)
    with (capsule / "trinity-accord-source.tar.gz").open("ab") as handle:
        handle.write(b"tamper")
    with pytest.raises(SystemExit, match="checksum mismatch"):
        recovery.restore(capsule, tmp_path / "refused", "test:tampered")


def test_synthetic_secret_fixture_allowlist_is_hash_pinned(tmp_path):
    repo, _commit = make_repository(tmp_path)
    fixture = repo / "tests/fixtures/redteam/gateway_payloads/contains_secret_like_token.json"
    fixture.write_bytes(fixture.read_bytes() + b"\n")
    subprocess.run(["git", "add", str(fixture)], cwd=repo, check=True)
    subprocess.run(
        ["git", "commit", "-m", "tamper fixture"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    with pytest.raises(SystemExit, match="synthetic secret fixture hash mismatch"):
        builder.build(repo, tmp_path / "refused-capsule", "HEAD")


def test_source_archive_path_traversal_is_rejected():
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as archive:
        info = tarfile.TarInfo("trinity-accord/../../escape")
        info.size = 1
        archive.addfile(info, io.BytesIO(b"x"))
    raw.seek(0)
    with tarfile.open(fileobj=raw, mode="r:") as archive:
        with pytest.raises(SystemExit, match="unsafe source archive member"):
            recovery.validate_tar_members(archive)


class DownloadClient:
    def __init__(self, blobs: dict[str, bytes]) -> None:
        self.blobs = blobs

    def request_bytes(self, url: str) -> bytes:
        return self.blobs[url]


def test_preservation_publisher_verifies_every_remote_byte(tmp_path):
    capsule, _commit = build_fixture(tmp_path)
    files: list[dict[str, Any]] = []
    blobs: dict[str, bytes] = {}
    for name in package.PUBLISHED_FILE_NAMES:
        raw = (capsule / name).read_bytes()
        url = f"https://zenodo.example/{name}"
        blobs[url] = raw
        files.append(
            {
                "filename": name,
                "filesize": len(raw),
                "checksum": "md5:"
                + hashlib.md5(raw, usedforsecurity=False).hexdigest(),
                "links": {"download": url},
            }
        )
    verified = publisher.verify_remote_files(DownloadClient(blobs), {"files": files}, capsule)
    assert set(verified) == set(package.PUBLISHED_FILE_NAMES)
    blobs[next(iter(blobs))] += b"tamper"
    with pytest.raises(SystemExit, match="downloaded size mismatch|downloaded SHA-256 mismatch"):
        publisher.verify_remote_files(DownloadClient(blobs), {"files": files}, capsule)


def test_preservation_retry_reconciles_existing_publication(tmp_path, monkeypatch):
    capsule, _commit = build_fixture(tmp_path)
    verified = package.verify_local_package(capsule)
    existing = {
        "id": 123,
        "record_id": 456,
        "submitted": True,
        "doi": "10.5281/zenodo.456",
        "conceptdoi": "10.5281/zenodo.455",
        "metadata": {
            "title": package.PACKAGE_TITLE,
            "version": verified["capsule_id"],
        },
    }

    class NoMutationClient:
        def request(self, *_args, **_kwargs):
            raise AssertionError("existing DOI reconciliation must not mutate Zenodo")

    monkeypatch.setattr(publisher, "list_depositions", lambda _client: [existing])
    monkeypatch.setattr(publisher, "refresh", lambda _client, _record: existing)
    monkeypatch.setattr(
        publisher,
        "verify_remote_files",
        lambda _client, _record, _capsule: verified["inventory"],
    )
    state = publisher.publish_or_reconcile(
        NoMutationClient(), capsule, {}, "https://zenodo.example/api"
    )
    assert state["latest_doi"] == "10.5281/zenodo.456"
    assert state["concept_doi"] == "10.5281/zenodo.455"
    assert state["latest_git_commit_sha"] == verified["git_commit_sha"]
    assert state["github_required_for_repository_recovery"] is False


def test_capsule_workflow_is_manual_for_publication_and_quarterly_for_validation():
    workflow = (ROOT / ".github/workflows/repository-preservation-capsule.yml").read_text()
    assert 'cron: "17 9 1 1,4,7,10 *"' in workflow
    assert "publish_to_zenodo" in workflow
    assert "github.event_name == 'workflow_dispatch'" in workflow
    assert "PUBLISH_TRINITY_REPOSITORY_CAPSULE_V1" in workflow
    assert "TRINITY_PRESERVATION_CAPSULE_RIGHTS_V1_APPROVED" in workflow
    assert "ZENODO_ACCESS_TOKEN" in workflow
    assert "Simulate GitHub-zero one-command restore" in workflow
    assert "Prove public DOI-only recovery" in workflow
    assert "permissions:\n      contents: read" in workflow
    assert "permissions:\n      contents: write" in workflow
    assert package.ZENODO_LICENSE_ID == "other-closed"


def test_published_state_records_verified_repository_doi_and_prior_snapshot():
    state = json.loads((ROOT / "preservation/zenodo-state.json").read_text())
    assert state["publication_status"] == "published"
    assert state["latest_record_id"] == 21739344
    assert state["latest_doi"] == "10.5281/zenodo.21739344"
    assert state["concept_doi"] == "10.5281/zenodo.21739343"
    assert state["latest_git_commit_sha"] == "484bdd7a85694ad53fe7e6e9dcea94d0dee5617e"
    assert state["latest_git_tree_oid"] == "47aa1f8b77f6f0c77237906b53929c08b665060f"
    assert state["earlier_software_snapshot"]["doi"] == "10.5281/zenodo.21675727"
    assert state["github_required_for_repository_recovery"] is False
    assert state["external_large_binary_annex_embedded"] is False


def test_recovery_index_routes_to_capsule_without_claiming_external_annex():
    index = json.loads((ROOT / "api/recovery-index.json").read_text())
    entrypoints = index["recovery_entrypoints"]
    assert entrypoints["repository_preservation_state"] == "preservation/zenodo-state.json"
    assert entrypoints["repository_preservation_restore_cli"].endswith(
        "restore_preservation_capsule.py"
    )
    assert "exact_eight_file_capsule" in index["mirror_classes"][
        "repository_preservation_zenodo"
    ]
    assert "large binary" in index["limitations"][-1]
