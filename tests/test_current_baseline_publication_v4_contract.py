from __future__ import annotations

import hashlib
import copy
import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys

import pytest


ROOT = pathlib.Path(__file__).resolve().parents[1]
AUTH = ROOT / "preservation/current-baseline-publication-authorization-v4.json"
STATE_MACHINE = ROOT / "scripts/current_baseline_publication_v4.py"
RUNNER = ROOT / "scripts/run_current_baseline_publication_v4_ci.sh"
DISPATCHER = ROOT / "scripts/run_repository_preservation_refresh_ci.sh"
CONTROLLER = ROOT / ".github/workflows/repository-preservation-capsule.yml"
INVENTORY = ROOT / "api/final-evidence-inventory.v1.json"
RECOVERY = ROOT / "api/recovery-index.json"
MANIFEST = ROOT / "api/evidence-manifest.json"
PLAN = ROOT / "api/evidence-evolution-plan.v1.json"
RELATIONSHIPS = ROOT / "api/evidence-relationship-map.v1.json"
SEQ3_AUTH = ROOT / "preservation/current-baseline-publication-authorization-v3.json"

PREVIOUS_DOI = "10.5281/zenodo.21855814"
CONCEPT_DOI = "10.5281/zenodo.21739343"
REQUIRED_CHECKPOINT = "5a4999c6108f1a05e153c63a06a4a70252467aed"


def load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_digest(value: dict) -> str:
    material = dict(value)
    material.pop("source_digest", None)
    raw = json.dumps(
        material, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def state_module():
    spec = importlib.util.spec_from_file_location("current_baseline_v4_test", STATE_MACHINE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sequence4_authorization_is_exact_checkpoint_not_permanent_final():
    auth = load(AUTH)
    assert auth["schema"] == "trinityaccord.current-baseline-publication-authorization.v4"
    assert auth["sequence"] == 4
    assert auth["status"] in {"pending", "prepared", "consumed"}
    assert auth["authorized_by"] == "thechurchofagi"
    assert auth["core_concept_doi"] == CONCEPT_DOI
    assert auth["previous_core_version_doi"] == PREVIOUS_DOI
    assert auth["publication_confirmation"] == "PUBLISH_TRINITY_EVIDENCE_CHECKPOINT_V4"
    assert auth["required_evidence_checkpoint_commit_sha"] == REQUIRED_CHECKPOINT
    assert auth["include_full_repository_doi"] is True
    assert auth["include_homepage_arweave_snapshot"] is False
    assert auth["intended_as_final_evidence_freeze"] is False
    assert auth["intended_as_current_evidence_checkpoint"] is True
    assert auth["future_material_versions_allowed"] is True
    assert auth["non_amending_boundary"] is True
    assert auth["live_main_equivalence_claimed"] is False
    assert auth["checkpoint_evidence_scope"] == {
        "bitcoin_inscriptions": 8,
        "bitcoin_canonical_originals": 3,
        "bitcoin_non_amending_ancillary": 5,
        "ethereum_non_nft_anchors": 12,
        "ethereum_chronicle_nfts": 175,
        "nft_contracts": 4,
        "proof_status_required": "PASS",
        "ordinary_verification_network_required": False,
    }
    previous = auth["previous_publication"]
    assert previous["sequence"] == 3
    assert previous["doi"] == PREVIOUS_DOI
    assert previous["record_id"] == 21855814


@pytest.mark.parametrize(
    ("path", "value"),
    (
        (("include_homepage_arweave_snapshot",), True),
        (("intended_as_final_evidence_freeze",), True),
        (("future_material_versions_allowed",), False),
        (("checkpoint_evidence_scope", "ethereum_non_nft_anchors"), 10),
        (("previous_core_version_doi",), "10.5281/zenodo.21739344"),
    ),
)
def test_sequence4_authorization_mutations_fail_closed(path, value):
    module = state_module()
    mutated = copy.deepcopy(load(AUTH))
    target = mutated
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(SystemExit):
        module.validate_static_auth(mutated)


def test_sequence4_state_machine_and_generated_maps_validate():
    subprocess.run([sys.executable, str(STATE_MACHINE), "validate"], cwd=ROOT, check=True)
    for path in (RECOVERY, MANIFEST, PLAN, INVENTORY):
        data = load(path)
        assert data["source_digest"] == canonical_digest(data)
    inventory = load(INVENTORY)
    assert inventory["status"] == "current_evidence_checkpoint_model"
    assert inventory["evidence_sets"]["bitcoin_inscriptions"]["count"] == 8
    assert inventory["evidence_sets"]["ethereum_non_nft"]["count"] == 12
    assert inventory["evidence_sets"]["ethereum_chronicle_nft"]["asset_count"] == 175
    assert inventory["current_checkpoint"]["sequence"] == 4
    assert inventory["current_checkpoint"]["intended_as_permanent_final"] is False
    assert inventory["current_checkpoint"]["future_material_versions_allowed"] is True
    assert inventory["final_freeze"]["published_doi"] == PREVIOUS_DOI


def test_sequence4_prepare_and_seal_transition_in_isolated_copy(tmp_path):
    module = state_module()
    path_map = {
        "AUTH": AUTH,
        "STATE": ROOT / "preservation/repository-preservation-state-v2.json",
        "INDEX": RECOVERY,
        "EVIDENCE_MANIFEST": MANIFEST,
        "ADDRESS_SCOPE": ROOT / "api/ethereum-address-evidence-scope.v1.json",
        "EXTERNAL_STATE": ROOT / "preservation/external-binary-annex-state.json",
        "RECOVERY_CATALOG": ROOT / "preservation/recovery-catalog.json",
        "EVOLUTION_PLAN": PLAN,
        "RELATIONSHIP_MAP": RELATIONSHIPS,
    }
    for name, source in path_map.items():
        destination = tmp_path / source.name
        shutil.copy2(source, destination)
        setattr(module, name, destination)
    module.PREPARED = tmp_path / "prepared-v4.json"
    module.OBSERVATION = tmp_path / "observation-v4.json"
    module.refresh_inventory = lambda: None

    base = "a" * 40
    module.prepare(base)
    prepared_auth = load(module.AUTH)
    prepared_state = load(module.STATE)
    assert prepared_auth["status"] == "prepared"
    assert prepared_auth["prepared_base_commit_sha"] == base
    assert prepared_state["latest_doi"] == PREVIOUS_DOI
    assert prepared_state["publication_status"] == "prepared_for_evidence_checkpoint_publication_v4"
    assert prepared_state["current_evidence_checkpoint"]["arweave_snapshot_refreshed"] is False

    source = "b" * 40
    new_record = 29999999
    new_doi = f"10.5281/zenodo.{new_record}"
    package = "c" * 64
    published = load(module.STATE)
    published.update(
        {
            "latest_git_commit_sha": source,
            "latest_git_tree_oid": "d" * 40,
            "latest_record_id": new_record,
            "latest_doi": new_doi,
            "concept_doi": CONCEPT_DOI,
            "latest_package_identity_sha256": package,
        }
    )
    published.setdefault("versions", []).append(
        {
            "doi": new_doi,
            "record_id": new_record,
            "git_commit_sha": source,
            "package_identity_sha256": package,
        }
    )
    work = tmp_path / "published-work.json"
    recovery = tmp_path / "recovery-report.json"
    metadata = tmp_path / "metadata-report.json"
    work.write_text(json.dumps(published), encoding="utf-8")
    recovery.write_text(
        json.dumps({"result": "pass", "source_git_commit_sha": source}),
        encoding="utf-8",
    )
    metadata.write_text(
        json.dumps(
            {
                "status": "passed",
                "git_commit_sha": source,
                "doi": new_doi,
                "package_identity_sha256": package,
            }
        ),
        encoding="utf-8",
    )
    module.seal(source, work, recovery, metadata)
    consumed = load(module.AUTH)
    final = load(module.STATE)
    final_index = load(module.INDEX)
    assert consumed["status"] == "consumed"
    assert consumed["published_doi"] == new_doi
    assert final["latest_doi"] == new_doi
    assert final["current_evidence_checkpoint"]["intended_as_final_evidence_freeze"] is False
    assert final["current_evidence_checkpoint"]["future_material_versions_allowed"] is True
    assert final["current_evidence_checkpoint"]["arweave_snapshot_refreshed"] is False
    assert final_index["latest_trusted_release"]["repository_additions_after_published_baseline"] == {}
    assert "pending_evidence_checkpoint" not in final_index
    assert load(module.OBSERVATION)["arweave_snapshot_refreshed"] is False


def test_sequence4_pending_or_published_machine_discovery_is_fail_closed():
    auth = load(AUTH)
    manifest = load(MANIFEST)["current_cryptographic_proof_state"]
    recovery = load(RECOVERY)
    plan = load(PLAN)
    graph = load(RELATIONSHIPS)
    assert manifest["ethereum_non_nft"]["anchor_count"] == 12
    assert manifest["repository_preservation"]["current_checkpoint_authorization"].endswith(
        "current-baseline-publication-authorization-v4.json"
    )
    assert plan["owner_decision"]["final_core_arweave_mirror"]["authorized_for_upload"] is False
    nodes = {item["id"]: item for item in graph["nodes"]}
    assert nodes["final_evidence_inventory"]["scope"]["ethereum_non_nft"] == 12
    assert nodes["historical_final_evidence_freeze_v3"]["version_doi"] == PREVIOUS_DOI
    if auth["status"] == "consumed":
        assert "pending_evidence_checkpoint" not in recovery
        assert recovery["publication_refresh"]["sequence"] == 4
        assert recovery["latest_trusted_release"]["repository_additions_after_published_baseline"] == {}
        assert plan["current_checkpoint"]["core_version_doi"] == auth["published_doi"]
        assert "pending_checkpoint_v4" not in plan
    else:
        assert recovery["pending_evidence_checkpoint"]["sequence"] == 4
        assert recovery["pending_evidence_checkpoint"]["status"] in {
            "owner_authorized_pending_publication",
            "prepared",
        }
        assert plan["pending_checkpoint_v4"]["status"] in {
            "owner_authorized_pending_publication",
            "prepared",
        }


def test_sequence4_runner_is_zenodo_only_lineage_locked_and_retry_safe():
    subprocess.run(["bash", "-n", str(RUNNER)], cwd=ROOT, check=True)
    runner = RUNNER.read_text(encoding="utf-8")
    assert "publish_preservation_capsule_to_zenodo_v3.py" in runner
    assert "repository_preservation_refresh.py verify-public" in runner
    assert "restore-trinity-accord.py" in runner
    assert "required_evidence_checkpoint_commit_sha" in runner
    assert "matching_published" in runner and "matching_drafts" in runner
    assert PREVIOUS_DOI in runner and CONCEPT_DOI in runner
    assert "git diff --quiet" in runner
    assert "ARKEY" not in runner
    assert "arweave_upload_homepage_snapshot" not in runner
    assert "record_arweave_upload_result" not in runner
    assert "phase5-ots-arweave-paid-upload" not in runner


def test_dispatcher_and_controller_prioritize_sequence4_safely():
    subprocess.run(["bash", "-n", str(DISPATCHER)], cwd=ROOT, check=True)
    dispatcher = DISPATCHER.read_text(encoding="utf-8")
    v4 = dispatcher.index("current-baseline-publication-authorization-v4.json")
    v3 = dispatcher.index("current-baseline-publication-authorization-v3.json")
    v2 = dispatcher.index("current-baseline-publication-authorization-v2.json")
    assert v4 < v3 < v2
    assert "run_current_baseline_publication_v4_ci.sh" in dispatcher
    assert "TRINITY_PRESERVATION_REFRESH_EXECUTOR" in dispatcher
    controller = CONTROLLER.read_text(encoding="utf-8")
    assert "scripts/run_current_baseline_publication_v4_ci.sh" in controller
    assert "scripts/current_baseline_publication_v4.py" in controller
    assert "preservation/current-baseline-publication-authorization-v4.json" in controller
    install = "python3 -m pip install -r requirements-ci.txt"
    execute = "bash scripts/run_repository_preservation_refresh_ci.sh"
    assert controller.index(install) < controller.index(execute)


def test_sequence3_publication_history_is_immutable_and_linked():
    seq3 = load(SEQ3_AUTH)
    seq4 = load(AUTH)
    assert seq3["status"] == "consumed"
    assert seq3["published_doi"] == PREVIOUS_DOI
    assert seq4["previous_publication"]["doi"] == seq3["published_doi"]
    assert seq4["previous_publication"]["source_baseline_commit_sha"] == seq3[
        "published_source_baseline_commit_sha"
    ]
    assert seq4["previous_publication"]["package_identity_sha256"] == seq3[
        "published_package_identity_sha256"
    ]
