#!/usr/bin/env python3
"""Generate cryptographic L2 execution witnesses and checkpoint-relative L3 finality witnesses.

This generator is networked and intended for controlled capture. The resulting witness
files are verified offline by verify_annex.py. L3 is explicitly conditional on a named
trusted finalized checkpoint (weak-subjectivity assumption); the checkpoint source is
preserved and never hidden.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import pathlib
import subprocess
import time
import urllib.error
import urllib.request

import rlp
from eth_hash.auto import keccak
from trie import HexaryTrie

GENESIS_TIME = 1606824023
SECONDS_PER_SLOT = 12
SLOTS_PER_EPOCH = 32


def canonical(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def write_json(path: pathlib.Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(obj))


def h2b(value: str) -> bytes:
    if not isinstance(value, str) or not value.startswith("0x"):
        raise ValueError(f"not hex: {value!r}")
    raw = value[2:]
    if len(raw) % 2:
        raw = "0" + raw
    return bytes.fromhex(raw)


def q(value: str | None) -> int:
    if value is None:
        return 0
    return int(value, 16)


def rpc(url: str, method: str, params: list, *, timeout: int = 45):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}, separators=(",", ":")).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", "User-Agent": "trinityaccord-l2-l3-proof-capture/1"})
    last = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as res:
                payload = json.loads(res.read())
            if payload.get("error"):
                raise RuntimeError(f"{method}: {payload['error']}")
            if payload.get("result") is None:
                raise RuntimeError(f"{method}: null result")
            return payload["result"]
        except Exception as exc:
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"RPC {method} failed: {last}")


def rpc_batch(url: str, method: str, params_list: list[list], *, timeout: int = 90):
    reqs = [{"jsonrpc": "2.0", "id": i + 1, "method": method, "params": p} for i, p in enumerate(params_list)]
    body = json.dumps(reqs, separators=(",", ":")).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", "User-Agent": "trinityaccord-l2-l3-proof-capture/1"})
    last = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as res:
                payload = json.loads(res.read())
            if not isinstance(payload, list):
                raise RuntimeError("batch response is not a list")
            by_id = {item.get("id"): item for item in payload}
            out = []
            for i in range(1, len(reqs) + 1):
                item = by_id.get(i)
                if not item or item.get("error") or item.get("result") is None:
                    raise RuntimeError(f"{method} batch item {i}: {item}")
                out.append(item["result"])
            return out
        except Exception as exc:
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"RPC batch {method} failed: {last}")


def get_json(base: str, path: str, *, timeout: int = 45):
    url = base.rstrip("/") + path
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "trinityaccord-l2-l3-proof-capture/1"})
    last = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as res:
                return json.loads(res.read())
        except Exception as exc:
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"GET {url} failed: {last}")


def encode_receipt(receipt: dict) -> bytes:
    if "status" in receipt and receipt["status"] is not None:
        first = q(receipt["status"])
    elif receipt.get("root"):
        first = h2b(receipt["root"])
    else:
        raise ValueError("receipt has neither status nor root")
    logs = []
    for log in receipt.get("logs", []):
        logs.append([h2b(log["address"]), [h2b(t) for t in log.get("topics", [])], h2b(log.get("data", "0x"))])
    payload = rlp.encode([first, q(receipt["cumulativeGasUsed"]), h2b(receipt["logsBloom"]), logs])
    tx_type = q(receipt.get("type", "0x0"))
    return payload if tx_type == 0 else bytes([tx_type]) + payload


def execution_header_hash(block: dict) -> bytes:
    fields = [
        h2b(block["parentHash"]), h2b(block["sha3Uncles"]), h2b(block["miner"]),
        h2b(block["stateRoot"]), h2b(block["transactionsRoot"]), h2b(block["receiptsRoot"]),
        h2b(block["logsBloom"]), q(block["difficulty"]), q(block["number"]), q(block["gasLimit"]),
        q(block["gasUsed"]), q(block["timestamp"]), h2b(block["extraData"]), h2b(block["mixHash"]), h2b(block["nonce"]),
    ]
    optional = [
        ("baseFeePerGas", q), ("withdrawalsRoot", h2b), ("blobGasUsed", q), ("excessBlobGas", q),
        ("parentBeaconBlockRoot", h2b), ("requestsHash", h2b),
    ]
    for name, conv in optional:
        if block.get(name) is not None:
            fields.append(conv(block[name]))
    return keccak(rlp.encode(fields))


def build_root(values: list[bytes]) -> bytes:
    trie = HexaryTrie(db={})
    for i, value in enumerate(values):
        trie[rlp.encode(i)] = value
    return trie.root_hash


def merkleize_chunks(chunks: list[bytes]) -> bytes:
    if any(len(x) != 32 for x in chunks):
        raise ValueError("SSZ chunk must be 32 bytes")
    n = 1
    while n < len(chunks):
        n *= 2
    nodes = chunks + [b"\x00" * 32] * (n - len(chunks))
    while len(nodes) > 1:
        nodes = [hashlib.sha256(nodes[i] + nodes[i + 1]).digest() for i in range(0, len(nodes), 2)]
    return nodes[0]


def beacon_header_root(message: dict) -> str:
    fields = [
        int(message["slot"]).to_bytes(8, "little") + b"\x00" * 24,
        int(message["proposer_index"]).to_bytes(8, "little") + b"\x00" * 24,
        h2b(message["parent_root"]), h2b(message["state_root"]), h2b(message["body_root"]),
    ]
    return "0x" + merkleize_chunks(fields).hex()


def fetch_header(beacon: str, block_id: str) -> dict:
    data = get_json(beacon, f"/eth/v1/beacon/headers/{block_id}")["data"]
    computed = beacon_header_root(data["header"]["message"])
    if computed.lower() != data["root"].lower():
        raise RuntimeError(f"beacon header root mismatch {data['root']} != {computed}")
    return {"root": data["root"].lower(), "canonical": bool(data.get("canonical", True)), "message": data["header"]["message"]}


def find_checkpoint(beacons: list[str], primary: str, target_slot: int, target_root: str) -> tuple[dict, list[dict]]:
    for offset in (96, 128, 160, 192, 256, 320):
        state_slot = target_slot + offset
        observations = []
        for base in beacons:
            try:
                value = get_json(base, f"/eth/v1/beacon/states/{state_slot}/finality_checkpoints")["data"]["finalized"]
                observations.append({"provider": base, "state_slot": state_slot, "epoch": int(value["epoch"]), "root": value["root"].lower()})
            except Exception as exc:
                observations.append({"provider": base, "state_slot": state_slot, "error": str(exc)})
        good = [o for o in observations if "root" in o and o["root"] != "0x" + "00" * 32]
        counts = collections.Counter((o["epoch"], o["root"]) for o in good)
        if not counts:
            continue
        (epoch, root), votes = counts.most_common(1)[0]
        if votes < 2 and len(beacons) >= 2:
            continue
        chain = []
        cur = root
        found = False
        for _ in range(512):
            hdr = fetch_header(primary, cur)
            chain.append(hdr)
            parent = hdr["message"]["parent_root"].lower()
            if parent == target_root.lower():
                found = True
                break
            cur = parent
        if found:
            checkpoint = {
                "schema": "trinityaccord.ethereum-trusted-finalized-checkpoint.v1",
                "network": "Ethereum Mainnet",
                "state_slot_observed": state_slot,
                "finalized_epoch": epoch,
                "root": root,
                "trust_model": "explicit weak-subjectivity finalized checkpoint; quorum observations are provenance, not a substitute for the declared trust assumption",
                "matching_provider_votes": votes,
            }
            return checkpoint, observations, chain
    raise RuntimeError("could not find a cross-checked finalized checkpoint descending from target")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rpc", default="https://ethereum-rpc.publicnode.com")
    ap.add_argument("--beacon", action="append", default=[])
    ap.add_argument("--node-helper", required=True)
    args = ap.parse_args()
    beacons = args.beacon or [
        "https://ethereum-beacon-api.publicnode.com",
        "https://lodestar-mainnet.chainsafe.io",
        "https://mainnet-checkpoint-sync.attestant.io",
    ]
    primary = beacons[0]
    genesis = get_json(primary, "/eth/v1/beacon/genesis")["data"]
    if int(genesis["genesis_time"]) != GENESIS_TIME:
        raise SystemExit("unexpected Ethereum mainnet genesis time")

    manifest = json.loads(pathlib.Path(args.manifest).read_text(encoding="utf-8"))
    out = pathlib.Path(args.out)
    summary = []
    for anchor in manifest["anchors"]:
        txh = anchor["tx_hash"].lower()
        print(f"capturing {txh}", flush=True)
        target_dir = out / txh
        block = rpc(args.rpc, "eth_getBlockByHash", [anchor["execution_reference"]["block_hash"], False])
        if block["hash"].lower() != anchor["execution_reference"]["block_hash"].lower():
            raise RuntimeError(f"{txh}: execution block hash drift")
        if execution_header_hash(block).hex() != block["hash"][2:].lower():
            raise RuntimeError(f"{txh}: execution header hash failed")
        tx_hashes = [x.lower() for x in block["transactions"]]
        if txh not in tx_hashes:
            raise RuntimeError(f"{txh}: target absent from block transactions")
        target_index = tx_hashes.index(txh)
        raw_hex = rpc_batch(args.rpc, "eth_getRawTransactionByHash", [[h] for h in tx_hashes])
        raw_txs = [h2b(x) for x in raw_hex]
        for expected, raw in zip(tx_hashes, raw_txs):
            if "0x" + keccak(raw).hex() != expected:
                raise RuntimeError(f"{txh}: raw transaction hash mismatch for {expected}")
        receipts = rpc(args.rpc, "eth_getBlockReceipts", [block["hash"]])
        if len(receipts) != len(tx_hashes):
            raise RuntimeError(f"{txh}: receipt count mismatch")
        encoded_receipts = [encode_receipt(x) for x in receipts]
        tx_root = "0x" + build_root(raw_txs).hex()
        receipt_root = "0x" + build_root(encoded_receipts).hex()
        if tx_root.lower() != block["transactionsRoot"].lower():
            raise RuntimeError(f"{txh}: transactionsRoot reconstruction failed")
        if receipt_root.lower() != block["receiptsRoot"].lower():
            raise RuntimeError(f"{txh}: receiptsRoot reconstruction failed")
        witness = {
            "schema": "trinityaccord.ethereum-execution-inclusion-witness.v1",
            "target_tx_hash": txh,
            "target_transaction_index": target_index,
            "block": block,
            "raw_transactions": raw_hex,
            "encoded_receipts": ["0x" + x.hex() for x in encoded_receipts],
            "verification": {"execution_header_hash": "PASS", "transactions_root": "PASS", "receipts_root": "PASS"},
        }
        write_json(target_dir / "L2-execution-witness.json", witness)

        timestamp = q(block["timestamp"])
        if timestamp < GENESIS_TIME or (timestamp - GENESIS_TIME) % SECONDS_PER_SLOT:
            raise RuntimeError(f"{txh}: execution timestamp does not map exactly to beacon slot")
        slot = (timestamp - GENESIS_TIME) // SECONDS_PER_SLOT
        beacon_block = get_json(primary, f"/eth/v2/beacon/blocks/{slot}")
        tmp_block = target_dir / "beacon-block.tmp.json"
        tmp_proof = target_dir / "execution-leaf-proof.tmp.json"
        write_json(tmp_block, beacon_block)
        subprocess.run(["node", args.node_helper, str(tmp_block), str(tmp_proof)], check=True)
        leaf_proof = json.loads(tmp_proof.read_text(encoding="utf-8"))
        tmp_block.unlink()
        tmp_proof.unlink()
        target_header = fetch_header(primary, str(slot))
        if leaf_proof["leaf"].lower() != block["hash"].lower():
            raise RuntimeError(f"{txh}: beacon execution leaf is not execution block hash")
        if leaf_proof["body_root"].lower() != target_header["message"]["body_root"].lower():
            raise RuntimeError(f"{txh}: beacon body root proof source mismatch")
        checkpoint, observations, chain = find_checkpoint(beacons, primary, slot, target_header["root"])
        consensus = {
            "schema": "trinityaccord.ethereum-consensus-finality-witness.v1",
            "target_tx_hash": txh,
            "execution_block_hash": block["hash"].lower(),
            "target_beacon_slot": slot,
            "target_beacon_header": target_header,
            "execution_block_hash_to_body_root": leaf_proof,
            "trusted_finalized_checkpoint": checkpoint,
            "checkpoint_observations": observations,
            "checkpoint_to_target_parent_chain": chain,
            "verification_model": "execution block hash is SSZ-proven into target beacon body; target beacon root is linked by verified parent roots to the explicit trusted finalized checkpoint",
        }
        write_json(target_dir / "L3-consensus-witness.json", consensus)
        summary.append({"tx_hash": txh, "block_hash": block["hash"].lower(), "slot": slot, "checkpoint_root": checkpoint["root"], "checkpoint_epoch": checkpoint["finalized_epoch"], "ancestor_headers": len(chain)})
    write_json(out / "CAPTURE-SUMMARY.json", {"schema": "trinityaccord.ethereum-l2-l3-capture-summary.v1", "anchors": summary})
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
