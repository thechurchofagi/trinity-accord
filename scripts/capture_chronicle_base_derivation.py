#!/usr/bin/env python3
"""Capture Base NFT transactions in canonical OP Stack L1 batch data.

The official, pinned Optimism ``batch-decoder`` performs frame/channel/span-batch
decoding and recomputes each archived blob's KZG commitment.  This orchestrator
discovers each Base block's L1 origin, bounds the L1 search, invokes that decoder,
locates every target transaction in exactly one derived batch element, and then
constructs an Ethereum transactionsRoot MPT proof for every channel-frame L1
transaction needed by those elements.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import time
import urllib.request

import rlp
from eth_hash.auto import keccak
from trie import HexaryTrie

BASE_CHAIN_ID = 8453
BASE_GENESIS_TIME = 1686789347
BASE_BLOCK_TIME = 2
BASE_INBOX = "0xff00000000000000000000000000000000008453"
BASE_BATCHER = "0x5050f69a9786f081509234f1a7f4684b5e5b76c9"
L1_INFO_PREDEPLOY = "0x4200000000000000000000000000000000000015"
L1_INFO_SELECTORS = {
    keccak(b"setL1BlockValuesEcotone()")[:4]: 164,
    keccak(b"setL1BlockValuesIsthmus()")[:4]: 176,
    keccak(b"setL1BlockValuesJovian()")[:4]: 178,
}


def stable_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def h2b(value: str) -> bytes:
    value = value[2:] if value.startswith("0x") else value
    if len(value) % 2:
        value = "0" + value
    return bytes.fromhex(value)


def h2i(value) -> int:
    return int(value, 16) if isinstance(value, str) and value.startswith("0x") else int(value)


def intb(value) -> bytes:
    number = h2i(value)
    return b"" if number == 0 else number.to_bytes((number.bit_length() + 7) // 8, "big")


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class RPC:
    def __init__(self, endpoints: list[str], timeout: int = 45, retries: int = 3):
        self.endpoints = endpoints
        self.timeout = timeout
        self.retries = retries
        self.preferred = 0

    def call(self, method: str, params: list):
        last = None
        for attempt in range(self.retries):
            order = list(range(self.preferred, len(self.endpoints))) + list(range(self.preferred))
            for index in order:
                payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
                request = urllib.request.Request(
                    self.endpoints[index], payload, {"content-type": "application/json", "user-agent": "trinity-accord-base-derivation/1.0"}
                )
                try:
                    with urllib.request.urlopen(request, timeout=self.timeout) as response:
                        value = json.loads(response.read())
                    if not isinstance(value, dict) or value.get("error") or value.get("result") is None:
                        raise RuntimeError(f"JSON-RPC error: {value.get('error') if isinstance(value, dict) else value!r}")
                    self.preferred = index
                    return value["result"]
                except Exception as exc:
                    last = exc
            if attempt + 1 < self.retries:
                time.sleep(2**attempt)
        raise RuntimeError(f"RPC {method} failed: {last!r}")

    def batch(self, calls: list[tuple[str, list]]) -> list:
        """Execute a bounded JSON-RPC batch and preserve caller order.

        Raw signed transactions are required to rebuild an Ethereum transaction
        trie.  Fetching them one by one is both slower and more likely to hit a
        public provider's request-rate limit, so L1 block reconstruction uses
        batches while retaining the same endpoint failover and fail-closed
        response checks as ``call``.
        """
        if not calls:
            return []
        last = None
        for attempt in range(self.retries):
            order = list(range(self.preferred, len(self.endpoints))) + list(range(self.preferred))
            for endpoint_index in order:
                payload = [
                    {"jsonrpc": "2.0", "id": position + 1, "method": method, "params": params}
                    for position, (method, params) in enumerate(calls)
                ]
                request = urllib.request.Request(
                    self.endpoints[endpoint_index],
                    json.dumps(payload).encode(),
                    {"content-type": "application/json", "user-agent": "trinity-accord-base-derivation/1.0"},
                )
                try:
                    with urllib.request.urlopen(request, timeout=self.timeout) as response:
                        values = json.loads(response.read())
                    if not isinstance(values, list) or len(values) != len(calls):
                        raise RuntimeError("malformed or incomplete JSON-RPC batch")
                    indexed = {int(item.get("id")): item for item in values if isinstance(item, dict)}
                    if set(indexed) != set(range(1, len(calls) + 1)):
                        raise RuntimeError("JSON-RPC batch response ids do not match requests")
                    result = []
                    for position in range(1, len(calls) + 1):
                        item = indexed[position]
                        if item.get("error") or item.get("result") is None:
                            raise RuntimeError(f"JSON-RPC batch error: {item.get('error')!r}")
                        result.append(item["result"])
                    self.preferred = endpoint_index
                    return result
                except Exception as exc:
                    last = exc
            if attempt + 1 < self.retries:
                time.sleep(2**attempt)
        raise RuntimeError(f"RPC batch failed: {last!r}")


def endpoint_list(primary: str | None, fallback: str) -> list[str]:
    out = []
    for raw in (primary or "", fallback):
        for value in raw.replace("\n", ",").split(","):
            value = value.strip()
            if value and value not in out:
                out.append(value)
    return out


def parse_l1_info(data_hex: str) -> dict:
    data = h2b(data_hex)
    expected_len = L1_INFO_SELECTORS.get(data[:4])
    if expected_len is None or len(data) != expected_len:
        raise ValueError(f"unknown L1 info format selector=0x{data[:4].hex()} bytes={len(data)}")
    # Ecotone is a packed format; all later formats append fields and preserve
    # this prefix. See op-node/rollup/derive/l1_block_info.go.
    return {
        "selector": "0x" + data[:4].hex(),
        "format_bytes": len(data),
        "base_fee_scalar": int.from_bytes(data[4:8], "big"),
        "blob_base_fee_scalar": int.from_bytes(data[8:12], "big"),
        "sequence_number": int.from_bytes(data[12:20], "big"),
        "l1_timestamp": int.from_bytes(data[20:28], "big"),
        "l1_block_number": int.from_bytes(data[28:36], "big"),
        "l1_block_hash": "0x" + data[100:132].hex(),
        "batcher_address": "0x" + data[144:164].hex(),
    }


def merge_windows(numbers: list[int], before: int, after: int) -> list[tuple[int, int]]:
    windows = sorted((max(0, value - before), value + after + 1) for value in numbers)
    merged: list[list[int]] = []
    for start, end in windows:
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return [(start, end) for start, end in merged]


def tx_hash(raw_hex: str) -> str:
    return "0x" + keccak(h2b(raw_hex)).hex()


def batch_elements(batch: dict) -> list[dict]:
    if "span_batch_elements" in batch:
        return batch["span_batch_elements"]
    return [batch]


def element_field(element: dict, name: str):
    return element.get(name) if name in element else element.get(name[0].upper() + name[1:])


def find_targets(channel_dir: pathlib.Path, targets: dict[str, dict]) -> dict[str, dict]:
    matches: dict[str, list[dict]] = {key: [] for key in targets}
    for path in sorted(channel_dir.glob("*.json")):
        channel = json.loads(path.read_text())
        if channel.get("is_ready") is not True or channel.get("invalid_frames") is True or channel.get("invalid_batches") is True:
            continue
        frames = [
            {
                "transaction_hash": frame["transaction_hash"].lower(),
                "inclusion_block": int(frame["inclusion_block"]),
                "block_hash": frame["block_hash"].lower(),
                "frame_number": int(frame["frame"]["frame_number"]),
                "is_last": bool(frame["frame"]["is_last"]),
            }
            for frame in channel.get("frames", [])
        ]
        for batch_index, batch in enumerate(channel.get("batches", [])):
            for element_index, element in enumerate(batch_elements(batch)):
                timestamp = int(element_field(element, "timestamp"))
                if timestamp < BASE_GENESIS_TIME or (timestamp - BASE_GENESIS_TIME) % BASE_BLOCK_TIME:
                    raise ValueError(f"derived Base timestamp is off cadence: {timestamp}")
                block_number = (timestamp - BASE_GENESIS_TIME) // BASE_BLOCK_TIME
                for transaction_index, raw in enumerate(element_field(element, "transactions") or []):
                    digest = tx_hash(raw)
                    if digest in targets:
                        target = targets[digest]
                        if block_number != target["block_number"] or timestamp != target["timestamp_unix"]:
                            raise ValueError(f"derived target block/timestamp mismatch: {digest}")
                        matches[digest].append(
                            {
                                "channel_id": channel["id"],
                                "channel_file": path.name,
                                "batch_index": batch_index,
                                "element_index": element_index,
                                "transaction_index": transaction_index,
                                "raw_transaction": raw,
                                "raw_transaction_sha256": hashlib.sha256(h2b(raw)).hexdigest(),
                                "derived_l2_block_number": block_number,
                                "derived_l2_timestamp": timestamp,
                                "l1_origin_number": int(element_field(element, "epochNum")),
                                "channel_frames": frames,
                            }
                        )
    result = {}
    for digest, values in matches.items():
        if len(values) != 1:
            raise ValueError(f"target transaction derived match count={len(values)} hash={digest}")
        result[digest] = values[0]
    return result


def header_fields(block: dict) -> list[bytes]:
    fields = [
        h2b(block["parentHash"]), h2b(block["sha3Uncles"]), h2b(block["miner"]), h2b(block["stateRoot"]),
        h2b(block["transactionsRoot"]), h2b(block["receiptsRoot"]), h2b(block["logsBloom"]), intb(block["difficulty"]),
        intb(block["number"]), intb(block["gasLimit"]), intb(block["gasUsed"]), intb(block["timestamp"]),
        h2b(block["extraData"]), h2b(block["mixHash"]), h2b(block["nonce"]),
    ]
    for name, kind in (
        ("baseFeePerGas", "int"), ("withdrawalsRoot", "hex"), ("blobGasUsed", "int"),
        ("excessBlobGas", "int"), ("parentBeaconBlockRoot", "hex"), ("requestsHash", "hex"),
        ("blockAccessListHash", "hex"),
    ):
        if block.get(name) is not None:
            fields.append(intb(block[name]) if kind == "int" else h2b(block[name]))
    return fields


def l1_transaction_proofs(eth: RPC, frame_rows: list[dict], output: pathlib.Path) -> dict[str, dict]:
    wanted_by_block: dict[int, set[str]] = {}
    for frame in frame_rows:
        wanted_by_block.setdefault(frame["inclusion_block"], set()).add(frame["transaction_hash"].lower())
    result = {}
    for number, wanted in sorted(wanted_by_block.items()):
        block = eth.call("eth_getBlockByNumber", [hex(number), False])
        header_rlp = rlp.encode(header_fields(block))
        block_hash = "0x" + keccak(header_rlp).hex()
        if block_hash != block["hash"].lower():
            raise ValueError(f"Ethereum header hash mismatch block={number}")
        raw_transactions = []
        trie = HexaryTrie(db={})
        indexes = {}
        block_digests = block["transactions"]
        for batch_start in range(0, len(block_digests), 100):
            batch_digests = block_digests[batch_start : batch_start + 100]
            batch_raw = eth.batch([("eth_getRawTransactionByHash", [digest]) for digest in batch_digests])
            for offset, (digest, raw) in enumerate(zip(batch_digests, batch_raw)):
                index = batch_start + offset
                if tx_hash(raw) != digest.lower():
                    raise ValueError(f"raw Ethereum tx hash mismatch block={number} index={index}")
                raw_bytes = h2b(raw)
                raw_transactions.append(raw_bytes)
                trie[rlp.encode(index)] = raw_bytes
                if digest.lower() in wanted:
                    indexes[digest.lower()] = index
        if trie.root_hash != h2b(block["transactionsRoot"]):
            raise ValueError(f"Ethereum transactions trie mismatch block={number}")
        if set(indexes) != wanted:
            raise ValueError(f"missing channel frame tx in Ethereum block={number}")
        block_dir = output / "l1-proofs" / str(number)
        block_dir.mkdir(parents=True, exist_ok=True)
        for digest, index in indexes.items():
            key = rlp.encode(index)
            proof = ["0x" + rlp.encode(node).hex() for node in trie.get_proof(key)]
            row = {
                "transaction_hash": digest,
                "transaction_index": index,
                "raw_transaction": "0x" + raw_transactions[index].hex(),
                "mpt_key_rlp": "0x" + key.hex(),
                "transaction_proof_nodes_rlp": proof,
                "ethereum_block_number": number,
                "ethereum_block_hash": block_hash,
                "ethereum_block_timestamp": h2i(block["timestamp"]),
                "ethereum_block_header_rlp": "0x" + header_rlp.hex(),
                "transactions_root": block["transactionsRoot"].lower(),
            }
            proof_path = block_dir / f"{digest[2:]}.json"
            proof_path.write_text(json.dumps(row, indent=2, sort_keys=True) + "\n")
            result[digest] = {**row, "proof_file": str(proof_path.relative_to(output))}
        print(f"[BASE L1 TX PROOF] block={number} txs={len(indexes)} all_block_txs={len(raw_transactions)}", flush=True)
    return result


def run(command: list[str]) -> None:
    print("[RUN] " + " ".join(command), flush=True)
    started = time.monotonic()
    with subprocess.Popen(command) as process:
        while True:
            try:
                result = process.wait(timeout=30)
                break
            except subprocess.TimeoutExpired:
                print(f"[PROCESS HEARTBEAT] pid={process.pid} elapsed_s={time.monotonic()-started:.1f} state=running_not_verified", flush=True)
        if result:
            raise subprocess.CalledProcessError(result, command)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-timeline", type=pathlib.Path, required=True)
    parser.add_argument("--batch-decoder", type=pathlib.Path, required=True)
    parser.add_argument("--beacon-archive", required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--window-before", type=int, default=160)
    parser.add_argument("--window-after", type=int, default=200)
    parser.add_argument("--concurrency", type=int, default=12)
    args = parser.parse_args()
    base_rpc = RPC(endpoint_list(os.getenv("BASE_RPC_URL"), "https://mainnet.base.org,https://base-rpc.publicnode.com,https://base.drpc.org"))
    eth_rpc_urls = endpoint_list(os.getenv("ETH_RPC_URL"), "https://ethereum-rpc.publicnode.com,https://eth.drpc.org")
    eth_rpc = RPC(eth_rpc_urls)
    timeline_raw = args.base_timeline.read_bytes()
    timeline = json.loads(timeline_raw)
    if len(timeline) != 61:
        raise SystemExit(f"expected 61 Base records, got {len(timeline)}")
    targets = {row["transaction_hash"].lower(): row for row in timeline}
    if len(targets) != 61:
        raise SystemExit("Base target transaction hashes are not unique")

    origins = []
    base_witnesses = {}
    for position, (digest, row) in enumerate(sorted(targets.items(), key=lambda item: item[1]["block_number"]), 1):
        block = base_rpc.call("eth_getBlockByNumber", [hex(row["block_number"]), True])
        if block["hash"].lower() != row["block_hash"].lower():
            raise SystemExit(f"Base block hash mismatch target={digest}")
        block_timestamp = h2i(block["timestamp"])
        expected_timestamp = BASE_GENESIS_TIME + BASE_BLOCK_TIME * int(row["block_number"])
        if block_timestamp != int(row["timestamp_unix"]) or block_timestamp != expected_timestamp:
            raise SystemExit(f"Base block timestamp/cadence mismatch target={digest}")
        transactions = block.get("transactions", [])
        tx_hashes = [item["hash"].lower() for item in transactions]
        if digest not in tx_hashes:
            raise SystemExit(f"target transaction absent from Base block: {digest}")
        first = transactions[0]
        if str(first.get("to", "")).lower() != L1_INFO_PREDEPLOY:
            raise SystemExit(f"Base first transaction is not L1 info deposit: block={row['block_number']}")
        info = parse_l1_info(first.get("input") or first.get("data"))
        if info["batcher_address"] != BASE_BATCHER:
            raise SystemExit(f"unexpected Base batcher in L1 info: {info['batcher_address']}")
        l1 = eth_rpc.call("eth_getBlockByNumber", [hex(info["l1_block_number"]), False])
        if l1["hash"].lower() != info["l1_block_hash"] or h2i(l1["timestamp"]) != info["l1_timestamp"]:
            raise SystemExit(f"Base L1 origin block mismatch: base_block={row['block_number']}")
        origins.append(info["l1_block_number"])
        base_witnesses[digest] = {
            "asset_id": row["asset_id"],
            "base_block_number": row["block_number"],
            "base_block_hash": row["block_hash"].lower(),
            "base_block_timestamp": block_timestamp,
            "base_transaction_index": tx_hashes.index(digest),
            "l1_info": info,
        }
        print(f"[BASE ORIGIN {position}/61] l2={row['block_number']} l1={info['l1_block_number']} sequence={info['sequence_number']}", flush=True)

    out = args.output
    tx_dir = out / "decoder" / "transactions"
    channel_dir = out / "decoder" / "channels"
    tx_dir.mkdir(parents=True, exist_ok=True)
    channel_dir.mkdir(parents=True, exist_ok=True)
    windows = merge_windows(origins, args.window_before, args.window_after)
    # The pinned decoder's Beacon request deadline is only ten seconds. Warm
    # the shared archive first so it never waits on archival HTTP or backoff.
    from base_blob_archive_proxy import Archive
    archive = Archive(out / "decoder" / "blobs", os.getenv("BLOBSCAN_API", "https://api.blobscan.com"))
    capture_started = time.monotonic()
    total_blocks = sum(end - start for start, end in windows)
    completed_blocks = 0
    blob_references = 0
    for window_index, (start, end) in enumerate(windows, 1):
        print(f"[PREFETCH START] window={window_index}/{len(windows)} blocks={start}-{end-1} total_blocks={total_blocks}", flush=True)
        for offset in range(start, end, 10):
            numbers = list(range(offset, min(offset + 10, end)))
            blocks = eth_rpc.batch([("eth_getBlockByNumber", [hex(number), True]) for number in numbers])
            for number, block in zip(numbers, blocks):
                if h2i(block["number"]) != number:
                    raise ValueError("prefetch block number mismatch")
                for transaction in block["transactions"]:
                    if str(transaction.get("to") or "").lower() != BASE_INBOX:
                        continue
                    for versioned_hash in transaction.get("blobVersionedHashes", []):
                        print(f"[BLOB START] window={window_index}/{len(windows)} block={number} hash={versioned_hash} completed_references={blob_references}", flush=True)
                        archive.get(versioned_hash)
                        blob_references += 1
                        print(f"[BLOB DONE] completed_references={blob_references} elapsed_s={time.monotonic()-capture_started:.1f}", flush=True)
            completed_blocks += len(numbers)
            print(f"[BLOB PREFETCH] window={window_index}/{len(windows)} blocks={offset}-{numbers[-1]} completed_blocks={completed_blocks}/{total_blocks} blob_references={blob_references} elapsed_s={time.monotonic()-capture_started:.1f}", flush=True)
        print(f"[DECODE START] window={window_index}/{len(windows)}", flush=True)
        run(
            [
                str(args.batch_decoder), "fetch", "--start", str(start), "--end", str(end),
                "--inbox", BASE_INBOX, "--sender", BASE_BATCHER,
                "--l1", eth_rpc_urls[0], "--l1.beacon", args.beacon_archive,
                "--out", str(tx_dir), "--concurrent-requests", str(args.concurrency),
            ]
        )
        print(f"[DECODE DONE] window={window_index}/{len(windows)} elapsed_s={time.monotonic()-capture_started:.1f}", flush=True)
    print("[REASSEMBLE START] all fetch windows complete", flush=True)
    run([str(args.batch_decoder), "reassemble", "--in", str(tx_dir), "--out", str(channel_dir), "--l2-chain-id", str(BASE_CHAIN_ID)])
    derived = find_targets(channel_dir, targets)
    all_frames = []
    for item in derived.values():
        all_frames.extend(item["channel_frames"])
    unique_frames = {(row["transaction_hash"], row["inclusion_block"]): row for row in all_frames}
    l1_proofs = l1_transaction_proofs(eth_rpc, list(unique_frames.values()), out)
    records = []
    for digest, target in targets.items():
        match = derived[digest]
        if match["l1_origin_number"] != base_witnesses[digest]["l1_info"]["l1_block_number"]:
            raise SystemExit(f"derived/L2-info L1 origin mismatch: {digest}")
        for frame in match["channel_frames"]:
            if frame["transaction_hash"] not in l1_proofs:
                raise SystemExit(f"channel frame has no L1 MPT proof: {frame['transaction_hash']}")
            frame["l1_transaction_proof_file"] = l1_proofs[frame["transaction_hash"]]["proof_file"]
        records.append({"transaction_hash": digest, **base_witnesses[digest], "derivation": match})
    report = {
        "schema": "trinity-accord/chronicle-base-op-stack-derivation/v1",
        "pass": True,
        "source_base_timeline_sha256": hashlib.sha256(timeline_raw).hexdigest(),
        "network": {
            "l2_chain_id": BASE_CHAIN_ID,
            "l2_genesis_time": BASE_GENESIS_TIME,
            "l2_block_time": BASE_BLOCK_TIME,
            "batch_inbox": BASE_INBOX,
            "batcher": BASE_BATCHER,
        },
        "summary": {
            "records": len(records),
            "derived_records": len(derived),
            "l1_origin_blocks": len(set(origins)),
            "search_windows": len(windows),
            "channel_frame_transactions": len(unique_frames),
            "l1_transaction_mpt_proofs": len(l1_proofs),
        },
        "search_windows": [{"start": start, "end_exclusive": end} for start, end in windows],
        "records": sorted(records, key=lambda item: item["base_block_number"]),
        "assurance": {
            "blob_binding": "official OP Stack decoder recomputed KZG commitment and matched every signed L1 transaction versioned hash",
            "batch_derivation": "official OP Stack frame/channel/span-batch decoder; exact raw target transaction hash in derived block timestamp",
            "l1_inclusion": "Ethereum signed transaction MPT proof to transactionsRoot and locally rehashed execution header",
            "withdrawal_fault_proof": "NOT_APPLICABLE: these are ordinary L2 NFT transactions, not L2-to-L1 withdrawal claims",
        },
    }
    (out / "BASE-OP-STACK-DERIVATION.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"[BASE DERIVATION PASS] records={len(records)} frames={len(unique_frames)} l1_proofs={len(l1_proofs)}", flush=True)


if __name__ == "__main__":
    main()
