from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import external_binary_annex as legacy  # noqa: E402
import external_binary_annex_v4 as annex_v4  # noqa: E402
import publish_external_binary_annexes_to_zenodo_v4 as publisher_v4  # noqa: E402


def _expected_metadata() -> dict[str, object]:
    annex_v4.activate_final_specs()
    return legacy.metadata_for(legacy.ANNEX_SPECS["evidence"], "2026-08-02")


def _public_record(expected: dict[str, object]) -> dict[str, object]:
    return {
        "access": {"record": "public", "files": "public", "status": "open"},
        "metadata": {
            key: value
            for key, value in expected.items()
            if key not in {"license", "access_right"}
        }
        | {
            "access_right": "open",
            "license": {"id": "other-closed"},
        },
    }


def _manifest_fixture() -> dict[str, object]:
    return {
        "schema": "trinityaccord.external-binary-annex.v2",
        "annex_type": "evidence",
        "annex_id": "external-evidence-annex-v4",
        "source_commit_sha": "1" * 40,
        "package_identity_sha256": "a" * 64,
        "source_release_tags": ["signed-large-data-mirror-v1"],
        "asset_count": 1,
        "payload_bytes": 12,
        "assets": [
            {
                "release_tag": "signed-large-data-mirror-v1",
                "asset_id": 123,
                "asset_name": "evidence.bin",
                "path": "releases/signed-large-data-mirror-v1/evidence.bin",
                "bytes": 12,
                "sha256": "b" * 64,
                "md5": "c" * 32,
                "download_count_at_capture": 1,
            }
        ],
        "rights_boundary": {
            "license_identifier": "other-closed",
            "deposit_grants_no_new_reuse_rights": True,
        },
    }


def test_v4_uses_new_immutable_pair_after_published_evidence_v3():
    assert annex_v4.FINAL_ANNEX_IDS == {
        "evidence": "external-evidence-annex-v4",
        "nft": "chronicle-nft-media-annex-v4",
    }
    assert publisher_v4.EVIDENCE_V4_RECORD_ID == 21753937
    assert publisher_v4.EVIDENCE_V4_DOI == "10.5281/zenodo.21753937"
    assert publisher_v4.EVIDENCE_V4_CONCEPT_RECORD_ID == 21753253
    assert set(annex_v4.FINAL_ANNEX_IDS.values()).isdisjoint(
        {"external-evidence-annex-v3", "chronicle-nft-media-annex-v3"}
    )


def test_direct_record_top_level_license_is_normalized_and_conflicts_fail_closed():
    expected = _expected_metadata()
    record = {
        "access": {"record": "public", "files": "public", "status": "open"},
        "license": {"id": "other-closed"},
        "metadata": {
            key: value
            for key, value in expected.items()
            if key not in {"license", "access_right"}
        }
        | {"access_right": "open"},
    }
    normalized = publisher_v4.normalized_public_record(record)
    assert normalized["metadata"]["license"] == {"id": "other-closed"}
    publisher_v4.validate_public_metadata_v4(record, expected)

    equivalent_duplicate = json.loads(json.dumps(record))
    equivalent_duplicate["metadata"]["license"] = "other-closed"
    publisher_v4.validate_public_metadata_v4(equivalent_duplicate, expected)

    conflicting = json.loads(json.dumps(record))
    conflicting["metadata"]["license"] = {"id": "cc-by-4.0"}
    with pytest.raises(SystemExit, match="metadata conflict: license/rights"):
        publisher_v4.normalized_public_record(conflicting)


def test_public_zenodo_doi_identifier_shape_is_equivalent_but_values_stay_strict():
    expected = _expected_metadata()
    record = _public_record(expected)
    record["metadata"]["related_identifiers"] = [
        {
            "identifier": "10.5281/zenodo.21739344",
            "relation": "isSupplementTo",
            "resource_type": "software",
            "scheme": "doi",
        },
        {
            "identifier": "https://github.com/thechurchofagi/trinity-accord",
            "relation": "isDerivedFrom",
            "resource_type": "other",
            "scheme": "url",
        },
        {
            "identifier": "https://www.trinityaccord.org",
            "relation": "isDocumentedBy",
            "resource_type": "other",
            "scheme": "url",
        },
    ]
    publisher_v4.validate_public_metadata_v4(record, expected)

    current_shape = json.loads(json.dumps(record))
    current_shape["metadata"]["related_identifiers"][0]["relation_type"] = {
        "id": "is-supplement-to"
    }
    del current_shape["metadata"]["related_identifiers"][0]["relation"]
    current_shape["metadata"]["related_identifiers"][0]["resource_type"] = {
        "id": "software"
    }
    publisher_v4.validate_public_metadata_v4(current_shape, expected)

    wrong_doi = json.loads(json.dumps(record))
    wrong_doi["metadata"]["related_identifiers"][0]["identifier"] = (
        "10.5281/zenodo.99999999"
    )
    with pytest.raises(SystemExit, match="metadata mismatch: related_identifiers"):
        publisher_v4.validate_public_metadata_v4(wrong_doi, expected)

    wrong_resource_type = json.loads(json.dumps(record))
    wrong_resource_type["metadata"]["related_identifiers"][0]["resource_type"] = (
        "publication"
    )
    with pytest.raises(SystemExit, match="metadata mismatch: related_identifiers"):
        publisher_v4.validate_public_metadata_v4(wrong_resource_type, expected)


def test_stable_manifest_view_ignores_only_provenance_and_download_counts():
    public = _manifest_fixture()
    current = copy.deepcopy(public)
    current["source_commit_sha"] = "2" * 40
    current["package_identity_sha256"] = "d" * 64
    current["assets"][0]["download_count_at_capture"] = 999
    assert publisher_v4._stable_manifest_view(public) == (
        publisher_v4._stable_manifest_view(current)
    )


def test_stable_manifest_view_rejects_every_content_and_rights_change():
    original = _manifest_fixture()
    for mutate in (
        lambda value: value["assets"][0].__setitem__("sha256", "e" * 64),
        lambda value: value["assets"][0].__setitem__("bytes", 13),
        lambda value: value["assets"][0].__setitem__("asset_id", 124),
        lambda value: value["assets"][0].__setitem__("path", "other.bin"),
        lambda value: value["source_release_tags"].append("unexpected-release"),
        lambda value: value["rights_boundary"].__setitem__(
            "deposit_grants_no_new_reuse_rights", False
        ),
    ):
        changed = copy.deepcopy(original)
        mutate(changed)
        assert publisher_v4._stable_manifest_view(original) != (
            publisher_v4._stable_manifest_view(changed)
        )


def test_stable_manifest_view_rejects_malformed_assets():
    missing = _manifest_fixture()
    del missing["assets"]
    with pytest.raises(SystemExit, match="lacks assets list"):
        publisher_v4._stable_manifest_view(missing)

    malformed = _manifest_fixture()
    malformed["assets"] = ["not-an-object"]
    with pytest.raises(SystemExit, match="non-object asset"):
        publisher_v4._stable_manifest_view(malformed)


def test_other_duplicate_public_metadata_conflicts_fail_closed():
    expected = _expected_metadata()
    record = {
        "access": {"record": "public", "files": "public", "status": "open"},
        "license": {"id": "other-closed"},
        "keywords": ["conflicting keyword"],
        "metadata": {
            key: value
            for key, value in expected.items()
            if key not in {"license", "access_right"}
        }
        | {"access_right": "open"},
    }
    with pytest.raises(SystemExit, match="metadata conflict: keywords"):
        publisher_v4.validate_public_metadata_v4(record, expected)


def test_v4_workflow_is_source_bound_serialized_and_self_retiring():
    workflow_path = ROOT / ".github/workflows/external-binary-annex-publication-v4.yml"
    state = json.loads(
        (ROOT / "preservation/external-binary-annex-state.json").read_text(
            encoding="utf-8"
        )
    )
    if not workflow_path.exists():
        assert state["publication_status"] == "published_and_publicly_restored"
        return

    text = workflow_path.read_text(encoding="utf-8")
    job_env = text.split("    env:\n", 1)[1].split("\n\n    steps:", 1)[0]
    assert "runner.temp" not in job_env
    assert "group: main-write-lock" in text
    assert "queue: max" in text
    assert "cancel-in-progress: false" in text
    assert "ref: ${{ github.sha }}" in text
    assert "TRINITY_PUBLICATION_SOURCE_SHA: ${{ github.sha }}" in text
    assert "external_binary_annex_v4.py" in text
    assert "publish_external_binary_annexes_to_zenodo_v4.py" in text
    assert "git fetch origin main --prune" in text
    assert "git rebase origin/main" in text
    assert ".github/workflows/external-binary-annex-publication.yml" in text
    assert ".github/workflows/external-binary-annex-publication-v4.yml" in text
    assert "preservation/external-binary-annex-publication-trigger.json" in text
    assert 'git rm "$path"' in text


def test_sealer_preserves_annex_specific_source_commits():
    text = (ROOT / "scripts/seal_external_binary_annex_publication.py").read_text(
        encoding="utf-8"
    )
    assert "publication_workflow_source_commit_sha" in text
    assert "annex_source_commits" in text
    assert 'annex_sources[annex_type]' in text
    assert 'entry["source_commit_sha"]' in text
