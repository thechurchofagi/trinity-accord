#!/usr/bin/env python3
"""Build preservation packages for the verified weekly archive chain.

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

from weekly_continuity_package import (
    CHECKSUM_TARGET_NAMES,
    MANIFEST_HASHED_NAMES,
    PACKAGE_TITLE,
    RIGHTS_BOUNDARY_VERSION,
    ZENODO_LICENSE_ID,
    verify_local_package,
)

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


def verified_weekly_archive_chain() -> list[tuple[Path, dict[str, Any], dict[str, Any]]]:
    candidates: dict[str, tuple[Path, dict[str, Any], dict[str, Any]]] = {}
    for path in ARCHIVES.glob("*/manifest.json"):
        payload_path = path.parent / "payload.json"
        try:
            manifest = read_json(path)
            payload = read_json(payload_path)
        except Exception:
            continue
        arweave = manifest.get("arweave") if isinstance(manifest.get("arweave"), dict) else {}
        coverage = payload.get("coverage") if isinstance(payload.get("coverage"), dict) else {}
        archive_id = payload.get("archive_id")
        count = coverage.get("current_native_record_count")
        if (
            manifest.get("mode") != "live"
            or arweave.get("archive_status") != "archived"
            or arweave.get("verified") is not True
            or arweave.get("hash_match") is not True
            or payload.get("schema") != "trinityaccord.record-chain-arweave-delta.v1"
            or payload.get("archive_cadence") != "weekly"
            or payload.get("archive_mode") not in {"full_snapshot", "incremental_delta"}
            or not isinstance(payload.get("continuity_bundle"), dict)
            or payload["continuity_bundle"].get("schema")
            != "trinityaccord.weekly-continuity-bundle.v1"
            or not isinstance(archive_id, str)
            or not archive_id
            or manifest.get("archive_id") != archive_id
            or not isinstance(count, int)
        ):
            continue
        if archive_id in candidates:
            raise SystemExit(f"duplicate verified weekly archive_id: {archive_id}")
        candidates[archive_id] = (path, manifest, payload)
    if not candidates:
        return []

    latest = max(
        candidates.values(),
        key=lambda item: (
            item[2]["coverage"]["current_native_record_count"],
            str(item[1].get("created_at") or ""),
        ),
    )
    chain: list[tuple[Path, dict[str, Any], dict[str, Any]]] = []
    seen: set[str] = set()
    current = latest
    while True:
        path, manifest, payload = current
        archive_id = str(payload["archive_id"])
        if archive_id in seen:
            raise SystemExit(f"cycle in verified weekly archive chain at {archive_id}")
        seen.add(archive_id)
        chain.append(current)
        coverage = payload["coverage"]
        if payload["archive_mode"] == "full_snapshot":
            if coverage.get("previous_native_record_count") != 0:
                raise SystemExit("weekly full_snapshot baseline must begin at record count zero")
            break
        previous = payload.get("previous_archive")
        previous_id = previous.get("archive_id") if isinstance(previous, dict) else None
        if not isinstance(previous_id, str) or previous_id not in candidates:
            raise SystemExit(
                f"verified weekly archive chain is missing predecessor for {archive_id}: "
                f"{previous_id or '<missing>'}"
            )
        current = candidates[previous_id]

    chain.reverse()
    previous_count = 0
    for position, (_path, manifest, payload) in enumerate(chain):
        coverage = payload["coverage"]
        if coverage.get("previous_native_record_count") != previous_count:
            raise SystemExit(f"verified weekly archive chain has a coverage gap at {payload['archive_id']}")
        if position > 0:
            previous_payload = chain[position - 1][2]
            previous_manifest = chain[position - 1][1]
            previous = payload.get("previous_archive")
            previous_txid = previous_manifest.get("arweave", {}).get("txid") or previous_manifest.get(
                "arweave", {}
            ).get("tx_id")
            if (
                not isinstance(previous, dict)
                or previous.get("archive_id") != previous_payload.get("archive_id")
                or previous.get("native_record_count")
                != previous_payload["coverage"].get("current_native_record_count")
                or previous.get("latest_record_id")
                != previous_payload["coverage"].get("current_latest_record_id")
                or previous.get("latest_record_sha256")
                != previous_payload["coverage"].get("current_latest_record_sha256")
                or previous.get("arweave_txid") != previous_txid
            ):
                raise SystemExit(
                    f"verified weekly archive predecessor identity mismatch at {payload['archive_id']}"
                )
        previous_count = coverage.get("current_native_record_count")
    return chain


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
    github_output("deposit_series_dir", "")
    github_output("deposit_changed", "false")
    print(f"Weekly continuity DOI deposit deferred: {reason}")


def build_archive(
    manifest_path: Path, manifest: dict[str, Any], payload: dict[str, Any]
) -> Path:
    archive_dir = manifest_path.parent
    payload_path = archive_dir / "payload.json"
    archive_id = str(manifest.get("archive_id") or archive_dir.name)
    target = DEPOSITS / archive_id
    target.mkdir(parents=True, exist_ok=True)

    target_payload = target / "weekly-continuity-bundle.json"
    target_manifest = target / "archive-manifest.json"
    shutil.copyfile(payload_path, target_payload)
    shutil.copyfile(manifest_path, target_manifest)

    continuity = payload["continuity_bundle"]
    native = manifest.get("source", {}).get("native_chain", {})
    arweave = manifest.get("arweave", {})
    heartbeat = continuity.get("heartbeat_summary", {})
    archive_contents = (
        "a self-contained full baseline of the native Record-Chain"
        if payload.get("archive_mode") == "full_snapshot"
        else "all native Record-Chain records added since the previous verified archive"
    )
    metadata = {
        "upload_type": "dataset",
        "title": PACKAGE_TITLE,
        "creators": [{"name": "Liu, Hongju"}],
        "description": (
            "A versioned, non-authoritative preservation mirror of the Trinity Accord "
            f"native Record-Chain. This version contains {archive_contents}, a Waiting "
            "Heartbeat period index, and the latest mature Native OpenTimestamps proof "
            "covering the archived chain head. The three Bitcoin Originals remain "
            "authoritative; this dataset is not governance, attestation, amendment, or "
            "successor reception."
        ),
        "access_right": "open",
        "license": ZENODO_LICENSE_ID,
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
            f"heartbeat span {heartbeat.get('period_start')} through {heartbeat.get('period_end')}. "
            "Rights boundary: the record is publicly readable for preservation and research, "
            "but the deposit grants no blanket reuse licence. Project-authored and embedded "
            "Record-Chain materials remain subject to their respective rights; inclusion does "
            "not transfer copyright or grant rights the archive publisher does not possess."
        ),
    }
    metadata_path = target / "zenodo-metadata.json"
    write_json(metadata_path, metadata)

    readme = target / "README.txt"
    readme.write_text(
        "Trinity Accord Weekly Continuity Archive\n"
        "========================================\n\n"
        f"Archive ID: {archive_id}\n"
        f"Archive mode: {payload.get('archive_mode')}\n"
        f"Latest record: {native.get('latest_record_id')}\n"
        f"Latest record SHA-256: {native.get('latest_record_sha256')}\n"
        f"Native record count: {native.get('native_record_count')}\n"
        f"Arweave transaction: {arweave.get('txid') or arweave.get('tx_id')}\n"
        f"Heartbeat period: {heartbeat.get('period_start')} to {heartbeat.get('period_end')}\n"
        f"Missing heartbeat days within observed span: {heartbeat.get('missing_days')}\n\n"
        "The JSON bundle contains the applicable native Record-Chain baseline or\n"
        "delta, a compact heartbeat index, and the latest mature Native OTS evidence.\n"
        "This is a preservation mirror only. The Bitcoin Originals prevail.\n"
        "\nRights and reuse boundary\n"
        "-------------------------\n"
        "This record is publicly readable for preservation and research, but this\n"
        "deposit grants no blanket reuse licence. Project-authored and embedded\n"
        "Record-Chain materials remain subject to their respective rights. Inclusion\n"
        "in this public mirror does not transfer copyright or grant rights the archive\n"
        "publisher does not possess. Public availability is not a claim of ownership.\n",
        encoding="utf-8",
    )

    checksum_paths = [target / name for name in CHECKSUM_TARGET_NAMES]
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
            for path in [target / name for name in MANIFEST_HASHED_NAMES]
        ],
        "published_file_names": [
            "weekly-continuity-bundle.json",
            "archive-manifest.json",
            "deposit-manifest.json",
            "checksums.sha256",
            "README.txt",
            "zenodo-metadata.json",
        ],
        "rights_boundary": {
            "schema": RIGHTS_BOUNDARY_VERSION,
            "license_identifier": ZENODO_LICENSE_ID,
            "publicly_readable_for_preservation_and_research": True,
            "deposit_grants_no_new_reuse_rights": True,
            "embedded_record_chain_entries_retain_their_respective_rights": True,
            "third_party_rights_are_not_transferred": True,
            "publisher_grants_no_rights_it_does_not_possess": True,
            "public_availability_is_not_ownership": True,
        },
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
    verified = verify_local_package(target)
    print(
        f"{target.relative_to(ROOT)} "
        f"package_identity_sha256={verified['package_identity_sha256']}"
    )
    return target


def build() -> Path | None:
    chain = verified_weekly_archive_chain()
    if not chain:
        defer("no verified live Record-Chain Arweave archive is available")
        return None
    targets = [build_archive(*archive) for archive in chain]
    target = targets[-1]
    archive_id = target.name

    github_output("deposit_available", "true")
    github_output("archive_id", archive_id)
    github_output("deposit_dir", str(target.relative_to(ROOT)))
    github_output("deposit_changed", "true")
    github_output("deposit_series_dir", str(DEPOSITS.relative_to(ROOT)))
    print(f"Materialized {len(targets)} verified Weekly Continuity package(s).")
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
            ["git", "diff", "--exit-code", "--", str(DEPOSITS.relative_to(ROOT))],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            check=False,
        )
        if result.returncode != 0:
            raise SystemExit("weekly continuity deposit is not reproducible")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
