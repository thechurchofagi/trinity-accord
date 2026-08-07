from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANNEX = ROOT / "evidence/ethereum-evidence-annex-v1"
MANIFEST = ANNEX / "ANNEX-MANIFEST.json"


def load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_all_audited_ethereum_anchors_carry_frozen_history_and_offline_proofs_without_overclaim():
    manifest = load(MANIFEST)
    anchors = manifest["anchors"]
    assert isinstance(anchors, list)
    assert len(anchors) == 10
    assert manifest["proof_material_policy"]["rpc_history_capture"] == (
        "PRESERVED_FOR_ALL_10_ANCHORS_REFERENCE_ONLY"
    )

    for anchor in anchors:
        assert anchor["rpc_capture_status"] == "REFERENCE_CAPTURED"
        proof_status = anchor["proof_status"]
        assert proof_status["L2_EXECUTION_INCLUSION"] == "PASS"
        assert proof_status["L3_CONSENSUS_FINALITY"] == "PASS"

        tx_hash = anchor["tx_hash"]
        evidence_dir = ANNEX / "proof-material" / tx_hash
        tx = load(evidence_dir / "transaction.json")
        receipt = load(evidence_dir / "receipt.json")
        block = load(evidence_dir / "block.json")
        capture = load(evidence_dir / "capture-manifest.json")
        l2 = load(evidence_dir / "L2-execution-witness.json")
        l3 = load(evidence_dir / "L3-consensus-witness.json")

        assert tx["hash"].lower() == tx_hash.lower()
        assert receipt["transactionHash"].lower() == tx_hash.lower()
        assert capture["tx_hash"].lower() == tx_hash.lower()
        assert capture["chain_id"] == "0x1"
        # Historical RPC capture remains reference-only. It is deliberately not
        # retroactively relabelled as the source of L2/L3 PASS.
        assert capture["verification_status"] == {
            "consensus_finality": "UNVERIFIED",
            "execution_inclusion": "UNVERIFIED",
            "rpc_capture": "PASS",
        }

        block_hash = tx["blockHash"]
        assert block_hash == receipt["blockHash"] == block["hash"] == capture["block_hash"]
        assert tx["blockNumber"] == receipt["blockNumber"] == block["number"] == capture["block_number"]
        assert block["timestamp"] == capture["block_timestamp"]

        raw_input = bytes.fromhex(tx["input"][2:])
        assert len(raw_input) == anchor["input_len"]
        assert hashlib.sha256(raw_input).hexdigest() == anchor["input_sha256"]

        reference = anchor["execution_reference"]
        assert reference["block_hash"] == block_hash
        assert reference["block_number"] == int(block["number"], 16)
        assert reference["block_timestamp_unix"] == int(block["timestamp"], 16)
        assert reference["transaction_index"] == int(tx["transactionIndex"], 16)
        assert reference["receipt_status"] == receipt.get("status")
        assert reference["reference_checked"] is True
        assert reference["reference_kind"] == "preserved_rpc_capture"

        record_digests = {record["path"]: record["sha256"] for record in capture["records"]}
        for name in ("transaction.json", "receipt.json", "block.json"):
            payload = (evidence_dir / name).read_bytes()
            assert hashlib.sha256(payload).hexdigest() == record_digests[name]

        assert l2["schema"] == "trinityaccord.ethereum-execution-inclusion-witness.v1"
        assert l2["target_tx_hash"].lower() == tx_hash.lower()
        assert l2["block"]["hash"].lower() == block_hash.lower()
        assert l3["schema"] == "trinityaccord.ethereum-consensus-finality-witness.v1"
        assert l3["target_tx_hash"].lower() == tx_hash.lower()
        assert l3["execution_block_hash"].lower() == block_hash.lower()
        checkpoint = l3["trusted_finalized_beacon_root"]
        assert checkpoint["schema"] == "trinityaccord.ethereum-trusted-finalized-beacon-root.v1"
        assert checkpoint["matching_provider_votes"] >= 2
        assert checkpoint["finalized_provider_votes"] >= 1
        assert "weak-subjectivity" in checkpoint["trust_model"]
        assert "provenance only" in checkpoint["trust_model"]

        proof_material = anchor["proof_material"]
        for key, filename in (
            ("l2_execution_witness", "L2-execution-witness.json"),
            ("l3_consensus_witness", "L3-consensus-witness.json"),
        ):
            binding = proof_material[key]
            path = evidence_dir / filename
            data = path.read_bytes()
            assert binding["path"] == path.relative_to(ROOT).as_posix()
            assert binding["size"] == len(data)
            assert binding["sha256"] == hashlib.sha256(data).hexdigest()


def test_original_ethereum_time_is_not_relabelled_as_preservation_time():
    manifest = load(MANIFEST)
    for anchor in manifest["anchors"]:
        ref = anchor["execution_reference"]
        capture = load(ANNEX / "proof-material" / anchor["tx_hash"] / "capture-manifest.json")
        assert "block_timestamp_utc" in ref
        assert "block_timestamp_unix" in ref
        assert "captured_at" in capture
        assert ref["claim_boundary"].startswith("Provider-returned historical evidence")
        # The later capture time is preserved separately and must never be used as
        # a substitute for the Ethereum block timestamp.
        assert capture["captured_at"] != ref["block_timestamp_utc"]
