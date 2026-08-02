#!/usr/bin/env python3
"""Build complete, source-bound Trinity external-binary annex packages.

This wrapper keeps the established package format while replacing the release
asset discovery path with the paginated List release assets API. It also binds
every package to the exact workflow source commit.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
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


def activate_v2_specs() -> None:
    """Use immutable V2 version identifiers without mutating imported callers."""
    specs = copy.deepcopy(legacy.ANNEX_SPECS)
    for annex_type, annex_id in V2_ANNEX_IDS.items():
        specs[annex_type]["annex_id"] = annex_id
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

    if not result:
        raise SystemExit(f"required release has no custom assets: release_id={release_id}")
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
        release_entry = {
            "tag": tag,
            "release_id": release_id,
            "html_url": release.get("html_url"),
            "published_at": release.get("published_at"),
            "asset_count": len(assets),
            "asset_listing": "github-rest-list-release-assets-paginated-v1",
            "asset_pages_complete": True,
        }
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
    }
    manifest["source_release_asset_counts"] = {
        str(item["tag"]): int(item["asset_count"])
        for item in manifest["releases"]
    }
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
