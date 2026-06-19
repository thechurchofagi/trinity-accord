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
NATIVE_OTS_LATEST = ROOT / "api" / "record-chain-native-ots-latest.json"
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


def archive_status_from_upload(upload_result: dict) -> str:
    if upload_result.get("txid") and upload_result.get("hash_match") is True and upload_result.get("result") == "uploaded":
        return "archived"
    if upload_result.get("result") == "readback_failed" or (upload_result.get("txid") and upload_result.get("hash_match") is not True):
        return "readback_failed"
    return "upload_failed"


def refresh_archive_backlog() -> None:
    detector = ROOT / "scripts" / "detect_archive_backlog.py"
    if detector.exists():
        subprocess.run([sys.executable, str(detector), "--write"], cwd=ROOT, check=False)


def record_wallet_upload(upload_result_path: Path, source_path: Path) -> None:
    if not upload_result_path.exists():
        return
    subprocess.run(
        [
            sys.executable,
            "scripts/record_arweave_upload_result.py",
            "--upload-result-json",
            str(upload_result_path),
            "--kind",
            "record_chain_arweave_archive",
            "--source-path",
            str(source_path.relative_to(ROOT)),
        ],
        cwd=ROOT,
        check=True,
    )

def source_file_ref(path: Path) -> dict:
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
    }



def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_dumps(obj), encoding="utf-8")




def load_native_chain_sources() -> dict:
    chain_tip_path = CHAIN / "chain-tip.json"
    record_index_path = INDEXES / "record-index.json"
    guardian_state_path = INDEXES / "guardian-state.json"
    statistics_path = INDEXES / "statistics.json"
    batch_index_path = INDEXES / "batch-index.json"

    chain_tip = read_json(chain_tip_path)
    record_index = read_json(record_index_path)

    if chain_tip.get("schema") != "trinityaccord.chain-tip.v1":
        raise SystemExit(f"unexpected chain-tip schema: {chain_tip.get('schema')}")
    if record_index.get("schema") != "trinityaccord.record-index.v1":
        raise SystemExit(f"unexpected record-index schema: {record_index.get('schema')}")

    native_count = chain_tip.get("native_record_count")
    latest_record_id = chain_tip.get("latest_record_id")
    latest_record_sha256 = chain_tip.get("latest_record_sha256")
    records = record_index.get("records", [])

    if not isinstance(records, list):
        raise SystemExit("record-index.records must be list")
    if len(records) != native_count:
        raise SystemExit(
            f"record-index count mismatch: records={len(records)} native_record_count={native_count}"
        )
    if not records or records[-1].get("record_id") != latest_record_id:
        raise SystemExit("record-index latest_record_id does not match chain-tip")
    if records[-1].get("record_sha256") != latest_record_sha256:
        raise SystemExit("record-index latest_record_sha256 does not match chain-tip")

    included_records = []
    for i, rec in enumerate(records, start=1):
        expected_id = f"R-{i:09d}"
        if rec.get("record_id") != expected_id:
            raise SystemExit(f"record sequence mismatch: expected {expected_id}, got {rec.get('record_id')}")
        rec_path = ROOT / rec.get("path", "")
        if not rec_path.exists():
            raise SystemExit(f"record file missing: {rec_path}")
        rec_data = read_json(rec_path)
        if rec_data.get("record_sha256") != rec.get("record_sha256"):
            raise SystemExit(f"record sha mismatch: {rec.get('record_id')}")
        included_records.append({
            "record_id": rec["record_id"],
            "path": rec["path"],
            "record_type": rec.get("record_type"),
            "record_sha256": rec["record_sha256"],
            "raw_file_sha256": sha256_file(rec_path),
            "bytes": rec_path.stat().st_size,
        })

    included_batches = []
    if batch_index_path.exists():
        batch_index = read_json(batch_index_path)
        for b in batch_index.get("batches", []):
            if not isinstance(b, dict):
                continue
            manifest_path_value = b.get("path")
            if not isinstance(manifest_path_value, str):
                continue
            manifest_path = ROOT / manifest_path_value
            if not manifest_path.exists():
                raise SystemExit(f"batch manifest missing: {manifest_path}")
            mf = read_json(manifest_path)
            included_batches.append({
                "batch_id": b.get("batch_id"),
                "manifest_path": manifest_path_value,
                "batch_manifest_sha256": mf.get("batch_manifest_sha256"),
                "merkle_root_sha256": mf.get("merkle_root_sha256"),
                "first_record_index": mf.get("first_record_index"),
                "last_record_index": mf.get("last_record_index"),
                "record_count": mf.get("record_count"),
                "coverage_is_auxiliary": True,
            })

    native_ots_latest_ref = None
    if NATIVE_OTS_LATEST.exists():
        native_ots_latest = read_json(NATIVE_OTS_LATEST)
        native_ots_latest_ref = {
            "path": str(NATIVE_OTS_LATEST.relative_to(ROOT)),
            "sha256": sha256_file(NATIVE_OTS_LATEST),
            "schema": native_ots_latest.get("schema"),
            "latest_record_id": native_ots_latest.get("latest_record_id"),
            "latest_record_sha256": native_ots_latest.get("latest_record_sha256"),
            "native_record_count": native_ots_latest.get("native_record_count"),
            "latest_anchor_file": native_ots_latest.get("latest_anchor_file"),
            "latest_anchored_file": native_ots_latest.get("latest_anchored_file"),
            "ots_status": native_ots_latest.get("ots_status"),
            "bitcoin_pending": native_ots_latest.get("bitcoin_pending"),
            "bitcoin_verified": native_ots_latest.get("bitcoin_verified"),
            "bitcoin_attestation_embedded": native_ots_latest.get("bitcoin_attestation_embedded"),
            "strict_bitcoin_verified": native_ots_latest.get("strict_bitcoin_verified"),
        }

    source_files = {
        "chain_tip": source_file_ref(chain_tip_path),
        "record_index": source_file_ref(record_index_path),
        "guardian_state": source_file_ref(guardian_state_path),
        "statistics": source_file_ref(statistics_path),
    }
    if batch_index_path.exists():
        source_files["batch_index"] = source_file_ref(batch_index_path)

    return {
        "chain_tip": chain_tip,
        "record_index": record_index,
        "included_records": included_records,
        "included_batches": included_batches,
        "source_files": source_files,
        "native_ots_latest": native_ots_latest_ref,
    }

def existing_batch_manifests():
    return sorted(BATCHES.glob("batch-*/manifest.json"))


def build_archive_id(first_batch_id: str, last_batch_id: str, source_hash: str) -> str:
    return f"archive-{first_batch_id}-{last_batch_id}-{source_hash[:12]}"


def build_payload_json(manifest: dict, archive_dir: Path) -> Path:
    """Build the Arweave upload payload from the manifest.

    Includes full record content (base64-encoded) so the archive is reconstructable.
    """
    included_records = []
    for r in manifest.get("included_records", []):
        rec_path = ROOT / r.get("path", "")
        raw_bytes = rec_path.read_bytes() if rec_path.exists() else b""
        included_records.append({
            "record_id": r["record_id"],
            "path": r.get("path"),
            "record_sha256": r.get("record_sha256"),
            "raw_file_sha256": sha256_bytes(raw_bytes),
            "bytes": len(raw_bytes),
            "content_base64": __import__("base64").b64encode(raw_bytes).decode("ascii"),
        })

    payload = {
        "schema": "trinityaccord.record-chain-arweave-payload.v1",
        "archive_id": manifest["archive_id"],
        "created_at": manifest["created_at"],
        "chain_id": CHAIN_ID,
        "included_batches": [
            {"batch_id": b["batch_id"], "batch_manifest_sha256": b.get("batch_manifest_sha256")}
            for b in manifest.get("included_batches", [])
        ],
        "included_records": included_records,
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

    timeout_seconds = int(os.environ.get("ARWEAVE_UPLOAD_TIMEOUT_SECONDS", "600"))
    print(f"Arweave upload timeout: {timeout_seconds}s")
    result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=timeout_seconds)
    if result.returncode != 0:
        print(f"Arweave upload failed:\nstdout: {result.stdout}\nstderr: {result.stderr}", file=sys.stderr)
        raise SystemExit(1)

    print(result.stdout.strip())
    return read_json(result_path)


def build_archive_manifest(mode: str) -> None:
    ARCHIVES.mkdir(parents=True, exist_ok=True)

    native = load_native_chain_sources()
    chain_tip = native["chain_tip"]
    included_records = native["included_records"]
    included_batches = native["included_batches"]

    latest_record_id = chain_tip["latest_record_id"]
    latest_record_sha256 = chain_tip["latest_record_sha256"]
    native_record_count = chain_tip["native_record_count"]

    if not included_records:
        print("No native records found; nothing to archive.")
        return

    # Idempotency: skip if native archive for this head already has txid
    for existing_manifest_path in ARCHIVES.glob("*/manifest.json"):
        existing = read_json(existing_manifest_path)
        source = existing.get("source", {})
        native_source = source.get("native_chain", {})
        if (
            native_source.get("latest_record_id") == latest_record_id
            and native_source.get("latest_record_sha256") == latest_record_sha256
            and native_source.get("native_record_count") == native_record_count
            and existing.get("arweave", {}).get("txid")
            and existing.get("arweave", {}).get("archive_status", "archived") == "archived"
        ):
            print(f"No new Arweave archive needed: native archive for {latest_record_id} already has txid; skipping.")
            return

    # Compute deterministic archive ID from native source
    source_hash_input = {
        "latest_record_id": latest_record_id,
        "latest_record_sha256": latest_record_sha256,
        "native_record_count": native_record_count,
        "record_index_sha256": native["source_files"]["record_index"]["sha256"],
        "native_ots_latest_sha256": (
            native["native_ots_latest"]["sha256"] if native["native_ots_latest"] else None
        ),
    }
    source_hash = sha256_canonical_json(source_hash_input)
    archive_id = f"archive-native-{latest_record_id}-{source_hash[:12]}"
    archive_dir = ARCHIVES / archive_id

    if archive_dir.exists():
        existing_manifest_path = archive_dir / "manifest.json"
        if existing_manifest_path.exists():
            existing = read_json(existing_manifest_path)
            if existing.get("arweave", {}).get("txid"):
                print(f"No new Arweave archive needed: archive {archive_id} already has txid; skipping.")
                return
        print(f"Archive {archive_id} exists locally but no txid; will process.")
    else:
        archive_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "schema": "trinityaccord.record-chain-arweave-archive-manifest.v1",
        "archive_id": archive_id,
        "created_at": utc_now(),
        "mode": mode,
        "chain_id": CHAIN_ID,
        "source": {
            "source_type": "native-record-chain",
            "chain_tip_path": "record-chain/chain-tip.json",
            "record_index_path": "record-chain/indexes/record-index.json",
            "batch_index_path": "record-chain/indexes/batch-index.json",
            "native_chain": {
                "latest_record_id": latest_record_id,
                "latest_record_sha256": latest_record_sha256,
                "native_record_count": native_record_count,
                "legacy_main_chain_jsonl_is_not_source": True,
                "latest_batch_id": chain_tip.get("latest_batch_id"),
                "latest_batch_manifest_sha256": chain_tip.get("latest_batch_manifest_sha256"),
            },
            "source_files": native["source_files"],
            "native_ots_latest": native["native_ots_latest"],
            "legacy_main_chain_jsonl_is_not_source": True,
            "batch_manifests_are_auxiliary": True,
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
            "archive_status": "pending_upload",
            "retry_count": 0,
            "last_attempt_at": None,
            "last_error": None,
            "hash_match": False,
        },
        "boundary": {
            "not_authority": True,
            "not_attestation": True,
            "not_amendment": True,
            "not_successor_reception": True,
            "bitcoin_originals_prevail": True,
        },
    }

    # Hard gate: refuse live upload if native OTS is not archivable
    native_ots_latest_data = read_json(NATIVE_OTS_LATEST) if NATIVE_OTS_LATEST.exists() else {}
    ots_archivable, ots_errors = native_ots_archivable_for_chain(native_ots_latest_data, chain_tip)

    if mode == "live" and not ots_archivable:
        raise SystemExit(
            "refusing live Arweave archive because native OTS latest is not archivable: "
            + "; ".join(ots_errors)
        )

    if mode != "live" and not ots_archivable:
        print(
            "WARN: native OTS latest is not archivable yet; dry-run continues: "
            + "; ".join(ots_errors),
            file=sys.stderr,
        )

    upload_failed = False
    if mode == "live":
        arkey = os.environ.get("ARKEY")
        if not arkey:
            manifest["arweave"].update({
                "enabled": True,
                "upload_mode": "live",
                "archive_status": "waiting_for_key",
                "last_attempt_at": utc_now(),
                "last_error": "ARKEY required for live Arweave upload",
                "next_action": "provide_arweave_key",
            })
            upload_failed = True
        else:
            payload_path = build_payload_json(manifest, archive_dir)
            # Bind payload hash into manifest after building
            manifest["payload"] = {
                "path": str(payload_path.relative_to(ROOT)),
                "sha256": sha256_file(payload_path),
                "bytes": payload_path.stat().st_size,
                "canonicalization": "json.sort_keys.no_whitespace.utf8.allow_nan_false.v1",
            }
            # Recompute archive_manifest_sha256 after payload binding
            # Must clear before computing to match verifier's None-reset approach
            manifest["archive_manifest_sha256"] = None
            manifest["archive_manifest_sha256"] = sha256_canonical_json(manifest)
            try:
                upload_result = upload_to_arweave(payload_path, archive_dir)
            except subprocess.TimeoutExpired as exc:
                manifest["arweave"].update({
                    "enabled": True,
                    "upload_mode": "live",
                    "archive_status": "upload_failed",
                    "last_attempt_at": utc_now(),
                    "last_error": f"Arweave upload timed out after {timeout_seconds}s: {exc}",
                    "next_action": "retry_upload",
                })
                upload_failed = True
            except SystemExit as exc:
                partial = archive_dir / "upload-result.json"
                upload_result = read_json(partial) if partial.exists() else {}

                # If Arweave already returned a tx_id before readback failed, record the wallet spend.
                if upload_result.get("txid") or upload_result.get("tx_id"):
                    record_wallet_upload(partial, payload_path)

                status = archive_status_from_upload(upload_result) if upload_result else "upload_failed"
                manifest["arweave"].update({
                    "enabled": True,
                    "upload_mode": "live",
                    "txid": upload_result.get("txid") or upload_result.get("tx_id"),
                    "wallet_address_sha256": upload_result.get("wallet_address_sha256"),
                    "uploaded_at": upload_result.get("uploaded_at"),
                    "verified": False,
                    "hash_match": upload_result.get("hash_match", False),
                    "readback_sha256": upload_result.get("readback_sha256"),
                    "archive_status": status,
                    "last_attempt_at": utc_now(),
                    "last_error": str(exc),
                    "next_action": "retry_readback_or_upload" if status == "readback_failed" else "retry_upload",
                })
                upload_failed = True
            else:
                status = archive_status_from_upload(upload_result)

                result_path = archive_dir / "upload-result.json"
                if upload_result.get("txid") or upload_result.get("tx_id"):
                    record_wallet_upload(result_path, payload_path)

                manifest["arweave"] = {
                    "enabled": True,
                    "upload_mode": "live",
                    "txid": upload_result.get("txid") or upload_result.get("tx_id"),
                    "wallet_address_sha256": upload_result.get("wallet_address_sha256"),
                    "uploaded_at": upload_result.get("uploaded_at"),
                    "verified": status == "archived",
                    "hash_match": upload_result.get("hash_match", False),
                    "readback_sha256": upload_result.get("readback_sha256"),
                    "archive_status": status,
                    "retry_count": 0,
                    "last_attempt_at": utc_now(),
                    "last_error": None if status == "archived" else upload_result.get("result"),
                    "next_action": "no_op" if status == "archived" else "retry_readback_or_upload",
                }
                upload_failed = status != "archived"
        manifest["mode"] = "live"

    manifest["archive_manifest_sha256"] = None
    manifest["archive_manifest_sha256"] = sha256_canonical_json(manifest)
    write_json(archive_dir / "manifest.json", manifest)
    update_arweave_index()
    refresh_archive_backlog()
    if upload_failed:
        raise SystemExit(1)



def native_ots_archivable_for_chain(native_ots_latest: dict, chain_tip: dict) -> tuple[bool, list[str]]:
    errors: list[str] = []

    if not native_ots_latest:
        return False, ["api/record-chain-native-ots-latest.json missing or empty"]

    expected = {
        "latest_record_id": chain_tip.get("latest_record_id"),
        "latest_record_sha256": chain_tip.get("latest_record_sha256"),
        "native_record_count": chain_tip.get("native_record_count"),
    }

    for key, value in expected.items():
        if native_ots_latest.get(key) != value:
            errors.append(f"{key} mismatch")

    if native_ots_latest.get("legacy_main_chain_jsonl_is_not_source") is not True:
        errors.append("legacy_main_chain_jsonl_is_not_source is not true")

    is_strictly_verified = (
        native_ots_latest.get("ots_status") == "verified"
        and native_ots_latest.get("bitcoin_verified") is True
        and native_ots_latest.get("strict_bitcoin_verified") is True
    )

    has_bitcoin_attestation = (
        native_ots_latest.get("ots_status") == "upgraded"
        and native_ots_latest.get("bitcoin_attestation_embedded") is True
        and native_ots_latest.get("bitcoin_pending") is False
    )

    if not (is_strictly_verified or has_bitcoin_attestation):
        errors.append(
            "native OTS is not archivable; expected verified+bitcoin_verified=true+strict_bitcoin_verified=true "
            "or upgraded+bitcoin_attestation_embedded=true+bitcoin_pending=false"
        )

    return not errors, errors


def _is_verified_live_archive_entry(entry: dict[str, Any]) -> bool:
    """Check if an archive entry qualifies as a strict verified live archive."""
    return (
        bool(entry.get("arweave_txid"))
        and entry.get("source_type") == "native-record-chain"
        and entry.get("mode") == "live"
        and entry.get("archive_status") == "archived"
        and entry.get("verified") is True
        and entry.get("hash_match") is True
    )


def update_arweave_index() -> None:
    archives = sorted(ARCHIVES.glob("*/manifest.json"))
    archive_entries = []
    live_attempt_count = 0
    verified_live_count = 0
    latest_txid = None
    wallet_address_sha256 = None

    for mf_path in archives:
        mf = read_json(mf_path)
        batches = mf.get("included_batches", [])
        arweave = mf.get("arweave", {})
        txid = arweave.get("txid")
        is_live = arweave.get("upload_mode") == "live" and txid is not None

        if is_live:
            live_attempt_count += 1
            if arweave.get("wallet_address_sha256"):
                wallet_address_sha256 = arweave["wallet_address_sha256"]

        source = mf.get("source", {})
        native_chain = source.get("native_chain", {})
        entry = {
            "archive_id": mf.get("archive_id"),
            "mode": mf.get("mode"),
            "manifest_path": str(mf_path.relative_to(ROOT)),
            "archive_manifest_sha256": mf.get("archive_manifest_sha256"),
            "arweave_txid": txid,
            "record_count": len(mf.get("included_records", [])),
            "batch_count": len(batches),
            "first_batch_id": batches[0]["batch_id"] if batches else None,
            "last_batch_id": batches[-1]["batch_id"] if batches else None,
            "source_type": source.get("source_type"),
            "native_latest_record_id": native_chain.get("latest_record_id"),
            "native_latest_record_sha256": native_chain.get("latest_record_sha256"),
            "native_record_count": native_chain.get("native_record_count"),
            "native_ots_latest": source.get("native_ots_latest"),
            "created_at": mf.get("created_at"),
            # Verification fields from arweave block
            "archive_status": arweave.get("archive_status"),
            "verified": arweave.get("verified") is True,
            "hash_match": arweave.get("hash_match") is True,
            "readback_sha256": arweave.get("readback_sha256"),
            "wallet_address_sha256": arweave.get("wallet_address_sha256"),
            "uploaded_at": arweave.get("uploaded_at"),
            "last_attempt_at": arweave.get("last_attempt_at"),
            "last_error": arweave.get("last_error"),
            "next_action": arweave.get("next_action"),
        }
        archive_entries.append(entry)

        # Count verified live archives for strict current gate
        if _is_verified_live_archive_entry(entry):
            verified_live_count += 1
            latest_txid = txid

    current_mode = "dry-run"
    live_upload_implemented = True
    if verified_live_count > 0:
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
        "live_archive_count": verified_live_count,
        "verified_live_archive_count": verified_live_count,
        "live_upload_attempt_count": live_attempt_count,
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
