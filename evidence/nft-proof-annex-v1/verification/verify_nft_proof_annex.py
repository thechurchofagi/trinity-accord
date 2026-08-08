#!/usr/bin/env python3
"""Fail-closed offline verifier for the NFT cryptographic proof annex."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import sys
from typing import Any

import rlp
from eth_hash.auto import keccak
from trie import HexaryTrie

ROOT = pathlib.Path(__file__).resolve().parents[3]
ANNEX = ROOT / "evidence" / "nft-proof-annex-v1"
COMMITMENT = ANNEX / "NFT-COLLECTION-COMMITMENT.json"
PROOF_DIR = ANNEX / "proof-material"
SUMMARY = PROOF_DIR / "CAPTURE-SUMMARY.json"
INDEX = ROOT / "nft-identity-index.json"
BUILD_SCRIPT = ROOT / "scripts" / "build_nft_cryptographic_commitment.py"
PRIMITIVES_DIR = ROOT / "evidence" / "ethereum-proof-primitives-v1"
PRIMITIVES_SCRIPT = PRIMITIVES_DIR / "ethereum_proof_primitives_v1.py"
PRIMITIVES_MANIFEST = PRIMITIVES_DIR / "PRIMITIVES-MANIFEST.json"
ZERO20 = b"\x00" * 20


def load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_frozen_primitives():
    manifest = json.loads(PRIMITIVES_MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("schema") != "trinityaccord.ethereum-proof-primitives-manifest.v1":
        raise ValueError("unexpected Ethereum proof primitives manifest schema")
    expected_rel = PRIMITIVES_SCRIPT.relative_to(ROOT).as_posix()
    if manifest.get("module_path") != expected_rel:
        raise ValueError("Ethereum proof primitives module path mismatch")
    digest = sha256_file(PRIMITIVES_SCRIPT)
    if digest != manifest.get("sha256"):
        raise ValueError("Ethereum proof primitives SHA-256 mismatch")
    return load_module("trinity_ethereum_proof_primitives_v1", PRIMITIVES_SCRIPT)


def h2b(value: str) -> bytes:
    if not isinstance(value, str) or not value.startswith("0x"):
        raise ValueError(f"not 0x hex: {value!r}")
    return bytes.fromhex(value[2:])


def int_bytes(value: bytes) -> int:
    return int.from_bytes(value, "big") if value else 0


def address_from_topic(value: bytes) -> str:
    if len(value) != 32:
        raise ValueError("address topic is not 32 bytes")
    return "0x" + value[-20:].hex()


def address_hex(value: bytes) -> str:
    if len(value) != 20:
        raise ValueError("log address is not 20 bytes")
    return "0x" + value.hex()


def require_address(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.startswith("0x") or len(value) != 42:
        raise ValueError(f"{field} must be a 20-byte 0x address")
    try:
        bytes.fromhex(value[2:])
    except ValueError as exc:
        raise ValueError(f"{field} must be a 20-byte 0x address") from exc
    return value.lower()


def decode_receipt(encoded: bytes) -> tuple[int, list]:
    if not encoded:
        raise ValueError("empty receipt")
    payload = encoded
    tx_type = 0
    # Typed receipts are EIP-2718 type-byte || rlp(payload). An RLP list starts >= 0xc0.
    if encoded[0] < 0xC0:
        tx_type = encoded[0]
        payload = encoded[1:]
    decoded = rlp.decode(payload)
    if not isinstance(decoded, list) or len(decoded) != 4:
        raise ValueError("invalid receipt RLP")
    return tx_type, decoded


def signed_transaction_chain_id(raw: bytes) -> int | None:
    """Return the signed transaction's EIP-155 chain id, if one is encoded."""
    if not raw:
        raise ValueError("empty raw transaction")
    if raw[0] < 0x80:
        tx_type = raw[0]
        if tx_type not in {1, 2, 3, 4}:
            raise ValueError(f"unsupported EIP-2718 transaction type: {tx_type}")
        decoded = rlp.decode(raw[1:])
        if not isinstance(decoded, list) or not decoded:
            raise ValueError("invalid typed transaction RLP")
        return int_bytes(decoded[0])

    decoded = rlp.decode(raw)
    if not isinstance(decoded, list) or len(decoded) != 9:
        raise ValueError("invalid legacy signed transaction RLP")
    v = int_bytes(decoded[6])
    if v in {27, 28}:
        return None
    if v < 35:
        raise ValueError("invalid legacy transaction v value")
    return (v - 35) // 2


def decode_uint_array(data: bytes, offset: int) -> list[int]:
    if offset % 32 != 0 or offset + 32 > len(data):
        raise ValueError("invalid ABI dynamic-array offset")
    count = int.from_bytes(data[offset:offset + 32], "big")
    end = offset + 32 + count * 32
    if end > len(data):
        raise ValueError("truncated ABI dynamic array")
    return [int.from_bytes(data[offset + 32 + i * 32:offset + 64 + i * 32], "big") for i in range(count)]


def verify_mint_log(asset: dict, encoded_receipt: bytes, log_position: int) -> dict:
    _, receipt = decode_receipt(encoded_receipt)
    status_or_root, _, _, logs = receipt
    if len(status_or_root) <= 1 and int_bytes(status_or_root) != 1:
        raise ValueError("receipt status is not success")
    if not isinstance(logs, list) or log_position < 0 or log_position >= len(logs):
        raise ValueError("receipt log position out of range")
    log = logs[log_position]
    if not isinstance(log, list) or len(log) != 3:
        raise ValueError("invalid receipt log")
    log_address, topics, data = log
    mint = asset["mint"]
    contract = asset["contract_address"].lower()
    if address_hex(log_address).lower() != contract:
        raise ValueError("mint log contract mismatch")
    if not topics:
        raise ValueError("mint log has no topics")

    transfer = keccak(b"Transfer(address,address,uint256)")
    transfer_single = keccak(b"TransferSingle(address,address,address,uint256,uint256)")
    transfer_batch = keccak(b"TransferBatch(address,address,address,uint256[],uint256[])")
    event = mint["event"]
    token_id = int(asset["token_id"])
    quantity = int(mint["quantity"])
    expected_to = mint["to"].lower()

    if event == "Transfer":
        if mint.get("operator") is not None:
            raise ValueError("ERC-721 mint operator must be null")
        if mint.get("batch_index") is not None:
            raise ValueError("ERC-721 mint batch_index must be null")
        if topics[0] != transfer or len(topics) != 4:
            raise ValueError("ERC-721 Transfer topic mismatch")
        if topics[1][-20:] != ZERO20:
            raise ValueError("ERC-721 mint does not originate from zero address")
        if address_from_topic(topics[2]).lower() != expected_to:
            raise ValueError("ERC-721 mint recipient mismatch")
        if int_bytes(topics[3]) != token_id or quantity != 1:
            raise ValueError("ERC-721 token/quantity mismatch")
        decoded_event = "erc721.Transfer"
    elif event == "TransferSingle":
        if mint.get("batch_index") is not None:
            raise ValueError("ERC-1155 TransferSingle batch_index must be null")
        expected_operator = require_address(mint.get("operator"), "ERC-1155 operator")
        if topics[0] != transfer_single or len(topics) != 4:
            raise ValueError("ERC-1155 TransferSingle topic mismatch")
        if topics[2][-20:] != ZERO20:
            raise ValueError("ERC-1155 mint does not originate from zero address")
        if address_from_topic(topics[3]).lower() != expected_to:
            raise ValueError("ERC-1155 recipient mismatch")
        if len(data) != 64 or int.from_bytes(data[:32], "big") != token_id or int.from_bytes(data[32:], "big") != quantity:
            raise ValueError("ERC-1155 TransferSingle token/quantity mismatch")
        if address_from_topic(topics[1]).lower() != expected_operator:
            raise ValueError("ERC-1155 operator mismatch")
        decoded_event = "erc1155.TransferSingle"
    elif event == "TransferBatch":
        expected_operator = require_address(mint.get("operator"), "ERC-1155 batch operator")
        if mint.get("batch_index") is None:
            raise ValueError("ERC-1155 TransferBatch batch_index is required")
        if isinstance(mint["batch_index"], bool):
            raise ValueError("ERC-1155 TransferBatch batch_index is invalid")
        try:
            batch_index = int(mint["batch_index"])
        except (TypeError, ValueError) as exc:
            raise ValueError("ERC-1155 TransferBatch batch_index is invalid") from exc
        if topics[0] != transfer_batch or len(topics) != 4:
            raise ValueError("ERC-1155 TransferBatch topic mismatch")
        if topics[2][-20:] != ZERO20:
            raise ValueError("ERC-1155 batch mint does not originate from zero address")
        if address_from_topic(topics[3]).lower() != expected_to:
            raise ValueError("ERC-1155 batch recipient mismatch")
        if len(data) < 64:
            raise ValueError("truncated TransferBatch data")
        ids = decode_uint_array(data, int.from_bytes(data[:32], "big"))
        values = decode_uint_array(data, int.from_bytes(data[32:64], "big"))
        if len(ids) != len(values):
            raise ValueError("TransferBatch ids/values mismatch")
        if batch_index < 0 or batch_index >= len(ids) or ids[batch_index] != token_id or values[batch_index] != quantity:
            raise ValueError("ERC-1155 TransferBatch item mismatch")
        if address_from_topic(topics[1]).lower() != expected_operator:
            raise ValueError("ERC-1155 batch operator mismatch")
        decoded_event = "erc1155.TransferBatch"
    else:
        raise ValueError(f"unsupported mint event: {event}")
    return {"event": decoded_event, "token_id": str(token_id), "quantity": str(quantity), "receipt_log_position": log_position}


def decode_proof_nodes(values: list[str]) -> tuple[Any, ...]:
    return tuple(rlp.decode(h2b(value)) for value in values)


def verify_commitment() -> dict:
    builder = load_module("trinity_nft_commitment", BUILD_SCRIPT)
    expected = builder.render(builder.build(INDEX))
    if not COMMITMENT.is_file():
        raise ValueError("missing NFT collection commitment")
    actual = COMMITMENT.read_bytes()
    if actual != expected:
        raise ValueError("NFT collection commitment drift")
    data = json.loads(actual)
    if data["source"]["asset_count"] != 175:
        raise ValueError("NFT commitment must cover exactly 175 records")
    return {
        "status": "PASS",
        "asset_count": data["source"]["asset_count"],
        "root_sha256": data["merkle"]["root_sha256"],
        "source_sha256": data["source"]["sha256"],
        "unique_transactions": data["mint_evidence_inventory"]["unique_transactions"],
        "unique_execution_blocks": data["mint_evidence_inventory"]["unique_execution_blocks"],
    }


def index_by_tx() -> dict[str, dict]:
    data = json.loads(INDEX.read_text(encoding="utf-8"))
    result = {}
    for asset in data["assets"]:
        txh = asset["mint"]["transaction_hash"].lower()
        if txh in result:
            raise ValueError(f"duplicate NFT mint transaction: {txh}")
        result[txh] = asset
    return result


def verify_bound(record: dict) -> pathlib.Path:
    path = ROOT / record["path"]
    if not path.is_file():
        raise ValueError(f"missing proof file: {record['path']}")
    if path.stat().st_size != int(record["size"]) or sha256_file(path) != record["sha256"]:
        raise ValueError(f"proof byte binding mismatch: {record['path']}")
    return path


def verify_l2(record: dict, asset: dict, ethv) -> dict:
    path = verify_bound(record)
    witness = json.loads(path.read_text(encoding="utf-8"))
    mint = asset["mint"]
    txh = mint["transaction_hash"].lower()
    if witness.get("schema") != "trinityaccord.nft-ethereum-compact-execution-witness.v1":
        raise ValueError("unexpected compact L2 schema")
    if witness.get("target_tx_hash", "").lower() != txh:
        raise ValueError("compact L2 target transaction mismatch")

    canonical_key = (asset.get("lookup") or {}).get("canonical_key")
    if not canonical_key or record.get("canonical_key") != canonical_key:
        raise ValueError("compact L2 canonical NFT key mismatch")

    block = witness["block"]
    block_hash = block["hash"].lower()
    if block_hash != mint["block_hash"].lower():
        raise ValueError("compact L2 block hash mismatch")
    if record.get("block_hash", "").lower() != block_hash:
        raise ValueError("compact L2 capture-summary block hash mismatch")
    if int(block["number"], 16) != int(mint["block_number"]):
        raise ValueError("compact L2 block number mismatch")
    if ethv.execution_header_hash(block) != h2b(block["hash"]):
        raise ValueError("compact L2 execution header hash mismatch")

    idx = int(witness["target_transaction_index"])
    if idx != int(mint["transaction_index"]):
        raise ValueError("compact L2 transaction index mismatch")
    if int(record.get("transaction_index", -1)) != idx:
        raise ValueError("compact L2 capture-summary transaction index mismatch")

    raw_tx = h2b(witness["target_raw_transaction"])
    if "0x" + keccak(raw_tx).hex() != txh:
        raise ValueError("compact L2 raw transaction hash mismatch")
    chain = asset.get("chain") or {}
    if chain.get("namespace") != "eip155":
        raise ValueError("compact L2 NFT chain namespace is not eip155")
    signed_chain_id = signed_transaction_chain_id(raw_tx)
    if signed_chain_id is None or signed_chain_id != int(chain["chain_id"]):
        raise ValueError("compact L2 signed transaction chain ID mismatch")

    key = rlp.encode(idx)
    if h2b(witness["transaction_mpt_proof"]["key_rlp"]) != key:
        raise ValueError("transaction MPT key mismatch")
    if witness["transaction_mpt_proof"]["root"].lower() != block["transactionsRoot"].lower():
        raise ValueError("transaction MPT root declaration mismatch")
    got_tx = HexaryTrie.get_from_proof(h2b(block["transactionsRoot"]), key, decode_proof_nodes(witness["transaction_mpt_proof"]["nodes"]))
    if got_tx != raw_tx:
        raise ValueError("transaction MPT inclusion proof mismatch")

    encoded_receipt = h2b(witness["target_encoded_receipt"])
    if h2b(witness["receipt_mpt_proof"]["key_rlp"]) != key:
        raise ValueError("receipt MPT key mismatch")
    if witness["receipt_mpt_proof"]["root"].lower() != block["receiptsRoot"].lower():
        raise ValueError("receipt MPT root declaration mismatch")
    got_receipt = HexaryTrie.get_from_proof(h2b(block["receiptsRoot"]), key, decode_proof_nodes(witness["receipt_mpt_proof"]["nodes"]))
    if got_receipt != encoded_receipt:
        raise ValueError("receipt MPT inclusion proof mismatch")

    _, decoded_receipt = decode_receipt(encoded_receipt)
    status_or_root = decoded_receipt[0]
    if len(status_or_root) > 1:
        raise ValueError("compact L2 receipt does not expose a post-Byzantium status")
    actual_status = int_bytes(status_or_root)
    if mint.get("receipt_status") is None or actual_status != int(mint["receipt_status"]):
        raise ValueError("compact L2 receipt status mismatch")

    event = mint["event"]
    expected_standard = "erc721" if event == "Transfer" else "erc1155" if event in {"TransferSingle", "TransferBatch"} else None
    if expected_standard is None or str(asset.get("standard", "")).lower() != expected_standard:
        raise ValueError("compact L2 token standard/event mismatch")

    if str(witness.get("declared_global_log_index")) != str(mint["log_index"]):
        raise ValueError("compact L2 historical global logIndex binding mismatch")
    log_position = int(witness["receipt_log_position"])
    if int(record.get("receipt_log_position", -1)) != log_position:
        raise ValueError("compact L2 capture-summary receipt log position mismatch")

    event_result = verify_mint_log(asset, encoded_receipt, log_position)
    return {
        "status": "PASS",
        "tx_hash": txh,
        "block_hash": block_hash,
        "block_timestamp": int(block["timestamp"], 16),
        "transaction_index": idx,
        **event_result,
    }


def verify_l3(record: dict, expected_block_hash: str, block_timestamp: int, ethv) -> dict:
    path = verify_bound(record)
    witness = json.loads(path.read_text(encoding="utf-8"))
    if witness.get("schema") != "trinityaccord.nft-ethereum-block-consensus-witness.v1":
        raise ValueError("unexpected NFT L3 schema")
    if witness.get("execution_block_hash", "").lower() != expected_block_hash:
        raise ValueError("NFT L3 execution block mismatch")
    target = witness["target_beacon_header"]
    target_root = ethv.beacon_header_root(target["message"]).lower()
    if target_root != target["root"].lower():
        raise ValueError("NFT L3 target Beacon header root mismatch")
    if block_timestamp < ethv.GENESIS_TIME or (block_timestamp - ethv.GENESIS_TIME) % ethv.SECONDS_PER_SLOT:
        raise ValueError("NFT execution timestamp does not map exactly to Beacon slot")
    expected_slot = (block_timestamp - ethv.GENESIS_TIME) // ethv.SECONDS_PER_SLOT
    if int(target["message"]["slot"]) != expected_slot or int(witness["target_beacon_slot"]) != expected_slot:
        raise ValueError("NFT L3 target slot mismatch")
    leaf = witness["execution_block_hash_to_body_root"]
    if leaf["leaf"].lower() != expected_block_hash:
        raise ValueError("NFT L3 execution hash leaf mismatch")
    body_root = target["message"]["body_root"].lower()
    if leaf["body_root"].lower() != body_root:
        raise ValueError("NFT L3 body-root declaration mismatch")
    ethv.verify_single_ssz_proof(leaf, body_root)

    checkpoint = witness["trusted_finalized_beacon_root"]
    if checkpoint.get("schema") != "trinityaccord.ethereum-trusted-finalized-beacon-root.v1":
        raise ValueError("unexpected trusted finalized root schema")
    trust_model = checkpoint.get("trust_model", "")
    if "weak-subjectivity" not in trust_model or "explicit" not in trust_model or "provenance only" not in trust_model:
        raise ValueError("NFT L3 weak-subjectivity boundary is not explicit")
    checkpoint_root = checkpoint["root"].lower()
    checkpoint_slot = int(checkpoint["slot"])
    if checkpoint_slot <= expected_slot:
        raise ValueError("NFT L3 checkpoint is not a descendant")
    votes = int(checkpoint.get("matching_provider_votes", 0))
    finalized_votes = int(checkpoint.get("finalized_provider_votes", 0))
    observations = witness.get("checkpoint_observations", [])
    observed_matches = sum(1 for o in observations if o.get("root", "").lower() == checkpoint_root and int(o.get("observed_slot", -1)) == checkpoint_slot and o.get("canonical") is True)
    observed_finalized = sum(1 for o in observations if o.get("root", "").lower() == checkpoint_root and int(o.get("observed_slot", -1)) == checkpoint_slot and o.get("canonical") is True and o.get("finalized") is True and o.get("execution_optimistic") is False)
    if votes < 2 or observed_matches < votes or finalized_votes < 1 or observed_finalized < finalized_votes:
        raise ValueError("NFT L3 checkpoint provenance quorum mismatch")
    expected = checkpoint_root
    chain = witness.get("checkpoint_to_target_parent_chain", [])
    if not chain:
        raise ValueError("NFT L3 empty checkpoint ancestry")
    for item in chain:
        computed = ethv.beacon_header_root(item["message"]).lower()
        if computed != item["root"].lower() or computed != expected:
            raise ValueError("NFT L3 ancestry header mismatch")
        expected = item["message"]["parent_root"].lower()
    if expected != target_root:
        raise ValueError("NFT L3 checkpoint is not linked to target Beacon block")
    return {
        "status": "PASS",
        "block_hash": expected_block_hash,
        "target_beacon_root": target_root,
        "target_beacon_slot": expected_slot,
        "trusted_finalized_root": checkpoint_root,
        "trusted_finalized_slot": checkpoint_slot,
        "ancestor_headers": len(chain),
    }


def main() -> int:
    failures = []
    report: dict[str, Any] = {"schema": "trinityaccord.nft-proof-offline-verification.v1"}
    try:
        commitment = verify_commitment()
        report["L1_COLLECTION_COMMITMENT"] = commitment
        summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        if summary.get("schema") != "trinityaccord.nft-ethereum-proof-capture-summary.v1":
            raise ValueError("unexpected NFT proof capture summary schema")
        if summary["index"]["sha256"] != sha256_file(INDEX):
            raise ValueError("NFT proof summary is bound to a different identity index")
        assets = index_by_tx()
        if len(assets) != 175:
            raise ValueError("NFT identity index must contain 175 unique mint transactions")
        if len(summary["l2_witnesses"]) != len(assets):
            raise ValueError("L2 witness count does not cover all NFT mint transactions")
        ethv = load_frozen_primitives()
        l2_results = []
        block_timestamps: dict[str, int] = {}
        for record in summary["l2_witnesses"]:
            txh = record["tx_hash"].lower()
            asset = assets.get(txh)
            if asset is None:
                raise ValueError(f"L2 witness targets unknown NFT mint tx: {txh}")
            result = verify_l2(record, asset, ethv)
            l2_results.append(result)
            previous = block_timestamps.setdefault(result["block_hash"], result["block_timestamp"])
            if previous != result["block_timestamp"]:
                raise ValueError("inconsistent timestamp for shared mint block")
        expected_blocks = {asset["mint"]["block_hash"].lower() for asset in assets.values()}
        if set(block_timestamps) != expected_blocks:
            raise ValueError("L2 witnesses do not cover the exact NFT mint block set")
        l3_records = {record["block_hash"].lower(): record for record in summary["l3_witnesses"]}
        if set(l3_records) != expected_blocks:
            raise ValueError("L3 witnesses do not cover the exact unique NFT mint block set")
        l3_results = [verify_l3(l3_records[block], block, block_timestamps[block], ethv) for block in sorted(expected_blocks)]
        report["L2_EXECUTION_INCLUSION"] = {"status": "PASS", "mint_transactions": len(l2_results), "checks": l2_results}
        report["L3_CONSENSUS_FINALITY"] = {"status": "PASS", "unique_execution_blocks": len(l3_results), "checks": l3_results, "trust_boundary": "PASS is conditional on each explicitly declared weak-subjectivity trusted finalized Beacon root; provider agreement/finality observations are provenance only."}
        if commitment["unique_transactions"] != len(l2_results) or commitment["unique_execution_blocks"] != len(l3_results):
            raise ValueError("commitment inventory and proof inventory disagree")
    except Exception as exc:
        failures.append(str(exc))
    report["result"] = "PASS" if not failures else "FAIL"
    report["failures"] = failures
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
