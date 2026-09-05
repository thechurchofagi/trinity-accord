#!/usr/bin/env python3
"""Offline verification of the frozen Base OP Stack derivation bundle."""
import argparse
import hashlib
import json
import pathlib

import rlp
from eth_hash.auto import keccak
from trie import HexaryTrie

from capture_chronicle_base_derivation import BASE_BLOCK_TIME, BASE_GENESIS_TIME, find_targets, h2b


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=pathlib.Path, required=True)
    parser.add_argument("--base-timeline", type=pathlib.Path, required=True)
    parser.add_argument("--channels", type=pathlib.Path)
    args = parser.parse_args()
    report_path = args.evidence / "BASE-OP-STACK-DERIVATION.json"
    report = json.loads(report_path.read_text())
    timeline_raw = args.base_timeline.read_bytes()
    timeline = json.loads(timeline_raw)
    if report.get("schema") != "trinity-accord/chronicle-base-op-stack-derivation/v1" or report.get("pass") is not True:
        raise SystemExit("unexpected or non-PASS Base report")
    if report.get("source_base_timeline_sha256") != hashlib.sha256(timeline_raw).hexdigest():
        raise SystemExit("Base timeline SHA-256 mismatch")
    if len(timeline) != 61 or report.get("summary", {}).get("records") != 61:
        raise SystemExit("Base population mismatch")
    source = {row["transaction_hash"].lower(): row for row in timeline}
    records = {row["transaction_hash"].lower(): row for row in report["records"]}
    if set(source) != set(records):
        raise SystemExit("Base transaction set mismatch")

    channels = args.channels or (args.evidence / "decoder" / "channels")
    rediscovered = find_targets(channels, source)
    proof_count = 0
    for digest, record in records.items():
        target = source[digest]
        derived = record["derivation"]
        again = rediscovered[digest]
        for field in ("channel_id", "batch_index", "element_index", "transaction_index", "raw_transaction", "derived_l2_block_number", "derived_l2_timestamp", "l1_origin_number"):
            if derived[field] != again[field]:
                raise SystemExit(f"fresh channel derivation mismatch tx={digest} field={field}")
        raw_tx = h2b(derived["raw_transaction"])
        if "0x" + keccak(raw_tx).hex() != digest:
            raise SystemExit(f"derived raw transaction hash mismatch: {digest}")
        if derived["derived_l2_block_number"] != target["block_number"]:
            raise SystemExit(f"derived block mismatch: {digest}")
        if derived["derived_l2_timestamp"] != BASE_GENESIS_TIME + BASE_BLOCK_TIME * target["block_number"]:
            raise SystemExit(f"derived timestamp mismatch: {digest}")
        if derived["derived_l2_timestamp"] != record["base_block_timestamp"]:
            raise SystemExit(f"derived/Base header timestamp mismatch: {digest}")
        if derived["l1_origin_number"] != record["l1_info"]["l1_block_number"]:
            raise SystemExit(f"derived/L2-info L1 origin mismatch: {digest}")
        for frame in derived["channel_frames"]:
            proof = json.loads((args.evidence / frame["l1_transaction_proof_file"]).read_text())
            header = h2b(proof["ethereum_block_header_rlp"])
            if "0x" + keccak(header).hex() != proof["ethereum_block_hash"]:
                raise SystemExit(f"Ethereum header hash mismatch: {proof['transaction_hash']}")
            header_fields = rlp.decode(header)
            if "0x" + bytes(header_fields[4]).hex() != proof["transactions_root"]:
                raise SystemExit(f"Ethereum transactionsRoot/header mismatch: {proof['transaction_hash']}")
            raw_l1 = h2b(proof["raw_transaction"])
            if "0x" + keccak(raw_l1).hex() != proof["transaction_hash"]:
                raise SystemExit(f"Ethereum raw transaction hash mismatch: {proof['transaction_hash']}")
            key = h2b(proof["mpt_key_rlp"])
            nodes = [rlp.decode(h2b(node)) for node in proof["transaction_proof_nodes_rlp"]]
            value = HexaryTrie.get_from_proof(bytes(header_fields[4]), key, nodes)
            if value != raw_l1:
                raise SystemExit(f"Ethereum transaction MPT proof mismatch: {proof['transaction_hash']}")
            proof_count += 1
    if len(rediscovered) != 61 or proof_count == 0:
        raise SystemExit("Base cold verification population is empty or incomplete")
    print(f"[BASE DERIVATION OFFLINE PASS] records={len(records)} frame_proofs={proof_count}")


if __name__ == "__main__":
    main()
