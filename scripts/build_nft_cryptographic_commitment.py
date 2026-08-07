#!/usr/bin/env python3
"""Build a deterministic collection-level commitment for the 175 NFT evidence records.

The commitment deliberately excludes presentation-only URLs and packed-token hints. It
binds canonical NFT identity, immutable mint coordinates, and content-recovery hashes /
Arweave transaction IDs. The Merkle construction follows RFC 6962 domain separation:
leaf = SHA256(0x00 || canonical_json(record)); node = SHA256(0x01 || left || right).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "nft-identity-index.json"
DEFAULT_OUTPUT = ROOT / "evidence" / "nft-proof-annex-v1" / "NFT-COLLECTION-COMMITMENT.json"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def norm_hex(value: Any, name: str, length: int | None = None) -> str:
    if not isinstance(value, str) or not value.startswith("0x"):
        raise ValueError(f"{name} must be 0x-prefixed hex")
    raw = value[2:].lower()
    if not raw or any(c not in "0123456789abcdef" for c in raw):
        raise ValueError(f"{name} is not valid hex")
    if length is not None and len(raw) != length * 2:
        raise ValueError(f"{name} must be {length} bytes")
    return "0x" + raw


def norm_decimal(value: Any, name: str) -> str:
    if isinstance(value, int):
        parsed = value
    elif isinstance(value, str) and value.isdigit():
        parsed = int(value, 10)
    else:
        raise ValueError(f"{name} must be an unsigned decimal integer")
    if parsed < 0:
        raise ValueError(f"{name} must be non-negative")
    return str(parsed)


def norm_optional_decimal(value: Any, name: str) -> str | None:
    return None if value is None else norm_decimal(value, name)


def project_content(asset: dict) -> dict:
    content = asset.get("content") or {}
    metadata = content.get("metadata") or {}
    media = content.get("media") or []
    projected_media = []
    for item in media:
        projected_media.append({
            "arweave_txid": str(item.get("arweave_txid") or ""),
            "car_sha256": str(item.get("car_sha256") or "").lower(),
            "car_size": int(item["car_size"]) if item.get("car_size") is not None else None,
            "leaf_path": item.get("leaf_path"),
            "root_cid": str(item.get("root_cid") or ""),
        })
    projected_media.sort(key=lambda x: (x["root_cid"], x["leaf_path"] or "", x["arweave_txid"]))
    return {
        "metadata": {
            "arweave_txid": str(metadata.get("arweave_txid") or ""),
            "car_sha256": str(metadata.get("car_sha256") or "").lower(),
            "car_size": int(metadata["car_size"]) if metadata.get("car_size") is not None else None,
            "root_cid": str(metadata.get("root_cid") or ""),
        },
        "media": projected_media,
    }


def project_asset(asset: dict) -> dict:
    chain_id = norm_decimal((asset.get("chain") or {}).get("chain_id"), "chain_id")
    contract = norm_hex(asset.get("contract_address"), "contract_address", 20)
    token_id = norm_decimal(asset.get("token_id"), "token_id")
    mint = asset.get("mint") or {}
    projected = {
        "identity": {
            "chain_id": chain_id,
            "standard": str(asset.get("standard") or "").lower(),
            "contract_address": contract,
            "token_id": token_id,
        },
        "mint": {
            "transaction_hash": norm_hex(mint.get("transaction_hash"), "mint.transaction_hash", 32),
            "block_number": norm_decimal(mint.get("block_number"), "mint.block_number"),
            "block_hash": norm_hex(mint.get("block_hash"), "mint.block_hash", 32),
            "transaction_index": norm_decimal(mint.get("transaction_index"), "mint.transaction_index"),
            "log_index": norm_decimal(mint.get("log_index"), "mint.log_index"),
            "batch_index": norm_optional_decimal(mint.get("batch_index"), "mint.batch_index"),
            "event": str(mint.get("event") or ""),
            "operator": None if mint.get("operator") is None else norm_hex(mint.get("operator"), "mint.operator", 20),
            "from": norm_hex(mint.get("from"), "mint.from", 20),
            "to": norm_hex(mint.get("to"), "mint.to", 20),
            "quantity": norm_decimal(mint.get("quantity"), "mint.quantity"),
            "receipt_status": norm_optional_decimal(mint.get("receipt_status"), "mint.receipt_status"),
            "receipt_verified": mint.get("receipt_verified") is True,
        },
        "content": project_content(asset),
    }
    if projected["identity"]["standard"] not in {"erc721", "erc1155"}:
        raise ValueError("unsupported token standard")
    if projected["mint"]["from"] != "0x" + "00" * 20:
        raise ValueError("mint event does not originate from the zero address")
    if not projected["mint"]["receipt_verified"]:
        raise ValueError("mint receipt is not marked verified")
    return projected


def canonical_key(record: dict) -> str:
    ident = record["identity"]
    return f"eip155:{ident['chain_id']}/{ident['standard']}:{ident['contract_address']}/{ident['token_id']}"


def split_point(n: int) -> int:
    if n < 2:
        raise ValueError("split_point requires n >= 2")
    k = 1 << (n.bit_length() - 1)
    return k // 2 if k == n else k


def merkle_root_from_leaf_hashes(leaves: list[bytes]) -> bytes:
    if not leaves:
        return hashlib.sha256(b"").digest()
    if len(leaves) == 1:
        return leaves[0]
    k = split_point(len(leaves))
    left = merkle_root_from_leaf_hashes(leaves[:k])
    right = merkle_root_from_leaf_hashes(leaves[k:])
    return hashlib.sha256(b"\x01" + left + right).digest()


def build(source: pathlib.Path) -> dict:
    raw = source.read_bytes()
    parsed = json.loads(raw)
    assets = parsed.get("assets")
    if not isinstance(assets, list) or not assets:
        raise ValueError("identity index has no assets")

    records = []
    for asset in assets:
        projected = project_asset(asset)
        records.append((canonical_key(projected), projected))
    records.sort(key=lambda item: (int(item[1]["identity"]["chain_id"]), item[1]["identity"]["contract_address"], int(item[1]["identity"]["token_id"])))

    keys = [key for key, _ in records]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate canonical NFT identity")
    mint_coordinates = []
    leaf_entries = []
    leaf_hashes = []
    for key, record in records:
        mint = record["mint"]
        coord = (mint["transaction_hash"], mint["log_index"], mint["batch_index"])
        mint_coordinates.append(coord)
        leaf_hash = hashlib.sha256(b"\x00" + canonical_bytes(record)).digest()
        leaf_hashes.append(leaf_hash)
        leaf_entries.append({
            "canonical_key": key,
            "leaf_sha256": leaf_hash.hex(),
            "mint_transaction_hash": mint["transaction_hash"],
            "mint_block_hash": mint["block_hash"],
        })
    if len(mint_coordinates) != len(set(mint_coordinates)):
        raise ValueError("duplicate mint-event coordinate")

    unique_txs = sorted({record["mint"]["transaction_hash"] for _, record in records})
    unique_blocks = sorted({record["mint"]["block_hash"] for _, record in records})
    root = merkle_root_from_leaf_hashes(leaf_hashes).hex()
    source_rel = source.resolve().relative_to(ROOT).as_posix()
    return {
        "schema": "trinityaccord.nft-collection-commitment.v1",
        "version": "1.0.0",
        "authority_boundary": {
            "canonical_authority": "three Bitcoin Originals only",
            "nft_role": "non-amending historical chronicle and recovery evidence",
            "no_authority_escalation": True,
        },
        "source": {
            "path": source_rel,
            "sha256": sha256_bytes(raw),
            "schema": parsed.get("schema"),
            "asset_count": len(records),
        },
        "canonicalization": {
            "format": "UTF-8 JSON with lexicographically sorted object keys, no insignificant whitespace, ensure_ascii=false",
            "sort_order": "numeric chain_id, lowercase contract_address, numeric token_id",
            "excluded_as_presentation_or_informational": ["asset_id", "lookup URLs", "transaction_url", "token_id_encoding_hint"],
        },
        "merkle": {
            "construction": "RFC6962-style SHA-256 domain-separated Merkle tree",
            "empty_root_rule": "SHA256(empty)",
            "leaf_rule": "SHA256(0x00 || canonical_json(projected_record))",
            "node_rule": "SHA256(0x01 || left || right)",
            "split_rule": "largest power of two strictly less than n",
            "leaf_count": len(records),
            "root_sha256": root,
        },
        "mint_evidence_inventory": {
            "unique_transactions": len(unique_txs),
            "unique_execution_blocks": len(unique_blocks),
            "all_receipts_marked_verified": all(record["mint"]["receipt_verified"] for _, record in records),
        },
        "leaves": leaf_entries,
    }


def render(manifest: dict) -> bytes:
    return (json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=str(DEFAULT_SOURCE))
    ap.add_argument("--output", default=str(DEFAULT_OUTPUT))
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    source = pathlib.Path(args.source).resolve()
    output = pathlib.Path(args.output).resolve()
    manifest = build(source)
    encoded = render(manifest)
    if args.check:
        if not output.is_file():
            print(f"FAIL: missing commitment {output.relative_to(ROOT)}")
            return 1
        if output.read_bytes() != encoded:
            print(f"FAIL: commitment drift {output.relative_to(ROOT)}")
            return 1
        print(f"PASS: NFT collection commitment {manifest['merkle']['root_sha256']} ({manifest['source']['asset_count']} NFTs; {manifest['mint_evidence_inventory']['unique_transactions']} tx; {manifest['mint_evidence_inventory']['unique_execution_blocks']} blocks)")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(encoded)
    print(f"Wrote {output.relative_to(ROOT)}")
    print(f"NFT_MERKLE_ROOT={manifest['merkle']['root_sha256']}")
    print(f"NFT_UNIQUE_MINT_TRANSACTIONS={manifest['mint_evidence_inventory']['unique_transactions']}")
    print(f"NFT_UNIQUE_MINT_BLOCKS={manifest['mint_evidence_inventory']['unique_execution_blocks']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
