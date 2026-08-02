from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import external_annex_publication_precheck as publication_precheck  # noqa: E402
import external_binary_annex as legacy  # noqa: E402
import external_binary_annex_v2 as v2  # noqa: E402
import external_binary_annex_v3 as v3  # noqa: E402
import publish_external_binary_annexes_to_zenodo_v2 as publisher_v2  # noqa: E402
import restore_external_binary_annex as restore  # noqa: E402


OLD_WRITE_WORKFLOWS = {
    "repository-preservation-authorized-publish-v1.yml",
    "repository-preservation-publish-v3.yml",
    "repository-preservation-publish-v4.yml",
    "repository-preservation-reconcile-first-doi-v1.yml",
    "repository-preservation-reconcile-public-v5.yml",
    "repository-preservation-retry-first-doi-v1.yml",
    "repository-preservation-retry-first-doi-v2.yml",
}


def _asset(index: int) -> dict[str, object]:
    return {
        "id": index + 1,
        "name": f"asset-{index:04d}.bin",
        "size": index,
        "browser_download_url": f"https://example.invalid/{index}",
    }


def test_release_assets_are_explicitly_paginated_past_100():
    calls: list[int] = []
    all_assets = [_asset(index) for index in range(205)]

    def fetch_json(url: str, token: str):
        assert token == "token"
        query = parse_qs(urlparse(url).query)
        page = int(query["page"][0])
        per_page = int(query["per_page"][0])
        calls.append(page)
        start = (page - 1) * per_page
        return all_assets[start : start + per_page]

    observed = v2.list_release_assets(
        "thechurchofagi/trinity-accord",
        123,
        "token",
        fetch_json=fetch_json,
    )
    assert len(observed) == 205
    assert calls == [1, 2, 3]


def test_release_asset_pagination_rejects_duplicates():
    duplicate = _asset(0)

    def fetch_json(url: str, token: str):
        return [duplicate, dict(duplicate)]

    with pytest.raises(SystemExit, match="duplicate GitHub release asset id"):
        v2.list_release_assets(
            "thechurchofagi/trinity-accord",
            123,
            "",
            fetch_json=fetch_json,
        )


def test_v2_and_final_v3_use_distinct_immutable_versions():
    v2.V2_ANNEX_IDS = {
        "evidence": "external-evidence-annex-v2",
        "nft": "chronicle-nft-media-annex-v2",
    }
    v2.activate_v2_specs()
    assert legacy.ANNEX_SPECS["evidence"]["annex_id"] == "external-evidence-annex-v2"
    assert legacy.ANNEX_SPECS["nft"]["annex_id"] == "chronicle-nft-media-annex-v2"

    v3.activate_final_specs()
    assert legacy.ANNEX_SPECS["evidence"]["annex_id"] == "external-evidence-annex-v3"
    assert legacy.ANNEX_SPECS["nft"]["annex_id"] == "chronicle-nft-media-annex-v3"
    assert set(v3.FINAL_ANNEX_IDS.values()).isdisjoint(
        {"external-evidence-annex-v2", "chronicle-nft-media-annex-v2"}
    )


def test_original_scope_and_rights_boundaries_remain_intact():
    v3.activate_final_specs()
    assert legacy.ANNEX_SPECS["evidence"]["release_tags"] == [
        "signed-large-data-mirror-v1",
        "notarial-certificate-images-v1",
        "flaw-covenant-video-mirror-v1",
        "ots-proof-bundle-mirror-v1",
        "ots-and-flaw-mirror-v1",
        "flaw-covenant-archive-accessibility-mirror-v1",
    ]
    assert legacy.ANNEX_SPECS["nft"]["release_tags"] == [
        "nft-arweave-mirror-175-v1",
        "nft-backup-v1",
    ]
    for spec in legacy.ANNEX_SPECS.values():
        metadata = legacy.metadata_for(spec, "2026-08-02")
        assert metadata["access_right"] == "open"
        assert metadata["license"] == "other-closed"
        assert "grants no new reuse rights" in metadata["notes"]


def test_public_metadata_verification_covers_legacy_and_current_shapes():
    v3.activate_final_specs()
    expected = legacy.metadata_for(legacy.ANNEX_SPECS["evidence"], "2026-08-02")

    legacy_observed = dict(expected)
    legacy_observed["license"] = {"id": "other-closed"}
    publisher_v2.validate_public_metadata({"metadata": legacy_observed}, expected)

    current_observed = dict(expected)
    current_observed.pop("access_right")
    current_observed.pop("license")
    current_observed["rights"] = [{"id": "other-closed"}]
    current_observed["creators"] = [
        {"person_or_org": {"name": "Liu, Hongju", "type": "personal"}}
    ]
    current_observed["related_identifiers"] = [
        {**item, "relation": {"id": item["relation"].lower()}}
        for item in expected["related_identifiers"]
    ]
    publisher_v2.validate_public_metadata(
        {
            "access": {"record": "public", "files": "public", "status": "open"},
            "metadata": current_observed,
        },
        expected,
    )

    bad = json.loads(json.dumps(current_observed))
    bad["rights"] = [{"id": "cc-by-4.0"}]
    with pytest.raises(SystemExit, match="license"):
        publisher_v2.validate_public_metadata(
            {"access": {"status": "open"}, "metadata": bad}, expected
        )


def test_current_zenodo_file_entries_and_pid_shapes_are_supported():
    record = {
        "id": "123",
        "pids": {"doi": {"identifier": "10.5281/zenodo.123"}},
        "parent": {
            "id": "122",
            "pids": {"doi": {"identifier": "10.5281/zenodo.122"}},
        },
        "files": {
            "entries": {
                name: {
                    "key": name,
                    "size": 1,
                    "checksum": {"md5": "0" * 32},
                    "links": {"content": f"https://example.invalid/{name}"},
                }
                for name in legacy.PUBLISHED_FILE_NAMES
            }
        },
    }
    assert set(publisher_v2._public_file_items(record)) == set(
        legacy.PUBLISHED_FILE_NAMES
    )
    assert publisher_v2._record_doi(record) == "10.5281/zenodo.123"
    assert publisher_v2._concept_doi(record) == "10.5281/zenodo.122"
    assert publisher_v2._concept_record_id(record) == 122
    restored = restore.public_files(record)
    assert set(restored) == set(legacy.PUBLISHED_FILE_NAMES)


def test_safe_restore_paths_remain_fail_closed():
    for value in ("../escape", "/absolute", "a/../../escape", "a\x00b"):
        with pytest.raises(SystemExit):
            legacy.safe_relative(value)
        with pytest.raises(SystemExit):
            restore.safe_member(value)


def test_completion_helper_recognizes_only_final_state(tmp_path):
    state_path = tmp_path / "state.json"
    state_path.write_text(
        json.dumps({"publication_status": publication_precheck.COMPLETE}),
        encoding="utf-8",
    )
    assert publication_precheck.COMPLETE == "published_and_publicly_restored"
    assert publication_precheck.is_complete(state_path) is True
    state_path.write_text(
        json.dumps({"publication_status": "published_pending_public_cold_restore"}),
        encoding="utf-8",
    )
    assert publication_precheck.is_complete(state_path) is False


def test_one_time_publication_workflow_is_source_bound_or_already_retired():
    workflow_path = ROOT / ".github/workflows/external-binary-annex-publication.yml"
    state = json.loads(
        (ROOT / "preservation/external-binary-annex-state.json").read_text(
            encoding="utf-8"
        )
    )
    if workflow_path.exists():
        workflow = workflow_path.read_text(encoding="utf-8")
        assert "ref: ${{ github.sha }}" in workflow
        assert "TRINITY_PUBLICATION_SOURCE_SHA: ${{ github.sha }}" in workflow
        assert "external_binary_annex_v3.py" in workflow
        assert "publish_external_binary_annexes_to_zenodo_v3.py" in workflow
        assert "external_annex_publication_precheck.py" in workflow
        assert "refs/remotes/origin/main" in workflow
        assert "seal_external_binary_annex_publication.py" in workflow
        assert "steps.precheck.outputs.required == 'false'" in workflow
        assert ".github/workflows/external-binary-annex-publication.yml" in workflow
        assert 'git rm "$path"' in workflow
    else:
        assert state["publication_status"] == publication_precheck.COMPLETE
        assert state["release_asset_pagination_complete"] is True
        assert state["public_metadata_verification"] == "passed"


def test_obsolete_irreversible_repository_publish_workflows_are_inactive():
    workflow_dir = ROOT / ".github/workflows"
    present = {path.name for path in workflow_dir.glob("*.yml")}
    assert not (present & OLD_WRITE_WORKFLOWS)


def test_recovery_index_declares_the_published_core_repository_doi():
    state = json.loads(
        (ROOT / "preservation/zenodo-state.json").read_text(encoding="utf-8")
    )
    index = json.loads((ROOT / "api/recovery-index.json").read_text(encoding="utf-8"))
    assert state["publication_status"] == "published"
    assert state["latest_doi"] == "10.5281/zenodo.21739344"
    latest = index["latest_trusted_release"]
    assert latest["status"] != "not_yet_declared"
    repository = latest["repository_preservation"]
    assert repository["doi"] == state["latest_doi"]
    assert repository["git_commit_sha"] == state["latest_git_commit_sha"]
    assert repository["github_required_for_recovery"] is False
