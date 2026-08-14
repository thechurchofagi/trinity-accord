#!/usr/bin/env python3
"""Converge current Bitcoin evidence surfaces on the verified 12-item v2 annex.

This script is deliberately non-publication-aware: it updates current cryptographic
proof truth while preserving the latest already-published repository DOI pointers.
A later publication reconciliation may advance those DOI pointers only after public
cold-restore verification succeeds.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
V2_MANIFEST = ROOT / "evidence/bitcoin-inscription-proof-annex-v2/ANNEX-MANIFEST.json"
V2_REPORT = ROOT / "evidence/bitcoin-inscription-proof-annex-v2/reports/OFFLINE-VERIFICATION.json"
V1_MANIFEST = "evidence/bitcoin-inscription-proof-annex-v1/ANNEX-MANIFEST.json"
V1_REPORT = "evidence/bitcoin-inscription-proof-annex-v1/reports/OFFLINE-VERIFICATION.json"
V1_VERIFIER = "evidence/bitcoin-inscription-proof-annex-v1/verification/verify_annex.py"
V2_MANIFEST_REL = "evidence/bitcoin-inscription-proof-annex-v2/ANNEX-MANIFEST.json"
V2_REPORT_REL = "evidence/bitcoin-inscription-proof-annex-v2/reports/OFFLINE-VERIFICATION.json"
V2_VERIFIER = "evidence/bitcoin-inscription-proof-annex-v2/verification/verify_annex.py"
PRIMITIVES = "evidence/bitcoin-inscription-proof-annex-v1/verification/bitcoin_proof_primitives_v1.py"
ADDRESS = "bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf"


def load(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise SystemExit(f"JSON object required: {path}")
    return obj


def dump(path: Path, obj: dict[str, Any]) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def verified_inputs() -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = load(V2_MANIFEST)
    report = load(V2_REPORT)
    if manifest.get("schema") != "trinityaccord.bitcoin-inscription-proof-carrying-annex.v2":
        raise SystemExit("unexpected Bitcoin v2 manifest schema")
    if report.get("result") != "PASS":
        raise SystemExit("Bitcoin v2 offline verification is not PASS")
    l1 = report["L1_INSCRIPTION_CONTENT_METADATA_AND_TAPROOT_BINDING"]
    l2 = report["L2_BLOCK_AND_WITNESS_INCLUSION"]
    l3 = report["L3_CHECKPOINT_RELATIVE_POW_ANCESTRY"]
    expected = {
        "inscriptions": 12,
        "pre_canonical_formation": 4,
        "canonical_originals": 3,
        "post_canonical_non_amending": 5,
        "tag5_metadata_present": 1,
        "tag5_metadata_absent_verified": 11,
    }
    for key, value in expected.items():
        if l1.get(key) != value:
            raise SystemExit(f"Bitcoin v2 L1 mismatch: {key}")
    if l2.get("reveal_transactions") != 12 or l2.get("bip141_witness_commitment_proofs") != 12:
        raise SystemExit("Bitcoin v2 L2 does not cover 12")
    if l3.get("anchors") != 12 or l3.get("descendant_confirmation_depth_per_anchor") != 144:
        raise SystemExit("Bitcoin v2 L3 does not cover 12x144")
    if len(manifest.get("anchors", [])) != 12:
        raise SystemExit("Bitcoin v2 manifest anchor count mismatch")
    return manifest, report


def inventory_items(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for anchor in manifest["anchors"]:
        item = {
            "classification": anchor["classification"],
            "historical_layer": anchor["historical_layer"],
            "title": anchor.get("title"),
            "inscription_number": str(anchor["inscription_number"]),
            "derived_inscription_id": anchor["ordinals_inscription_id"],
            "txid": anchor["txid"],
            "wtxid": anchor["wtxid"],
            "block_height": anchor["block_reference"]["height"],
            "block_hash": anchor["block_reference"]["hash"],
            "body_sha256": anchor["content"]["body_sha256"],
            "tag5_metadata_present": anchor["inscription_metadata"]["present"],
            "tag5_metadata_sha256": anchor["inscription_metadata"]["sha256"],
        }
        out.append(item)
    return out


def update_final_inventory(manifest: dict[str, Any], report: dict[str, Any]) -> None:
    path = ROOT / "api/final-evidence-inventory.v1.json"
    doc = load(path)
    doc["version"] = "1.2.0"
    doc["status"] = "current_verified_evidence_model_with_historical_published_checkpoints"
    bitcoin = doc["evidence_sets"]["bitcoin_inscriptions"]
    bitcoin.update({
        "object_role": "complete observed current-address Bitcoin history: four pre-canonical formation records, three canonical Originals, and five post-canonical non-amending records",
        "count": 12,
        "pre_canonical_formation": 4,
        "canonical_originals": 3,
        "post_canonical_non_amending": 5,
        "items": inventory_items(manifest),
        "proof_layers": {
            "L1": {
                "status": "PASS",
                "inscriptions": 12,
                "pre_canonical_formation": 4,
                "canonical_originals": 3,
                "post_canonical_non_amending": 5,
                "tag5_metadata_present": 1,
                "tag5_metadata_absent_verified": 11,
            },
            "L2": {
                "status": "PASS",
                "reveal_transactions": 12,
                "txid_merkle_proofs": 12,
                "bip141_witness_commitment_proofs": 12,
            },
            "L3": {
                "status": "PASS",
                "anchors": 12,
                "descendant_confirmation_depth_per_anchor": 144,
                "valid_pow_headers": report["L3_CHECKPOINT_RELATIVE_POW_ANCESTRY"]["valid_pow_headers"],
            },
        },
        "manifest": V2_MANIFEST_REL,
        "offline_report": V2_REPORT_REL,
        "verifier": V2_VERIFIER,
        "frozen_primitives": PRIMITIVES,
        "runtime": "Python 3 standard library only",
        "network_required_for_verification": False,
        "historical_proof_checkpoint_v1": {
            "scope": "3 canonical Originals + 5 post-canonical non-amending records",
            "count": 8,
            "manifest": V1_MANIFEST,
            "offline_report": V1_REPORT,
            "verifier": V1_VERIFIER,
            "immutable_historical_checkpoint": True,
        },
        "snapshot_boundary": "The 12-item set is the complete current set returned by the Ord address endpoint at the first complete observation on 2026-08-14; it does not prove that no inscription left the address earlier.",
        "authority_boundary": "Only the three designated Bitcoin Originals are canonical. The four formation records and five later records are non-canonical and non-amending.",
    })
    bitcoin.pop("non_amending_ancillary", None)
    dump(path, doc)


def update_evidence_manifest(report: dict[str, Any]) -> None:
    path = ROOT / "api/evidence-manifest.json"
    doc = load(path)
    state = doc["current_cryptographic_proof_state"]
    state["status"] = "offline_verifiable_current_bitcoin_v2_plus_published_repository_checkpoint_v4"
    state["updated_scope"] = "2026-08 complete 12-item Bitcoin current-address proof v2, 12 non-NFT Ethereum anchors, and 175 Chronicle NFTs"
    btc = state["bitcoin_inscriptions"]
    btc.update({
        "inscription_count": 12,
        "pre_canonical_formation": 4,
        "canonical_originals": 3,
        "post_canonical_non_amending": 5,
        "l1_inscription_content_metadata_and_taproot_binding": "PASS",
        "bip340_tapscript_signatures": 12,
        "l2_block_and_witness_inclusion": "PASS",
        "l3_checkpoint_relative_pow_ancestry": "PASS",
        "txid_merkle_proofs": 12,
        "bip141_witness_commitment_proofs": 12,
        "descendant_confirmation_depth_per_anchor": 144,
        "valid_pow_headers": report["L3_CHECKPOINT_RELATIVE_POW_ANCESTRY"]["valid_pow_headers"],
        "tag5_metadata_present": 1,
        "tag5_metadata_absent_verified": 11,
        "reveal_destination_p2tr_address": ADDRESS,
        "manifest": V2_MANIFEST_REL,
        "offline_report": V2_REPORT_REL,
        "verifier": V2_VERIFIER,
        "frozen_primitives": PRIMITIVES,
        "runtime": "Python 3 standard library only",
        "network_required_for_verification": False,
        "historical_v1_checkpoint": {
            "count": 8,
            "manifest": V1_MANIFEST,
            "offline_report": V1_REPORT,
            "verifier": V1_VERIFIER,
            "status": "immutable_historical_checkpoint",
        },
        "snapshot_boundary": "Current-address 12-item snapshot observed 2026-08-14; not an all-time no-departure claim.",
        "authority_boundary": "Only three Bitcoin Originals are canonical; proof parity does not elevate the four formation records or five later records.",
    })
    btc.pop("non_amending_ancillary", None)
    btc.pop("l1_inscription_content_and_taproot_binding", None)
    repo = state.get("repository_preservation", {})
    delta = repo.setdefault("live_repository_delta", {})
    delta.update({
        "status": "bitcoin_v2_verified_in_git_pending_next_repository_preservation_version",
        "bitcoin_proof_v2_additions": 4,
        "bitcoin_current_proof_count": 12,
        "independent_tag5_cbor_metadata_now_archived": 1,
        "new_doi_publication": "required_for_current_git_delta_not_yet_claimed_here",
        "new_arweave_upload": "required_for_current_git_delta_not_yet_claimed_here",
        "recovery_boundary": "The currently named older DOI remains an exact historical publication baseline until a new version is publicly verified. Current Git v2 proof bytes are not retroactively attributed to it.",
    })
    dump(path, doc)


def update_relationship_map() -> None:
    path = ROOT / "api/evidence-relationship-map.v1.json"
    doc = load(path)
    nodes = {node["id"]: node for node in doc["nodes"]}
    inv = nodes["final_evidence_inventory"]
    inv["scope"]["bitcoin_inscriptions"] = 12
    inv["freeze_role"] = "current verified machine inventory; immutable repository DOI checkpoint v4 remains separately identified as an 8-Bitcoin historical publication baseline"
    inv["role"] = "Current machine inventory exposes 12 verified Bitcoin inscriptions while preserving the older 8 + 12 + 175 DOI checkpoint as immutable history."

    live = nodes["current_live_evidence_state"]
    live["scope"]["bitcoin_inscriptions"] = 12
    live["role"] = "Exposes current verified 12 Bitcoin + 12 Ethereum + 175 NFT evidence, while separately naming older immutable DOI scopes."
    live["published_checkpoint_v4_scope"]["bitcoin_inscriptions"] = 8

    proof = nodes["bitcoin_inscription_proof_annex"]
    proof.update({
        "manifest": V2_MANIFEST_REL,
        "offline_report": V2_REPORT_REL,
        "verifier": V2_VERIFIER,
        "scope": {
            "pre_canonical_formation": 4,
            "canonical_originals": 3,
            "post_canonical_non_amending": 5,
            "total": 12,
        },
        "layers": [
            "L1_INSCRIPTION_CONTENT_METADATA_AND_TAPROOT_BINDING",
            "L2_BLOCK_AND_WITNESS_INCLUSION",
            "L3_CHECKPOINT_RELATIVE_POW_ANCESTRY",
        ],
        "network_required_for_verification": False,
        "supports": [
            "exact_inscription_body",
            "exact_ord_tag5_metadata_or_verified_absence",
            "taproot_prevout_binding",
            "bip340_tapscript_signature",
            "txid_block_inclusion",
            "bip141_witness_inclusion",
            "checkpoint_relative_pow_ancestry",
        ],
        "historical_v1_checkpoint": {
            "manifest": V1_MANIFEST,
            "offline_report": V1_REPORT,
            "verifier": V1_VERIFIER,
            "total": 8,
            "status": "immutable_historical_checkpoint",
        },
    })
    dump(path, doc)


def update_recovery_catalog() -> None:
    path = ROOT / "preservation/recovery-catalog.json"
    doc = load(path)
    core = doc["core_repository"]
    core["current_git_verified_bitcoin_proof"] = {
        "status": "PASS",
        "count": 12,
        "pre_canonical_formation": 4,
        "canonical_originals": 3,
        "post_canonical_non_amending": 5,
        "manifest": V2_MANIFEST_REL,
        "offline_report": V2_REPORT_REL,
        "verifier": V2_VERIFIER,
        "published_repository_version_boundary": "The current verified v2 proof is Git-tracked after the currently named checkpoint DOI. Do not attribute v2 bytes to an older DOI; resolve the concept DOI after the next verified publication.",
    }
    checkpoint = core["current_evidence_checkpoint"]
    checkpoint["historical_scope_note"] = "Immutable checkpoint v4 predates the 12-item Bitcoin v2 proof and remains correctly described as an 8-Bitcoin publication baseline."
    order = doc["recovery_order"]
    order[3] = "Run the checked-in current offline verifier for the 12-item Bitcoin v2 snapshot, plus the Ethereum and 175-item NFT verifiers; when restoring an older DOI, respect that version's historical Bitcoin scope."
    dump(path, doc)


def update_human_pages() -> None:
    path = ROOT / "authority-address-inscriptions.md"
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "| 2025-01-30 05:03:20 | #83928339 | [`8e81cf6054d37dc1f4606fa4f3fba238024292d72511fa70eeee693626271695i0`](https://ordinals.com/inscription/8e81cf6054d37dc1f4606fa4f3fba238024292d72511fa70eeee693626271695i0) | Early WebP visual artifact. Title/identity not inferred without independent evidence. |",
        "| 2025-01-30 05:03:20 | #83928339 | [`8e81cf6054d37dc1f4606fa4f3fba238024292d72511fa70eeee693626271695i0`](https://ordinals.com/inscription/8e81cf6054d37dc1f4606fa4f3fba238024292d72511fa70eeee693626271695i0) | *ASIMilestones: Permanently engraved the moment of the open-source release of DeepSeek-R1* — WebP body whose independent Ord tag-5 CBOR metadata supplies this title and additional historical context. |",
    )
    old_start = "The older curated 3 + 5 set additionally carries the existing proof-carrying Bitcoin annex."
    old_end = "| #103635270 | Address-wide archive + existing curated L1/L2/L3 offline proof coverage |"
    if old_start not in text or old_end not in text:
        raise SystemExit("authority page old proof-status block not found")
    before, rest = text.split(old_start, 1)
    _, after = rest.split(old_end, 1)
    replacement = """The historical v1 annex remains an immutable 8-item checkpoint. The current v2 annex extends the same fail-closed, network-free proof model to the complete 12-item snapshot. All 12 now have exact inscription-body binding, exact Ord tag-5 metadata binding (including verified absence), Taproot/BIP340 verification, BIP141 witness inclusion, and 144-block checkpoint-relative proof-of-work ancestry. This proof parity changes evidence strength, not authority: the four formation records remain non-canonical and the five later records remain non-amending.\n\n| Inscription Number | Current proof status |\n|---:|---|\n| #83928339 | v2 L1/L2/L3 PASS · independent tag-5 CBOR metadata present and bound |\n| #97406645 | v2 L1/L2/L3 PASS · tag-5 metadata absence verified |\n| #97446192 | v2 L1/L2/L3 PASS · tag-5 metadata absence verified |\n| #97534036 | v2 L1/L2/L3 PASS · tag-5 metadata absence verified |\n| #97631551 | v2 L1/L2/L3 PASS · also preserved in historical v1 |\n| #98369145 | v2 L1/L2/L3 PASS · also preserved in historical v1 |\n| #98387475 | v2 L1/L2/L3 PASS · also preserved in historical v1 |\n| #100385359 | v2 L1/L2/L3 PASS · also preserved in historical v1 |\n| #100550942 | v2 L1/L2/L3 PASS · also preserved in historical v1 |\n| #100751953 | v2 L1/L2/L3 PASS · also preserved in historical v1 |\n| #103034280 | v2 L1/L2/L3 PASS · also preserved in historical v1 |\n| #103635270 | v2 L1/L2/L3 PASS · also preserved in historical v1 |"""
    text = before + replacement + after
    text = text.replace(
        "# Existing curated 3 + 5 offline proof verifier\npython3 scripts/verify_bitcoin_inscription_mirrors.py --offline --all",
        "# Current complete 12-item offline proof verifier\npython3 evidence/bitcoin-inscription-proof-annex-v2/verification/verify_annex.py\n\n# Historical immutable 3 + 5 v1 verifier\npython3 evidence/bitcoin-inscription-proof-annex-v1/verification/verify_annex.py",
    )
    text = text.replace("- The four recovered formation records do not yet have the curated set's checked-in L1/L2/L3 Bitcoin proof-annex coverage.\n", "")
    path.write_text(text, encoding="utf-8")

    readme = ROOT / "bitcoin-inscription-mirrors/README.md"
    r = readme.read_text(encoding="utf-8")
    r = r.replace(
        "checked-in, proof-carrying Bitcoin annex, so the on-chain comparison can be\nreproduced cryptographically without a network connection.",
        "checked-in, proof-carrying Bitcoin annexes, so the on-chain comparison can be\nreproduced cryptographically without a network connection. V1 preserves the historical\ncurated eight; v2 covers the complete 12-item current-address snapshot first observed\non 14 August 2026, including exact Ord tag-5 CBOR metadata bytes or verified absence.",
    )
    r = r.replace(
        "- Run `python3 evidence/bitcoin-inscription-proof-annex-v1/verification/verify_annex.py`\n  for the fail-closed, network-free comparison.",
        "- Run `python3 evidence/bitcoin-inscription-proof-annex-v2/verification/verify_annex.py`\n  for the current complete 12-item fail-closed, network-free comparison.\n- V1 remains an immutable historical 8-item checkpoint and is not rewritten by v2.",
    )
    readme.write_text(r, encoding="utf-8")


def main() -> int:
    manifest, report = verified_inputs()
    update_final_inventory(manifest, report)
    update_evidence_manifest(report)
    update_relationship_map()
    update_recovery_catalog()
    update_human_pages()
    print("Bitcoin 12-item v2 evidence surfaces finalized without advancing unpublished DOI/Arweave pointers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
