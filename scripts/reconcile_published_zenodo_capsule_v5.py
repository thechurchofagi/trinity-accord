#!/usr/bin/env python3
"""Accept a published Zenodo capsule only through public-record self-proof.

A published preservation record must be judged against the bytes it actually
made public, not against a fresh Git pack produced by a later toolchain.  This
script performs no Zenodo writes.  It downloads one public record and its exact
eight-file payload without credentials, validates the capsule's own SHA-256
contract and rights boundary, requires the fixed production commit/tree/file
count, and writes repository state only for that self-consistent public record.

An independent workflow step then executes the downloaded record's own restore
program with ``--zenodo-record-id`` and verifies the recovered Git identities.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable

from preservation_capsule import (
    PACKAGE_TITLE,
    PUBLISHED_FILE_NAMES,
    file_inventory,
    verify_local_package,
)
from publish_preservation_capsule_to_zenodo import build_state, write_json


DEFAULT_API_BASE = "https://zenodo.org/api"
DEFAULT_WEB_BASE = "https://zenodo.org"
EXPECTED_RECORD_ID = 21739344
EXPECTED_CAPSULE_ID = "repository-484bdd7a8569"
EXPECTED_SOURCE_COMMIT = "484bdd7a85694ad53fe7e6e9dcea94d0dee5617e"
EXPECTED_TREE_OID = "47aa1f8b77f6f0c77237906b53929c08b665060f"
EXPECTED_RECOVERY_COMMIT = "83a3ba042e8786ed1ce1234c3991110c06bde71c"
EXPECTED_TRACKED_FILE_COUNT = 4253
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def strict_json_bytes(raw: bytes, source: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"public Zenodo JSON is invalid: {source}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"public Zenodo JSON is not an object: {source}")
    return value


def public_request_bytes(
    url: str,
    *,
    attempts: int = 8,
    accept: str = "application/octet-stream",
) -> bytes:
    diagnostics: list[str] = []
    for attempt in range(1, attempts + 1):
        request = urllib.request.Request(
            url,
            method="GET",
            headers={
                "Accept": accept,
                "User-Agent": "trinity-repository-preservation-public-proof/1.0",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            diagnostics.append(f"HTTP {exc.code} {url}: {detail[:240]}")
        except (urllib.error.URLError, OSError) as exc:
            diagnostics.append(f"{url}: {exc}")
        if attempt < attempts:
            time.sleep(float(min(attempt * 2, 10)))
    raise SystemExit(
        "public Zenodo request failed after bounded retries: "
        + " | ".join(diagnostics[-8:])
    )


def public_record(record_id: int, api_base: str) -> dict[str, Any]:
    url = f"{api_base.rstrip('/')}/records/{record_id}"
    value = strict_json_bytes(
        public_request_bytes(url, accept="application/json"), url
    )
    try:
        observed_id = int(value.get("id"))
    except (TypeError, ValueError) as exc:
        raise SystemExit("public Zenodo record is missing its numeric id") from exc
    if observed_id != record_id:
        raise SystemExit(
            f"public Zenodo record id mismatch: observed={observed_id} expected={record_id}"
        )
    return value


def metadata(record: dict[str, Any]) -> dict[str, Any]:
    value = record.get("metadata")
    return value if isinstance(value, dict) else {}


def nested_identifier(value: Any, *path: str) -> str:
    current = value
    for key in path:
        if not isinstance(current, dict):
            return ""
        current = current.get(key)
    return str(current or "")


def record_doi(record: dict[str, Any]) -> str:
    candidates = (
        str(record.get("doi") or ""),
        str(metadata(record).get("doi") or ""),
        nested_identifier(record, "pids", "doi", "identifier"),
    )
    return next((value for value in candidates if value), "")


def concept_doi(record: dict[str, Any]) -> str:
    candidates = (
        str(record.get("conceptdoi") or ""),
        str(metadata(record).get("conceptdoi") or ""),
        nested_identifier(record, "parent", "pids", "doi", "identifier"),
    )
    return next((value for value in candidates if value), "")


def concept_record_id(record: dict[str, Any]) -> int | None:
    candidates = (
        record.get("conceptrecid"),
        nested_identifier(record, "parent", "id"),
    )
    for value in candidates:
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return None


def public_file_items(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = record.get("files")
    result: dict[str, dict[str, Any]] = {}
    if isinstance(raw, list):
        iterable: Iterable[tuple[str, Any]] = (
            (str(item.get("key") or item.get("filename") or ""), item)
            for item in raw
            if isinstance(item, dict)
        )
    elif isinstance(raw, dict):
        entries = raw.get("entries")
        if isinstance(entries, dict):
            iterable = (
                (str(key), item)
                for key, item in entries.items()
                if isinstance(item, dict)
            )
        elif isinstance(entries, list):
            iterable = (
                (str(item.get("key") or item.get("filename") or ""), item)
                for item in entries
                if isinstance(item, dict)
            )
        else:
            iterable = ()
    else:
        iterable = ()

    for fallback_name, item in iterable:
        name = str(item.get("key") or item.get("filename") or fallback_name)
        if not name:
            continue
        if name in result:
            raise SystemExit(f"duplicate public Zenodo file name: {name}")
        normalized = dict(item)
        normalized.setdefault("key", name)
        result[name] = normalized

    expected = set(PUBLISHED_FILE_NAMES)
    if set(result) != expected:
        raise SystemExit(
            "public Zenodo preservation file set mismatch: "
            f"missing={sorted(expected - set(result))} "
            f"unexpected={sorted(set(result) - expected)}"
        )
    return result


def item_size(item: dict[str, Any]) -> int | None:
    for key in ("size", "filesize"):
        try:
            return int(item.get(key))
        except (TypeError, ValueError):
            continue
    return None


def item_checksum(item: dict[str, Any]) -> str:
    value = item.get("checksum")
    if isinstance(value, str):
        return value.lower()
    if isinstance(value, dict):
        for key in ("md5", "sha256"):
            candidate = value.get(key)
            if candidate:
                return f"{key}:{str(candidate).lower()}"
    return ""


def download_candidates(
    record_id: int,
    name: str,
    item: dict[str, Any],
    web_base: str,
    api_base: str,
) -> list[str]:
    links = item.get("links")
    link_map = links if isinstance(links, dict) else {}
    file_id = str(item.get("id") or "")
    quoted_name = urllib.parse.quote(name)
    candidates = [
        str(link_map.get("content") or ""),
        str(link_map.get("download") or ""),
        str(link_map.get("self") or ""),
        f"{web_base.rstrip('/')}/records/{record_id}/files/{quoted_name}?download=1",
    ]
    if file_id:
        candidates.append(
            f"{api_base.rstrip('/')}/records/{record_id}/files/{urllib.parse.quote(file_id)}/content"
        )
    result: list[str] = []
    seen: set[str] = set()
    for value in candidates:
        if value and value not in seen:
            result.append(value)
            seen.add(value)
    return result


def download_one_file(
    record_id: int,
    name: str,
    item: dict[str, Any],
    destination: Path,
    web_base: str,
    api_base: str,
) -> dict[str, Any]:
    expected_size = item_size(item)
    checksum = item_checksum(item)
    diagnostics: list[str] = []
    for url in download_candidates(record_id, name, item, web_base, api_base):
        try:
            raw = public_request_bytes(url, attempts=4)
        except SystemExit as exc:
            diagnostics.append(str(exc))
            continue
        if expected_size is not None and len(raw) != expected_size:
            diagnostics.append(
                f"{url}: bytes={len(raw)} expected_record_bytes={expected_size}"
            )
            continue
        digest_sha256 = hashlib.sha256(raw).hexdigest()
        digest_md5 = hashlib.md5(raw, usedforsecurity=False).hexdigest()
        if checksum:
            algorithm, _, expected = checksum.partition(":")
            if algorithm == "md5" and digest_md5 != expected:
                diagnostics.append(f"{url}: public-record MD5 mismatch")
                continue
            if algorithm == "sha256" and digest_sha256 != expected:
                diagnostics.append(f"{url}: public-record SHA-256 mismatch")
                continue
        destination.write_bytes(raw)
        return {
            "bytes": len(raw),
            "sha256": digest_sha256,
            "md5": digest_md5,
            "public_url_used": url,
            "record_checksum": checksum or None,
        }
    raise SystemExit(
        f"public Zenodo file could not be downloaded exactly: {name}: "
        + " | ".join(diagnostics[-8:])
    )


def normalized_published_record(
    raw_record: dict[str, Any],
    package: dict[str, Any],
    record_id: int,
) -> dict[str, Any]:
    doi = record_doi(raw_record)
    if not doi:
        raise SystemExit("public Zenodo record lacks a registered DOI")
    raw_metadata = dict(metadata(raw_record))
    if raw_metadata.get("title") != PACKAGE_TITLE:
        raise SystemExit("public Zenodo record title is not the preservation series")
    if str(raw_metadata.get("version") or "") != package["capsule_id"]:
        raise SystemExit("public Zenodo record version does not match its capsule")
    normalized = dict(raw_record)
    normalized.update(
        {
            "id": record_id,
            "record_id": record_id,
            "submitted": True,
            "state": "done",
            "doi": doi,
            "conceptdoi": concept_doi(raw_record),
            "conceptrecid": concept_record_id(raw_record),
            "metadata": raw_metadata,
            "links": {
                **(
                    raw_record.get("links")
                    if isinstance(raw_record.get("links"), dict)
                    else {}
                ),
                "doi": f"https://doi.org/{doi}",
            },
        }
    )
    return normalized


def verify_fixed_preservation_target(package: dict[str, Any]) -> None:
    if package["capsule_id"] != EXPECTED_CAPSULE_ID:
        raise SystemExit(f"unexpected published capsule id: {package['capsule_id']}")
    if package["git_commit_sha"] != EXPECTED_SOURCE_COMMIT:
        raise SystemExit("published capsule source commit is not the authorized target")
    if package["git_tree_oid"] != EXPECTED_TREE_OID:
        raise SystemExit("published capsule tree is not the authorized target")
    if package["tracked_file_count"] != EXPECTED_TRACKED_FILE_COUNT:
        raise SystemExit("published capsule tracked-file count is not 4,253")
    git = package["manifest"].get("git")
    recovery_commit = str(git.get("recovery_commit_sha") or "") if isinstance(git, dict) else ""
    if recovery_commit != EXPECTED_RECOVERY_COMMIT:
        raise SystemExit("published capsule recovery commit is unexpected")
    identity = str(package["package_identity_sha256"])
    if SHA256_RE.fullmatch(identity) is None:
        raise SystemExit("published capsule package identity is not canonical SHA-256")


def reconcile(
    *,
    record_id: int,
    api_base: str,
    web_base: str,
    download_dir: Path,
    state_path: Path,
    observation_path: Path,
) -> dict[str, Any]:
    if record_id != EXPECTED_RECORD_ID:
        raise SystemExit(f"V5 is restricted to record {EXPECTED_RECORD_ID}")
    if download_dir.exists() and any(download_dir.iterdir()):
        raise SystemExit(f"public capsule download directory is not empty: {download_dir}")
    download_dir.mkdir(parents=True, exist_ok=True)

    raw_record = public_record(record_id, api_base)
    remote = public_file_items(raw_record)
    downloads: dict[str, dict[str, Any]] = {}
    for name in PUBLISHED_FILE_NAMES:
        downloads[name] = download_one_file(
            record_id,
            name,
            remote[name],
            download_dir / name,
            web_base,
            api_base,
        )

    package = verify_local_package(download_dir)
    verify_fixed_preservation_target(package)
    inventory = file_inventory(download_dir)
    for name in PUBLISHED_FILE_NAMES:
        if downloads[name]["bytes"] != inventory[name]["bytes"]:
            raise SystemExit(f"download/inventory byte mismatch: {name}")
        if downloads[name]["sha256"] != inventory[name]["sha256"]:
            raise SystemExit(f"download/inventory SHA-256 mismatch: {name}")

    published = normalized_published_record(raw_record, package, record_id)
    old_state = (
        json.loads(state_path.read_text(encoding="utf-8"))
        if state_path.is_file()
        else {}
    )
    if not isinstance(old_state, dict):
        raise SystemExit("existing Zenodo state is not an object")
    next_state = build_state(
        published,
        package,
        api_base,
        [published],
        old_state,
    )

    observation = {
        "schema": "trinityaccord.repository-preservation-public-record-observation.v1",
        "observed_without_credentials": True,
        "record_id": record_id,
        "doi": next_state["latest_doi"],
        "doi_url": next_state["latest_doi_url"],
        "concept_record_id": next_state.get("concept_record_id"),
        "concept_doi": next_state.get("concept_doi"),
        "capsule_id": package["capsule_id"],
        "package_identity_sha256": package["package_identity_sha256"],
        "git_commit_sha": package["git_commit_sha"],
        "git_tree_oid": package["git_tree_oid"],
        "recovery_commit_sha": EXPECTED_RECOVERY_COMMIT,
        "tracked_file_count": package["tracked_file_count"],
        "rights_boundary_schema": next_state["rights_boundary_schema"],
        "external_large_binary_annex_embedded": False,
        "public_files": inventory,
        "public_download_evidence": downloads,
        "capsule_self_verification": "passed",
        "independent_public_restore_required_before_state_commit": True,
    }
    write_json(observation_path, observation)
    write_json(state_path, next_state)

    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"record_id={record_id}\n")
            handle.write(f"doi={next_state['latest_doi']}\n")
            handle.write(f"concept_doi={next_state.get('concept_doi') or ''}\n")
            handle.write(
                f"package_identity_sha256={package['package_identity_sha256']}\n"
            )
    return next_state


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-id", type=int, default=EXPECTED_RECORD_ID)
    parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    parser.add_argument("--web-base", default=DEFAULT_WEB_BASE)
    parser.add_argument("--download-dir", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--observation", required=True)
    args = parser.parse_args()
    state = reconcile(
        record_id=args.record_id,
        api_base=args.api_base,
        web_base=args.web_base,
        download_dir=Path(args.download_dir).resolve(),
        state_path=Path(args.state).resolve(),
        observation_path=Path(args.observation).resolve(),
    )
    print(json.dumps(state, ensure_ascii=False, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        raise SystemExit(130)
