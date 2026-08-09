#!/usr/bin/env python3
"""Fail-closed, network-free verifier for Bitcoin inscription proof annex v1."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from bitcoin_proof_primitives_v1 import (
    canonicalize_text_bytes,
    extract_inscription_envelopes,
    parse_header,
    parse_transaction_hex,
    segwit_address,
    sha256_file,
    verify_header_pow,
    verify_merkle_branch,
    verify_simple_inscription_tapscript_spend,
    verify_taproot_reveal_binding,
    verify_witness_commitment,
)


ANNEX_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = ANNEX_DIR.parents[1]
MANIFEST = ANNEX_DIR / "ANNEX-MANIFEST.json"
AUTHORITY = REPO_ROOT / "archive/authority-manifest/authority.jcs.json"
EXPECTED_INSCRIPTIONS = {
    "97631551",
    "98369145",
    "98387475",
    "100385359",
    "100550942",
    "100751953",
    "103034280",
    "103635270",
}
CANONICAL_INSCRIPTIONS = {"97631551", "98369145", "98387475"}
EXPECTED_CONFIRMATION_DEPTH = 144


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def authority_closed_set() -> dict[str, dict[str, Any]]:
    data = load_json(AUTHORITY)["bitcoin"]
    output: dict[str, dict[str, Any]] = {}
    for classification, records in [
        ("canonical_original", data["originals"]),
        ("non_amending_ancillary", data["ancillary"]),
    ]:
        for record in records:
            inscription = str(record["inscription_id"])
            if inscription in output:
                raise ValueError("duplicate authority inscription id")
            output[inscription] = {**record, "classification": classification}
    if set(output) != EXPECTED_INSCRIPTIONS:
        raise ValueError("authority inscription closed set mismatch")
    return output


def bound_proof(anchor: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    txid = str(anchor["txid"]).lower()
    expected = f"evidence/bitcoin-inscription-proof-annex-v1/proof-material/{txid}/proof-witness.json"
    binding = anchor.get("proof_material")
    if not isinstance(binding, dict) or binding.get("path") != expected:
        raise ValueError("unexpected or missing proof-material path binding")
    path = REPO_ROOT / expected
    if not path.is_file():
        raise ValueError("proof-material file is missing")
    size = path.stat().st_size
    digest = sha256_file(path)
    if size != binding.get("size") or digest != binding.get("sha256"):
        raise ValueError("proof-material size/SHA-256 binding mismatch")
    return path, {"path": expected, "size": size, "sha256": digest, "status": "PASS"}


def require_equal(value: Any, expected: Any, field: str) -> None:
    if value != expected:
        raise ValueError(f"{field} mismatch")


def verify_l1(anchor: dict[str, Any], proof: dict[str, Any]) -> dict[str, Any]:
    declared = proof.get("inscription")
    reveal_record = proof.get("reveal")
    if not isinstance(declared, dict) or not isinstance(reveal_record, dict):
        raise ValueError("proof inscription/reveal objects are missing")

    txid = str(anchor["txid"]).lower()
    inscription_number = str(anchor["inscription_number"])
    require_equal(proof.get("schema"), "trinityaccord.bitcoin-inscription-proof-witness.v1", "proof schema")
    require_equal(proof.get("network"), "bitcoin-mainnet", "proof network")
    require_equal(declared.get("inscription_number"), inscription_number, "inscription number")
    require_equal(declared.get("ordinals_inscription_id"), f"{txid}i0", "txid+i0 identity")
    require_equal(declared.get("inscription_index"), 0, "inscription index")
    require_equal(declared.get("classification"), anchor["classification"], "classification")
    require_equal(declared.get("expected_destination_address"), anchor["destination_address"], "destination address")

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
    if not content_type_utf8.lower().startswith("text/plain"):
        raise ValueError("v1 closed set requires text/plain inscription bodies")

    body = envelope["body"]
    body_sha = hashlib.sha256(body).hexdigest()
    require_equal(len(body), declared.get("body_bytes"), "inscription body size")
    require_equal(len(body), anchor["content"]["body_bytes"], "manifest body size")
    require_equal(body_sha, declared.get("body_sha256"), "inscription body SHA-256")
    require_equal(body_sha, anchor["content"]["body_sha256"], "manifest body SHA-256")

    mirror_rel = anchor["content"]["mirror_path"]
    require_equal(declared.get("mirror_path"), mirror_rel, "mirror path")
    mirror_path = REPO_ROOT / mirror_rel
    if not mirror_path.is_file():
        raise ValueError("mirror file is missing")
    mirror = mirror_path.read_bytes()
    mirror_sha = hashlib.sha256(mirror).hexdigest()
    require_equal(len(mirror), anchor["content"]["mirror_bytes"], "mirror size")
    require_equal(len(mirror), declared.get("mirror_bytes"), "proof mirror size")
    require_equal(mirror_sha, anchor["content"]["mirror_sha256"], "mirror SHA-256")
    require_equal(mirror_sha, declared.get("mirror_sha256"), "proof mirror SHA-256")
    method = anchor["content"]["mirror_binding_method"]
    require_equal(declared.get("mirror_binding_method"), method, "mirror binding method")
    if method == "exact_bytes":
        if body != mirror:
            raise ValueError("exact mirror bytes differ from inscription body")
    elif method == "canonicalized_utf8_strip_and_line_endings":
        canonical_body = canonicalize_text_bytes(body)
        if canonical_body != canonicalize_text_bytes(mirror):
            raise ValueError("canonicalized mirror differs from inscription body")
        require_equal(
            hashlib.sha256(canonical_body).hexdigest(),
            declared.get("canonicalized_body_sha256"),
            "canonicalized inscription SHA-256",
        )
    else:
        raise ValueError("unsupported mirror binding method")

    prevout = parse_transaction_hex(reveal_record["prevout_transaction_hex"])
    require_equal(prevout["txid"], reveal_record.get("prevout_txid"), "prevout transaction id")
    taproot = verify_taproot_reveal_binding(reveal, envelope, prevout)
    require_equal(taproot, reveal_record.get("taproot_binding"), "Taproot reveal binding")
    tapscript_signature = verify_simple_inscription_tapscript_spend(
        reveal, envelope, prevout
    )

    destination_index = int(anchor["destination_output_index"])
    require_equal(destination_index, declared.get("destination_output_index"), "destination output index")
    if destination_index < 0 or destination_index >= len(reveal["outputs"]):
        raise ValueError("destination output index is invalid")
    address = segwit_address(reveal["outputs"][destination_index]["script_pubkey"])
    require_equal(address, anchor["destination_address"], "recomputed destination address")

    return {
        "inscription_number": inscription_number,
        "txid": txid,
        "wtxid": reveal["wtxid"],
        "status": "PASS",
        "body_bytes": len(body),
        "body_sha256": body_sha,
        "content_type": content_type_utf8,
        "mirror_binding_method": method,
        "destination_address": address,
        "taproot_prevout_txid": taproot["prevout_txid"],
        "tapleaf_hash": taproot["tapleaf_hash"],
        "tapscript_signature_status": tapscript_signature["signature_status"],
        "tapscript_public_key": tapscript_signature["tapscript_public_key"],
        "taproot_sighash": tapscript_signature["taproot_sighash"],
    }


def verify_l2(anchor: dict[str, Any], proof: dict[str, Any], l1: dict[str, Any]) -> dict[str, Any]:
    inclusion = proof.get("block_inclusion")
    witness = proof.get("witness_inclusion")
    if not isinstance(inclusion, dict) or not isinstance(witness, dict):
        raise ValueError("block/witness inclusion proof is missing")
    header_hex = inclusion.get("header_hex")
    if not isinstance(header_hex, str) or len(header_hex) != 160:
        raise ValueError("block header hex is invalid")
    header = bytes.fromhex(header_hex)
    parsed_header = verify_header_pow(header)
    block_ref = anchor["block_reference"]
    require_equal(parsed_header["hash"], block_ref["hash"], "block hash")
    require_equal(inclusion.get("hash"), block_ref["hash"], "proof block hash")
    require_equal(inclusion.get("height"), block_ref["height"], "block height")
    require_equal(block_ref.get("timestamp"), parsed_header["timestamp"], "manifest block timestamp")
    require_equal(inclusion.get("timestamp"), parsed_header["timestamp"], "proof block timestamp")
    require_equal(inclusion.get("bits"), parsed_header["bits"], "block bits")

    tx_count = int(inclusion["transaction_count"])
    position = int(inclusion["target_transaction_position"])
    if position <= 0:
        raise ValueError("reveal transaction cannot be coinbase")
    verify_merkle_branch(
        l1["txid"],
        inclusion["target_txid_merkle_branch"],
        position,
        tx_count,
        parsed_header["merkle_root"],
    )

    coinbase = parse_transaction_hex(inclusion["coinbase_transaction_hex"])
    require_equal(coinbase["txid"], inclusion.get("coinbase_txid"), "coinbase txid")
    verify_merkle_branch(
        coinbase["txid"],
        inclusion["coinbase_txid_merkle_branch"],
        0,
        tx_count,
        parsed_header["merkle_root"],
    )

    require_equal(witness.get("target_wtxid"), l1["wtxid"], "target wtxid")
    require_equal(witness.get("target_wtxid_position"), position, "wtxid position")
    witness_root = str(witness["witness_root"]).lower()
    verify_merkle_branch(
        l1["wtxid"],
        witness["target_wtxid_merkle_branch"],
        position,
        tx_count,
        witness_root,
    )
    commitment = verify_witness_commitment(witness_root, coinbase)
    require_equal(commitment["coinbase_commitment"], witness.get("coinbase_commitment"), "witness commitment")
    require_equal(commitment["coinbase_reserved_value"], witness.get("coinbase_reserved_value"), "witness reserved value")
    require_equal(
        commitment["coinbase_commitment_output_index"],
        witness.get("coinbase_commitment_output_index"),
        "witness commitment output index",
    )
    return {
        "inscription_number": l1["inscription_number"],
        "txid": l1["txid"],
        "status": "PASS",
        "block_height": block_ref["height"],
        "block_hash": block_ref["hash"],
        "block_timestamp": parsed_header["timestamp"],
        "transaction_position": position,
        "transaction_count": tx_count,
        "transaction_merkle_root": parsed_header["merkle_root"],
        "witness_merkle_root": witness_root,
        "coinbase_txid": coinbase["txid"],
        "coinbase_witness_commitment": commitment["coinbase_commitment"],
    }


def verify_l3(anchor: dict[str, Any], proof: dict[str, Any], l2: dict[str, Any]) -> dict[str, Any]:
    ancestry = proof.get("pow_ancestry")
    if not isinstance(ancestry, dict):
        raise ValueError("PoW ancestry proof is missing")
    target_height = int(ancestry["target_height"])
    checkpoint_height = int(ancestry["checkpoint_height"])
    depth = int(ancestry["descendant_confirmation_depth"])
    require_equal(target_height, l2["block_height"], "PoW target height")
    require_equal(depth, EXPECTED_CONFIRMATION_DEPTH, "PoW confirmation depth")
    require_equal(checkpoint_height - target_height, depth, "PoW checkpoint distance")
    if target_height // 2016 != checkpoint_height // 2016:
        raise ValueError("v1 PoW segment crosses a difficulty retarget boundary")

    header_values = ancestry.get("headers_target_through_checkpoint")
    if not isinstance(header_values, list) or len(header_values) != depth + 1:
        raise ValueError("PoW ancestry header count mismatch")
    if header_values[0] != proof["block_inclusion"]["header_hex"]:
        raise ValueError("L2 block header is not L3 target header")
    previous: dict[str, Any] | None = None
    total_work = 0
    expected_bits: int | None = None
    for offset, header_hex in enumerate(header_values):
        if not isinstance(header_hex, str) or len(header_hex) != 160:
            raise ValueError("invalid header in PoW ancestry")
        current = verify_header_pow(bytes.fromhex(header_hex))
        if offset == 0:
            require_equal(current["hash"], l2["block_hash"], "PoW target block hash")
            expected_bits = current["bits"]
        else:
            if current["previous_block_hash"] != previous["hash"]:
                raise ValueError("PoW ancestry parent link mismatch")
            if current["bits"] != expected_bits:
                raise ValueError("unexpected difficulty bits within one retarget period")
        total_work += int(current["work"])
        previous = current
    assert previous is not None
    require_equal(previous["hash"], ancestry.get("checkpoint_hash"), "PoW checkpoint hash")

    trust_model = str(ancestry.get("trust_model", ""))
    for phrase in ["checkpoint-relative", "provenance only", "not a full-node", "heavier competing chain"]:
        if phrase not in trust_model:
            raise ValueError("PoW checkpoint trust boundary is incomplete")
    observations = ancestry.get("checkpoint_observations")
    votes = int(ancestry.get("matching_provider_votes", 0))
    if not isinstance(observations, list) or votes < 2 or len(observations) < votes:
        raise ValueError("PoW checkpoint provenance quorum is missing")
    providers: set[str] = set()
    matching_providers: set[str] = set()
    for observation in observations:
        provider = str(observation.get("provider", ""))
        if not provider:
            raise ValueError("PoW checkpoint provenance provider is missing")
        providers.add(provider)
        if (
            observation.get("target_height") == target_height
            and str(observation.get("target_hash", "")).lower() == l2["block_hash"]
            and observation.get("checkpoint_height") == checkpoint_height
            and str(observation.get("checkpoint_hash", "")).lower() == previous["hash"]
            and "provenance only" in str(observation.get("role", ""))
        ):
            matching_providers.add(provider)
    if len(providers) < 2 or len(matching_providers) < votes:
        raise ValueError("PoW checkpoint provenance observations do not match")

    return {
        "inscription_number": l2["inscription_number"],
        "txid": l2["txid"],
        "status": "PASS",
        "target_height": target_height,
        "checkpoint_height": checkpoint_height,
        "checkpoint_hash": previous["hash"],
        "valid_pow_headers": len(header_values),
        "descendant_confirmation_depth": depth,
        "cumulative_segment_work": str(total_work),
        "matching_provider_votes": votes,
        "trust_boundary": "PASS proves preserved valid-PoW ancestry to an explicit 144-block descendant checkpoint. Provider observations are provenance only; this is not full-node validation from genesis and does not prove absence of a heavier chain.",
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

    if manifest.get("schema") != "trinityaccord.bitcoin-inscription-proof-carrying-annex.v1":
        failures.append("unexpected manifest schema")
    if manifest.get("network", {}).get("name") != "Bitcoin Mainnet":
        failures.append("network must be Bitcoin Mainnet")
    boundary = manifest.get("authority_boundary", {})
    if boundary.get("canonical_authority") != "three Bitcoin Originals only":
        failures.append("canonical authority boundary changed")
    if boundary.get("canonical_original_count") != 3:
        failures.append("canonical original count must be 3")
    if boundary.get("ancillary_inscriptions_non_amending") is not True:
        failures.append("ancillary inscription boundary changed")
    if boundary.get("proof_annex_is_non_amending") is not True or boundary.get("no_authority_escalation") is not True:
        failures.append("proof annex non-amending boundary changed")

    implementation = manifest.get("verification_implementation", {})
    expected_impl = {
        "verifier": "evidence/bitcoin-inscription-proof-annex-v1/verification/verify_annex.py",
        "frozen_primitives": "evidence/bitcoin-inscription-proof-annex-v1/verification/bitcoin_proof_primitives_v1.py",
    }
    for key, expected_path in expected_impl.items():
        if implementation.get(key) != expected_path:
            failures.append(f"{key} path binding mismatch")
            continue
        path = REPO_ROOT / expected_path
        digest_field = f"{key}_sha256" if key != "frozen_primitives" else "frozen_primitives_sha256"
        if not path.is_file() or sha256_file(path) != implementation.get(digest_field):
            failures.append(f"{key} SHA-256 binding mismatch")
    if implementation.get("network_required_for_verification") is not False:
        failures.append("ordinary verification must be network-free")
    if implementation.get("runtime") != "Python 3 standard library only":
        failures.append("unexpected Bitcoin verifier runtime boundary")

    try:
        authority = authority_closed_set()
    except Exception as exc:
        failures.append(f"authority closed set: {exc}")
        authority = {}
    anchors = manifest.get("anchors")
    if not isinstance(anchors, list):
        failures.append("manifest anchors are missing")
        anchors = []
    ids = {str(anchor.get("inscription_number")) for anchor in anchors}
    txids = [str(anchor.get("txid", "")).lower() for anchor in anchors]
    if len(anchors) != 8 or ids != EXPECTED_INSCRIPTIONS:
        failures.append("manifest must contain the exact 8-inscription closed set")
    if len(txids) != len(set(txids)):
        failures.append("duplicate reveal txid")

    for anchor in anchors:
        inscription = str(anchor.get("inscription_number"))
        txid = str(anchor.get("txid", "")).lower()
        try:
            if inscription not in authority:
                raise ValueError("inscription is absent from authority manifest")
            source = authority[inscription]
            require_equal(txid, str(source["txid"]).lower(), "authority txid")
            require_equal(anchor.get("classification"), source["classification"], "authority classification")
            require_equal(anchor["block_reference"]["height"], source["block_height"], "authority block height")
            require_equal(anchor["block_reference"]["hash"], str(source["block_hash"]).lower(), "authority block hash")
            expected_class = "canonical_original" if inscription in CANONICAL_INSCRIPTIONS else "non_amending_ancillary"
            require_equal(anchor.get("classification"), expected_class, "closed-set classification")
            for level in [
                "L1_INSCRIPTION_CONTENT_AND_TAPROOT_BINDING",
                "L2_BLOCK_AND_WITNESS_INCLUSION",
                "L3_CHECKPOINT_RELATIVE_POW_ANCESTRY",
            ]:
                if anchor.get("proof_status", {}).get(level) != "PASS":
                    raise ValueError(f"manifest does not declare {level} PASS")
            proof_path, byte_check = bound_proof(anchor)
            proof_byte_checks.append({"inscription_number": inscription, "txid": txid, **byte_check})
            proof = load_json(proof_path)
            l1 = verify_l1(anchor, proof)
            l1_checks.append(l1)
            l2 = verify_l2(anchor, proof, l1)
            l2_checks.append(l2)
            l3 = verify_l3(anchor, proof, l2)
            l3_checks.append(l3)
        except Exception as exc:
            failures.append(f"{inscription or txid}: {exc}")

    result = "PASS" if not failures else "FAIL"
    report = {
        "schema": "trinityaccord.bitcoin-inscription-annex-offline-verification.v1",
        "result": result,
        "L1_INSCRIPTION_CONTENT_AND_TAPROOT_BINDING": {
            "status": "PASS" if len(l1_checks) == 8 and not failures else "FAIL",
            "inscriptions": len(l1_checks),
            "canonical_originals": sum(item["inscription_number"] in CANONICAL_INSCRIPTIONS for item in l1_checks),
            "non_amending_ancillary": sum(item["inscription_number"] not in CANONICAL_INSCRIPTIONS for item in l1_checks),
        },
        "L2_BLOCK_AND_WITNESS_INCLUSION": {
            "status": "PASS" if len(l2_checks) == 8 and not failures else "FAIL",
            "reveal_transactions": len(l2_checks),
            "txid_merkle_proofs": len(l2_checks),
            "bip141_witness_commitment_proofs": len(l2_checks),
        },
        "L3_CHECKPOINT_RELATIVE_POW_ANCESTRY": {
            "status": "PASS" if len(l3_checks) == 8 and not failures else "FAIL",
            "anchors": len(l3_checks),
            "descendant_confirmation_depth_per_anchor": EXPECTED_CONFIRMATION_DEPTH,
            "valid_pow_headers": sum(item["valid_pow_headers"] for item in l3_checks),
        },
        "proof_byte_checks": proof_byte_checks,
        "l1_checks": l1_checks,
        "l2_checks": l2_checks,
        "l3_checks": l3_checks,
        "failures": failures,
        "claim_boundary": "The report proves exact Ord envelope/body extraction, BIP341 tapscript-to-prevout binding, the observed BIP342 script shape and BIP340 Schnorr spend signature, reveal txid inclusion, BIP141 witness inclusion, and 144-block checkpoint-relative valid-PoW ancestry from preserved bytes. It is not full-node validation from genesis, does not prove absence of a heavier chain, does not reconstruct the global Ordinals inscription-number index, and is not absolute physical-world time, civil authorship, continuing key control, or philosophical truth.",
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
