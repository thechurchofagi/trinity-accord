from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
COMMITMENT_SCRIPT = ROOT / "scripts" / "build_nft_cryptographic_commitment.py"
VERIFY_SCRIPT = ROOT / "evidence" / "nft-proof-annex-v1" / "verification" / "verify_nft_proof_annex.py"


def load(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_collection_commitment_covers_exact_nft_inventory():
    mod = load("nft_commitment_test", COMMITMENT_SCRIPT)
    manifest = mod.build(ROOT / "nft-identity-index.json")
    assert manifest["schema"] == "trinityaccord.nft-collection-commitment.v1"
    assert manifest["source"]["asset_count"] == 175
    assert manifest["merkle"]["leaf_count"] == 175
    assert len(manifest["leaves"]) == 175
    assert len({row["canonical_key"] for row in manifest["leaves"]}) == 175
    assert manifest["mint_evidence_inventory"]["unique_transactions"] == 175
    assert 1 <= manifest["mint_evidence_inventory"]["unique_execution_blocks"] <= 175
    assert len(manifest["merkle"]["root_sha256"]) == 64
    assert mod.render(manifest) == mod.render(mod.build(ROOT / "nft-identity-index.json"))


def test_rfc6962_domain_separation_and_odd_tree_shape():
    mod = load("nft_commitment_merkle_test", COMMITMENT_SCRIPT)
    records = [b"a", b"b", b"c"]
    leaves = [hashlib.sha256(b"\x00" + item).digest() for item in records]
    left = hashlib.sha256(b"\x01" + leaves[0] + leaves[1]).digest()
    expected = hashlib.sha256(b"\x01" + left + leaves[2]).digest()
    assert mod.merkle_root_from_leaf_hashes(leaves) == expected


def test_compact_mpt_proof_round_trip():
    trie = pytest.importorskip("trie")
    rlp = pytest.importorskip("rlp")
    HexaryTrie = trie.HexaryTrie
    t = HexaryTrie(db={})
    values = [b"alpha", b"beta", b"gamma", b"delta"]
    for i, value in enumerate(values):
        t[rlp.encode(i)] = value
    key = rlp.encode(2)
    proof = t.get_proof(key)
    encoded_nodes = ["0x" + rlp.encode(node).hex() for node in proof]
    decoded_nodes = tuple(rlp.decode(bytes.fromhex(node[2:])) for node in encoded_nodes)
    assert HexaryTrie.get_from_proof(t.root_hash, key, decoded_nodes) == values[2]


def test_offline_receipt_decoder_verifies_erc721_mint():
    rlp = pytest.importorskip("rlp")
    eth_hash = pytest.importorskip("eth_hash.auto")
    mod = load("nft_proof_verify_test", VERIFY_SCRIPT)
    contract = bytes.fromhex("11" * 20)
    recipient = bytes.fromhex("22" * 20)
    zero_topic = b"\x00" * 32
    recipient_topic = b"\x00" * 12 + recipient
    token_topic = (7).to_bytes(32, "big")
    topic0 = eth_hash.keccak(b"Transfer(address,address,uint256)")
    log = [contract, [topic0, zero_topic, recipient_topic, token_topic], b""]
    receipt = rlp.encode([1, 21000, b"\x00" * 256, [log]])
    asset = {
        "contract_address": "0x" + contract.hex(),
        "token_id": "7",
        "mint": {
            "event": "Transfer",
            "quantity": "1",
            "to": "0x" + recipient.hex(),
            "operator": None,
            "batch_index": None,
        },
    }
    result = mod.verify_mint_log(asset, receipt, 0)
    assert result["event"] == "erc721.Transfer"
    assert result["token_id"] == "7"
