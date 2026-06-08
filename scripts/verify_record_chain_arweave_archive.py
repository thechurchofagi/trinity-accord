#!/usr/bin/env python3
"""Verify record-chain Arweave archive metadata integrity.

Checks:
- archive_manifest_sha256 recomputation
- included batch manifests exist and match
- included records exist and match
- dry-run entries do not claim arweave_txid
- boundary fields
- no ARV5/LV5/IPFS current terminology in index

Native archive validation semantics:
- Each historical native archive is verified against its OWN snapshot
  (source.native_chain fields vs included_records), not the current chain-tip.
- Only the latest live native archive is checked against the current chain-tip
  to ensure archive coverage is up to date.

Optional network verification:
- --network: GET arweave.net/<txid> and compare body SHA256; warn on propagation delay
- --strict-network: same as --network but fail on propagation delay
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAIN = ROOT / "record-chain"
RECORDS = CHAIN / "records"
BATCHES = CHAIN / "batches"
ARCHIVES = CHAIN / "arweave-archives"
API_INDEX = ROOT / "api" / "record-chain-arweave-index.json"
INDEXES = CHAIN / "indexes"
CHAIN_TIP = CHAIN / "chain-tip.json"

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


def verify_txid_shape(txid: str) -> bool:
    """Verify txid looks like a valid Arweave transaction ID (base64url, 43 chars)."""
    if not txid or not isinstance(txid, str):
        return False
    import string
    allowed = set(string.ascii_letters + string.digits + "-_")
    return len(txid) >= 40 and all(c in allowed for c in txid)


def verify_network(txid: str, expected_sha256: str, strict: bool) -> list[str]:
    """Verify Arweave transaction is available on network and matches payload hash."""
    errors = []
    url = f"https://arweave.net/{txid}"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read()
    except urllib.error.HTTPError as exc:
        msg = f"Arweave network fetch failed for txid={txid}: HTTP {exc.code}"
        if strict:
            errors.append(msg)
        else:
            print(f"WARN: {msg} (propagation delay?)")
        return errors
    except Exception as exc:
        msg = f"Arweave network fetch failed for txid={txid}: {type(exc).__name__}"
        if strict:
            errors.append(msg)
        else:
            print(f"WARN: {msg} (propagation delay?)")
        return errors

    body_sha = sha256_bytes(body)
    if body_sha != expected_sha256:
        errors.append(f"Arweave body SHA256 mismatch for txid={txid}: expected={expected_sha256[:16]} got={body_sha[:16]}")
    else:
        print(f"PASS: Arweave network verification ok for txid={txid}")

    return errors


def find_latest_live_native_archive(archives: list[dict]) -> dict | None:
    """Find the latest live (non-dry-run) native archive from the index."""
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
                "_manifest": manifest,
            }
    return latest


def verify_native_archive_self_consistency(
    archive_id: str,
    manifest: dict,
    native_chain: dict,
) -> list[str]:
    """Verify a native archive against its own snapshot (self-consistency).

    Historical archives are checked for internal consistency only:
    - included_records count matches the archive's own native_record_count
    - included_records contains the archive's own latest_record_id/record_sha256
    - included record files exist and SHA matches
    - legacy JSONL references are absent
    """
    errors = []
    archive_native_count = native_chain.get("native_record_count")
    archive_latest_id = native_chain.get("latest_record_id")
    archive_latest_sha = native_chain.get("latest_record_sha256")

    included_records = manifest.get("included_records", [])

    # Check included_records count matches archive's own count
    if isinstance(archive_native_count, int) and len(included_records) != archive_native_count:
        errors.append(
            f"{archive_id}: included_records count ({len(included_records)}) "
            f"does not match archive native_record_count ({archive_native_count})"
        )

    # Check archive's own latest record is in included_records
    if archive_latest_id:
        if not any(
            r.get("record_id") == archive_latest_id
            and r.get("record_sha256") == archive_latest_sha
            for r in included_records
        ):
            errors.append(
                f"{archive_id}: archive's own latest record ({archive_latest_id}) "
                f"missing from included_records"
            )

    # Legacy JSONL checks
    if native_chain.get("legacy_main_chain_jsonl_is_not_source") is not True:
        errors.append(f"{archive_id}: native archive must declare legacy JSONL is not source")

    manifest_text = canonical_dumps(manifest)
    if "main.chain.jsonl" in manifest_text:
        errors.append(f"{archive_id}: native archive must not reference main.chain.jsonl")

    return errors


def verify_latest_archive_covers_chain_tip(
    latest_archive_id: str,
    native_chain: dict,
    chain_tip: dict,
) -> list[str]:
    """Verify the latest live native archive covers the current chain-tip."""
    errors = []

    if native_chain.get("latest_record_id") != chain_tip.get("latest_record_id"):
        errors.append(
            f"latest live archive ({latest_archive_id}): "
            f"native latest_record_id ({native_chain.get('latest_record_id')}) "
            f"does not match chain-tip ({chain_tip.get('latest_record_id')})"
        )
    if native_chain.get("latest_record_sha256") != chain_tip.get("latest_record_sha256"):
        errors.append(
            f"latest live archive ({latest_archive_id}): "
            f"native latest_record_sha256 mismatch"
        )
    if native_chain.get("native_record_count") != chain_tip.get("native_record_count"):
        errors.append(
            f"latest live archive ({latest_archive_id}): "
            f"native_record_count ({native_chain.get('native_record_count')}) "
            f"does not match chain-tip ({chain_tip.get('native_record_count')})"
        )

    return errors


def verify(network: bool = False, strict_network: bool = False) -> list[str]:
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

    # Pre-pass: find latest live native archive for chain-tip coverage check
    latest_live = find_latest_live_native_archive(index.get("archives", []))

    for archive in index.get("archives", []):
        archive_id = archive.get("archive_id", "unknown")
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
            errors.append(f"{archive_id}: archive_manifest_sha256 mismatch")

        # Check arweave boundary
        arweave = manifest.get("arweave", {})
        if manifest.get("mode") == "dry-run" and arweave.get("txid") is not None:
            errors.append(f"{archive_id}: dry-run but claims arweave_txid")

        # Check boundary fields in manifest
        m_boundary = manifest.get("boundary", {})
        for key in ["not_authority", "not_attestation", "not_amendment",
                     "not_successor_reception", "bitcoin_originals_prevail"]:
            if not m_boundary.get(key):
                errors.append(f"{archive_id}: manifest boundary missing/false: {key}")

        # Native archive validation
        source = manifest.get("source", {})
        if source.get("source_type") == "native-record-chain":
            native_chain = source.get("native_chain", {})

            # Self-consistency: verify against the archive's own snapshot
            sc_errors = verify_native_archive_self_consistency(
                archive_id, manifest, native_chain
            )
            errors.extend(sc_errors)

            # Chain-tip coverage: only for the latest live archive
            if latest_live and archive_id == latest_live["_archive_id"]:
                chain_tip = read_json(CHAIN_TIP)
                ct_errors = verify_latest_archive_covers_chain_tip(
                    archive_id, native_chain, chain_tip
                )
                errors.extend(ct_errors)

        # Check included batches
        for batch in manifest.get("included_batches", []):
            batch_path = ROOT / batch.get("manifest_path", "")
            if not batch_path.exists():
                errors.append(f"{archive_id}: batch manifest missing: {batch_path}")
                continue
            batch_data = read_json(batch_path)
            if batch_data.get("batch_manifest_sha256") != batch.get("batch_manifest_sha256"):
                errors.append(f"{archive_id}: batch {batch.get('batch_id')} sha mismatch")

        # Check included records
        for rec in manifest.get("included_records", []):
            rec_path = ROOT / rec.get("path", "")
            if not rec_path.exists():
                errors.append(f"{archive_id}: record missing: {rec_path}")
                continue
            rec_data = read_json(rec_path)
            if rec_data.get("record_sha256") != rec.get("record_sha256"):
                errors.append(f"{archive_id}: record {rec.get('record_id')} sha mismatch")

        # Check forbidden terminology in manifest
        manifest_text = canonical_dumps(manifest)
        for term in FORBIDDEN_TERMS:
            if term in manifest_text:
                errors.append(f"{archive_id}: forbidden term '{term}' in manifest")

        # Verify txid shape if present
        txid = arweave.get("txid")
        if txid:
            if not verify_txid_shape(txid):
                errors.append(f"{archive_id}: invalid txid shape: {txid[:20]}...")

            # Network verification if requested
            if network or strict_network:
                # Find payload.json for expected hash
                archive_dir = manifest_path.parent
                payload_path = archive_dir / "payload.json"
                if payload_path.exists():
                    payload_sha = sha256_file(payload_path)
                    net_errors = verify_network(txid, payload_sha, strict=strict_network)
                    errors.extend(net_errors)
                else:
                    msg = f"{archive_id}: payload.json not found for network verification"
                    if strict_network:
                        errors.append(msg)
                    else:
                        print(f"WARN: {msg}")

    return errors


def main():
    parser = argparse.ArgumentParser(description="Verify record-chain Arweave archive metadata")
    parser.add_argument("--network", action="store_true", help="Verify Arweave transactions on network")
    parser.add_argument("--strict-network", action="store_true", help="Fail on network propagation delays")
    args = parser.parse_args()

    errors = verify(network=args.network, strict_network=args.strict_network)
    if errors:
        print("Arweave archive verification failed:", file=sys.stderr)
        for e in errors:
            print(f"- {e}", file=sys.stderr)
        raise SystemExit(1)
    print("Arweave archive verification passed.")


if __name__ == "__main__":
    main()
