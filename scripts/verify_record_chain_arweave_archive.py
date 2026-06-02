#!/usr/bin/env python3
"""Verify record-chain Arweave archive metadata integrity.

Checks:
- archive_manifest_sha256 recomputation
- included batch manifests exist and match
- included records exist and match
- dry-run entries do not claim arweave_txid
- boundary fields
- no ARV5/LV5/IPFS current terminology in index
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAIN = ROOT / "record-chain"
RECORDS = CHAIN / "records"
BATCHES = CHAIN / "batches"
ARCHIVES = CHAIN / "arweave-archives"
API_INDEX = ROOT / "api" / "record-chain-arweave-index.json"

FORBIDDEN_TERMS = {"ARV5", "LV5", "IVV5", "IPFS"}


def canonical_dumps(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def canonical_bytes(obj):
    return canonical_dumps(obj).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_canonical_json(obj) -> str:
    return sha256_bytes(canonical_bytes(obj))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def verify() -> list[str]:
    errors: list[str] = []

    if not API_INDEX.exists():
        errors.append("api/record-chain-arweave-index.json missing")
        return errors

    index = read_json(API_INDEX)

    # Check boundary fields
    boundary = index.get("boundary", {})
    for key in ["arweave_archive_is_mirror_only", "arweave_archive_is_not_authority",
                 "arweave_archive_is_not_amendment", "bitcoin_originals_prevail"]:
        if not boundary.get(key):
            errors.append(f"index boundary missing/false: {key}")

    # Check for forbidden terminology in the index JSON
    index_text = canonical_dumps(index)
    for term in FORBIDDEN_TERMS:
        if term in index_text:
            errors.append(f"forbidden current terminology '{term}' found in arweave index")

    for archive in index.get("archives", []):
        manifest_path = ROOT / archive.get("manifest_path", "")
        if not manifest_path.exists():
            errors.append(f"archive manifest missing: {manifest_path}")
            continue

        manifest = read_json(manifest_path)

        # Recompute archive_manifest_sha256
        computed = dict(manifest)
        computed["archive_manifest_sha256"] = None
        expected_sha = sha256_canonical_json(computed)
        if manifest.get("archive_manifest_sha256") != expected_sha:
            errors.append(f"{archive['archive_id']}: archive_manifest_sha256 mismatch")

        # Check arweave boundary
        arweave = manifest.get("arweave", {})
        if manifest.get("mode") == "dry-run" and arweave.get("txid") is not None:
            errors.append(f"{archive['archive_id']}: dry-run but claims arweave_txid")

        # Check boundary fields in manifest
        m_boundary = manifest.get("boundary", {})
        for key in ["not_authority", "not_attestation", "not_amendment",
                     "not_successor_reception", "bitcoin_originals_prevail"]:
            if not m_boundary.get(key):
                errors.append(f"{archive['archive_id']}: manifest boundary missing/false: {key}")

        # Check included batches
        for batch in manifest.get("included_batches", []):
            batch_path = ROOT / batch.get("manifest_path", "")
            if not batch_path.exists():
                errors.append(f"{archive['archive_id']}: batch manifest missing: {batch_path}")
                continue
            batch_data = read_json(batch_path)
            if batch_data.get("batch_manifest_sha256") != batch.get("batch_manifest_sha256"):
                errors.append(f"{archive['archive_id']}: batch {batch.get('batch_id')} sha mismatch")

        # Check included records
        for rec in manifest.get("included_records", []):
            rec_path = ROOT / rec.get("path", "")
            if not rec_path.exists():
                errors.append(f"{archive['archive_id']}: record missing: {rec_path}")
                continue
            rec_data = read_json(rec_path)
            if rec_data.get("record_sha256") != rec.get("record_sha256"):
                errors.append(f"{archive['archive_id']}: record {rec.get('record_id')} sha mismatch")

        # Check forbidden terminology in manifest
        manifest_text = canonical_dumps(manifest)
        for term in FORBIDDEN_TERMS:
            if term in manifest_text:
                errors.append(f"{archive['archive_id']}: forbidden term '{term}' in manifest")

    return errors


def main():
    errors = verify()
    if errors:
        print("Arweave archive verification failed:", file=sys.stderr)
        for e in errors:
            print(f"- {e}", file=sys.stderr)
        raise SystemExit(1)
    print("Arweave archive verification passed.")


if __name__ == "__main__":
    main()
