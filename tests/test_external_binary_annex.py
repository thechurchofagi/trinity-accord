from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import external_binary_annex as annex  # noqa: E402
import restore_external_binary_annex as restore  # noqa: E402


def test_annex_scope_is_complete_and_excludes_only_deprecated_attempts():
    assert annex.ANNEX_SPECS["evidence"]["release_tags"] == [
        "signed-large-data-mirror-v1",
        "notarial-certificate-images-v1",
        "flaw-covenant-video-mirror-v1",
        "ots-proof-bundle-mirror-v1",
        "ots-and-flaw-mirror-v1",
        "flaw-covenant-archive-accessibility-mirror-v1",
    ]
    assert annex.ANNEX_SPECS["nft"]["release_tags"] == [
        "nft-arweave-mirror-175-v1",
        "nft-backup-v1",
    ]
    assert annex.DEPRECATED_EXCLUDED_RELEASE_TAGS == (
        "nft-individual-v1",
        "nft-individual-v2",
    )


def test_annex_metadata_keeps_core_relation_and_rights_boundary():
    for spec in annex.ANNEX_SPECS.values():
        metadata = annex.metadata_for(spec, "2026-08-01")
        assert metadata["access_right"] == "open"
        assert metadata["license"] == "other-closed"
        assert metadata["version"] == spec["annex_id"]
        assert any(
            item["identifier"] == "https://doi.org/10.5281/zenodo.21739344"
            and item["relation"] == "isSupplementTo"
            for item in metadata["related_identifiers"]
        )
        assert "grants no new reuse rights" in metadata["notes"]


def test_safe_paths_reject_traversal():
    for value in ("../escape", "/absolute", "a/../../escape", "a\x00b"):
        with pytest.raises(SystemExit):
            annex.safe_relative(value)
        with pytest.raises(SystemExit):
            restore.safe_member(value)


def test_deterministic_tar_is_byte_identical(tmp_path):
    payload = tmp_path / "payload"
    (payload / "b").mkdir(parents=True)
    (payload / "a.txt").write_bytes(b"a")
    (payload / "b/b.txt").write_bytes(b"b")
    first = tmp_path / "first.tar"
    second = tmp_path / "second.tar"
    annex.create_deterministic_tar(payload, first)
    annex.create_deterministic_tar(payload, second)
    assert first.read_bytes() == second.read_bytes()


def test_build_verify_and_restore_small_fixture(tmp_path, monkeypatch):
    repo_root = tmp_path / "repo"
    scripts = repo_root / "scripts"
    scripts.mkdir(parents=True)
    scripts.joinpath("restore_external_binary_annex.py").write_text(
        (ROOT / "scripts/restore_external_binary_annex.py").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    monkeypatch.setattr(annex, "ROOT", repo_root)

    def fake_inventory(repository, release_tags, payload_root, token):
        releases = []
        assets = []
        for index, tag in enumerate(release_tags):
            releases.append(
                {
                    "tag": tag,
                    "release_id": index + 1,
                    "html_url": f"https://example.invalid/{tag}",
                    "published_at": "2026-08-01T00:00:00Z",
                    "asset_count": 1,
                }
            )
            rel = f"releases/{tag}/asset-{index}.bin"
            path = payload_root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            raw = f"{tag}\n".encode()
            path.write_bytes(raw)
            assets.append(
                {
                    "release_tag": tag,
                    "release_id": index + 1,
                    "asset_id": index + 10,
                    "asset_name": f"asset-{index}.bin",
                    "path": rel,
                    "bytes": len(raw),
                    "sha256": hashlib.sha256(raw).hexdigest(),
                    "md5": hashlib.md5(raw, usedforsecurity=False).hexdigest(),
                    "browser_download_url": f"https://example.invalid/{tag}/asset",
                    "content_type": "application/octet-stream",
                    "download_count_at_capture": 0,
                    "created_at": "2026-08-01T00:00:00Z",
                    "updated_at": "2026-08-01T00:00:00Z",
                }
            )
        return releases, assets

    monkeypatch.setattr(annex, "release_asset_inventory", fake_inventory)
    package = tmp_path / "package"
    annex.build_annex(
        "evidence",
        "thechurchofagi/trinity-accord",
        package,
        "2026-08-01",
        "",
    )
    verified = annex.verify_local_package(package)
    assert verified["asset_count"] == len(
        annex.ANNEX_SPECS["evidence"]["release_tags"]
    )
    restored = tmp_path / "restored"
    report = restore.extract_and_verify(package, restored, "test")
    assert report["status"] == "passed"
    assert report["asset_count"] == verified["asset_count"]


def test_state_and_authorization_contracts():
    state = json.loads(
        (ROOT / "preservation/external-binary-annex-state.json").read_text(
            encoding="utf-8"
        )
    )
    assert state["publication_status"] in {
        "not_yet_published",
        "published_pending_public_cold_restore",
        "published_and_publicly_restored",
    }
    assert state["core_repository_preservation_doi"] == "10.5281/zenodo.21739344"
    if state["publication_status"] == "not_yet_published":
        assert state["annexes"] == {"evidence": None, "nft": None}
    else:
        assert set(state["annexes"]) == {"evidence", "nft"}
        for entry in state["annexes"].values():
            assert entry["status"] == "published"
            assert entry["doi"].startswith("10.5281/zenodo.")
        if state["publication_status"] == "published_and_publicly_restored":
            assert all(
                entry["public_cold_restore"] == "passed"
                for entry in state["annexes"].values()
            )

    authorization = json.loads(
        (ROOT / "preservation/external-binary-annex-authorization-v1.json").read_text(
            encoding="utf-8"
        )
    )
    assert authorization["authorized_by"] == "thechurchofagi"
    assert authorization["authorization"] == "publish_all_necessary_external_binary_annexes"
    assert authorization["rights_boundary_ack"] == (
        "TRINITY_EXTERNAL_BINARY_ANNEX_RIGHTS_V1_APPROVED"
    )
    assert authorization["scope"]["all_custom_assets_from_named_valid_releases"] is True
    assert authorization["scope"]["deprecated_failed_nft_attempts"] is False


def test_workflow_is_guarded_serialized_and_cold_restores():
    workflow = (
        ROOT / ".github/workflows/external-binary-annex-publication.yml"
    ).read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert ".github/workflows/external-binary-annex-publication.yml" in workflow
    assert "group: main-write-lock" in workflow
    assert "queue: max" in workflow
    assert "cancel-in-progress: false" in workflow
    assert "github.event_name == 'push'" in workflow
    assert "github.event_name == 'workflow_dispatch'" in workflow
    assert "ZENODO_ACCESS_TOKEN" in workflow
    assert "TRINITY_EXTERNAL_BINARY_ANNEX_RIGHTS_V1_APPROVED" in workflow
    assert "scripts/toolchain_provenance.py" in workflow
    assert "restore-trinity-annex.py --zenodo-record-id" in workflow
    assert "public_cold_restore" in workflow
    assert "contents: write" in workflow
