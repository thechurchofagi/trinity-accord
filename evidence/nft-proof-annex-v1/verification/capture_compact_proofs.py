#!/usr/bin/env python3
"""Capture compact, offline-verifiable Ethereum proofs for NFT mint records.

L2 reconstructs each target block trie during capture but preserves only the raw target
transaction, encoded target receipt, and the MPT proof nodes needed to prove both at the
declared transaction index. This avoids checking in every transaction/receipt in every
mint block.

L3 is stored once per unique execution block and reuses the established Trinity Accord
Ethereum Annex model: execution block hash SSZ-proven into the Beacon body, then Beacon
parent-root ancestry to an explicit weak-subjectivity trusted finalized descendant root.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
ETH_GENERATOR = ROOT / "evidence" / "ethereum-evidence-annex-v1" / "verification" / "generate_l2_l3_proofs.py"
NODE_HELPER_DEFAULT = ROOT / "evidence" / "ethereum-evidence-annex-v1" / "verification" / "make_beacon_execution_proof.mjs"
INDEX_DEFAULT = ROOT / "nft-identity-index.json"
OUT_DEFAULT = ROOT / "evidence" / "nft-proof-annex-v1" / "proof-material"


def load_eth_module():
    spec = importlib.util.spec_from_file_location("trinity_eth_proof_capture", ETH_GENERATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load established Ethereum proof generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def write_json(path: pathlib.Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(obj))


def proof_nodes_hex(eth, proof) -> list[str]:
    return ["0x" + eth.rlp.encode(node).hex() for node in proof]


def header_only(block: dict) -> dict:
    fields = [
        "hash", "parentHash", "sha3Uncles", "miner", "stateRoot", "transactionsRoot",
        "receiptsRoot", "logsBloom", "difficulty", "number", "gasLimit", "gasUsed",
        "timestamp", "extraData", "mixHash", "nonce", "baseFeePerGas", "withdrawalsRoot",
        "blobGasUsed", "excessBlobGas", "parentBeaconBlockRoot", "requestsHash",
    ]
    return {name: block[name] for name in fields if block.get(name) is not None}


def load_targets(path: pathlib.Path) -> tuple[list[dict], dict[str, list[dict]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assets = data.get("assets")
    if not isinstance(assets, list) or not assets:
        raise ValueError("NFT identity index has no assets")
    by_block: dict[str, list[dict]] = {}
    seen_tx: set[str] = set()
    for asset in assets:
        mint = asset.get("mint") or {}
        txh = str(mint.get("transaction_hash") or "").lower()
        blockh = str(mint.get("block_hash") or "").lower()
        if not txh.startswith("0x") or len(txh) != 66:
            raise ValueError("invalid NFT mint transaction hash")
        if not blockh.startswith("0x") or len(blockh) != 66:
            raise ValueError("invalid NFT mint block hash")
        if txh in seen_tx:
            raise ValueError(f"duplicate mint transaction in identity index: {txh}")
        seen_tx.add(txh)
        by_block.setdefault(blockh, []).append(asset)
    return assets, by_block


def build_trie(eth, values: list[bytes]):
    trie = eth.HexaryTrie(db={})
    for i, value in enumerate(values):
        trie[eth.rlp.encode(i)] = value
    return trie


def capture_block_l2(eth, rpc_url: str, block_hash: str, assets: list[dict], out: pathlib.Path) -> list[dict]:
    block = eth.rpc(rpc_url, "eth_getBlockByHash", [block_hash, False])
    if block["hash"].lower() != block_hash:
        raise RuntimeError(f"{block_hash}: execution block hash drift")
    if eth.execution_header_hash(block) != eth.h2b(block["hash"]):
        raise RuntimeError(f"{block_hash}: execution header hash failed")
    tx_hashes = [x.lower() for x in block["transactions"]]
    raw_hex = eth.rpc_batch(rpc_url, "eth_getRawTransactionByHash", [[h] for h in tx_hashes])
    raw_txs = [eth.h2b(x) for x in raw_hex]
    for expected, raw in zip(tx_hashes, raw_txs):
        if "0x" + eth.keccak(raw).hex() != expected:
            raise RuntimeError(f"{block_hash}: raw transaction hash mismatch for {expected}")
    receipts = eth.rpc(rpc_url, "eth_getBlockReceipts", [block["hash"]])
    if len(receipts) != len(tx_hashes):
        raise RuntimeError(f"{block_hash}: receipt count mismatch")
    encoded_receipts = [eth.encode_receipt(x) for x in receipts]
    tx_trie = build_trie(eth, raw_txs)
    receipt_trie = build_trie(eth, encoded_receipts)
    if "0x" + tx_trie.root_hash.hex() != block["transactionsRoot"].lower():
        raise RuntimeError(f"{block_hash}: transactionsRoot reconstruction failed")
    if "0x" + receipt_trie.root_hash.hex() != block["receiptsRoot"].lower():
        raise RuntimeError(f"{block_hash}: receiptsRoot reconstruction failed")

    summaries = []
    for asset in assets:
        mint = asset["mint"]
        txh = mint["transaction_hash"].lower()
        if txh not in tx_hashes:
            raise RuntimeError(f"{txh}: target absent from declared mint block")
        idx = tx_hashes.index(txh)
        if idx != int(mint["transaction_index"]):
            raise RuntimeError(f"{txh}: transaction index disagrees with identity index")
        receipt = receipts[idx]
        if receipt.get("transactionHash", "").lower() != txh:
            raise RuntimeError(f"{txh}: receipt transaction hash mismatch")
        if int(receipt.get("status", "0x1"), 16) != 1:
            raise RuntimeError(f"{txh}: failed mint receipt")
        wanted_log = int(mint["log_index"])
        positions = [i for i, log in enumerate(receipt.get("logs", [])) if int(log["logIndex"], 16) == wanted_log]
        if len(positions) != 1:
            raise RuntimeError(f"{txh}: cannot resolve unique receipt log position for global logIndex {wanted_log}")
        log_position = positions[0]
        key = eth.rlp.encode(idx)
        tx_proof = tx_trie.get_proof(key)
        receipt_proof = receipt_trie.get_proof(key)
        witness = {
            "schema": "trinityaccord.nft-ethereum-compact-execution-witness.v1",
            "canonical_key": asset.get("lookup", {}).get("canonical_key"),
            "target_tx_hash": txh,
            "target_transaction_index": idx,
            "receipt_log_position": log_position,
            "declared_global_log_index": str(mint["log_index"]),
            "block": header_only(block),
            "target_raw_transaction": raw_hex[idx],
            "target_encoded_receipt": "0x" + encoded_receipts[idx].hex(),
            "transaction_mpt_proof": {
                "key_rlp": "0x" + key.hex(),
                "root": block["transactionsRoot"].lower(),
                "nodes": proof_nodes_hex(eth, tx_proof),
            },
            "receipt_mpt_proof": {
                "key_rlp": "0x" + key.hex(),
                "root": block["receiptsRoot"].lower(),
                "nodes": proof_nodes_hex(eth, receipt_proof),
            },
            "verification": {
                "execution_header_hash": "PASS",
                "transactions_root_reconstructed_at_capture": "PASS",
                "receipts_root_reconstructed_at_capture": "PASS",
                "target_transaction_proof_generated": "PASS",
                "target_receipt_proof_generated": "PASS",
            },
            "claim_boundary": {
                "global_log_index": "Ethereum receipt RLP does not encode global logIndex; it is retained as the historical lookup coordinate used to derive receipt_log_position. Offline cryptographic verification binds the actual receipt log at receipt_log_position.",
                "canonicality": "L2 proves inclusion in the declared execution block; L3 separately proves that execution block into checkpoint-relative Beacon consensus history.",
            },
        }
        path = out / "L2" / f"{txh}.json"
        write_json(path, witness)
        summaries.append({
            "canonical_key": witness["canonical_key"],
            "tx_hash": txh,
            "block_hash": block_hash,
            "transaction_index": idx,
            "receipt_log_position": log_position,
            "path": path.relative_to(ROOT).as_posix(),
        })
    return summaries


def capture_block_l3(eth, block_hash: str, block_header: dict, out: pathlib.Path, beacons: list[str], node_helper: pathlib.Path) -> dict:
    primary = beacons[0]
    timestamp = eth.q(block_header["timestamp"])
    if timestamp < eth.GENESIS_TIME or (timestamp - eth.GENESIS_TIME) % eth.SECONDS_PER_SLOT:
        raise RuntimeError(f"{block_hash}: execution timestamp does not map exactly to Beacon slot")
    slot = (timestamp - eth.GENESIS_TIME) // eth.SECONDS_PER_SLOT
    beacon_block = eth.get_json(primary, f"/eth/v2/beacon/blocks/{slot}")
    target_dir = out / "L3" / block_hash
    tmp_block = target_dir / "beacon-block.tmp.json"
    tmp_proof = target_dir / "execution-leaf-proof.tmp.json"
    write_json(tmp_block, beacon_block)
    subprocess.run(["node", str(node_helper), str(tmp_block), str(tmp_proof)], check=True)
    leaf_proof = json.loads(tmp_proof.read_text(encoding="utf-8"))
    tmp_block.unlink()
    tmp_proof.unlink()
    target_header = eth.fetch_header(primary, str(slot))
    if leaf_proof["leaf"].lower() != block_hash:
        raise RuntimeError(f"{block_hash}: Beacon execution leaf mismatch")
    if leaf_proof["body_root"].lower() != target_header["message"]["body_root"].lower():
        raise RuntimeError(f"{block_hash}: Beacon body-root source mismatch")
    checkpoint, observations, chain = eth.find_trusted_finalized_root(beacons, primary, slot, target_header["root"])
    witness = {
        "schema": "trinityaccord.nft-ethereum-block-consensus-witness.v1",
        "execution_block_hash": block_hash,
        "target_beacon_slot": slot,
        "target_beacon_header": target_header,
        "execution_block_hash_to_body_root": leaf_proof,
        "trusted_finalized_beacon_root": checkpoint,
        "checkpoint_observations": observations,
        "checkpoint_to_target_parent_chain": chain,
        "verification_model": "execution block hash is SSZ-proven into target Beacon body; target Beacon root is linked by verified parent roots to an explicit trusted finalized descendant Beacon root",
    }
    path = target_dir / "L3-consensus-witness.json"
    write_json(path, witness)
    return {
        "block_hash": block_hash,
        "slot": slot,
        "trusted_finalized_root": checkpoint["root"],
        "trusted_finalized_slot": checkpoint["slot"],
        "ancestor_headers": len(chain),
        "path": path.relative_to(ROOT).as_posix(),
    }


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def bind_file(record: dict) -> dict:
    path = ROOT / record["path"]
    return {**record, "size": path.stat().st_size, "sha256": sha256_file(path)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default=str(INDEX_DEFAULT))
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    ap.add_argument("--rpc", default="https://ethereum-rpc.publicnode.com")
    ap.add_argument("--beacon", action="append", default=[])
    ap.add_argument("--node-helper", default=str(NODE_HELPER_DEFAULT))
    ap.add_argument("--skip-l3", action="store_true")
    args = ap.parse_args()
    eth = load_eth_module()
    index_path = pathlib.Path(args.index).resolve()
    out = pathlib.Path(args.out).resolve()
    node_helper = pathlib.Path(args.node_helper).resolve()
    beacons = args.beacon or ["https://ethereum-beacon-api.publicnode.com", "https://docs-demo.quiknode.pro"]
    genesis = eth.get_json(beacons[0], "/eth/v1/beacon/genesis")["data"]
    if int(genesis["genesis_time"]) != eth.GENESIS_TIME:
        raise RuntimeError("unexpected Ethereum mainnet genesis time")

    assets, by_block = load_targets(index_path)
    l2 = []
    l3 = []
    for number, block_hash in enumerate(sorted(by_block), 1):
        block_assets = by_block[block_hash]
        print(f"[{number}/{len(by_block)}] block {block_hash}: {len(block_assets)} NFT mint(s)", flush=True)
        block = eth.rpc(args.rpc, "eth_getBlockByHash", [block_hash, False])
        block_l2 = capture_block_l2(eth, args.rpc, block_hash, block_assets, out)
        l2.extend(block_l2)
        if not args.skip_l3:
            l3.append(capture_block_l3(eth, block_hash, header_only(block), out, beacons, node_helper))

    bound_l2 = [bind_file(x) for x in l2]
    bound_l3 = [bind_file(x) for x in l3]
    summary = {
        "schema": "trinityaccord.nft-ethereum-proof-capture-summary.v1",
        "index": {
            "path": index_path.relative_to(ROOT).as_posix(),
            "sha256": sha256_file(index_path),
            "nfts": len(assets),
            "unique_mint_transactions": len(l2),
            "unique_mint_blocks": len(by_block),
        },
        "proof_model": {
            "L2": "compact target transaction + target receipt MPT inclusion proof against a fully reconstructed block trie at capture time",
            "L3": "one checkpoint-relative Beacon consensus witness per unique execution block",
            "deduplication": "L2 grouped by block during reconstruction; L3 emitted once per unique block",
        },
        "l2_witnesses": bound_l2,
        "l3_witnesses": bound_l3,
    }
    write_json(out / "CAPTURE-SUMMARY.json", summary)
    print(json.dumps({
        "nfts": len(assets),
        "unique_mint_transactions": len(l2),
        "unique_mint_blocks": len(by_block),
        "l2_files": len(bound_l2),
        "l3_files": len(bound_l3),
    }, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise
