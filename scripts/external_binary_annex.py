#!/usr/bin/env python3
"""Build and verify Trinity Accord external-binary Zenodo annex packages."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
import urllib.error
import urllib.request
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CORE_DOI = "10.5281/zenodo.21739344"
RIGHTS_SCHEMA = "trinityaccord.external-binary-annex-rights.v1"
LICENSE_ID = "other-closed"
PACKAGE_SCHEMA = "trinityaccord.external-binary-annex.v1"
STATE_SCHEMA = "trinityaccord.external-binary-annex-zenodo-state.v1"
PUBLISHED_FILE_NAMES = (
    "payload.tar",
    "annex-manifest.json",
    "checksums.sha256",
    "README.txt",
    "restore-trinity-annex.py",
    "zenodo-metadata.json",
)
CHECKSUM_TARGET_NAMES = (
    "payload.tar",
    "annex-manifest.json",
    "README.txt",
    "restore-trinity-annex.py",
    "zenodo-metadata.json",
)

ANNEX_SPECS: dict[str, dict[str, Any]] = {
    "evidence": {
        "annex_id": "external-evidence-annex-v1",
        "title": "Trinity Accord External Evidence Binary Annex",
        "release_tags": [
            "signed-large-data-mirror-v1",
            "notarial-certificate-images-v1",
            "flaw-covenant-video-mirror-v1",
            "ots-proof-bundle-mirror-v1",
            "ots-and-flaw-mirror-v1",
            "flaw-covenant-archive-accessibility-mirror-v1",
        ],
        "description": (
            "A non-authoritative, non-amending preservation annex containing the exact "
            "custom GitHub Release assets for the Trinity Accord public evidence, flaw "
            "videos, notarial images, OTS proof bundles, and large accessibility archives. "
            "All bytes were already publicly released before this annex. The annex grants "
            "no new reuse rights and does not change the Bitcoin Originals."
        ),
        "keywords": [
            "Trinity Accord",
            "evidence preservation",
            "digital preservation",
            "OpenTimestamps",
            "notarial evidence",
        ],
    },
    "nft": {
        "annex_id": "chronicle-nft-media-annex-v1",
        "title": "Trinity Accord Chronicle NFT Media Binary Annex",
        "release_tags": [
            "nft-arweave-mirror-175-v1",
            "nft-backup-v1",
        ],
        "description": (
            "A non-authoritative, non-amending preservation annex containing the exact "
            "custom GitHub Release assets for the verified 175-item ASIMilestones Chronicle "
            "NFT Arweave/CAR mirror and the earlier content-complete NFT backup release. "
            "The Chronicle is historical context only; NFT ownership or media preservation "
            "confers no authority, governance, guardianship, investment expectation, or "
            "private-evidence access."
        ),
        "keywords": [
            "Trinity Accord",
            "Chronicle",
            "NFT media preservation",
            "Arweave CAR",
            "digital preservation",
        ],
    },
}
DEPRECATED_EXCLUDED_RELEASE_TAGS = (
    "nft-individual-v1",
    "nft-individual-v2",
)


def strict_json(path: Path) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise SystemExit(f"duplicate JSON key {key!r}: {path}")
            result[key] = value
        return result

    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"non-finite JSON number {token}")
            ),
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise SystemExit(f"invalid strict JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def hash_file(path: Path, algorithm: str = "sha256") -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def md5_file(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_relative(value: str) -> str:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or ".." in path.parts or "\x00" in value:
        raise SystemExit(f"unsafe annex path: {value!r}")
    return str(path)


def github_json(url: str, token: str) -> dict[str, Any]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "trinity-external-binary-annex/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            value = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"GitHub API failed with HTTP {exc.code}: {detail[:1000]}") from exc
    if not isinstance(value, dict):
        raise SystemExit("GitHub release response is not an object")
    return value


def download(url: str, target: Path, token: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "curl",
        "--fail",
        "--location",
        "--silent",
        "--show-error",
        "--retry",
        "6",
        "--retry-delay",
        "3",
        "--retry-all-errors",
        "--output",
        str(target),
    ]
    if token:
        command.extend(["--header", f"Authorization: Bearer {token}"])
    command.append(url)
    subprocess.run(command, check=True)


def release_asset_inventory(
    repository: str,
    release_tags: list[str],
    payload_root: Path,
    token: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    releases: list[dict[str, Any]] = []
    assets_out: list[dict[str, Any]] = []
    owner, name = repository.split("/", 1)
    for tag in release_tags:
        release = github_json(
            f"https://api.github.com/repos/{owner}/{name}/releases/tags/{tag}",
            token,
        )
        assets = release.get("assets")
        if not isinstance(assets, list) or not assets:
            raise SystemExit(f"required release has no custom assets: {tag}")
        release_entry = {
            "tag": tag,
            "release_id": release.get("id"),
            "html_url": release.get("html_url"),
            "published_at": release.get("published_at"),
            "asset_count": len(assets),
        }
        releases.append(release_entry)
        for asset in sorted(
            (item for item in assets if isinstance(item, dict)),
            key=lambda item: str(item.get("name") or ""),
        ):
            asset_name = safe_relative(str(asset.get("name") or ""))
            browser_url = str(asset.get("browser_download_url") or "")
            expected_size = int(asset.get("size") or -1)
            if not browser_url or expected_size < 0:
                raise SystemExit(f"invalid GitHub Release asset metadata: {tag}/{asset_name}")
            rel_path = safe_relative(f"releases/{tag}/{asset_name}")
            target = payload_root / rel_path
            download(browser_url, target, token)
            observed_size = target.stat().st_size
            if observed_size != expected_size:
                raise SystemExit(
                    f"GitHub Release asset size mismatch: {tag}/{asset_name}: "
                    f"{observed_size} != {expected_size}"
                )
            assets_out.append(
                {
                    "release_tag": tag,
                    "release_id": release.get("id"),
                    "asset_id": asset.get("id"),
                    "asset_name": asset_name,
                    "path": rel_path,
                    "bytes": observed_size,
                    "sha256": hash_file(target),
                    "md5": md5_file(target),
                    "browser_download_url": browser_url,
                    "content_type": asset.get("content_type"),
                    "download_count_at_capture": asset.get("download_count"),
                    "created_at": asset.get("created_at"),
                    "updated_at": asset.get("updated_at"),
                }
            )
    return releases, assets_out


def create_deterministic_tar(payload_root: Path, target: Path) -> None:
    with target.open("wb") as raw:
        with tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as archive:
            for path in sorted(
                (item for item in payload_root.rglob("*") if item.is_file()),
                key=lambda item: item.relative_to(payload_root).as_posix(),
            ):
                rel = path.relative_to(payload_root).as_posix()
                info = tarfile.TarInfo(rel)
                info.size = path.stat().st_size
                info.mode = 0o644
                info.uid = 0
                info.gid = 0
                info.uname = ""
                info.gname = ""
                info.mtime = 0
                with path.open("rb") as handle:
                    archive.addfile(info, handle)


def metadata_for(spec: dict[str, Any], publication_date: str) -> dict[str, Any]:
    return {
        "upload_type": "dataset",
        "title": spec["title"],
        "creators": [{"name": "Liu, Hongju"}],
        "description": spec["description"],
        "access_right": "open",
        "license": LICENSE_ID,
        "publication_date": publication_date,
        "version": spec["annex_id"],
        "keywords": spec["keywords"],
        "related_identifiers": [
            {
                "identifier": f"https://doi.org/{CORE_DOI}",
                "relation": "isSupplementTo",
                "resource_type": "software",
            },
            {
                "identifier": "https://github.com/thechurchofagi/trinity-accord",
                "relation": "isDerivedFrom",
                "resource_type": "other",
            },
            {
                "identifier": "https://www.trinityaccord.org",
                "relation": "isDocumentedBy",
                "resource_type": "other",
            },
        ],
        "notes": (
            "All embedded bytes were already publicly available in the named GitHub Releases. "
            "Open access permits preservation retrieval only and grants no new reuse rights. "
            "Each component retains its existing rights; third-party rights are not transferred. "
            "This annex is a non-amending mirror, not authority, attestation, governance, "
            "successor reception, verification level, or investment representation."
        ),
    }


def manifest_identity(manifest: dict[str, Any]) -> str:
    value = dict(manifest)
    value.pop("package_identity_sha256", None)
    return canonical_sha256(value)


def parse_checksums(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        sha, name = line.split("  ", 1)
        if len(sha) != 64 or name in result:
            raise SystemExit(f"invalid annex checksum entry: {name}")
        result[name] = sha
    return result


def file_inventory(package_dir: Path) -> dict[str, dict[str, Any]]:
    return {
        name: {
            "bytes": (package_dir / name).stat().st_size,
            "sha256": hash_file(package_dir / name),
            "md5": md5_file(package_dir / name),
        }
        for name in PUBLISHED_FILE_NAMES
    }


def verify_local_package(package_dir: Path) -> dict[str, Any]:
    observed = {path.name for path in package_dir.iterdir() if path.is_file()}
    if observed != set(PUBLISHED_FILE_NAMES):
        raise SystemExit(
            f"annex file set mismatch: missing={sorted(set(PUBLISHED_FILE_NAMES)-observed)} "
            f"unexpected={sorted(observed-set(PUBLISHED_FILE_NAMES))}"
        )
    checksums = parse_checksums(package_dir / "checksums.sha256")
    if set(checksums) != set(CHECKSUM_TARGET_NAMES):
        raise SystemExit("annex checksums do not cover the exact payload set")
    for name, expected in checksums.items():
        if hash_file(package_dir / name) != expected:
            raise SystemExit(f"annex checksum mismatch: {name}")
    manifest = strict_json(package_dir / "annex-manifest.json")
    if manifest.get("schema") != PACKAGE_SCHEMA:
        raise SystemExit("unsupported annex manifest schema")
    annex_type = str(manifest.get("annex_type") or "")
    spec = ANNEX_SPECS.get(annex_type)
    if not spec or manifest.get("annex_id") != spec["annex_id"]:
        raise SystemExit("annex type/id mismatch")
    if manifest.get("source_release_tags") != spec["release_tags"]:
        raise SystemExit("annex release-tag set/order mismatch")
    if manifest.get("package_identity_sha256") != manifest_identity(manifest):
        raise SystemExit("annex package identity mismatch")
    assets = manifest.get("assets")
    if not isinstance(assets, list) or not assets:
        raise SystemExit("annex asset inventory is empty")
    if manifest.get("asset_count") != len(assets):
        raise SystemExit("annex asset count mismatch")
    if manifest.get("payload_bytes") != sum(int(item["bytes"]) for item in assets):
        raise SystemExit("annex payload byte count mismatch")
    paths: set[str] = set()
    for item in assets:
        if not isinstance(item, dict):
            raise SystemExit("annex asset entry is not an object")
        path = safe_relative(str(item.get("path") or ""))
        if path in paths:
            raise SystemExit(f"duplicate annex asset path: {path}")
        paths.add(path)
        if len(str(item.get("sha256") or "")) != 64 or int(item.get("bytes") or -1) < 0:
            raise SystemExit(f"invalid annex asset identity: {path}")
    metadata = strict_json(package_dir / "zenodo-metadata.json")
    if metadata.get("title") != spec["title"] or metadata.get("version") != spec["annex_id"]:
        raise SystemExit("annex Zenodo metadata mismatch")
    if metadata.get("access_right") != "open" or metadata.get("license") != LICENSE_ID:
        raise SystemExit("annex visibility/rights mismatch")
    return {
        "annex_type": annex_type,
        "annex_id": spec["annex_id"],
        "package_identity_sha256": manifest["package_identity_sha256"],
        "asset_count": len(assets),
        "payload_bytes": manifest["payload_bytes"],
        "inventory": file_inventory(package_dir),
        "manifest": manifest,
        "metadata": metadata,
    }


def build_annex(
    annex_type: str,
    repository: str,
    output_dir: Path,
    publication_date: str,
    token: str,
) -> Path:
    spec = ANNEX_SPECS.get(annex_type)
    if spec is None:
        raise SystemExit(f"unsupported annex type: {annex_type}")
    output_dir = output_dir.resolve()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise SystemExit(f"annex output directory must be empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=f"trinity-{annex_type}-annex-") as temp_name:
        payload_root = Path(temp_name) / "payload"
        payload_root.mkdir()
        releases, assets = release_asset_inventory(
            repository,
            list(spec["release_tags"]),
            payload_root,
            token,
        )
        create_deterministic_tar(payload_root, output_dir / "payload.tar")

    duplicate_groups: dict[str, list[str]] = {}
    for item in assets:
        duplicate_groups.setdefault(str(item["sha256"]), []).append(str(item["path"]))
    exact_duplicate_groups = [
        {"sha256": digest, "paths": paths}
        for digest, paths in sorted(duplicate_groups.items())
        if len(paths) > 1
    ]
    manifest: dict[str, Any] = {
        "schema": PACKAGE_SCHEMA,
        "annex_type": annex_type,
        "annex_id": spec["annex_id"],
        "created_at": publication_date + "T00:00:00Z",
        "source_repository": f"https://github.com/{repository}",
        "core_repository_preservation_doi": CORE_DOI,
        "source_release_tags": list(spec["release_tags"]),
        "deprecated_release_tags_excluded": list(DEPRECATED_EXCLUDED_RELEASE_TAGS),
        "releases": releases,
        "asset_count": len(assets),
        "payload_bytes": sum(int(item["bytes"]) for item in assets),
        "assets": assets,
        "exact_duplicate_groups": exact_duplicate_groups,
        "scope": {
            "all_custom_assets_from_named_releases_embedded": True,
            "github_generated_source_archives_embedded": False,
            "deprecated_failed_individual_nft_attempts_embedded": False,
            "public_release_bytes_only": True,
            "github_required_after_annex_download": False,
            "network_required_after_annex_download": False,
        },
        "rights_boundary": {
            "schema": RIGHTS_SCHEMA,
            "license_identifier": LICENSE_ID,
            "publicly_readable_for_preservation": True,
            "deposit_grants_no_new_reuse_rights": True,
            "components_retain_existing_rights": True,
            "third_party_rights_are_not_transferred": True,
            "publisher_grants_no_rights_not_possessed": True,
        },
        "boundary": {
            "annex_is_non_authoritative_mirror": True,
            "annex_is_not_amendment": True,
            "annex_is_not_attestation": True,
            "annex_is_not_governance": True,
            "annex_is_not_successor_reception": True,
            "bitcoin_originals_prevail": True,
        },
        "package_identity_sha256": None,
    }
    manifest["package_identity_sha256"] = manifest_identity(manifest)
    write_json(output_dir / "annex-manifest.json", manifest)
    write_json(output_dir / "zenodo-metadata.json", metadata_for(spec, publication_date))
    restore_source = ROOT / "scripts" / "restore_external_binary_annex.py"
    shutil.copyfile(restore_source, output_dir / "restore-trinity-annex.py")
    (output_dir / "README.txt").write_text(
        f"{spec['title']}\n"
        f"{'=' * len(spec['title'])}\n\n"
        f"Annex ID: {spec['annex_id']}\n"
        f"Source releases: {', '.join(spec['release_tags'])}\n"
        f"Custom assets: {len(assets)}\n"
        f"Payload bytes: {sum(int(item['bytes']) for item in assets)}\n"
        f"Core repository DOI: {CORE_DOI}\n\n"
        "Restore from this downloaded package directory:\n\n"
        "  python3 restore-trinity-annex.py --deposit-dir . --output-dir ./restored-annex\n\n"
        "Restore after downloading only the standalone script:\n\n"
        "  python3 restore-trinity-annex.py --zenodo-record-id <RECORD_ID> "
        "--output-dir ./restored-annex\n\n"
        "The result includes every exact custom GitHub Release asset from the named "
        "release tags, together with a recovery report. This is a non-amending mirror "
        "and grants no new reuse rights.\n",
        encoding="utf-8",
    )
    (output_dir / "checksums.sha256").write_text(
        "".join(
            f"{hash_file(output_dir / name)}  {name}\n"
            for name in CHECKSUM_TARGET_NAMES
        ),
        encoding="utf-8",
    )
    verified = verify_local_package(output_dir)
    print(json.dumps(verified, ensure_ascii=False, indent=2))
    return output_dir


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--annex-type", choices=sorted(ANNEX_SPECS), required=True)
    parser.add_argument("--repository", default="thechurchofagi/trinity-accord")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--publication-date", default="2026-08-01")
    args = parser.parse_args()
    build_annex(
        args.annex_type,
        args.repository,
        Path(args.output_dir),
        args.publication_date,
        os.environ.get("GITHUB_TOKEN", "").strip(),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
