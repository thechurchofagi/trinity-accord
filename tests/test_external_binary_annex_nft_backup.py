from __future__ import annotations

import io
import json
import sys
import tarfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import external_binary_annex as legacy  # noqa: E402
import external_binary_annex_v2 as annex  # noqa: E402
import external_binary_annex_v3 as annex_v3  # noqa: E402


def _release_entries() -> list[dict[str, object]]:
    return [
        {
            "tag": annex.HISTORICAL_EMPTY_NFT_RELEASE_TAG,
            "release_id": annex.HISTORICAL_EMPTY_NFT_RELEASE_ID,
            "asset_count": 0,
            "empty_release_observation": {
                "observed_custom_asset_count": 0,
                "observed_through_paginated_release_assets_api": True,
                "historical_release_text_claims_175_individual_archives": True,
                "historical_release_text_is_not_byte_evidence": True,
                "content_recovery_source_tag": annex.CONTENT_COMPLETE_NFT_BACKUP_TAG,
            },
        },
        {
            "tag": annex.CONTENT_COMPLETE_NFT_BACKUP_TAG,
            "release_id": annex.CONTENT_COMPLETE_NFT_BACKUP_RELEASE_ID,
            "asset_count": len(annex.NFT_BACKUP_ASSET_NAMES),
        },
    ]


def _asset_entries() -> list[dict[str, object]]:
    return [
        {
            "release_tag": annex.CONTENT_COMPLETE_NFT_BACKUP_TAG,
            "asset_name": name,
        }
        for name in annex.NFT_BACKUP_ASSET_NAMES
    ]


def _manifest(*, failed: int = 0, nfts: int = 175) -> dict[str, object]:
    files: list[dict[str, object]] = []
    for index in range(434):
        token_index = index % 175
        files.append(
            {
                "contract": f"0x{token_index % 4:040x}",
                "token_id": str(token_index),
                "txid": f"tx-{index:043d}",
                "sha256": f"{index:064x}"[-64:],
                "cid": f"bafy-test-{index}",
                "role": "metadata" if index < 175 else "media",
                "size": index + 1,
            }
        )
    return {
        "contracts": 4,
        "nfts": nfts,
        "downloaded": 434,
        "failed": failed,
        "total_txids": 434,
        "files": files,
    }


def _write_manifest_archive(payload_root: Path, value: dict[str, object]) -> Path:
    target = (
        payload_root
        / "releases"
        / annex.CONTENT_COMPLETE_NFT_BACKUP_TAG
        / "nft-cars-manifest.tar.gz"
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")
    with tarfile.open(target, mode="w:gz") as archive:
        info = tarfile.TarInfo("manifest.json")
        info.size = len(raw)
        info.mode = 0o644
        info.uid = 0
        info.gid = 0
        info.mtime = 0
        archive.addfile(info, io.BytesIO(raw))
    return target


def test_paginated_asset_listing_can_observe_an_empty_release():
    calls: list[str] = []

    def fetch_json(url: str, token: str):
        calls.append(url)
        return []

    assert annex.list_release_assets(
        "thechurchofagi/trinity-accord",
        annex.HISTORICAL_EMPTY_NFT_RELEASE_ID,
        "",
        fetch_json=fetch_json,
    ) == []
    assert len(calls) == 1
    assert "per_page=100" in calls[0]


def test_only_the_exact_historical_nft_release_may_be_empty():
    release = {
        "body": "Verified Chronicle mirror with 175 individual NFT archives."
    }
    observed = annex._empty_release_observation(
        annex.HISTORICAL_EMPTY_NFT_RELEASE_TAG,
        annex.HISTORICAL_EMPTY_NFT_RELEASE_ID,
        release,
    )
    assert observed["observed_custom_asset_count"] == 0
    assert observed["historical_release_text_is_not_byte_evidence"] is True
    assert observed["content_recovery_source_tag"] == annex.CONTENT_COMPLETE_NFT_BACKUP_TAG

    with pytest.raises(SystemExit, match="required release has no custom assets"):
        annex._empty_release_observation("unexpected-empty-release", 999, release)
    with pytest.raises(SystemExit, match="release id changed"):
        annex._empty_release_observation(
            annex.HISTORICAL_EMPTY_NFT_RELEASE_TAG,
            999,
            release,
        )
    with pytest.raises(SystemExit, match="no longer states its 175-item scope"):
        annex._empty_release_observation(
            annex.HISTORICAL_EMPTY_NFT_RELEASE_TAG,
            annex.HISTORICAL_EMPTY_NFT_RELEASE_ID,
            {"body": "No scope statement."},
        )


def test_manifest_proves_complete_175_nft_backup(tmp_path: Path):
    payload_root = tmp_path / "payload"
    manifest_path = _write_manifest_archive(payload_root, _manifest())
    releases = _release_entries()
    coverage = annex.validate_nft_release_set(
        releases,
        _asset_entries(),
        payload_root,
    )

    assert coverage["contracts"] == 4
    assert coverage["nfts"] == 175
    assert coverage["arweave_transactions_and_files"] == 434
    assert coverage["successful_downloads"] == 434
    assert coverage["failed_downloads"] == 0
    assert coverage["unique_nft_identities_verified"] == 175
    assert coverage["unique_txids_verified"] == 434
    assert coverage["release_asset_count"] == 10
    assert coverage["manifest_asset_sha256"] == legacy.hash_file(manifest_path)
    assert releases[1]["logical_coverage"] == coverage


def test_manifest_coverage_fails_closed_on_any_failed_download(tmp_path: Path):
    payload_root = tmp_path / "payload"
    _write_manifest_archive(payload_root, _manifest(failed=1))
    with pytest.raises(SystemExit, match="failed: 1 != 0"):
        annex.validate_nft_release_set(
            _release_entries(),
            _asset_entries(),
            payload_root,
        )


def test_manifest_coverage_fails_closed_on_wrong_nft_count(tmp_path: Path):
    payload_root = tmp_path / "payload"
    _write_manifest_archive(payload_root, _manifest(nfts=174))
    with pytest.raises(SystemExit, match="nfts: 174 != 175"):
        annex.validate_nft_release_set(
            _release_entries(),
            _asset_entries(),
            payload_root,
        )


def test_final_nft_metadata_describes_the_observed_availability_boundary():
    annex_v3.activate_final_specs()
    description = legacy.ANNEX_SPECS["nft"]["description"]
    assert "currently exposes zero custom assets" in description
    assert "not treated as byte evidence" in description
    assert "175 NFTs" in description
    assert "434 Arweave transactions/files" in description
    assert "zero failed downloads" in description
