from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
AUTH = ROOT / "preservation/current-baseline-publication-authorization-v3.json"
STATE_MACHINE = ROOT / "scripts/current_baseline_publication_v3.py"
RUNNER = ROOT / "scripts/run_current_baseline_publication_v3_ci.sh"
DISPATCHER = ROOT / "scripts/run_repository_preservation_refresh_ci.sh"
INVENTORY = ROOT / "api/final-evidence-inventory.v1.json"
RECOVERY = ROOT / "api/recovery-index.json"
RELATIONSHIPS = ROOT / "api/evidence-relationship-map.v1.json"


def load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_digest(value: dict) -> str:
    material = dict(value)
    material.pop("source_digest", None)
    raw = json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def test_sequence3_authorization_is_exact_and_state_is_valid():
    auth = load(AUTH)
    assert auth["schema"] == "trinityaccord.current-baseline-publication-authorization.v3"
    assert auth["sequence"] == 3
    assert auth["status"] in {"pending", "prepared", "consumed"}
    assert auth["core_concept_doi"] == "10.5281/zenodo.21739343"
    assert auth["previous_core_version_doi"] == "10.5281/zenodo.21846249"
    assert auth["required_evidence_freeze_commit_sha"] == "5fdc53605d1a3e3782a9257b12cf2fc9b5fa2162"
    assert auth["publication_confirmation"] == "PUBLISH_TRINITY_FINAL_EVIDENCE_BASELINE_V3"
    assert auth["zenodo_rights_acknowledgement"] == "TRINITY_PRESERVATION_CAPSULE_RIGHTS_V1_APPROVED"
    assert auth["include_full_repository_doi"] is True
    assert auth["include_homepage_arweave_snapshot"] is False
    assert auth["intended_as_final_evidence_freeze"] is True
    assert auth["non_amending_boundary"] is True
    assert auth["live_main_equivalence_claimed"] is False
    assert auth["frozen_evidence_scope"] == {
        "bitcoin_inscriptions": 8,
        "bitcoin_canonical_originals": 3,
        "bitcoin_non_amending_ancillary": 5,
        "ethereum_non_nft_anchors": 10,
        "ethereum_chronicle_nfts": 175,
        "nft_contracts": 4,
        "proof_status_required": "PASS",
        "ordinary_verification_network_required": False,
    }
    subprocess.run([sys.executable, str(STATE_MACHINE), "validate"], cwd=ROOT, check=True)


def test_final_inventory_is_derived_and_complete():
    subprocess.run(
        [sys.executable, "scripts/build_final_evidence_inventory.py", "--check"],
        cwd=ROOT,
        check=True,
    )
    inventory = load(INVENTORY)
    assert inventory["source_digest"] == canonical_digest(inventory)
    assert inventory["authority_boundary"]["canonical_count"] == 3
    assert inventory["evidence_sets"]["bitcoin_inscriptions"]["count"] == 12
    assert inventory["evidence_sets"]["bitcoin_inscriptions"]["network_required_for_verification"] is False
    # The compatibility inventory path now exposes the current v4 checkpoint;
    # the immutable v3 10-anchor scope remains under final_freeze history.
    assert inventory["evidence_sets"]["ethereum_non_nft"]["count"] == 12
    assert inventory["final_freeze"]["published_doi"] == "10.5281/zenodo.21855814"
    assert inventory["current_checkpoint"]["sequence"] == 4
    assert inventory["evidence_sets"]["ethereum_non_nft"]["network_required_for_existing_proof_verification"] is False
    assert inventory["evidence_sets"]["ethereum_chronicle_nft"]["asset_count"] == 175
    assert inventory["evidence_sets"]["ethereum_chronicle_nft"]["network_required_for_existing_proof_verification"] is False
    assert inventory["storage_and_preservation"]["zenodo"]["core_repository_series"]["concept_doi"] == "10.5281/zenodo.21739343"
    assert inventory["storage_and_preservation"]["zenodo"]["external_evidence_annex"]["doi"] == "10.5281/zenodo.21753937"
    assert inventory["storage_and_preservation"]["zenodo"]["chronicle_nft_media_annex"]["doi"] == "10.5281/zenodo.21754229"


def test_recovery_and_relationship_topology_cover_all_layers():
    recovery = load(RECOVERY)
    assert recovery["source_digest"] == canonical_digest(recovery)
    required_steps = set(recovery["mandatory_recovery_steps"])
    assert {
        "verify_final_evidence_inventory_and_relationship_topology",
        "verify_bitcoin_inscription_proof_annex_offline",
        "verify_ethereum_non_nft_proof_annex_offline",
        "verify_175_item_nft_commitment_and_proof_annex_offline",
        "verify_opentimestamps_proof_and_preserved_fullnode_observation",
        "restore_and_verify_core_repository_version_doi",
        "restore_and_verify_external_evidence_annex_doi",
        "restore_and_verify_chronicle_nft_media_annex_doi",
    } <= required_steps
    graph = load(RELATIONSHIPS)
    node_ids = {item["id"] for item in graph["nodes"]}
    assert {
        "final_evidence_inventory",
        "current_live_evidence_state",
        "ethereum_address_scope_audit",
        "bitcoin_inscription_proof_annex",
        "ethereum_non_nft_proof_annex",
        "chronicle_nft_proof_annex",
        "github_repository_and_pages",
        "arweave_mirrors",
        "core_repository_zenodo_series",
        "external_evidence_zenodo_annex",
        "nft_media_zenodo_annex",
    } <= node_ids


def test_final_runner_is_zenodo_only_retry_safe_and_dispatcher_priority_is_correct():
    subprocess.run(["bash", "-n", str(RUNNER)], cwd=ROOT, check=True)
    runner = RUNNER.read_text(encoding="utf-8")
    assert "publish_preservation_capsule_to_zenodo_v3.py" in runner
    assert "restore-trinity-accord.py" in runner
    assert "repository_preservation_refresh.py verify-public" in runner
    assert "required_evidence_freeze_commit_sha" in runner
    assert "git diff --quiet" in runner
    assert "matching_published" in runner and "matching_drafts" in runner
    assert "ARKEY" not in runner
    assert "arweave_upload_homepage_snapshot" not in runner
    dispatcher = DISPATCHER.read_text(encoding="utf-8")
    assert dispatcher.index("current-baseline-publication-authorization-v4.json") < dispatcher.index(
        "current-baseline-publication-authorization-v3.json"
    ) < dispatcher.index("current-baseline-publication-authorization-v2.json")
    assert "run_current_baseline_publication_v4_ci.sh" in dispatcher
    assert "run_current_baseline_publication_v3_ci.sh" in dispatcher
