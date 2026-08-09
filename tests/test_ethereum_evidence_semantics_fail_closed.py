from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
ANNEX = ROOT / "evidence/ethereum-evidence-annex-v1"
VERIFIER = ANNEX / "verification/verify_annex.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("ethereum_semantic_verifier", VERIFIER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def case():
    module = load_verifier()
    manifest = json.loads((ANNEX / "ANNEX-MANIFEST.json").read_text(encoding="utf-8"))
    by_id = {anchor["id"]: anchor for anchor in manifest["anchors"]}
    return module, by_id


@pytest.mark.parametrize(
    ("field", "value", "message"),
    (
        ("chain_id", 5, "chainId mismatch"),
        ("expected_from", "0x" + "11" * 20, "sender mismatch"),
        ("expected_to", "0x" + "22" * 20, "destination mismatch"),
        ("expected_value_wei", "1", "value mismatch"),
        ("input_len", 31, "input length mismatch"),
        ("input_sha256", "00" * 32, "input SHA-256 mismatch"),
    ),
)
def test_signed_transaction_semantics_fail_closed(case, field, value, message):
    module, anchors = case
    anchor = copy.deepcopy(anchors["eth-authority-manifest-sha256-notarization"])
    anchor[field] = value
    with pytest.raises(ValueError, match=message):
        module.verify_l2(anchor)


def test_receipt_success_is_required(case):
    module, anchors = case
    anchor = copy.deepcopy(anchors["eth-authority-manifest-sha256-notarization"])
    anchor["execution_reference"]["receipt_status"] = "0x0"
    with pytest.raises(ValueError, match="successful execution"):
        module.verify_l2(anchor)


def test_authority_digest_calldata_relation_is_exact(case):
    module, anchors = case
    anchor = anchors["eth-authority-manifest-sha256-notarization"]
    authority = (ROOT / anchor["payloads"][0]["path"]).read_bytes()
    digest = __import__("hashlib").sha256(authority).digest()
    assert module.verify_payload_binding(anchor, digest) == "sha256_of_declared_payload"
    with pytest.raises(ValueError, match="SHA-256"):
        module.verify_payload_binding(anchor, bytes([digest[0] ^ 1]) + digest[1:])


def test_eip712_signature_and_signer_are_cryptographically_checked(case):
    module, _anchors = case
    authority = (ROOT / "archive/authority-manifest/authority.jcs.json").read_bytes()
    signature = json.loads(
        (ROOT / "archive/authority-manifest/signature.json").read_text(encoding="utf-8")
    )
    result = module.verify_eip712_authority_signature(
        authority, signature, "0xbc63566a41cbfdb9c266a5941cbe47894daa54a8"
    )
    assert result["recovered_signer"] == "0xbc63566a41cbfdb9c266a5941cbe47894daa54a8"

    mutated = copy.deepcopy(signature)
    raw = bytearray.fromhex(mutated["signature"][2:])
    raw[10] ^= 1
    mutated["signature"] = "0x" + raw.hex()
    with pytest.raises(ValueError):
        module.verify_eip712_authority_signature(
            authority, mutated, "0xbc63566a41cbfdb9c266a5941cbe47894daa54a8"
        )


def test_all_twelve_real_witnesses_close_transaction_receipt_and_payload_semantics(case):
    module, anchors = case
    assert len(anchors) == 12
    checks = [module.verify_l2(anchor)[0] for anchor in anchors.values()]
    assert all(item["chain_id"] == 1 for item in checks)
    assert all(item["receipt_status"] == 1 for item in checks)
    assert all(item["sender"] == "0xbc63566a41cbfdb9c266a5941cbe47894daa54a8" for item in checks)
    assert {
        item["payload_binding"] for item in checks
    } >= {
        "exact_payload_bytes",
        "sha256_of_declared_payload",
        "verified_eip712_authority_and_cross-system_record",
        "btc_signature_object_and_arweave_pointer_record",
    }
