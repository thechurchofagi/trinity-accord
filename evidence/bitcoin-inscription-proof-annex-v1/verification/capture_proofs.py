#!/usr/bin/env python3
"""Networked controlled capture for Bitcoin inscription proof annex v1.

Ordinary verification never calls this script. It downloads historical Bitcoin
blocks, reduces them to compact proof witnesses, cross-checks explicit PoW
checkpoints with two providers, and writes bytes for later offline verification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bitcoin_proof_primitives_v1 import (
    canonicalize_text_bytes,
    extract_inscription_envelopes,
    header_from_fields,
    internal_hash,
    merkle_branch,
    merkle_root,
    parse_block,
    parse_header,
    parse_transaction_hex,
    segwit_address,
    sha256_file,
    verify_header_pow,
    verify_taproot_reveal_binding,
    verify_witness_commitment,
    witness_commitment,
)


ANNEX_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = ANNEX_DIR.parents[1]
AUTHORITY = REPO_ROOT / "archive/authority-manifest/authority.jcs.json"
MIRROR_ROOT = REPO_ROOT / "bitcoin-inscription-mirrors"
PRIMARY = "https://mempool.space/api"
SECONDARY = "https://blockstream.info/api"
CONFIRMATION_DEPTH = 144
USER_AGENT = "trinity-accord-bitcoin-proof-capture/1.0"


def fetch(url: str, *, binary: bool = False, retries: int = 4) -> bytes | str:
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=90) as response:
                data = response.read()
            return data if binary else data.decode("utf-8")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"capture fetch failed: {url}: {last_error}")


def fetch_json(url: str) -> Any:
    return json.loads(str(fetch(url)))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
    ).strip()


def mirror_records() -> dict[str, tuple[dict[str, Any], Path]]:
    records: dict[str, tuple[dict[str, Any], Path]] = {}
    for directory in ["canonical-originals", "vision-layer", "context-layer"]:
        for path in sorted((MIRROR_ROOT / directory).glob("*.json")):
            record = json.loads(path.read_text(encoding="utf-8"))
            inscription_id = str(record["inscription"]["inscription_id"])
            if inscription_id in records:
                raise SystemExit(f"duplicate mirror inscription id: {inscription_id}")
            records[inscription_id] = (record, path)
    return records


def authority_anchors() -> list[dict[str, Any]]:
    authority = json.loads(AUTHORITY.read_text(encoding="utf-8"))
    bitcoin = authority["bitcoin"]
    anchors = [dict(item, _classification="canonical_original") for item in bitcoin["originals"]]
    ancillary = [dict(item, _classification="non_amending_ancillary") for item in bitcoin["ancillary"]]
    ancillary.sort(key=lambda item: int(item["block_height"]))
    anchors.extend(ancillary)
    if len(anchors) != 8 or len(bitcoin["originals"]) != 3 or len(ancillary) != 5:
        raise SystemExit("authority manifest must contain exactly 3 originals + 5 ancillary inscriptions")
    return anchors


def fetch_header_chain(target_height: int, checkpoint_height: int) -> list[str]:
    blocks: dict[int, dict[str, Any]] = {}
    cursor = checkpoint_height
    while cursor >= target_height:
        page = fetch_json(f"{PRIMARY}/v1/blocks/{cursor}")
        if not isinstance(page, list) or not page:
            raise RuntimeError(f"empty header page at height {cursor}")
        for item in page:
            height = int(item["height"])
            if target_height <= height <= checkpoint_height:
                blocks[height] = item
        cursor = min(int(item["height"]) for item in page) - 1
    expected = list(range(target_height, checkpoint_height + 1))
    if sorted(blocks) != expected:
        missing = sorted(set(expected) - set(blocks))
        raise RuntimeError(f"header ancestry is not contiguous; missing={missing[:5]}")
    headers = [header_from_fields(blocks[height]).hex() for height in expected]
    for offset, raw_hex in enumerate(headers):
        parsed = verify_header_pow(bytes.fromhex(raw_hex))
        expected_hash = str(blocks[target_height + offset]["id"]).lower()
        if parsed["hash"] != expected_hash:
            raise RuntimeError("header reconstruction mismatch")
        if offset and parsed["previous_block_hash"] != parse_header(bytes.fromhex(headers[offset - 1]))["hash"]:
            raise RuntimeError("header ancestry link mismatch")
    return headers


def provider_observations(target_height: int, checkpoint_height: int) -> list[dict[str, Any]]:
    captured = datetime.now(timezone.utc).isoformat()
    observations = []
    for provider, base in [("mempool.space", PRIMARY), ("blockstream.info", SECONDARY)]:
        target_hash = str(fetch(f"{base}/block-height/{target_height}")).strip().lower()
        checkpoint_hash = str(fetch(f"{base}/block-height/{checkpoint_height}")).strip().lower()
        observations.append(
            {
                "provider": provider,
                "base_url": base,
                "captured_at_utc": captured,
                "target_height": target_height,
                "target_hash": target_hash,
                "checkpoint_height": checkpoint_height,
                "checkpoint_hash": checkpoint_hash,
                "role": "capture provenance only; not a substitute for offline proof or full-node validation",
            }
        )
    if len({item["target_hash"] for item in observations}) != 1:
        raise RuntimeError("provider target-block observations disagree")
    if len({item["checkpoint_hash"] for item in observations}) != 1:
        raise RuntimeError("provider checkpoint observations disagree")
    return observations


def raw_tx_crosscheck(txid: str) -> tuple[str, list[dict[str, Any]]]:
    observations = []
    values = []
    for provider, base in [("mempool.space", PRIMARY), ("blockstream.info", SECONDARY)]:
        raw_hex = str(fetch(f"{base}/tx/{txid}/hex")).strip().lower()
        parsed = parse_transaction_hex(raw_hex)
        if parsed["txid"] != txid.lower():
            raise RuntimeError(f"{provider} returned wrong raw transaction for {txid}")
        values.append(raw_hex)
        observations.append(
            {
                "provider": provider,
                "base_url": base,
                "raw_transaction_sha256": hashlib.sha256(bytes.fromhex(raw_hex)).hexdigest(),
                "raw_transaction_bytes": len(raw_hex) // 2,
            }
        )
    if len(set(values)) != 1:
        raise RuntimeError(f"raw transaction providers disagree for {txid}")
    return values[0], observations


def capture_anchor(
    anchor: dict[str, Any], mirror: dict[str, Any], mirror_path: Path, output_dir: Path
) -> dict[str, Any]:
    txid = str(anchor["txid"]).lower()
    inscription_number = str(anchor["inscription_id"])
    block_height = int(anchor["block_height"])
    block_hash = str(anchor["block_hash"]).lower()
    checkpoint_height = block_height + CONFIRMATION_DEPTH
    print(f"capture {inscription_number}: tx={txid} block={block_height}", flush=True)

    observations = provider_observations(block_height, checkpoint_height)
    if observations[0]["target_hash"] != block_hash:
        raise RuntimeError(f"authority block hash mismatch for {txid}")
    headers = fetch_header_chain(block_height, checkpoint_height)
    target_header = parse_header(bytes.fromhex(headers[0]))
    checkpoint_header = parse_header(bytes.fromhex(headers[-1]))
    if target_header["hash"] != block_hash:
        raise RuntimeError("target header does not match authority manifest")
    if checkpoint_header["hash"] != observations[0]["checkpoint_hash"]:
        raise RuntimeError("checkpoint header does not match provider quorum")
    if block_height // 2016 != checkpoint_height // 2016:
        raise RuntimeError("v1 capture segment crosses a Bitcoin difficulty retarget boundary")

    raw_block = bytes(fetch(f"{PRIMARY}/block/{block_hash}/raw", binary=True))
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

    endpoint_reveal_hex, reveal_observations = raw_tx_crosscheck(txid)
    if reveal["raw"].hex() != endpoint_reveal_hex:
        raise RuntimeError("raw block reveal bytes differ from transaction endpoints")

    envelopes = extract_inscription_envelopes(reveal)
    expected_ord_id = str(mirror["inscription"]["ordinals_inscription_id"]).lower()
    if expected_ord_id != f"{txid}i0":
        raise RuntimeError("v1 annex requires txid+i0 inscription identity")
    if not envelopes or envelopes[0]["inscription_index"] != 0:
        raise RuntimeError("reveal transaction does not contain inscription index 0")
    envelope = envelopes[0]
    if not envelope["body_present"]:
        raise RuntimeError("inscription has no body separator")

    prev_txid = reveal["inputs"][int(envelope["input_index"])]["prev_txid"]
    prevout_hex, prevout_observations = raw_tx_crosscheck(prev_txid)
    prevout_tx = parse_transaction_hex(prevout_hex)
    taproot = verify_taproot_reveal_binding(reveal, envelope, prevout_tx)

    expected_address = str(mirror["inscription"]["source_address"]).lower()
    address_outputs = []
    for output in reveal["outputs"]:
        try:
            address = segwit_address(output["script_pubkey"])
        except ValueError:
            continue
        if address == expected_address:
            address_outputs.append(int(output["index"]))
    if len(address_outputs) != 1:
        raise RuntimeError("expected authority destination address is not unique in reveal outputs")
    destination_output_index = address_outputs[0]

    mirror_raw_path = REPO_ROOT / str(mirror["content"]["raw_text_path"])
    mirror_bytes = mirror_raw_path.read_bytes()
    body = envelope["body"]
    if body == mirror_bytes:
        mirror_binding_method = "exact_bytes"
    elif canonicalize_text_bytes(body) == canonicalize_text_bytes(mirror_bytes):
        mirror_binding_method = "canonicalized_utf8_strip_and_line_endings"
    else:
        raise RuntimeError("on-chain inscription body does not bind to repository mirror")

    coinbase = transactions[0]
    wtxids = ["00" * 32] + [item["wtxid"] for item in transactions[1:]]
    witness_root = merkle_root(wtxids)
    witness_result = verify_witness_commitment(witness_root, coinbase)
    commitment_record = witness_commitment(coinbase)

    proof = {
        "schema": "trinityaccord.bitcoin-inscription-proof-witness.v1",
        "network": "bitcoin-mainnet",
        "inscription": {
            "inscription_number": inscription_number,
            "ordinals_inscription_id": expected_ord_id,
            "inscription_index": 0,
            "classification": anchor["_classification"],
            "title": anchor.get("label") or anchor.get("title"),
            "expected_destination_address": expected_address,
            "destination_output_index": destination_output_index,
            "content_type_hex": envelope["content_type"].hex(),
            "content_type_utf8": envelope["content_type"].decode("utf-8"),
            "body_bytes": len(body),
            "body_sha256": hashlib.sha256(body).hexdigest(),
            "mirror_path": str(mirror_raw_path.relative_to(REPO_ROOT)),
            "mirror_binding_method": mirror_binding_method,
            "mirror_bytes": len(mirror_bytes),
            "mirror_sha256": hashlib.sha256(mirror_bytes).hexdigest(),
            "canonicalized_body_sha256": hashlib.sha256(canonicalize_text_bytes(body)).hexdigest(),
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
            "height": block_height,
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
            "target_height": block_height,
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
                "the exact inscription body is serialized in the reveal transaction witness",
                "the tapscript/control block commits that body to the reveal input prevout",
                "the reveal txid and witness wtxid are committed into the declared Bitcoin block",
                "the block has 144 preserved valid-PoW descendants relative to the explicit checkpoint",
                "the reveal transaction pays its declared output to the recorded P2TR destination address",
            ],
            "does_not_prove": [
                "full Bitcoin consensus validity from genesis",
                "absence of a heavier competing chain",
                "civil identity or authorship",
                "philosophical truth",
                "absolute physical-world time",
                "the global Ordinals inscription number without ordinal-theory index reconstruction",
            ],
        },
    }

    rel = Path("evidence/bitcoin-inscription-proof-annex-v1/proof-material") / txid / "proof-witness.json"
    proof_path = output_dir / txid / "proof-witness.json"
    write_json(proof_path, proof)
    return {
        "id": f"bitcoin-inscription-{inscription_number}",
        "title": proof["inscription"]["title"],
        "classification": anchor["_classification"],
        "inscription_number": inscription_number,
        "ordinals_inscription_id": expected_ord_id,
        "txid": txid,
        "wtxid": reveal["wtxid"],
        "destination_address": expected_address,
        "destination_output_index": destination_output_index,
        "block_reference": {
            "height": block_height,
            "hash": block_hash,
            "timestamp": target_header["timestamp"],
        },
        "content": {
            "content_type_hex": envelope["content_type"].hex(),
            "content_type_utf8": envelope["content_type"].decode("utf-8"),
            "body_bytes": len(body),
            "body_sha256": hashlib.sha256(body).hexdigest(),
            "mirror_path": str(mirror_raw_path.relative_to(REPO_ROOT)),
            "mirror_bytes": len(mirror_bytes),
            "mirror_sha256": hashlib.sha256(mirror_bytes).hexdigest(),
            "mirror_binding_method": mirror_binding_method,
        },
        "proof_status": {
            "L1_INSCRIPTION_CONTENT_AND_TAPROOT_BINDING": "PASS",
            "L2_BLOCK_AND_WITNESS_INCLUSION": "PASS",
            "L3_CHECKPOINT_RELATIVE_POW_ANCESTRY": "PASS",
        },
        "proof_material": {
            "path": str(rel),
            "size": proof_path.stat().st_size,
            "sha256": sha256_file(proof_path),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ANNEX_DIR / "proof-material",
        help="proof-material output directory",
    )
    parser.add_argument("--manifest", type=Path, default=ANNEX_DIR / "ANNEX-MANIFEST.json")
    args = parser.parse_args()

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    mirrors = mirror_records()
    anchors = authority_anchors()
    if set(mirrors) != {str(item["inscription_id"]) for item in anchors}:
        raise SystemExit("mirror/authority inscription closed set mismatch")

    captured = []
    for anchor in anchors:
        inscription_number = str(anchor["inscription_id"])
        mirror, mirror_path = mirrors[inscription_number]
        captured.append(capture_anchor(anchor, mirror, mirror_path, output_dir))

    primitives = Path(__file__).with_name("bitcoin_proof_primitives_v1.py")
    verifier = Path(__file__).with_name("verify_annex.py")
    manifest = {
        "schema": "trinityaccord.bitcoin-inscription-proof-carrying-annex.v1",
        "version": "1.0.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "created_from_git_commit": git_head(),
        "network": {"name": "Bitcoin Mainnet", "chain": "main", "bech32_hrp": "bc"},
        "authority_boundary": {
            "canonical_authority": "three Bitcoin Originals only",
            "canonical_original_count": 3,
            "ancillary_inscriptions_non_amending": True,
            "proof_annex_is_non_amending": True,
            "no_authority_escalation": True,
        },
        "claim_model": {
            "L1_INSCRIPTION_CONTENT_AND_TAPROOT_BINDING": "PASS only when the preserved reveal/prevout bytes recompute the declared txids, the txid+i0 envelope yields the declared exact body/content type, the tapscript and BIP341 control block commit to the referenced P2TR prevout, the observed BIP342 script shape executes with a valid BIP340 SIGHASH_DEFAULT signature, the mirror binding is explicit, and the reveal destination address matches.",
            "L2_BLOCK_AND_WITNESS_INCLUSION": "PASS only when the reveal txid reconstructs the block-header transaction Merkle root and the reveal wtxid reconstructs the BIP141 witness root whose commitment is in a coinbase transaction independently proven into the same block header.",
            "L3_CHECKPOINT_RELATIVE_POW_ANCESTRY": "PASS only when the target block header and 144 descendants form a contiguous valid-PoW Bitcoin-mainnet header chain to an explicit checkpoint observed consistently by two providers.",
            "checkpoint_rule": "The offline proof verifies actual header work and ancestry. Provider observations are capture provenance only. The result remains checkpoint-relative and is not a substitute for full-node validation from genesis or a proof that no heavier competing chain exists.",
            "time_rule": "Bitcoin header timestamps are consensus header fields with protocol bounds; they are not absolute physical-world clocks.",
        },
        "closed_set": {
            "inscription_count": 8,
            "canonical_originals": 3,
            "non_amending_ancillary": 5,
            "source": "archive/authority-manifest/authority.jcs.json",
        },
        "verification_implementation": {
            "verifier": str(verifier.relative_to(REPO_ROOT)),
            "verifier_sha256": sha256_file(verifier),
            "frozen_primitives": str(primitives.relative_to(REPO_ROOT)),
            "frozen_primitives_sha256": sha256_file(primitives),
            "runtime": "Python 3 standard library only",
            "network_required_for_verification": False,
            "network_required_for_controlled_capture": True,
        },
        "preservation_policy": {
            "proof_material_git_tracked": True,
            "future_repository_capsule_coverage": "Automatically included in the next authorized repository preservation capsule because every annex byte is Git-tracked.",
            "current_published_repository_doi_boundary": "The repository DOI published before this annex remains an exact older baseline and must not be claimed to contain these proof bytes.",
            "runtime_self_containment": "Ordinary verification uses only Python 3 standard-library modules; no package-index artifact is required.",
        },
        "anchors": captured,
        "does_not_prove": [
            "full Bitcoin consensus validity from genesis",
            "absence of a heavier competing chain",
            "civil identity or authorship",
            "philosophical truth",
            "absolute physical-world time",
            "that no other related Bitcoin transactions exist",
        ],
    }
    write_json(args.manifest, manifest)
    print(f"captured {len(captured)} Bitcoin inscription proof witnesses")
    return 0


if __name__ == "__main__":
    sys.exit(main())
