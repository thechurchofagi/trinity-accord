#!/usr/bin/env python3
"""Controlled network capture for the four pre-canonical address-wide Bitcoin proofs.

The existing eight curated inscriptions keep their frozen v1 proof witnesses.
This capture adds proof witnesses only for the four previously omitted formation
records and builds a v2 manifest that composes 8 inherited v1 proofs + 4 new v2
proofs without changing canonical authority.
"""
from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ANNEX_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = ANNEX_DIR.parents[1]
V1_DIR = REPO_ROOT / "evidence/bitcoin-inscription-proof-annex-v1"
V1_VERIFICATION = V1_DIR / "verification"
sys.path.insert(0, str(V1_VERIFICATION))

from bitcoin_proof_primitives_v1 import (  # noqa: E402
    extract_inscription_envelopes,
    merkle_branch,
    merkle_root,
    parse_block,
    parse_header,
    parse_transaction_hex,
    segwit_address,
    sha256_file,
    verify_simple_inscription_tapscript_spend,
    verify_taproot_reveal_binding,
    verify_witness_commitment,
    witness_commitment,
)
from capture_proofs import (  # noqa: E402
    CONFIRMATION_DEPTH,
    PRIMARY,
    fetch,
    fetch_header_chain,
    provider_observations,
    raw_tx_crosscheck,
)

TARGETS = ANNEX_DIR / "TARGETS.json"
ADDRESS_ROOT = REPO_ROOT / "bitcoin-inscription-mirrors/address-wide"
ADDRESS_MANIFEST = ADDRESS_ROOT / "manifest.json"
V1_MANIFEST = V1_DIR / "ANNEX-MANIFEST.json"
PROOF_ROOT = ANNEX_DIR / "proof-material"
MANIFEST = ANNEX_DIR / "ANNEX-MANIFEST.json"
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
    ).strip()


def decode_b64(path: Path) -> bytes:
    return base64.b64decode(path.read_text(encoding="ascii").strip(), validate=True)


def address_objects() -> dict[str, dict[str, Any]]:
    manifest = load_json(ADDRESS_MANIFEST)
    if manifest.get("schema") != "trinityaccord.bitcoin-address-inscription-mirror.v2":
        raise ValueError("address-wide archive schema mismatch")
    if manifest.get("count") != 12 or len(manifest.get("ids", [])) != 12:
        raise ValueError("v2 proof capture requires the complete 12-item address snapshot")
    if not manifest.get("authority_boundary", {}).get("three_bitcoin_originals_remain_canonical"):
        raise ValueError("address archive lost canonical authority boundary")
    objects = {str(item["id"]): item for item in manifest.get("objects", [])}
    if set(objects) != set(manifest["ids"]):
        raise ValueError("address-wide object set mismatch")
    return objects


def target_records() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    config = load_json(TARGETS)
    boundary = config.get("authority_boundary", {})
    if boundary.get("canonical_authority_count") != 3:
        raise ValueError("canonical authority count must remain three")
    if not boundary.get("formation_targets_are_non_canonical"):
        raise ValueError("formation targets must remain non-canonical")
    canonical = set(config.get("canonical_original_ids", []))
    if len(canonical) != 3:
        raise ValueError("exactly three canonical ids are required")
    targets = config.get("formation_targets", [])
    if not isinstance(targets, list) or len(targets) != 4:
        raise ValueError("exactly four formation targets are required")
    ids = [str(item["ordinals_inscription_id"]) for item in targets]
    if len(set(ids)) != 4 or canonical.intersection(ids):
        raise ValueError("formation targets must be four unique non-canonical ids")
    for item in targets:
        if item.get("canonical") is not False or item.get("amends_canon") is not False:
            raise ValueError("formation target attempts authority escalation")
        if item.get("classification") != "pre_canonical_formation":
            raise ValueError("unexpected formation classification")
    return config, targets


def archive_payload(inscription_id: str, object_record: dict[str, Any]) -> tuple[bytes, bytes, dict[str, Any]]:
    obj = ADDRESS_ROOT / "objects" / inscription_id
    info = load_json(obj / "metadata.json")
    body = decode_b64(obj / "content.b64")
    metadata = decode_b64(obj / "inscription-metadata.cbor.b64")
    if info.get("id") != inscription_id:
        raise ValueError("archived recursive metadata id mismatch")
    if len(body) != int(object_record["content_length"]):
        raise ValueError("archived body length mismatch")
    if hashlib.sha256(body).hexdigest() != object_record["content_sha256"]:
        raise ValueError("archived body SHA-256 mismatch")
    if len(metadata) != int(object_record["inscription_metadata_length"]):
        raise ValueError("archived inscription metadata length mismatch")
    if hashlib.sha256(metadata).hexdigest() != object_record["inscription_metadata_sha256"]:
        raise ValueError("archived inscription metadata SHA-256 mismatch")
    if bool(metadata) != bool(object_record["inscription_metadata_present"]):
        raise ValueError("archived inscription metadata presence mismatch")
    return body, metadata, info


def capture_target(
    target: dict[str, Any], object_record: dict[str, Any]
) -> dict[str, Any]:
    inscription_id = str(target["ordinals_inscription_id"]).lower()
    if not inscription_id.endswith("i0") or len(inscription_id) != 66:
        raise ValueError("v2 formation proof requires stable txid+i0 identity")
    txid = inscription_id[:-2]
    expected_height = int(target["expected_height"])
    checkpoint_height = expected_height + CONFIRMATION_DEPTH
    body_archive, metadata_archive, recursive_info = archive_payload(inscription_id, object_record)

    if int(recursive_info["height"]) != expected_height:
        raise ValueError("target height differs from archived recursive metadata")
    if int(recursive_info["timestamp"]) != int(target["expected_timestamp"]):
        raise ValueError("target timestamp differs from archived recursive metadata")
    if str(recursive_info["address"]) != load_json(TARGETS)["authority_address"]:
        raise ValueError("target address differs from authority address")

    observations = provider_observations(expected_height, checkpoint_height)
    block_hash = observations[0]["target_hash"]
    headers = fetch_header_chain(expected_height, checkpoint_height)
    target_header = parse_header(bytes.fromhex(headers[0]))
    checkpoint_header = parse_header(bytes.fromhex(headers[-1]))
    if target_header["hash"] != block_hash:
        raise ValueError("target header differs from provider-agreed target block")
    if target_header["timestamp"] != int(target["expected_timestamp"]):
        raise ValueError("target block timestamp differs from archived timestamp")
    if checkpoint_header["hash"] != observations[0]["checkpoint_hash"]:
        raise ValueError("checkpoint header differs from provider quorum")
    if expected_height // 2016 != checkpoint_height // 2016:
        raise ValueError("v2 capture segment crosses a difficulty retarget boundary")

    raw_block = bytes(fetch(f"{PRIMARY}/block/{block_hash}/raw", binary=True))
    parsed_block = parse_block(raw_block)
    if parsed_block["header"].hex() != headers[0]:
        raise ValueError("raw block header differs from ancestry header")
    transactions = parsed_block["transactions"]
    txids = [item["txid"] for item in transactions]
    if merkle_root(txids) != target_header["merkle_root"]:
        raise ValueError("raw block transaction Merkle root mismatch")
    if txids.count(txid) != 1:
        raise ValueError("target reveal transaction is not unique in declared block")
    position = txids.index(txid)
    reveal = transactions[position]

    endpoint_reveal_hex, reveal_observations = raw_tx_crosscheck(txid)
    if reveal["raw"].hex() != endpoint_reveal_hex:
        raise ValueError("raw block reveal differs from transaction endpoints")

    envelopes = extract_inscription_envelopes(reveal)
    matching = [item for item in envelopes if int(item["inscription_index"]) == 0]
    if len(matching) != 1:
        raise ValueError("expected exactly one parsed inscription index 0 envelope")
    envelope = matching[0]
    if not envelope["body_present"]:
        raise ValueError("inscription body separator is missing")
    body = envelope["body"]
    metadata_parts = [value for tag, value in envelope["fields"] if tag == b"\x05"]
    metadata = b"".join(metadata_parts)
    if body != body_archive:
        raise ValueError("reveal witness body differs from exact address-wide archive")
    if metadata != metadata_archive:
        raise ValueError("reveal witness tag-5 metadata differs from exact address-wide archive")
    if envelope["content_type"].decode("utf-8") != str(object_record["content_type"]):
        raise ValueError("reveal content type differs from address-wide archive")

    input_index = int(envelope["input_index"])
    prev_txid = reveal["inputs"][input_index]["prev_txid"]
    prevout_hex, prevout_observations = raw_tx_crosscheck(prev_txid)
    prevout = parse_transaction_hex(prevout_hex)
    taproot = verify_taproot_reveal_binding(reveal, envelope, prevout)
    signature = verify_simple_inscription_tapscript_spend(reveal, envelope, prevout)

    expected_address = str(load_json(TARGETS)["authority_address"])
    address_outputs: list[int] = []
    for output in reveal["outputs"]:
        try:
            address = segwit_address(output["script_pubkey"])
        except ValueError:
            continue
        if address == expected_address:
            address_outputs.append(int(output["index"]))
    if len(address_outputs) != 1:
        raise ValueError("authority destination address is not unique in reveal outputs")
    destination_index = address_outputs[0]

    coinbase = transactions[0]
    wtxids = ["00" * 32] + [item["wtxid"] for item in transactions[1:]]
    witness_root = merkle_root(wtxids)
    witness_result = verify_witness_commitment(witness_root, coinbase)
    commitment_record = witness_commitment(coinbase)

    proof = {
        "schema": "trinityaccord.bitcoin-address-proof-witness.v2",
        "network": "bitcoin-mainnet",
        "inscription": {
            "ordinals_inscription_id": inscription_id,
            "inscription_index": 0,
            "classification": target["classification"],
            "role": target["role"],
            "title": target["title"],
            "canonical": False,
            "amends_canon": False,
            "expected_destination_address": expected_address,
            "destination_output_index": destination_index,
            "content_type_hex": envelope["content_type"].hex(),
            "content_type_utf8": envelope["content_type"].decode("utf-8"),
            "body_bytes": len(body),
            "body_sha256": hashlib.sha256(body).hexdigest(),
            "archive_body_path": str((ADDRESS_ROOT / "objects" / inscription_id / "content.b64").relative_to(REPO_ROOT)),
            "metadata_field_tag_hex": "05",
            "metadata_field_count": len(metadata_parts),
            "metadata_present": bool(metadata),
            "metadata_bytes": len(metadata),
            "metadata_sha256": hashlib.sha256(metadata).hexdigest(),
            "archive_metadata_path": str((ADDRESS_ROOT / "objects" / inscription_id / "inscription-metadata.cbor.b64").relative_to(REPO_ROOT)),
            "metadata_binding_method": "ordered_concatenation_of_all_ordinals_tag_5_fields_exact_bytes",
        },
        "reveal": {
            "transaction_hex": reveal["raw"].hex(),
            "txid": reveal["txid"],
            "wtxid": reveal["wtxid"],
            "input_index": input_index,
            "prevout_transaction_hex": prevout_hex,
            "prevout_txid": prev_txid,
            "taproot_binding": taproot,
            "tapscript_signature": signature,
            "provider_observations": reveal_observations,
            "prevout_provider_observations": prevout_observations,
        },
        "block_inclusion": {
            "height": expected_height,
            "hash": block_hash,
            "header_hex": parsed_block["header"].hex(),
            "timestamp": target_header["timestamp"],
            "bits": target_header["bits"],
            "transaction_count": len(transactions),
            "target_transaction_position": position,
            "target_txid_merkle_branch": merkle_branch(txids, position),
            "coinbase_txid": coinbase["txid"],
            "coinbase_transaction_hex": coinbase["raw"].hex(),
            "coinbase_txid_merkle_branch": merkle_branch(txids, 0),
            "raw_block_bytes_at_capture": len(raw_block),
            "raw_block_sha256_at_capture": hashlib.sha256(raw_block).hexdigest(),
        },
        "witness_inclusion": {
            "target_wtxid": reveal["wtxid"],
            "target_wtxid_position": position,
            "target_wtxid_merkle_branch": merkle_branch(wtxids, position),
            "witness_root": witness_root,
            "coinbase_commitment": witness_result["coinbase_commitment"],
            "coinbase_reserved_value": witness_result["coinbase_reserved_value"],
            "coinbase_commitment_output_index": commitment_record["output_index"],
        },
        "pow_ancestry": {
            "target_height": expected_height,
            "checkpoint_height": checkpoint_height,
            "descendant_confirmation_depth": CONFIRMATION_DEPTH,
            "checkpoint_hash": checkpoint_header["hash"],
            "headers_target_through_checkpoint": headers,
            "matching_provider_votes": 2,
            "checkpoint_observations": observations,
            "trust_model": "Explicit checkpoint-relative Bitcoin PoW ancestry. The preserved headers independently prove target inclusion plus 144 valid-PoW descendants. Provider observations are provenance only. This is not a full-node consensus validation and does not prove absence of a heavier competing chain from genesis.",
        },
        "claim_boundary": {
            "proves": [
                "the exact inscription body is serialized in the reveal witness",
                "the exact ordered tag-5 metadata bytes, including explicit absence, are derived from the same reveal witness",
                "the tapscript/control block commits the inscription envelope to the reveal input prevout",
                "the reveal tapscript spend has a valid BIP340 SIGHASH_DEFAULT signature under the supported v1 script shape",
                "the reveal txid and wtxid are committed into the declared Bitcoin block",
                "the block has 144 preserved valid-PoW descendants relative to the explicit checkpoint",
                "the reveal transaction pays its declared output to the authority P2TR address",
            ],
            "does_not_prove": [
                "full Bitcoin consensus validity from genesis",
                "absence of a heavier competing chain",
                "canonical status merely because the inscription shares an address or has a proof",
                "that decoded metadata derivatives are more authoritative than the exact CBOR bytes",
            ],
        },
    }

    out = PROOF_ROOT / txid / "proof-witness.json"
    write_json(out, proof)
    return {
        "ordinals_inscription_id": inscription_id,
        "txid": txid,
        "wtxid": reveal["wtxid"],
        "classification": target["classification"],
        "role": target["role"],
        "title": target["title"],
        "canonical": False,
        "amends_canon": False,
        "destination_address": expected_address,
        "destination_output_index": destination_index,
        "block_reference": {
            "height": expected_height,
            "hash": block_hash,
            "timestamp": target_header["timestamp"],
        },
        "content": {
            "content_type_hex": envelope["content_type"].hex(),
            "content_type_utf8": envelope["content_type"].decode("utf-8"),
            "body_bytes": len(body),
            "body_sha256": hashlib.sha256(body).hexdigest(),
            "archive_body_path": proof["inscription"]["archive_body_path"],
            "binding_method": "exact_bytes_from_reveal_witness",
        },
        "inscription_metadata": {
            "present": bool(metadata),
            "field_tag_hex": "05",
            "field_count": len(metadata_parts),
            "bytes": len(metadata),
            "sha256": hashlib.sha256(metadata).hexdigest(),
            "archive_metadata_path": proof["inscription"]["archive_metadata_path"],
            "binding_method": "ordered_concatenation_of_all_ordinals_tag_5_fields_exact_bytes",
        },
        "proof_status": {
            "L1_INSCRIPTION_CONTENT_METADATA_AND_TAPROOT_BINDING": "PASS",
            "L2_BLOCK_AND_WITNESS_INCLUSION": "PASS",
            "L3_CHECKPOINT_RELATIVE_POW_ANCESTRY": "PASS",
        },
        "proof_material": {
            "path": str(out.relative_to(REPO_ROOT)),
            "size": out.stat().st_size,
            "sha256": sha256_file(out),
        },
    }


def inherited_v1_anchors(v1: dict[str, Any]) -> list[dict[str, Any]]:
    output = []
    for anchor in v1.get("anchors", []):
        output.append(
            {
                "ordinals_inscription_id": anchor["ordinals_inscription_id"],
                "txid": anchor["txid"],
                "classification": anchor["classification"],
                "title": anchor["title"],
                "canonical": anchor["classification"] == "canonical_original",
                "amends_canon": False,
                "block_reference": anchor["block_reference"],
                "content": anchor["content"],
                "proof_status": anchor["proof_status"],
                "proof_source": "inherited_frozen_v1",
                "proof_material": anchor["proof_material"],
            }
        )
    return output


def build_manifest(new_anchors: list[dict[str, Any]], config: dict[str, Any]) -> dict[str, Any]:
    v1 = load_json(V1_MANIFEST)
    inherited = inherited_v1_anchors(v1)
    if len(inherited) != 8:
        raise ValueError("frozen v1 annex must contribute exactly eight anchors")
    all_anchors = inherited + [{**item, "proof_source": "captured_v2"} for item in new_anchors]
    all_anchors.sort(key=lambda item: (int(item["block_reference"]["height"]), item["ordinals_inscription_id"]))
    current_ids = set(load_json(ADDRESS_MANIFEST)["ids"])
    if {item["ordinals_inscription_id"] for item in all_anchors} != current_ids:
        raise ValueError("composed v2 proof set does not equal the 12-item address snapshot")

    return {
        "schema": "trinityaccord.bitcoin-address-proof-carrying-annex.v2",
        "version": "2.0.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "created_from_git_commit": git_head(),
        "network": "bitcoin-mainnet",
        "authority_boundary": {
            "canonical_authority": "three Bitcoin Originals only",
            "canonical_original_ids": config["canonical_original_ids"],
            "canonical_original_count": 3,
            "formation_records_are_non_canonical": True,
            "post_canonical_records_are_non_amending": True,
            "proof_inclusion_does_not_confer_authority": True,
            "same_address_does_not_imply_canonical": True,
            "no_authority_escalation": True,
        },
        "coverage": {
            "address_snapshot_count": 12,
            "inherited_v1_proofs": 8,
            "new_v2_formation_proofs": 4,
            "canonical_originals": 3,
            "pre_canonical_formation": 4,
            "post_canonical_non_amending": 5,
            "metadata_witness_binding_count": 12,
            "metadata_present_count": 1,
            "metadata_absence_proved_count": 11,
        },
        "claim_model": {
            "L1_INSCRIPTION_CONTENT_METADATA_AND_TAPROOT_BINDING": "For all 12 stable inscription IDs, body bytes are tied to reveal witnesses and tag-5 CBOR metadata is reconstructed from the same Ordinals envelope; for the single metadata-bearing image the exact 2,941 CBOR bytes are bound, while the other 11 prove tag-5 absence. Existing eight body/Taproot/signature proofs remain frozen v1; four formation records receive equivalent v2 proofs.",
            "L2_BLOCK_AND_WITNESS_INCLUSION": "Reveal txid Merkle inclusion plus reveal wtxid BIP141 witness commitment into the same Bitcoin block.",
            "L3_CHECKPOINT_RELATIVE_POW_ANCESTRY": "Target header plus 144 contiguous valid-PoW descendants to an explicit two-provider observed checkpoint, with the same checkpoint-relative limitations as v1.",
        },
        "inheritance": {
            "v1_manifest_path": str(V1_MANIFEST.relative_to(REPO_ROOT)),
            "v1_manifest_size": V1_MANIFEST.stat().st_size,
            "v1_manifest_sha256": sha256_file(V1_MANIFEST),
            "v1_verifier_path": "evidence/bitcoin-inscription-proof-annex-v1/verification/verify_annex.py",
            "v1_proof_count": 8,
        },
        "address_archive_binding": {
            "manifest_path": str(ADDRESS_MANIFEST.relative_to(REPO_ROOT)),
            "manifest_size": ADDRESS_MANIFEST.stat().st_size,
            "manifest_sha256": sha256_file(ADDRESS_MANIFEST),
            "stable_id_count": 12,
        },
        "anchors": all_anchors,
    }


def main() -> int:
    config, targets = target_records()
    objects = address_objects()
    new_anchors = []
    for index, target in enumerate(targets, start=1):
        inscription_id = str(target["ordinals_inscription_id"])
        if inscription_id not in objects:
            raise ValueError(f"formation target missing from address archive: {inscription_id}")
        print(f"[{index}/4] capture {inscription_id}", flush=True)
        new_anchors.append(capture_target(target, objects[inscription_id]))
    manifest = build_manifest(new_anchors, config)
    write_json(MANIFEST, manifest)
    print("captured four v2 formation proofs; composed 12-item manifest", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
