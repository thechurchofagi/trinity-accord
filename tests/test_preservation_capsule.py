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
    assert report["repository_recovery_status"] == "full_exact_publication_baseline"
    assert report["source_git_commit_sha"] == commit
    assert report["recovery_git_commit_sha"] != commit
    assert report["github_required"] is False
    assert report["production_parent_history_embedded"] is False
    assert report["production_tag_identity_count"] == 0
    assert verified["manifest"]["scope"]["production_tag_identities_recorded"] is False
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
    catalog = json.loads((ROOT / "preservation/recovery-catalog.json").read_text())
    core = catalog["core_repository"]

    assert state["publication_status"] == "published"
    assert state["latest_record_id"] == core["current_verified_record_id"]
    assert state["latest_doi"] == core["current_verified_version_doi"]
    assert state["latest_git_commit_sha"] == core["current_verified_source_git_commit_sha"]
    assert state["latest_package_identity_sha256"] == core["current_verified_package_identity_sha256"]
    assert state["concept_doi"] == "10.5281/zenodo.21739343"

    versions = {entry["doi"]: entry for entry in state["versions"]}
    initial = versions["10.5281/zenodo.21739344"]
    assert initial["record_id"] == 21739344
    assert initial["git_commit_sha"] == "484bdd7a85694ad53fe7e6e9dcea94d0dee5617e"
    assert initial["git_tree_oid"] == "47aa1f8b77f6f0c77237906b53929c08b665060f"

    assert state["github_required_for_repository_recovery"] is False
    assert state["external_large_binary_annex_embedded"] is False


def test_recovery_index_routes_to_complete_repository_and_annex_recovery():
    index = json.loads((ROOT / "api/recovery-index.json").read_text())
    entrypoints = index["recovery_entrypoints"]
    assert entrypoints["repository_preservation_state"] == (
        "preservation/repository-preservation-state-v2.json"
    )
    assert entrypoints["repository_preservation_legacy_state"] == (
        "preservation/zenodo-state.json"
    )
    assert entrypoints["repository_preservation_restore_cli"].endswith(
        "restore_preservation_capsule.py"
    )
    assert entrypoints["external_binary_annex_state"] == (
        "preservation/external-binary-annex-state.json"
    )
    assert entrypoints["external_binary_annex_restore_cli"] == (
        "scripts/restore_external_binary_annex.py"
    )
    repository_mirror = index["mirror_classes"][
        "repository_preservation_zenodo"
    ]
    assert "publication-baseline" in repository_mirror
    assert "stable recovery catalog" in repository_mirror
    assert "public DOI-only restore" in repository_mirror
    trusted = index["latest_trusted_release"]
    assert trusted["status"] == "published_and_publicly_restored"
    annexes = trusted["external_binary_annexes"]
    assert annexes["evidence"]["doi"] == "10.5281/zenodo.21753937"
    assert annexes["evidence"]["public_cold_restore"] == "passed"
    assert annexes["nft"]["doi"] == "10.5281/zenodo.21754229"
    assert annexes["nft"]["public_cold_restore"] == "passed"
    assert not any("remain pending" in item.lower() for item in index["limitations"])
    assert any(
        "preserve the exact Git-tracked publication baseline named by the core manifest"
        in item
        for item in index["limitations"]
    )


def test_capsule_build_is_byte_reproducible(tmp_path):
    repo, commit = make_repository(tmp_path)
    capsule_a = tmp_path / "capsule-a"
    capsule_b = tmp_path / "capsule-b"
    builder.build(repo, capsule_a, commit)
    builder.build(repo, capsule_b, commit)

    assert package.verify_local_package(capsule_a)["package_identity_sha256"] == (
        package.verify_local_package(capsule_b)["package_identity_sha256"]
    )
    assert sorted(path.name for path in capsule_a.iterdir()) == sorted(
        path.name for path in capsule_b.iterdir()
    )
    for path_a in capsule_a.iterdir():
        path_b = capsule_b / path_a.name
        assert path_a.read_bytes() == path_b.read_bytes(), path_a.name


def test_capsule_identity_is_independent_of_later_refs(tmp_path):
    repo, frozen_commit = make_repository(tmp_path)
    capsule_before = tmp_path / "capsule-before"
    builder.build(repo, capsule_before, frozen_commit)

    subprocess.run(["git", "switch", "-c", "later-unrelated-branch"], cwd=repo, check=True)
    write(repo / "later-unrelated.txt", b"must not affect frozen capsule\n")
    subprocess.run(["git", "add", "later-unrelated.txt"], cwd=repo, check=True)
    subprocess.run(
        ["git", "commit", "-m", "later unrelated ref state"],
        cwd=repo,
        check=True,
        capture_output=True,
    )
    subprocess.run(["git", "tag", "later-unrelated-tag"], cwd=repo, check=True)
    subprocess.run(["git", "tag", "later-tag-on-frozen-commit", frozen_commit], cwd=repo, check=True)

    capsule_after = tmp_path / "capsule-after"
    builder.build(repo, capsule_after, frozen_commit)

    verified_before = package.verify_local_package(capsule_before)
    verified_after = package.verify_local_package(capsule_after)
    assert verified_before["package_identity_sha256"] == verified_after["package_identity_sha256"]
    assert verified_before["manifest"]["git"]["production_tag_identity_count"] == 0
    assert verified_after["manifest"]["git"]["production_tag_identity_count"] == 0
    for path_before in capsule_before.iterdir():
        path_after = capsule_after / path_before.name
        assert path_before.read_bytes() == path_after.read_bytes(), path_before.name


def test_capsule_identity_is_independent_of_clone_depth(tmp_path):
    repo, frozen_commit = make_repository(tmp_path)
    capsule_full = tmp_path / "capsule-full"
    builder.build(repo, capsule_full, frozen_commit)

    shallow = tmp_path / "shallow-repository"
    subprocess.run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "--no-tags",
            "--branch",
            "main",
            repo.resolve().as_uri(),
            str(shallow),
        ],
        check=True,
        capture_output=True,
    )
    assert subprocess.run(
        ["git", "rev-parse", "--is-shallow-repository"],
        cwd=shallow,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip() == "true"
    assert subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=shallow,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip() == frozen_commit

    capsule_shallow = tmp_path / "capsule-shallow"
    builder.build(shallow, capsule_shallow, frozen_commit)

    verified_full = package.verify_local_package(capsule_full)
    verified_shallow = package.verify_local_package(capsule_shallow)
    assert verified_full["package_identity_sha256"] == verified_shallow["package_identity_sha256"]
    assert sorted(path.name for path in capsule_full.iterdir()) == sorted(
        path.name for path in capsule_shallow.iterdir()
    )
    for path_full in capsule_full.iterdir():
        path_shallow = capsule_shallow / path_full.name
        assert path_full.read_bytes() == path_shallow.read_bytes(), path_full.name
