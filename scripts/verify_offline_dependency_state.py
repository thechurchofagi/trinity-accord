#!/usr/bin/env python3
"""Generate or verify a committed offline-dependency identity state."""
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


def build_state(capsule_dir: Path, archive_path: Path) -> dict[str, Any]:
    """Derive the exact content identity state from a verified capsule.

    Transport metadata such as a GitHub Actions artifact id is deliberately not
    part of this generated state: artifact ids are assigned only after upload
    and are not part of the preserved dependency content identity.
    """
    manifest_path = capsule_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return {
        "schema": STATE_SCHEMA,
        "authority_effect": "none",
        "capsule_archive": {
            "bytes": archive_path.stat().st_size,
            "sha256": sha256_file(archive_path),
            "manifest_sha256": sha256_file(manifest_path),
            "payload_file_count": manifest["payload_file_count"],
        },
        "python": {
            "wheel_count": manifest["python"]["wheel_count"],
            "resolved_distribution_count": manifest["python"][
                "resolved_distribution_count"
            ],
            "sdist_identities": expected_python_identities(manifest),
        },
        "node": expected_node_identities(manifest),
    }


def write_state(path: Path, state: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(state, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
        + "\n",
        encoding="utf-8",
    )


def verify(state_path: Path, capsule_dir: Path, archive_path: Path) -> None:
    state = json.loads(state_path.read_text(encoding="utf-8"))
    expected = build_state(capsule_dir, archive_path)

    if state.get("schema") != STATE_SCHEMA:
        raise SystemExit("unsupported offline dependency state schema")
    if state.get("authority_effect") != "none":
        raise SystemExit("offline dependency state must remain non-authoritative")

    archive = state.get("capsule_archive")
    if not isinstance(archive, dict):
        raise SystemExit("offline dependency state lacks capsule archive identity")
    if archive.get("bytes") != expected["capsule_archive"]["bytes"]:
        raise SystemExit("offline dependency archive size does not match committed state")
    if archive.get("sha256") != expected["capsule_archive"]["sha256"]:
        raise SystemExit("offline dependency archive SHA-256 does not match committed state")
    if archive.get("manifest_sha256") != expected["capsule_archive"]["manifest_sha256"]:
        raise SystemExit("offline dependency manifest SHA-256 does not match committed state")
    if archive.get("payload_file_count") != expected["capsule_archive"]["payload_file_count"]:
        raise SystemExit("offline dependency payload count does not match committed state")

    python_state = state.get("python")
    if not isinstance(python_state, dict):
        raise SystemExit("offline dependency state lacks Python identity set")
    if python_state.get("wheel_count") != expected["python"]["wheel_count"]:
        raise SystemExit("offline dependency Python wheel count does not match committed state")
    if python_state.get("resolved_distribution_count") != expected["python"]["resolved_distribution_count"]:
        raise SystemExit("offline dependency Python resolved count does not match committed state")
    if python_state.get("sdist_identities") != expected["python"]["sdist_identities"]:
        raise SystemExit("offline dependency Python source identities do not match committed state")

    if state.get("node") != expected["node"]:
        raise SystemExit("offline dependency Node tarball identities do not match committed state")


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--state")
    group.add_argument("--write-state")
    parser.add_argument("--capsule-dir", required=True)
    parser.add_argument("--archive", required=True)
    args = parser.parse_args()

    capsule_dir = Path(args.capsule_dir)
    archive_path = Path(args.archive)
    if args.write_state:
        output = Path(args.write_state)
        write_state(output, build_state(capsule_dir, archive_path))
        print(f"offline dependency candidate identity state: {output}")
        return 0

    verify(Path(args.state), capsule_dir, archive_path)
    print("offline dependency committed identity state: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
