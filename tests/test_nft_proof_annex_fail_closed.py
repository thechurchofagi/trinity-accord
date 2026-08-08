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


def real_l2_cases():
    mod = load_verifier()
    summary = json.loads(mod.SUMMARY.read_text(encoding="utf-8"))
    assets = mod.index_by_tx()
    primitives = mod.load_frozen_primitives()
    cases = []
    for original_record in summary["l2_witnesses"]:
        record = copy.deepcopy(original_record)
        asset = copy.deepcopy(assets[record["tx_hash"].lower()])
        cases.append((mod, record, asset, primitives))
    return cases


def first_real_l2_case():
    return real_l2_cases()[0]


def first_case_for_event(event: str):
    for case in real_l2_cases():
        if case[2]["mint"]["event"] == event:
            return case
    raise AssertionError(f"no real NFT proof case for event {event}")


def first_erc1155_case():
    for case in real_l2_cases():
        if case[2]["mint"]["event"] in {"TransferSingle", "TransferBatch"}:
            return case
    raise AssertionError("no real ERC-1155 NFT proof case")


def different_address(value: str) -> str:
    assert value.startswith("0x") and len(value) == 42
    raw = bytearray.fromhex(value[2:])
    raw[-1] ^= 1
    return "0x" + raw.hex()


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


def test_all_real_compact_l2_witnesses_pass_event_specific_semantics():
    cases = real_l2_cases()
    assert len(cases) == 175
    for mod, record, asset, primitives in cases:
        assert mod.verify_l2(record, asset, primitives)["status"] == "PASS"


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


def test_erc721_rejects_operator_and_batch_index_metadata():
    mod, record, asset, primitives = first_case_for_event("Transfer")
    assert asset["standard"].lower() == "erc721"

    bad_operator = copy.deepcopy(asset)
    bad_operator["mint"]["operator"] = "0x0000000000000000000000000000000000000001"
    with pytest.raises(ValueError, match="ERC-721 mint operator must be null"):
        mod.verify_l2(record, bad_operator, primitives)

    bad_batch = copy.deepcopy(asset)
    bad_batch["mint"]["batch_index"] = 0
    with pytest.raises(ValueError, match="ERC-721 mint batch_index must be null"):
        mod.verify_l2(record, bad_batch, primitives)


def test_erc1155_rejects_missing_or_mismatched_operator():
    mod, record, asset, primitives = first_erc1155_case()
    operator = asset["mint"].get("operator")
    assert isinstance(operator, str) and len(operator) == 42

    missing = copy.deepcopy(asset)
    missing["mint"]["operator"] = None
    with pytest.raises(ValueError, match="operator must be a 20-byte 0x address"):
        mod.verify_l2(record, missing, primitives)

    malformed = copy.deepcopy(asset)
    malformed["mint"]["operator"] = "0x1234"
    with pytest.raises(ValueError, match="operator must be a 20-byte 0x address"):
        mod.verify_l2(record, malformed, primitives)

    mismatched = copy.deepcopy(asset)
    mismatched["mint"]["operator"] = different_address(operator)
    with pytest.raises(ValueError, match="operator mismatch"):
        mod.verify_l2(record, mismatched, primitives)


def test_erc1155_event_specific_batch_index_is_fail_closed():
    mod, record, asset, primitives = first_erc1155_case()
    event = asset["mint"]["event"]
    mutated = copy.deepcopy(asset)

    if event == "TransferSingle":
        assert asset["mint"].get("batch_index") is None
        mutated["mint"]["batch_index"] = 0
        with pytest.raises(ValueError, match="TransferSingle batch_index must be null"):
            mod.verify_l2(record, mutated, primitives)
    else:
        assert event == "TransferBatch"
        assert asset["mint"].get("batch_index") is not None
        mutated["mint"]["batch_index"] = None
        with pytest.raises(ValueError, match="TransferBatch batch_index is required"):
            mod.verify_l2(record, mutated, primitives)
