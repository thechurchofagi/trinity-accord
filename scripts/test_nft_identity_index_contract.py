#!/usr/bin/env python3
"""Validate the committed NFT identity index and its storage boundary."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN_INDEX = ROOT / "token_index.json"
IDENTITY_INDEX = ROOT / "nft-identity-index.json"
GENERATOR = ROOT / "scripts/generate_nft_identity_index.mjs"

ADDRESS_RE = re.compile(r"^0x[0-9a-f]{40}$")
HASH_RE = re.compile(r"^0x[0-9a-f]{64}$")
ARWEAVE_TXID_RE = re.compile(r"^[A-Za-z0-9_-]{43}$")
DECIMAL_RE = re.compile(r"^(0|[1-9][0-9]*)$")


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def load(path: Path):
    require(path.exists(), f"missing {path.relative_to(ROOT)}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON {path.relative_to(ROOT)}: {exc}")


def normalize_content(record: dict) -> dict:
    metadata = record.get("metadata") or {}
    media = record.get("media") or []
    return {
        "metadata": {
            "arweave_txid": metadata.get("txid"),
            "root_cid": metadata.get("root_cid"),
            "car_sha256": metadata.get("car_sha256"),
            "car_size": metadata.get("car_size"),
        },
        "media": [
            {
                "arweave_txid": item.get("txid"),
                "root_cid": item.get("root_cid"),
                "leaf_path": item.get("leaf_path"),
                "car_sha256": item.get("car_sha256"),
                "car_size": item.get("car_size"),
            }
            for item in media
        ],
    }


def main() -> int:
    token_index = load(TOKEN_INDEX)
    identity = load(IDENTITY_INDEX)

    require(identity.get("schema") == "trinityaccord.nft-identity-index.v1", "identity schema mismatch")
    source = identity.get("source") or {}
    summary = identity.get("summary") or {}
    policy = identity.get("storage_policy") or {}
    assets = identity.get("assets")
    contracts = identity.get("contracts")

    require(isinstance(assets, list), "assets must be an array")
    require(isinstance(contracts, list), "contracts must be an array")
    require(policy.get("repository_does_not_embed_car_payloads") is True, "large-payload repository boundary missing")
    require("GitHub Releases" in policy.get("large_binary_payloads_remain_in", []), "GitHub Release storage boundary missing")
    require("Arweave" in policy.get("large_binary_payloads_remain_in", []), "Arweave storage boundary missing")
    require(IDENTITY_INDEX.stat().st_size < 2_000_000, "identity index is unexpectedly large; binary payloads must not be committed")

    expected_sha = hashlib.sha256(TOKEN_INDEX.read_bytes()).hexdigest()
    require(source.get("token_index_path") == "token_index.json", "token index source path mismatch")
    require(source.get("token_index_sha256") == expected_sha, "token index source digest mismatch")
    chain_id = source.get("chain_id")
    require(isinstance(chain_id, str) and DECIMAL_RE.fullmatch(chain_id) and int(chain_id) > 0, "invalid chain ID")
    require(HASH_RE.fullmatch(source.get("snapshot_block_hash", "")) is not None, "invalid snapshot block hash")
    require(DECIMAL_RE.fullmatch(source.get("snapshot_block_number", "")) is not None, "invalid snapshot block number")

    expected: dict[tuple[str, str], dict] = {}
    for contract_raw, tokens in token_index.items():
        contract = contract_raw.lower()
        require(ADDRESS_RE.fullmatch(contract) is not None, f"invalid token_index contract: {contract_raw}")
        require(isinstance(tokens, dict), f"invalid token map: {contract}")
        for token_id, record in tokens.items():
            require(DECIMAL_RE.fullmatch(token_id) is not None, f"invalid token ID: {contract}/{token_id}")
            expected[(contract, token_id)] = normalize_content(record)

    require(summary.get("nfts") == len(expected), "summary NFT count mismatch")
    require(summary.get("contracts") == len(token_index), "summary contract count mismatch")
    require(summary.get("unresolved") == 0, "identity index has unresolved mint events")
    require(summary.get("receipt_verified") == len(expected), "not every mint receipt is verified")
    require(len(assets) == len(expected), "asset count does not match token_index")
    require(len(contracts) == len(token_index), "contract summary count mismatch")

    seen: set[tuple[str, str]] = set()
    asset_ids: set[str] = set()
    mint_txs: set[str] = set()
    for asset in assets:
        contract = asset.get("contract_address")
        token_id = asset.get("token_id")
        standard = asset.get("standard")
        require(isinstance(contract, str) and ADDRESS_RE.fullmatch(contract) is not None, f"invalid asset contract: {contract}")
        require(isinstance(token_id, str) and DECIMAL_RE.fullmatch(token_id) is not None, f"invalid asset token ID: {token_id}")
        require(standard in {"erc721", "erc1155"}, f"invalid token standard: {standard}")
        key = (contract, token_id)
        require(key in expected, f"asset missing from token_index: {contract}/{token_id}")
        require(key not in seen, f"duplicate asset: {contract}/{token_id}")
        seen.add(key)

        expected_asset_id = f"eip155:{chain_id}/{standard}:{contract}/{token_id}"
        require(asset.get("asset_id") == expected_asset_id, f"asset_id mismatch: {contract}/{token_id}")
        require(expected_asset_id not in asset_ids, f"duplicate asset_id: {expected_asset_id}")
        asset_ids.add(expected_asset_id)
        require((asset.get("chain") or {}).get("chain_id") == chain_id, f"asset chain mismatch: {contract}/{token_id}")
        require((asset.get("lookup") or {}).get("canonical_key") == f"{chain_id}:{contract}:{token_id}", f"canonical lookup key mismatch: {contract}/{token_id}")

        mint = asset.get("mint") or {}
        tx_hash = mint.get("transaction_hash", "")
        require(HASH_RE.fullmatch(tx_hash) is not None, f"invalid mint tx hash: {contract}/{token_id}")
        mint_txs.add(tx_hash)
        require(HASH_RE.fullmatch(mint.get("block_hash", "")) is not None, f"invalid mint block hash: {contract}/{token_id}")
        for field in ("block_number", "transaction_index", "log_index", "quantity"):
            require(DECIMAL_RE.fullmatch(mint.get(field, "")) is not None, f"invalid mint {field}: {contract}/{token_id}")
        require(mint.get("event") in {"Transfer", "TransferSingle", "TransferBatch"}, f"invalid mint event: {contract}/{token_id}")
        require(mint.get("from") == "0x0000000000000000000000000000000000000000", f"mint is not from zero address: {contract}/{token_id}")
        require(ADDRESS_RE.fullmatch(mint.get("to", "")) is not None, f"invalid mint recipient: {contract}/{token_id}")
        require(mint.get("receipt_verified") is True, f"mint receipt not verified: {contract}/{token_id}")
        require(mint.get("receipt_status") in {"1", None}, f"mint transaction failed: {contract}/{token_id}")
        tx_url = mint.get("transaction_url")
        if tx_url is not None:
            require(tx_hash in tx_url, f"transaction URL does not contain hash: {contract}/{token_id}")

        content = asset.get("content") or {}
        require(content == expected[key], f"content linkage drift: {contract}/{token_id}")
        require(ARWEAVE_TXID_RE.fullmatch(content["metadata"]["arweave_txid"] or "") is not None, f"invalid metadata Arweave TXID: {contract}/{token_id}")
        for media in content["media"]:
            require(ARWEAVE_TXID_RE.fullmatch(media["arweave_txid"] or "") is not None, f"invalid media Arweave TXID: {contract}/{token_id}")

        hint = asset.get("token_id_encoding_hint")
        if hint is not None:
            require(ADDRESS_RE.fullmatch(hint.get("high_160_bits_address", "")) is not None, f"invalid packed token address hint: {contract}/{token_id}")
            require(DECIMAL_RE.fullmatch(hint.get("low_96_bits_serial", "")) is not None, f"invalid packed token serial hint: {contract}/{token_id}")
            reconstructed = (int(hint["high_160_bits_address"], 16) << 96) | int(hint["low_96_bits_serial"])
            require(str(reconstructed) == token_id, f"packed token hint does not reconstruct token ID: {contract}/{token_id}")

    require(seen == set(expected), "identity index is missing token_index assets")
    require(summary.get("mint_transactions") == len(mint_txs), "mint transaction count mismatch")

    generator = GENERATOR.read_text(encoding="utf-8")
    for marker in [
        "eth_getLogs",
        "eth_getTransactionReceipt",
        "TransferSingle(address,address,address,uint256,uint256)",
        "TransferBatch(address,address,address,uint256[],uint256[])",
        "Transfer(address,address,uint256)",
        "ZERO_TOPIC",
        "receipt_verified: true",
        "eip155:${chainId}",
        "repository_does_not_embed_car_payloads: true",
        "--self-test",
    ]:
        require(marker in generator, f"generator missing control: {marker}")

    print(f"PASS: NFT identity index links {len(assets)} NFTs to {len(mint_txs)} receipt-verified mint transactions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
