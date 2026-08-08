from __future__ import annotations

import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
EVIDENCE_MANIFEST = ROOT / "api" / "evidence-manifest.json"
EXTERNAL_ANNEX_STATE = ROOT / "preservation" / "external-binary-annex-state.json"
ETH_REPORT = ROOT / "evidence" / "ethereum-evidence-annex-v1" / "reports" / "OFFLINE-VERIFICATION.json"
NFT_REPORT = ROOT / "evidence" / "nft-proof-annex-v1" / "reports" / "OFFLINE-VERIFICATION.json"

CONCEPT_DOI = "10.5281/zenodo.21739343"
LATEST_REPOSITORY_DOI = "10.5281/zenodo.21846249"
HISTORICAL_CORE_VERSION_DOI = "10.5281/zenodo.21739344"
NFT_ROOT = "097bb48d98ab7fc036aed97f5b5fcb1a65962d64d327081277255d1829212267"


def load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def source_digest(data: dict) -> str:
    clone = dict(data)
    clone.pop("source_digest", None)
    canonical = json.dumps(clone, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()[:16]


def test_machine_evidence_manifest_exposes_current_offline_proof_state():
    data = load(EVIDENCE_MANIFEST)
    assert data["schema"] == "trinity-accord.evidence-manifest.v1"
    assert data["non_amending_boundary"] is True
    assert data["canonical_authority"] == "Bitcoin Originals only"
    assert data["source_digest_algorithm"] == "sha256(canonical_json_without_source_digest)"
    assert data["source_digest"] == source_digest(data)

    legacy = data["github_archive_mirror"]
    assert legacy["stats"]["eth_attestations_verified"] == 8
    assert legacy["stats_scope"] == "legacy_archive_snapshot_not_current_cryptographic_proof_inventory"
    assert "current_cryptographic_proof_state" in data["warning"]

    current = data["current_cryptographic_proof_state"]
    assert current["status"] == "offline_verifiable"

    eth = current["ethereum_non_nft"]
    assert eth["anchor_count"] == 10
    assert eth["l1_byte_integrity"] == "PASS"
    assert eth["l2_execution_inclusion"] == "PASS"
    assert eth["l3_checkpoint_relative_finality"] == "PASS"
    assert "weak-subjectivity" in eth["trust_boundary"]
    assert ROOT.joinpath(eth["manifest"]).is_file()
    assert ROOT.joinpath(eth["offline_report"]).is_file()
    assert ROOT.joinpath(eth["verifier"]).is_file()

    nft = current["chronicle_nft"]
    assert nft["asset_count"] == 175
    assert nft["collection_merkle_root_sha256"] == NFT_ROOT
    assert nft["l1_collection_commitment"] == "PASS"
    assert nft["l2_execution_inclusion"] == "PASS"
    assert nft["l3_checkpoint_relative_finality"] == "PASS"
    assert "lookup coordinate" in nft["global_log_index_boundary"]
    assert ROOT.joinpath(nft["commitment"]).is_file()
    assert ROOT.joinpath(nft["capture_summary"]).is_file()
    assert ROOT.joinpath(nft["offline_report"]).is_file()
    assert ROOT.joinpath(nft["verifier"]).is_file()
    assert ROOT.joinpath(nft["frozen_primitives_manifest"]).is_file()

    preservation = current["repository_preservation"]
    assert preservation["concept_doi"] == CONCEPT_DOI
    assert preservation["latest_published_version_doi"] == LATEST_REPOSITORY_DOI
    assert preservation["status"] == "published_and_publicly_restored"
    assert preservation["cold_restore"] == "PASS"
    assert ROOT.joinpath(preservation["state"]).is_file()
    assert ROOT.joinpath(preservation["latest_observation"]).is_file()


def test_machine_summary_matches_checked_in_offline_reports():
    manifest = load(EVIDENCE_MANIFEST)["current_cryptographic_proof_state"]
    eth_report = load(ETH_REPORT)
    nft_report = load(NFT_REPORT)

    assert eth_report["result"] == "PASS"
    assert eth_report["anchors"] == manifest["ethereum_non_nft"]["anchor_count"]
    assert eth_report["L1_BYTE_INTEGRITY"] == manifest["ethereum_non_nft"]["l1_byte_integrity"]
    assert eth_report["L2_EXECUTION_INCLUSION"] == manifest["ethereum_non_nft"]["l2_execution_inclusion"]
    assert eth_report["L3_CONSENSUS_FINALITY"] == manifest["ethereum_non_nft"]["l3_checkpoint_relative_finality"]

    assert nft_report["result"] == "PASS"
    assert nft_report["L1_COLLECTION_COMMITMENT"]["status"] == manifest["chronicle_nft"]["l1_collection_commitment"]
    assert nft_report["L2_EXECUTION_INCLUSION"]["status"] == manifest["chronicle_nft"]["l2_execution_inclusion"]
    assert nft_report["L3_CONSENSUS_FINALITY"]["status"] == manifest["chronicle_nft"]["l3_checkpoint_relative_finality"]
    assert nft_report["L1_COLLECTION_COMMITMENT"]["asset_count"] == manifest["chronicle_nft"]["asset_count"]
    assert nft_report["L1_COLLECTION_COMMITMENT"]["root_sha256"] == manifest["chronicle_nft"]["collection_merkle_root_sha256"]


def test_external_annex_state_disambiguates_historical_core_version_from_current_concept():
    data = load(EXTERNAL_ANNEX_STATE)
    assert data["publication_status"] == "published_and_publicly_restored"
    assert data["core_repository_preservation_doi"] == HISTORICAL_CORE_VERSION_DOI
    assert data["core_repository_preservation_doi_role"] == "historical_version_reference"
    assert data["current_core_repository_concept_doi"] == CONCEPT_DOI
    assert data["current_core_repository_latest_version_doi"] == LATEST_REPOSITORY_DOI
    assert "not the current Concept DOI" in data["core_repository_reference_note"]

    assert data["annexes"]["evidence"]["public_cold_restore"] == "passed"
    assert data["annexes"]["nft"]["public_cold_restore"] == "passed"
    assert data["external_binary_payload_recovery_requires_github"] is False
