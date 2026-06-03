#!/usr/bin/env python3
"""Verify record-chain Arweave archive metadata integrity.

Checks:
- archive_manifest_sha256 recomputation
- included batch manifests exist and match
- included records exist and match
- dry-run entries do not claim arweave_txid
- boundary fields
- no ARV5/LV5/IPFS current terminology in index

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

        # Verify txid shape if present
        txid = arweave.get("txid")
        if txid:
            if not verify_txid_shape(txid):
                errors.append(f"{archive['archive_id']}: invalid txid shape: {txid[:20]}...")

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
                    msg = f"{archive['archive_id']}: payload.json not found for network verification"
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
