#!/usr/bin/env python3
"""Fail-closed classifier for the Base and Polygon Chronicle evidence.

This program deliberately separates cryptographic inclusion from chain finality and
from payload availability.  A green audit means that the classification is honest;
it does not mean ``strict_completion`` is true.
"""
import argparse
import hashlib
import json
import pathlib

import rlp
from eth_hash.auto import keccak
from trie import HexaryTrie

ROOTCHAIN = "0x86e4dc95c7fbdbf52e33d563bbdb00823894c287"
NEW_HEADER_TOPIC = "0x" + keccak(b"NewHeaderBlock(address,uint256,uint256,uint256,uint256,bytes32)").hex()
OPTIMISM_COMMIT = "c6f39182c975db976aaaa01ef32884c41b1c9660"
SUPERCHAIN_REGISTRY_COMMIT = "5b055be4d294ce43814a44c8839d89b2436dc8aa"


def load(path):
    return json.loads(pathlib.Path(path).read_text())


def h2b(value):
    if isinstance(value, (bytes, bytearray)):
        return bytes(value)
    value = str(value)
    value = value[2:] if value.startswith("0x") else value
    return bytes.fromhex(value)


def word(value):
    return int(value).to_bytes(32, "big")


def sha256_file(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def merkle_root(leaf, index, siblings):
    value = leaf
    for raw in siblings:
        sibling = h2b(raw)
        value = keccak(value + sibling) if index % 2 == 0 else keccak(sibling + value)
        index //= 2
    return value


def receipt_payload(encoded):
    """Return the RLP receipt fields for both legacy and typed receipts."""
    if not encoded:
        raise ValueError("empty receipt")
    payload = encoded[1:] if encoded[0] <= 0x7f else encoded
    fields = rlp.decode(payload)
    if not isinstance(fields, list) or len(fields) != 4:
        raise ValueError("malformed receipt fields")
    return fields


def verify_checkpoint_receipt(checkpoint):
    header = h2b(checkpoint["block_header_rlp"])
    fields = rlp.decode(header)
    if len(fields) < 12:
        raise ValueError("Ethereum header has fewer than 12 fields")
    if "0x" + keccak(header).hex() != checkpoint["ethereum_block_hash"].lower():
        raise ValueError("Ethereum header hash mismatch")
    if "0x" + bytes(fields[5]).hex() != checkpoint["receipts_root"].lower():
        raise ValueError("Ethereum receiptsRoot mismatch")
    if int.from_bytes(fields[8], "big") != int(checkpoint["ethereum_block_number"]):
        raise ValueError("Ethereum block number mismatch")
    if int.from_bytes(fields[11], "big") != int(checkpoint["ethereum_block_timestamp"]):
        raise ValueError("Ethereum block timestamp mismatch")

    key = h2b(checkpoint["mpt_key_rlp"])
    if key != rlp.encode(int(checkpoint["receipt_index"])):
        raise ValueError("receipt MPT key/index mismatch")
    proof = [rlp.decode(h2b(node)) for node in checkpoint["receipt_proof_nodes_rlp"]]
    encoded_receipt = h2b(checkpoint["receipt_rlp"])
    actual = HexaryTrie.get_from_proof(bytes(fields[5]), key, proof)
    if actual != encoded_receipt:
        raise ValueError("Ethereum receipt MPT proof mismatch")

    expected_data = word(checkpoint["start"]) + word(checkpoint["end"]) + h2b(checkpoint["root"])
    expected_id = "0x" + word(checkpoint["header_block_id"]).hex()
    matches = 0
    for log in receipt_payload(encoded_receipt)[3]:
        address, topics, data = log
        topic_hex = ["0x" + bytes(topic).hex() for topic in topics]
        if (
            "0x" + bytes(address).hex() == ROOTCHAIN
            and len(topic_hex) == 4
            and topic_hex[0] == NEW_HEADER_TOPIC
            and topic_hex[2] == expected_id
            and bytes(data) == expected_data
        ):
            matches += 1
    if matches != 1:
        raise ValueError(f"exact RootChain NewHeaderBlock log count={matches}")


def polygon_leaf(source, block):
    witness = load(source / block["checkpoint_leaf"]["witness_file"])
    header = h2b(witness["block_header_rlp"])
    fields = rlp.decode(header)
    if len(fields) < 12:
        raise ValueError("Polygon header has fewer than 12 fields")
    block_hash = "0x" + keccak(header).hex()
    if block_hash != block["polygon_block_hash"].lower() or block_hash != witness["block_hash"].lower():
        raise ValueError("Polygon block hash mismatch")
    number = int.from_bytes(fields[8], "big")
    timestamp = int.from_bytes(fields[11], "big")
    if number != int(block["polygon_block_number"]):
        raise ValueError("Polygon block number mismatch")
    tx_root, receipt_root = bytes(fields[4]), bytes(fields[5])
    if "0x" + tx_root.hex() != witness["transactions_root"].lower():
        raise ValueError("Polygon transactionsRoot mismatch")
    if "0x" + receipt_root.hex() != witness["receipts_root"].lower():
        raise ValueError("Polygon receiptsRoot mismatch")
    leaf = keccak(word(number) + word(timestamp) + tx_root + receipt_root)
    if "0x" + leaf.hex() != block["checkpoint_leaf"]["checkpoint_leaf"].lower():
        raise ValueError("Polygon checkpoint leaf mismatch")
    return leaf


def content_roots(records):
    roots = {}
    for record in records:
        cars = [("metadata", record["content"]["metadata"].get("car"))]
        cars += [(item["role"], item.get("car")) for item in record["content"].get("media", [])]
        for role, car in cars:
            if not car:
                continue
            root = car.get("root_cid")
            if root:
                roots.setdefault(root, {"status": car.get("status"), "asset_id": record["asset_id"], "chain": record["chain"]["name"], "role": role})
    return roots


def verify_finality_bundle(root, source, settlement, settlement_path, source_tag, source_sha):
    """Verify finality bundle bindings and complete cross-layer populations.

    The workflow separately runs the OP Stack KZG/channel verifier, Ethereum MPT
    verifier, and Lodestar SSZ verifier.  This classifier recomputes every file
    binding and makes sure those proof populations are exactly the populations
    needed by the immutable identity and Polygon settlement sources.
    """
    root = pathlib.Path(root)
    binding = load(root / "SOURCE-BINDING.json")
    base = load(root / "base" / "BASE-OP-STACK-DERIVATION.json")
    beacon = load(root / "beacon" / "ETHEREUM-BEACON-FINALITY.json")
    timeline_path = source / "evidence-v2" / "BASE-TIMELINE.json"
    errors = []
    expected_binding = {
        "source_sidechain_release_tag": source_tag,
        "source_sidechain_commit_sha": source_sha,
        "base_timeline_sha256": sha256_file(timeline_path),
        "polygon_settlement_sha256": sha256_file(settlement_path),
        "base_derivation_sha256": sha256_file(root / "base" / "BASE-OP-STACK-DERIVATION.json"),
        "beacon_finality_sha256": sha256_file(root / "beacon" / "ETHEREUM-BEACON-FINALITY.json"),
    }
    copied_settlement = root / "POLYGON-ETHEREUM-SETTLEMENT.json"
    if not copied_settlement.exists() or sha256_file(copied_settlement) != expected_binding["polygon_settlement_sha256"]:
        errors.append("finality bundle copied Polygon settlement differs from verified source")
    copied_timeline = root / "BASE-TIMELINE.json"
    if not copied_timeline.exists() or sha256_file(copied_timeline) != expected_binding["base_timeline_sha256"]:
        errors.append("finality bundle copied Base timeline differs from verified source")
    if binding.get("optimism_commit_sha") != OPTIMISM_COMMIT:
        errors.append("finality bundle Optimism implementation pin mismatch")
    if binding.get("superchain_registry_commit_sha") != SUPERCHAIN_REGISTRY_COMMIT:
        errors.append("finality bundle Superchain Registry pin mismatch")
    if len(binding.get("proof_implementation_commit_sha", "")) != 40:
        errors.append("finality proof implementation commit is not a full SHA")
    for key, expected in expected_binding.items():
        if binding.get(key) != expected:
            errors.append(f"finality binding mismatch {key}")

    timeline = load(timeline_path)
    timeline_txs = {item["transaction_hash"].lower() for item in timeline}
    base_txs = {item["transaction_hash"].lower() for item in base.get("records", [])}
    if (
        base.get("schema") != "trinity-accord/chronicle-base-op-stack-derivation/v1"
        or base.get("pass") is not True
        or base.get("source_base_timeline_sha256") != sha256_file(timeline_path)
        or base.get("summary", {}).get("records") != 61
        or base.get("summary", {}).get("derived_records") != 61
        or len(timeline) != 61
        or base_txs != timeline_txs
    ):
        errors.append("Base OP Stack derivation is not exact PASS 61/61")

    frame_blocks = set()
    for record in base.get("records", []):
        for frame in record.get("derivation", {}).get("channel_frames", []):
            proof_path = root / "base" / frame.get("l1_transaction_proof_file", "")
            if not proof_path.is_file():
                errors.append(f"missing Base L1 transaction proof {proof_path}")
                continue
            proof = load(proof_path)
            if proof.get("transaction_hash", "").lower() != frame.get("transaction_hash", "").lower():
                errors.append("Base frame/L1 transaction proof hash mismatch")
            frame_blocks.add(int(proof["ethereum_block_number"]))

    polygon_blocks = {int(item["ethereum_block_number"]) for item in settlement.get("checkpoints", [])}
    claims = {int(item["execution_block_number"]): item for item in beacon.get("claims", [])}
    needed_blocks = polygon_blocks | frame_blocks
    if (
        beacon.get("schema") != "trinity-accord/chronicle-ethereum-beacon-finality/v1"
        or beacon.get("pass") is not True
        or beacon.get("source_polygon_settlement_sha256") != expected_binding["polygon_settlement_sha256"]
        or beacon.get("source_base_derivation_sha256") != sha256_file(root / "base" / "BASE-OP-STACK-DERIVATION.json")
        or beacon.get("summary", {}).get("polygon_checkpoint_blocks") != 117
        or set(claims) != needed_blocks
    ):
        errors.append(f"Beacon finality population mismatch claims={len(claims)} needed={len(needed_blocks)}")
    for number, claim in claims.items():
        ssz_path = root / "beacon" / claim.get("ssz_file", "")
        observations = claim.get("observations", [])
        if not ssz_path.is_file() or sha256_file(ssz_path) != claim.get("ssz_sha256"):
            errors.append(f"Beacon SSZ object mismatch execution_block={number}")
        if claim.get("provider_quorum", 0) < 2 or len(observations) < 2:
            errors.append(f"Beacon provider quorum below two execution_block={number}")
        for observation in observations:
            if (
                observation.get("beacon_root") != claim.get("beacon_root")
                or observation.get("execution_block_hash") != claim.get("execution_block_hash")
                or observation.get("finalized") is not True
                or observation.get("execution_optimistic") is not False
            ):
                errors.append(f"Beacon observation mismatch execution_block={number}")

    assurance = base.get("assurance", {})
    if not str(assurance.get("withdrawal_fault_proof", "")).startswith("NOT_APPLICABLE"):
        errors.append("Base ordinary-transaction withdrawal boundary is absent")
    return {
        "errors": errors,
        "polygon_execution_blocks": len(polygon_blocks),
        "base_l1_frame_blocks": len(frame_blocks),
        "beacon_execution_blocks": len(claims),
    }


def strict_layer_complete(layer):
    return layer["status"] in {"PASS", "NOT_APPLICABLE"}


def audit(args):
    source = pathlib.Path(args.source_dir)
    evidence = source / "evidence-v2"
    index_path = evidence / "SIDECHAIN-NFT-IDENTITY-INDEX.json"
    index = load(index_path)
    records = index["records"]
    offline = load(evidence / "OFFLINE-VERIFICATION.json")
    exceptions = load(args.exceptions)["exceptions"]
    provenance = load(args.provenance)
    settlement = load(args.polygon_settlement)
    binding = load(args.polygon_binding)
    errors = []

    counts = {"polygon": 0, "base": 0}
    assets = {}
    for record in records:
        name = record["chain"]["name"]
        if name not in counts:
            errors.append(f"unexpected chain {name}")
            continue
        counts[name] += 1
        assets[record["asset_id"]] = record
    if len(records) != 217 or counts != {"polygon": 156, "base": 61} or len(assets) != 217:
        errors.append(f"identity population mismatch records={len(records)} chains={counts} unique={len(assets)}")
    if offline.get("pass") is not True or offline.get("records") != 217 or offline.get("l2_records_checked") != 217:
        errors.append("source offline L1/L2 verification is not PASS 217/217")

    roots = content_roots(records)
    unresolved = {root for root, item in roots.items() if item["status"] != "ok"}
    declared = {item["root_cid"] for item in exceptions}
    if len(roots) != 257 or len(roots) - len(unresolved) != 250:
        errors.append(f"payload root population mismatch total={len(roots)} exact={len(roots)-len(unresolved)}")
    if unresolved != declared:
        errors.append("unresolved payload roots differ from closed exception set")
    reviewed = {item["root_cid"] for item in provenance.get("records", [])}
    if reviewed != unresolved or provenance.get("summary", {}).get("external_delivery_confirmed") != 7:
        errors.append("seven-root external-delivery review does not exactly cover exceptions")
    for item in provenance.get("records", []):
        if item.get("classification") != "externally_delivered_not_self_minted":
            errors.append(f"provenance classification mismatch {item.get('root_cid')}")

    if settlement.get("schema") != "trinity-accord/chronicle-polygon-ethereum-settlement/v1":
        errors.append("unexpected Polygon settlement schema")
    if settlement.get("source_identity_index_sha256") != sha256_file(index_path):
        errors.append("Polygon settlement source identity SHA-256 mismatch")
    source_tag = binding.get("source_sidechain_release_tag", "")
    source_sha = binding.get("source_sidechain_commit_sha", "")
    if not source_tag.endswith(source_sha[:12]) or len(source_sha) != 40:
        errors.append("Polygon source release/commit binding mismatch")
    if settlement.get("rootchain_proxy", "").lower() != ROOTCHAIN:
        errors.append("Polygon RootChain address mismatch")

    checkpoint_by_id = {}
    for checkpoint in settlement.get("checkpoints", []):
        try:
            verify_checkpoint_receipt(checkpoint)
            checkpoint_by_id[int(checkpoint["header_block_id"])] = checkpoint
        except Exception as exc:
            errors.append(f"checkpoint {checkpoint.get('header_block_id')}: {exc}")
    seen_polygon = set()
    for block in settlement.get("blocks", []):
        try:
            leaf = polygon_leaf(source, block)
            checkpoint = checkpoint_by_id[int(block["header_block_id"])]
            if not (int(checkpoint["start"]) <= int(block["polygon_block_number"]) <= int(checkpoint["end"])):
                raise ValueError("block outside checkpoint range")
            root = merkle_root(leaf, int(block["proof_index"]), block["proof_siblings"])
            if "0x" + root.hex() != checkpoint["root"].lower() or "0x" + root.hex() != block["checkpoint_root"].lower():
                raise ValueError("Bor checkpoint Merkle root mismatch")
            expected_assets = set(block["asset_ids"])
            for asset_id in expected_assets:
                record = assets.get(asset_id)
                if not record or record["chain"]["name"] != "polygon":
                    raise ValueError(f"invalid Polygon asset mapping {asset_id}")
                if int(record["origin"]["block_number"]) != int(block["polygon_block_number"]):
                    raise ValueError(f"asset block mismatch {asset_id}")
            if seen_polygon & expected_assets:
                raise ValueError("duplicate Polygon asset mapping")
            seen_polygon |= expected_assets
        except Exception as exc:
            errors.append(f"Polygon block {block.get('polygon_block_number')}: {exc}")
    all_polygon = {asset_id for asset_id, record in assets.items() if record["chain"]["name"] == "polygon"}
    if seen_polygon != all_polygon or len(checkpoint_by_id) != 117:
        errors.append(f"Polygon settlement coverage mismatch assets={len(seen_polygon)}/156 checkpoints={len(checkpoint_by_id)}/117")

    finality = None
    if args.finality_dir:
        try:
            finality = verify_finality_bundle(
                args.finality_dir, source, settlement, args.polygon_settlement, source_tag, source_sha
            )
            errors.extend(finality["errors"])
        except Exception as exc:
            errors.append(f"finality bundle: {exc}")

    audit_pass = not errors
    finality_pass = finality is not None and not finality["errors"]
    layers = {
        "identity_commitment": {"status": "PASS" if audit_pass else "FAIL", "records": len(records)},
        "exact_payload_recovery": {"status": "INCOMPLETE", "verified_roots": len(roots)-len(unresolved), "total_roots": len(roots), "unresolved_roots": sorted(unresolved)},
        "l2_execution_inclusion": {"status": "PASS" if audit_pass else "FAIL", "records": offline.get("l2_records_checked")},
        "polygon_checkpoint_to_ethereum_execution": {"status": "PASS" if audit_pass else "FAIL", "records": len(seen_polygon), "checkpoints": len(checkpoint_by_id)},
        "polygon_ethereum_beacon_finality": {
            "status": "PASS" if finality_pass else ("FAIL" if args.finality_dir else "NOT_CAPTURED"),
            "execution_blocks": finality["polygon_execution_blocks"] if finality else 0,
            "assumption": "Ethereum weak subjectivity; two independent finalized/non-optimistic consensus-client observations plus offline SSZ root and execution-payload verification",
        },
        "base_op_stack_l1_data_derivation": {
            "status": "PASS" if finality_pass else ("FAIL" if args.finality_dir else "NOT_CAPTURED"),
            "records": 61 if finality_pass else 0,
            "l1_frame_blocks": finality["base_l1_frame_blocks"] if finality else 0,
        },
        "base_ethereum_beacon_finality": {
            "status": "PASS" if finality_pass else ("FAIL" if args.finality_dir else "NOT_CAPTURED"),
            "execution_blocks": finality["base_l1_frame_blocks"] if finality else 0,
            "assumption": "Ethereum weak subjectivity; same consensus evidence boundary as Polygon",
        },
        "base_l2_to_l1_withdrawal_fault_proof": {
            "status": "NOT_APPLICABLE",
            "reason": "The 61 origins are ordinary Base L2 NFT transactions, not withdrawal claims.",
        },
    }
    strict_complete = all(strict_layer_complete(value) for value in layers.values())
    return {
        "schema": "trinity-accord/chronicle-sidechain-strict-verification/v2",
        "audit_pass": audit_pass,
        "strict_completion": "PASS" if strict_complete else "INCOMPLETE",
        "strict_completion_pass": strict_complete,
        "chains": counts,
        "source": {"release_tag": source_tag, "commit_sha": source_sha, "identity_index_sha256": sha256_file(index_path)},
        "layers": layers,
        "provenance_boundary": "Seven roots were externally delivered, not self-minted by the target. This does not recover or verify their payload bytes and is not a legal ownership conclusion.",
        "finality_boundary": "When the supplementary bundle is supplied, Polygon and Base execution blocks are bound to raw Beacon SSZ objects and two independent finalized/non-optimistic consensus-client observations. This is Ethereum weak-subjectivity evidence, not Bitcoin-style objective proof from genesis. Base's seven-day fault-proof window is not applicable to ordinary L2 origin transactions.",
        "errors": errors,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--polygon-settlement", required=True)
    parser.add_argument("--polygon-binding", required=True)
    parser.add_argument("--finality-dir")
    parser.add_argument("--exceptions", default="evidence/chronicle-sidechain-historical-payload-exceptions.json")
    parser.add_argument("--provenance", default="evidence/chronicle-sidechain-seven-root-provenance-review.v1.json")
    parser.add_argument("--output", required=True)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    report = audit(args)
    output = pathlib.Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"[SIDECHAIN STRICT AUDIT] audit_pass={str(report['audit_pass']).lower()} strict_completion={report['strict_completion']} polygon={report['chains']['polygon']} base={report['chains']['base']}")
    for error in report["errors"]:
        print(f"[SIDECHAIN STRICT ERROR] {error}")
    if not report["audit_pass"] or (args.require_complete and not report["strict_completion_pass"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
