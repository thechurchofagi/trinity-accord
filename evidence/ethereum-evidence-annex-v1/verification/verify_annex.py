#!/usr/bin/env python3
"""Fail-closed offline verifier for Ethereum Proof-Carrying Evidence Annex v1."""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

import rlp
from eth_hash.auto import keccak
from trie import HexaryTrie

ANNEX_DIR = pathlib.Path(__file__).resolve().parents[1]
REPO_ROOT = ANNEX_DIR.parents[1]
MANIFEST = ANNEX_DIR / "ANNEX-MANIFEST.json"
GENESIS_TIME = 1606824023
SECONDS_PER_SLOT = 12


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def h2b(value: str) -> bytes:
    if not isinstance(value, str) or not value.startswith("0x"):
        raise ValueError(f"not hex: {value!r}")
    raw = value[2:]
    if len(raw) % 2:
        raw = "0" + raw
    return bytes.fromhex(raw)


def q(value: str | None) -> int:
    return 0 if value is None else int(value, 16)


def execution_header_hash(block: dict) -> bytes:
    fields = [
        h2b(block["parentHash"]), h2b(block["sha3Uncles"]), h2b(block["miner"]),
        h2b(block["stateRoot"]), h2b(block["transactionsRoot"]), h2b(block["receiptsRoot"]),
        h2b(block["logsBloom"]), q(block["difficulty"]), q(block["number"]), q(block["gasLimit"]),
        q(block["gasUsed"]), q(block["timestamp"]), h2b(block["extraData"]), h2b(block["mixHash"]), h2b(block["nonce"]),
    ]
    for name, conv in [
        ("baseFeePerGas", q), ("withdrawalsRoot", h2b), ("blobGasUsed", q), ("excessBlobGas", q),
        ("parentBeaconBlockRoot", h2b), ("requestsHash", h2b),
    ]:
        if block.get(name) is not None:
            fields.append(conv(block[name]))
    return keccak(rlp.encode(fields))


def build_root(values: list[bytes]) -> bytes:
    trie = HexaryTrie(db={})
    for i, value in enumerate(values):
        trie[rlp.encode(i)] = value
    return trie.root_hash


def merkleize_chunks(chunks: list[bytes]) -> bytes:
    if any(len(x) != 32 for x in chunks):
        raise ValueError("SSZ chunk must be 32 bytes")
    n = 1
    while n < len(chunks):
        n *= 2
    nodes = chunks + [b"\x00" * 32] * (n - len(chunks))
    while len(nodes) > 1:
        nodes = [hashlib.sha256(nodes[i] + nodes[i + 1]).digest() for i in range(0, len(nodes), 2)]
    return nodes[0]


def beacon_header_root(message: dict) -> str:
    fields = [
        int(message["slot"]).to_bytes(8, "little") + b"\x00" * 24,
        int(message["proposer_index"]).to_bytes(8, "little") + b"\x00" * 24,
        h2b(message["parent_root"]), h2b(message["state_root"]), h2b(message["body_root"]),
    ]
    return "0x" + merkleize_chunks(fields).hex()


def verify_single_ssz_proof(proof: dict, expected_root: str) -> None:
    node = h2b(proof["leaf"])
    gindex = int(proof["gindex"])
    if gindex <= 1:
        raise ValueError("invalid SSZ generalized index")
    for witness_hex in proof["witnesses"]:
        witness = h2b(witness_hex)
        if len(witness) != 32:
            raise ValueError("invalid SSZ witness length")
        node = hashlib.sha256((witness + node) if (gindex & 1) else (node + witness)).digest()
        gindex //= 2
    if gindex != 1:
        raise ValueError("SSZ proof depth does not terminate at root")
    if "0x" + node.hex() != expected_root.lower():
        raise ValueError("SSZ proof root mismatch")


def verify_l2(anchor: dict) -> dict:
    txh = anchor["tx_hash"].lower()
    path = ANNEX_DIR / "proof-material" / txh / "L2-execution-witness.json"
    witness = json.loads(path.read_text(encoding="utf-8"))
    if witness.get("schema") != "trinityaccord.ethereum-execution-inclusion-witness.v1":
        raise ValueError("unexpected L2 witness schema")
    if witness.get("target_tx_hash", "").lower() != txh:
        raise ValueError("L2 target transaction mismatch")
    block = witness["block"]
    if block["hash"].lower() != anchor["execution_reference"]["block_hash"].lower():
        raise ValueError("L2 execution block hash mismatch")
    if execution_header_hash(block) != h2b(block["hash"]):
        raise ValueError("execution header hash mismatch")
    raw_txs = [h2b(x) for x in witness["raw_transactions"]]
    encoded_receipts = [h2b(x) for x in witness["encoded_receipts"]]
    tx_hashes = [x.lower() for x in block["transactions"]]
    if len(raw_txs) != len(tx_hashes) or len(encoded_receipts) != len(tx_hashes):
        raise ValueError("L2 witness list length mismatch")
    for expected, raw in zip(tx_hashes, raw_txs):
        if "0x" + keccak(raw).hex() != expected:
            raise ValueError(f"raw transaction hash mismatch: {expected}")
    if "0x" + build_root(raw_txs).hex() != block["transactionsRoot"].lower():
        raise ValueError("transactions trie root mismatch")
    if "0x" + build_root(encoded_receipts).hex() != block["receiptsRoot"].lower():
        raise ValueError("receipts trie root mismatch")
    idx = int(witness["target_transaction_index"])
    if idx < 0 or idx >= len(tx_hashes) or tx_hashes[idx] != txh:
        raise ValueError("target transaction index mismatch")
    return {"tx_hash": txh, "status": "PASS", "block_hash": block["hash"].lower(), "transaction_index": idx, "transactions": len(tx_hashes)}


def verify_l3(anchor: dict, l2: dict) -> dict:
    txh = anchor["tx_hash"].lower()
    path = ANNEX_DIR / "proof-material" / txh / "L3-consensus-witness.json"
    witness = json.loads(path.read_text(encoding="utf-8"))
    if witness.get("schema") != "trinityaccord.ethereum-consensus-finality-witness.v1":
        raise ValueError("unexpected L3 witness schema")
    if witness.get("target_tx_hash", "").lower() != txh:
        raise ValueError("L3 target transaction mismatch")
    if witness.get("execution_block_hash", "").lower() != l2["block_hash"]:
        raise ValueError("L3 execution block hash mismatch")
    target = witness["target_beacon_header"]
    target_root = beacon_header_root(target["message"]).lower()
    if target_root != target["root"].lower():
        raise ValueError("target beacon header root mismatch")
    expected_slot = (anchor["execution_reference"]["block_timestamp_unix"] - GENESIS_TIME) // SECONDS_PER_SLOT
    if int(target["message"]["slot"]) != expected_slot or int(witness["target_beacon_slot"]) != expected_slot:
        raise ValueError("target beacon slot mismatch")
    leaf_proof = witness["execution_block_hash_to_body_root"]
    if leaf_proof["leaf"].lower() != l2["block_hash"]:
        raise ValueError("SSZ execution block-hash leaf mismatch")
    body_root = target["message"]["body_root"].lower()
    if leaf_proof["body_root"].lower() != body_root:
        raise ValueError("SSZ proof body root declaration mismatch")
    verify_single_ssz_proof(leaf_proof, body_root)

    checkpoint = witness["trusted_finalized_checkpoint"]
    trust_model = checkpoint.get("trust_model", "")
    if checkpoint.get("schema") != "trinityaccord.ethereum-trusted-finalized-checkpoint.v1":
        raise ValueError("unexpected trusted checkpoint schema")
    if "weak-subjectivity" not in trust_model or "explicit" not in trust_model:
        raise ValueError("trusted checkpoint assumption is not explicit")
    checkpoint_root = checkpoint["root"].lower()
    votes = int(checkpoint.get("matching_provider_votes", 0))
    observed_matches = sum(
        1 for o in witness.get("checkpoint_observations", [])
        if o.get("root", "").lower() == checkpoint_root and int(o.get("epoch", -1)) == int(checkpoint["finalized_epoch"])
    )
    if votes < 2 or observed_matches < votes:
        raise ValueError("trusted checkpoint provenance quorum mismatch")

    expected = checkpoint_root
    chain = witness.get("checkpoint_to_target_parent_chain", [])
    if not chain:
        raise ValueError("empty checkpoint ancestry chain")
    for item in chain:
        computed = beacon_header_root(item["message"]).lower()
        if computed != item["root"].lower() or computed != expected:
            raise ValueError("checkpoint ancestry header root mismatch")
        expected = item["message"]["parent_root"].lower()
    if expected != target_root:
        raise ValueError("trusted finalized checkpoint is not linked to target beacon block")
    return {
        "tx_hash": txh,
        "status": "PASS",
        "target_beacon_root": target_root,
        "trusted_finalized_checkpoint": checkpoint_root,
        "checkpoint_epoch": int(checkpoint["finalized_epoch"]),
        "ancestor_headers": len(chain),
        "trust_boundary": "PASS is conditional on the explicitly declared weak-subjectivity finalized checkpoint.",
    }


def main() -> int:
    failures: list[str] = []
    checks: list[dict] = []
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"result": "FAIL", "failures": [f"manifest parse: {exc}"]}, indent=2))
        return 1

    if data.get("schema") != "trinityaccord.ethereum-proof-carrying-evidence-annex.v1":
        failures.append("unexpected schema")
    if data.get("network", {}).get("chain_id") != 1:
        failures.append("network chain_id must be 1")
    boundary = data.get("authority_boundary", {})
    if boundary.get("canonical_authority") != "three Bitcoin Originals only":
        failures.append("canonical authority boundary changed")
    if boundary.get("no_authority_escalation") is not True:
        failures.append("no_authority_escalation must be true")

    anchors = data.get("anchors")
    if not isinstance(anchors, list) or not anchors:
        failures.append("anchors missing")
        anchors = []
    txs = [a.get("tx_hash") for a in anchors]
    if len(txs) != len(set(txs)):
        failures.append("duplicate transaction hash")
    if len(anchors) != 10:
        failures.append(f"expected 10 audited non-NFT anchors, found {len(anchors)}")

    byte_pass = True
    l2_pass = True
    l3_pass = True
    l2_checks = []
    l3_checks = []
    for a in anchors:
        tx = a.get("tx_hash", "")
        if not (isinstance(tx, str) and tx.startswith("0x") and len(tx) == 66):
            failures.append(f"{a.get('id')}: invalid tx hash")
        payloads = a.get("payloads", [])
        if not payloads:
            failures.append(f"{tx}: no preserved payload mapping")
            byte_pass = False
        for p in payloads:
            rel = p.get("path")
            fp = REPO_ROOT / rel if rel else None
            result = {"tx_hash": tx, "path": rel}
            if not fp or not fp.is_file():
                result.update({"status": "FAIL", "reason": "missing"})
                failures.append(f"{tx}: missing {rel}")
                byte_pass = False
            else:
                size = fp.stat().st_size
                digest = sha256_file(fp)
                result.update({"size": size, "sha256": digest})
                if size != p.get("size") or digest != p.get("sha256"):
                    result.update({"status": "FAIL", "reason": "size_or_sha256_mismatch"})
                    failures.append(f"{tx}: byte mismatch {rel}")
                    byte_pass = False
                else:
                    result["status"] = "PASS"
            checks.append(result)
        try:
            if a.get("proof_status", {}).get("L2_EXECUTION_INCLUSION") != "PASS":
                raise ValueError("manifest does not declare L2 PASS")
            l2 = verify_l2(a)
            l2_checks.append(l2)
        except Exception as exc:
            l2_pass = False
            failures.append(f"{tx}: L2 {exc}")
            continue
        try:
            if a.get("proof_status", {}).get("L3_CONSENSUS_FINALITY") != "PASS":
                raise ValueError("manifest does not declare L3 PASS")
            l3_checks.append(verify_l3(a, l2))
        except Exception as exc:
            l3_pass = False
            failures.append(f"{tx}: L3 {exc}")

    summary = {
        "schema": "trinityaccord.ethereum-annex-offline-verification.v2",
        "result": "PASS" if not failures else "FAIL",
        "L1_BYTE_INTEGRITY": "PASS" if byte_pass else "FAIL",
        "L2_EXECUTION_INCLUSION": "PASS" if l2_pass and len(l2_checks) == len(anchors) else "FAIL",
        "L3_CONSENSUS_FINALITY": "PASS" if l3_pass and len(l3_checks) == len(anchors) else "FAIL",
        "anchors": len(anchors),
        "payload_checks": len(checks),
        "checks": checks,
        "l2_checks": l2_checks,
        "l3_checks": l3_checks,
        "failures": failures,
        "claim_boundary": "L2 PASS is offline execution inclusion bound to the execution block hash. L3 PASS links that execution block hash through an SSZ Beacon-body proof and Beacon parent-root ancestry to an explicit weak-subjectivity trusted finalized checkpoint; it is not a trust-free real-world clock attestation.",
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
