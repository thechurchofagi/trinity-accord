#!/usr/bin/env python3
"""Integrity contract for the full Trinity Accord repository capsule."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any


PACKAGE_TITLE = "Trinity Accord Repository Preservation Capsule"
PACKAGE_SCHEMA = "trinityaccord.repository-preservation-capsule.v1"
TRACKED_FILES_SCHEMA = "trinityaccord.repository-tracked-files.v1"
RIGHTS_BOUNDARY_VERSION = "trinityaccord.repository-preservation-rights.v1"
ZENODO_LICENSE_ID = "other-closed"

PUBLISHED_FILE_NAMES = (
    "trinity-accord-source.tar.gz",
    "trinity-accord-recovery.bundle",
    "tracked-files.json",
    "preservation-manifest.json",
    "checksums.sha256",
    "README.txt",
    "restore-trinity-accord.py",
    "zenodo-metadata.json",
)
CHECKSUM_TARGET_NAMES = (
    "trinity-accord-source.tar.gz",
    "trinity-accord-recovery.bundle",
    "tracked-files.json",
    "README.txt",
    "restore-trinity-accord.py",
    "zenodo-metadata.json",
)
MANIFEST_HASHED_NAMES = CHECKSUM_TARGET_NAMES + ("checksums.sha256",)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_OID_RE = re.compile(r"^[0-9a-f]{40,64}$")


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


def canonical_sha256(value: Any) -> str:
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


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


def safe_repository_path(value: Any) -> str:
    if not isinstance(value, str) or not value:
        raise SystemExit("tracked repository path is missing")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "\x00" in value:
        raise SystemExit(f"unsafe tracked repository path: {value!r}")
    return str(path)


def parse_checksums(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            expected, name = line.split("  ", 1)
        except ValueError as exc:
            raise SystemExit(f"invalid checksum line: {line!r}") from exc
        if name in result or SHA256_RE.fullmatch(expected) is None:
            raise SystemExit(f"invalid or duplicate checksum entry: {name}")
        result[name] = expected
    return result


def file_inventory(capsule_dir: Path) -> dict[str, dict[str, Any]]:
    return {
        name: {
            "bytes": (capsule_dir / name).stat().st_size,
            "sha256": sha256(capsule_dir / name),
            "md5": md5(capsule_dir / name),
        }
        for name in PUBLISHED_FILE_NAMES
    }


def manifest_identity(manifest: dict[str, Any]) -> str:
    value = dict(manifest)
    value.pop("package_identity_sha256", None)
    return canonical_sha256(value)


def verify_tracked_inventory(path: Path) -> dict[str, Any]:
    tracked = strict_json(path)
    if tracked.get("schema") != TRACKED_FILES_SCHEMA:
        raise SystemExit("unsupported tracked-files schema")
    commit = str(tracked.get("git_commit_sha") or "")
    tree = str(tracked.get("git_tree_oid") or "")
    if GIT_OID_RE.fullmatch(commit) is None or GIT_OID_RE.fullmatch(tree) is None:
        raise SystemExit("tracked-files Git identity is invalid")
    files = tracked.get("files")
    if not isinstance(files, list) or not files:
        raise SystemExit("tracked-files inventory is empty")
    observed_paths: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for item in files:
        if not isinstance(item, dict):
            raise SystemExit("tracked-files entry is not an object")
        name = safe_repository_path(item.get("path"))
        if name in observed_paths:
            raise SystemExit(f"duplicate tracked repository path: {name}")
        observed_paths.add(name)
        if item.get("mode") not in {"100644", "100755"}:
            raise SystemExit(f"unsupported tracked file mode for capsule: {name}")
        if GIT_OID_RE.fullmatch(str(item.get("git_blob_oid") or "")) is None:
            raise SystemExit(f"invalid Git blob identity: {name}")
        if not isinstance(item.get("bytes"), int) or item["bytes"] < 0:
            raise SystemExit(f"invalid tracked byte length: {name}")
        if SHA256_RE.fullmatch(str(item.get("sha256") or "")) is None:
            raise SystemExit(f"invalid tracked SHA-256: {name}")
        normalized.append(item)
    if tracked.get("file_count") != len(normalized):
        raise SystemExit("tracked-files count mismatch")
    if normalized != sorted(normalized, key=lambda item: item["path"]):
        raise SystemExit("tracked-files entries are not path-sorted")
    expected_identity = canonical_sha256(normalized)
    if tracked.get("inventory_sha256") != expected_identity:
        raise SystemExit("tracked-files inventory identity mismatch")
    return tracked


def verify_local_package(capsule_dir: Path) -> dict[str, Any]:
    if not capsule_dir.is_dir():
        raise SystemExit(f"preservation capsule directory is missing: {capsule_dir}")
    observed = {path.name for path in capsule_dir.iterdir() if path.is_file()}
    expected = set(PUBLISHED_FILE_NAMES)
    if observed != expected:
        raise SystemExit(
            "preservation capsule file set mismatch: "
            f"missing={sorted(expected - observed)} unexpected={sorted(observed - expected)}"
        )

    checksums = parse_checksums(capsule_dir / "checksums.sha256")
    if set(checksums) != set(CHECKSUM_TARGET_NAMES):
        raise SystemExit("capsule checksums do not cover the exact payload set")
    for name, expected_sha in checksums.items():
        if sha256(capsule_dir / name) != expected_sha:
            raise SystemExit(f"preservation capsule checksum mismatch: {name}")

    tracked = verify_tracked_inventory(capsule_dir / "tracked-files.json")
    manifest = strict_json(capsule_dir / "preservation-manifest.json")
    if manifest.get("schema") != PACKAGE_SCHEMA:
        raise SystemExit("unsupported preservation capsule schema")
    capsule_id = str(manifest.get("capsule_id") or "")
    if not capsule_id.startswith("repository-"):
        raise SystemExit("preservation capsule id is missing")
    if manifest.get("published_file_names") != list(PUBLISHED_FILE_NAMES):
        raise SystemExit("preservation manifest published file set/order mismatch")
    if manifest.get("git", {}).get("commit_sha") != tracked["git_commit_sha"]:
        raise SystemExit("preservation manifest/tracked-files commit mismatch")
    if manifest.get("git", {}).get("tree_oid") != tracked["git_tree_oid"]:
        raise SystemExit("preservation manifest/tracked-files tree mismatch")
    git = manifest.get("git")
    recovery_commit = str(git.get("recovery_commit_sha") or "") if isinstance(git, dict) else ""
    expected_refs = [{"ref": "refs/heads/main", "object_oid": recovery_commit}]
    if (
        GIT_OID_RE.fullmatch(recovery_commit) is None
        or git.get("bundle_ref_count") != 1
        or git.get("bundle_refs") != expected_refs
        or git.get("production_parent_history_embedded") is not False
        or git.get("production_tags_embedded") is not False
    ):
        raise SystemExit("preservation manifest safe recovery-bundle boundary is invalid")

    entries = manifest.get("files")
    if not isinstance(entries, list):
        raise SystemExit("preservation manifest files list is missing")
    by_name = {
        str(item.get("name")): item
        for item in entries
        if isinstance(item, dict) and item.get("name")
    }
    if set(by_name) != set(MANIFEST_HASHED_NAMES):
        raise SystemExit("preservation manifest does not cover the exact non-self file set")
    for name, item in by_name.items():
        path = capsule_dir / name
        if item.get("bytes") != path.stat().st_size or item.get("sha256") != sha256(path):
            raise SystemExit(f"preservation manifest file identity mismatch: {name}")

    if manifest.get("package_identity_sha256") != manifest_identity(manifest):
        raise SystemExit("preservation manifest package identity mismatch")
    rights = manifest.get("rights_boundary")
    if not isinstance(rights, dict) or rights.get("schema") != RIGHTS_BOUNDARY_VERSION:
        raise SystemExit("preservation capsule rights boundary is missing")
    if rights.get("license_identifier") != ZENODO_LICENSE_ID:
        raise SystemExit("preservation capsule licence boundary mismatch")
    if rights.get("deposit_grants_no_new_reuse_rights") is not True:
        raise SystemExit("preservation capsule no-new-rights boundary is missing")
    if rights.get("third_party_rights_are_not_transferred") is not True:
        raise SystemExit("preservation capsule third-party rights boundary is missing")

    scope = manifest.get("scope")
    if not isinstance(scope, dict):
        raise SystemExit("preservation capsule scope is missing")
    if (
        scope.get("github_required_for_repository_recovery") is not False
        or scope.get("git_tracked_repository_embedded") is not True
        or scope.get("main_history_and_tags_embedded") is not False
        or scope.get("exact_current_production_tree_embedded") is not True
        or scope.get("cloneable_single_root_recovery_bundle_embedded") is not True
        or scope.get("external_large_binary_annex_embedded") is not False
    ):
        raise SystemExit("preservation capsule recovery scope is inconsistent")

    metadata = strict_json(capsule_dir / "zenodo-metadata.json")
    if (
        metadata.get("upload_type") != "software"
        or metadata.get("title") != PACKAGE_TITLE
        or metadata.get("version") != capsule_id
        or metadata.get("access_right") != "open"
        or metadata.get("license") != ZENODO_LICENSE_ID
        or not isinstance(metadata.get("creators"), list)
        or not metadata["creators"]
    ):
        raise SystemExit("preservation capsule Zenodo metadata is incomplete")

    inventory = file_inventory(capsule_dir)
    return {
        "capsule_id": capsule_id,
        "git_commit_sha": tracked["git_commit_sha"],
        "git_tree_oid": tracked["git_tree_oid"],
        "tracked_file_count": tracked["file_count"],
        "manifest": manifest,
        "metadata": metadata,
        "inventory": inventory,
        "package_identity_sha256": manifest["package_identity_sha256"],
    }
