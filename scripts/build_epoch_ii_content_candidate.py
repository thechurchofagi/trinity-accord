#!/usr/bin/env python3
"""Build and cold-verify the scoped Preservation Epoch II research corpus candidate.

The candidate verifies public payload bytes already hosted by the project.  It does
not publish, amend, submit or mutate any Harvard/Zenodo record.  Large operational
Bitcoin checkpoints, superseded museum builds and the independently preserved
Finality payload remain distributed dependencies with explicit identities.
"""
from __future__ import annotations

import argparse
import base64
import concurrent.futures
import datetime as dt
import hashlib
import io
import json
import os
import pathlib
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
from collections import defaultdict
from typing import Any, BinaryIO

SCHEMA = "trinityaccord.preservation-epoch-ii-content-candidate.v1"
SELECTED_FAMILIES = {
    "evidence_or_content",
    "encrypted_witness_ciphertext",
    "presentation_current",
    "research_context",
}
FINALITY_RECEIPT_MAX_BYTES = 5_000_000
MAX_ARCHIVE_MEMBER_BYTES = 2 * 1024 * 1024 * 1024
MAX_NESTED_ARCHIVE_BYTES = 1024 * 1024 * 1024
HEX64 = set("0123456789abcdef")


def log(message: str) -> None:
    print(f"[epoch-ii-content] {message}", flush=True)


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stream_identity(handle: BinaryIO) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
        digest.update(chunk)
        size += len(chunk)
        if size > MAX_ARCHIVE_MEMBER_BYTES:
            raise SystemExit(f"archive member exceeds safety limit: {size}")
    return digest.hexdigest(), size


def object_path(store: pathlib.Path, sha256: str) -> pathlib.Path:
    value = sha256.lower()
    if len(value) != 64 or any(ch not in HEX64 for ch in value):
        raise SystemExit(f"invalid SHA-256: {sha256!r}")
    return store / "objects" / "sha256" / value[:2] / value


def safe_member(name: str) -> str:
    value = name.replace("\\", "/")
    path = pathlib.PurePosixPath(value)
    if not value or value.startswith("/") or ".." in path.parts or "\x00" in value:
        raise SystemExit(f"unsafe archive member: {name!r}")
    return value


def selected_release_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected = []
    for row in rows:
        family = row.get("family")
        if family in SELECTED_FAMILIES:
            selected.append(row)
        elif family == "sidechain_finality" and int(row.get("size_bytes") or 0) < FINALITY_RECEIPT_MAX_BYTES:
            selected.append(row)
    return selected


def full_finality_dependency(rows: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [row for row in rows if row.get("family") == "sidechain_finality"]
    objects = validate_release_rows(selected)
    return {
        "role": "noncanonical_polygon_base_finality_dependency",
        "institutional_copy_requirement": "copy_every_public_file_byte_for_byte",
        "logical_assets": len(selected),
        "logical_bytes": sum(int(row["size_bytes"]) for row in selected),
        "unique_objects": len(objects),
        "unique_bytes": sum(int(row["size_bytes"]) for row in objects.values()),
        "release_tags": sorted({str(row["release_tag"]) for row in selected}),
        "zenodo_version_doi": "10.5281/zenodo.22710291",
        "files": [
            {
                "filename": str(row["filename"]),
                "bytes": int(row["size_bytes"]),
                "sha256": str(row["declared_sha256"]),
                "release_tag": str(row["release_tag"]),
                "source_locator": str(row["source_locator"]),
            }
            for row in sorted(selected, key=lambda item: (str(item["release_tag"]), str(item["filename"])))
        ],
    }


def validate_release_rows(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    objects: dict[str, dict[str, Any]] = {}
    logical: set[tuple[int, str]] = set()
    for index, row in enumerate(rows):
        sha = str(row.get("declared_sha256") or "").lower()
        size = int(row.get("size_bytes") or -1)
        url = str(row.get("source_locator") or "")
        key = (int(row.get("release_id") or 0), str(row.get("filename") or ""))
        if key in logical:
            raise SystemExit(f"duplicate selected Release identity: {key}")
        logical.add(key)
        if len(sha) != 64 or any(ch not in HEX64 for ch in sha) or size < 0:
            raise SystemExit(f"invalid selected Release row {index}")
        if not url.startswith("https://github.com/thechurchofagi/trinity-accord/releases/download/"):
            raise SystemExit(f"unapproved selected Release URL: {url}")
        old = objects.setdefault(sha, row)
        if int(old["size_bytes"]) != size:
            raise SystemExit(f"same digest has conflicting sizes: {sha}")
    return objects


def download_object(store: pathlib.Path, row: dict[str, Any]) -> dict[str, Any]:
    sha = str(row["declared_sha256"]).lower()
    expected_size = int(row["size_bytes"])
    target = object_path(store, sha)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_file() and target.stat().st_size == expected_size and sha256_file(target) == sha:
        return {"sha256": sha, "bytes": expected_size, "result": "verified_cached"}
    target.unlink(missing_ok=True)
    last: Exception | None = None
    for attempt in range(1, 6):
        part = target.with_name(target.name + ".part")
        part.unlink(missing_ok=True)
        try:
            request = urllib.request.Request(
                str(row["source_locator"]),
                headers={"User-Agent": "trinity-epoch-ii-content/1.0"},
            )
            digest = hashlib.sha256()
            size = 0
            with urllib.request.urlopen(request, timeout=900) as response, part.open("wb") as handle:
                effective = response.geturl()
                if not (
                    effective.startswith("https://github.com/")
                    or effective.startswith("https://release-assets.githubusercontent.com/")
                ):
                    raise SystemExit(f"unexpected Release redirect host: {effective}")
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    handle.write(chunk)
                    digest.update(chunk)
                    size += len(chunk)
                    if size > expected_size:
                        raise SystemExit(f"Release object exceeded declared size: {sha}")
            if size != expected_size or digest.hexdigest() != sha:
                raise SystemExit(
                    f"Release object identity mismatch {sha}: bytes={size}, digest={digest.hexdigest()}"
                )
            os.replace(part, target)
            return {"sha256": sha, "bytes": size, "result": "downloaded_and_verified"}
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
            last = exc
            part.unlink(missing_ok=True)
            if attempt < 5:
                time.sleep(min(2**attempt, 20))
    raise SystemExit(f"unable to download selected object {sha}: {last}")


def verify_or_download_objects(
    store: pathlib.Path,
    objects: dict[str, dict[str, Any]],
    download: bool,
    workers: int,
) -> list[dict[str, Any]]:
    def one(item: tuple[str, dict[str, Any]]) -> dict[str, Any]:
        sha, row = item
        path = object_path(store, sha)
        if download:
            return download_object(store, row)
        if not path.is_file():
            raise SystemExit(f"selected object absent from cache: {sha}")
        if path.stat().st_size != int(row["size_bytes"]) or sha256_file(path) != sha:
            raise SystemExit(f"selected cached object identity mismatch: {sha}")
        return {"sha256": sha, "bytes": path.stat().st_size, "result": "verified_cached"}

    results: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(one, item) for item in sorted(objects.items())]
        for index, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            value = future.result()
            results.append(value)
            log(f"objects {index}/{len(futures)} verified bytes={value['bytes']} sha256={value['sha256'][:12]}")
    return sorted(results, key=lambda item: item["sha256"])


def archive_kind(name: str) -> str | None:
    lower = name.lower()
    if lower.endswith(".zip"):
        return "zip"
    if lower.endswith((".tar", ".tar.gz", ".tgz")):
        return "tar"
    return None


def scan_archive_file(
    path: pathlib.Path,
    logical: str,
    rows: list[dict[str, Any]],
    nested_dir: pathlib.Path,
    depth: int = 0,
) -> None:
    kind = archive_kind(logical)
    if kind is None or depth > 2:
        return
    seen: set[str] = set()
    if kind == "zip":
        with zipfile.ZipFile(path) as archive:
            for info in archive.infolist():
                name = safe_member(info.filename)
                if name in seen:
                    raise SystemExit(f"duplicate ZIP member: {logical}!{name}")
                seen.add(name)
                mode = (info.external_attr >> 16) & 0xFFFF
                if info.is_dir():
                    continue
                if stat.S_ISLNK(mode):
                    raise SystemExit(f"ZIP symlink rejected: {logical}!{name}")
                with archive.open(info) as handle:
                    sha, size = stream_identity(handle)
                member_logical = f"{logical}!{name}"
                rows.append({"container": logical, "member_path": name, "logical_path": member_logical, "sha256": sha, "bytes": size, "depth": depth})
                if archive_kind(name) and size <= MAX_NESTED_ARCHIVE_BYTES:
                    nested = nested_dir / hashlib.sha256(member_logical.encode()).hexdigest()
                    with archive.open(info) as source, nested.open("wb") as target:
                        shutil.copyfileobj(source, target, 1024 * 1024)
                    scan_archive_file(nested, member_logical, rows, nested_dir, depth + 1)
                    nested.unlink(missing_ok=True)
    else:
        with tarfile.open(path, "r:*") as archive:
            for info in archive:
                name = safe_member(info.name)
                if name in seen:
                    raise SystemExit(f"duplicate TAR member: {logical}!{name}")
                seen.add(name)
                if info.isdir():
                    continue
                if not info.isfile():
                    raise SystemExit(f"non-regular TAR member rejected: {logical}!{name}")
                if info.size > MAX_ARCHIVE_MEMBER_BYTES:
                    raise SystemExit(f"TAR member exceeds safety limit: {logical}!{name}")
                handle = archive.extractfile(info)
                if handle is None:
                    raise SystemExit(f"unable to read TAR member: {logical}!{name}")
                with handle:
                    sha, size = stream_identity(handle)
                if size != info.size:
                    raise SystemExit(f"TAR member size mismatch: {logical}!{name}")
                member_logical = f"{logical}!{name}"
                rows.append({"container": logical, "member_path": name, "logical_path": member_logical, "sha256": sha, "bytes": size, "depth": depth})
                if archive_kind(name) and size <= MAX_NESTED_ARCHIVE_BYTES:
                    nested = nested_dir / hashlib.sha256(member_logical.encode()).hexdigest()
                    handle = archive.extractfile(info)
                    if handle is None:
                        raise SystemExit(f"unable to reopen nested TAR member: {logical}!{name}")
                    with handle, nested.open("wb") as target:
                        shutil.copyfileobj(handle, target, 1024 * 1024)
                    scan_archive_file(nested, member_logical, rows, nested_dir, depth + 1)
                    nested.unlink(missing_ok=True)


def scan_selected_archives(
    store: pathlib.Path, selected: list[dict[str, Any]], work: pathlib.Path
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    scanned: set[str] = set()
    nested = work / "nested"
    nested.mkdir(parents=True, exist_ok=True)
    for row in selected:
        sha = str(row["declared_sha256"])
        if sha in scanned or archive_kind(str(row["filename"])) is None:
            continue
        scanned.add(sha)
        logical = f"github-release/{row['release_id']}-{row['release_tag']}/{row['filename']}"
        log(f"scan archive {logical}")
        scan_archive_file(object_path(store, sha), logical, rows, nested)
    return rows


def b58encode(value: bytes) -> str:
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    number = int.from_bytes(value, "big")
    out = ""
    while number:
        number, rem = divmod(number, 58)
        out = alphabet[rem] + out
    zeros = len(value) - len(value.lstrip(b"\0"))
    return "1" * zeros + (out or "")


def read_varint(data: bytes, pos: int) -> tuple[int, int]:
    value = shift = 0
    for _ in range(10):
        if pos >= len(data):
            raise ValueError("truncated varint")
        byte = data[pos]
        pos += 1
        value |= (byte & 0x7F) << shift
        if byte < 0x80:
            return value, pos
        shift += 7
    raise ValueError("overlong varint")


def cbor_length(data: bytes, pos: int, additional: int) -> tuple[int, int]:
    if additional < 24:
        return additional, pos
    sizes = {24: 1, 25: 2, 26: 4, 27: 8}
    if additional not in sizes or pos + sizes[additional] > len(data):
        raise ValueError("unsupported or truncated CBOR length")
    size = sizes[additional]
    return int.from_bytes(data[pos : pos + size], "big"), pos + size


def cbor(data: bytes, pos: int = 0) -> tuple[Any, int]:
    if pos >= len(data):
        raise ValueError("truncated CBOR")
    initial = data[pos]
    pos += 1
    major, additional = initial >> 5, initial & 31
    length, pos = cbor_length(data, pos, additional)
    if major in {0, 1}:
        return (length if major == 0 else -1 - length), pos
    if major in {2, 3}:
        end = pos + length
        if end > len(data):
            raise ValueError("truncated CBOR string")
        raw = data[pos:end]
        return (raw if major == 2 else raw.decode("utf-8")), end
    if major == 4:
        result = []
        for _ in range(length):
            item, pos = cbor(data, pos)
            result.append(item)
        return result, pos
    if major == 5:
        result = {}
        for _ in range(length):
            key, pos = cbor(data, pos)
            value, pos = cbor(data, pos)
            result[key] = value
        return result, pos
    if major == 6:
        value, pos = cbor(data, pos)
        return ("tag", length, value), pos
    raise ValueError(f"unsupported CBOR major type: {major}")


def car_root_cid(data: bytes) -> str:
    header_size, pos = read_varint(data, 0)
    end = pos + header_size
    if header_size <= 0 or end > len(data):
        raise ValueError("invalid CAR header size")
    header, consumed = cbor(data[pos:end])
    if consumed != header_size or not isinstance(header, dict) or header.get("version") != 1:
        raise ValueError("invalid CAR v1 header")
    roots = header.get("roots")
    if not isinstance(roots, list) or len(roots) != 1:
        raise ValueError("CAR must declare exactly one root")
    root = roots[0]
    if not (isinstance(root, tuple) and len(root) == 3 and root[:2] == ("tag", 42) and isinstance(root[2], bytes)):
        raise ValueError("CAR root is not DAG-CBOR link tag 42")
    binary = root[2]
    if not binary or binary[0] != 0:
        raise ValueError("CAR CID tag payload lacks identity prefix")
    cid = binary[1:]
    if cid.startswith(b"\x01"):
        return "b" + base64.b32encode(cid).decode("ascii").lower().rstrip("=")
    return b58encode(cid)


def extract_nft_cars(
    store: pathlib.Path,
    selected: list[dict[str, Any]],
    expected_manifest: dict[str, Any],
) -> dict[str, Any]:
    parts = [row for row in selected if row.get("release_tag") == "nft-backup-v1" and str(row.get("filename", "")).startswith("nft-cars-part")]
    expected = {str(item["sha256"]).lower(): item for item in expected_manifest["files"]}
    if len(parts) != 9 or len(expected) != 434:
        raise SystemExit(f"NFT backup boundary changed: parts={len(parts)} expected={len(expected)}")
    found: dict[str, dict[str, Any]] = {}
    metadata_cid_pass = media_cid_pass = 0
    errors: list[dict[str, Any]] = []
    media_cid_audit_warnings: list[dict[str, Any]] = []
    for row in sorted(parts, key=lambda item: str(item["filename"])):
        with tarfile.open(object_path(store, str(row["declared_sha256"])), "r:gz") as archive:
            seen: set[str] = set()
            for info in archive:
                name = safe_member(info.name)
                if name in seen:
                    raise SystemExit(f"duplicate NFT TAR member: {row['filename']}!{name}")
                seen.add(name)
                if not info.isfile() or not name.endswith(".car"):
                    raise SystemExit(f"unexpected NFT TAR member: {row['filename']}!{name}")
                handle = archive.extractfile(info)
                if handle is None:
                    raise SystemExit(f"unreadable NFT CAR: {name}")
                with handle:
                    data = handle.read(MAX_ARCHIVE_MEMBER_BYTES + 1)
                if len(data) > MAX_ARCHIVE_MEMBER_BYTES:
                    raise SystemExit(f"NFT CAR exceeds safety limit: {name}")
                sha = hashlib.sha256(data).hexdigest()
                item = expected.get(sha)
                if item is None or int(item["size"]) != len(data):
                    errors.append({"member": name, "error": "hash_or_size_not_in_expected_manifest", "sha256": sha, "bytes": len(data)})
                    continue
                if sha in found:
                    errors.append({"member": name, "error": "duplicate_expected_car", "sha256": sha})
                    continue
                root = car_root_cid(data)
                cid_match = root == item["cid"]
                if item["role"] == "metadata":
                    metadata_cid_pass += int(cid_match)
                    if not cid_match:
                        errors.append({"member": name, "error": "metadata_root_cid_mismatch", "expected": item["cid"], "actual": root})
                else:
                    media_cid_pass += int(cid_match)
                    if not cid_match:
                        # The manifest's media CID can name the parent UnixFS DAG
                        # while its archived CAR is rooted at the selected leaf.
                        # Preserve the difference for audit; only metadata roots
                        # are a strict identity gate, matching the established
                        # release verifier's published boundary.
                        media_cid_audit_warnings.append({"member": name, "warning": "media_car_root_differs_from_manifest_parent_or_root_cid", "expected": item["cid"], "actual": root})
                found[sha] = {"archive": row["filename"], "member": name, "sha256": sha, "bytes": len(data), "role": item["role"], "root_cid": root, "expected_root_cid": item["cid"], "root_cid_match": cid_match, "txid": item["txid"], "contract": item["contract"], "token_id": item["token_id"]}
    missing = sorted(set(expected) - set(found))
    status = "pass" if not errors and not missing and len(found) == 434 else "fail"
    return {"schema": "trinityaccord.epoch-ii-nft-car-verification.v1", "status": status, "verification_scope": "container_sha256_size_and_metadata_root_cid_strict_media_root_audit", "full_dag_check_enabled": False, "expected_cars": 434, "verified_cars": len(found), "metadata_cid_pass": metadata_cid_pass, "media_cid_pass": media_cid_pass, "media_cid_audit_warning_count": len(media_cid_audit_warnings), "media_cid_audit_warnings": media_cid_audit_warnings, "missing_sha256": missing, "errors": errors, "files": sorted(found.values(), key=lambda item: item["sha256"])}


def physical_crosscheck(physical: dict[str, Any], members: list[dict[str, Any]]) -> dict[str, Any]:
    by_identity = defaultdict(list)
    for member in members:
        by_identity[(member["sha256"], int(member["bytes"]))].append(member["logical_path"])
    files = []
    for row in physical["files"]:
        matches = by_identity[(row["declared_sha256"], int(row["size_bytes"]))]
        files.append({**row, "archive_member_matches": matches, "verification": "archive_member_bytes_match" if matches else row.get("verification", "not_run")})
    verified = sum(row["verification"] == "archive_member_bytes_match" or row.get("capture") == "content_bytes_verified" for row in files)
    return {"schema": "trinityaccord.epoch-ii-physical-payload-crosscheck.v1", "status": "pass" if verified == len(files) else "incomplete", "public_files": len(files), "verified_from_selected_archives_or_prior_capture": verified, "unmatched": len(files) - verified, "files": files}


def historical_crosscheck(
    historical: dict[str, Any],
    members: list[dict[str, Any]],
    current_nft_cids: set[str] | None = None,
) -> dict[str, Any]:
    current_nft_cids = current_nft_cids or set()
    by_identity = defaultdict(list)
    for member in members:
        by_identity[(member["sha256"], int(member["bytes"]))].append(member["logical_path"])
    rows = []
    counts: defaultdict[str, int] = defaultdict(int)
    for row in historical["rows"]:
        matches = by_identity[(row["declared_sha256"], int(row["size_bytes"]))]
        path = str(row.get("historical_path") or "").replace("\\", "/")
        if row.get("capture") == "source_bytes_match":
            status = "source_bytes_match"
        elif matches:
            status = "selected_archive_member_bytes_match"
        elif row.get("matching_public_asset_metadata"):
            status = "public_asset_locator_only"
        elif row.get("historical_nonpublic_label") or any(
            label in path for label in ("不公开", "未公开")
        ):
            status = "historical_nonpublic_label_commitment"
        else:
            name = path.rsplit("/", 1)[-1]
            cid_match = re.search(r"(bafy[a-z0-9]+|Qm[A-Za-z0-9]+)", name)
            cid = cid_match.group(1) if cid_match else None
            if "/cars/media/" in path and cid in current_nft_cids:
                status = "legacy_parent_car_commitment_current_leaf_cars_verified"
            elif "/tools/" in path:
                status = "historical_operational_tool_commitment"
            elif any(label in path for label in ("星月见证", "气泡星座")):
                status = "historical_witness_plaintext_or_archive_commitment_public_ciphertext_preserved"
            else:
                status = "public_historical_commitment_unresolved"
        counts[status] += 1
        rows.append({**row, "selected_archive_member_matches": matches, "content_resolution": status})
    return {
        "schema": "trinityaccord.epoch-ii-historical-digest-expansion.v1",
        "boundary": (
            "Only exact hash-and-size member matches are byte recovery. Semantic/status mappings preserve "
            "the identity of unavailable legacy containers and do not prove historical bytes, full DAG "
            "completeness, or by themselves decide current publication scope."
        ),
        "summary": dict(sorted(counts.items())),
        "rows": rows,
    }


def historical_publication_scope(
    historical: dict[str, Any], decision: dict[str, Any]
) -> dict[str, Any]:
    """Bind the owner's publication decision to the exact affected inventory rows.

    Historical path labels remain provenance facts. They are not silently erased,
    but the later human decision can supersede them for publication. This function
    never promotes commitment-only rows into recovered bytes.
    """
    affected_statuses = {
        "historical_nonpublic_label_commitment",
        "public_historical_commitment_unresolved",
    }
    rows = [
        row for row in historical["rows"]
        if row["content_resolution"] in affected_statuses
    ]
    canonical_rows = sorted(
        [
            {
                "declared_sha256": str(row["declared_sha256"]),
                "historical_path": str(row["historical_path"]),
                "size_bytes": int(row["size_bytes"]),
            }
            for row in rows
        ],
        key=lambda row: (
            row["declared_sha256"], row["size_bytes"], row["historical_path"]
        ),
    )
    encoded = json.dumps(
        canonical_rows,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    actual_digest = hashlib.sha256(encoded).hexdigest()
    binding = decision["bound_historical_rows"]
    identities = {
        (row["declared_sha256"], int(row["size_bytes"])) for row in rows
    }
    checks = {
        "combined_rows": len(rows),
        "distinct_sha256_and_size_identities": len(identities),
        "logical_bytes_including_duplicate_commitments": sum(
            int(row["size_bytes"]) for row in rows
        ),
        "canonical_rows_sha256": actual_digest,
    }
    mismatches = {
        key: {"expected": binding.get(key), "actual": value}
        for key, value in checks.items()
        if binding.get(key) != value
    }
    if mismatches:
        raise SystemExit(f"historical publication decision binding mismatch: {mismatches}")
    if decision.get("decision", {}).get("public_access_authorized") is not True:
        raise SystemExit("historical publication decision does not authorize public access")
    resolved_rows = [
        {
            "historical_path": row["historical_path"],
            "size_bytes": int(row["size_bytes"]),
            "declared_sha256": row["declared_sha256"],
            "historical_resolution": row["content_resolution"],
            "current_publication_scope": "public_if_exact_bytes_are_recovered",
            "current_byte_status": "commitment_only_exact_bytes_not_recovered",
        }
        for row in rows
    ]
    return {
        "schema": "trinityaccord.epoch-ii-historical-publication-scope-resolution.v1",
        "status": "pass",
        "decision_record": "preservation/epoch-ii-publication-scope-decision-20260912.json",
        "decision_binding": checks,
        "historical_labels_preserved_as_provenance": True,
        "human_scope_decision_complete": True,
        "public_if_exact_bytes_are_recovered_rows": len(rows),
        "distinct_commitment_identities": len(identities),
        "currently_uploadable_rows": 0,
        "commitment_only_exact_bytes_not_recovered_rows": len(rows),
        "privacy_excluded_rows": 0,
        "unresolved_scope_decisions": 0,
        "exact_byte_inventory_complete": False,
        "project_content_gap_created_by_unavailable_legacy_wrappers": 0,
        "rows": resolved_rows,
    }


def verify_encrypted_witness_archives(
    repo: pathlib.Path, selected: list[dict[str, Any]]
) -> dict[str, Any]:
    """Verify the complete public computationally delayed witness layer.

    The archival object is the ciphertext plus recovery/verification metadata.
    Plaintext and unlock material are intentionally absent; that is the delayed-
    access design, not an unresolved privacy review.
    """
    index = load_json(repo / "archive" / "encrypted-witness-archives.v1.json")
    selected_rows = [
        row for row in selected if row.get("family") == "encrypted_witness_ciphertext"
    ]
    by_tag: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in selected_rows:
        by_tag[str(row["release_tag"])].append(row)
    archive_reports = []
    errors = []
    for key, item in sorted(index["archives"].items()):
        tag = str(item["github_release_tag"])
        state = load_json(repo / str(item["state_record"]))
        rows = by_tag.get(tag, [])
        actual = {
            str(row["filename"]): {
                "bytes": int(row["size_bytes"]),
                "sha256": str(row["declared_sha256"]),
            }
            for row in rows
        }
        expected = {
            str(name): {
                "bytes": int(value["bytes"]),
                "sha256": str(value["sha256"]),
            }
            for name, value in state["source_inventory"].items()
        }
        if actual != expected:
            errors.append({"archive": key, "error": "selected_release_inventory_mismatch"})
        state_checks = {
            "release_tag": state.get("source_release_tag") == tag,
            "doi": state.get("doi") == item.get("zenodo_doi"),
            "verified_file_count": state.get("verified_file_count")
            == item.get("verified_file_count")
            == len(expected),
            "verified_total_bytes": state.get("verified_total_bytes")
            == item.get("verified_total_bytes")
            == sum(value["bytes"] for value in expected.values()),
            "remote_full_readback_sha256_verified": state.get(
                "remote_full_readback_sha256_verified"
            )
            is True
            and item.get("remote_full_readback_sha256_verified") is True,
        }
        if not all(state_checks.values()):
            errors.append(
                {"archive": key, "error": "index_state_mismatch", "checks": state_checks}
            )
        archive_reports.append(
            {
                "archive": key,
                "title": item["title"],
                "release_tag": tag,
                "zenodo_doi": item["zenodo_doi"],
                "files": len(actual),
                "bytes": sum(value["bytes"] for value in actual.values()),
                "remote_full_readback_sha256_verified": state_checks[
                    "remote_full_readback_sha256_verified"
                ],
                "inventory_match": actual == expected,
            }
        )
    expected_tags = {
        str(item["github_release_tag"]) for item in index["archives"].values()
    }
    extra_tags = sorted(set(by_tag) - expected_tags)
    missing_tags = sorted(expected_tags - set(by_tag))
    if extra_tags or missing_tags:
        errors.append(
            {
                "error": "encrypted_witness_release_set_mismatch",
                "extra_tags": extra_tags,
                "missing_tags": missing_tags,
            }
        )
    logical_bytes = sum(int(row["size_bytes"]) for row in selected_rows)
    aggregate = index["aggregate"]
    if len(selected_rows) != int(aggregate["verified_file_count"]):
        errors.append({"error": "aggregate_file_count_mismatch"})
    if logical_bytes != int(aggregate["verified_total_bytes"]):
        errors.append({"error": "aggregate_byte_count_mismatch"})
    return {
        "schema": "trinityaccord.epoch-ii-encrypted-delayed-access-verification.v1",
        "status": "pass" if not errors else "fail",
        "role": "public_ciphertext_computationally_delayed_access_evidence",
        "plaintext_public_now": False,
        "unlock_material_public_now": False,
        "future_computational_decryption_intended": True,
        "publication_scope_note": (
            "The complete public archival object is ciphertext plus format, recovery, "
            "integrity, verification, benchmark and destruction-receipt metadata. "
            "Absent plaintext is intentional and is not a missing-payload claim."
        ),
        "archive_count": len(archive_reports),
        "logical_files": len(selected_rows),
        "logical_bytes": logical_bytes,
        "unique_sha256_objects": len(
            {str(row["declared_sha256"]) for row in selected_rows}
        ),
        "archives": archive_reports,
        "errors": errors,
    }


def verify_public_checksum_lists(store: pathlib.Path, selected: list[dict[str, Any]]) -> dict[str, Any]:
    releases: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in selected:
        releases[str(row["release_tag"])].append(row)
    reports = []
    errors = []
    for tag, rows in releases.items():
        by_name = {str(row["filename"]): str(row["declared_sha256"]) for row in rows}
        lists = [row for row in rows if str(row["filename"]).endswith((".sha256", "SHA256.txt"))]
        for checksum_row in lists:
            path = object_path(store, str(checksum_row["declared_sha256"]))
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            checked = 0
            for number, line in enumerate(text.splitlines(), 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(None, 1)
                if len(parts) != 2 or len(parts[0]) != 64 or any(ch not in HEX64 for ch in parts[0].lower()):
                    continue
                name = parts[1].lstrip("* ").replace("\\", "/").split("/")[-1]
                if name not in by_name:
                    continue
                checked += 1
                if by_name[name] != parts[0].lower():
                    errors.append({"release_tag": tag, "checksum_file": checksum_row["filename"], "line": number, "filename": name, "declared": by_name[name], "checksum_list": parts[0].lower()})
            reports.append({"release_tag": tag, "checksum_file": checksum_row["filename"], "selected_sibling_entries_checked": checked})
    return {"schema": "trinityaccord.epoch-ii-public-checksum-list-crosscheck.v1", "status": "pass" if not errors else "fail", "lists": reports, "errors": errors}


def cleanup_source_restore_residue(output: pathlib.Path) -> None:
    """Remove atomic restore staging paths before sealing the candidate."""
    for leftover in output.glob(".source-cold-restore.partial-*"):
        if leftover.is_dir():
            shutil.rmtree(leftover)
        else:
            leftover.unlink()


def build_source_capsule(repo: pathlib.Path, output: pathlib.Path) -> dict[str, Any]:
    capsule = output / "source-capsule"
    restore = output / "source-cold-restore"
    subprocess.run([sys.executable, str(repo / "scripts/build_preservation_capsule.py"), "--repository-root", str(repo), "--commit", "HEAD", "--output-dir", str(capsule)], check=True)
    subprocess.run([sys.executable, str(capsule / "restore-trinity-accord.py"), "--deposit-dir", str(capsule), "--output-dir", str(restore)], check=True)
    report = load_json(restore / "recovery-report.json")
    if report.get("result") != "pass":
        raise SystemExit("source capsule cold restore failed")
    shutil.rmtree(restore)
    # The established restorer uses an atomic sibling staging directory. Clean
    # any completed staging residue so it cannot silently enter this candidate.
    cleanup_source_restore_residue(output)
    return report


def write_candidate_checksums(output: pathlib.Path) -> None:
    cleanup_source_restore_residue(output)
    rows = []
    for path in sorted(output.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS":
            rows.append(f"{sha256_file(path)}  {path.relative_to(output).as_posix()}")
    (output / "SHA256SUMS").write_text("\n".join(rows) + "\n", encoding="utf-8")
    # A Git child process may finish its atomic restore staging after the
    # directory walk above has begun. Remove that late residue after hashing,
    # then prove the sealed list covers the exact remaining file set.
    cleanup_source_restore_residue(output)
    expected = {row.split("  ", 1)[1] for row in rows}
    actual = {
        path.relative_to(output).as_posix()
        for path in output.rglob("*")
        if path.is_file() and path.name != "SHA256SUMS"
    }
    if actual != expected:
        raise SystemExit("candidate checksum set does not cover exact file set after sealing")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=pathlib.Path, default=pathlib.Path("."))
    parser.add_argument("--inventory-dir", type=pathlib.Path, required=True)
    parser.add_argument("--object-store", type=pathlib.Path, required=True)
    parser.add_argument("--output-dir", type=pathlib.Path, required=True)
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--skip-source-capsule", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.workers <= 16:
        raise SystemExit("workers must be 1..16")
    repo = args.repository_root.resolve()
    inventory = args.inventory_dir.resolve()
    store = args.object_store.resolve()
    output = args.output_dir.resolve()
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"output directory must be empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    release_rows = load_json(inventory / "RELEASE-ASSETS.json")
    selected = selected_release_rows(release_rows)
    finality_dependency = full_finality_dependency(release_rows)
    objects = validate_release_rows(selected)
    log(f"selected logical_assets={len(selected)} unique_objects={len(objects)} bytes={sum(int(row['size_bytes']) for row in objects.values())}")
    verified_objects = verify_or_download_objects(store, objects, args.download, args.workers)
    with tempfile.TemporaryDirectory(prefix="epoch-ii-archives-") as temp:
        members = scan_selected_archives(store, selected, pathlib.Path(temp))
    nft_manifest = load_json(repo / "nft-text-descriptions/nft-cars-manifest.json")
    nft = extract_nft_cars(store, selected, nft_manifest)
    physical = physical_crosscheck(load_json(inventory / "PHYSICAL-EVIDENCE-FILES.json"), members)
    historical = historical_crosscheck(
        load_json(inventory / "HISTORICAL-DIGEST-CROSSWALK.json"),
        members,
        {str(item["cid"]) for item in nft_manifest["files"]},
    )
    historical_scope = historical_publication_scope(
        historical,
        load_json(
            repo
            / "preservation"
            / "epoch-ii-publication-scope-decision-20260912.json"
        ),
    )
    encrypted_witnesses = verify_encrypted_witness_archives(repo, selected)
    checksum_lists = verify_public_checksum_lists(store, selected)
    # Persist diagnostic reports before the fail-closed semantic gate so a
    # failed run remains reviewable instead of reducing the result to one line.
    write_json(output / "NFT-CAR-VERIFICATION.json", nft)
    write_json(output / "PHYSICAL-PAYLOAD-CROSSCHECK.json", physical)
    write_json(output / "HISTORICAL-DIGEST-EXPANSION.json", historical)
    write_json(
        output / "HISTORICAL-PUBLICATION-SCOPE-RESOLUTION.json",
        historical_scope,
    )
    write_json(output / "ENCRYPTED-DELAYED-ACCESS-VERIFICATION.json", encrypted_witnesses)
    write_json(output / "PUBLIC-CHECKSUM-LIST-CROSSCHECK.json", checksum_lists)
    if (
        nft["status"] != "pass"
        or encrypted_witnesses["status"] != "pass"
        or checksum_lists["status"] != "pass"
    ):
        raise SystemExit("selected content semantic verification failed")
    source_report = None if args.skip_source_capsule else build_source_capsule(repo, output)
    write_json(output / "SELECTED-RELEASE-ASSETS.json", selected)
    write_json(output / "FULL-FINALITY-INSTITUTIONAL-COPY-MANIFEST.json", finality_dependency)
    write_json(output / "VERIFIED-OBJECTS.json", verified_objects)
    write_json(output / "ARCHIVE-MEMBERS.json", members)
    families = {}
    for family in sorted({str(row["family"]) for row in selected}):
        logical = [row for row in selected if row["family"] == family]
        unique = {row["declared_sha256"]: row for row in logical}
        families[family] = {"logical_assets": len(logical), "logical_bytes": sum(int(row["size_bytes"]) for row in logical), "unique_objects": len(unique), "unique_bytes": sum(int(row["size_bytes"]) for row in unique.values())}
    source_sha = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True, text=True, stdout=subprocess.PIPE).stdout.strip()
    submission_blocks = [
        "human rights/license/Custom Terms/Terms of Use review",
        "copy every Polygon/Base Finality file to the second institution and verify anonymous public readback",
        "assemble institution-sized files and run independent remote cold recovery",
    ]
    if physical["unmatched"]:
        submission_blocks.insert(0, "resolve public physical payloads not found in selected archives")
    if historical_scope["unresolved_scope_decisions"]:
        submission_blocks.insert(
            0,
            "human scope decision for public historical commitments whose exact legacy bytes remain unavailable",
        )
    candidate = {
        "schema": SCHEMA,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_git_commit_sha": source_sha,
        "authority": "three Bitcoin Originals only",
        "role": "non_amending_research_corpus_content_verification_candidate",
        "selected_payload_scope": families,
        "selected_logical_assets": len(selected),
        "selected_unique_objects": len(objects),
        "selected_unique_bytes_verified": sum(int(row["size_bytes"]) for row in objects.values()),
        "selected_objects_sha256_and_size_verified": True,
        "archive_members_safely_enumerated": len(members),
        "nft_car_verification": {k: nft[k] for k in ("status", "expected_cars", "verified_cars", "metadata_cid_pass", "media_cid_pass", "media_cid_audit_warning_count")},
        "physical_payload_crosscheck": {k: physical[k] for k in ("status", "public_files", "verified_from_selected_archives_or_prior_capture", "unmatched")},
        "historical_digest_expansion": historical["summary"],
        "historical_publication_scope": {
            key: historical_scope[key]
            for key in (
                "status",
                "human_scope_decision_complete",
                "public_if_exact_bytes_are_recovered_rows",
                "distinct_commitment_identities",
                "currently_uploadable_rows",
                "commitment_only_exact_bytes_not_recovered_rows",
                "privacy_excluded_rows",
                "unresolved_scope_decisions",
                "exact_byte_inventory_complete",
                "project_content_gap_created_by_unavailable_legacy_wrappers",
            )
        },
        "encrypted_delayed_access_witnesses": {
            key: encrypted_witnesses[key]
            for key in (
                "status",
                "role",
                "plaintext_public_now",
                "unlock_material_public_now",
                "future_computational_decryption_intended",
                "archive_count",
                "logical_files",
                "logical_bytes",
                "unique_sha256_objects",
            )
        },
        "source_capsule_cold_restore": source_report,
        "distributed_dependencies": {
            "sidechain_finality_large_payload": finality_dependency,
            "bitcoin_operational_checkpoints": "reproducibility cache; retain inventory and latest recovery guidance, not 88.65 GB of cumulative node checkpoints",
            "superseded_museum_releases": "retain version identities; current reconstructable museum snapshot selected",
        },
        "institutional_submission_ready": False,
        "institutional_submission_blocks": submission_blocks,
        "harvard_mutated": False,
        "automatic_harvard_resubmission_allowed": False,
        "ai_disclosure": "Audit implementation and narrative were AI-assisted; the human initiator/guardian remains responsible for scope, rights, source attribution and any institutional submission.",
    }
    identity_material = json.dumps(candidate, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    candidate["candidate_identity_sha256"] = hashlib.sha256(identity_material).hexdigest()
    write_json(output / "CONTENT-CANDIDATE.json", candidate)
    (output / "START-HERE.md").write_text(
        "# Preservation Epoch II content verification candidate\n\n"
        "This is fixed, citable research data for independent inspection of Trinity Accord's public corpus and evidence relationships. "
        "It records actual byte verification of the selected public content, archive-member expansion, the 175-NFT CAR set, physical-evidence coverage and an exact-source cold restore. "
        "It is non-amending and does not replace the three Bitcoin Originals.\n\n"
        "The human publication-scope decision authorizes public access to recoverable project materials, including historically nonpublic-labelled paths. "
        "Commitment-only rows remain non-uploadable until their exact SHA-256 and size are recovered; no substitute bytes are permitted.\n\n"
        "The three encrypted witness archives are a separate computationally delayed-access layer. Their complete public object is ciphertext plus recovery and verification metadata; plaintext and unlock material are intentionally absent so future computation, rather than present disclosure, controls access.\n\n"
        "The candidate is not an institutional submission. Harvard v1.0 is unchanged, and automated Harvard submission or resubmission is prohibited. "
        "Review `CONTENT-CANDIDATE.json` and the specific verification reports before using the package.\n",
        encoding="utf-8",
    )
    # Seal only the intended candidate. Repeat the staging cleanup immediately
    # before checksumming so late filesystem residue cannot enter or invalidate
    # the exact file-set commitment.
    cleanup_source_restore_residue(output)
    write_candidate_checksums(output)
    log(f"PASS candidate={candidate['candidate_identity_sha256']} verified_bytes={candidate['selected_unique_bytes_verified']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
