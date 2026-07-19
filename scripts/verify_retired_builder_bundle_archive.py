#!/usr/bin/env python3
"""Verify committed retired Gateway v1 builder archives without executing them."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tarfile
from pathlib import Path, PurePosixPath
from typing import Any

REQUIRED_REPLACEMENT = {
    "contract": "/api/record-chain-intake-gateway.v1.json",
    "builder": "/downloads/record-chain-builder.mjs",
    "preflight": "/record-chain/preflight",
    "submit": "/record-chain/submit",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=strict_object,
            parse_constant=reject_constant,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"{label} is not strict UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} root must be an object")
    return value


def safe_member(member: tarfile.TarInfo) -> bool:
    path = PurePosixPath(member.name)
    if path.is_absolute() or ".." in path.parts or not member.name:
        return False
    return not (member.issym() or member.islnk() or member.isdev() or member.isfifo())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-dir", type=Path)
    args = parser.parse_args()
    root = (args.site_dir or Path(__file__).resolve().parents[1]).resolve()
    manifest_path = root / "api/formal-builder-bundles.v1.json"
    helper = root / "builder-bundles/download_and_run_builder_bundle.py"
    errors: list[str] = []

    try:
        doc = load_json_object(manifest_path, "retired bundle manifest")
    except ValueError as exc:
        print(f"FAIL: cannot read retired bundle manifest: {exc}")
        return 1

    for key in (
        "historical_archive_only",
        "do_not_use_for_new_public_submissions",
        "all_bundles_retired",
    ):
        if doc.get(key) is not True:
            errors.append(f"top-level {key} must be true")
    if doc.get("status") != "historical_archive_only":
        errors.append("top-level status must be historical_archive_only")
    if doc.get("replacement") != "/api/agent-first-contact.json":
        errors.append("top-level replacement must be current First Contact")

    bundles = doc.get("bundles")
    if not isinstance(bundles, dict) or not bundles:
        errors.append("bundles must be a non-empty object")
        bundles = {}

    for route, meta in bundles.items():
        if not isinstance(route, str) or not isinstance(meta, dict):
            errors.append(f"invalid bundle entry {route!r}")
            continue
        if meta.get("route_id") != route:
            errors.append(f"{route}: route_id mismatch")
        if not (
            meta.get("status") == "historical_archive_only"
            and meta.get("retired") is True
            and meta.get("do_not_use_for_new_public_submissions") is True
        ):
            errors.append(f"{route}: retirement flags incomplete")
        if meta.get("retired_replacement") != REQUIRED_REPLACEMENT:
            errors.append(f"{route}: current replacement drifted")

        archive_name = meta.get("archive_name")
        if not isinstance(archive_name, str) or not archive_name or PurePosixPath(archive_name).name != archive_name:
            errors.append(f"{route}: archive_name must be a safe basename")
            continue
        archive = root / "builder-bundles" / archive_name
        archive_url = meta.get("archive_url")
        if archive_url != f"/builder-bundles/{archive_name}":
            errors.append(f"{route}: archive_url mismatch")
        if not archive.is_file():
            errors.append(f"{route}: missing archive {archive_name}")
            continue
        raw = archive.read_bytes()
        if sha256(raw) != meta.get("sha256"):
            errors.append(f"{route}: archive sha256 mismatch")
        if len(raw) != meta.get("size_bytes"):
            errors.append(f"{route}: archive size mismatch")

        manifest_url = meta.get("manifest_url")
        if not isinstance(manifest_url, str) or not manifest_url.startswith("/builder-bundles/"):
            errors.append(f"{route}: manifest_url must stay under /builder-bundles/")
            continue
        bundle_manifest = root / manifest_url.lstrip("/")
        if not bundle_manifest.is_file():
            errors.append(f"{route}: missing bundle manifest")
            continue
        try:
            bm = load_json_object(bundle_manifest, f"{route} bundle manifest")
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if not (
            bm.get("archive") == archive_name
            and bm.get("archive_sha256") == sha256(raw)
            and bm.get("archive_size_bytes") == len(raw)
        ):
            errors.append(f"{route}: bundle manifest archive binding mismatch")

        files = bm.get("files")
        if not isinstance(files, list):
            errors.append(f"{route}: bundle manifest files must be an array")
            files = []
        declared: dict[str, dict[str, Any]] = {}
        for item in files:
            if not isinstance(item, dict):
                errors.append(f"{route}: non-object file declaration")
                continue
            declared_path = item.get("path")
            if not isinstance(declared_path, str) or not declared_path:
                errors.append(f"{route}: file declaration has no path")
                continue
            if declared_path in declared:
                errors.append(f"{route}: duplicate declared file {declared_path}")
                continue
            declared[declared_path] = item

        try:
            with tarfile.open(archive, "r:gz") as tar:
                all_members = tar.getmembers()
                for member in all_members:
                    if not safe_member(member):
                        errors.append(f"{route}: unsafe tar member {member.name}")
                members = [member for member in all_members if member.isfile()]
                member_names = [member.name for member in members]
                if len(member_names) != len(set(member_names)):
                    errors.append(f"{route}: duplicate tar member name")
                actual = set(member_names)
                if actual != set(declared):
                    errors.append(f"{route}: tar file set differs from manifest")
                for member in members:
                    fileobj = tar.extractfile(member)
                    data = fileobj.read() if fileobj else b""
                    item = declared.get(member.name, {})
                    if sha256(data) != item.get("sha256") or len(data) != item.get("size_bytes"):
                        errors.append(f"{route}: member binding mismatch {member.name}")
        except (OSError, tarfile.TarError) as exc:
            errors.append(f"{route}: cannot inspect archive: {exc}")

        if bm.get("entrypoint") not in declared:
            errors.append(f"{route}: entrypoint absent from manifest files")

    if not helper.is_file():
        errors.append("missing public retired-bundle helper")
    else:
        text = helper.read_text(encoding="utf-8")
        for marker in (
            "--allow-historical-retired-bundle",
            "REFUSED: all formal Gateway v1 builder bundles are retired",
            "HISTORICAL OUTPUT ONLY — DO NOT SUBMIT",
        ):
            if marker not in text:
                errors.append(f"public helper missing fail-closed marker {marker!r}")

    if errors:
        print("FAIL: retired builder bundle archive contract errors:")
        for error in errors:
            print("  -", error)
        return 1
    print(f"PASS: {len(bundles)} retired builder archives are strictly bound, safe, and fail closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
