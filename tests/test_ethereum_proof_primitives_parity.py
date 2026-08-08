from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ETH_VERIFY = ROOT / "evidence/ethereum-evidence-annex-v1/verification/verify_annex.py"
PRIMITIVES = ROOT / "evidence/ethereum-proof-primitives-v1/ethereum_proof_primitives_v1.py"
PRIMITIVES_MANIFEST = ROOT / "evidence/ethereum-proof-primitives-v1/PRIMITIVES-MANIFEST.json"
ETH_MANIFEST = ROOT / "evidence/ethereum-evidence-annex-v1/ANNEX-MANIFEST.json"
EXPECTED_V1_SHA256 = "d605cc3d7aad3b846d998f4192aae9cceb8ce3c1f0efa4e4578a22a2b5d47dc2"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_v1_primitives_are_explicitly_frozen_by_contract():
    manifest = json.loads(PRIMITIVES_MANIFEST.read_text(encoding="utf-8"))
    assert manifest["schema"] == "trinityaccord.ethereum-proof-primitives-manifest.v1"
    assert manifest["version"] == "1.0.0"
    assert manifest["change_policy"] == "immutable_v1_publish_new_version_instead"
    assert manifest["sha256"] == EXPECTED_V1_SHA256
    assert sha256(PRIMITIVES) == EXPECTED_V1_SHA256


def test_non_nft_ethereum_verifier_matches_frozen_v1_primitives_on_all_real_witnesses():
    eth = load("trinity_eth_verify_parity", ETH_VERIFY)
    frozen = load("trinity_eth_frozen_v1_parity", PRIMITIVES)
    manifest = json.loads(ETH_MANIFEST.read_text(encoding="utf-8"))

    assert eth.GENESIS_TIME == frozen.GENESIS_TIME
    assert eth.SECONDS_PER_SLOT == frozen.SECONDS_PER_SLOT

    for anchor in manifest["anchors"]:
        txh = anchor["tx_hash"].lower()
        proof_dir = ROOT / "evidence/ethereum-evidence-annex-v1/proof-material" / txh
        l2 = json.loads((proof_dir / "L2-execution-witness.json").read_text(encoding="utf-8"))
        block = l2["block"]

        assert eth.execution_header_hash(block) == frozen.execution_header_hash(block)
        raw_txs = [eth.h2b(value) for value in l2["raw_transactions"]]
        receipts = [eth.h2b(value) for value in l2["encoded_receipts"]]
        assert eth.build_root(raw_txs) == frozen.build_root(raw_txs)
        assert eth.build_root(receipts) == frozen.build_root(receipts)

        l3 = json.loads((proof_dir / "L3-consensus-witness.json").read_text(encoding="utf-8"))
        target = l3["target_beacon_header"]
        assert eth.beacon_header_root(target["message"]) == frozen.beacon_header_root(target["message"])

        branch = l3["execution_block_hash_to_body_root"]
        body_root = target["message"]["body_root"]
        eth.verify_single_ssz_proof(branch, body_root)
        frozen.verify_single_ssz_proof(branch, body_root)

        for item in l3["checkpoint_to_target_parent_chain"]:
            assert eth.beacon_header_root(item["message"]) == frozen.beacon_header_root(item["message"])
