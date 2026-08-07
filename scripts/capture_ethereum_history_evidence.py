#!/usr/bin/env python3
"""Capture read-only Ethereum mainnet historical evidence for legacy attestations.

This script never signs or sends a transaction. It queries multiple JSON-RPC
providers, requires consensus on immutable block/transaction/receipt fields,
and writes a compact evidence bundle suitable for later offline inspection.

The bundle deliberately distinguishes the Ethereum block timestamp from any
human timestamp text embedded in calldata and from the later capture time.
It does not claim to be a self-contained proof that the block is canonical
without an Ethereum chain/checkpoint source; see the generated README.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request

CHAIN_ID = "0x1"
BOUNDARY = "Non-amending Ethereum historical-evidence mirror; Bitcoin Originals prevail."
DEFAULT_RPCS = [
    "https://ethereum-rpc.publicnode.com",
    "https://eth.llamarpc.com",
    "https://cloudflare-eth.com",
]

TARGETS = [
    ("Guardianship Principles", "0xd082a3ced27ece935d4093fb001a9ebfba42b415f78de4377c8cda55338c6420", 2446, "3e9d2bd10c3e8f4d37713c4b8e28d518fd7efff52613e572a1451ffedadab5483"),
    ("BTC-ETH Guardianship Mirrors Attestation", "0x59cf33b1291de63c4840b79e7c674b8fc7c6a771d8a3ba2bb50def1fe55a71c6", 3231, "f4af38f0f42c9b38deaccbace119736da57a245a6601e5d0ea5698deec4a8a01"),
    ("Protocol mirror", "0x6652162e8e6c56ddc0d9476407b3b911e918d4e4683408440dc3af51c5bb63d5", 1183, "4e89bfabe03c8b53f80eb7979d56c8cccf0ae382c9647a2bea3b1477054616a8"),
    ("Covenant mirror", "0x9c1bd6e21dc2370e8dbb6549b7ba13b4ea7ba7a192b3b876e0ec28b4633f1612", 1710, "003ef48c72307243b1f7a17c0578b311ee76d6f9a8078850773ad8fba04ab86d"),
    ("Accord mirror", "0x0affc8099ea965cd6d6a0d1cf9b93adb11f7e40ac41fffe1b0ca4637f39df665", 15637, "25edaa35e7116614d3381ab6734ab5ee3369fb628fe11289e199d8871c2498ba"),
    ("BIP-322 notice", "0x55a0c131642f71c7b2386ccaac8bcee36563992226befb35363e978044a18e8f", 412, "abd10a807323ef3a07fe22eb3a3cc083e77db93d7362eb29c939c195825f2c2d"),
    ("Mirror correction (superseded erroneous version)", "0x940300cba1acd7aa7078e614510400d4ec4b8961a2f05470d129c709b8cce3e6", 2446, "3e9d2bd10c3e8f4d37713c4b8e28d518fd7efff52613e572a1451ffedadab5483"),
    ("Mirror correction (final version)", "0xa4023b1eb0de76993e1a8dcd571e5e033bf64e2d32a9a113b030b4094a19cf51", 4994, "fc009f5393b11e95f013464405e24c9713a55415fa326b2707886d436d4cbd6f"),
    ("Guardianship Principles v1.1", "0x7bdff0d696337ceb04539b44a746d0f13ce731ac25de259d8a4faf69b276a628", 4694, "e19018f1c71da8307ef20e8e8e5c12834f854d60a6aae60e35d2d8c71a333a81"),
    ("BTC BIP-340 witness", "0x214d73b839ed95707410af3d5b8224a44a5dd310041d5e7ab1756ae9c5378137", 600, "fb8746462a4aae73628f542b3ada48621ab298ab2117b6162161d79d2aaad54e"),
]

# Header fields are enough to reconstruct/check the header hash with an
# Ethereum-aware verifier, while avoiding a huge duplicate list of block txs.
HEADER_FIELDS = [
    "number", "hash", "parentHash", "sha3Uncles", "miner", "stateRoot",
    "transactionsRoot", "receiptsRoot", "logsBloom", "difficulty",
    "totalDifficulty", "gasLimit", "gasUsed", "timestamp", "extraData",
    "mixHash", "nonce", "baseFeePerGas", "withdrawalsRoot",
    "blobGasUsed", "excessBlobGas", "parentBeaconBlockRoot", "requestsHash",
]


def rpc(url: str, method: str, params: list, timeout: int = 30):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(url, data=body, headers={"content-type": "application/json", "user-agent": "trinityaccord-ethereum-evidence/1"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        payload = json.load(response)
    if payload.get("error"):
        raise RuntimeError(f"{method}: {payload['error']}")
    return payload.get("result")


def normalize_tx(tx: dict) -> dict:
    return {k: tx.get(k) for k in sorted(tx)}


def normalize_receipt(receipt: dict) -> dict:
    return {k: receipt.get(k) for k in sorted(receipt)}


def header(block: dict) -> dict:
    return {k: block.get(k) for k in HEADER_FIELDS if k in block}


def core_fingerprint(e: dict) -> dict:
    tx = e["transaction"]
    receipt = e["receipt"]
    block = e["block_header"]
    return {
        "tx_hash": tx["hash"],
        "block_number": tx["blockNumber"],
        "block_hash": tx["blockHash"],
        "transaction_index": tx["transactionIndex"],
        "from": tx["from"].lower(),
        "to": (tx.get("to") or "").lower(),
        "input": tx.get("input", "0x"),
        "receipt_block_hash": receipt["blockHash"],
        "receipt_block_number": receipt["blockNumber"],
        "receipt_transaction_index": receipt["transactionIndex"],
        "receipt_status": receipt.get("status"),
        "block_header": block,
    }


def fetch_one(url: str, tx_hash: str) -> dict:
    tx = rpc(url, "eth_getTransactionByHash", [tx_hash])
    if not tx:
        raise RuntimeError("transaction not found")
    receipt = rpc(url, "eth_getTransactionReceipt", [tx_hash])
    if not receipt:
        raise RuntimeError("receipt not found")
    block_hash = tx.get("blockHash")
    if not block_hash:
        raise RuntimeError("transaction is not mined")
    block = rpc(url, "eth_getBlockByHash", [block_hash, False])
    if not block:
        raise RuntimeError("block not found")
    if receipt.get("blockHash") != block_hash or block.get("hash") != block_hash:
        raise RuntimeError("block hash disagreement inside RPC response")
    return {"transaction": normalize_tx(tx), "receipt": normalize_receipt(receipt), "block_header": header(block)}


def iso_timestamp(hex_timestamp: str) -> str:
    unix = int(hex_timestamp, 16)
    return dt.datetime.fromtimestamp(unix, tz=dt.timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="archive/ethereum-evidence")
    parser.add_argument("--min-agreeing-rpcs", type=int, default=2)
    args = parser.parse_args()

    urls = [u.strip() for u in os.getenv("ETH_HISTORY_RPC_URLS", ";".join(DEFAULT_RPCS)).split(";") if u.strip()]
    out = Path(args.output)
    txdir = out / "transactions"
    txdir.mkdir(parents=True, exist_ok=True)
    captured_at = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    manifest_records = []

    for label, tx_hash, expected_len, expected_sha in TARGETS:
        observations = []
        errors = []
        for url in urls:
            try:
                data = fetch_one(url, tx_hash)
                observations.append((url, data))
            except Exception as exc:  # each public RPC is an independent best-effort source
                errors.append({"rpc": url, "error": str(exc)[:300]})
            time.sleep(0.15)

        if len(observations) < args.min_agreeing_rpcs:
            raise SystemExit(f"{tx_hash}: only {len(observations)} successful RPCs; errors={errors}")
        first_fp = core_fingerprint(observations[0][1])
        agreeing = [url for url, data in observations if core_fingerprint(data) == first_fp]
        if len(agreeing) < args.min_agreeing_rpcs:
            raise SystemExit(f"{tx_hash}: fewer than {args.min_agreeing_rpcs} RPCs agree on immutable evidence")

        data = observations[0][1]
        tx = data["transaction"]
        raw_input = bytes.fromhex(tx.get("input", "0x")[2:])
        actual_len = len(raw_input)
        actual_sha = hashlib.sha256(raw_input).hexdigest()
        if actual_len != expected_len or actual_sha != expected_sha:
            raise SystemExit(f"{tx_hash}: calldata mismatch len={actual_len} sha256={actual_sha}")
        if tx.get("chainId") not in (None, CHAIN_ID):
            raise SystemExit(f"{tx_hash}: unexpected chainId {tx.get('chainId')}")

        block_ts_hex = data["block_header"]["timestamp"]
        record = {
            "schema": "trinityaccord.ethereum-history-evidence.v1",
            "boundary": BOUNDARY,
            "label": label,
            "chain": "ethereum-mainnet",
            "chain_id": 1,
            "tx_hash": tx_hash,
            "ethereum_block_timestamp": {
                "unix": int(block_ts_hex, 16),
                "utc": iso_timestamp(block_ts_hex),
                "source_field": "block.timestamp",
                "meaning": "Timestamp accepted in the Ethereum block header containing this transaction; not a later preservation timestamp and not necessarily a wall-clock oracle.",
            },
            "calldata": {"length_bytes": actual_len, "sha256": actual_sha},
            "transaction": data["transaction"],
            "receipt": data["receipt"],
            "block_header": data["block_header"],
            "capture": {
                "observed_at_utc": captured_at,
                "agreeing_rpc_count": len(agreeing),
                "agreeing_rpcs": agreeing,
                "rpc_failures": errors,
                "comparison_scope": "transaction/block/receipt immutable core fields",
            },
            "verification_scope": {
                "preserves_original_block_timestamp": True,
                "preserves_transaction_and_receipt_context": True,
                "self_contained_canonical_chain_proof": False,
                "note": "The saved block header is hash-checkable evidence. Canonical-chain inclusion should be rechecked against Ethereum history/checkpoints; this bundle does not overclaim a standalone MPT plus chain proof.",
            },
        }
        path = txdir / f"{tx_hash}.json"
        path.write_text(json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        manifest_records.append({
            "label": label,
            "tx_hash": tx_hash,
            "block_number": int(tx["blockNumber"], 16),
            "block_hash": tx["blockHash"],
            "ethereum_block_timestamp_unix": int(block_ts_hex, 16),
            "ethereum_block_timestamp_utc": iso_timestamp(block_ts_hex),
            "calldata_len": actual_len,
            "calldata_sha256": actual_sha,
            "evidence_path": str(path),
            "agreeing_rpc_count": len(agreeing),
        })

    manifest = {
        "schema": "trinityaccord.ethereum-history-evidence-manifest.v1",
        "boundary": BOUNDARY,
        "generated_at": captured_at,
        "chain": "ethereum-mainnet",
        "chain_id": 1,
        "record_count": len(manifest_records),
        "records": manifest_records,
        "timestamp_semantics": {
            "ethereum_block_timestamp": "The block.header timestamp of the block that includes the transaction.",
            "capture_generated_at": "A later observation/preservation time; it does not replace or backdate the Ethereum timestamp.",
        },
        "limitations": [
            "This compact bundle does not claim a fully self-contained proof that each saved block is canonical without an Ethereum chain/checkpoint source.",
            "DOI, GitHub, or Arweave copies preserve these proof bytes but do not recreate the original Ethereum block timestamp.",
        ],
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
