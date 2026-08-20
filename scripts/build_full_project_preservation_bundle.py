#!/usr/bin/env python3
"""Build a content-addressed, auditable Trinity Accord full-project backup.

Scope:
- a safe current repository preservation capsule (not unsafe leaked historical blobs),
- every custom asset exposed by every GitHub Release through complete pagination,
- the exact already-published Polygon/Base sidechain DOI files,
- manifests/checksums sufficient for offline verification and reconstruction.

This is preservation only. It cannot amend or reinterpret the three Bitcoin Originals.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import external_binary_annex_v2
import verify_full_project_preservation_bundle as verifier

GITHUB_API = "https://api.github.com"
ZENODO_API = "https://zenodo.org/api"
SCHEMA = verifier.SCHEMA
SIDECHAIN_ARCHIVE_NAME = "chronicle-sidechain-evidence-v2-f64cc872b3b5.tar.gz"
SIDECHAIN_ARCHIVE_SHA256 = "64152b7fc861dbf8aa9cec447ab7078a6a815136ccfc1b9bb0285aaca2ff1572"
EXPECTED_SIDECHAIN_COORDINATES = 217
EXPECTED_SIDECHAIN_L2_PASS = 217
EXPECTED_SIDECHAIN_IPFS_ROOTS = 257
EXPECTED_SIDECHAIN_EXACT_CAR_ROOTS = 250
EXPECTED_SIDECHAIN_UNRESOLVED_ROOTS = 7


def log(message: str) -> None:
    print(f"[full-project-preservation] {message}", flush=True)


def strict_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"JSON root is not an object: {path}")
    return value


def safe_segment(value: str) -> str:
    value = value.strip()
    if not value or value in {".", ".."} or "/" in value or "\\" in value or "\x00" in value:
        raise SystemExit(f"unsafe path segment: {value!r}")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def md5_file(path: Path) -> str:
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def request_json(url: str, token: str = "") -> Any:
    headers = {
        "Accept": "application/vnd.github+json" if url.startswith(GITHUB_API) else "application/json",
        "User-Agent": "trinity-full-project-preservation/1.0",
    }
    if url.startswith(GITHUB_API):
        headers["X-GitHub-Api-Version"] = "2022-11-28"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    last: Exception | None = None
    for attempt in range(1, 6):
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            last = exc
            if isinstance(exc, urllib.error.HTTPError) and exc.code < 500 and exc.code not in {408, 429}:
                detail = exc.read().decode("utf-8", errors="replace")
                raise SystemExit(f"HTTP {exc.code} for {url}: {detail[:1000]}") from exc
            log(f"JSON request retry {attempt}/5 after {type(exc).__name__}: {url}")
            time.sleep(min(2 ** attempt, 20))
    raise SystemExit(f"JSON request failed after retries: {url}: {last}")


def download(url: str, target: Path, token: str = "") -> None:
    headers = {"User-Agent": "trinity-full-project-preservation/1.0"}
    if token and url.startswith("https://github.com/"):
        headers["Authorization"] = f"Bearer {token}"
    last: Exception | None = None
    target.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(1, 6):
        tmp = target.with_name(target.name + f".part-{attempt}")
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=600) as response, tmp.open("wb") as handle:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    handle.write(chunk)
            os.replace(tmp, target)
            return
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
            last = exc
            tmp.unlink(missing_ok=True)
            if isinstance(exc, urllib.error.HTTPError) and exc.code < 500 and exc.code not in {408, 429}:
                detail = exc.read().decode("utf-8", errors="replace")
                raise SystemExit(f"download HTTP {exc.code}: {url}: {detail[:1000]}") from exc
            log(f"download retry {attempt}/5 after {type(exc).__name__}: {url}")
            time.sleep(min(2 ** attempt, 20))
    raise SystemExit(f"download failed after retries: {url}: {last}")


class ObjectStore:
    def __init__(self, output: Path):
        self.output = output
        self.objects: dict[str, dict[str, Any]] = {}
        self.unique_bytes = 0
        self.logical_bytes = 0

    def ingest(self, path: Path, origin: dict[str, Any]) -> tuple[str, int, bool]:
        size = path.stat().st_size
        sha = sha256_file(path)
        object_path = self.output / "objects" / "sha256" / sha[:2] / sha
        is_new = sha not in self.objects
        if is_new:
            object_path.parent.mkdir(parents=True, exist_ok=True)
            if object_path.exists():
                if object_path.stat().st_size != size or sha256_file(object_path) != sha:
                    raise SystemExit(f"pre-existing object mismatch: {sha}")
            else:
                shutil.copyfile(path, object_path)
            self.objects[sha] = {"sha256": sha, "bytes": size, "origin_count": 0}
            self.unique_bytes += size
        elif int(self.objects[sha]["bytes"]) != size:
            raise SystemExit(f"SHA-256 collision/size disagreement: {sha}")
        self.objects[sha]["origin_count"] = int(self.objects[sha]["origin_count"]) + 1
        self.logical_bytes += size
        return sha, size, is_new

    def manifest_objects(self) -> list[dict[str, Any]]:
        return [self.objects[key] for key in sorted(self.objects)]


def git_value(*args: str) -> str:
    result = subprocess.run(["git", *args], check=True, text=True, stdout=subprocess.PIPE)
    return result.stdout.strip()


def list_all_releases(repository: str, token: str) -> list[dict[str, Any]]:
    owner, name = repository.split("/", 1)
    result: list[dict[str, Any]] = []
    for page in range(1, 101):
        query = urllib.parse.urlencode({"per_page": 100, "page": page})
        value = request_json(f"{GITHUB_API}/repos/{owner}/{name}/releases?{query}", token)
        if not isinstance(value, list):
            raise SystemExit("GitHub releases endpoint returned a non-list")
        items = [item for item in value if isinstance(item, dict)]
        if len(items) != len(value):
            raise SystemExit("GitHub releases endpoint returned a non-object item")
        result.extend(items)
        log(f"release enumeration page={page} items={len(items)} cumulative={len(result)}")
        if len(items) < 100:
            break
    else:
        raise SystemExit("GitHub release pagination exceeded 10,000 releases")
    ids: set[int] = set()
    for item in result:
        try:
            release_id = int(item.get("id"))
        except (TypeError, ValueError) as exc:
            raise SystemExit("GitHub release missing numeric id") from exc
        if release_id in ids:
            raise SystemExit(f"duplicate GitHub release id: {release_id}")
        ids.add(release_id)
    return result


def release_sources(
    repository: str,
    token: str,
    store: ObjectStore,
    scratch: Path,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    releases = list_all_releases(repository, token)
    sources: list[dict[str, Any]] = []
    total_assets = 0
    total_declared_bytes = 0
    downloaded_bytes = 0
    duplicate_asset_bytes = 0

    for release_index, release in enumerate(releases, start=1):
        release_id = int(release["id"])
        tag = safe_segment(str(release.get("tag_name") or f"release-{release_id}"))
        assets = external_binary_annex_v2.list_release_assets(repository, release_id, token)
        declared = sum(int(item.get("size") or 0) for item in assets)
        total_assets += len(assets)
        total_declared_bytes += declared
        log(
            f"release {release_index}/{len(releases)} tag={tag} id={release_id} "
            f"assets={len(assets)} declared_bytes={declared}"
        )
        source: dict[str, Any] = {
            "source_id": f"github-release:{release_id}",
            "kind": "github_release_custom_assets",
            "release_id": release_id,
            "release_tag": tag,
            "release_name": release.get("name"),
            "draft": bool(release.get("draft")),
            "prerelease": bool(release.get("prerelease")),
            "published_at": release.get("published_at"),
            "asset_listing": "github-rest-list-release-assets-paginated-v1",
            "asset_pages_complete": True,
            "files": [],
        }
        for asset_index, asset in enumerate(sorted(assets, key=lambda x: int(x.get("id") or 0)), start=1):
            asset_id = int(asset.get("id"))
            asset_name = safe_segment(str(asset.get("name") or ""))
            expected_size = int(asset.get("size") or -1)
            browser_url = str(asset.get("browser_download_url") or "")
            if expected_size < 0 or not browser_url:
                raise SystemExit(f"invalid Release asset metadata: {tag}/{asset_name}")
            tmp = scratch / "release-assets" / str(release_id) / asset_name
            log(
                f"download release_asset tag={tag} asset={asset_index}/{len(assets)} "
                f"id={asset_id} bytes={expected_size}"
            )
            download(browser_url, tmp, token)
            observed_size = tmp.stat().st_size
            if observed_size != expected_size:
                raise SystemExit(
                    f"Release asset size mismatch: {tag}/{asset_name}: "
                    f"{observed_size} != {expected_size}"
                )
            sha, size, is_new = store.ingest(
                tmp,
                {"kind": "github_release_asset", "release_id": release_id, "asset_id": asset_id},
            )
            downloaded_bytes += size
            if not is_new:
                duplicate_asset_bytes += size
            source["files"].append(
                {
                    "logical_path": f"github-releases/{release_id}-{tag}/{asset_name}",
                    "object_sha256": sha,
                    "bytes": size,
                    "asset_id": asset_id,
                    "github_declared_size": expected_size,
                    "content_type": asset.get("content_type"),
                    "state": asset.get("state"),
                    "created_at": asset.get("created_at"),
                    "updated_at": asset.get("updated_at"),
                }
            )
            tmp.unlink(missing_ok=True)
        sources.append(source)
    return sources, {
        "release_count": len(releases),
        "release_asset_count": total_assets,
        "release_declared_bytes": total_declared_bytes,
        "release_downloaded_bytes": downloaded_bytes,
        "release_duplicate_bytes_deduplicated": duplicate_asset_bytes,
    }


def current_repository_capsule_source(
    source_sha: str,
    store: ObjectStore,
    scratch: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    capsule = scratch / "current-repository-capsule"
    subprocess.run(
        [
            sys.executable,
            "scripts/build_preservation_capsule.py",
            "--repository-root",
            ".",
            "--commit",
            source_sha,
            "--output-dir",
            str(capsule),
        ],
        check=True,
    )
    restore_dir = scratch / "current-repository-cold-restore"
    subprocess.run(
        [
            sys.executable,
            str(capsule / "restore-trinity-accord.py"),
            "--deposit-dir",
            str(capsule),
            "--output-dir",
            str(restore_dir),
        ],
        check=True,
    )
    report = strict_json(restore_dir / "recovery-report.json")
    if report.get("result") != "pass":
        raise SystemExit("current repository capsule cold restore did not PASS")
    if report.get("source_git_commit_sha") != source_sha:
        raise SystemExit("current repository capsule restored wrong source commit")

    files: list[dict[str, Any]] = []
    for path in sorted(item for item in capsule.iterdir() if item.is_file()):
        sha, size, _ = store.ingest(path, {"kind": "current_repository_capsule"})
        files.append(
            {
                "logical_path": f"current-repository-capsule/{safe_segment(path.name)}",
                "object_sha256": sha,
                "bytes": size,
            }
        )
    source = {
        "source_id": f"current-repository-capsule:{source_sha}",
        "kind": "safe_current_repository_preservation_capsule",
        "source_git_commit_sha": source_sha,
        "unsafe_parent_history_republished": False,
        "security_boundary": (
            "Uses the established safe single-root repository capsule. Full parent-history/tag blobs "
            "are intentionally not republished because historical Git objects included a leaked credential."
        ),
        "local_github_zero_cold_restore": "passed",
        "files": files,
    }
    return source, report


def _expected_sidechain_state() -> tuple[int, dict[str, str]]:
    state = strict_json(Path("archive/chronicle-sidechain-zenodo-state.json"))
    record_id = int(state.get("record_id") or 0)
    if state.get("doi") != "10.5281/zenodo.22012616" or record_id != 22012616:
        raise SystemExit("sidechain DOI state changed unexpectedly")
    if state.get("remote_full_readback_sha256_verified") is not True:
        raise SystemExit("sidechain DOI is not marked remote-full-readback verified")
    expected = state.get("public_file_sha256")
    if not isinstance(expected, dict) or not expected:
        raise SystemExit("sidechain DOI public SHA-256 map missing")
    expected_map = {safe_segment(str(k)): str(v).lower() for k, v in expected.items()}
    if expected_map.get(SIDECHAIN_ARCHIVE_NAME) != SIDECHAIN_ARCHIVE_SHA256:
        raise SystemExit("sidechain archive SHA-256 state mismatch")
    return record_id, expected_map


def validate_sidechain_semantics() -> None:
    summary = strict_json(Path("nft-text-descriptions/crosschain-formation-summary.json"))
    generated = summary.get("generated_from")
    counts = summary.get("counts")
    verification = summary.get("verification")
    if not isinstance(generated, dict) or generated.get("zenodo_doi") != "10.5281/zenodo.22012616":
        raise SystemExit("cross-chain summary DOI binding mismatch")
    if not isinstance(counts, dict) or int(counts.get("all_sidechain_coordinates", -1)) != EXPECTED_SIDECHAIN_COORDINATES:
        raise SystemExit("cross-chain coordinate count mismatch")
    if not isinstance(verification, dict):
        raise SystemExit("cross-chain verification summary missing")
    expected = {
        "l2_records_pass": EXPECTED_SIDECHAIN_L2_PASS,
        "ipfs_roots_total": EXPECTED_SIDECHAIN_IPFS_ROOTS,
        "ipfs_roots_exact_verified": EXPECTED_SIDECHAIN_EXACT_CAR_ROOTS,
        "historical_payload_unresolved_roots": EXPECTED_SIDECHAIN_UNRESOLVED_ROOTS,
    }
    for key, value in expected.items():
        if int(verification.get(key, -1)) != value:
            raise SystemExit(f"cross-chain verification count mismatch: {key}")
    if verification.get("offline_verification_pass") is not True:
        raise SystemExit("cross-chain offline verification is not PASS")


def zenodo_sidechain_source(
    store: ObjectStore,
    scratch: Path,
) -> dict[str, Any]:
    validate_sidechain_semantics()
    record_id, expected_sha = _expected_sidechain_state()
    record = request_json(f"{ZENODO_API}/records/{record_id}")
    if not isinstance(record, dict) or int(record.get("id") or 0) != record_id:
        raise SystemExit("Zenodo sidechain public record mismatch")
    files_value = record.get("files")
    if not isinstance(files_value, list):
        raise SystemExit("Zenodo sidechain public files are not a list")
    if len(files_value) != len(expected_sha):
        raise SystemExit(
            f"Zenodo sidechain file count mismatch: {len(files_value)} != {len(expected_sha)}"
        )
    files: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in files_value:
        if not isinstance(item, dict):
            raise SystemExit("Zenodo sidechain file entry is not an object")
        key = safe_segment(str(item.get("key") or ""))
        if key in seen:
            raise SystemExit(f"duplicate Zenodo sidechain filename: {key}")
        seen.add(key)
        if key not in expected_sha:
            raise SystemExit(f"unexpected Zenodo sidechain public file: {key}")
        links = item.get("links")
        if not isinstance(links, dict):
            raise SystemExit(f"Zenodo file links missing: {key}")
        url = str(links.get("content") or links.get("self") or "")
        if not url:
            raise SystemExit(f"Zenodo file download URL missing: {key}")
        target = scratch / "zenodo-sidechain" / key
        log(f"download zenodo_sidechain record={record_id} file={key}")
        download(url, target)
        expected_size = int(item.get("size") or -1)
        if target.stat().st_size != expected_size:
            raise SystemExit(f"Zenodo sidechain size mismatch: {key}")
        checksum = str(item.get("checksum") or "")
        if checksum.startswith("md5:") and md5_file(target) != checksum.split(":", 1)[1].lower():
            raise SystemExit(f"Zenodo sidechain MD5 mismatch: {key}")
        sha = sha256_file(target)
        if sha != expected_sha[key]:
            raise SystemExit(f"Zenodo sidechain SHA-256 mismatch: {key}: {sha} != {expected_sha[key]}")
        object_sha, size, _ = store.ingest(target, {"kind": "zenodo_sidechain", "record_id": record_id})
        if object_sha != sha:
            raise SystemExit("object-store hash disagreement")
        files.append(
            {
                "logical_path": f"published-sidechain-doi/{record_id}/{key}",
                "object_sha256": object_sha,
                "bytes": size,
                "zenodo_checksum": checksum,
            }
        )
        target.unlink(missing_ok=True)
    if seen != set(expected_sha):
        raise SystemExit("Zenodo sidechain expected file set was not fully recovered")
    return {
        "source_id": f"zenodo-record:{record_id}",
        "kind": "published_polygon_base_sidechain_evidence",
        "doi": "10.5281/zenodo.22012616",
        "concept_doi": "10.5281/zenodo.22012615",
        "remote_full_readback_reverified_during_bundle_build": True,
        "sidechain_coordinates": EXPECTED_SIDECHAIN_COORDINATES,
        "l2_pass": EXPECTED_SIDECHAIN_L2_PASS,
        "ipfs_roots_total": EXPECTED_SIDECHAIN_IPFS_ROOTS,
        "exact_car_roots": EXPECTED_SIDECHAIN_EXACT_CAR_ROOTS,
        "historical_payload_unresolved_roots": EXPECTED_SIDECHAIN_UNRESOLVED_ROOTS,
        "files": sorted(files, key=lambda item: item["logical_path"]),
    }


def write_checksums(output: Path, objects: list[dict[str, Any]]) -> None:
    lines = []
    for item in objects:
        sha = str(item["sha256"])
        lines.append(f"{sha}  objects/sha256/{sha[:2]}/{sha}")
    (output / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", "thechurchofagi/trinity-accord"))
    parser.add_argument("--github-token", default=os.environ.get("GITHUB_TOKEN", ""))
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    repository = args.repository
    if repository != "thechurchofagi/trinity-accord":
        raise SystemExit(f"unexpected repository: {repository}")
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"output directory must be empty: {output}")
    output.mkdir(parents=True, exist_ok=True)

    source_sha = git_value("rev-parse", "HEAD")
    source_tree = git_value("rev-parse", "HEAD^{tree}")
    if len(source_sha) != 40 or len(source_tree) != 40:
        raise SystemExit("invalid Git source identity")
    log(f"source_sha={source_sha} source_tree={source_tree}")

    with tempfile.TemporaryDirectory(prefix="trinity-full-preservation-") as scratch_value:
        scratch = Path(scratch_value)
        store = ObjectStore(output)

        log("build safe current repository capsule")
        repository_source, cold_restore_report = current_repository_capsule_source(
            source_sha, store, scratch
        )

        log("enumerate and download every GitHub Release custom asset")
        release_source_list, release_stats = release_sources(
            repository, args.github_token, store, scratch
        )

        log("re-download and verify exact published Polygon/Base sidechain DOI files")
        sidechain_source = zenodo_sidechain_source(store, scratch)

        sources = [repository_source, *release_source_list, sidechain_source]
        objects = store.manifest_objects()
        manifest: dict[str, Any] = {
            "schema": SCHEMA,
            "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
            "source_repository": repository,
            "source_git_commit_sha": source_sha,
            "source_git_tree_oid": source_tree,
            "authority_boundary": {
                "canonical_interpretive_authority": "three_bitcoin_originals_only",
                "ethereum_chronicle_status": "175_entry_corpus_unchanged",
                "crosschain_record_status": "noncanonical_historical_evidence_and_formation_context_only",
                "non_amending_preservation": True,
            },
            "security_boundary": {
                "unsafe_full_parent_history_republished": False,
                "reason": (
                    "The established repository capsule intentionally excludes parent-history/tag blobs "
                    "that would republish a historical leaked credential. Current safe source and recovery state are preserved."
                ),
            },
            "known_limitations": {
                "sidechain_historical_payload_unresolved_roots": EXPECTED_SIDECHAIN_UNRESOLVED_ROOTS,
                "sidechain_exact_car_roots": EXPECTED_SIDECHAIN_EXACT_CAR_ROOTS,
                "sidechain_total_ipfs_roots": EXPECTED_SIDECHAIN_IPFS_ROOTS,
                "external_dataverse_copy_created": False,
                "external_dataverse_copy_note": (
                    "Bundle is staged and verified first. Harvard Dataverse upload requires a Dataverse account/API token; GitHub OAuth is not a Dataverse login method."
                ),
            },
            "coverage": {
                **release_stats,
                "current_repository_capsule_local_cold_restore": cold_restore_report.get("result"),
                "sidechain_doi_remote_full_readback_reverified": True,
                "unique_object_count": len(objects),
                "unique_object_bytes": store.unique_bytes,
                "logical_bytes_before_sha256_deduplication": store.logical_bytes,
                "logical_source_count": len(sources),
            },
            "sources": sources,
            "objects": objects,
        }
        manifest["bundle_identity_sha256"] = hashlib.sha256(
            verifier.canonical_identity_material(manifest)
        ).hexdigest()
        (output / "full-project-manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        write_checksums(output, objects)
        shutil.copyfile(
            "scripts/verify_full_project_preservation_bundle.py",
            output / "verify-and-restore-full-project.py",
        )

    report = verifier.verify_bundle(output)
    (output / "verification-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    log(
        "PASS "
        f"identity={report['bundle_identity_sha256']} "
        f"sources={report['source_count']} logical_files={report['logical_file_count']} "
        f"unique_objects={report['unique_object_count']} unique_bytes={report['unique_object_bytes']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
