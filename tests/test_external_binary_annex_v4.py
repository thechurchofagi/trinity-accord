from __future__ import annotations

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


def test_v4_uses_new_immutable_pair_after_published_evidence_v3():
    assert annex_v4.FINAL_ANNEX_IDS == {
        "evidence": "external-evidence-annex-v4",
        "nft": "chronicle-nft-media-annex-v4",
    }
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
    with pytest.raises(SystemExit, match="metadata conflict: license/rights"):
        publisher_v4.validate_public_metadata_v4(conflicting, expected)


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
