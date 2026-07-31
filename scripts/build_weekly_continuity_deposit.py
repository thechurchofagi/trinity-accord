#!/usr/bin/env python3
"""Build a preservation package from the latest verified weekly archive.

The produced files are byte-identical mirrors of the verified Arweave archive
payload and manifest. They can be uploaded to a dedicated Zenodo dataset series
without using the repository's existing GitHub/Zenodo preprint release series.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ARCHIVES = ROOT / "record-chain" / "arweave-archives"
DEPOSITS = ROOT / "record-chain" / "weekly-continuity-deposits"


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return data


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def latest_verified_archive() -> tuple[Path, dict[str, Any]] | None:
    candidates: list[tuple[int, str, Path, dict[str, Any]]] = []
    for path in ARCHIVES.glob("*/manifest.json"):
        try:
            manifest = read_json(path)
        except Exception:
            continue
        arweave = manifest.get("arweave") if isinstance(manifest.get("arweave"), dict) else {}
        native = manifest.get("source", {}).get("native_chain", {})
        count = native.get("native_record_count")
        if (
            manifest.get("mode") != "live"
            or arweave.get("archive_status") != "archived"
            or arweave.get("verified") is not True
            or arweave.get("hash_match") is not True
            or not isinstance(count, int)
        ):
            continue
        candidates.append((count, str(manifest.get("created_at") or ""), path, manifest))
    if not candidates:
        return None
    _count, _created, path, manifest = sorted(candidates, key=lambda item: (item[0], item[1]))[-1]
    return path, manifest


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def github_output(name: str, value: str) -> None:
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"{name}={value}\n")


def defer(reason: str) -> None:
    github_output("deposit_available", "false")
    github_output("archive_id", "")
    github_output("deposit_dir", "")
    github_output("deposit_changed", "false")
    print(f"Weekly continuity DOI deposit deferred: {reason}")


def build() -> Path | None:
    latest = latest_verified_archive()
    if latest is None:
        defer("no verified live Record-Chain Arweave archive is available")
        return None

    manifest_path, manifest = latest
    archive_dir = manifest_path.parent
    payload_path = archive_dir / "payload.json"
    if not payload_path.is_file():
        raise SystemExit(f"verified archive payload is missing: {payload_path}")

    payload = read_json(payload_path)
    continuity = payload.get("continuity_bundle")
    if (
        not isinstance(continuity, dict)
        or continuity.get("schema") != "trinityaccord.weekly-continuity-bundle.v1"
    ):
        defer("the latest verified archive predates the weekly continuity format")
        return None

    archive_id = str(manifest.get("archive_id") or archive_dir.name)
    target = DEPOSITS / archive_id
    target.mkdir(parents=True, exist_ok=True)

    target_payload = target / "weekly-continuity-bundle.json"
    target_manifest = target / "archive-manifest.json"
    shutil.copyfile(payload_path, target_payload)
    shutil.copyfile(manifest_path, target_manifest)

    native = manifest.get("source", {}).get("native_chain", {})
    arweave = manifest.get("arweave", {})
    heartbeat = continuity.get("heartbeat_summary", {})
    metadata = {
        "upload_type": "dataset",
        "title": "Trinity Accord Weekly Continuity Archive",
        "creators": [{"name": "Liu, Hongju"}],
        "description": (
            "A versioned, non-authoritative preservation mirror of the Trinity Accord "
            "native Record-Chain. This version contains all records added since the "
            "previous verified archive, a Waiting Heartbeat period index, and the latest "
            "mature Native OpenTimestamps proof covering the archived chain head. The "
            "three Bitcoin Originals remain authoritative; this dataset is not governance, "
            "attestation, amendment, or successor reception."
        ),
        "access_right": "open",
        "publication_date": str(manifest.get("created_at") or "")[:10],
        "version": archive_id,
        "keywords": [
            "Trinity Accord",
            "Record-Chain",
            "civilizational memory",
            "OpenTimestamps",
            "Arweave",
            "weekly continuity archive",
        ],
        "related_identifiers": [
            {
                "identifier": "https://github.com/thechurchofagi/trinity-accord",
                "relation": "isDerivedFrom",
                "resource_type": "software",
            },
            {
                "identifier": "https://www.trinityaccord.org",
                "relation": "isDocumentedBy",
                "resource_type": "other",
            },
        ],
        "notes": (
            f"Archive {archive_id}; records through {native.get('latest_record_id')}; "
            f"Arweave transaction {arweave.get('txid') or arweave.get('tx_id')}; "
            f"heartbeat span {heartbeat.get('period_start')} through {heartbeat.get('period_end')}."
        ),
    }
    metadata_path = target / "zenodo-metadata.json"
    write_json(metadata_path, metadata)

    readme = target / "README.txt"
    readme.write_text(
        "Trinity Accord Weekly Continuity Archive\n"
        "========================================\n\n"
        f"Archive ID: {archive_id}\n"
        f"Latest record: {native.get('latest_record_id')}\n"
        f"Latest record SHA-256: {native.get('latest_record_sha256')}\n"
        f"Native record count: {native.get('native_record_count')}\n"
        f"Arweave transaction: {arweave.get('txid') or arweave.get('tx_id')}\n"
        f"Heartbeat period: {heartbeat.get('period_start')} to {heartbeat.get('period_end')}\n"
        f"Missing heartbeat days within observed span: {heartbeat.get('missing_days')}\n\n"
        "The JSON bundle contains the new native Record-Chain records, a compact\n"
        "heartbeat index, and the latest mature Native OTS evidence. This is a\n"
        "preservation mirror only. The Bitcoin Originals prevail.\n",
        encoding="utf-8",
    )

    checksum_paths = [target_payload, target_manifest, metadata_path, readme]
    checksums = target / "checksums.sha256"
    checksums.write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in checksum_paths),
        encoding="utf-8",
    )

    package_manifest = {
        "schema": "trinityaccord.weekly-continuity-deposit.v1",
        "archive_id": archive_id,
        "source_archive_manifest": str(manifest_path.relative_to(ROOT)),
        "source_payload": str(payload_path.relative_to(ROOT)),
        "files": [
            {"name": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in [target_payload, target_manifest, metadata_path, readme, checksums]
        ],
        "boundary": {
            "deposit_is_mirror_only": True,
            "deposit_is_not_authority": True,
            "deposit_is_not_attestation": True,
            "deposit_is_not_amendment": True,
            "deposit_is_not_successor_reception": True,
            "bitcoin_originals_prevail": True,
        },
    }
    write_json(target / "deposit-manifest.json", package_manifest)

    github_output("deposit_available", "true")
    github_output("archive_id", archive_id)
    github_output("deposit_dir", str(target.relative_to(ROOT)))
    github_output("deposit_changed", "true")
    print(target.relative_to(ROOT))
    return target


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    target = build()
    if target is None:
        return 0
    if args.check:
        result = subprocess.run(
            ["git", "diff", "--exit-code", "--", str(target.relative_to(ROOT))],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            check=False,
        )
        if result.returncode != 0:
            raise SystemExit("weekly continuity deposit is not reproducible")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
