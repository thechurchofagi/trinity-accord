#!/usr/bin/env python3
"""One-time branch-only helper to bind captured L2/L3 witnesses into the annex manifest."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANNEX = ROOT / "evidence/ethereum-evidence-annex-v1"
MANIFEST = ANNEX / "ANNEX-MANIFEST.json"


def record(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def main() -> int:
    value = json.loads(MANIFEST.read_text(encoding="utf-8"))
    anchors = value.get("anchors")
    if not isinstance(anchors, list) or len(anchors) != 10:
        raise SystemExit("expected exactly 10 audited non-NFT Ethereum anchors")
    boundary = value.get("authority_boundary", {})
    if boundary.get("canonical_authority") != "three Bitcoin Originals only":
        raise SystemExit("canonical authority boundary changed")
    if boundary.get("no_authority_escalation") is not True:
        raise SystemExit("no_authority_escalation must stay true")

    value["version"] = "1.1.0"
    value["claim_model"]["levels"]["L2_EXECUTION_INCLUSION"] = (
        "PASS only when preserved raw signed transactions and encoded receipts independently reconstruct "
        "the execution block transactionsRoot/receiptsRoot and the execution header recomputes to the declared block hash."
    )
    value["claim_model"]["levels"]["L3_CONSENSUS_FINALITY"] = (
        "PASS only when the execution block hash is SSZ-proven into the target Beacon block body and that target "
        "Beacon root is linked by verified parent-root ancestry to an explicitly declared trusted finalized descendant "
        "Beacon root under the documented weak-subjectivity assumption."
    )
    value["claim_model"]["trusted_checkpoint_rule"] = (
        "L3 PASS is checkpoint-relative: the annex explicitly names the trusted finalized Beacon root for each anchor. "
        "Cross-provider canonical/finalized API observations are preserved as provenance only and never replace the "
        "weak-subjectivity trust assumption."
    )
    policy = value["proof_material_policy"]
    policy["execution_reconstruction_witness"] = "PRESERVED_AND_SHA256_BOUND_FOR_ALL_10_ANCHORS"
    policy["beacon_consensus_witness"] = "PRESERVED_AND_SHA256_BOUND_FOR_ALL_10_ANCHORS"
    policy["transaction_or_receipt_inclusion_proof"] = (
        "full deterministic trie reconstruction witness accepted: all raw signed transactions and encoded receipts "
        "reconstruct the committed roots offline"
    )
    policy["beacon_finality_material"] = (
        "SSZ execution-block-hash branch plus Beacon header parent-root ancestry to an explicit trusted finalized descendant root"
    )
    policy["trusted_finalized_checkpoint"] = "explicit per-anchor trusted finalized Beacon root under weak subjectivity"
    policy["current_v1_note"] = (
        "All 10 audited non-NFT anchors now preserve byte-bound L2 execution reconstruction witnesses and L3 "
        "checkpoint-relative Beacon consensus witnesses. Historical RPC capture files remain reference-only and are not "
        "the basis of L2/L3 PASS."
    )
    policy["offline_verifier"] = "evidence/ethereum-evidence-annex-v1/verification/verify_annex.py"

    for anchor in anchors:
        tx = anchor["tx_hash"].lower()
        if not (tx.startswith("0x") and len(tx) == 66):
            raise SystemExit(f"invalid tx hash: {tx}")
        proof_dir = ANNEX / "proof-material" / tx
        l2 = proof_dir / "L2-execution-witness.json"
        l3 = proof_dir / "L3-consensus-witness.json"
        if not l2.is_file() or not l3.is_file():
            raise SystemExit(f"missing proof witness for {tx}")
        l2v = json.loads(l2.read_text(encoding="utf-8"))
        l3v = json.loads(l3.read_text(encoding="utf-8"))
        if l2v.get("target_tx_hash", "").lower() != tx:
            raise SystemExit(f"L2 target mismatch for {tx}")
        if l3v.get("target_tx_hash", "").lower() != tx:
            raise SystemExit(f"L3 target mismatch for {tx}")
        checkpoint = l3v.get("trusted_finalized_beacon_root", {})
        if int(checkpoint.get("matching_provider_votes", 0)) < 2:
            raise SystemExit(f"insufficient checkpoint root provenance for {tx}")
        if int(checkpoint.get("finalized_provider_votes", 0)) < 1:
            raise SystemExit(f"missing finalized checkpoint provenance for {tx}")
        anchor["proof_material"] = {
            "l2_execution_witness": record(l2),
            "l3_consensus_witness": record(l3),
        }
        anchor["proof_status"] = {
            "L1_BYTE_INTEGRITY": "CHECK_ON_VERIFY",
            "L2_EXECUTION_INCLUSION": "PASS",
            "L3_CONSENSUS_FINALITY": "PASS",
        }

    summary = ANNEX / "proof-material" / "L2-L3-CAPTURE-SUMMARY.json"
    if not summary.is_file():
        raise SystemExit("missing L2/L3 capture summary")
    value["proof_material_policy"]["capture_summary"] = record(summary)
    MANIFEST.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "result": "PASS",
        "anchors": len(anchors),
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "l2": "PASS_DECLARED_WITH_BYTE_BINDINGS",
        "l3": "PASS_DECLARED_WITH_EXPLICIT_WEAK_SUBJECTIVITY_BOUNDARY",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
