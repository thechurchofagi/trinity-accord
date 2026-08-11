from __future__ import annotations

import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def release_entry(registry: dict, tag: str) -> dict:
    return next(item for item in registry["release_registry"] if item["tag"] == tag)


def workflow_inputs(path: str) -> dict:
    parsed = yaml.load(read(path), Loader=yaml.BaseLoader)
    return parsed["on"]["workflow_dispatch"]["inputs"]


def test_public_status_matches_checked_in_offline_proof_reports():
    status = load_json("api/status.json")["current_evidence_checkpoint"]
    bitcoin = load_json(
        "evidence/bitcoin-inscription-proof-annex-v1/reports/OFFLINE-VERIFICATION.json"
    )
    ethereum = load_json(
        "evidence/ethereum-evidence-annex-v1/reports/OFFLINE-VERIFICATION.json"
    )
    nft = load_json("evidence/nft-proof-annex-v1/reports/OFFLINE-VERIFICATION.json")

    assert status["status"] == "PASS"
    assert status["ordinary_verification_network_required"] is False

    bitcoin_status = status["proof_sets"]["bitcoin_inscriptions"]
    assert bitcoin["result"] == "PASS"
    assert bitcoin_status["count"] == bitcoin[
        "L1_INSCRIPTION_CONTENT_AND_TAPROOT_BINDING"
    ]["inscriptions"] == 8
    assert bitcoin_status["canonical_originals"] == 3
    assert bitcoin_status["non_amending_ancillary"] == 5

    ethereum_status = status["proof_sets"]["ethereum_non_nft_anchors"]
    assert ethereum["result"] == "PASS"
    assert ethereum["L1_BYTE_INTEGRITY"] == "PASS"
    assert ethereum["L2_EXECUTION_INCLUSION"] == "PASS"
    assert ethereum["L3_CONSENSUS_FINALITY"] == "PASS"
    assert ethereum_status["count"] == ethereum["anchors"] == 12

    nft_status = status["proof_sets"]["chronicle_nfts"]
    assert nft["result"] == "PASS"
    assert nft_status["count"] == nft["L1_COLLECTION_COMMITMENT"]["asset_count"] == 175
    assert nft["L2_EXECUTION_INCLUSION"]["mint_transactions"] == 175
    assert nft["L3_CONSENSUS_FINALITY"]["unique_execution_blocks"] == 175


def test_status_checkpoint_identity_matches_published_recovery_state():
    status = load_json("api/status.json")["current_evidence_checkpoint"]
    inventory = load_json("api/final-evidence-inventory.v1.json")["current_checkpoint"]
    catalog = load_json("preservation/recovery-catalog.json")["core_repository"][
        "current_evidence_checkpoint"
    ]

    assert inventory["status"] == "consumed"
    assert status["published_version_doi"] == inventory["published_doi"]
    assert status["published_version_doi"] == catalog["version_doi"]
    assert status["published_source_baseline_commit_sha"] == inventory[
        "published_source_baseline_commit_sha"
    ]
    assert status["published_source_baseline_commit_sha"] == catalog[
        "source_baseline_commit_sha"
    ]


def test_empty_historical_release_is_not_exposed_as_current_byte_evidence():
    registry = load_json("GUARDIANSHIP-SYSTEM-REGISTRY.json")
    historical = release_entry(registry, "nft-arweave-mirror-175-v1")

    assert historical["status"] == "historical_release_empty"
    assert historical["observed_custom_asset_count"] == 0
    assert historical["historical_release_text_is_byte_evidence"] is False
    assert historical["content_recovery_source_tag"] == "nft-backup-v1"

    status = load_json("api/status.json")["nft_media_availability"]
    observed = status["historical_individual_archive_release"]
    assert observed["observed_custom_asset_count"] == 0
    assert observed["usable_as_current_recovery_source"] is False

    for path in [
        "status.md",
        "guardianship-system-overview.md",
        "evidence-backup-coverage.md",
        "preservation/EXTERNAL-BINARY-ANNEX.md",
        "nft-text-descriptions/README.md",
    ]:
        text = read(path)
        assert "nft-arweave-mirror-175-v1" in text
        assert "zero custom assets" in text or "0 custom assets" in text or "0 个自定义资产" in text


def test_content_complete_nft_recovery_path_is_consistent():
    registry = load_json("GUARDIANSHIP-SYSTEM-REGISTRY.json")
    backup = release_entry(registry, "nft-backup-v1")
    status = load_json("api/status.json")["nft_media_availability"][
        "current_content_recovery"
    ]
    annex = load_json("preservation/external-binary-annex-state.json")["annexes"]["nft"]

    assert backup["status"] == "PASS"
    assert backup["custom_assets"] == "10/10"
    assert backup["logical_coverage"] == {
        "nfts": 175,
        "arweave_transactions_and_files": 434,
        "successful_downloads": 434,
        "failed_downloads": 0,
    }
    assert status["custom_asset_count"] == annex["asset_count"] == 10
    assert status["logical_nft_coverage"] == 175
    assert status["logical_car_file_coverage"] == 434
    assert status["zenodo_annex_doi"] == annex["doi"] == "10.5281/zenodo.21754229"
    assert annex["public_cold_restore"] == "passed"


def test_legacy_175_tar_workflows_require_an_explicit_compatible_release():
    workflow_paths = [
        ".github/workflows/verify-full-evidence-chain.yml",
        ".github/workflows/verify-dag-digest.yml",
        ".github/workflows/verify-dag-and-signed-cids.yml",
        ".github/workflows/verify-release-assets.yml",
    ]
    for path in workflow_paths:
        release_input = workflow_inputs(path)["release_tag"]
        assert release_input["required"] == "true"
        assert release_input.get("default") != "nft-arweave-mirror-175-v1"
        assert "historical" in release_input["description"].lower()

    scripts = [
        "scripts/verify-full-evidence-chain.mjs",
        "scripts/verify-dag-digest.mjs",
        "scripts/verify-dag-and-signed-cids.mjs",
        "scripts/verify-release-assets.mjs",
        "scripts/probe-blake2b-variants.mjs",
    ]
    for path in scripts:
        text = read(path)
        assert "--release-tag is required" in text
        assert "getArg('--release-tag', 'nft-arweave-mirror-175-v1')" not in text


def test_onchain_audit_defaults_to_checked_in_token_index():
    inputs = workflow_inputs(".github/workflows/verify-onchain-tokenuri.yml")
    assert inputs["source"]["default"] == "token_index"
    assert inputs["release_tag"]["default"] == ""

    script = read("scripts/verify-onchain-tokenuri.mjs")
    assert ": 'token_index';" in script
    assert "--release-tag is required when --source manifest" in script
    assert "Authorization: `Bearer ${GITHUB_TOKEN}`" in script
    assert "...(GITHUB_TOKEN ?" in script


def test_text_description_workflow_validates_without_using_the_empty_release():
    path = ".github/workflows/extract-nft-metadata.yml"
    parsed = yaml.load(read(path), Loader=yaml.BaseLoader)
    workflow = read(path)

    assert parsed["name"] == "Validate NFT Text Descriptions"
    assert parsed["permissions"]["contents"] == "read"
    assert "scripts/test_nft_text_description_mirror_integrity.py" in workflow
    assert "git push" not in workflow
    assert "releases/tags/" not in workflow
    assert "nft-backup-v1" in workflow
    assert "10.5281/zenodo.21754229" in workflow


def test_generated_reports_link_status_and_corrections_separately():
    for path in [
        "scripts/verify-full-evidence-chain.mjs",
        "scripts/verify-release-assets.mjs",
    ]:
        text = read(path)
        assert "current_status_url: 'https://www.trinityaccord.org/api/status.json'" in text
        assert "corrections_index_url: 'https://www.trinityaccord.org/api/corrections-index.json'" in text
