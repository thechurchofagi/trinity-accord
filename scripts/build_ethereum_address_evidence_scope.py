#!/usr/bin/env python3
"""Build an observation-bounded Ethereum address evidence classification.

This is a discovery/scope audit, not an absence proof. The cryptographic claims for the
12 non-NFT evidence transactions and 175 NFT mints remain in their respective annexes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADDRESS = "0xbc63566a41cbfdb9c266a5941cbe47894daa54a8"
POST_FREEZE_TXS = {
    "0x06b1d82b7828054f249cdcc2e820321f634bd8bef44318751113098d2ee37acd",
    "0x04314e8f9b47fac54dcf2db3a65f40aad60c226e65614f0ad22588bd39c416d2",
}


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def source_digest(value: dict) -> str:
    material = dict(value)
    material.pop("source_digest", None)
    return hashlib.sha256(canonical(material)).hexdigest()[:16]


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def compact_tx(tx: dict, classification: str, reason: str) -> dict:
    raw_input = tx.get("input", "")
    if not isinstance(raw_input, str) or not raw_input.startswith("0x"):
        raise SystemExit(f"malformed transaction input: {tx.get('hash')}")
    return {
        "tx_hash": tx["hash"].lower(),
        "block_number": int(tx["blockNumber"]),
        "transaction_index": int(tx["transactionIndex"]),
        "nonce": int(tx["nonce"]) if tx["from"].lower() == ADDRESS else None,
        "from": tx["from"].lower(),
        "to": str(tx.get("to") or "").lower() or None,
        "value_wei": tx["value"],
        "input_len": (len(raw_input) - 2) // 2,
        "classification": classification,
        "reason": reason,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--transactions-json", required=True)
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--provider", default="https://eth.blockscout.com")
    parser.add_argument("--query-url", required=True)
    parser.add_argument(
        "--output", default="api/ethereum-address-evidence-scope.v1.json"
    )
    args = parser.parse_args()

    source_path = Path(args.transactions_json)
    source_bytes = source_path.read_bytes()
    source = json.loads(source_bytes)
    if source.get("status") != "1" or source.get("message") != "OK":
        raise SystemExit("address-history provider response is not successful")
    transactions = source.get("result")
    if not isinstance(transactions, list) or not transactions:
        raise SystemExit("address-history response has no transactions")
    hashes = [str(tx.get("hash", "")).lower() for tx in transactions]
    if len(hashes) != len(set(hashes)):
        raise SystemExit("address-history response contains duplicate transaction hashes")

    annex = load(ROOT / "evidence/ethereum-evidence-annex-v1/ANNEX-MANIFEST.json")
    anchor_by_hash = {
        anchor["tx_hash"].lower(): anchor for anchor in annex["anchors"]
    }
    nft_index = load(ROOT / "nft-identity-index.json")
    nft_hashes = {
        asset["mint"]["transaction_hash"].lower() for asset in nft_index["assets"]
    }
    if len(anchor_by_hash) != 12 or len(nft_hashes) != 175:
        raise SystemExit("current annex counts are not 12 Ethereum / 175 NFT")

    outgoing = [tx for tx in transactions if tx["from"].lower() == ADDRESS]
    incoming = [tx for tx in transactions if tx["from"].lower() != ADDRESS]
    nonces = sorted(int(tx["nonce"]) for tx in outgoing)
    if nonces != list(range(220)):
        raise SystemExit("observed outgoing nonce range is not exactly contiguous 0..219")

    self_data = {
        tx["hash"].lower()
        for tx in outgoing
        if str(tx.get("to") or "").lower() == ADDRESS
        and int(tx["value"]) == 0
        and tx.get("input") not in (None, "", "0x")
    }
    if self_data != set(anchor_by_hash):
        missing = sorted(self_data - set(anchor_by_hash))
        extra = sorted(set(anchor_by_hash) - self_data)
        raise SystemExit(
            f"annex/self-data set mismatch; missing={missing!r} extra={extra!r}"
        )
    outgoing_hashes = {tx["hash"].lower() for tx in outgoing}
    if not nft_hashes.issubset(outgoing_hashes):
        raise SystemExit("NFT transaction set is not a subset of observed outgoing history")
    other_hashes = outgoing_hashes - self_data - nft_hashes
    if len(other_hashes) != 33 or len(incoming) != 12:
        raise SystemExit("observed address-history classification counts drifted")

    tx_by_hash = {tx["hash"].lower(): tx for tx in transactions}
    evidence_records = []
    for tx_hash in sorted(self_data, key=lambda value: int(tx_by_hash[value]["nonce"])):
        record = compact_tx(
            tx_by_hash[tx_hash],
            "non_nft_evidence_self_transaction",
            "self-addressed, zero-value and non-empty calldata; cryptographic proof is in the Ethereum annex",
        )
        record["anchor_id"] = anchor_by_hash[tx_hash]["id"]
        record["freeze_membership"] = (
            "post_doi_v3_delta" if tx_hash in POST_FREEZE_TXS else "frozen_doi_v3"
        )
        evidence_records.append(record)
    other_records = [
        compact_tx(
            tx_by_hash[tx_hash],
            "other_outgoing_account_operation",
            "not in the self-addressed evidence set and not one of the 175 NFT mint transactions",
        )
        for tx_hash in sorted(other_hashes, key=lambda value: int(tx_by_hash[value]["nonce"]))
    ]
    incoming_records = [
        compact_tx(
            tx,
            "incoming_transaction",
            "not sent by the guardian address and therefore outside the outgoing evidence inventory",
        )
        for tx in sorted(incoming, key=lambda item: (int(item["blockNumber"]), int(item["transactionIndex"])))
    ]
    nft_set_digest = hashlib.sha256(
        ("\n".join(sorted(nft_hashes)) + "\n").encode("ascii")
    ).hexdigest()

    report = {
        "schema": "trinityaccord.ethereum-address-evidence-scope.v1",
        "status": "PASS",
        "address": ADDRESS,
        "network": {"name": "Ethereum Mainnet", "chain_id": 1},
        "observed_at": args.observed_at,
        "observation_source": {
            "provider": args.provider,
            "query_url": args.query_url,
            "response_sha256": hashlib.sha256(source_bytes).hexdigest(),
            "response_status": source.get("status"),
            "response_message": source.get("message"),
        },
        "observation_boundary": (
            "This classifies the provider-returned normal-transaction history visible at the named observation time, "
            "through outgoing nonce 219. It is a completeness/discovery audit for that bounded view, not a "
            "cryptographic proof that no omitted, internal, future, reorged or provider-hidden transaction exists."
        ),
        "summary": {
            "observed_transactions": len(transactions),
            "outgoing_transactions": len(outgoing),
            "incoming_transactions": len(incoming),
            "outgoing_nonce_min": min(nonces),
            "outgoing_nonce_max": max(nonces),
            "outgoing_nonces_contiguous": True,
            "non_nft_evidence_self_transactions": len(self_data),
            "chronicle_nft_mint_transactions": len(nft_hashes),
            "other_outgoing_account_operations": len(other_hashes),
            "max_observed_block": max(int(tx["blockNumber"]) for tx in transactions),
        },
        "classification_invariant": (
            "220 outgoing = 12 non-NFT self-data evidence + 175 Chronicle NFT mints + 33 other account operations; "
            "the 12 incoming transactions are classified separately."
        ),
        "non_nft_evidence": {
            "manifest": "evidence/ethereum-evidence-annex-v1/ANNEX-MANIFEST.json",
            "offline_report": "evidence/ethereum-evidence-annex-v1/reports/OFFLINE-VERIFICATION.json",
            "records": evidence_records,
        },
        "chronicle_nft": {
            "identity_index": "nft-identity-index.json",
            "proof_annex": "evidence/nft-proof-annex-v1/NFT-COLLECTION-COMMITMENT.json",
            "transaction_count": len(nft_hashes),
            "sorted_transaction_hashes_sha256": nft_set_digest,
            "duplication_policy": "Use the identity index for the complete 175-item list; this scope audit binds the sorted set digest instead of duplicating it.",
        },
        "other_outgoing_account_operations": other_records,
        "incoming_transactions": incoming_records,
        "freeze_boundary": {
            "published_final_doi_v3": "10.5281/zenodo.21855814",
            "published_final_doi_v3_non_nft_anchor_count": 10,
            "current_live_repository_non_nft_anchor_count": 12,
            "post_freeze_addition_tx_hashes": sorted(POST_FREEZE_TXS),
            "new_doi_publication_status": "not_authorized_not_attempted",
            "new_arweave_upload_status": "intentionally_deferred_not_attempted",
        },
        "source_digest_algorithm": "sha256(canonical_json_without_source_digest)",
    }
    report["source_digest"] = source_digest(report)
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
