#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any
import hashlib
import re


TX_RE = re.compile(r"^[A-Za-z0-9_-]{20,}$")


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def load_registry(path: Path, chain_id: str) -> dict[str, Any]:
    if path.exists():
        return load_json(path)
    return {
        "schema": "trinity_record_chain_ots_arweave_registry.v1",
        "chain_id": chain_id,
        "authority": (
            "registry of Arweave archives for OTS head anchors; "
            "main.chain.jsonl remains authoritative"
        ),
        "entries": [],
        "latest_by_head": {},
        "generated_at": utc_now(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update OTS-Arweave registry after uploading an OTS bundle to Arweave."
    )
    parser.add_argument("--registry", default="record-chain/ots/arweave-registry.json")
    parser.add_argument("--api-out", default="api/record-chain-ots-arweave-registry.json")
    parser.add_argument("--anchor-file", required=True)
    parser.add_argument("--bundle-file", required=True)
    parser.add_argument("--upload-result", required=True)
    parser.add_argument("--readback-result", required=True)
    parser.add_argument(
        "--allow-dry-run-anchor",
        action="store_true",
        help="Only for tests. Production registry updates must not archive dry_run OTS anchors.",
    )
    args = parser.parse_args()

    registry_path = Path(args.registry)
    api_out = Path(args.api_out)

    anchor_path = Path(args.anchor_file)
    bundle_path = Path(args.bundle_file)
    upload_path = Path(args.upload_result)
    readback_path = Path(args.readback_result)

    anchor = load_json(anchor_path)
    bundle = load_json(bundle_path)
    upload = load_json(upload_path)
    readback = load_json(readback_path)

    chain_id = bundle.get("chain_id")
    if not chain_id:
        raise SystemExit("bundle.chain_id missing")

    if anchor.get("schema") != "trinity_record_chain_ots_anchor.v1":
        raise SystemExit("anchor schema mismatch")
    if bundle.get("schema") != "trinity_record_chain_ots_arweave_bundle.v1":
        raise SystemExit("bundle schema mismatch")
    if anchor.get("chain_id") != chain_id:
        raise SystemExit("anchor chain_id != bundle chain_id")

    ots_status = bundle.get("ots_status")
    if ots_status == "dry_run" and not args.allow_dry_run_anchor:
        raise SystemExit(
            "Refusing to write dry_run OTS anchor to Arweave registry. "
            "Use --allow-dry-run-anchor only in tests."
        )

    bundle_sha = sha256_bytes(bundle_path.read_bytes())

    if upload.get("result") != "uploaded":
        raise SystemExit(f"upload result is not uploaded: {upload.get('result')}")
    tx_id = upload.get("tx_id")
    if not isinstance(tx_id, str) or not TX_RE.match(tx_id):
        raise SystemExit(f"invalid tx_id: {tx_id}")

    if readback.get("result") != "pass":
        raise SystemExit("readback result is not pass")
    if readback.get("hash_match") is not True:
        raise SystemExit("readback hash_match is not true")

    payload_sha = upload.get("payload_sha256")
    downloaded_sha = readback.get("downloaded_sha256")
    if payload_sha != downloaded_sha:
        raise SystemExit("upload payload sha != readback downloaded sha")
    if payload_sha != bundle_sha:
        raise SystemExit(
            f"bundle sha mismatch: bundle={bundle_sha}, upload_payload={payload_sha}"
        )

    if bundle.get("source_anchor_file") != str(anchor_path):
        raise SystemExit("bundle.source_anchor_file does not match --anchor-file")

    registry = load_registry(registry_path, chain_id)
    if registry.get("chain_id") != chain_id:
        raise SystemExit("registry chain_id mismatch")

    entries = registry.setdefault("entries", [])

    if any(e.get("arweave_tx_id") == tx_id for e in entries):
        print(f"Registry already contains tx_id {tx_id}; no update needed.")
        return

    height = bundle.get("height")
    head_entry_hash = bundle.get("head_entry_hash")
    registry_key = f"height-{height}-{str(head_entry_hash)[:16]}-{ots_status}-{bundle_sha[:16]}"

    if any(e.get("registry_key") == registry_key for e in entries):
        raise SystemExit(f"registry_key already exists with different tx_id: {registry_key}")

    entry = {
        "registry_key": registry_key,
        "chain_id": chain_id,
        "height": height,
        "entry_count": bundle.get("entry_count"),
        "head_entry_hash": head_entry_hash,
        "anchored_file_sha256": bundle.get("anchored_file_sha256"),
        "ots_status": ots_status,
        "bitcoin_verified": bundle.get("bitcoin_verified"),
        "bitcoin_pending": bundle.get("bitcoin_pending"),
        "bitcoin_attestation_embedded": bundle.get("bitcoin_attestation_embedded", False),
        "bundle_file": str(bundle_path),
        "bundle_sha256": bundle_sha,
        "bundle_bytes": bundle_path.stat().st_size,
        "arweave_tx_id": tx_id,
        "arweave_gateway_url": upload.get("gateway_url"),
        "arweave_payload_sha256": payload_sha,
        "arweave_readback_sha256": downloaded_sha,
        "arweave_hash_match": True,
        "source_anchor_file": str(anchor_path),
        "source_anchor_sha256": sha256_bytes(anchor_path.read_bytes()),
        "created_at": utc_now(),
    }

    entries.append(entry)
    entries.sort(key=lambda x: (x.get("height") or -1, x.get("created_at") or ""))

    latest_by_head: dict[str, Any] = {}
    for item in entries:
        h = item.get("head_entry_hash")
        if not h:
            continue
        existing = latest_by_head.get(h, {
            "height": item.get("height"),
            "latest_pending_tx_id": None,
            "latest_upgraded_tx_id": None,
            "latest_verified_tx_id": None,
            "latest_any_tx_id": None,
        })
        # Ensure backward compat: add latest_upgraded_tx_id if missing
        existing.setdefault("latest_upgraded_tx_id", None)

        existing["latest_any_tx_id"] = item.get("arweave_tx_id")
        if item.get("bitcoin_verified") is True or item.get("ots_status") == "verified":
            existing["latest_verified_tx_id"] = item.get("arweave_tx_id")
        elif item.get("ots_status") == "upgraded":
            existing["latest_upgraded_tx_id"] = item.get("arweave_tx_id")
        elif item.get("ots_status") == "pending":
            existing["latest_pending_tx_id"] = item.get("arweave_tx_id")
        latest_by_head[h] = existing

    registry["latest_by_head"] = latest_by_head
    registry["generated_at"] = utc_now()
    registry["entry_count"] = len(entries)

    write_json(registry_path, registry)
    write_json(api_out, registry)

    print(json.dumps({
        "result": "updated",
        "registry": str(registry_path),
        "api_out": str(api_out),
        "entry_count": len(entries),
        "added_tx_id": tx_id,
        "registry_key": registry_key,
    }, indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
