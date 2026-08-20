#!/usr/bin/env python3
"""Offline verifier/restorer for a Trinity Accord full-project preservation bundle.

The bundle is non-amending preservation material. It never changes the authority
boundary: only the three Bitcoin Originals are canonical/interpretive authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any

SCHEMA = "trinityaccord.full-project-preservation-bundle.v1"
HEX = set("0123456789abcdef")


def strict_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"unable to read strict JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"JSON root is not an object: {path}")
    return value


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_relative(value: str) -> Path:
    path = Path(value)
    if not value or path.is_absolute() or ".." in path.parts:
        raise SystemExit(f"unsafe logical path in manifest: {value!r}")
    return path


def object_path(bundle: Path, sha256: str) -> Path:
    value = str(sha256).lower()
    if len(value) != 64 or any(ch not in HEX for ch in value):
        raise SystemExit(f"invalid object SHA-256: {sha256!r}")
    return bundle / "objects" / "sha256" / value[:2] / value


def canonical_identity_material(manifest: dict[str, Any]) -> bytes:
    material = {
        "schema": manifest.get("schema"),
        "source_repository": manifest.get("source_repository"),
        "source_git_commit_sha": manifest.get("source_git_commit_sha"),
        "source_git_tree_oid": manifest.get("source_git_tree_oid"),
        "authority_boundary": manifest.get("authority_boundary"),
        "known_limitations": manifest.get("known_limitations"),
        "sources": manifest.get("sources"),
        "objects": manifest.get("objects"),
    }
    return json.dumps(
        material, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def verify_bundle(bundle: Path, materialize: Path | None = None) -> dict[str, Any]:
    manifest = strict_json(bundle / "full-project-manifest.json")
    if manifest.get("schema") != SCHEMA:
        raise SystemExit(f"unexpected bundle schema: {manifest.get('schema')!r}")
    authority = manifest.get("authority_boundary")
    if not isinstance(authority, dict):
        raise SystemExit("authority boundary missing")
    if authority.get("canonical_interpretive_authority") != "three_bitcoin_originals_only":
        raise SystemExit("canonical authority boundary changed")
    if authority.get("non_amending_preservation") is not True:
        raise SystemExit("bundle is not marked non-amending")

    objects = manifest.get("objects")
    sources = manifest.get("sources")
    if not isinstance(objects, list) or not isinstance(sources, list):
        raise SystemExit("manifest objects/sources are not lists")

    by_hash: dict[str, dict[str, Any]] = {}
    total_bytes = 0
    for index, item in enumerate(objects):
        if not isinstance(item, dict):
            raise SystemExit(f"object entry {index} is not an object")
        sha = str(item.get("sha256") or "").lower()
        try:
            expected_size = int(item.get("bytes"))
        except (TypeError, ValueError) as exc:
            raise SystemExit(f"object entry {index} has invalid size") from exc
        if sha in by_hash:
            raise SystemExit(f"duplicate object entry: {sha}")
        path = object_path(bundle, sha)
        if not path.is_file():
            raise SystemExit(f"missing content-addressed object: {sha}")
        observed_size = path.stat().st_size
        if observed_size != expected_size:
            raise SystemExit(
                f"object size mismatch {sha}: {observed_size} != {expected_size}"
            )
        observed_sha = hash_file(path)
        if observed_sha != sha:
            raise SystemExit(f"object hash mismatch: {sha} != {observed_sha}")
        by_hash[sha] = item
        total_bytes += observed_size

    logical_paths: set[str] = set()
    logical_file_count = 0
    for source_index, source in enumerate(sources):
        if not isinstance(source, dict):
            raise SystemExit(f"source entry {source_index} is not an object")
        files = source.get("files")
        if not isinstance(files, list):
            raise SystemExit(f"source entry {source_index} files is not a list")
        for file_index, item in enumerate(files):
            if not isinstance(item, dict):
                raise SystemExit(
                    f"source {source_index} file {file_index} is not an object"
                )
            logical = str(item.get("logical_path") or "")
            safe_relative(logical)
            if logical in logical_paths:
                raise SystemExit(f"duplicate logical path: {logical}")
            logical_paths.add(logical)
            sha = str(item.get("object_sha256") or "").lower()
            if sha not in by_hash:
                raise SystemExit(f"logical file refers to missing object: {logical}: {sha}")
            if int(item.get("bytes", -1)) != int(by_hash[sha]["bytes"]):
                raise SystemExit(f"logical file size differs from object: {logical}")
            logical_file_count += 1
            if materialize is not None:
                target = materialize / safe_relative(logical)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(object_path(bundle, sha), target)

    expected_identity = str(manifest.get("bundle_identity_sha256") or "").lower()
    observed_identity = hashlib.sha256(canonical_identity_material(manifest)).hexdigest()
    if expected_identity != observed_identity:
        raise SystemExit(
            f"bundle identity mismatch: {observed_identity} != {expected_identity}"
        )

    report = {
        "schema": "trinityaccord.full-project-preservation-verification.v1",
        "result": "pass",
        "bundle_identity_sha256": observed_identity,
        "source_git_commit_sha": manifest.get("source_git_commit_sha"),
        "unique_object_count": len(by_hash),
        "logical_file_count": logical_file_count,
        "unique_object_bytes": total_bytes,
        "source_count": len(sources),
        "materialized": materialize is not None,
        "authority_boundary": "three_bitcoin_originals_only",
        "non_amending_preservation": True,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-dir", required=True, type=Path)
    parser.add_argument("--materialize-dir", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    bundle = args.bundle_dir.resolve()
    materialize = args.materialize_dir.resolve() if args.materialize_dir else None
    if materialize:
        if materialize.exists() and any(materialize.iterdir()):
            raise SystemExit(f"materialize directory must be empty: {materialize}")
        materialize.mkdir(parents=True, exist_ok=True)
    report = verify_bundle(bundle, materialize)
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
