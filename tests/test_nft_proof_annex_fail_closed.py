from __future__ import annotations

import copy
import importlib.util
import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
VERIFY_SCRIPT = ROOT / "evidence" / "nft-proof-annex-v1" / "verification" / "verify_nft_proof_annex.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("nft_proof_fail_closed_test", VERIFY_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def first_real_l2_case():
    mod = load_verifier()
    summary = json.loads(mod.SUMMARY.read_text(encoding="utf-8"))
    assets = mod.index_by_tx()
    record = copy.deepcopy(summary["l2_witnesses"][0])
    asset = copy.deepcopy(assets[record["tx_hash"].lower()])
    primitives = mod.load_frozen_primitives()
    return mod, record, asset, primitives


def test_frozen_ethereum_primitives_manifest_matches_module():
    mod = load_verifier()
    manifest = json.loads(mod.PRIMITIVES_MANIFEST.read_text(encoding="utf-8"))
    assert manifest["schema"] == "trinityaccord.ethereum-proof-primitives-manifest.v1"
    assert manifest["module_path"] == mod.PRIMITIVES_SCRIPT.relative_to(ROOT).as_posix()
    assert manifest["sha256"] == mod.sha256_file(mod.PRIMITIVES_SCRIPT)
    primitives = mod.load_frozen_primitives()
    assert primitives.GENESIS_TIME == 1606824023
    assert primitives.SECONDS_PER_SLOT == 12


def test_real_compact_l2_witness_still_passes_after_hardening():
    mod, record, asset, primitives = first_real_l2_case()
    result = mod.verify_l2(record, asset, primitives)
    assert result["status"] == "PASS"
    assert result["tx_hash"] == asset["mint"]["transaction_hash"].lower()


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("block_number", "block number mismatch"),
        ("receipt_status", "receipt status mismatch"),
        ("chain_id", "chain ID mismatch"),
        ("standard", "token standard/event mismatch"),
        ("global_log_index", "global logIndex binding mismatch"),
        ("summary_transaction_index", "capture-summary transaction index mismatch"),
    ],
)
def test_real_compact_l2_witness_rejects_cross_field_mutation(mutation: str, message: str):
    mod, record, asset, primitives = first_real_l2_case()

    if mutation == "block_number":
        asset["mint"]["block_number"] = str(int(asset["mint"]["block_number"]) + 1)
    elif mutation == "receipt_status":
        asset["mint"]["receipt_status"] = "0"
    elif mutation == "chain_id":
        asset["chain"]["chain_id"] = str(int(asset["chain"]["chain_id"]) + 1)
    elif mutation == "standard":
        asset["standard"] = "erc1155" if asset["standard"].lower() == "erc721" else "erc721"
    elif mutation == "global_log_index":
        asset["mint"]["log_index"] = str(int(asset["mint"]["log_index"]) + 1)
    elif mutation == "summary_transaction_index":
        record["transaction_index"] = int(record["transaction_index"]) + 1
    else:
        raise AssertionError(f"unknown mutation: {mutation}")

    with pytest.raises(ValueError, match=message):
        mod.verify_l2(record, asset, primitives)
