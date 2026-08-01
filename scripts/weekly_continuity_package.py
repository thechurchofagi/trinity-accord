#!/usr/bin/env python3
"""Shared integrity contract for Weekly Continuity Archive packages."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


PACKAGE_TITLE = "Trinity Accord Weekly Continuity Archive"
PACKAGE_SCHEMA = "trinityaccord.weekly-continuity-deposit.v1"
RIGHTS_BOUNDARY_VERSION = "trinityaccord.weekly-continuity-rights.v1"
ZENODO_LICENSE_ID = "other-open"
ARWEAVE_TXID_RE = re.compile(r"^[A-Za-z0-9_-]{43}$")

PUBLISHED_FILE_NAMES = (
    "weekly-continuity-bundle.json",
    "archive-manifest.json",
    "deposit-manifest.json",
    "checksums.sha256",
    "README.txt",
    "zenodo-metadata.json",
)
CHECKSUM_TARGET_NAMES = (
    "weekly-continuity-bundle.json",
    "archive-manifest.json",
    "zenodo-metadata.json",
    "README.txt",
)
MANIFEST_HASHED_NAMES = CHECKSUM_TARGET_NAMES + ("checksums.sha256",)


def read_json(path: Path) -> dict[str, Any]:
    def reject_duplicates(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise SystemExit(f"duplicate JSON key {key!r}: {path}")
            result[key] = value
        return result

    try:
        data = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=reject_duplicates,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"non-finite JSON number {token}")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise SystemExit(f"invalid strict JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return data


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def md5(path: Path) -> str:
    """Return Zenodo's transport checksum; SHA-256 remains authoritative."""
    digest = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def file_inventory(deposit_dir: Path) -> dict[str, dict[str, Any]]:
    return {
        name: {
            "bytes": (deposit_dir / name).stat().st_size,
            "sha256": sha256(deposit_dir / name),
            "md5": md5(deposit_dir / name),
        }
        for name in PUBLISHED_FILE_NAMES
    }


def package_identity(inventory: dict[str, dict[str, Any]]) -> str:
    return canonical_sha256(
        {
            name: {
                "bytes": inventory[name]["bytes"],
                "sha256": inventory[name]["sha256"],
            }
            for name in sorted(inventory)
        }
    )


def parse_checksums(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            expected, name = line.split("  ", 1)
        except ValueError as exc:
            raise SystemExit(f"invalid checksum line: {line!r}") from exc
        if name in result or len(expected) != 64:
            raise SystemExit(f"invalid or duplicate checksum entry: {name}")
        result[name] = expected
    return result


def verify_local_package(deposit_dir: Path) -> dict[str, Any]:
    if not deposit_dir.is_dir():
        raise SystemExit(f"weekly continuity deposit directory is missing: {deposit_dir}")
    observed = {path.name for path in deposit_dir.iterdir() if path.is_file()}
    expected = set(PUBLISHED_FILE_NAMES)
    if observed != expected:
        raise SystemExit(
            "weekly continuity package file set mismatch: "
            f"missing={sorted(expected - observed)} unexpected={sorted(observed - expected)}"
        )

    checksums = parse_checksums(deposit_dir / "checksums.sha256")
    if set(checksums) != set(CHECKSUM_TARGET_NAMES):
        raise SystemExit("checksums.sha256 does not cover the exact required target set")
    for name, expected_sha in checksums.items():
        if sha256(deposit_dir / name) != expected_sha:
            raise SystemExit(f"deposit checksum mismatch: {name}")

    package_manifest = read_json(deposit_dir / "deposit-manifest.json")
    if package_manifest.get("schema") != PACKAGE_SCHEMA:
        raise SystemExit("unsupported weekly continuity deposit schema")
    archive_id = str(package_manifest.get("archive_id") or "")
    if not archive_id:
        raise SystemExit("deposit manifest is missing archive_id")
    if package_manifest.get("published_file_names") != list(PUBLISHED_FILE_NAMES):
        raise SystemExit("deposit manifest published file set/order mismatch")

    entries = package_manifest.get("files")
    if not isinstance(entries, list):
        raise SystemExit("deposit manifest files list is missing")
    by_name = {
        str(item.get("name")): item
        for item in entries
        if isinstance(item, dict) and item.get("name")
    }
    if set(by_name) != set(MANIFEST_HASHED_NAMES):
        raise SystemExit("deposit manifest does not cover the exact non-self file set")
    for name, item in by_name.items():
        path = deposit_dir / name
        if item.get("bytes") != path.stat().st_size or item.get("sha256") != sha256(path):
            raise SystemExit(f"deposit manifest file identity mismatch: {name}")

    rights = package_manifest.get("rights_boundary")
    if not isinstance(rights, dict) or rights.get("schema") != RIGHTS_BOUNDARY_VERSION:
        raise SystemExit("weekly continuity rights boundary is missing")
    if rights.get("third_party_rights_are_not_transferred") is not True:
        raise SystemExit("third-party rights transfer boundary is missing")
    if rights.get("license_identifier") != ZENODO_LICENSE_ID:
        raise SystemExit("Zenodo license identifier does not match the package boundary")

    metadata = read_json(deposit_dir / "zenodo-metadata.json")
    if metadata.get("title") != PACKAGE_TITLE:
        raise SystemExit("Zenodo metadata title mismatch")
    if metadata.get("version") != archive_id:
        raise SystemExit("Zenodo metadata version does not match archive_id")
    if metadata.get("license") != ZENODO_LICENSE_ID:
        raise SystemExit("Zenodo metadata license is missing or incorrect")
    if (
        metadata.get("upload_type") != "dataset"
        or metadata.get("access_right") != "open"
        or not isinstance(metadata.get("description"), str)
        or not metadata["description"].strip()
        or not isinstance(metadata.get("creators"), list)
        or not metadata["creators"]
    ):
        raise SystemExit("Zenodo dataset metadata is incomplete")

    payload_path = deposit_dir / "weekly-continuity-bundle.json"
    payload = read_json(payload_path)
    if (
        payload.get("schema") != "trinityaccord.record-chain-arweave-delta.v1"
        or payload.get("archive_id") != archive_id
        or payload.get("archive_cadence") != "weekly"
        or not isinstance(payload.get("continuity_bundle"), dict)
        or payload["continuity_bundle"].get("schema")
        != "trinityaccord.weekly-continuity-bundle.v1"
    ):
        raise SystemExit("weekly continuity payload identity/format mismatch")

    archive_manifest = read_json(deposit_dir / "archive-manifest.json")
    if archive_manifest.get("archive_id") != archive_id:
        raise SystemExit("archive manifest archive_id mismatch")
    payload_ref = archive_manifest.get("payload")
    if (
        not isinstance(payload_ref, dict)
        or payload_ref.get("bytes") != payload_path.stat().st_size
        or payload_ref.get("sha256") != sha256(payload_path)
    ):
        raise SystemExit("archive manifest payload identity mismatch")
    arweave = archive_manifest.get("arweave")
    txid = (arweave or {}).get("txid") or (arweave or {}).get("tx_id")
    if (
        archive_manifest.get("mode") != "live"
        or not isinstance(arweave, dict)
        or arweave.get("archive_status") != "archived"
        or arweave.get("verified") is not True
        or arweave.get("hash_match") is not True
        or arweave.get("readback_sha256") != sha256(payload_path)
        or not isinstance(txid, str)
        or ARWEAVE_TXID_RE.fullmatch(txid) is None
    ):
        raise SystemExit("archive manifest lacks verified Arweave payload identity")
    stored_manifest_sha = archive_manifest.get("archive_manifest_sha256")
    manifest_for_hash = dict(archive_manifest)
    manifest_for_hash["archive_manifest_sha256"] = None
    if stored_manifest_sha != canonical_sha256(manifest_for_hash):
        raise SystemExit("archive manifest self-hash mismatch")

    inventory = file_inventory(deposit_dir)
    return {
        "archive_id": archive_id,
        "manifest": package_manifest,
        "metadata": metadata,
        "inventory": inventory,
        "package_identity_sha256": package_identity(inventory),
    }
