from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def canonical_digest(value: dict[str, object]) -> str:
    canonical = dict(value)
    canonical.pop("source_digest", None)
    return hashlib.sha256(
        json.dumps(
            canonical,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()[:16]


def test_final_annex_state_is_complete_and_consistent():
    state = json.loads(
        (ROOT / "preservation/external-binary-annex-state.json").read_text(
            encoding="utf-8"
        )
    )
    observation = json.loads(
        (ROOT / "preservation/external-binary-annex-observation.json").read_text(
            encoding="utf-8"
        )
    )
    index = json.loads(
        (ROOT / "api/recovery-index.json").read_text(encoding="utf-8")
    )

    assert state["publication_status"] == "published_and_publicly_restored"
    assert observation["publication_status"] == state["publication_status"]
    assert index["latest_trusted_release"]["status"] == state["publication_status"]
    assert state["release_asset_pagination_complete"] is True
    assert state["public_metadata_verification"] == "passed"
    assert state["external_binary_payload_recovery_requires_github"] is False
    assert observation["observed_without_github_credentials"] is True
    assert observation["observed_without_zenodo_credentials"] is True

    expected = {
        "evidence": ("10.5281/zenodo.21753937", 21753937, 28, 204595967),
        "nft": ("10.5281/zenodo.21754229", 21754229, 10, 862714954),
    }
    for annex_type, (doi, record_id, asset_count, payload_bytes) in expected.items():
        entry = state["annexes"][annex_type]
        assert entry["doi"] == doi
        assert entry["record_id"] == record_id
        assert entry["asset_count"] == asset_count
        assert entry["payload_bytes"] == payload_bytes
        assert entry["public_download_verification"] == "passed"
        assert entry["public_metadata_verification"] == "passed"
        assert entry["public_cold_restore"] == "passed"
        assert entry["public_cold_restore_report"]["status"] == "passed"
        assert entry["public_cold_restore_report"]["github_credentials_used"] is False
        assert entry["public_cold_restore_report"]["zenodo_credentials_used"] is False
        assert observation["annexes"][annex_type] == entry
        indexed = index["latest_trusted_release"]["external_binary_annexes"][
            annex_type
        ]
        assert indexed["doi"] == doi
        assert indexed["record_id"] == record_id
        assert indexed["public_cold_restore"] == "passed"


def test_recovery_index_has_no_stale_pending_claim_and_valid_digest():
    index = json.loads(
        (ROOT / "api/recovery-index.json").read_text(encoding="utf-8")
    )
    limitations = index["limitations"]
    assert not any("remain pending" in item.lower() for item in limitations)
    assert not any("V2 annex state" in item for item in limitations)
    assert any(
        "together preserve the current Git-tracked repository and every custom asset"
        in item
        for item in limitations
    )
    assert index["source_digest"] == canonical_digest(index)


def test_one_time_publication_entrypoints_are_retired():
    for path in (
        ".github/workflows/external-binary-annex-publication.yml",
        ".github/workflows/external-binary-annex-publication-v4.yml",
        "preservation/external-binary-annex-publication-trigger.json",
        "preservation/external-binary-annex-publication-attempt.json",
    ):
        assert not (ROOT / path).exists(), path


def test_sealer_removes_every_known_pending_wording():
    text = (ROOT / "scripts/seal_external_binary_annex_publication.py").read_text(
        encoding="utf-8"
    )
    assert "remain pending until the V2 annex state" in text
    assert "does not embed the separately hosted large binary" in text
    assert "separately published evidence and Chronicle NFT" in text
