#!/usr/bin/env python3
"""Controlled capture for the 12-item authority-address Bitcoin proof annex v2.

The eight already-proved inscriptions reuse their immutable v1 reveal/block proof
bytes and are re-bound to the exact address-wide archive. The four recovered
formation records are captured from two public Bitcoin providers. Ordinary
verification is network-free and is performed by verify_annex.py.
"""
from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ANNEX_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = ANNEX_DIR.parents[1]
V1_DIR = ANNEX_DIR.parent / "bitcoin-inscription-proof-annex-v1"
V1_VERIFICATION = V1_DIR / "verification"
sys.path.insert(0, str(V1_VERIFICATION))

import capture_proofs as legacy_capture  # noqa: E402
from bitcoin_proof_primitives_v1 import (  # noqa: E402
    extract_inscription_envelopes,
    merkle_branch,
    merkle_root,
    parse_block,
    parse_header,
    parse_transaction_hex,
    segwit_address,
    sha256_file,
    verify_taproot_reveal_binding,
    verify_witness_commitment,
    witness_commitment,
)

ADDRESS_ROOT = REPO_ROOT / "bitcoin-inscription-mirrors/address-wide"
ADDRESS_MANIFEST = ADDRESS_ROOT / "manifest.json"
CLASSIFICATION = ADDRESS_ROOT / "classification.json"
AUTHORITY = REPO_ROOT / "archive/authority-manifest/authority.jcs.json"
V1_MANIFEST = V1_DIR / "ANNEX-MANIFEST.json"
CONFIRMATION_DEPTH = 144
EXPECTED_COUNT = 12
EXPECTED_FORMATION = 4
EXPECTED_CANONICAL = 3
EXPECTED_POST = 5


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON object required: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()


def _authority_by_txid() -> dict[str, dict[str, Any]]:
    bitcoin = load_json(AUTHORITY)["bitcoin"]
    out: dict[str, dict[str, Any]] = {}
    for classification, records in (
        ("canonical_original", bitcoin["originals"]),
        ("non_amending_ancillary", bitcoin["ancillary"]),
    ):
        for source in records:
            txid = str(source["txid"]).lower()
            out[txid] = {**source, "_proof_classification": classification}
    if len(out) != 8:
        raise RuntimeError("legacy authority set must remain exactly 3 + 5")
    return out


def address_records() -> list[dict[str, Any]]:
    manifest = load_json(ADDRESS_MANIFEST)
    classification = load_json(CLASSIFICATION)
    if manifest.get("schema") != "trinityaccord.bitcoin-address-inscription-mirror.v2":
        raise RuntimeError("address-wide mirror must be v2")
    if manifest.get("count") != EXPECTED_COUNT or len(manifest.get("ids", [])) != EXPECTED_COUNT:
        raise RuntimeError("address-wide mirror must contain exactly 12 current-address records")
    counts = classification.get("counts", {})
    expected_counts = {
        "current_address_snapshot": EXPECTED_COUNT,
        "pre_canonical_formation": EXPECTED_FORMATION,
        "canonical_originals": EXPECTED_CANONICAL,
        "post_canonical_non_amending": EXPECTED_POST,
    }
    if counts != expected_counts:
        raise RuntimeError("classification must preserve the 4 + 3 + 5 boundary")

    objects = {str(item["id"]): item for item in manifest["objects"]}
    classes = {str(item["ordinals_inscription_id"]): item for item in classification["records"]}
    ids = [str(item) for item in manifest["ids"]]
    if set(ids) != set(objects) or set(ids) != set(classes):
        raise RuntimeError("address-wide manifest/classification ID set mismatch")

    authority = _authority_by_txid()
    records: list[dict[str, Any]] = []
    canonical_count = 0
    formation_count = 0
    post_count = 0
    for inscription_id in ids:
        if not inscription_id.endswith("i0") or len(inscription_id) != 66:
            raise RuntimeError(f"v2 requires txid+i0 identity: {inscription_id}")
        txid = inscription_id[:-2]
        obj_dir = ADDRESS_ROOT / "objects" / inscription_id
        metadata = load_json(obj_dir / "metadata.json")
        cls = classes[inscription_id]
        if metadata.get("id") != inscription_id or metadata.get("address") != manifest["address"]:
            raise RuntimeError(f"address metadata identity mismatch: {inscription_id}")
        layer = str(cls.get("layer"))
        canonical = cls.get("canonical") is True
        if canonical:
            proof_classification = "canonical_original"
            canonical_count += 1
        elif layer == "pre_canonical_formation":
            proof_classification = "pre_canonical_formation"
            formation_count += 1
        elif layer == "post_canonical_non_amending":
            proof_classification = "non_amending_ancillary"
            post_count += 1
        else:
            raise RuntimeError(f"unsupported historical layer: {inscription_id}")
        if cls.get("amends_canon") is not False:
            raise RuntimeError(f"non-amending boundary violated: {inscription_id}")

        known = authority.get(txid)
        if proof_classification == "pre_canonical_formation":
            if known is not None:
                raise RuntimeError("formation record unexpectedly appears in the legacy authority set")
        else:
            if known is None or known["_proof_classification"] != proof_classification:
                raise RuntimeError("legacy authority/classification mismatch")
            if int(known["inscription_id"]) != int(metadata["number"]):
                raise RuntimeError("legacy authority inscription number mismatch")
            if int(known["block_height"]) != int(metadata["height"]):
                raise RuntimeError("legacy authority block height mismatch")

        records.append(
            {
                "inscription_number": str(metadata["number"]),
                "ordinals_inscription_id": inscription_id,
                "txid": txid,
                "block_height": int(metadata["height"]),
                "known_block_hash": str(known["block_hash"]).lower() if known else None,
                "classification": proof_classification,
                "historical_layer": layer,
                "title": cls.get("title"),
                "destination_address": str(manifest["address"]).lower(),
                "object": objects[inscription_id],
                "object_dir": obj_dir,
            }
        )
    if (formation_count, canonical_count, post_count) != (4, 3, 5):
        raise RuntimeError("proof source set is not exactly 4 + 3 + 5")
    records.sort(key=lambda item: (item["block_height"], int(item["inscription_number"])))
    return records


def archived_payload(record: dict[str, Any]) -> dict[str, Any]:
    obj = record["object"]
    obj_dir: Path = record["object_dir"]
    body_path = obj_dir / "content.b64"
    metadata_path = obj_dir / "inscription-metadata.cbor.b64"
    body = base64.b64decode(body_path.read_text(encoding="ascii").strip(), validate=True)
    metadata = base64.b64decode(metadata_path.read_text(encoding="ascii").strip(), validate=True)
    body_sha = hashlib.sha256(body).hexdigest()
    metadata_sha = hashlib.sha256(metadata).hexdigest()
    if len(body) != int(obj["content_length"]) or body_sha != obj["content_sha256"]:
        raise RuntimeError(f"address body binding mismatch: {record['ordinals_inscription_id']}")
    if len(metadata) != int(obj["inscription_metadata_length"]):
        raise RuntimeError(f"address metadata length mismatch: {record['ordinals_inscription_id']}")
    if metadata_sha != obj["inscription_metadata_sha256"]:
        raise RuntimeError(f"address metadata SHA mismatch: {record['ordinals_inscription_id']}")
    if bool(metadata) != bool(obj["inscription_metadata_present"]):
        raise RuntimeError(f"address metadata presence mismatch: {record['ordinals_inscription_id']}")
    return {
        "body": body,
        "body_path": body_path,
        "metadata": metadata,
        "metadata_path": metadata_path,
        "body_sha256": body_sha,
        "metadata_sha256": metadata_sha,
    }


def envelope_metadata(envelope: dict[str, Any]) -> bytes:
    # Ord tag 5 may repeat because individual tapscript pushes are limited; ord
    # concatenates the values in encounter order before CBOR decoding.
    return b"".join(value for tag, value in envelope["fields"] if tag == b"\x05")


def enrich_proof_inscription(
    proof: dict[str, Any], record: dict[str, Any], envelope: dict[str, Any], archived: dict[str, Any]
) -> None:
    body = envelope["body"]
    metadata = envelope_metadata(envelope)
    if body != archived["body"]:
        raise RuntimeError("reveal body differs from address-wide exact bytes")
    if metadata != archived["metadata"]:
        raise RuntimeError("reveal tag-5 metadata differs from address-wide exact CBOR bytes")
    content_type = envelope["content_type"].decode("utf-8")
    if content_type != record["object"].get("content_type"):
        raise RuntimeError("reveal content type differs from address-wide manifest")

    inscription = proof["inscription"]
    inscription.update(
        {
            "inscription_number": record["inscription_number"],
            "ordinals_inscription_id": record["ordinals_inscription_id"],
            "inscription_index": 0,
            "classification": record["classification"],
            "historical_layer": record["historical_layer"],
            "title": record["title"],
            "expected_destination_address": record["destination_address"],
            "content_type_hex": envelope["content_type"].hex(),
            "content_type_utf8": content_type,
            "body_bytes": len(body),
            "body_sha256": archived["body_sha256"],
            "mirror_path": str(archived["body_path"].relative_to(REPO_ROOT)),
            "mirror_encoding": "base64_of_exact_body_bytes",
            "mirror_binding_method": "exact_bytes",
            "mirror_bytes": len(body),
            "mirror_sha256": archived["body_sha256"],
            "inscription_metadata_present": bool(metadata),
            "inscription_metadata_bytes": len(metadata),
            "inscription_metadata_sha256": archived["metadata_sha256"],
            "inscription_metadata_mirror_path": str(archived["metadata_path"].relative_to(REPO_ROOT)),
            "inscription_metadata_mirror_encoding": "base64_of_exact_concatenated_tag5_cbor_bytes",
            "inscription_metadata_binding_method": "exact_bytes",
        }
    )
    inscription.pop("canonicalized_body_sha256", None)


def write_proof_and_anchor(
    proof: dict[str, Any], record: dict[str, Any], output_dir: Path, *, block_hash: str, block_timestamp: int
) -> dict[str, Any]:
    txid = record["txid"]
    proof_path = output_dir / txid / "proof-witness.json"
    write_json(proof_path, proof)
    archived = archived_payload(record)
    return {
        "id": f"bitcoin-inscription-{record['inscription_number']}",
        "title": record["title"],
        "classification": record["classification"],
        "historical_layer": record["historical_layer"],
        "inscription_number": record["inscription_number"],
        "ordinals_inscription_id": record["ordinals_inscription_id"],
        "txid": txid,
        "wtxid": proof["reveal"]["wtxid"],
        "destination_address": record["destination_address"],
        "destination_output_index": proof["inscription"]["destination_output_index"],
        "block_reference": {
            "height": record["block_height"],
            "hash": block_hash,
            "timestamp": block_timestamp,
        },
        "content": {
            "content_type_hex": proof["inscription"]["content_type_hex"],
            "content_type_utf8": proof["inscription"]["content_type_utf8"],
            "body_bytes": len(archived["body"]),
            "body_sha256": archived["body_sha256"],
            "mirror_path": str(archived["body_path"].relative_to(REPO_ROOT)),
            "mirror_encoding": "base64_of_exact_body_bytes",
            "mirror_bytes": len(archived["body"]),
            "mirror_sha256": archived["body_sha256"],
            "mirror_binding_method": "exact_bytes",
        },
        "inscription_metadata": {
            "tag": 5,
            "present": bool(archived["metadata"]),
            "bytes": len(archived["metadata"]),
            "sha256": archived["metadata_sha256"],
            "mirror_path": str(archived["metadata_path"].relative_to(REPO_ROOT)),
            "mirror_encoding": "base64_of_exact_concatenated_tag5_cbor_bytes",
            "binding_method": "exact_bytes",
        },
        "proof_status": {
            "L1_INSCRIPTION_CONTENT_METADATA_AND_TAPROOT_BINDING": "PASS",
            "L2_BLOCK_AND_WITNESS_INCLUSION": "PASS",
            "L3_CHECKPOINT_RELATIVE_POW_ANCESTRY": "PASS",
        },
        "proof_material": {
            "path": f"evidence/bitcoin-inscription-proof-annex-v2/proof-material/{txid}/proof-witness.json",
            "size": proof_path.stat().st_size,
            "sha256": sha256_file(proof_path),
        },
    }


def upgrade_v1(record: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    old_manifest = load_json(V1_MANIFEST)
    old_by_txid = {str(item["txid"]).lower(): item for item in old_manifest["anchors"]}
    old_anchor = old_by_txid.get(record["txid"])
    if old_anchor is None:
        raise RuntimeError("v1 proof anchor missing for legacy inscription")
    old_path = REPO_ROOT / old_anchor["proof_material"]["path"]
    proof = copy.deepcopy(load_json(old_path))
    proof["schema"] = "trinityaccord.bitcoin-inscription-proof-witness.v2"
    reveal = parse_transaction_hex(proof["reveal"]["transaction_hex"])
    envelopes = extract_inscription_envelopes(reveal)
    if not envelopes or envelopes[0]["inscription_index"] != 0:
        raise RuntimeError("legacy reveal has no txid+i0 envelope")
    archived = archived_payload(record)
    enrich_proof_inscription(proof, record, envelopes[0], archived)
    proof["claim_boundary"]["proves"] = [
        "the exact inscription body is serialized in the reveal transaction witness",
        "the exact concatenated Ord tag-5 metadata bytes, including verified absence, are serialized in the same reveal envelope",
        "the tapscript/control block commits the envelope to the reveal input prevout",
        "the reveal txid and witness wtxid are committed into the declared Bitcoin block",
        "the block has 144 preserved valid-PoW descendants relative to the explicit checkpoint",
        "the reveal transaction pays its declared output to the recorded P2TR destination address",
    ]
    return write_proof_and_anchor(
        proof,
        record,
        output_dir,
        block_hash=str(old_anchor["block_reference"]["hash"]).lower(),
        block_timestamp=int(old_anchor["block_reference"]["timestamp"]),
    )


def capture_formation(record: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    txid = record["txid"]
    height = record["block_height"]
    checkpoint_height = height + CONFIRMATION_DEPTH
    print(f"capture formation {record['inscription_number']}: tx={txid} block={height}", flush=True)
    observations = legacy_capture.provider_observations(height, checkpoint_height)
    block_hash = observations[0]["target_hash"]
    known = record.get("known_block_hash")
    if known and block_hash != known:
        raise RuntimeError("known block hash differs from provider quorum")
    headers = legacy_capture.fetch_header_chain(height, checkpoint_height)
    target_header = parse_header(bytes.fromhex(headers[0]))
    checkpoint_header = parse_header(bytes.fromhex(headers[-1]))
    if target_header["hash"] != block_hash:
        raise RuntimeError("target header differs from provider quorum")
    if checkpoint_header["hash"] != observations[0]["checkpoint_hash"]:
        raise RuntimeError("checkpoint header differs from provider quorum")
    if height // 2016 != checkpoint_height // 2016:
        raise RuntimeError("v2 capture segment crosses a Bitcoin difficulty retarget boundary")

    raw_block = bytes(legacy_capture.fetch(f"{legacy_capture.PRIMARY}/block/{block_hash}/raw", binary=True))
    parsed_block = parse_block(raw_block)
    if parsed_block["header"].hex() != headers[0]:
        raise RuntimeError("raw block header differs from ancestry header")
    transactions = parsed_block["transactions"]
    txids = [item["txid"] for item in transactions]
    if merkle_root(txids) != target_header["merkle_root"]:
        raise RuntimeError("raw block transaction Merkle root mismatch")
    if txids.count(txid) != 1:
        raise RuntimeError("target reveal transaction is not unique in block")
    target_position = txids.index(txid)
    reveal = transactions[target_position]
    endpoint_reveal_hex, reveal_observations = legacy_capture.raw_tx_crosscheck(txid)
    if reveal["raw"].hex() != endpoint_reveal_hex:
        raise RuntimeError("raw block reveal differs from transaction endpoints")

    envelopes = extract_inscription_envelopes(reveal)
    if not envelopes or envelopes[0]["inscription_index"] != 0:
        raise RuntimeError("formation reveal has no txid+i0 envelope")
    envelope = envelopes[0]
    if not envelope["body_present"]:
        raise RuntimeError("formation inscription has no body separator")
    archived = archived_payload(record)
    body = envelope["body"]
    metadata = envelope_metadata(envelope)
    if body != archived["body"]:
        raise RuntimeError("formation reveal body differs from address-wide exact bytes")
    if metadata != archived["metadata"]:
        raise RuntimeError("formation reveal tag-5 metadata differs from address-wide exact CBOR bytes")

    prev_txid = reveal["inputs"][int(envelope["input_index"])]["prev_txid"]
    prevout_hex, prevout_observations = legacy_capture.raw_tx_crosscheck(prev_txid)
    prevout_tx = parse_transaction_hex(prevout_hex)
    taproot = verify_taproot_reveal_binding(reveal, envelope, prevout_tx)

    destination_outputs: list[int] = []
    for output in reveal["outputs"]:
        try:
            address = segwit_address(output["script_pubkey"])
        except ValueError:
            continue
        if address == record["destination_address"]:
            destination_outputs.append(int(output["index"]))
    if len(destination_outputs) != 1:
        raise RuntimeError("authority destination address is not unique in formation reveal outputs")
    destination_output_index = destination_outputs[0]

    coinbase = transactions[0]
    wtxids = ["00" * 32] + [item["wtxid"] for item in transactions[1:]]
    witness_root = merkle_root(wtxids)
    witness_result = verify_witness_commitment(witness_root, coinbase)
    commitment_record = witness_commitment(coinbase)

    proof = {
        "schema": "trinityaccord.bitcoin-inscription-proof-witness.v2",
        "network": "bitcoin-mainnet",
        "inscription": {
            "destination_output_index": destination_output_index
        },
        "reveal": {
            "transaction_hex": reveal["raw"].hex(),
            "txid": reveal["txid"],
            "wtxid": reveal["wtxid"],
            "input_index": int(envelope["input_index"]),
            "prevout_transaction_hex": prevout_hex,
            "prevout_txid": prev_txid,
            "taproot_binding": taproot,
            "provider_observations": reveal_observations,
            "prevout_provider_observations": prevout_observations,
        },
        "block_inclusion": {
            "height": height,
            "hash": block_hash,
            "header_hex": parsed_block["header"].hex(),
            "timestamp": target_header["timestamp"],
            "bits": target_header["bits"],
            "transaction_count": len(transactions),
            "target_transaction_position": target_position,
            "target_txid_merkle_branch": merkle_branch(txids, target_position),
            "coinbase_txid": coinbase["txid"],
            "coinbase_transaction_hex": coinbase["raw"].hex(),
            "coinbase_txid_merkle_branch": merkle_branch(txids, 0),
            "raw_block_bytes_at_capture": len(raw_block),
            "raw_block_sha256_at_capture": hashlib.sha256(raw_block).hexdigest(),
        },
        "witness_inclusion": {
            "target_wtxid": reveal["wtxid"],
            "target_wtxid_position": target_position,
            "target_wtxid_merkle_branch": merkle_branch(wtxids, target_position),
            "witness_root": witness_root,
            "coinbase_commitment": witness_result["coinbase_commitment"],
            "coinbase_reserved_value": witness_result["coinbase_reserved_value"],
            "coinbase_commitment_output_index": commitment_record["output_index"],
        },
        "pow_ancestry": {
            "target_height": height,
            "checkpoint_height": checkpoint_height,
            "descendant_confirmation_depth": CONFIRMATION_DEPTH,
            "checkpoint_hash": checkpoint_header["hash"],
            "headers_target_through_checkpoint": headers,
            "matching_provider_votes": 2,
            "checkpoint_observations": observations,
            "trust_model": "Explicit checkpoint-relative Bitcoin PoW ancestry. The preserved headers independently prove target inclusion plus 144 valid-PoW descendants. Provider observations are provenance only. This is not a full-node consensus validation and does not prove absence of a heavier competing chain from genesis.",
        },
        "claim_boundary": {
            "proves": [],
            "does_not_prove": [
                "full Bitcoin consensus validity from genesis",
                "absence of a heavier competing chain",
                "civil identity or authorship",
                "philosophical truth",
                "absolute physical-world time",
                "the global Ordinals inscription number without ordinal-theory index reconstruction"
            ]
        }
    }
    enrich_proof_inscription(proof, record, envelope, archived)
    proof["claim_boundary"]["proves"] = [
        "the exact inscription body is serialized in the reveal transaction witness",
        "the exact concatenated Ord tag-5 metadata bytes, including verified absence, are serialized in the same reveal envelope",
        "the tapscript/control block commits the envelope to the reveal input prevout",
        "the reveal txid and witness wtxid are committed into the declared Bitcoin block",
        "the block has 144 preserved valid-PoW descendants relative to the explicit checkpoint",
        "the reveal transaction pays its declared output to the recorded P2TR destination address"
    ]
    return write_proof_and_anchor(
        proof, record, output_dir, block_hash=block_hash, block_timestamp=int(target_header["timestamp"])
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ANNEX_DIR / "proof-material")
    parser.add_argument("--manifest", type=Path, default=ANNEX_DIR / "ANNEX-MANIFEST.json")
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    records = address_records()
    legacy_txids = {str(item["txid"]).lower() for item in load_json(V1_MANIFEST)["anchors"]}
    captured: list[dict[str, Any]] = []
    for record in records:
        if record["txid"] in legacy_txids:
            print(f"reuse v1 proof {record['inscription_number']}: {record['txid']}", flush=True)
            captured.append(upgrade_v1(record, output_dir))
        else:
            captured.append(capture_formation(record, output_dir))

    if len(captured) != 12:
        raise RuntimeError("v2 capture did not produce exactly 12 anchors")
    verifier = Path(__file__).with_name("verify_annex.py")
    primitives = V1_VERIFICATION / "bitcoin_proof_primitives_v1.py"
    manifest = {
        "schema": "trinityaccord.bitcoin-inscription-proof-carrying-annex.v2",
        "version": "2.0.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "created_from_git_commit": git_head(),
        "network": {"name": "Bitcoin Mainnet", "chain": "main", "bech32_hrp": "bc"},
        "authority_boundary": {
            "canonical_authority": "three Bitcoin Originals only",
            "canonical_original_count": 3,
            "formation_records_non_canonical": True,
            "post_canonical_inscriptions_non_amending": True,
            "proof_annex_is_non_amending": True,
            "no_authority_escalation": True
        },
        "claim_model": {
            "L1_INSCRIPTION_CONTENT_METADATA_AND_TAPROOT_BINDING": "PASS only when preserved reveal/prevout bytes recompute the declared identities; the txid+i0 Ord envelope yields the exact body, content type, and concatenated tag-5 CBOR metadata bytes (or proves tag-5 absence); the tapscript and BIP341 control block commit the envelope to the referenced P2TR prevout; the observed BIP342 script shape carries a valid BIP340 SIGHASH_DEFAULT signature; and the reveal destination address matches.",
            "L2_BLOCK_AND_WITNESS_INCLUSION": "PASS only when the reveal txid reconstructs the block-header transaction Merkle root and the reveal wtxid reconstructs the BIP141 witness root whose commitment is in a coinbase transaction independently proven into the same block header.",
            "L3_CHECKPOINT_RELATIVE_POW_ANCESTRY": "PASS only when the target block header and 144 descendants form a contiguous valid-PoW Bitcoin-mainnet header chain to an explicit checkpoint observed consistently by two providers.",
            "metadata_rule": "Ord tag-5 field values are concatenated in envelope order before comparison with the archived CBOR bytes.",
            "checkpoint_rule": "Provider observations are capture provenance only; ordinary verification is entirely offline and checkpoint-relative.",
            "time_rule": "Bitcoin header timestamps are consensus header fields, not absolute physical-world clocks."
        },
        "closed_set": {
            "inscription_count": 12,
            "pre_canonical_formation": 4,
            "canonical_originals": 3,
            "post_canonical_non_amending": 5,
            "source": "bitcoin-inscription-mirrors/address-wide/manifest.json + classification.json; legacy 3 + 5 authority bindings remain checked against archive/authority-manifest/authority.jcs.json"
        },
        "verification_implementation": {
            "verifier": str(verifier.relative_to(REPO_ROOT)),
            "verifier_sha256": sha256_file(verifier),
            "frozen_primitives": str(primitives.relative_to(REPO_ROOT)),
            "frozen_primitives_sha256": sha256_file(primitives),
            "runtime": "Python 3 standard library only",
            "network_required_for_verification": False,
            "network_required_for_controlled_capture": True,
            "legacy_v1_proof_bytes_reused_for_existing_eight": True
        },
        "preservation_policy": {
            "proof_material_git_tracked": True,
            "future_repository_capsule_coverage": "Included in the next authorized repository preservation capsule because every v2 annex byte is Git-tracked.",
            "v1_immutability": "The eight-item v1 annex remains unchanged as a historical proof checkpoint.",
            "runtime_self_containment": "Ordinary verification uses only checked-in Python standard-library code and proof bytes."
        },
        "anchors": captured,
        "does_not_prove": [
            "full Bitcoin consensus validity from genesis",
            "absence of a heavier competing chain",
            "civil identity or authorship",
            "philosophical truth",
            "absolute physical-world time",
            "that no inscription ever left the address before the first complete observation"
        ]
    }
    write_json(args.manifest, manifest)
    print(f"captured/upgraded {len(captured)} Bitcoin inscription proof witnesses for v2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
