from __future__ import annotations

import copy
import importlib.util
import json
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
VERIFY_SCRIPT = ROOT / "evidence" / "nft-proof-annex-v1" / "verification" / "verify_nft_proof_annex.py"
COMMITMENT_SCRIPT = ROOT / "scripts" / "build_nft_cryptographic_commitment.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("nft_proof_fail_closed_test", VERIFY_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_commitment_builder():
    spec = importlib.util.spec_from_file_location("nft_commitment_fail_closed_test", COMMITMENT_SCRIPT)
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

    missing_operator = copy.deepcopy(asset)
    del missing_operator["mint"]["operator"]
    with pytest.raises(ValueError, match="operator must be explicitly present"):
        mod.verify_l2(record, missing_operator, primitives)

    missing_batch = copy.deepcopy(asset)
    del missing_batch["mint"]["batch_index"]
    with pytest.raises(ValueError, match="batch_index must be explicitly present"):
        mod.verify_l2(record, missing_batch, primitives)


def test_commitment_builder_rejects_omitted_event_semantic_keys():
    _, _, asset, _ = first_case_for_event("Transfer")
    builder = load_commitment_builder()
    for field in ("operator", "batch_index"):
        mutated = copy.deepcopy(asset)
        del mutated["mint"][field]
        with pytest.raises(ValueError, match=rf"mint\.{field} must be explicitly present"):
            builder.project_asset(mutated)


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


def test_synthetic_transfer_batch_path_is_fully_exercised():
    mod = load_verifier()
    contract = "0x" + "11" * 20
    recipient = "0x" + "22" * 20
    operator = "0x" + "33" * 20
    topic_address = lambda value: b"\x00" * 12 + bytes.fromhex(value[2:])
    word = lambda value: int(value).to_bytes(32, "big")
    event_topic = mod.keccak(b"TransferBatch(address,address,address,uint256[],uint256[])")
    # ABI: heads point to ids at 0x40 and values at 0xa0.
    data = b"".join(
        [word(64), word(160), word(2), word(9), word(10), word(2), word(4), word(5)]
    )
    receipt = mod.rlp.encode(
        [
            b"\x01",
            b"",
            b"",
            [[bytes.fromhex(contract[2:]), [event_topic, topic_address(operator), topic_address("0x" + "00" * 20), topic_address(recipient)], data]],
        ]
    )
    asset = {
        "contract_address": contract,
        "token_id": "10",
        "mint": {
            "event": "TransferBatch",
            "quantity": "5",
            "to": recipient,
            "operator": operator,
            "batch_index": 1,
        },
    }
    result = mod.verify_mint_log(asset, receipt, 0)
    assert result["event"] == "erc1155.TransferBatch"
    assert result["token_id"] == "10"

    missing_index = copy.deepcopy(asset)
    del missing_index["mint"]["batch_index"]
    with pytest.raises(ValueError, match="batch_index must be explicitly present"):
        mod.verify_mint_log(missing_index, receipt, 0)

    bad_index = copy.deepcopy(asset)
    bad_index["mint"]["batch_index"] = 0
    with pytest.raises(ValueError, match="TransferBatch item mismatch"):
        mod.verify_mint_log(bad_index, receipt, 0)
