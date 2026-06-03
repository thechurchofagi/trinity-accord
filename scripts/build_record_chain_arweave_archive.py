#!/usr/bin/env python3
"""Build record-chain Arweave archive manifest (dry-run or live).

Deterministic archive ID from included batch range + source hash.
Idempotent: skips if same archive already exists.

Boundary: Arweave archive is a mirror/backup only, not authority.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAIN = ROOT / "record-chain"
RECORDS = CHAIN / "records"
BATCHES = CHAIN / "batches"
INDEXES = CHAIN / "indexes"
ARCHIVES = CHAIN / "arweave-archives"
API_INDEX = ROOT / "api" / "record-chain-arweave-index.json"
CHAIN_ID = "trinity-accord-public-reception-ledger"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_dumps(obj), encoding="utf-8")


def existing_batch_manifests():
    return sorted(BATCHES.glob("batch-*/manifest.json"))


def build_archive_id(first_batch_id: str, last_batch_id: str, source_hash: str) -> str:
    return f"archive-{first_batch_id}-{last_batch_id}-{source_hash[:12]}"


def build_payload_json(manifest: dict, archive_dir: Path) -> Path:
    """Build the Arweave upload payload from the manifest."""
    payload = {
        "schema": "trinityaccord.record-chain-arweave-payload.v1",
        "archive_id": manifest["archive_id"],
        "created_at": manifest["created_at"],
        "chain_id": CHAIN_ID,
        "included_batches": [
            {"batch_id": b["batch_id"], "batch_manifest_sha256": b.get("batch_manifest_sha256")}
            for b in manifest.get("included_batches", [])
        ],
        "included_records": [
            {"record_id": r["record_id"], "record_sha256": r.get("record_sha256")}
            for r in manifest.get("included_records", [])
        ],
        "source": manifest.get("source", {}),
        "boundary": {
            "arweave_archive_is_mirror_only": True,
            "arweave_archive_is_not_authority": True,
            "arweave_archive_is_not_attestation": True,
            "arweave_archive_is_not_amendment": True,
            "arweave_archive_is_not_successor_reception": True,
            "bitcoin_originals_prevail": True,
        },
    }
    payload_path = archive_dir / "payload.json"
    write_json(payload_path, payload)
    return payload_path


def upload_to_arweave(payload_path: Path, archive_dir: Path) -> dict:
    """Call Node Arweave uploader and return the result."""
    result_path = archive_dir / "upload-result.json"
    uploader = ROOT / "scripts" / "arweave_upload_payload.mjs"
    if not uploader.exists():
        raise SystemExit(f"Arweave uploader not found: {uploader}")

    cmd = ["node", str(uploader), "--payload", str(payload_path), "--out", str(result_path)]
    env = os.environ.copy()

    result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        print(f"Arweave upload failed:\nstdout: {result.stdout}\nstderr: {result.stderr}", file=sys.stderr)
        raise SystemExit(1)

    print(result.stdout.strip())
    return read_json(result_path)


def build_archive_manifest(mode: str) -> None:
    ARCHIVES.mkdir(parents=True, exist_ok=True)

    chain_tip_path = CHAIN / "chain-tip.json"
    record_index_path = INDEXES / "record-index.json"
    batch_index_path = INDEXES / "batch-index.json"

    if not chain_tip_path.exists():
        print("No chain-tip.json found; nothing to archive.")
        return

    batches = existing_batch_manifests()
    if not batches:
        print("No batch manifests found; nothing to archive.")
        return

    included_batches = []
    included_records = []
    record_ids_seen = set()

    for mf_path in batches:
        mf = read_json(mf_path)
        batch_id = mf.get("batch_id", "")
        # Check if this batch is already in an existing archive via structured index
        already_in_archive = False
        if API_INDEX.exists():
            idx = read_json(API_INDEX)
            for arc in idx.get("archives", []):
                first = arc.get("first_batch_id", "")
                last = arc.get("last_batch_id", "")
                if first and last and first <= batch_id <= last:
                    already_in_archive = True
                    break
        if already_in_archive:
            continue

        ots_file = mf_path.parent / "manifest.json.ots"
        batch_entry = {
            "batch_id": batch_id,
            "manifest_path": str(mf_path.relative_to(ROOT)),
            "batch_manifest_sha256": mf.get("batch_manifest_sha256"),
            "merkle_root_sha256": mf.get("merkle_root_sha256"),
            "ots_file": str(ots_file.relative_to(ROOT)) if ots_file.exists() else None,
            "ots_file_sha256": sha256_file(ots_file) if ots_file.exists() else None,
        }
        included_batches.append(batch_entry)

        for rid in mf.get("record_ids", []):
            if rid in record_ids_seen:
                continue
            record_ids_seen.add(rid)
            rec_path = RECORDS / f"{rid}.json"
            if rec_path.exists():
                rec = read_json(rec_path)
                included_records.append({
                    "record_id": rid,
                    "path": str(rec_path.relative_to(ROOT)),
                    "record_sha256": rec.get("record_sha256"),
                })

    if not included_batches:
        print("No new Arweave archive needed.")
        return

    # Compute deterministic archive ID
    first_batch_id = included_batches[0]["batch_id"]
    last_batch_id = included_batches[-1]["batch_id"]

    # Source hash from concatenating all batch manifest SHA256s
    source_concat = "".join(b["batch_manifest_sha256"] or "" for b in included_batches)
    source_hash = sha256_bytes(source_concat.encode("utf-8"))

    archive_id = build_archive_id(first_batch_id, last_batch_id, source_hash)
    archive_dir = ARCHIVES / archive_id

    if archive_dir.exists():
        # Check idempotency: if archive already has a txid, skip upload
        existing_manifest_path = archive_dir / "manifest.json"
        if existing_manifest_path.exists():
            existing = read_json(existing_manifest_path)
            if existing.get("arweave", {}).get("txid"):
                print(f"Archive {archive_id} already has txid; skipping.")
                return
        print(f"Archive {archive_id} exists locally but no txid; will process.")
    else:
        archive_dir.mkdir(parents=True, exist_ok=True)

    # Build manifest (without archive_manifest_sha256 first)
    manifest = {
        "schema": "trinityaccord.record-chain-arweave-archive-manifest.v1",
        "archive_id": archive_id,
        "created_at": utc_now(),
        "mode": mode,
        "chain_id": CHAIN_ID,
        "source": {
            "chain_tip_path": str(chain_tip_path.relative_to(ROOT)),
            "record_index_path": str(record_index_path.relative_to(ROOT)) if record_index_path.exists() else None,
            "batch_index_path": str(batch_index_path.relative_to(ROOT)) if batch_index_path.exists() else None,
        },
        "included_batches": included_batches,
        "included_records": included_records,
        "archive_manifest_sha256": None,
        "arweave": {
            "enabled": False,
            "upload_mode": mode,
            "txid": None,
            "wallet_address_sha256": None,
            "uploaded_at": None,
            "verified": False,
        },
        "boundary": {
            "not_authority": True,
            "not_attestation": True,
            "not_amendment": True,
            "not_successor_reception": True,
            "bitcoin_originals_prevail": True,
        },
    }

    if mode == "live":
        arkey = os.environ.get("ARKEY")
        if not arkey:
            raise SystemExit("ARKEY required for live Arweave upload")

        # Build payload
        payload_path = build_payload_json(manifest, archive_dir)

        # Upload to Arweave
        upload_result = upload_to_arweave(payload_path, archive_dir)

        # Update manifest with live upload results
        manifest["arweave"] = {
            "enabled": True,
            "upload_mode": "live",
            "txid": upload_result.get("txid"),
            "wallet_address_sha256": upload_result.get("wallet_address_sha256"),
            "uploaded_at": upload_result.get("uploaded_at"),
            "verified": False,
        }
        manifest["mode"] = "live"

    # Compute and set archive_manifest_sha256
    manifest["archive_manifest_sha256"] = sha256_canonical_json(manifest)

    # Write manifest
    write_json(archive_dir / "manifest.json", manifest)

    # Update public index
    update_arweave_index()


def update_arweave_index() -> None:
    archives = sorted(ARCHIVES.glob("*/manifest.json"))
    archive_entries = []
    live_count = 0
    latest_txid = None
    wallet_address_sha256 = None

    for mf_path in archives:
        mf = read_json(mf_path)
        batches = mf.get("included_batches", [])
        arweave = mf.get("arweave", {})
        txid = arweave.get("txid")
        is_live = arweave.get("upload_mode") == "live" and txid is not None

        if is_live:
            live_count += 1
            latest_txid = txid
            if arweave.get("wallet_address_sha256"):
                wallet_address_sha256 = arweave["wallet_address_sha256"]

        archive_entries.append({
            "archive_id": mf.get("archive_id"),
            "mode": mf.get("mode"),
            "manifest_path": str(mf_path.relative_to(ROOT)),
            "archive_manifest_sha256": mf.get("archive_manifest_sha256"),
            "arweave_txid": txid,
            "record_count": len(mf.get("included_records", [])),
            "batch_count": len(batches),
            "first_batch_id": batches[0]["batch_id"] if batches else None,
            "last_batch_id": batches[-1]["batch_id"] if batches else None,
            "created_at": mf.get("created_at"),
        })

    current_mode = "dry-run"
    live_upload_implemented = True
    if live_count > 0:
        current_mode = "live"

    index = {
        "schema": "trinityaccord.record-chain-arweave-index.v1",
        "generated_at": utc_now(),
        "chain_id": CHAIN_ID,
        "current_upload_mode": current_mode,
        "live_upload_enabled": True,
        "live_upload_implemented": live_upload_implemented,
        "arweave_wallet_address_sha256": wallet_address_sha256,
        "latest_arweave_txid": latest_txid,
        "live_archive_count": live_count,
        "archives": archive_entries,
        "boundary": {
            "arweave_archive_is_mirror_only": True,
            "arweave_archive_is_not_authority": True,
            "arweave_archive_is_not_amendment": True,
            "bitcoin_originals_prevail": True,
        },
    }
    write_json(API_INDEX, index)


def main():
    parser = argparse.ArgumentParser(description="Build record-chain Arweave archive manifest")
    parser.add_argument("--mode", choices=["dry-run", "live", "verify-only"], default="dry-run")
    args = parser.parse_args()

    if args.mode == "verify-only":
        print("Use verify_record_chain_arweave_archive.py for verification.")
        return

    build_archive_manifest(mode=args.mode)


if __name__ == "__main__":
    main()
