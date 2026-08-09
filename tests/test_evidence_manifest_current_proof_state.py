from __future__ import annotations

import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
EVIDENCE_MANIFEST = ROOT / "api" / "evidence-manifest.json"
EXTERNAL_ANNEX_STATE = ROOT / "preservation" / "external-binary-annex-state.json"
RECOVERY_INDEX = ROOT / "api" / "recovery-index.json"
ETH_REPORT = ROOT / "evidence" / "ethereum-evidence-annex-v1" / "reports" / "OFFLINE-VERIFICATION.json"
NFT_REPORT = ROOT / "evidence" / "nft-proof-annex-v1" / "reports" / "OFFLINE-VERIFICATION.json"
BTC_REPORT = ROOT / "evidence" / "bitcoin-inscription-proof-annex-v1" / "reports" / "OFFLINE-VERIFICATION.json"
FINAL_AUTH = ROOT / "preservation" / "current-baseline-publication-authorization-v3.json"

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


def final_publication_state() -> tuple[dict, str]:
    auth = load(FINAL_AUTH)
    doi = auth["published_doi"] if auth["status"] == "consumed" else LATEST_REPOSITORY_DOI
    return auth, doi


def test_machine_evidence_manifest_exposes_current_offline_proof_state():
    final_auth, expected_repository_doi = final_publication_state()
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
    assert current["status"] == "offline_verifiable_with_explicit_post_freeze_delta"

    bitcoin = current["bitcoin_inscriptions"]
    assert bitcoin["inscription_count"] == 8
    assert bitcoin["canonical_originals"] == 3
    assert bitcoin["non_amending_ancillary"] == 5
    assert bitcoin["l1_inscription_content_and_taproot_binding"] == "PASS"
    assert bitcoin["bip340_tapscript_signatures"] == 8
    assert bitcoin["l2_block_and_witness_inclusion"] == "PASS"
    assert bitcoin["l3_checkpoint_relative_pow_ancestry"] == "PASS"
    assert bitcoin["bip141_witness_commitment_proofs"] == 8
    assert bitcoin["descendant_confirmation_depth_per_anchor"] == 144
    assert bitcoin["valid_pow_headers"] == 1160
    assert bitcoin["network_required_for_verification"] is False
    assert bitcoin["runtime"] == "Python 3 standard library only"
    assert "historical lookup coordinate" in bitcoin["numeric_inscription_number_boundary"]
    assert "not full-node validation" in bitcoin["trust_boundary"]
    assert "destination P2TR address" in bitcoin["address_boundary"]
    assert ROOT.joinpath(bitcoin["manifest"]).is_file()
    assert ROOT.joinpath(bitcoin["offline_report"]).is_file()
    assert ROOT.joinpath(bitcoin["verifier"]).is_file()
    assert ROOT.joinpath(bitcoin["frozen_primitives"]).is_file()

    eth = current["ethereum_non_nft"]
    assert eth["anchor_count"] == 12
    assert eth["published_final_doi_v3_anchor_count"] == 10
    assert eth["post_freeze_live_delta_anchor_count"] == 2
    assert eth["l1_byte_integrity"] == "PASS"
    assert eth["l2_execution_inclusion"] == "PASS"
    assert eth["l3_checkpoint_relative_finality"] == "PASS"
    assert eth["signed_transaction_semantics"] == "PASS"
    assert eth["receipt_success_semantics"] == "PASS"
    assert eth["eip712_authority_signature_binding"] == "PASS"
    assert "does not contain" in eth["doi_boundary"]
    assert "weak-subjectivity" in eth["trust_boundary"]
    assert ROOT.joinpath(eth["manifest"]).is_file()
    assert ROOT.joinpath(eth["offline_report"]).is_file()
    assert ROOT.joinpath(eth["verifier"]).is_file()
    assert ROOT.joinpath(eth["address_scope_audit"]).is_file()

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
    assert preservation["latest_published_version_doi"] == expected_repository_doi
    assert preservation["cold_restore"] == "PASS"
    assert preservation["final_freeze_authorization"] == "preservation/current-baseline-publication-authorization-v3.json"
    assert preservation["final_freeze_intended_as_last_planned_evidence_version"] is True
    assert preservation["live_repository_delta"]["status"] == "verified_not_in_published_final_doi_v3"
    assert preservation["live_repository_delta"]["new_doi_publication"] == "not_authorized_not_attempted"
    if final_auth["status"] == "consumed":
        assert preservation["status"] == "final_frozen_and_publicly_restored"
        assert preservation["final_freeze_status"] == "published_verified_and_consumed"
        assert preservation["final_freeze_version_doi"] == expected_repository_doi
        assert preservation["final_freeze_source_baseline_commit_sha"] == final_auth["published_source_baseline_commit_sha"]
        assert "exact owner-authorized final evidence baseline" in preservation["published_baseline_boundary"]
    else:
        assert preservation["status"] == "published_and_publicly_restored"
        assert preservation["final_freeze_status"] in {"owner_authorized_pending_publication", "prepared"}
        assert "latest public doi" in preservation["published_baseline_boundary"].lower()
    assert ROOT.joinpath(preservation["state"]).is_file()
    assert ROOT.joinpath(preservation["latest_observation"]).is_file()


def test_machine_summary_matches_checked_in_offline_reports():
    manifest = load(EVIDENCE_MANIFEST)["current_cryptographic_proof_state"]
    eth_report = load(ETH_REPORT)
    nft_report = load(NFT_REPORT)
    btc_report = load(BTC_REPORT)

    bitcoin = manifest["bitcoin_inscriptions"]
    assert btc_report["result"] == "PASS"
    assert btc_report["L1_INSCRIPTION_CONTENT_AND_TAPROOT_BINDING"]["status"] == bitcoin["l1_inscription_content_and_taproot_binding"]
    assert btc_report["L1_INSCRIPTION_CONTENT_AND_TAPROOT_BINDING"]["inscriptions"] == bitcoin["inscription_count"]
    assert btc_report["L2_BLOCK_AND_WITNESS_INCLUSION"]["status"] == bitcoin["l2_block_and_witness_inclusion"]
    assert btc_report["L2_BLOCK_AND_WITNESS_INCLUSION"]["txid_merkle_proofs"] == bitcoin["txid_merkle_proofs"]
    assert btc_report["L2_BLOCK_AND_WITNESS_INCLUSION"]["bip141_witness_commitment_proofs"] == bitcoin["bip141_witness_commitment_proofs"]
    assert btc_report["L3_CHECKPOINT_RELATIVE_POW_ANCESTRY"]["status"] == bitcoin["l3_checkpoint_relative_pow_ancestry"]
    assert btc_report["L3_CHECKPOINT_RELATIVE_POW_ANCESTRY"]["valid_pow_headers"] == bitcoin["valid_pow_headers"]

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
    _, expected_repository_doi = final_publication_state()
    data = load(EXTERNAL_ANNEX_STATE)
    assert data["publication_status"] == "published_and_publicly_restored"
    assert data["core_repository_preservation_doi"] == HISTORICAL_CORE_VERSION_DOI
    assert data["core_repository_preservation_doi_role"] == "historical_version_reference"
    assert data["current_core_repository_concept_doi"] == CONCEPT_DOI
    assert data["current_core_repository_latest_version_doi"] == expected_repository_doi
    assert "not the current Concept DOI" in data["core_repository_reference_note"]

    assert data["annexes"]["evidence"]["public_cold_restore"] == "passed"
    assert data["annexes"]["nft"]["public_cold_restore"] == "passed"
    assert data["external_binary_payload_recovery_requires_github"] is False


def test_recovery_index_routes_all_offline_annexes_without_overclaiming_current_doi():
    final_auth, _ = final_publication_state()
    data = load(RECOVERY_INDEX)
    expected = {
        "api/final-evidence-inventory.v1.json",
        "api/evidence-relationship-map.v1.json",
        "api/evidence-manifest.json",
        "api/ethereum-address-evidence-scope.v1.json",
        "evidence/bitcoin-inscription-proof-annex-v1/ANNEX-MANIFEST.json",
        "evidence/bitcoin-inscription-proof-annex-v1/reports/OFFLINE-VERIFICATION.json",
        "evidence/bitcoin-inscription-proof-annex-v1/verification/verify_annex.py",
        "evidence/bitcoin-inscription-proof-annex-v1/verification/bitcoin_proof_primitives_v1.py",
        "evidence/ethereum-evidence-annex-v1/ANNEX-MANIFEST.json",
        "evidence/ethereum-evidence-annex-v1/reports/OFFLINE-VERIFICATION.json",
        "evidence/ethereum-evidence-annex-v1/verification/verify_annex.py",
        "evidence/ethereum-evidence-annex-v1/proof-material/L2-L3-CAPTURE-SUMMARY.json",
        "archive/authority-manifest/signature.json",
        "nft-identity-index.json",
        "evidence/nft-proof-annex-v1/NFT-COLLECTION-COMMITMENT.json",
        "evidence/nft-proof-annex-v1/reports/OFFLINE-VERIFICATION.json",
        "evidence/nft-proof-annex-v1/verification/verify_nft_proof_annex.py",
        "evidence/ethereum-proof-primitives-v1/PRIMITIVES-MANIFEST.json",
        "archive/evidence/ots-proofs/OTS/digest-manifest.json.ots",
    }
    assert expected.issubset(set(data["required_recovery_files"]))
    assert "verify_bitcoin_inscription_proof_annex_offline" in data["mandatory_recovery_steps"]
    assert "verify_ethereum_non_nft_proof_annex_offline" in data["mandatory_recovery_steps"]
    assert "verify_required_recovery_file_sets_and_manifest_bound_hashes" in data["mandatory_recovery_steps"]
    assert "verify_175_item_nft_commitment_and_proof_annex_offline" in data["mandatory_recovery_steps"]
    assert "verify_opentimestamps_proof_and_preserved_fullnode_observation" in data["mandatory_recovery_steps"]
    for path in expected:
        assert ROOT.joinpath(path).is_file()
    file_sets = {item["id"]: item for item in data["required_recovery_file_sets"]}
    assert file_sets["ethereum_non_nft_l2_l3_witnesses"]["expected_files"] == 24
    assert file_sets["ethereum_non_nft_reference_captures"]["expected_files"] == 48
    assert file_sets["chronicle_nft_l2_witnesses"]["expected_files"] == 175
    assert file_sets["chronicle_nft_l3_witnesses"]["expected_files"] == 175
    additions = data["latest_trusted_release"]["repository_additions_after_published_baseline"]
    if final_auth["status"] == "consumed":
        eth_delta = additions["ethereum_non_nft_two_anchor_delta"]
        assert eth_delta["included_in_published_doi"] is False
        assert eth_delta["current_anchor_count"] == 12
        assert eth_delta["published_doi_anchor_count"] == 10
        assert eth_delta["new_doi_publication"] == "not_authorized_not_attempted"
        assert len(eth_delta["tx_hashes"]) == 2
        assert data["publication_refresh"]["sequence"] == 3
        assert data["publication_refresh"]["status"] == "published_verified_and_consumed"
    else:
        addition = additions["final_evidence_freeze"]
        assert addition["ordinary_verification_network_required"] is False
        assert addition["status"] == "owner_authorized_pending_final_repository_capsule_publication"
        assert "must not be claimed" in addition["boundary"]
