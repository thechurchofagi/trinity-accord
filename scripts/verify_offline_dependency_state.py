#!/usr/bin/env python3
"""Verify a committed offline-dependency identity state against a built capsule."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

STATE_SCHEMA = "trinityaccord.offline-dependency-state.v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def expected_python_identities(manifest: dict[str, Any]) -> list[str]:
    result = []
    for item in manifest["python"]["sdists"]:
        result.append(
            f"{item['name']}=={item['version']}|{item['original_filename']}|"
            f"sha256:{item['sha256']}"
        )
    return result


def expected_node_identities(manifest: dict[str, Any]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for group in manifest["node"]:
        result[group["label"]] = [
            f"{item['package_path']}@{item['version']}|sha256:{item['sha256']}"
            for item in group["tarballs"]
        ]
    return result


def verify(state_path: Path, capsule_dir: Path, archive_path: Path) -> None:
    state = json.loads(state_path.read_text(encoding="utf-8"))
    manifest_path = capsule_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if state.get("schema") != STATE_SCHEMA:
        raise SystemExit("unsupported offline dependency state schema")
    if state.get("authority_effect") != "none":
        raise SystemExit("offline dependency state must remain non-authoritative")

    archive = state.get("capsule_archive")
    if not isinstance(archive, dict):
        raise SystemExit("offline dependency state lacks capsule archive identity")
    if archive.get("bytes") != archive_path.stat().st_size:
        raise SystemExit("offline dependency archive size does not match committed state")
    if archive.get("sha256") != sha256_file(archive_path):
        raise SystemExit("offline dependency archive SHA-256 does not match committed state")
    if archive.get("manifest_sha256") != sha256_file(manifest_path):
        raise SystemExit("offline dependency manifest SHA-256 does not match committed state")
    if archive.get("payload_file_count") != manifest.get("payload_file_count"):
        raise SystemExit("offline dependency payload count does not match committed state")

    python_state = state.get("python")
    if not isinstance(python_state, dict):
        raise SystemExit("offline dependency state lacks Python identity set")
    if python_state.get("wheel_count") != manifest["python"]["wheel_count"]:
        raise SystemExit("offline dependency Python wheel count does not match committed state")
    if python_state.get("resolved_distribution_count") != manifest["python"]["resolved_distribution_count"]:
        raise SystemExit("offline dependency Python resolved count does not match committed state")
    if python_state.get("sdist_identities") != expected_python_identities(manifest):
        raise SystemExit("offline dependency Python source identities do not match committed state")

    if state.get("node") != expected_node_identities(manifest):
        raise SystemExit("offline dependency Node tarball identities do not match committed state")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True)
    parser.add_argument("--capsule-dir", required=True)
    parser.add_argument("--archive", required=True)
    args = parser.parse_args()
    verify(Path(args.state), Path(args.capsule_dir), Path(args.archive))
    print("offline dependency committed identity state: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
