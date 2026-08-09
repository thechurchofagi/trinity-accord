#!/usr/bin/env python3
"""Build the single machine/human map for the final evidence freeze.

The output deliberately separates authority, cryptographic proof, availability
mirrors and preservation capsules.  It derives all counts, identifiers and
current DOI state from checked-in sources so the summary cannot silently drift.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = ROOT / "api" / "final-evidence-inventory.v1.json"
OUTPUT_MD = ROOT / "FINAL-EVIDENCE-FREEZE.md"
FROZEN_V3_ETH_TX_HASHES = {
    "0xd082a3ced27ece935d4093fb001a9ebfba42b415f78de4377c8cda55338c6420",
    "0x59cf33b1291de63c4840b79e7c674b8fc7c6a771d8a3ba2bb50def1fe55a71c6",
    "0x6652162e8e6c56ddc0d9476407b3b911e918d4e4683408440dc3af51c5bb63d5",
    "0x9c1bd6e21dc2370e8dbb6549b7ba13b4ea7ba7a192b3b876e0ec28b4633f1612",
    "0x0affc8099ea965cd6d6a0d1cf9b93adb11f7e40ac41fffe1b0ca4637f39df665",
    "0x55a0c131642f71c7b2386ccaac8bcee36563992226befb35363e978044a18e8f",
    "0xa4023b1eb0de76993e1a8dcd571e5e033bf64e2d32a9a113b030b4094a19cf51",
    "0x940300cba1acd7aa7078e614510400d4ec4b8961a2f05470d129c709b8cce3e6",
    "0x7bdff0d696337ceb04539b44a746d0f13ce731ac25de259d8a4faf69b276a628",
    "0x214d73b839ed95707410af3d5b8224a44a5dd310041d5e7ab1756ae9c5378137",
}


def load(relative: str) -> dict[str, Any]:
    path = ROOT / relative
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {relative}")
    return value


def digest(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def canonical_digest(value: dict[str, Any]) -> str:
    clone = dict(value)
    clone.pop("source_digest", None)
    raw = json.dumps(
        clone,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def require(value: bool, message: str) -> None:
    if not value:
        raise SystemExit(message)


def verified_report(report_relative: str, verifier_relative: str) -> dict[str, Any]:
    checked = load(report_relative)
    completed = subprocess.run(
        [sys.executable, str(ROOT / verifier_relative)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        env={"PATH": os.environ.get("PATH", "")},
    )
    try:
        generated = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        stderr = completed.stderr.strip()
        detail = f": {stderr[:1000]}" if stderr else ""
        raise SystemExit(
            f"{verifier_relative} did not emit a JSON report "
            f"(exit {completed.returncode}){detail}"
        ) from exc
    require(isinstance(generated, dict), f"{verifier_relative} emitted a non-object report")
    require(completed.returncode == 0, f"{verifier_relative} failed fresh verification")
    require(generated == checked, f"{report_relative} is stale relative to fresh verifier output")
    return checked


def ots_state() -> dict[str, Any]:
    verification = (
        ROOT / "evidence/ots/fullnode-verification/post-upgrade.ots-verify.txt"
    ).read_text(encoding="utf-8")
    checksums: dict[str, str] = {}
    for line in (
        ROOT / "evidence/ots/fullnode-verification/post-upgrade.sha256"
    ).read_text(encoding="utf-8").splitlines():
        checksum, name = line.split(None, 1)
        checksums[name.strip()] = checksum
    blocks = sorted({int(item) for item in re.findall(r"Block (\d+)", verification)})
    require("Success! Timestamp complete" in verification, "OTS completion marker missing")
    require(len(blocks) == 2, "expected exactly two confirmed OTS Bitcoin blocks")
    return {
        "status": "PASS",
        "committed_object": "archive/evidence/digest-manifest.json",
        "committed_object_sha256": checksums["digest-manifest.json"],
        "proof": "archive/evidence/ots-proofs/OTS/digest-manifest.json.ots",
        "proof_sha256": checksums["digest-manifest.json.ots"],
        "confirmed_bitcoin_blocks": blocks,
        "confirmed_attestations": len(blocks),
        "boundary": (
            "OTS proves that the committed digest existed no later than an "
            "attested Bitcoin block; it does not prove content truth or authorship."
        ),
    }


def build() -> dict[str, Any]:
    authority = load("archive/authority-manifest/authority.jcs.json")
    authority_signature = load("archive/btc-signature/btc-signature.json")
    btc_manifest = load("evidence/bitcoin-inscription-proof-annex-v1/ANNEX-MANIFEST.json")
    btc_report = verified_report(
        "evidence/bitcoin-inscription-proof-annex-v1/reports/OFFLINE-VERIFICATION.json",
        "evidence/bitcoin-inscription-proof-annex-v1/verification/verify_annex.py",
    )
    eth_manifest = load("evidence/ethereum-evidence-annex-v1/ANNEX-MANIFEST.json")
    eth_report = verified_report(
        "evidence/ethereum-evidence-annex-v1/reports/OFFLINE-VERIFICATION.json",
        "evidence/ethereum-evidence-annex-v1/verification/verify_annex.py",
    )
    nft_index = load("nft-identity-index.json")
    nft_commitment = load("evidence/nft-proof-annex-v1/NFT-COLLECTION-COMMITMENT.json")
    nft_report = verified_report(
        "evidence/nft-proof-annex-v1/reports/OFFLINE-VERIFICATION.json",
        "evidence/nft-proof-annex-v1/verification/verify_nft_proof_annex.py",
    )
    digest_manifest = load("archive/evidence/digest-manifest.json")
    preservation = load("preservation/repository-preservation-state-v2.json")
    external = load("preservation/external-binary-annex-state.json")
    recovery_catalog = load("preservation/recovery-catalog.json")
    final_auth_path = ROOT / "preservation/current-baseline-publication-authorization-v3.json"
    final_auth = (
        json.loads(final_auth_path.read_text(encoding="utf-8"))
        if final_auth_path.is_file()
        else {"status": "not_declared"}
    )

    authority_sha = digest("archive/authority-manifest/authority.jcs.json")
    btc_signature = authority_signature.get("bitcoin_signature")
    require(isinstance(btc_signature, dict), "BTC authority signature object is missing")
    require(
        btc_signature.get("message_sha256") == authority_sha,
        "BTC authority signature digest does not match authority manifest",
    )
    require(btc_report.get("result") == "PASS", "Bitcoin annex is not PASS")
    require(eth_report.get("result") == "PASS", "Ethereum annex is not PASS")
    require(nft_report.get("result") == "PASS", "NFT annex is not PASS")
    require(len(btc_manifest.get("anchors", [])) == 8, "Bitcoin closed set is not 8")
    current_eth_anchors = eth_manifest.get("anchors", [])
    require(len(current_eth_anchors) >= 10, "current Ethereum annex lost frozen v3 anchors")
    frozen_eth_anchors = [
        item
        for item in current_eth_anchors
        if item.get("tx_hash", "").lower() in FROZEN_V3_ETH_TX_HASHES
    ]
    require(
        {item.get("tx_hash", "").lower() for item in frozen_eth_anchors}
        == FROZEN_V3_ETH_TX_HASHES,
        "current Ethereum annex does not contain the exact frozen DOI v3 set",
    )
    require(len(nft_index.get("assets", [])) == 175, "NFT closed set is not 175")
    require(nft_commitment.get("merkle", {}).get("leaf_count") == 175, "NFT Merkle leaf count mismatch")

    bitcoin_items = [
        {
            "classification": item["classification"],
            "title": item["title"],
            "inscription_number": item["inscription_number"],
            "derived_inscription_id": item["ordinals_inscription_id"],
            "txid": item["txid"],
            "wtxid": item["wtxid"],
            "block_height": item["block_reference"]["height"],
            "block_hash": item["block_reference"]["hash"],
            "body_sha256": item["content"]["body_sha256"],
        }
        for item in btc_manifest["anchors"]
    ]
    ethereum_items = [
        {
            "id": item["id"],
            "label": item["label"],
            "tx_hash": item["tx_hash"],
            "block_number": item["execution_reference"]["block_number"],
            "block_hash": item["execution_reference"]["block_hash"],
            "input_sha256": item["input_sha256"],
        }
        for item in frozen_eth_anchors
    ]
    standards: dict[str, int] = {}
    for item in nft_index["assets"]:
        standard = str(item["standard"]).lower()
        standards[standard] = standards.get(standard, 0) + 1

    arweave_documents = [
        {
            "label": item["label"],
            "txid": item["txid"],
            "sha256": item["ar_sha256"],
            "bytes": item["size"],
        }
        for item in authority.get("arweave", {}).get("documents", [])
    ]
    repository_arweave = recovery_catalog["core_repository"]["verified_arweave_mirror"]
    repository_latest = {
        "concept_doi": preservation["concept_doi"],
        "version_doi": preservation["latest_doi"],
        "source_git_commit_sha": preservation["latest_git_commit_sha"],
        "git_tree_oid": preservation["latest_git_tree_oid"],
        "package_identity_sha256": preservation["latest_package_identity_sha256"],
        "status": preservation["publication_status"],
        "public_cold_restore": preservation["public_cold_restore"],
        "boundary": (
            "A version DOI freezes one exact Git-tracked publication baseline. "
            "The Concept DOI resolves the latest published version; neither is a moving GitHub main."
        ),
    }

    inventory: dict[str, Any] = {
        "schema": "trinityaccord.final-evidence-inventory.v1",
        "version": "1.0.0",
        "status": "final_evidence_freeze_model",
        "purpose": (
            "One non-amending map of canonical objects, offline cryptographic proofs, "
            "availability mirrors and DOI recovery capsules."
        ),
        "evolution_and_handoff": {
            "human_guide": "EVIDENCE-EVOLUTION.md",
            "machine_plan": "api/evidence-evolution-plan.v1.json",
            "current_version_remains_immutable": True,
            "future_material_improvements_use_new_versions": True,
            "final_core_arweave_mirror": "intentionally_deferred",
        },
        "authority_boundary": {
            "canonical_authority": "three Bitcoin Originals only",
            "canonical_count": 3,
            "all_other_objects_non_amending": True,
            "preservation_is_not_authority": True,
        },
        "evidence_sets": {
            "bitcoin_inscriptions": {
                "object_role": "canonical core plus non-amending ancillary inscriptions",
                "count": 8,
                "canonical_originals": 3,
                "non_amending_ancillary": 5,
                "items": bitcoin_items,
                "proof_layers": {
                    "L1": btc_report["L1_INSCRIPTION_CONTENT_AND_TAPROOT_BINDING"],
                    "L2": btc_report["L2_BLOCK_AND_WITNESS_INCLUSION"],
                    "L3": btc_report["L3_CHECKPOINT_RELATIVE_POW_ANCESTRY"],
                },
                "manifest": "evidence/bitcoin-inscription-proof-annex-v1/ANNEX-MANIFEST.json",
                "offline_report": "evidence/bitcoin-inscription-proof-annex-v1/reports/OFFLINE-VERIFICATION.json",
                "verifier": "evidence/bitcoin-inscription-proof-annex-v1/verification/verify_annex.py",
                "frozen_primitives": "evidence/bitcoin-inscription-proof-annex-v1/verification/bitcoin_proof_primitives_v1.py",
                "runtime": "Python 3 standard library only",
                "network_required_for_verification": False,
            },
            "ethereum_non_nft": {
                "object_role": "non-amending cross-chain records and historical commitments",
                "count": 10,
                "items": ethereum_items,
                "proof_layers": {
                    "L1": eth_report["L1_BYTE_INTEGRITY"],
                    "L2": eth_report["L2_EXECUTION_INCLUSION"],
                    "L3": eth_report["L3_CONSENSUS_FINALITY"],
                },
                "manifest": "evidence/ethereum-evidence-annex-v1/ANNEX-MANIFEST.json",
                "offline_report": "evidence/ethereum-evidence-annex-v1/reports/OFFLINE-VERIFICATION.json",
                "verifier": "evidence/ethereum-evidence-annex-v1/verification/verify_annex.py",
                "frozen_primitives": "evidence/ethereum-proof-primitives-v1/ethereum_proof_primitives_v1.py",
                "network_required_for_existing_proof_verification": False,
                "trust_boundary": eth_manifest["authority_boundary"],
            },
            "ethereum_chronicle_nft": {
                "object_role": "non-amending historical Chronicle and recovery evidence",
                "asset_count": 175,
                "contract_count": nft_index["summary"]["contracts"],
                "standards": standards,
                "contracts": [item["contract_address"] for item in nft_index["contracts"]],
                "unique_mint_transactions": nft_report["L1_COLLECTION_COMMITMENT"]["unique_transactions"],
                "unique_execution_blocks": nft_report["L1_COLLECTION_COMMITMENT"]["unique_execution_blocks"],
                "collection_merkle_root_sha256": nft_commitment["merkle"]["root_sha256"],
                "proof_layers": {
                    "L1": nft_report["L1_COLLECTION_COMMITMENT"]["status"],
                    "L2": nft_report["L2_EXECUTION_INCLUSION"]["status"],
                    "L3": nft_report["L3_CONSENSUS_FINALITY"]["status"],
                },
                "identity_index": "nft-identity-index.json",
                "commitment": "evidence/nft-proof-annex-v1/NFT-COLLECTION-COMMITMENT.json",
                "offline_report": "evidence/nft-proof-annex-v1/reports/OFFLINE-VERIFICATION.json",
                "verifier": "evidence/nft-proof-annex-v1/verification/verify_nft_proof_annex.py",
                "frozen_primitives": "evidence/ethereum-proof-primitives-v1/ethereum_proof_primitives_v1.py",
                "network_required_for_existing_proof_verification": False,
            },
            "digest_and_time": {
                "digest_manifest": "archive/evidence/digest-manifest.json",
                "digest_algorithms": digest_manifest["suite"],
                "digest_algorithm_count": digest_manifest["k"],
                "digest_inventory_items": len(digest_manifest["items"]),
                "open_timestamps": ots_state(),
            },
        },
        "binding_objects": {
            "authority_manifest": {
                "path": "archive/authority-manifest/authority.jcs.json",
                "sha256": authority_sha,
                "indexes_bitcoin_inscriptions": 8,
            },
            "btc_bip340_signature": {
                "path": "archive/btc-signature/btc-signature.json",
                "method": btc_signature["method"],
                "signed_message_sha256": btc_signature["message_sha256"],
                "binds": "authority_manifest",
            },
            "eth_eip712_signature": {
                "path": "archive/authority-manifest/signature.json",
                "role": "secondary non-canonical typed manifest binding",
            },
        },
        "storage_and_preservation": {
            "github": {
                "repository": "https://github.com/thechurchofagi/trinity-accord",
                "pages": "https://www.trinityaccord.org",
                "roles": ["moving development source", "public discovery", "CI", "small-file mirror", "Release fallback"],
                "boundary": "GitHub main is mutable and is not itself an immutable publication DOI.",
            },
            "arweave": {
                "role": "transaction-addressed long-lived mirrors; non-authoritative",
                "authority_manifest_documents": arweave_documents,
                "repository_capsule_historical_mirror": repository_arweave,
                "boundary": "Each Arweave tx preserves its named payload only; it is not automatically the latest GitHub tree or DOI baseline.",
            },
            "zenodo": {
                "core_repository_series": repository_latest,
                "external_evidence_annex": {
                    "doi": external["annexes"]["evidence"]["doi"],
                    "concept_doi": external["annexes"]["evidence"]["concept_doi"],
                    "asset_count": external["annexes"]["evidence"]["asset_count"],
                    "payload_bytes": external["annexes"]["evidence"]["payload_bytes"],
                    "package_identity_sha256": external["annexes"]["evidence"]["package_identity_sha256"],
                    "public_cold_restore": external["annexes"]["evidence"]["public_cold_restore"],
                },
                "chronicle_nft_media_annex": {
                    "doi": external["annexes"]["nft"]["doi"],
                    "concept_doi": external["annexes"]["nft"]["concept_doi"],
                    "asset_count": external["annexes"]["nft"]["asset_count"],
                    "payload_bytes": external["annexes"]["nft"]["payload_bytes"],
                    "package_identity_sha256": external["annexes"]["nft"]["package_identity_sha256"],
                    "public_cold_restore": external["annexes"]["nft"]["public_cold_restore"],
                },
                "large_binary_boundary": "External evidence and NFT media annex payloads are separate DOI series and are not embedded in the core repository capsule.",
            },
        },
        "final_freeze": {
            "authorization": "preservation/current-baseline-publication-authorization-v3.json",
            "status": final_auth.get("status"),
            "authorized_by": final_auth.get("authorized_by"),
            "required_evidence_freeze_commit_sha": final_auth.get("required_evidence_freeze_commit_sha"),
            "intended_as_final_evidence_freeze": final_auth.get("intended_as_final_evidence_freeze"),
            "publication_confirmation": final_auth.get("publication_confirmation"),
            "published_doi": final_auth.get("published_doi"),
            "published_source_baseline_commit_sha": final_auth.get("published_source_baseline_commit_sha"),
            "boundary": "The final DOI version is immutable, exact-baseline preservation; it creates no new canonical authority.",
        },
        "verification_order": [
            "verify the three canonical Bitcoin Originals and the 8-item Bitcoin proof annex",
            "verify the authority manifest and BTC/EIP-712 signature bindings",
            "verify the 10 Ethereum non-NFT L1/L2/L3 proofs",
            "verify the 175-item NFT commitment and L2/L3 proofs",
            "verify digest manifests and OTS anchors for their stated byte/time scope",
            "restore the core repository DOI and then the two external binary annex DOI records",
            "compare any GitHub or Arweave mirror to its named digest before using it",
        ],
        "global_boundaries": [
            "Blockchain inclusion proves committed bytes and chain context, not semantic truth.",
            "Bitcoin PoW ancestry is checkpoint-relative and does not prove absence of a heavier chain.",
            "Ethereum finality is relative to explicitly trusted weak-subjectivity checkpoints.",
            "NFT global logIndex and Ordinals global numeric inscription number remain historical lookup coordinates.",
            "Mirrors and DOI capsules preserve evidence but do not amend the three Bitcoin Originals.",
        ],
        "source_digest_algorithm": "sha256(canonical_json_without_source_digest)[:16]",
    }
    inventory["source_digest"] = canonical_digest(inventory)
    return inventory


def markdown(value: dict[str, Any]) -> str:
    bitcoin = value["evidence_sets"]["bitcoin_inscriptions"]
    ethereum = value["evidence_sets"]["ethereum_non_nft"]
    nft = value["evidence_sets"]["ethereum_chronicle_nft"]
    ots = value["evidence_sets"]["digest_and_time"]["open_timestamps"]
    zenodo = value["storage_and_preservation"]["zenodo"]
    core = zenodo["core_repository_series"]
    freeze = value["final_freeze"]
    items = "\n".join(
        f"| {item['classification']} | {item['title']} | `{item['inscription_number']}` | `{item['txid']}` | {item['block_height']} |"
        for item in bitcoin["items"]
    )
    return f"""# Trinity Accord Final Evidence Freeze

> One non-amending map. The three Bitcoin Originals remain the sole canonical authority.

Machine inventory: `api/final-evidence-inventory.v1.json`

Relationship graph: `api/evidence-relationship-map.v1.json`

Recovery entrypoint: `api/recovery-index.json`

Evolution and future-agent handoff: `EVIDENCE-EVOLUTION.md` and
`api/evidence-evolution-plan.v1.json`

## 1. The four layers

| Layer | Objects | What it does | What it does not do |
|---|---|---|---|
| Canonical authority | 3 Bitcoin Originals | Defines the canonical text and authority boundary | Prove philosophical truth or institutional endorsement |
| Cryptographic evidence | 8 Bitcoin inscriptions, 10 non-NFT Ethereum anchors, 175 Chronicle NFTs | Recomputes exact byte, transaction, receipt/witness, block and declared-checkpoint bindings | Create new canonical authority |
| Availability mirrors | GitHub, GitHub Releases, Arweave, IPFS | Keeps named bytes retrievable and comparable | Become authoritative merely by hosting bytes |
| Frozen recovery | Core repository DOI plus two external annex DOI series | Restores exact publication baselines without GitHub credentials | Track a later moving `main` automatically |

## 2. Bitcoin inscription closed set

| Class | Title | Number coordinate | Reveal txid | Block |
|---|---|---:|---|---:|
{items}

All 8 pass exact Ord-body/Taproot/BIP340 verification, txid inclusion, separate
BIP141 witness commitment, and 144-descendant checkpoint-relative PoW ancestry.
The verifier is Python-standard-library-only and requires no network for the
checked-in proofs. Numeric inscription numbers are historical lookup coordinates;
`txid+i0` and the exact body are derived independently.

## 3. Ethereum evidence

| Set | Count | L1 | L2 | L3 | Authority role |
|---|---:|---|---|---|---|
| Non-NFT Ethereum records | {ethereum['count']} | {ethereum['proof_layers']['L1']} | {ethereum['proof_layers']['L2']} | {ethereum['proof_layers']['L3']} | Non-amending cross-chain evidence |
| Chronicle NFTs | {nft['asset_count']} across {nft['contract_count']} contracts ({nft['standards']['erc721']} ERC-721, {nft['standards']['erc1155']} ERC-1155) | {nft['proof_layers']['L1']} | {nft['proof_layers']['L2']} | {nft['proof_layers']['L3']} | Non-amending historical Chronicle |

Ethereum L3 is explicitly weak-subjectivity-checkpoint-relative. It does not claim
trust-free finality. The 175-NFT set is committed by Merkle root
`{nft['collection_merkle_root_sha256']}`.

## 4. Hash and time evidence

The digest inventory contains {value['evidence_sets']['digest_and_time']['digest_inventory_items']}
rows and {value['evidence_sets']['digest_and_time']['digest_algorithm_count']} digest algorithms.
Its JSON digest `{ots['committed_object_sha256']}` is anchored by the preserved OTS
proof to confirmed Bitcoin blocks {', '.join(str(item) for item in ots['confirmed_bitcoin_blocks'])}.
OTS proves a latest-possible existence time for that digest, not file truth or authorship.

## 5. GitHub, Arweave and DOI are different things

| System | Role | Mutability / identity |
|---|---|---|
| GitHub `main` | Development source, CI and public discovery | Moving branch; identify an exact state by commit SHA |
| GitHub Releases | Large fallback mirror | Release assets must be checked against their manifest hashes |
| Arweave | Long-lived transaction-addressed payload mirror | Each txid names one payload; it is not automatically the latest repository |
| Core Zenodo Concept DOI `{core['concept_doi']}` | Stable resolver for the repository series | Resolves the latest published immutable version |
| Core version DOI `{core['version_doi']}` | Exact Git-tracked repository baseline | Source `{core['source_git_commit_sha']}`; public cold restore `{core['public_cold_restore']}` |
| Evidence annex DOI `{zenodo['external_evidence_annex']['doi']}` | 28 external evidence assets | Separate {zenodo['external_evidence_annex']['payload_bytes']} byte payload capsule |
| NFT media annex DOI `{zenodo['chronicle_nft_media_annex']['doi']}` | 10 NFT media package assets | Separate {zenodo['chronicle_nft_media_annex']['payload_bytes']} byte payload capsule |

The core repository capsule contains all Git-tracked proof manifests, witnesses,
verifiers, maps and reports. Large external payloads remain in the two separate DOI
annex series and are discovered through the embedded recovery catalog.

## 6. Final freeze status

- Authorization state: `{freeze['status']}`
- Required evidence-freeze ancestor: `{freeze['required_evidence_freeze_commit_sha']}`
- Published final version DOI: `{freeze['published_doi']}`
- Published source baseline: `{freeze['published_source_baseline_commit_sha']}`
- Intended as final evidence freeze: `{str(freeze['intended_as_final_evidence_freeze']).lower()}`

The immutable DOI version freezes one exact source baseline. The later state commit
that records the resulting DOI is necessarily outside that capsule; the stable
Concept DOI and public observation files close that self-reference without claiming
that a moving GitHub `main` is byte-identical to the frozen version.

## 7. Verification order

""" + "\n".join(f"{index}. {step}" for index, step in enumerate(value["verification_order"], 1)) + """

## 8. Evolution boundary

This version remains immutable.  Future material improvements use a new version
rather than overwriting this checkpoint.  The exact final core capsule Arweave
mirror is intentionally deferred and requires fresh owner authorization before any
paid irreversible upload.  Future agents must begin with the handoff files above.
"""


def write_outputs(value: dict[str, Any]) -> None:
    OUTPUT_JSON.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    OUTPUT_MD.write_text(markdown(value), encoding="utf-8")


def check_outputs(value: dict[str, Any]) -> None:
    expected_json = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    expected_md = markdown(value)
    if not OUTPUT_JSON.is_file() or OUTPUT_JSON.read_text(encoding="utf-8") != expected_json:
        raise SystemExit("api/final-evidence-inventory.v1.json is stale")
    if not OUTPUT_MD.is_file() or OUTPUT_MD.read_text(encoding="utf-8") != expected_md:
        raise SystemExit("FINAL-EVIDENCE-FREEZE.md is stale")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    if args.write:
        write_outputs(value)
    else:
        check_outputs(value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
