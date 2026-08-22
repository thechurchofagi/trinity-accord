#!/usr/bin/env python3
"""Fail-closed, network-free verifier for the 12-item Bitcoin address proof annex v2."""
from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ANNEX_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = ANNEX_DIR.parents[1]
V1_DIR = REPO_ROOT / "evidence/bitcoin-inscription-proof-annex-v1"
V1_VERIFICATION = V1_DIR / "verification"
sys.path.insert(0, str(V1_VERIFICATION))

from bitcoin_proof_primitives_v1 import (  # noqa: E402
    extract_inscription_envelopes,
    parse_transaction_hex,
    segwit_address,
    sha256_file,
    verify_simple_inscription_tapscript_spend,
    verify_taproot_reveal_binding,
)
from verify_annex import verify_l2 as verify_l2_v1  # noqa: E402
from verify_annex import verify_l3 as verify_l3_v1  # noqa: E402

TARGETS = ANNEX_DIR / "TARGETS.json"
MANIFEST = ANNEX_DIR / "ANNEX-MANIFEST.json"
ADDRESS_ROOT = REPO_ROOT / "bitcoin-inscription-mirrors/address-wide"
ADDRESS_MANIFEST = ADDRESS_ROOT / "manifest.json"
V1_MANIFEST = V1_DIR / "ANNEX-MANIFEST.json"
V1_VERIFIER = V1_VERIFICATION / "verify_annex.py"
EXPECTED_CANONICAL_IDS = {
    "e40dfb2aa78cbccca88f749e9ec5cbe3c1df503273d73c72297863ae0d1d8343i0",
    "90116f35de075074f5e5d1fbdda69a646a124e2287d7d58e2520317098cd4258i0",
    "4d1c8f5ea8e8bae2982b42de6cc79deda3d243a21010a2888546e62ed7192c8ci0",
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON object required: {path}")
    return value


def require_equal(value: Any, expected: Any, field: str) -> None:
    if value != expected:
        raise ValueError(f"{field} mismatch")


def decode_b64(path: Path) -> bytes:
    return base64.b64decode(path.read_text(encoding="ascii").strip(), validate=True)


def archived_payload(inscription_id: str) -> tuple[bytes, bytes, dict[str, Any]]:
    obj = ADDRESS_ROOT / "objects" / inscription_id
    if not obj.is_dir():
        raise ValueError(f"address archive object missing: {inscription_id}")
    body = decode_b64(obj / "content.b64")
    metadata = decode_b64(obj / "inscription-metadata.cbor.b64")
    info = load_json(obj / "metadata.json")
    if info.get("id") != inscription_id:
        raise ValueError("address archive recursive metadata id mismatch")
    return body, metadata, info


def envelope_metadata(envelope: dict[str, Any]) -> tuple[bytes, int]:
    parts = [value for tag, value in envelope["fields"] if tag == b"\x05"]
    return b"".join(parts), len(parts)


def run_v1_verifier() -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, str(V1_VERIFIER)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={"PATH": str(Path(sys.executable).parent)},
    )
    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError(f"frozen v1 verifier did not emit JSON: {completed.stderr}") from exc
    if completed.returncode != 0 or report.get("result") != "PASS":
        raise ValueError("frozen eight-item v1 Bitcoin proof annex is not PASS")
    for key in [
        "L1_INSCRIPTION_CONTENT_AND_TAPROOT_BINDING",
        "L2_BLOCK_AND_WITNESS_INCLUSION",
        "L3_CHECKPOINT_RELATIVE_POW_ANCESTRY",
    ]:
        if report.get(key, {}).get("status") != "PASS":
            raise ValueError(f"frozen v1 layer is not PASS: {key}")
    return report


def verify_manifest_boundaries(manifest: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    require_equal(manifest.get("schema"), "trinityaccord.bitcoin-address-proof-carrying-annex.v2", "v2 manifest schema")
    config = load_json(TARGETS)
    address = load_json(ADDRESS_MANIFEST)
    v1 = load_json(V1_MANIFEST)

    current_ids = set(address.get("ids", []))
    if address.get("count") != 12 or len(current_ids) != 12:
        raise ValueError("address archive must contain exactly 12 current stable IDs")
    require_equal(set(config.get("canonical_original_ids", [])), EXPECTED_CANONICAL_IDS, "canonical original IDs")
    boundary = manifest.get("authority_boundary", {})
    require_equal(boundary.get("canonical_original_count"), 3, "canonical original count")
    require_equal(set(boundary.get("canonical_original_ids", [])), EXPECTED_CANONICAL_IDS, "manifest canonical IDs")
    for flag in [
        "formation_records_are_non_canonical",
        "post_canonical_records_are_non_amending",
        "proof_inclusion_does_not_confer_authority",
        "same_address_does_not_imply_canonical",
        "no_authority_escalation",
    ]:
        if boundary.get(flag) is not True:
            raise ValueError(f"authority boundary flag must be true: {flag}")

    anchors = manifest.get("anchors", [])
    if not isinstance(anchors, list) or len(anchors) != 12:
        raise ValueError("v2 manifest must contain exactly 12 anchors")
    by_id = {str(item["ordinals_inscription_id"]): item for item in anchors}
    if len(by_id) != 12 or set(by_id) != current_ids:
        raise ValueError("v2 anchor set does not equal address-wide stable ID set")

    inherited = [item for item in anchors if item.get("proof_source") == "inherited_frozen_v1"]
    captured = [item for item in anchors if item.get("proof_source") == "captured_v2"]
    if len(inherited) != 8 or len(captured) != 4:
        raise ValueError("v2 composition must be exactly 8 inherited + 4 captured")
    formation_ids = {str(item["ordinals_inscription_id"]) for item in config["formation_targets"]}
    if {str(item["ordinals_inscription_id"]) for item in captured} != formation_ids:
        raise ValueError("captured v2 set differs from declared formation targets")
    if formation_ids.intersection(EXPECTED_CANONICAL_IDS):
        raise ValueError("formation target intersects canonical originals")
    if any(item.get("canonical") is not False or item.get("amends_canon") is not False for item in captured):
        raise ValueError("captured formation proof attempts authority escalation")

    inheritance = manifest.get("inheritance", {})
    require_equal(inheritance.get("v1_manifest_size"), V1_MANIFEST.stat().st_size, "v1 manifest size binding")
    require_equal(inheritance.get("v1_manifest_sha256"), sha256_file(V1_MANIFEST), "v1 manifest SHA-256 binding")
    require_equal(inheritance.get("v1_proof_count"), 8, "v1 inherited proof count")
    address_binding = manifest.get("address_archive_binding", {})
    require_equal(address_binding.get("manifest_size"), ADDRESS_MANIFEST.stat().st_size, "address manifest size binding")
    require_equal(address_binding.get("manifest_sha256"), sha256_file(ADDRESS_MANIFEST), "address manifest SHA-256 binding")
    require_equal(address_binding.get("stable_id_count"), 12, "address stable id count")

    v1_ids = {str(item["ordinals_inscription_id"]) for item in v1.get("anchors", [])}
    if len(v1_ids) != 8 or v1_ids.union(formation_ids) != current_ids or v1_ids.intersection(formation_ids):
        raise ValueError("8+4 stable-ID composition mismatch")
    return config, address, v1


def verify_inherited_metadata(v1: dict[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for anchor in v1.get("anchors", []):
        inscription_id = str(anchor["ordinals_inscription_id"])
        path = REPO_ROOT / str(anchor["proof_material"]["path"])
        if not path.is_file():
            raise ValueError(f"inherited v1 proof missing: {inscription_id}")
        proof = load_json(path)
        reveal = parse_transaction_hex(proof["reveal"]["transaction_hex"])
        require_equal(f"{reveal['txid']}i0", inscription_id, "inherited stable inscription id")
        envelopes = extract_inscription_envelopes(reveal)
        matching = [item for item in envelopes if int(item["inscription_index"]) == 0]
        if len(matching) != 1:
            raise ValueError(f"inherited proof has ambiguous inscription index 0: {inscription_id}")
        onchain_metadata, field_count = envelope_metadata(matching[0])
        body_archive, metadata_archive, _ = archived_payload(inscription_id)
        if onchain_metadata != metadata_archive:
            raise ValueError(f"inherited witness metadata differs from address archive: {inscription_id}")
        if hashlib.sha256(body_archive).hexdigest() != anchor["content"]["body_sha256"]:
            raise ValueError(f"address archive body differs from frozen v1 body hash: {inscription_id}")
        checks.append(
            {
                "ordinals_inscription_id": inscription_id,
                "proof_source": "inherited_frozen_v1",
                "status": "PASS",
                "metadata_present": bool(onchain_metadata),
                "metadata_field_count": field_count,
                "metadata_bytes": len(onchain_metadata),
                "metadata_sha256": hashlib.sha256(onchain_metadata).hexdigest(),
            }
        )
    if len(checks) != 8:
        raise ValueError("expected eight inherited metadata witness checks")
    return checks


def bound_v2_proof(anchor: dict[str, Any]) -> dict[str, Any]:
    binding = anchor.get("proof_material")
    if not isinstance(binding, dict):
        raise ValueError("v2 proof binding missing")
    path = REPO_ROOT / str(binding.get("path", ""))
    if not path.is_file():
        raise ValueError("v2 proof material file missing")
    require_equal(path.stat().st_size, binding.get("size"), "v2 proof size binding")
    require_equal(sha256_file(path), binding.get("sha256"), "v2 proof SHA-256 binding")
    return load_json(path)


def verify_l1_v2(anchor: dict[str, Any], proof: dict[str, Any]) -> dict[str, Any]:
    declared = proof.get("inscription")
    reveal_record = proof.get("reveal")
    if not isinstance(declared, dict) or not isinstance(reveal_record, dict):
        raise ValueError("v2 proof inscription/reveal objects missing")
    require_equal(proof.get("schema"), "trinityaccord.bitcoin-address-proof-witness.v2", "v2 proof schema")
    require_equal(proof.get("network"), "bitcoin-mainnet", "v2 proof network")
    inscription_id = str(anchor["ordinals_inscription_id"])
    txid = str(anchor["txid"])
    require_equal(inscription_id, f"{txid}i0", "v2 stable inscription identity")
    require_equal(declared.get("ordinals_inscription_id"), inscription_id, "v2 declared inscription id")
    require_equal(declared.get("inscription_index"), 0, "v2 inscription index")
    require_equal(declared.get("classification"), "pre_canonical_formation", "v2 formation classification")
    require_equal(declared.get("canonical"), False, "v2 canonical flag")
    require_equal(declared.get("amends_canon"), False, "v2 amend flag")

    reveal = parse_transaction_hex(reveal_record["transaction_hex"])
    require_equal(reveal["txid"], txid, "recomputed v2 reveal txid")
    require_equal(reveal["wtxid"], str(anchor["wtxid"]), "recomputed v2 reveal wtxid")
    require_equal(reveal_record.get("txid"), reveal["txid"], "stored v2 reveal txid")
    require_equal(reveal_record.get("wtxid"), reveal["wtxid"], "stored v2 reveal wtxid")

    envelopes = extract_inscription_envelopes(reveal)
    matching = [item for item in envelopes if int(item["inscription_index"]) == 0]
    if len(matching) != 1:
        raise ValueError("v2 proof requires exactly one inscription index 0 envelope")
    envelope = matching[0]
    require_equal(envelope["input_index"], reveal_record.get("input_index"), "v2 envelope input index")
    if not envelope["body_present"]:
        raise ValueError("v2 inscription body separator missing")

    body_archive, metadata_archive, info = archived_payload(inscription_id)
    body = envelope["body"]
    if body != body_archive:
        raise ValueError("v2 reveal body differs from exact address archive")
    body_sha = hashlib.sha256(body).hexdigest()
    require_equal(len(body), declared.get("body_bytes"), "v2 body bytes")
    require_equal(body_sha, declared.get("body_sha256"), "v2 body SHA-256")
    require_equal(body_sha, anchor["content"]["body_sha256"], "v2 manifest body SHA-256")
    content_type = envelope["content_type"].decode("utf-8")
    require_equal(content_type, declared.get("content_type_utf8"), "v2 content type")
    require_equal(content_type, anchor["content"]["content_type_utf8"], "v2 manifest content type")
    require_equal(content_type, info["content_type"], "v2 archived recursive content type")

    metadata, field_count = envelope_metadata(envelope)
    if metadata != metadata_archive:
        raise ValueError("v2 reveal tag-5 metadata differs from exact address archive")
    metadata_sha = hashlib.sha256(metadata).hexdigest()
    require_equal(field_count, declared.get("metadata_field_count"), "v2 metadata field count")
    require_equal(bool(metadata), declared.get("metadata_present"), "v2 metadata presence")
    require_equal(len(metadata), declared.get("metadata_bytes"), "v2 metadata bytes")
    require_equal(metadata_sha, declared.get("metadata_sha256"), "v2 metadata SHA-256")
    require_equal(bool(metadata), anchor["inscription_metadata"]["present"], "v2 manifest metadata presence")
    require_equal(field_count, anchor["inscription_metadata"]["field_count"], "v2 manifest metadata field count")
    require_equal(len(metadata), anchor["inscription_metadata"]["bytes"], "v2 manifest metadata bytes")
    require_equal(metadata_sha, anchor["inscription_metadata"]["sha256"], "v2 manifest metadata SHA-256")

    prevout = parse_transaction_hex(reveal_record["prevout_transaction_hex"])
    require_equal(prevout["txid"], reveal_record.get("prevout_txid"), "v2 prevout txid")
    taproot = verify_taproot_reveal_binding(reveal, envelope, prevout)
    require_equal(taproot, reveal_record.get("taproot_binding"), "v2 Taproot reveal binding")
    signature = verify_simple_inscription_tapscript_spend(reveal, envelope, prevout)
    require_equal(signature, reveal_record.get("tapscript_signature"), "v2 tapscript signature proof")

    destination_index = int(anchor["destination_output_index"])
    require_equal(destination_index, declared.get("destination_output_index"), "v2 destination output index")
    address = segwit_address(reveal["outputs"][destination_index]["script_pubkey"])
    require_equal(address, anchor["destination_address"], "v2 destination address")
    require_equal(address, declared.get("expected_destination_address"), "v2 declared destination address")

    return {
        "inscription_number": inscription_id,
        "ordinals_inscription_id": inscription_id,
        "txid": txid,
        "wtxid": reveal["wtxid"],
        "status": "PASS",
        "body_bytes": len(body),
        "body_sha256": body_sha,
        "content_type": content_type,
        "metadata_present": bool(metadata),
        "metadata_field_count": field_count,
        "metadata_bytes": len(metadata),
        "metadata_sha256": metadata_sha,
        "destination_address": address,
        "tapleaf_hash": taproot["tapleaf_hash"],
        "tapscript_signature_status": signature["signature_status"],
    }


def main() -> int:
    failures: list[str] = []
    l1_new: list[dict[str, Any]] = []
    l2_new: list[dict[str, Any]] = []
    l3_new: list[dict[str, Any]] = []
    metadata_checks: list[dict[str, Any]] = []
    v1_report: dict[str, Any] | None = None

    try:
        manifest = load_json(MANIFEST)
        _, _, v1 = verify_manifest_boundaries(manifest)
        v1_report = run_v1_verifier()
        metadata_checks.extend(verify_inherited_metadata(v1))
        for anchor in manifest["anchors"]:
            if anchor.get("proof_source") != "captured_v2":
                continue
            try:
                proof = bound_v2_proof(anchor)
                l1 = verify_l1_v2(anchor, proof)
                l2 = verify_l2_v1(anchor, proof, l1)
                l3 = verify_l3_v1(anchor, proof, l2)
                l1_new.append(l1)
                l2_new.append(l2)
                l3_new.append(l3)
                metadata_checks.append(
                    {
                        "ordinals_inscription_id": l1["ordinals_inscription_id"],
                        "proof_source": "captured_v2",
                        "status": "PASS",
                        "metadata_present": l1["metadata_present"],
                        "metadata_field_count": l1["metadata_field_count"],
                        "metadata_bytes": l1["metadata_bytes"],
                        "metadata_sha256": l1["metadata_sha256"],
                    }
                )
            except Exception as exc:
                failures.append(f"{anchor.get('ordinals_inscription_id')}: {exc}")
    except Exception as exc:
        failures.append(f"annex: {exc}")

    v1_ok = v1_report is not None and v1_report.get("result") == "PASS"
    l1_total = (8 if v1_ok else 0) + len(l1_new)
    l2_total = (8 if v1_ok else 0) + len(l2_new)
    l3_total = (8 if v1_ok else 0) + len(l3_new)
    metadata_present = sum(1 for item in metadata_checks if item["metadata_present"])
    metadata_absent = sum(1 for item in metadata_checks if not item["metadata_present"])
    if l1_total != 12:
        failures.append(f"L1 aggregate count is {l1_total}, expected 12")
    if l2_total != 12:
        failures.append(f"L2 aggregate count is {l2_total}, expected 12")
    if l3_total != 12:
        failures.append(f"L3 aggregate count is {l3_total}, expected 12")
    if len(metadata_checks) != 12 or metadata_present != 1 or metadata_absent != 11:
        failures.append("metadata witness coverage must be exactly 12/12 with 1 present and 11 absent")

    result = "PASS" if not failures else "FAIL"
    report = {
        "schema": "trinityaccord.bitcoin-address-proof-offline-verification.v2",
        "result": result,
        "authority_boundary": {
            "canonical_original_count": 3,
            "canonical_original_ids": sorted(EXPECTED_CANONICAL_IDS),
            "proof_inclusion_does_not_confer_authority": True,
            "same_address_does_not_imply_canonical": True,
        },
        "L1_INSCRIPTION_CONTENT_METADATA_AND_TAPROOT_BINDING": {
            "status": "PASS" if l1_total == 12 and len(metadata_checks) == 12 and not failures else "FAIL",
            "inscriptions": l1_total,
            "inherited_v1": 8 if v1_ok else 0,
            "captured_v2": len(l1_new),
            "metadata_witness_checks": len(metadata_checks),
            "metadata_present": metadata_present,
            "metadata_absence_proved": metadata_absent,
        },
        "L2_BLOCK_AND_WITNESS_INCLUSION": {
            "status": "PASS" if l2_total == 12 and not failures else "FAIL",
            "inscriptions": l2_total,
            "inherited_v1": 8 if v1_ok else 0,
            "captured_v2": len(l2_new),
        },
        "L3_CHECKPOINT_RELATIVE_POW_ANCESTRY": {
            "status": "PASS" if l3_total == 12 and not failures else "FAIL",
            "inscriptions": l3_total,
            "inherited_v1": 8 if v1_ok else 0,
            "captured_v2": len(l3_new),
            "confirmation_depth": 144,
        },
        "new_formation_l1_checks": l1_new,
        "new_formation_l2_checks": l2_new,
        "new_formation_l3_checks": l3_new,
        "metadata_witness_checks": metadata_checks,
        "frozen_v1_result": v1_report.get("result") if v1_report else None,
        "failures": failures,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
