#!/usr/bin/env python3
"""Capture additive Ethereum-settlement witnesses for Chronicle Polygon/Base evidence.

Polygon: reconstruct the official checkpoint Merkle tree, prove each referenced Bor
block is a checkpoint leaf, and prove the checkpoint submission receipt is included
in an Ethereum execution block. Base: capture the strongest standard-RPC L1-origin
binding available for each referenced L2 block and probe OP output-root support.

Nothing in this script upgrades a partial observation into a stronger claim. Every
network attempt is written to a JSONL trace for future debugging.
"""
from __future__ import annotations

import concurrent.futures
import hashlib
import json
import math
import os
import pathlib
import threading
import time
import urllib.error
import urllib.request
from typing import Any

import rlp
from eth_hash.auto import keccak
from trie import HexaryTrie

OUT = pathlib.Path(os.getenv("CHRONICLE_OUT", "artifacts/chronicle-sidechain-scan"))
EVID = OUT / "evidence-v2"
SETTLE = EVID / "settlement-v1"
TRACE = SETTLE / "attempts.jsonl"
ROOT_CHAIN = "0x86E4Dc95c7FBdBf52e33D563BbDB00823894C287"
BASE_L1_BLOCK = "0x4200000000000000000000000000000000000015"
BASE_CONTRACTS = {
    "optimism_portal": "0x49048044D57e1C92A77f79988d21Fa8fAF74E97e",
    "dispute_game_factory": "0x43edB88C4B80fDD2AdFF2412A7BebF9dF42cB40e",
    "anchor_state_registry": "0x909f6cf47ed12f010A796527f562bFc26C7F4E72",
}
NEW_HEADER_SIG = "0x" + keccak(b"NewHeaderBlock(address,uint256,uint256,uint256,uint256,bytes32)").hex()
TRACE_LOCK = threading.Lock()


def endpoints(primary: str | None, fallbacks: str) -> list[str]:
    out: list[str] = []
    for raw in (primary or "", fallbacks):
        for v in raw.replace("\n", ",").split(","):
            v = v.strip().rstrip("/")
            if v and v not in out:
                out.append(v)
    return out


RPC = {
    "ethereum": endpoints(os.getenv("ETH_RPC_URL"), os.getenv("CHRONICLE_ETH_RPC_FALLBACK_URLS", "https://ethereum-rpc.publicnode.com,https://eth.drpc.org")),
    "polygon": endpoints(os.getenv("POLYGON_RPC_URL"), os.getenv("CHRONICLE_POLYGON_RPC_FALLBACK_URLS", "https://polygon.drpc.org,https://polygon-bor-rpc.publicnode.com")),
    "base": endpoints(os.getenv("BASE_RPC_URL"), os.getenv("CHRONICLE_BASE_RPC_FALLBACK_URLS", "https://base.drpc.org,https://base-rpc.publicnode.com,https://mainnet.base.org")),
}
TIMEOUT = int(os.getenv("CHRONICLE_SETTLEMENT_HTTP_TIMEOUT_SECONDS", "45"))
RETRIES = int(os.getenv("CHRONICLE_SETTLEMENT_HTTP_RETRIES", "2"))
CONCURRENCY = max(1, min(24, int(os.getenv("CHRONICLE_SETTLEMENT_CONCURRENCY", "12"))))
PREFERRED = {k: 0 for k in RPC}
PREF_LOCK = threading.Lock()


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def jwrite(path: pathlib.Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def trace(event: str, **kw: Any) -> None:
    row = {"ts": now(), "event": event, **kw}
    SETTLE.mkdir(parents=True, exist_ok=True)
    with TRACE_LOCK:
        with TRACE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, sort_keys=True) + "\n")
    print("[SETTLEMENT] " + json.dumps(row, sort_keys=True), flush=True)


def rpc(chain: str, method: str, params: list[Any], retries: int | None = None) -> Any:
    rounds = (RETRIES if retries is None else retries) + 1
    last = None
    for attempt in range(rounds):
        with PREF_LOCK:
            pref = PREFERRED[chain]
        order = list(range(pref, len(RPC[chain]))) + list(range(pref))
        for idx in order:
            endpoint = RPC[chain][idx]
            payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
            req = urllib.request.Request(endpoint, data=payload, headers={"content-type": "application/json", "user-agent": "trinity-sidechain-settlement/1.0"})
            try:
                with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
                    data = json.loads(res.read())
                if data.get("error"):
                    raise RuntimeError(str(data["error"]))
                with PREF_LOCK:
                    PREFERRED[chain] = idx
                trace("rpc_ok", chain=chain, method=method, endpoint_index=idx + 1, attempt=attempt + 1)
                return data.get("result")
            except Exception as exc:
                last = exc
                trace("rpc_error", chain=chain, method=method, endpoint_index=idx + 1, attempt=attempt + 1, error=str(exc)[:500])
        if attempt + 1 < rounds:
            time.sleep(min(2 ** attempt, 8))
    raise RuntimeError(f"{chain} {method} failed: {last}")


def h2i(v: Any) -> int:
    if isinstance(v, int):
        return v
    return int(v, 16) if str(v).startswith("0x") else int(v)


def h2b(v: Any, allow_none: bool = False) -> bytes:
    if v is None and allow_none:
        return b""
    s = str(v)
    if s.startswith("0x"):
        s = s[2:]
    if len(s) % 2:
        s = "0" + s
    return bytes.fromhex(s)


def intb(v: Any) -> bytes:
    n = h2i(v)
    return b"" if n == 0 else n.to_bytes((n.bit_length() + 7) // 8, "big")


def selector(signature: str) -> str:
    return "0x" + keccak(signature.encode())[:4].hex()


def eth_call(chain: str, to: str, data: str, block: str = "latest") -> str:
    result = rpc(chain, "eth_call", [{"to": to, "data": data}, block])
    if not isinstance(result, str) or not result.startswith("0x"):
        raise RuntimeError("invalid eth_call result")
    return result


def header_fields(block: dict[str, Any]) -> list[bytes]:
    fields = [
        h2b(block["parentHash"]), h2b(block["sha3Uncles"]), h2b(block["miner"]), h2b(block["stateRoot"]),
        h2b(block["transactionsRoot"]), h2b(block["receiptsRoot"]), h2b(block["logsBloom"]), intb(block["difficulty"]),
        intb(block["number"]), intb(block["gasLimit"]), intb(block["gasUsed"]), intb(block["timestamp"]),
        h2b(block["extraData"]), h2b(block["mixHash"]), h2b(block["nonce"]),
    ]
    for name, kind in [("baseFeePerGas", "int"), ("withdrawalsRoot", "hex"), ("blobGasUsed", "int"), ("excessBlobGas", "int"), ("parentBeaconBlockRoot", "hex"), ("requestsHash", "hex")]:
        if block.get(name) is not None:
            fields.append(intb(block[name]) if kind == "int" else h2b(block[name]))
    return fields


def encode_log(log: dict[str, Any]) -> list[Any]:
    return [h2b(log["address"]), [h2b(x) for x in log.get("topics", [])], h2b(log.get("data", "0x"))]


def encode_receipt(rec: dict[str, Any]) -> bytes:
    first = intb(rec["status"]) if rec.get("status") is not None else h2b(rec["root"])
    fields = [first, intb(rec["cumulativeGasUsed"]), h2b(rec["logsBloom"]), [encode_log(x) for x in rec.get("logs", [])]]
    typ = h2i(rec.get("type", "0x0"))
    payload = rlp.encode(fields)
    return (bytes([typ]) + payload) if typ else payload


def block_header_proof_material(block: dict[str, Any]) -> dict[str, Any]:
    encoded = rlp.encode(header_fields(block))
    computed = "0x" + keccak(encoded).hex()
    if computed.lower() != block["hash"].lower():
        raise RuntimeError(f"block header mismatch computed={computed} rpc={block['hash']}")
    return {"number": h2i(block["number"]), "hash": block["hash"], "header_rlp": "0x" + encoded.hex(), "computed_hash": computed, "receipts_root": block["receiptsRoot"], "timestamp": h2i(block["timestamp"])}


def receipt_inclusion(chain: str, tx_hash: str) -> dict[str, Any]:
    rec = rpc(chain, "eth_getTransactionReceipt", [tx_hash])
    if not rec:
        raise RuntimeError("receipt missing")
    block = rpc(chain, "eth_getBlockByHash", [rec["blockHash"], True])
    if not block:
        raise RuntimeError("block missing")
    try:
        receipts = rpc(chain, "eth_getBlockReceipts", [block["hash"]], retries=0)
        if not isinstance(receipts, list) or len(receipts) != len(block["transactions"]):
            raise RuntimeError("batch receipt count mismatch")
        source = "eth_getBlockReceipts"
    except Exception:
        receipts = [rpc(chain, "eth_getTransactionReceipt", [tx["hash"]]) for tx in block["transactions"]]
        source = "per_transaction_receipts"
    trie = HexaryTrie(db={})
    encoded: list[bytes] = []
    target_index = None
    for idx, rr in enumerate(receipts):
        raw = encode_receipt(rr)
        trie[rlp.encode(idx)] = raw
        encoded.append(raw)
        if rr["transactionHash"].lower() == tx_hash.lower():
            target_index = idx
    if target_index is None:
        raise RuntimeError("target receipt absent from block")
    root = "0x" + trie.root_hash.hex()
    if root.lower() != block["receiptsRoot"].lower():
        raise RuntimeError(f"receipt root mismatch computed={root} header={block['receiptsRoot']}")
    key = rlp.encode(target_index)
    proof_nodes = ["0x" + rlp.encode(n).hex() for n in trie.get_proof(key)]
    return {
        "transaction_hash": tx_hash, "transaction_index": target_index, "receipt_source": source,
        "receipt_rlp": "0x" + encoded[target_index].hex(), "mpt_key_rlp": "0x" + key.hex(),
        "receipt_proof_nodes_rlp": proof_nodes, "ethereum_block": block_header_proof_material(block),
    }


def decode_header_block(raw: str) -> dict[str, Any]:
    b = h2b(raw)
    if len(b) < 160:
        raise RuntimeError(f"short headerBlocks result: {len(b)}")
    words = [b[i:i + 32] for i in range(0, 160, 32)]
    return {
        "root": "0x" + words[0].hex(), "start": int.from_bytes(words[1], "big"), "end": int.from_bytes(words[2], "big"),
        "created_at": int.from_bytes(words[3], "big"), "proposer": "0x" + words[4][-20:].hex(),
    }


def polygon_header_block(header_id: int) -> dict[str, Any]:
    data = selector("headerBlocks(uint256)") + header_id.to_bytes(32, "big").hex()
    row = decode_header_block(eth_call("ethereum", ROOT_CHAIN, data))
    row["header_block_id"] = header_id
    return row


def find_polygon_checkpoint(block_number: int, current_id: int, cache: dict[int, dict[str, Any]]) -> dict[str, Any]:
    lo, hi = 1, current_id // 10000
    while lo <= hi:
        mid = (lo + hi) // 2
        hid = mid * 10000
        row = cache.setdefault(hid, polygon_header_block(hid))
        if block_number < row["start"]:
            hi = mid - 1
        elif block_number > row["end"]:
            lo = mid + 1
        else:
            return row
    raise RuntimeError(f"no Polygon checkpoint covers block {block_number}")


def polygon_leaf(block: dict[str, Any]) -> bytes:
    packed = h2i(block["number"]).to_bytes(32, "big") + h2i(block["timestamp"]).to_bytes(32, "big") + h2b(block["transactionsRoot"]) + h2b(block["receiptsRoot"])
    return keccak(packed)


def merkle_layers(leaves: list[bytes]) -> list[list[bytes]]:
    if not leaves:
        raise RuntimeError("empty Merkle tree")
    depth = math.ceil(math.log2(len(leaves))) if len(leaves) > 1 else 0
    padded = leaves + [b"\x00" * 32] * ((1 << depth) - len(leaves))
    layers = [padded]
    while len(layers[-1]) > 1:
        cur = layers[-1]
        layers.append([keccak(cur[i] + cur[i + 1]) for i in range(0, len(cur), 2)])
    return layers


def merkle_proof(layers: list[list[bytes]], index: int) -> list[bytes]:
    proof = []
    for layer in layers[:-1]:
        proof.append(layer[index + 1] if index % 2 == 0 else layer[index - 1])
        index //= 2
    return proof


def verify_merkle(leaf: bytes, index: int, root: bytes, proof: list[bytes]) -> bool:
    h = leaf
    for p in proof:
        h = keccak(h + p) if index % 2 == 0 else keccak(p + h)
        index //= 2
    return h == root


def collect_witnesses(chain: str) -> list[dict[str, Any]]:
    root = EVID / "l2" / chain
    rows = []
    if root.exists():
        for p in root.rglob("witness.json"):
            row = json.loads(p.read_text())
            if row.get("pass"):
                rows.append(row)
    return rows


def fetch_polygon_range(start: int, end: int) -> list[dict[str, Any]]:
    def one(n: int) -> dict[str, Any]:
        b = rpc("polygon", "eth_getBlockByNumber", [hex(n), False])
        if not b:
            raise RuntimeError(f"Polygon block missing {n}")
        return b
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        return list(ex.map(one, range(start, end + 1)))


def checkpoint_event(checkpoint: dict[str, Any]) -> dict[str, Any]:
    hid = checkpoint["header_block_id"]
    topic_hid = "0x" + hid.to_bytes(32, "big").hex()
    logs = rpc("ethereum", "eth_getLogs", [{"fromBlock": "0x0", "toBlock": "latest", "address": ROOT_CHAIN, "topics": [NEW_HEADER_SIG, None, topic_hid]}])
    if not isinstance(logs, list) or len(logs) != 1:
        raise RuntimeError(f"expected one NewHeaderBlock log for {hid}, got {len(logs) if isinstance(logs, list) else 'non-list'}")
    log = logs[0]
    data = h2b(log["data"])
    if len(data) != 96:
        raise RuntimeError("unexpected NewHeaderBlock data length")
    start, end = int.from_bytes(data[:32], "big"), int.from_bytes(data[32:64], "big")
    root = "0x" + data[64:96].hex()
    if start != checkpoint["start"] or end != checkpoint["end"] or root.lower() != checkpoint["root"].lower():
        raise RuntimeError("NewHeaderBlock event disagrees with RootChain storage")
    inc = receipt_inclusion("ethereum", log["transactionHash"])
    return {"log": {"transaction_hash": log["transactionHash"], "log_index": h2i(log["logIndex"]), "block_hash": log["blockHash"], "topics": log["topics"], "data": log["data"]}, "receipt_inclusion": inc}


def capture_polygon() -> dict[str, Any]:
    targets = collect_witnesses("polygon")
    unique = {int(w["block_number"]): w for w in targets}
    current_raw = eth_call("ethereum", ROOT_CHAIN, selector("currentHeaderBlock()"))
    current_id = int.from_bytes(h2b(current_raw), "big")
    cache: dict[int, dict[str, Any]] = {}
    groups: dict[int, dict[str, Any]] = {}
    for n, w in sorted(unique.items()):
        cp = find_polygon_checkpoint(n, current_id, cache)
        groups.setdefault(cp["header_block_id"], {"checkpoint": cp, "targets": []})["targets"].append(w)
    finalized = rpc("ethereum", "eth_getBlockByNumber", ["finalized", False])
    finalized_number = h2i(finalized["number"]) if finalized else None
    out_groups = []
    for hid, group in sorted(groups.items()):
        cp = group["checkpoint"]
        trace("polygon_checkpoint_start", header_block_id=hid, start=cp["start"], end=cp["end"], target_count=len(group["targets"]))
        blocks = fetch_polygon_range(cp["start"], cp["end"])
        leaves = [polygon_leaf(b) for b in blocks]
        layers = merkle_layers(leaves)
        computed_root = "0x" + layers[-1][0].hex()
        root_match = computed_root.lower() == cp["root"].lower()
        if not root_match:
            raise RuntimeError(f"Polygon checkpoint root mismatch header={hid} expected={cp['root']} computed={computed_root}")
        members = []
        for w in group["targets"]:
            idx = int(w["block_number"]) - cp["start"]
            leaf = leaves[idx]
            proof = merkle_proof(layers, idx)
            ok = verify_merkle(leaf, idx, layers[-1][0], proof)
            if not ok or ("0x" + leaf.hex()).lower() != ("0x" + polygon_leaf(blocks[idx]).hex()).lower():
                raise RuntimeError("Polygon checkpoint membership self-check failed")
            members.append({"asset_block_number": int(w["block_number"]), "asset_block_hash": w["block_hash"], "leaf": "0x" + leaf.hex(), "leaf_index": idx, "proof": ["0x" + p.hex() for p in proof], "membership_pass": True})
        event = checkpoint_event(cp)
        eth_bn = event["receipt_inclusion"]["ethereum_block"]["number"]
        final_observed = finalized_number is not None and eth_bn <= finalized_number
        if not final_observed:
            raise RuntimeError(f"checkpoint Ethereum block {eth_bn} is not <= finalized {finalized_number}")
        out_groups.append({"checkpoint": cp, "computed_root": computed_root, "root_match": True, "members": members, "ethereum_submission": event, "ethereum_finalized_block_number_observed": finalized_number, "checkpoint_block_finalized_observed": True})
        trace("polygon_checkpoint_pass", header_block_id=hid, ethereum_block=eth_bn, members=len(members))
    return {"status": "ethereum_checkpoint_membership_verified", "root_chain": ROOT_CHAIN, "target_records": len(targets), "unique_target_blocks": len(unique), "checkpoint_groups": len(out_groups), "groups": out_groups, "pass": True}


def base_l1_origin(block_number: int) -> dict[str, Any]:
    tag = hex(block_number)
    row: dict[str, Any] = {"base_block_number": block_number, "number_call": None, "hash_call": None, "verified": False, "output_at_block": None}
    try:
        nraw = eth_call("base", BASE_L1_BLOCK, selector("number()"), tag)
        hraw = eth_call("base", BASE_L1_BLOCK, selector("hash()"), tag)
        l1n = int.from_bytes(h2b(nraw), "big")
        l1h = "0x" + h2b(hraw)[-32:].hex()
        row["number_call"], row["hash_call"] = l1n, l1h
        l1 = rpc("ethereum", "eth_getBlockByNumber", [hex(l1n), False])
        if l1:
            mat = block_header_proof_material(l1)
            row["ethereum_l1_block"] = mat
            row["verified"] = mat["hash"].lower() == l1h.lower()
    except Exception as exc:
        row["origin_error"] = str(exc)
        trace("base_l1_origin_error", block_number=block_number, error=str(exc)[:500])
    try:
        row["output_at_block"] = rpc("base", "optimism_outputAtBlock", [tag], retries=0)
    except Exception as exc:
        row["output_at_block_error"] = str(exc)
    return row


def capture_base() -> dict[str, Any]:
    targets = collect_witnesses("base")
    unique_numbers = sorted({int(w["block_number"]) for w in targets})
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(CONCURRENCY, 8)) as ex:
        origins = list(ex.map(base_l1_origin, unique_numbers))
    verified = sum(1 for r in origins if r.get("verified"))
    outputs = sum(1 for r in origins if r.get("output_at_block"))
    finalized = rpc("ethereum", "eth_getBlockByNumber", ["finalized", False])
    contract_state = {}
    for name, address in BASE_CONTRACTS.items():
        code = rpc("ethereum", "eth_getCode", [address, "finalized"])
        contract_state[name] = {"address": address, "code_sha256": hashlib.sha256(h2b(code)).hexdigest(), "code_bytes": len(h2b(code)), "present": bool(code and code != "0x")}
    status = "l1_origin_binding_observed" if verified == len(unique_numbers) and unique_numbers else ("partial_l1_origin_binding" if verified else "l1_origin_unavailable")
    return {
        "status": status, "claim_boundary": "This Base section proves only captured L1-origin observations and locally verifies the referenced Ethereum block headers. It is not labeled a full OP settlement/finality proof unless an exact output-root path is also present.",
        "target_records": len(targets), "unique_target_blocks": len(unique_numbers), "l1_origins_verified": verified, "output_roots_observed": outputs,
        "ethereum_finalized_block": block_header_proof_material(finalized) if finalized else None, "base_l1_contracts_at_finalized": contract_state, "origins": origins,
        "full_settlement_pass": False,
    }


def main() -> None:
    SETTLE.mkdir(parents=True, exist_ok=True)
    TRACE.write_text("", encoding="utf-8")
    trace("capture_start", rpc_endpoint_counts={k: len(v) for k, v in RPC.items()})
    polygon = capture_polygon()
    jwrite(SETTLE / "POLYGON-ETHEREUM-SETTLEMENT.json", polygon)
    base = capture_base()
    jwrite(SETTLE / "BASE-ETHEREUM-SETTLEMENT.json", base)
    summary = {
        "schema": "trinity-accord/chronicle-sidechain-settlement-summary/v1", "generated_at": now(),
        "polygon": {k: polygon[k] for k in ("status", "target_records", "unique_target_blocks", "checkpoint_groups", "pass")},
        "base": {k: base[k] for k in ("status", "target_records", "unique_target_blocks", "l1_origins_verified", "output_roots_observed", "full_settlement_pass")},
        "overall_status": "polygon_full_base_partial" if polygon["pass"] and not base["full_settlement_pass"] else "complete",
        "boundary": "Polygon checkpoint membership is fully verified through Ethereum execution inclusion. Base is separately statused and is not promoted beyond evidence actually captured.",
    }
    jwrite(SETTLE / "SETTLEMENT-SUMMARY.json", summary)
    trace("capture_complete", overall_status=summary["overall_status"], polygon_groups=polygon["checkpoint_groups"], base_origins_verified=base["l1_origins_verified"])
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
