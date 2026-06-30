#!/usr/bin/env python3
"""Verify record-chain Arweave archive metadata integrity."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAIN = ROOT / "record-chain"
CHAIN_TIP = CHAIN / "chain-tip.json"
API_INDEX = ROOT / "api" / "record-chain-arweave-index.json"
FORBIDDEN_TERMS = {"ARV5", "LV5", "IVV5", "IPFS"}


def canonical_dumps(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_canonical_json(obj) -> str:
    return sha256_bytes(canonical_dumps(obj).encode("utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def verify_txid_shape(txid: str) -> bool:
    if not txid or not isinstance(txid, str):
        return False
    import string
    allowed = set(string.ascii_letters + string.digits + "-_")
    return len(txid) >= 40 and all(c in allowed for c in txid)


def find_latest_live_native_archive(archives: list[dict]) -> dict | None:
    latest = None
    for archive in archives:
        manifest_path = ROOT / archive.get("manifest_path", "")
        if not manifest_path.exists():
            continue
        manifest = read_json(manifest_path)
        source = manifest.get("source", {})
        if source.get("source_type") != "native-record-chain":
            continue
        if manifest.get("mode") == "dry-run":
            continue
        native_chain = source.get("native_chain", {})
        record_id = native_chain.get("latest_record_id", "")
        if latest is None or record_id > latest.get("_record_id", ""):
            latest = {
                "_record_id": record_id,
                "_native_chain": native_chain,
                "_archive_id": archive.get("archive_id", ""),
            }
    return latest


def verify_native_archive_self_consistency(archive_id: str, manifest: dict, native_chain: dict) -> list[str]:
    errors = []
    archive_native_count = native_chain.get("native_record_count")
    archive_latest_id = native_chain.get("latest_record_id")
    archive_latest_sha = native_chain.get("latest_record_sha256")
    included_records = manifest.get("included_records", [])

    if isinstance(archive_native_count, int) and len(included_records) != archive_native_count:
        errors.append(
            f"{archive_id}: included_records does not cover native_record_count; "
            f"included_records_count={len(included_records)} native_record_count={archive_native_count}"
        )

    if archive_latest_id and not any(
        r.get("record_id") == archive_latest_id and r.get("record_sha256") == archive_latest_sha
        for r in included_records
    ):
        errors.append(f"{archive_id}: latest native record missing from included_records; latest_record_id={archive_latest_id}")

    if native_chain.get("legacy_main_chain_jsonl_is_not_source") is not True:
        errors.append(f"{archive_id}: native archive must declare legacy JSONL is not source")

    if "main.chain.jsonl" in canonical_dumps(manifest):
        errors.append(f"{archive_id}: native archive must not reference main.chain.jsonl")

    return errors


def verify_latest_archive_covers_chain_tip(latest_archive_id: str, native_chain: dict, chain_tip: dict) -> list[str]:
    errors = []
    if native_chain.get("latest_record_id") != chain_tip.get("latest_record_id"):
        errors.append(
            f"latest live archive ({latest_archive_id}): native latest_record_id "
            f"({native_chain.get('latest_record_id')}) does not match chain-tip ({chain_tip.get('latest_record_id')})"
        )
    if native_chain.get("latest_record_sha256") != chain_tip.get("latest_record_sha256"):
        errors.append(f"latest live archive ({latest_archive_id}): native latest_record_sha256 mismatch")
    if native_chain.get("native_record_count") != chain_tip.get("native_record_count"):
        errors.append(
            f"latest live archive ({latest_archive_id}): native_record_count ({native_chain.get('native_record_count')}) "
            f"does not match chain-tip ({chain_tip.get('native_record_count')})"
        )
    return errors


def verify(
    network: bool = False,
    strict_network: bool = False,
    allow_stale_live_chain_tip: bool = False,
) -> list[str]:
    errors: list[str] = []

    if network or strict_network:
        print("WARN: network transaction lookup is skipped in this metadata verifier", file=sys.stderr)

    if not API_INDEX.exists():
        return ["api/record-chain-arweave-index.json missing"]

    index = read_json(API_INDEX)
    boundary = index.get("boundary", {})
    for key in [
        "arweave_archive_is_mirror_only",
        "arweave_archive_is_not_authority",
        "arweave_archive_is_not_amendment",
        "bitcoin_originals_prevail",
    ]:
        if not boundary.get(key):
            errors.append(f"index boundary missing/false: {key}")

    index_text = canonical_dumps(index)
    for term in FORBIDDEN_TERMS:
        if term in index_text:
            errors.append(f"forbidden current terminology '{term}' found in arweave index")

    latest_live = find_latest_live_native_archive(index.get("archives", []))

    for archive in index.get("archives", []):
        archive_id = archive.get("archive_id", "unknown")
        manifest_path = ROOT / archive.get("manifest_path", "")
        if not manifest_path.exists():
            errors.append(f"archive manifest missing: {manifest_path}")
            continue

        manifest = read_json(manifest_path)
        computed = dict(manifest)
        computed["archive_manifest_sha256"] = None
        expected_sha = sha256_canonical_json(computed)
        if manifest.get("archive_manifest_sha256") != expected_sha:
            errors.append(f"{archive_id}: archive_manifest_sha256 mismatch")

        arweave = manifest.get("arweave", {})
        if manifest.get("mode") == "dry-run" and arweave.get("txid") is not None:
            errors.append(f"{archive_id}: dry-run but claims arweave_txid")

        if manifest.get("mode") == "live" and arweave.get("txid"):
            if arweave.get("archive_status") == "archived":
                if arweave.get("verified") is not True:
                    errors.append(f"{archive_id}: archive_status=archived but verified is not true")
                if arweave.get("hash_match") is not True:
                    errors.append(f"{archive_id}: archive_status=archived but hash_match is not true")
            if arweave.get("verified") is True and arweave.get("hash_match") is not True:
                errors.append(f"{archive_id}: verified=true but hash_match is not true")

        m_boundary = manifest.get("boundary", {})
        for key in ["not_authority", "not_attestation", "not_amendment", "not_successor_reception", "bitcoin_originals_prevail"]:
            if not m_boundary.get(key):
                errors.append(f"{archive_id}: manifest boundary missing/false: {key}")

        source = manifest.get("source", {})
        if source.get("source_type") == "native-record-chain":
            native_chain = source.get("native_chain", {})
            errors.extend(verify_native_archive_self_consistency(archive_id, manifest, native_chain))

            if latest_live and archive_id == latest_live["_archive_id"]:
                chain_tip = read_json(CHAIN_TIP)
                live_errors = verify_latest_archive_covers_chain_tip(archive_id, native_chain, chain_tip)
                if allow_stale_live_chain_tip and live_errors:
                    for error in live_errors:
                        print(f"WARN: {error} (allowed while live archive catches up)", file=sys.stderr)
                else:
                    errors.extend(live_errors)

        for batch in manifest.get("included_batches", []):
            batch_path = ROOT / batch.get("manifest_path", "")
            if not batch_path.exists():
                errors.append(f"{archive_id}: batch manifest missing: {batch_path}")
                continue
            batch_data = read_json(batch_path)
            if batch_data.get("batch_manifest_sha256") != batch.get("batch_manifest_sha256"):
                errors.append(f"{archive_id}: batch {batch.get('batch_id')} sha mismatch")

        for rec in manifest.get("included_records", []):
            rec_path = ROOT / rec.get("path", "")
            if not rec_path.exists():
                errors.append(f"{archive_id}: record missing: {rec_path}")
                continue
            rec_data = read_json(rec_path)
            if rec_data.get("record_sha256") != rec.get("record_sha256"):
                errors.append(f"{archive_id}: record {rec.get('record_id')} sha mismatch")
            actual_raw_sha = sha256_file(rec_path)
            if rec.get("raw_file_sha256") and rec["raw_file_sha256"] != actual_raw_sha:
                errors.append(
                    f"{archive_id}: record {rec.get('record_id')} raw_file_sha256 mismatch: "
                    f"manifest={rec['raw_file_sha256'][:16]} actual={actual_raw_sha[:16]}"
                )
            rec_body = dict(rec_data)
            rec_body.pop("record_sha256", None)
            expected_record_sha = sha256_canonical_json(rec_body)
            if rec_data.get("record_sha256") != expected_record_sha:
                errors.append(f"{archive_id}: record {rec.get('record_id')} record_sha256 does not match recomputed hash")

        manifest_text = canonical_dumps(manifest)
        for term in FORBIDDEN_TERMS:
            if term in manifest_text:
                errors.append(f"{archive_id}: forbidden term '{term}' in manifest")

        txid = arweave.get("txid")
        if txid and not verify_txid_shape(txid):
            errors.append(f"{archive_id}: invalid txid shape: {txid[:20]}...")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify record-chain Arweave archive metadata")
    parser.add_argument("--network", action="store_true", help="Verify Arweave transactions on network")
    parser.add_argument("--strict-network", action="store_true", help="Fail on network propagation delays")
    parser.add_argument("--allow-stale-live-chain-tip", action="store_true", help="Warn instead of failing when the latest live archive lags the current chain-tip")
    args = parser.parse_args()

    errors = verify(
        network=args.network,
        strict_network=args.strict_network,
        allow_stale_live_chain_tip=args.allow_stale_live_chain_tip,
    )
    if errors:
        print("Arweave archive verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)
    print("Arweave archive verification passed.")


if __name__ == "__main__":
    main()
