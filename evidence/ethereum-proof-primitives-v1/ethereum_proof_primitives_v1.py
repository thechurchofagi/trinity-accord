#!/usr/bin/env python3
"""Frozen Ethereum proof primitives for Trinity Accord proof annexes v1.

This module intentionally contains only deterministic, offline verification
primitives shared by the NFT proof annex. Its exact bytes are bound by
PRIMITIVES-MANIFEST.json. Do not modify in place; publish a new version instead.
"""
from __future__ import annotations

import hashlib

import rlp
from eth_hash.auto import keccak
from trie import HexaryTrie

GENESIS_TIME = 1606824023
SECONDS_PER_SLOT = 12


def h2b(value: str) -> bytes:
    if not isinstance(value, str) or not value.startswith("0x"):
        raise ValueError(f"not 0x-prefixed hex: {value!r}")
    raw = value[2:]
    if len(raw) % 2:
        raw = "0" + raw
    return bytes.fromhex(raw)


def q(value: str | None) -> int:
    return 0 if value is None else int(value, 16)


def execution_header_hash(block: dict) -> bytes:
    fields = [
        h2b(block["parentHash"]), h2b(block["sha3Uncles"]), h2b(block["miner"]),
        h2b(block["stateRoot"]), h2b(block["transactionsRoot"]), h2b(block["receiptsRoot"]),
        h2b(block["logsBloom"]), q(block["difficulty"]), q(block["number"]), q(block["gasLimit"]),
        q(block["gasUsed"]), q(block["timestamp"]), h2b(block["extraData"]), h2b(block["mixHash"]), h2b(block["nonce"]),
    ]
    for name, conv in [
        ("baseFeePerGas", q), ("withdrawalsRoot", h2b), ("blobGasUsed", q), ("excessBlobGas", q),
        ("parentBeaconBlockRoot", h2b), ("requestsHash", h2b),
    ]:
        if block.get(name) is not None:
            fields.append(conv(block[name]))
    return keccak(rlp.encode(fields))


def build_root(values: list[bytes]) -> bytes:
    trie = HexaryTrie(db={})
    for i, value in enumerate(values):
        trie[rlp.encode(i)] = value
    return trie.root_hash


def merkleize_chunks(chunks: list[bytes]) -> bytes:
    if not chunks:
        raise ValueError("SSZ merkleization requires at least one chunk")
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


def verify_single_ssz_proof(proof: dict, expected_root: str) -> None:
    node = h2b(proof["leaf"])
    if len(node) != 32:
        raise ValueError("SSZ leaf must be 32 bytes")
    gindex = int(proof["gindex"])
    if gindex <= 1:
        raise ValueError("invalid SSZ generalized index")
    for witness_hex in proof["witnesses"]:
        witness = h2b(witness_hex)
        if len(witness) != 32:
            raise ValueError("invalid SSZ witness length")
        node = hashlib.sha256((witness + node) if (gindex & 1) else (node + witness)).digest()
        gindex //= 2
    if gindex != 1:
        raise ValueError("SSZ proof depth does not terminate at root")
    if "0x" + node.hex() != expected_root.lower():
        raise ValueError("SSZ proof root mismatch")
