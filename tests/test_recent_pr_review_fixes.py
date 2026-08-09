from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[1]
BITCOIN_ANNEX = ROOT / "evidence/bitcoin-inscription-proof-annex-v1"
BITCOIN_VERIFIER = BITCOIN_ANNEX / "verification/verify_annex.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module


def bitcoin_case():
    module = load_module("bitcoin_review_fix_verifier", BITCOIN_VERIFIER)
    manifest = json.loads((BITCOIN_ANNEX / "ANNEX-MANIFEST.json").read_text(encoding="utf-8"))
    anchor = copy.deepcopy(manifest["anchors"][0])
    proof = json.loads((ROOT / anchor["proof_material"]["path"]).read_text(encoding="utf-8"))
    return module, anchor, proof


def canonical_digest(value: dict) -> str:
    material = dict(value)
    material.pop("source_digest", None)
    raw = json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def test_bitcoin_declared_timestamps_are_bound_to_header():
    module, anchor, proof = bitcoin_case()
    l1 = module.verify_l1(anchor, proof)
    mutated_anchor = copy.deepcopy(anchor)
    mutated_proof = copy.deepcopy(proof)
    wrong = int(anchor["block_reference"]["timestamp"]) + 1
    mutated_anchor["block_reference"]["timestamp"] = wrong
    mutated_proof["block_inclusion"]["timestamp"] = wrong
    with pytest.raises(ValueError, match="manifest block timestamp"):
        module.verify_l2(mutated_anchor, mutated_proof, l1)


def test_bitcoin_checkpoint_votes_require_distinct_matching_providers():
    module, anchor, proof = bitcoin_case()
    l1 = module.verify_l1(anchor, proof)
    l2 = module.verify_l2(anchor, proof, l1)
    mutated = copy.deepcopy(proof)
    observations = mutated["pow_ancestry"]["checkpoint_observations"]
    assert len(observations) >= 2
    nonmatching = copy.deepcopy(observations[1])
    nonmatching["checkpoint_hash"] = "00" * 32
    mutated["pow_ancestry"]["checkpoint_observations"] = [
        copy.deepcopy(observations[0]),
        copy.deepcopy(observations[0]),
        nonmatching,
    ]
    mutated["pow_ancestry"]["matching_provider_votes"] = 2
    with pytest.raises(ValueError, match="observations do not match"):
        module.verify_l3(anchor, mutated, l2)


@pytest.mark.parametrize(
    ("module_name", "path", "message"),
    (
        (
            "ethereum_review_fix_verifier",
            ROOT / "evidence/ethereum-evidence-annex-v1/verification/verify_annex.py",
            "provenance quorum mismatch",
        ),
        (
            "nft_review_fix_verifier",
            ROOT / "evidence/nft-proof-annex-v1/verification/verify_nft_proof_annex.py",
            "provenance quorum mismatch",
        ),
    ),
)
def test_ethereum_checkpoint_votes_require_distinct_matching_providers(
    module_name, path, message
):
    module = load_module(module_name, path)
    checkpoint = {
        "root": "0x" + "12" * 32,
        "slot": 123,
        "matching_provider_votes": 2,
        "finalized_provider_votes": 1,
    }
    observation = {
        "provider": "https://provider.example",
        "root": checkpoint["root"],
        "observed_slot": checkpoint["slot"],
        "canonical": True,
        "finalized": True,
        "execution_optimistic": False,
    }
    with pytest.raises(ValueError, match=message):
        module.verify_checkpoint_provider_quorum(
            checkpoint, [copy.deepcopy(observation), copy.deepcopy(observation)]
        )


def test_recovery_index_lists_every_bitcoin_annex_runtime_dependency():
    manifest = json.loads((BITCOIN_ANNEX / "ANNEX-MANIFEST.json").read_text(encoding="utf-8"))
    recovery = json.loads((ROOT / "api/recovery-index.json").read_text(encoding="utf-8"))
    required = set(recovery["required_recovery_files"])
    assert recovery["source_digest"] == canonical_digest(recovery)
    for anchor in manifest["anchors"]:
        assert anchor["proof_material"]["path"] in required
        assert anchor["content"]["mirror_path"] in required


def test_scoped_legacy_verifier_ignores_unselected_annex_failure(monkeypatch):
    module = load_module(
        "bitcoin_scoped_mirror_review_fix",
        ROOT / "scripts/verify_bitcoin_inscription_mirrors.py",
    )
    records = module.load_mirror_records()
    selected = records[0]["inscription"]["inscription_id"]
    unselected = records[1]["inscription"]["inscription_id"]
    selected_body = (ROOT / records[0]["content"]["raw_text_path"]).read_text(encoding="utf-8")
    fake_report = {
        "result": "FAIL",
        "failures": [f"{unselected}: unrelated proof failure"],
        "l1_checks": [
            {
                "inscription_number": selected,
                "status": "PASS",
                "body_sha256": module.sha256_text(selected_body),
            }
        ],
    }
    monkeypatch.setattr(
        module.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=1,
            stdout=json.dumps(fake_report),
            stderr="",
        ),
    )
    args = SimpleNamespace(inscription_id=selected, layer=None, all=False)
    checked, errors = module.verify_offline(records, args)
    assert checked == 1
    assert errors == []


def test_node_adapter_reports_malformed_inputs_and_manifest_totals():
    node = os.environ.get("NODE", "node")
    program = r"""
      const { adaptBitcoinInscriptionOfflineReport } = await import(
        './scripts/bitcoin-inscription-offline-adapter.mjs'
      );
      const manifest = {
        anchors: [
          { txid: 'a', classification: 'canonical_original', title: 'a', wtxid: 'a', block_reference: {height: 1, hash: 'a', timestamp: 1} },
          { txid: 'b', classification: 'canonical_original', title: 'b', wtxid: 'b', block_reference: {height: 2, hash: 'b', timestamp: 2} },
          { txid: 'c', classification: 'non_amending_ancillary', title: 'c', wtxid: 'c', block_reference: {height: 3, hash: 'c', timestamp: 3} },
        ],
        verification_implementation: {frozen_primitives: 'frozen.py'},
      };
      const report = {
        result: 'FAIL', failures: ['b: failed'],
        l1_checks: [{txid: 'a', status: 'PASS', tapscript_signature_status: 'PASS'}],
        l2_checks: [{txid: 'a', status: 'PASS'}],
        l3_checks: [{txid: 'a', status: 'PASS', descendant_confirmation_depth: 144}],
        L2_BLOCK_AND_WITNESS_INCLUSION: {txid_merkle_proofs: 1, bip141_witness_commitment_proofs: 1},
        L3_CHECKPOINT_RELATIVE_POW_ANCESTRY: {valid_pow_headers: 145, descendant_confirmation_depth_per_anchor: 144},
        claim_boundary: 'test',
      };
      const partial = adaptBitcoinInscriptionOfflineReport(report, manifest);
      const failedLayerReport = structuredClone(report);
      failedLayerReport.result = 'PASS';
      failedLayerReport.l1_checks[0].status = 'FAIL';
      const failedLayer = adaptBitcoinInscriptionOfflineReport(failedLayerReport, manifest);
      const malformed = adaptBitcoinInscriptionOfflineReport(report, {});
      process.stdout.write(JSON.stringify({partial, failedLayer, malformed}));
    """
    completed = subprocess.run(
        [node, "--input-type=module", "--eval", program],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout)
    assert result["partial"]["originals_total"] == 2
    assert result["partial"]["ancillary_total"] == 1
    assert result["partial"]["bitcoin_anchors_total"] == 3
    assert result["failedLayer"]["bitcoin_tx_anchor_pass"] is False
    assert result["failedLayer"]["bitcoin_anchors_pass"] == 0
    assert result["malformed"]["bitcoin_tx_anchor_pass"] is False
    assert any("manifest" in item for item in result["malformed"]["critical_errors"])


def test_zenodo_concept_lineage_helper_fails_closed():
    module = load_module(
        "zenodo_concept_review_fix",
        ROOT / "scripts/publish_preservation_capsule_to_zenodo.py",
    )
    expected_doi = "10.5281/zenodo.21739343"
    expected_id = 21739343
    module.require_concept_series(
        {"conceptdoi": expected_doi, "conceptrecid": expected_id},
        expected_doi,
        expected_id,
    )
    with pytest.raises(SystemExit, match="different Concept DOI"):
        module.require_concept_series(
            {"conceptdoi": "10.5281/zenodo.999", "conceptrecid": expected_id},
            expected_doi,
            expected_id,
        )
    with pytest.raises(SystemExit, match="lacks a fail-closed"):
        module.require_concept_series({}, expected_doi, expected_id)


def test_zenodo_state_builder_preserves_rich_historical_version_metadata():
    module = load_module(
        "zenodo_history_review_fix",
        ROOT / "scripts/publish_preservation_capsule_to_zenodo.py",
    )
    historical = {
        "capsule_id": "capsule-old",
        "deposition_id": 1,
        "record_id": 101,
        "doi": "10.5281/zenodo.101",
        "git_commit_sha": "a" * 40,
        "git_tree_oid": "b" * 40,
        "package_identity_sha256": "c" * 64,
        "files": [{"path": "README.md", "sha256": "d" * 64}],
    }
    old_record = {
        "id": 1,
        "record_id": 101,
        "submitted": True,
        "doi": historical["doi"],
        "metadata": {"title": module.PACKAGE_TITLE, "version": "capsule-old"},
    }
    current_record = {
        "id": 2,
        "record_id": 102,
        "submitted": True,
        "doi": "10.5281/zenodo.102",
        "conceptdoi": "10.5281/zenodo.100",
        "metadata": {"title": module.PACKAGE_TITLE, "version": "capsule-new"},
    }
    package = {
        "capsule_id": "capsule-new",
        "git_commit_sha": "e" * 40,
        "git_tree_oid": "f" * 40,
        "package_identity_sha256": "1" * 64,
        "inventory": [],
    }
    state = module.build_state(
        current_record,
        package,
        "https://zenodo.example/api",
        [old_record, current_record],
        {"versions": [historical]},
    )
    by_id = {item["capsule_id"]: item for item in state["versions"]}
    for field in ("git_commit_sha", "git_tree_oid", "package_identity_sha256", "files"):
        assert by_id["capsule-old"][field] == historical[field]


def test_sequence2_terminal_writer_keeps_historical_state_fail_closed():
    runner = (ROOT / "scripts/run_current_baseline_publication_v2_ci.sh").read_text(
        encoding="utf-8"
    )
    state_machine = (ROOT / "scripts/current_baseline_publication_v2.py").read_text(
        encoding="utf-8"
    )
    assert "pub.require_concept_series(item, concept_doi, concept_record_id)" in runner
    assert 'final.pop("public_metadata_report", None)' in state_machine


def test_external_annex_writer_preserves_current_doi_roles():
    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import publish_external_binary_annexes_to_zenodo_v4 as publisher

    reference = publisher.current_core_repository_reference()
    current = json.loads(
        (ROOT / "preservation/external-binary-annex-state.json").read_text(encoding="utf-8")
    )
    for field in (
        "core_repository_preservation_doi",
        "core_repository_preservation_doi_role",
        "current_core_repository_concept_doi",
        "current_core_repository_latest_version_doi",
        "core_repository_reference_note",
    ):
        assert reference[field] == current[field]


def test_final_runner_freezes_all_named_binding_roots():
    runner = (ROOT / "scripts/run_current_baseline_publication_v3_ci.sh").read_text(
        encoding="utf-8"
    )
    for path in (
        "archive/authority-manifest",
        "archive/btc-signature",
        "archive/eth-witness",
        "archive/trust-root-policy.json",
        "archive/evidence",
        "scripts/build_nft_cryptographic_commitment.py",
    ):
        assert path in runner


def test_evidence_evolution_handoff_is_consistent_and_non_authorizing():
    plan = json.loads((ROOT / "api/evidence-evolution-plan.v1.json").read_text(encoding="utf-8"))
    assert plan["source_digest"] == canonical_digest(plan)
    assert plan["status"] == "active_handoff"
    assert plan["current_checkpoint"]["core_version_doi"] == "10.5281/zenodo.21855814"
    assert plan["current_checkpoint"]["evidence_scope"]["bitcoin_inscriptions"] == 8
    assert plan["current_checkpoint"]["evidence_scope"]["ethereum_non_nft_anchors"] == 10
    assert plan["current_checkpoint"]["evidence_scope"]["ethereum_chronicle_nfts"] == 175
    arweave = plan["owner_decision"]["final_core_arweave_mirror"]
    assert arweave["status"] == "intentionally_deferred"
    assert arweave["authorized_for_upload"] is False
    assert plan["authorization_boundary"]["paid_arweave_upload_requires_fresh_owner_authorization_and_cost_cap"] is True
    assert (ROOT / "EVIDENCE-EVOLUTION.md").is_file()
    graph = json.loads(
        (ROOT / "api/evidence-relationship-map.v1.json").read_text(encoding="utf-8")
    )
    nodes = {item["id"]: item for item in graph["nodes"]}
    assert nodes["evidence_evolution_handoff"]["type"] == "maintenance_handoff_not_evidence"
    arweave_node = nodes["arweave_mirrors"]
    assert arweave_node["repository_capsule_record_role"] == "historical_version_only"
    assert (
        arweave_node["current_final_core_capsule_arweave_status"]
        == "intentionally_deferred_not_uploaded"
    )
    assert any(
        edge["from"] == "arweave_mirrors"
        and edge["to"] == "core_repository_zenodo_series"
        and edge["relationship"] == "mirrors_historical_capsule"
        for edge in graph["edges"]
    )
