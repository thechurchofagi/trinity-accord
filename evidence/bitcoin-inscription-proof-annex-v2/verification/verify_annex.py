#!/usr/bin/env python3
"""Fail-closed, network-free verifier for the 12-item Bitcoin inscription annex v2."""
from __future__ import annotations

import base64
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ANNEX_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = ANNEX_DIR.parents[1]
V1_DIR = ANNEX_DIR.parent / "bitcoin-inscription-proof-annex-v1"
V1_VERIFICATION = V1_DIR / "verification"
sys.path.insert(0, str(V1_VERIFICATION))

import verify_annex as legacy_verify  # noqa: E402
from bitcoin_proof_primitives_v1 import (  # noqa: E402
    extract_inscription_envelopes,
    parse_transaction_hex,
    segwit_address,
    sha256_file,
    verify_simple_inscription_tapscript_spend,
    verify_taproot_reveal_binding,
)

MANIFEST = ANNEX_DIR / "ANNEX-MANIFEST.json"
ADDRESS_ROOT = REPO_ROOT / "bitcoin-inscription-mirrors/address-wide"
ADDRESS_MANIFEST = ADDRESS_ROOT / "manifest.json"
CLASSIFICATION = ADDRESS_ROOT / "classification.json"
AUTHORITY = REPO_ROOT / "archive/authority-manifest/authority.jcs.json"
EXPECTED_COUNT = 12
EXPECTED_FORMATION = 4
EXPECTED_CANONICAL = 3
EXPECTED_POST = 5
EXPECTED_CONFIRMATION_DEPTH = 144


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_equal(value: Any, expected: Any, field: str) -> None:
    if value != expected:
        raise ValueError(f"{field} mismatch")


def source_records() -> dict[str, dict[str, Any]]:
    address = load_json(ADDRESS_MANIFEST)
    classification = load_json(CLASSIFICATION)
    if address.get("schema") != "trinityaccord.bitcoin-address-inscription-mirror.v2":
        raise ValueError("address-wide mirror must be v2")
    if address.get("count") != EXPECTED_COUNT or len(address.get("ids", [])) != EXPECTED_COUNT:
        raise ValueError("address-wide mirror is not the exact 12-item set")
    expected_counts = {
        "current_address_snapshot": 12,
        "pre_canonical_formation": 4,
        "canonical_originals": 3,
        "post_canonical_non_amending": 5,
    }
    if classification.get("counts") != expected_counts:
        raise ValueError("historical classification is not 4 + 3 + 5")

    objects = {str(item["id"]): item for item in address["objects"]}
    classes = {
        str(item["ordinals_inscription_id"]): item
        for item in classification.get("records", [])
    }
    ids = [str(item) for item in address["ids"]]
    if set(ids) != set(objects) or set(ids) != set(classes):
        raise ValueError("address/classification ID set mismatch")

    bitcoin = load_json(AUTHORITY)["bitcoin"]
    legacy_by_txid: dict[str, dict[str, Any]] = {}
    for proof_classification, records in (
        ("canonical_original", bitcoin["originals"]),
        ("non_amending_ancillary", bitcoin["ancillary"]),
    ):
        for item in records:
            txid = str(item["txid"]).lower()
            legacy_by_txid[txid] = {**item, "_proof_classification": proof_classification}
    if len(legacy_by_txid) != 8:
        raise ValueError("legacy 3 + 5 authority binding changed")

    out: dict[str, dict[str, Any]] = {}
    layer_counts = {"pre_canonical_formation": 0, "canonical_original": 0, "post_canonical_non_amending": 0}
    for inscription_id in ids:
        if not inscription_id.endswith("i0") or len(inscription_id) != 66:
            raise ValueError("v2 closed set requires txid+i0 identities")
        txid = inscription_id[:-2]
        cls = classes[inscription_id]
        layer = str(cls.get("layer"))
        if cls.get("amends_canon") is not False:
            raise ValueError("classification amendment boundary changed")
        if cls.get("canonical") is True:
            proof_classification = "canonical_original"
            layer_counts["canonical_original"] += 1
        elif layer == "pre_canonical_formation":
            proof_classification = "pre_canonical_formation"
            layer_counts["pre_canonical_formation"] += 1
        elif layer == "post_canonical_non_amending":
            proof_classification = "non_amending_ancillary"
            layer_counts["post_canonical_non_amending"] += 1
        else:
            raise ValueError("unsupported historical layer")

        metadata = load_json(ADDRESS_ROOT / "objects" / inscription_id / "metadata.json")
        require_equal(metadata.get("id"), inscription_id, "address metadata id")
        require_equal(metadata.get("address"), address["address"], "address metadata address")
        known = legacy_by_txid.get(txid)
        if proof_classification == "pre_canonical_formation":
            if known is not None:
                raise ValueError("formation record unexpectedly appears in legacy authority set")
        else:
            if known is None:
                raise ValueError("legacy authority binding missing")
            require_equal(known["_proof_classification"], proof_classification, "legacy proof classification")
            require_equal(int(known["inscription_id"]), int(metadata["number"]), "legacy inscription number")
            require_equal(int(known["block_height"]), int(metadata["height"]), "legacy block height")

        out[str(metadata["number"])] = {
            "inscription_number": str(metadata["number"]),
            "ordinals_inscription_id": inscription_id,
            "txid": txid,
            "block_height": int(metadata["height"]),
            "known_block_hash": str(known["block_hash"]).lower() if known else None,
            "classification": proof_classification,
            "historical_layer": layer,
            "canonical": cls.get("canonical") is True,
            "title": cls.get("title"),
            "object": objects[inscription_id],
            "object_dir": ADDRESS_ROOT / "objects" / inscription_id,
            "destination_address": str(address["address"]).lower(),
        }
    if len(out) != 12 or layer_counts != {
        "pre_canonical_formation": 4,
        "canonical_original": 3,
        "post_canonical_non_amending": 5,
    }:
        raise ValueError("source closed set is not exactly 4 + 3 + 5")
    return out


def bound_proof(anchor: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    txid = str(anchor["txid"]).lower()
    expected = f"evidence/bitcoin-inscription-proof-annex-v2/proof-material/{txid}/proof-witness.json"
    binding = anchor.get("proof_material")
    if not isinstance(binding, dict) or binding.get("path") != expected:
        raise ValueError("unexpected or missing v2 proof-material path binding")
    path = REPO_ROOT / expected
    if not path.is_file():
        raise ValueError("v2 proof-material file is missing")
    size = path.stat().st_size
    digest = sha256_file(path)
    require_equal(size, binding.get("size"), "proof-material size")
    require_equal(digest, binding.get("sha256"), "proof-material SHA-256")
    return path, {"path": expected, "size": size, "sha256": digest, "status": "PASS"}


def decode_archive(path: Path) -> bytes:
    try:
        return base64.b64decode(path.read_text(encoding="ascii").strip(), validate=True)
    except Exception as exc:
        raise ValueError(f"invalid base64 archive: {path}") from exc


def envelope_metadata(envelope: dict[str, Any]) -> bytes:
    return b"".join(value for tag, value in envelope["fields"] if tag == b"\x05")


def verify_l1(anchor: dict[str, Any], proof: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    declared = proof.get("inscription")
    reveal_record = proof.get("reveal")
    if not isinstance(declared, dict) or not isinstance(reveal_record, dict):
        raise ValueError("proof inscription/reveal objects are missing")

    txid = str(anchor["txid"]).lower()
    inscription_number = str(anchor["inscription_number"])
    require_equal(proof.get("schema"), "trinityaccord.bitcoin-inscription-proof-witness.v2", "proof schema")
    require_equal(proof.get("network"), "bitcoin-mainnet", "proof network")
    require_equal(declared.get("inscription_number"), inscription_number, "inscription number")
    require_equal(declared.get("ordinals_inscription_id"), f"{txid}i0", "txid+i0 identity")
    require_equal(declared.get("ordinals_inscription_id"), source["ordinals_inscription_id"], "source inscription identity")
    require_equal(declared.get("inscription_index"), 0, "inscription index")
    require_equal(declared.get("classification"), source["classification"], "classification")
    require_equal(declared.get("historical_layer"), source["historical_layer"], "historical layer")
    require_equal(declared.get("expected_destination_address"), source["destination_address"], "destination address")

    reveal = parse_transaction_hex(reveal_record["transaction_hex"])
    require_equal(reveal["txid"], txid, "recomputed reveal txid")
    require_equal(reveal["wtxid"], str(anchor["wtxid"]).lower(), "recomputed reveal wtxid")
    require_equal(reveal_record.get("txid"), reveal["txid"], "proof reveal txid")
    require_equal(reveal_record.get("wtxid"), reveal["wtxid"], "proof reveal wtxid")

    envelopes = extract_inscription_envelopes(reveal)
    if not envelopes:
        raise ValueError("no Ord inscription envelope in reveal witness")
    envelope = envelopes[0]
    require_equal(envelope["inscription_index"], 0, "parsed inscription index")
    require_equal(envelope["input_index"], reveal_record.get("input_index"), "inscription input index")
    if not envelope["body_present"]:
        raise ValueError("inscription body separator is missing")

    content_type_hex = envelope["content_type"].hex()
    try:
        content_type_utf8 = envelope["content_type"].decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("inscription content type is not UTF-8") from exc
    require_equal(content_type_hex, declared.get("content_type_hex"), "content-type bytes")
    require_equal(content_type_hex, anchor["content"]["content_type_hex"], "manifest content-type bytes")
    require_equal(content_type_utf8, declared.get("content_type_utf8"), "content-type text")
    require_equal(content_type_utf8, anchor["content"]["content_type_utf8"], "manifest content-type text")
    require_equal(content_type_utf8, source["object"].get("content_type"), "address-wide content type")

    body = envelope["body"]
    body_sha = hashlib.sha256(body).hexdigest()
    body_archive_path = source["object_dir"] / "content.b64"
    archived_body = decode_archive(body_archive_path)
    if body != archived_body:
        raise ValueError("exact address-wide body archive differs from reveal envelope")
    require_equal(len(body), source["object"]["content_length"], "address-wide body size")
    require_equal(body_sha, source["object"]["content_sha256"], "address-wide body SHA-256")
    require_equal(len(body), declared.get("body_bytes"), "proof body size")
    require_equal(body_sha, declared.get("body_sha256"), "proof body SHA-256")
    require_equal(len(body), anchor["content"]["body_bytes"], "manifest body size")
    require_equal(body_sha, anchor["content"]["body_sha256"], "manifest body SHA-256")
    require_equal(anchor["content"].get("mirror_encoding"), "base64_of_exact_body_bytes", "body mirror encoding")
    require_equal(anchor["content"].get("mirror_binding_method"), "exact_bytes", "body binding method")
    require_equal(declared.get("mirror_binding_method"), "exact_bytes", "proof body binding method")
    require_equal(declared.get("mirror_path"), str(body_archive_path.relative_to(REPO_ROOT)), "body mirror path")

    metadata = envelope_metadata(envelope)
    metadata_sha = hashlib.sha256(metadata).hexdigest()
    metadata_archive_path = source["object_dir"] / "inscription-metadata.cbor.b64"
    archived_metadata = decode_archive(metadata_archive_path)
    if metadata != archived_metadata:
        raise ValueError("exact address-wide tag-5 CBOR archive differs from reveal envelope")
    expected_meta = source["object"]
    require_equal(bool(metadata), expected_meta["inscription_metadata_present"], "metadata presence")
    require_equal(len(metadata), expected_meta["inscription_metadata_length"], "metadata length")
    require_equal(metadata_sha, expected_meta["inscription_metadata_sha256"], "metadata SHA-256")
    anchor_meta = anchor.get("inscription_metadata")
    if not isinstance(anchor_meta, dict):
        raise ValueError("manifest inscription_metadata binding is missing")
    require_equal(anchor_meta.get("tag"), 5, "metadata tag")
    require_equal(anchor_meta.get("present"), bool(metadata), "manifest metadata presence")
    require_equal(anchor_meta.get("bytes"), len(metadata), "manifest metadata length")
    require_equal(anchor_meta.get("sha256"), metadata_sha, "manifest metadata SHA-256")
    require_equal(anchor_meta.get("mirror_path"), str(metadata_archive_path.relative_to(REPO_ROOT)), "metadata mirror path")
    require_equal(anchor_meta.get("mirror_encoding"), "base64_of_exact_concatenated_tag5_cbor_bytes", "metadata mirror encoding")
    require_equal(anchor_meta.get("binding_method"), "exact_bytes", "metadata binding method")
    require_equal(declared.get("inscription_metadata_present"), bool(metadata), "proof metadata presence")
    require_equal(declared.get("inscription_metadata_bytes"), len(metadata), "proof metadata length")
    require_equal(declared.get("inscription_metadata_sha256"), metadata_sha, "proof metadata SHA-256")

    prevout = parse_transaction_hex(reveal_record["prevout_transaction_hex"])
    require_equal(prevout["txid"], reveal_record.get("prevout_txid"), "prevout transaction id")
    taproot = verify_taproot_reveal_binding(reveal, envelope, prevout)
    require_equal(taproot, reveal_record.get("taproot_binding"), "Taproot reveal binding")
    signature = verify_simple_inscription_tapscript_spend(reveal, envelope, prevout)

    destination_index = int(anchor["destination_output_index"])
    require_equal(destination_index, declared.get("destination_output_index"), "destination output index")
    if destination_index < 0 or destination_index >= len(reveal["outputs"]):
        raise ValueError("destination output index is invalid")
    address = segwit_address(reveal["outputs"][destination_index]["script_pubkey"])
    require_equal(address, source["destination_address"], "recomputed destination address")

    return {
        "inscription_number": inscription_number,
        "ordinals_inscription_id": source["ordinals_inscription_id"],
        "txid": txid,
        "wtxid": reveal["wtxid"],
        "classification": source["classification"],
        "historical_layer": source["historical_layer"],
        "status": "PASS",
        "body_bytes": len(body),
        "body_sha256": body_sha,
        "content_type": content_type_utf8,
        "inscription_metadata_present": bool(metadata),
        "inscription_metadata_bytes": len(metadata),
        "inscription_metadata_sha256": metadata_sha,
        "destination_address": address,
        "taproot_prevout_txid": taproot["prevout_txid"],
        "tapleaf_hash": taproot["tapleaf_hash"],
        "tapscript_signature_status": signature["signature_status"],
        "tapscript_public_key": signature["tapscript_public_key"],
        "taproot_sighash": signature["taproot_sighash"],
    }


def main() -> int:
    failures: list[str] = []
    proof_byte_checks: list[dict[str, Any]] = []
    l1_checks: list[dict[str, Any]] = []
    l2_checks: list[dict[str, Any]] = []
    l3_checks: list[dict[str, Any]] = []
    try:
        manifest = load_json(MANIFEST)
    except Exception as exc:
        print(json.dumps({"result": "FAIL", "failures": [f"manifest parse: {exc}"]}, indent=2))
        return 1

    if manifest.get("schema") != "trinityaccord.bitcoin-inscription-proof-carrying-annex.v2":
        failures.append("unexpected manifest schema")
    if manifest.get("network", {}).get("name") != "Bitcoin Mainnet":
        failures.append("network must be Bitcoin Mainnet")
    boundary = manifest.get("authority_boundary", {})
    if boundary.get("canonical_authority") != "three Bitcoin Originals only":
        failures.append("canonical authority boundary changed")
    if boundary.get("canonical_original_count") != 3:
        failures.append("canonical original count must remain 3")
    if boundary.get("formation_records_non_canonical") is not True:
        failures.append("formation records must remain non-canonical")
    if boundary.get("post_canonical_inscriptions_non_amending") is not True:
        failures.append("post-canonical records must remain non-amending")
    if boundary.get("proof_annex_is_non_amending") is not True or boundary.get("no_authority_escalation") is not True:
        failures.append("proof annex non-amending boundary changed")

    closed = manifest.get("closed_set", {})
    expected_closed = {
        "inscription_count": 12,
        "pre_canonical_formation": 4,
        "canonical_originals": 3,
        "post_canonical_non_amending": 5,
    }
    for key, value in expected_closed.items():
        if closed.get(key) != value:
            failures.append(f"closed_set {key} mismatch")

    implementation = manifest.get("verification_implementation", {})
    expected_impl = {
        "verifier": "evidence/bitcoin-inscription-proof-annex-v2/verification/verify_annex.py",
        "frozen_primitives": "evidence/bitcoin-inscription-proof-annex-v1/verification/bitcoin_proof_primitives_v1.py",
    }
    for key, expected_path in expected_impl.items():
        if implementation.get(key) != expected_path:
            failures.append(f"{key} path binding mismatch")
            continue
        path = REPO_ROOT / expected_path
        digest_field = "verifier_sha256" if key == "verifier" else "frozen_primitives_sha256"
        if not path.is_file() or sha256_file(path) != implementation.get(digest_field):
            failures.append(f"{key} SHA-256 binding mismatch")
    if implementation.get("network_required_for_verification") is not False:
        failures.append("ordinary verification must be network-free")
    if implementation.get("runtime") != "Python 3 standard library only":
        failures.append("unexpected verifier runtime boundary")

    try:
        sources = source_records()
    except Exception as exc:
        failures.append(f"source closed set: {exc}")
        sources = {}

    anchors = manifest.get("anchors")
    if not isinstance(anchors, list):
        failures.append("manifest anchors are missing")
        anchors = []
    ids = {str(anchor.get("inscription_number")) for anchor in anchors}
    txids = [str(anchor.get("txid", "")).lower() for anchor in anchors]
    if len(anchors) != 12 or ids != set(sources):
        failures.append("manifest must contain the exact 12-item source set")
    if len(txids) != len(set(txids)):
        failures.append("duplicate reveal txid")

    for anchor in anchors:
        inscription = str(anchor.get("inscription_number"))
        txid = str(anchor.get("txid", "")).lower()
        try:
            source = sources.get(inscription)
            if source is None:
                raise ValueError("inscription is absent from source set")
            require_equal(txid, source["txid"], "source txid")
            require_equal(anchor.get("ordinals_inscription_id"), source["ordinals_inscription_id"], "source Ordinals ID")
            require_equal(anchor.get("classification"), source["classification"], "source classification")
            require_equal(anchor.get("historical_layer"), source["historical_layer"], "source historical layer")
            require_equal(anchor["block_reference"]["height"], source["block_height"], "source block height")
            if source["known_block_hash"] is not None:
                require_equal(anchor["block_reference"]["hash"], source["known_block_hash"], "legacy authority block hash")
            for level in (
                "L1_INSCRIPTION_CONTENT_METADATA_AND_TAPROOT_BINDING",
                "L2_BLOCK_AND_WITNESS_INCLUSION",
                "L3_CHECKPOINT_RELATIVE_POW_ANCESTRY",
            ):
                if anchor.get("proof_status", {}).get(level) != "PASS":
                    raise ValueError(f"manifest does not declare {level} PASS")

            proof_path, byte_check = bound_proof(anchor)
            proof_byte_checks.append({"inscription_number": inscription, "txid": txid, **byte_check})
            proof = load_json(proof_path)
            l1 = verify_l1(anchor, proof, source)
            l1_checks.append(l1)
            l2 = legacy_verify.verify_l2(anchor, proof, l1)
            l2_checks.append(l2)
            l3 = legacy_verify.verify_l3(anchor, proof, l2)
            l3_checks.append(l3)
        except Exception as exc:
            failures.append(f"{inscription or txid}: {exc}")

    formation_l1 = sum(item["classification"] == "pre_canonical_formation" for item in l1_checks)
    canonical_l1 = sum(item["classification"] == "canonical_original" for item in l1_checks)
    post_l1 = sum(item["classification"] == "non_amending_ancillary" for item in l1_checks)
    complete = (
        len(l1_checks) == 12
        and len(l2_checks) == 12
        and len(l3_checks) == 12
        and (formation_l1, canonical_l1, post_l1) == (4, 3, 5)
        and not failures
    )
    result = "PASS" if complete else "FAIL"
    report = {
        "schema": "trinityaccord.bitcoin-inscription-annex-offline-verification.v2",
        "result": result,
        "L1_INSCRIPTION_CONTENT_METADATA_AND_TAPROOT_BINDING": {
            "status": "PASS" if complete else "FAIL",
            "inscriptions": len(l1_checks),
            "pre_canonical_formation": formation_l1,
            "canonical_originals": canonical_l1,
            "post_canonical_non_amending": post_l1,
            "tag5_metadata_present": sum(item["inscription_metadata_present"] for item in l1_checks),
            "tag5_metadata_absent_verified": sum(not item["inscription_metadata_present"] for item in l1_checks),
        },
        "L2_BLOCK_AND_WITNESS_INCLUSION": {
            "status": "PASS" if complete else "FAIL",
            "reveal_transactions": len(l2_checks),
            "txid_merkle_proofs": len(l2_checks),
            "bip141_witness_commitment_proofs": len(l2_checks),
        },
        "L3_CHECKPOINT_RELATIVE_POW_ANCESTRY": {
            "status": "PASS" if complete else "FAIL",
            "anchors": len(l3_checks),
            "descendant_confirmation_depth_per_anchor": EXPECTED_CONFIRMATION_DEPTH,
            "valid_pow_headers": sum(item["valid_pow_headers"] for item in l3_checks),
        },
        "proof_byte_checks": proof_byte_checks,
        "l1_checks": l1_checks,
        "l2_checks": l2_checks,
        "l3_checks": l3_checks,
        "failures": failures,
        "claim_boundary": "PASS proves the exact Ord envelope body and concatenated tag-5 metadata bytes (or tag-5 absence), BIP341 tapscript-to-prevout binding, the observed BIP342 script shape and BIP340 Schnorr spend signature, reveal txid inclusion, BIP141 witness inclusion, and 144-block checkpoint-relative valid-PoW ancestry for the 12-item 2026-08-14 current-address snapshot. It does not make the four formation records canonical, does not amend the three Bitcoin Originals, is not full-node validation from genesis, does not prove absence of a heavier chain, and does not prove that no inscription ever left the address before the first complete observation.",
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
