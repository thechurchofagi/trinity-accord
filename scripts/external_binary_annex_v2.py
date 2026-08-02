#!/usr/bin/env python3
"""Build complete, source-bound Trinity external-binary annex packages.

This wrapper keeps the established package format while replacing the release
asset discovery path with the paginated List release assets API. It also binds
every package to the exact workflow source commit and records the observed
availability boundary of each named release.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import tarfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable

import external_binary_annex as legacy

GITHUB_API = "https://api.github.com"
V2_ANNEX_IDS = {
    "evidence": "external-evidence-annex-v2",
    "nft": "chronicle-nft-media-annex-v2",
}
FetchJson = Callable[[str, str], Any]

HISTORICAL_EMPTY_NFT_RELEASE_TAG = "nft-arweave-mirror-175-v1"
HISTORICAL_EMPTY_NFT_RELEASE_ID = 315637397
CONTENT_COMPLETE_NFT_BACKUP_TAG = "nft-backup-v1"
CONTENT_COMPLETE_NFT_BACKUP_RELEASE_ID = 315551270
NFT_BACKUP_ASSET_NAMES = (
    "nft-cars-manifest.tar.gz",
    "nft-cars-part01.tar.gz",
    "nft-cars-part02.tar.gz",
    "nft-cars-part03.tar.gz",
    "nft-cars-part04.tar.gz",
    "nft-cars-part05.tar.gz",
    "nft-cars-part06.tar.gz",
    "nft-cars-part07.tar.gz",
    "nft-cars-part08.tar.gz",
    "nft-cars-part09.tar.gz",
)
NFT_BACKUP_EXPECTED_COVERAGE = {
    "contracts": 4,
    "nfts": 175,
    "downloaded": 434,
    "failed": 0,
    "total_txids": 434,
    "files": 434,
}


def activate_v2_specs() -> None:
    """Use immutable version identifiers and accurate NFT availability wording."""
    specs = copy.deepcopy(legacy.ANNEX_SPECS)
    for annex_type, annex_id in V2_ANNEX_IDS.items():
        specs[annex_type]["annex_id"] = annex_id
    specs["nft"]["description"] = (
        "A non-authoritative, non-amending preservation annex containing every "
        "custom asset currently available from the named Trinity Accord Chronicle "
        "NFT GitHub Releases. The historical nft-arweave-mirror-175-v1 Release "
        "currently exposes zero custom assets; its Release text is recorded only as "
        "an availability observation and is not treated as byte evidence. The exact "
        "ten custom assets from nft-backup-v1 are embedded, and their own manifest is "
        "verified to cover 175 NFTs, 434 Arweave transactions/files, four contracts, "
        "434 successful downloads, and zero failed downloads. The Chronicle is "
        "historical context only; preservation confers no authority, governance, "
        "guardianship, investment expectation, or private-evidence access."
    )
    legacy.ANNEX_SPECS = specs


def github_json_any(url: str, token: str) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "trinity-external-binary-annex/2.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"GitHub API failed with HTTP {exc.code}: {detail[:1000]}") from exc
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"GitHub API response failed: {url}: {exc}") from exc


def list_release_assets(
    repository: str,
    release_id: int,
    token: str,
    *,
    fetch_json: FetchJson = github_json_any,
) -> list[dict[str, Any]]:
    """Return the complete release asset list through explicit pagination."""
    owner, name = repository.split("/", 1)
    result: list[dict[str, Any]] = []
    per_page = 100
    for page in range(1, 101):
        query = urllib.parse.urlencode({"per_page": per_page, "page": page})
        value = fetch_json(
            f"{GITHUB_API}/repos/{owner}/{name}/releases/{release_id}/assets?{query}",
            token,
        )
        if not isinstance(value, list):
            raise SystemExit("GitHub release-assets endpoint returned a non-list")
        page_items = [item for item in value if isinstance(item, dict)]
        if len(page_items) != len(value):
            raise SystemExit("GitHub release-assets endpoint returned a non-object item")
        result.extend(page_items)
        if len(page_items) < per_page:
            break
    else:
        raise SystemExit("GitHub release asset pagination exceeded 10,000 assets")

    ids: set[int] = set()
    names: set[str] = set()
    for item in result:
        try:
            asset_id = int(item.get("id"))
        except (TypeError, ValueError) as exc:
            raise SystemExit("GitHub release asset is missing a numeric id") from exc
        asset_name = legacy.safe_relative(str(item.get("name") or ""))
        if asset_id in ids:
            raise SystemExit(f"duplicate GitHub release asset id: {asset_id}")
        if asset_name in names:
            raise SystemExit(f"duplicate GitHub release asset name: {asset_name}")
        ids.add(asset_id)
        names.add(asset_name)
    return result


def _empty_release_observation(
    tag: str,
    release_id: int,
    release: dict[str, Any],
) -> dict[str, Any]:
    if tag != HISTORICAL_EMPTY_NFT_RELEASE_TAG:
        raise SystemExit(f"required release has no custom assets: {tag}")
    if release_id != HISTORICAL_EMPTY_NFT_RELEASE_ID:
        raise SystemExit("historical empty NFT release id changed")
    body = str(release.get("body") or "")
    if "175 individual NFT archives" not in body:
        raise SystemExit("historical empty NFT release no longer states its 175-item scope")
    return {
        "observed_custom_asset_count": 0,
        "observed_through_paginated_release_assets_api": True,
        "historical_release_text_claims_175_individual_archives": True,
        "historical_release_text_sha256": hashlib.sha256(
            body.encode("utf-8")
        ).hexdigest(),
        "historical_release_text_is_not_byte_evidence": True,
        "content_recovery_source_tag": CONTENT_COMPLETE_NFT_BACKUP_TAG,
    }


def _read_nft_backup_manifest(path: Path) -> dict[str, Any]:
    with tarfile.open(path, mode="r:gz") as archive:
        members = archive.getmembers()
        if len(members) != 1:
            raise SystemExit("NFT backup manifest archive must contain exactly one file")
        member = members[0]
        if not member.isfile() or legacy.safe_relative(member.name) != "manifest.json":
            raise SystemExit("NFT backup manifest archive member is not manifest.json")
        handle = archive.extractfile(member)
        if handle is None:
            raise SystemExit("unable to read NFT backup manifest.json")
        with handle:
            try:
                value = json.loads(handle.read().decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise SystemExit("invalid NFT backup manifest JSON") from exc
    if not isinstance(value, dict):
        raise SystemExit("NFT backup manifest is not an object")
    return value


def validate_nft_release_set(
    releases: list[dict[str, Any]],
    assets: list[dict[str, Any]],
    payload_root: Path,
) -> dict[str, Any]:
    by_tag = {str(item["tag"]): item for item in releases}
    if set(by_tag) != {
        HISTORICAL_EMPTY_NFT_RELEASE_TAG,
        CONTENT_COMPLETE_NFT_BACKUP_TAG,
    }:
        raise SystemExit("unexpected NFT release-tag set")

    historical = by_tag[HISTORICAL_EMPTY_NFT_RELEASE_TAG]
    if int(historical["release_id"]) != HISTORICAL_EMPTY_NFT_RELEASE_ID:
        raise SystemExit("historical NFT mirror release id mismatch")
    if int(historical["asset_count"]) != 0:
        raise SystemExit("historical NFT mirror release is no longer empty")
    if not isinstance(historical.get("empty_release_observation"), dict):
        raise SystemExit("historical empty NFT release observation is missing")

    backup = by_tag[CONTENT_COMPLETE_NFT_BACKUP_TAG]
    if int(backup["release_id"]) != CONTENT_COMPLETE_NFT_BACKUP_RELEASE_ID:
        raise SystemExit("content-complete NFT backup release id mismatch")
    backup_assets = [
        item for item in assets if item["release_tag"] == CONTENT_COMPLETE_NFT_BACKUP_TAG
    ]
    observed_names = tuple(sorted(str(item["asset_name"]) for item in backup_assets))
    if observed_names != tuple(sorted(NFT_BACKUP_ASSET_NAMES)):
        raise SystemExit(
            "NFT backup release asset set mismatch: "
            f"observed={list(observed_names)}"
        )
    if int(backup["asset_count"]) != len(NFT_BACKUP_ASSET_NAMES):
        raise SystemExit("NFT backup release asset count mismatch")

    manifest_path = (
        payload_root
        / "releases"
        / CONTENT_COMPLETE_NFT_BACKUP_TAG
        / "nft-cars-manifest.tar.gz"
    )
    manifest = _read_nft_backup_manifest(manifest_path)
    for key, expected in NFT_BACKUP_EXPECTED_COVERAGE.items():
        value = manifest.get(key)
        observed = len(value) if key == "files" and isinstance(value, list) else value
        if observed != expected:
            raise SystemExit(
                f"NFT backup manifest coverage mismatch: {key}: {observed} != {expected}"
            )

    files = manifest.get("files")
    if not isinstance(files, list):
        raise SystemExit("NFT backup manifest files is not a list")
    identities: set[tuple[str, str]] = set()
    txids: set[str] = set()
    for index, item in enumerate(files):
        if not isinstance(item, dict):
            raise SystemExit(f"NFT backup manifest file entry is not an object: {index}")
        contract = str(item.get("contract") or "").lower()
        token_id = str(item.get("token_id") or "")
        txid = str(item.get("txid") or "")
        sha256 = str(item.get("sha256") or "")
        cid = str(item.get("cid") or "")
        role = str(item.get("role") or "")
        try:
            size = int(item.get("size"))
        except (TypeError, ValueError) as exc:
            raise SystemExit(f"invalid NFT backup manifest file size: {index}") from exc
        if not contract or not token_id or not txid or not cid or not role:
            raise SystemExit(f"incomplete NFT backup manifest file identity: {index}")
        if len(sha256) != 64 or any(ch not in "0123456789abcdef" for ch in sha256.lower()):
            raise SystemExit(f"invalid NFT backup manifest SHA-256: {index}")
        if size < 0:
            raise SystemExit(f"negative NFT backup manifest file size: {index}")
        identities.add((contract, token_id))
        if txid in txids:
            raise SystemExit(f"duplicate NFT backup manifest txid: {txid}")
        txids.add(txid)
    if len(identities) != NFT_BACKUP_EXPECTED_COVERAGE["nfts"]:
        raise SystemExit("NFT backup manifest unique NFT identity count mismatch")
    if len(txids) != NFT_BACKUP_EXPECTED_COVERAGE["total_txids"]:
        raise SystemExit("NFT backup manifest unique txid count mismatch")

    coverage = {
        "schema": "trinityaccord.chronicle-nft-backup-logical-coverage.v1",
        "manifest_asset": "nft-cars-manifest.tar.gz",
        "manifest_asset_sha256": legacy.hash_file(manifest_path),
        "contracts": NFT_BACKUP_EXPECTED_COVERAGE["contracts"],
        "nfts": NFT_BACKUP_EXPECTED_COVERAGE["nfts"],
        "arweave_transactions_and_files": NFT_BACKUP_EXPECTED_COVERAGE[
            "total_txids"
        ],
        "successful_downloads": NFT_BACKUP_EXPECTED_COVERAGE["downloaded"],
        "failed_downloads": NFT_BACKUP_EXPECTED_COVERAGE["failed"],
        "unique_nft_identities_verified": len(identities),
        "unique_txids_verified": len(txids),
        "release_asset_count": len(backup_assets),
        "content_complete_backup_manifest_verified": True,
    }
    backup["logical_coverage"] = coverage
    return coverage


def release_asset_inventory_v2(
    repository: str,
    release_tags: list[str],
    payload_root: Path,
    token: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    releases: list[dict[str, Any]] = []
    assets_out: list[dict[str, Any]] = []
    owner, name = repository.split("/", 1)
    for tag in release_tags:
        release = github_json_any(
            f"{GITHUB_API}/repos/{owner}/{name}/releases/tags/{urllib.parse.quote(tag)}",
            token,
        )
        if not isinstance(release, dict):
            raise SystemExit(f"GitHub release response is not an object: {tag}")
        try:
            release_id = int(release.get("id"))
        except (TypeError, ValueError) as exc:
            raise SystemExit(f"GitHub release is missing id: {tag}") from exc
        assets = list_release_assets(repository, release_id, token)
        release_entry: dict[str, Any] = {
            "tag": tag,
            "release_id": release_id,
            "name": release.get("name"),
            "html_url": release.get("html_url"),
            "published_at": release.get("published_at"),
            "asset_count": len(assets),
            "asset_listing": "github-rest-list-release-assets-paginated-v1",
            "asset_pages_complete": True,
        }
        if not assets:
            release_entry["empty_release_observation"] = _empty_release_observation(
                tag, release_id, release
            )
        releases.append(release_entry)
        for asset in sorted(assets, key=lambda item: str(item.get("name") or "")):
            asset_name = legacy.safe_relative(str(asset.get("name") or ""))
            browser_url = str(asset.get("browser_download_url") or "")
            expected_size = int(asset.get("size") or -1)
            if not browser_url or expected_size < 0:
                raise SystemExit(f"invalid GitHub Release asset metadata: {tag}/{asset_name}")
            rel_path = legacy.safe_relative(f"releases/{tag}/{asset_name}")
            target = payload_root / rel_path
            legacy.download(browser_url, target, token)
            observed_size = target.stat().st_size
            if observed_size != expected_size:
                raise SystemExit(
                    f"GitHub Release asset size mismatch: {tag}/{asset_name}: "
                    f"{observed_size} != {expected_size}"
                )
            assets_out.append(
                {
                    "release_tag": tag,
                    "release_id": release_id,
                    "asset_id": int(asset["id"]),
                    "asset_name": asset_name,
                    "path": rel_path,
                    "bytes": observed_size,
                    "sha256": legacy.hash_file(target),
                    "md5": legacy.md5_file(target),
                    "browser_download_url": browser_url,
                    "content_type": asset.get("content_type"),
                    "download_count_at_capture": asset.get("download_count"),
                    "created_at": asset.get("created_at"),
                    "updated_at": asset.get("updated_at"),
                }
            )
    if sum(int(item["asset_count"]) for item in releases) != len(assets_out):
        raise SystemExit("release asset page counts do not match the downloaded inventory")
    if release_tags == legacy.ANNEX_SPECS["nft"]["release_tags"]:
        validate_nft_release_set(releases, assets_out, payload_root)
    elif not assets_out:
        raise SystemExit("annex release set contains no custom assets")
    return releases, assets_out


def _valid_commit_sha(value: str) -> str:
    normalized = value.strip().lower()
    if len(normalized) != 40 or any(ch not in "0123456789abcdef" for ch in normalized):
        raise SystemExit("source commit must be an exact 40-character Git SHA-1")
    return normalized


def build_annex_v2(
    annex_type: str,
    repository: str,
    output_dir: Path,
    publication_date: str,
    token: str,
    source_commit: str,
) -> Path:
    activate_v2_specs()
    legacy.release_asset_inventory = release_asset_inventory_v2
    package_dir = legacy.build_annex(
        annex_type,
        repository,
        output_dir,
        publication_date,
        token,
    )
    manifest_path = package_dir / "annex-manifest.json"
    manifest = legacy.strict_json(manifest_path)
    manifest["source_commit_sha"] = _valid_commit_sha(source_commit)
    manifest["release_asset_discovery"] = {
        "api": "GitHub REST List release assets",
        "per_page": 100,
        "pagination_complete": True,
        "duplicate_asset_ids_rejected": True,
        "duplicate_asset_names_rejected": True,
        "empty_named_release_allowed_only_with_exact_observation_contract": True,
    }
    manifest["source_release_asset_counts"] = {
        str(item["tag"]): int(item["asset_count"])
        for item in manifest["releases"]
    }
    if annex_type == "nft":
        by_tag = {str(item["tag"]): item for item in manifest["releases"]}
        manifest["release_availability_observation"] = {
            HISTORICAL_EMPTY_NFT_RELEASE_TAG: by_tag[
                HISTORICAL_EMPTY_NFT_RELEASE_TAG
            ]["empty_release_observation"]
        }
        manifest["logical_payload_coverage"] = by_tag[
            CONTENT_COMPLETE_NFT_BACKUP_TAG
        ]["logical_coverage"]
    manifest["source_asset_inventory_sha256"] = hashlib.sha256(
        json.dumps(
            [
                {
                    "release_tag": item["release_tag"],
                    "asset_id": item["asset_id"],
                    "asset_name": item["asset_name"],
                    "bytes": item["bytes"],
                    "sha256": item["sha256"],
                }
                for item in manifest["assets"]
            ],
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    manifest["package_identity_sha256"] = None
    manifest["package_identity_sha256"] = legacy.manifest_identity(manifest)
    legacy.write_json(manifest_path, manifest)
    (package_dir / "checksums.sha256").write_text(
        "".join(
            f"{legacy.hash_file(package_dir / name)}  {name}\n"
            for name in legacy.CHECKSUM_TARGET_NAMES
        ),
        encoding="utf-8",
    )
    legacy.verify_local_package(package_dir)
    return package_dir


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--annex-type", choices=sorted(V2_ANNEX_IDS), required=True)
    parser.add_argument("--repository", default="thechurchofagi/trinity-accord")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--publication-date", default="2026-08-02")
    parser.add_argument(
        "--source-commit",
        default=os.environ.get("TRINITY_PUBLICATION_SOURCE_SHA", ""),
        required=False,
    )
    args = parser.parse_args()
    build_annex_v2(
        args.annex_type,
        args.repository,
        Path(args.output_dir),
        args.publication_date,
        os.environ.get("GITHUB_TOKEN", "").strip(),
        args.source_commit,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
