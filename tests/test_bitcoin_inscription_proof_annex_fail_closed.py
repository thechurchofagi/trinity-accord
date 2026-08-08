from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANNEX = ROOT / "evidence/bitcoin-inscription-proof-annex-v1"
VERIFIER = ANNEX / "verification/verify_annex.py"


def load_case():
    spec = importlib.util.spec_from_file_location("bitcoin_inscription_annex_mutation_verifier", VERIFIER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(VERIFIER.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    manifest = json.loads((ANNEX / "ANNEX-MANIFEST.json").read_text(encoding="utf-8"))
    anchor = copy.deepcopy(manifest["anchors"][0])
    proof = json.loads((ROOT / anchor["proof_material"]["path"]).read_text(encoding="utf-8"))
    return module, anchor, proof


def flip_hex(value: str, byte_offset: int = -1) -> str:
    raw = bytearray.fromhex(value)
    raw[byte_offset] ^= 1
    return raw.hex()


def flip_hash(value: str) -> str:
    raw = bytearray.fromhex(value)
    raw[-1] ^= 1
    return raw.hex()


def test_rejects_reveal_witness_body_mutation_even_though_txid_excludes_witness():
    module, anchor, proof = load_case()
    mutated = copy.deepcopy(proof)
    mutated["reveal"]["transaction_hex"] = flip_hex(mutated["reveal"]["transaction_hex"], -80)
    with pytest.raises(ValueError):
        module.verify_l1(anchor, mutated)


def test_rejects_tapscript_schnorr_signature_mutation():
    module, anchor, proof = load_case()
    mutated = copy.deepcopy(proof)
    # The first witness item begins after the SegWit transaction prefix. Find
    # the exact 64-byte signature and mutate it without touching the txid.
    reveal = module.parse_transaction_hex(mutated["reveal"]["transaction_hex"])
    signature = reveal["inputs"][0]["witness"][0]
    raw = bytearray.fromhex(mutated["reveal"]["transaction_hex"])
    offset = bytes(raw).find(signature)
    assert offset >= 0
    raw[offset] ^= 1
    mutated["reveal"]["transaction_hex"] = raw.hex()
    mutated_reveal = module.parse_transaction_hex(mutated["reveal"]["transaction_hex"])
    anchor["wtxid"] = mutated_reveal["wtxid"]
    mutated["reveal"]["wtxid"] = mutated_reveal["wtxid"]
    with pytest.raises(ValueError, match="Schnorr signature"):
        module.verify_l1(anchor, mutated)


def test_rejects_taproot_control_or_prevout_binding_mutation():
    module, anchor, proof = load_case()
    mutated = copy.deepcopy(proof)
    mutated["reveal"]["prevout_transaction_hex"] = flip_hex(
        mutated["reveal"]["prevout_transaction_hex"], 0
    )
    with pytest.raises(ValueError):
        module.verify_l1(anchor, mutated)


def test_rejects_target_txid_merkle_branch_mutation():
    module, anchor, proof = load_case()
    l1 = module.verify_l1(anchor, proof)
    mutated = copy.deepcopy(proof)
    branch = mutated["block_inclusion"]["target_txid_merkle_branch"]
    branch[0] = flip_hash(branch[0])
    with pytest.raises(ValueError, match="Merkle"):
        module.verify_l2(anchor, mutated, l1)


def test_rejects_wtxid_merkle_branch_mutation():
    module, anchor, proof = load_case()
    l1 = module.verify_l1(anchor, proof)
    mutated = copy.deepcopy(proof)
    branch = mutated["witness_inclusion"]["target_wtxid_merkle_branch"]
    branch[0] = flip_hash(branch[0])
    with pytest.raises(ValueError, match="Merkle"):
        module.verify_l2(anchor, mutated, l1)


def test_rejects_coinbase_witness_commitment_metadata_mutation():
    module, anchor, proof = load_case()
    l1 = module.verify_l1(anchor, proof)
    mutated = copy.deepcopy(proof)
    mutated["witness_inclusion"]["coinbase_commitment"] = flip_hash(
        mutated["witness_inclusion"]["coinbase_commitment"]
    )
    with pytest.raises(ValueError, match="witness commitment"):
        module.verify_l2(anchor, mutated, l1)


def test_rejects_block_header_mutation():
    module, anchor, proof = load_case()
    l1 = module.verify_l1(anchor, proof)
    mutated = copy.deepcopy(proof)
    mutated["block_inclusion"]["header_hex"] = flip_hex(mutated["block_inclusion"]["header_hex"])
    with pytest.raises(ValueError):
        module.verify_l2(anchor, mutated, l1)


def test_rejects_pow_ancestry_link_mutation():
    module, anchor, proof = load_case()
    l1 = module.verify_l1(anchor, proof)
    l2 = module.verify_l2(anchor, proof, l1)
    mutated = copy.deepcopy(proof)
    mutated["pow_ancestry"]["headers_target_through_checkpoint"][1] = flip_hex(
        mutated["pow_ancestry"]["headers_target_through_checkpoint"][1]
    )
    with pytest.raises(ValueError):
        module.verify_l3(anchor, mutated, l2)


def test_rejects_erased_checkpoint_provenance_boundary():
    module, anchor, proof = load_case()
    l1 = module.verify_l1(anchor, proof)
    l2 = module.verify_l2(anchor, proof, l1)
    mutated = copy.deepcopy(proof)
    mutated["pow_ancestry"]["trust_model"] = "trust-free finality"
    with pytest.raises(ValueError, match="trust boundary"):
        module.verify_l3(anchor, mutated, l2)


def test_rejects_single_provider_checkpoint_quorum():
    module, anchor, proof = load_case()
    l1 = module.verify_l1(anchor, proof)
    l2 = module.verify_l2(anchor, proof, l1)
    mutated = copy.deepcopy(proof)
    mutated["pow_ancestry"]["matching_provider_votes"] = 1
    mutated["pow_ancestry"]["checkpoint_observations"] = mutated["pow_ancestry"][
        "checkpoint_observations"
    ][:1]
    with pytest.raises(ValueError, match="quorum"):
        module.verify_l3(anchor, mutated, l2)
