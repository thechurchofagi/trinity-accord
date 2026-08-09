#!/usr/bin/env python3
"""Sequence-4 one-shot current-evidence checkpoint publication state machine.

This lifecycle advances the existing repository-preservation Concept DOI by one
owner-authorized version.  It freezes the complete current 8 Bitcoin + 12
Ethereum + 175 NFT proof topology, performs no Arweave write, remains
non-amending, and explicitly allows later material evidence versions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "preservation/current-baseline-publication-authorization-v4.json"
PREPARED = ROOT / "preservation/current-baseline-publication-prepared-v4.json"
OBSERVATION = ROOT / "preservation/current-baseline-publication-observation-v4.json"
STATE = ROOT / "preservation/repository-preservation-state-v2.json"
INDEX = ROOT / "api/recovery-index.json"
EVIDENCE_MANIFEST = ROOT / "api/evidence-manifest.json"
ADDRESS_SCOPE = ROOT / "api/ethereum-address-evidence-scope.v1.json"
EXTERNAL_STATE = ROOT / "preservation/external-binary-annex-state.json"
RECOVERY_CATALOG = ROOT / "preservation/recovery-catalog.json"
EVOLUTION_PLAN = ROOT / "api/evidence-evolution-plan.v1.json"
RELATIONSHIP_MAP = ROOT / "api/evidence-relationship-map.v1.json"
SEQ3_AUTH = ROOT / "preservation/current-baseline-publication-authorization-v3.json"
SEQ3_PREPARED = ROOT / "preservation/current-baseline-publication-prepared-v3.json"
SEQ3_OBSERVATION = ROOT / "preservation/current-baseline-publication-observation-v3.json"

CONCEPT_DOI = "10.5281/zenodo.21739343"
PREVIOUS_DOI = "10.5281/zenodo.21855814"
PREVIOUS_RECORD_ID = 21855814
PREVIOUS_SOURCE = "887322dc7f6f64efd04f7452e2039ee4440b226b"
PREVIOUS_PACKAGE = "a5a9bf9a6ed6a3bcb493c73a8679a6d468cdc6a08f9322e6620c44da4b19f06c"
REQUIRED_CHECKPOINT = "5a4999c6108f1a05e153c63a06a4a70252467aed"
RIGHTS_ACK = "TRINITY_PRESERVATION_CAPSULE_RIGHTS_V1_APPROVED"
CONFIRMATION = "PUBLISH_TRINITY_EVIDENCE_CHECKPOINT_V4"
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DOI_RE = re.compile(r"^10\.5281/zenodo\.([0-9]+)$")

EXPECTED_SCOPE = {
    "bitcoin_inscriptions": 8,
    "bitcoin_canonical_originals": 3,
    "bitcoin_non_amending_ancillary": 5,
    "ethereum_non_nft_anchors": 12,
    "ethereum_chronicle_nfts": 175,
    "nft_contracts": 4,
    "proof_status_required": "PASS",
    "ordinary_verification_network_required": False,
}


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"invalid JSON: {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path.relative_to(ROOT)}")
    return value


def write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def canonical_digest(value: dict[str, Any]) -> str:
    material = dict(value)
    material.pop("source_digest", None)
    raw = json.dumps(
        material,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def update_digest(value: dict[str, Any]) -> None:
    value["source_digest"] = canonical_digest(value)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def require_equal(observed: Any, expected: Any, label: str) -> None:
    if observed != expected:
        raise SystemExit(f"{label} mismatch: observed={observed!r} expected={expected!r}")


def node(graph: dict[str, Any], node_id: str) -> dict[str, Any]:
    for item in graph.get("nodes", []):
        if isinstance(item, dict) and item.get("id") == node_id:
            return item
    raise SystemExit(f"relationship map missing node: {node_id}")


def inventory_module():
    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import build_final_evidence_inventory  # type: ignore

    return build_final_evidence_inventory


def refresh_inventory() -> None:
    module = inventory_module()
    module.write_outputs(module.build())


def validate_static_auth(auth: dict[str, Any]) -> None:
    expected = {
        "schema": "trinityaccord.current-baseline-publication-authorization.v4",
        "sequence": 4,
        "authorized_by": "thechurchofagi",
        "core_concept_doi": CONCEPT_DOI,
        "previous_core_version_doi": PREVIOUS_DOI,
        "zenodo_rights_acknowledgement": RIGHTS_ACK,
        "publication_confirmation": CONFIRMATION,
        "include_full_repository_doi": True,
        "include_homepage_arweave_snapshot": False,
        "intended_as_final_evidence_freeze": False,
        "intended_as_current_evidence_checkpoint": True,
        "future_material_versions_allowed": True,
        "non_amending_boundary": True,
        "live_main_equivalence_claimed": False,
        "required_evidence_checkpoint_commit_sha": REQUIRED_CHECKPOINT,
        "checkpoint_evidence_scope": EXPECTED_SCOPE,
    }
    for key, expected_value in expected.items():
        require_equal(auth.get(key), expected_value, f"authorization.{key}")
    previous = auth.get("previous_publication")
    require(isinstance(previous, dict), "authorization.previous_publication missing")
    for key, expected_value in {
        "sequence": 3,
        "source_baseline_commit_sha": PREVIOUS_SOURCE,
        "doi": PREVIOUS_DOI,
        "record_id": PREVIOUS_RECORD_ID,
        "package_identity_sha256": PREVIOUS_PACKAGE,
    }.items():
        require_equal(previous.get(key), expected_value, f"authorization.previous_publication.{key}")


def validate_sequence3_history(state: dict[str, Any]) -> None:
    auth = load(SEQ3_AUTH)
    require_equal(auth.get("status"), "consumed", "sequence3.status")
    require_equal(auth.get("published_source_baseline_commit_sha"), PREVIOUS_SOURCE, "sequence3.source")
    require_equal(auth.get("published_doi"), PREVIOUS_DOI, "sequence3.doi")
    require_equal(auth.get("published_record_id"), PREVIOUS_RECORD_ID, "sequence3.record_id")
    require_equal(auth.get("published_package_identity_sha256"), PREVIOUS_PACKAGE, "sequence3.package")
    prepared = load(SEQ3_PREPARED)
    observation = load(SEQ3_OBSERVATION)
    require_equal(prepared.get("status"), "published_verified", "sequence3.prepared.status")
    require_equal(prepared.get("version_doi"), PREVIOUS_DOI, "sequence3.prepared.doi")
    require_equal(observation.get("status"), "passed", "sequence3.observation.status")
    require_equal(observation.get("version_doi"), PREVIOUS_DOI, "sequence3.observation.doi")
    versions = state.get("versions")
    require(isinstance(versions, list), "state.versions missing")
    matches = [item for item in versions if isinstance(item, dict) and item.get("doi") == PREVIOUS_DOI]
    require(len(matches) == 1, "sequence-3 DOI must appear exactly once in preservation history")
    require_equal(matches[0].get("git_commit_sha"), PREVIOUS_SOURCE, "sequence3.history.source")
    require_equal(matches[0].get("package_identity_sha256"), PREVIOUS_PACKAGE, "sequence3.history.package")


def validate_generated(auth: dict[str, Any], index: dict[str, Any]) -> None:
    require_equal(index.get("source_digest"), canonical_digest(index), "recovery.source_digest")
    evidence = load(EVIDENCE_MANIFEST)
    require_equal(evidence.get("source_digest"), canonical_digest(evidence), "evidence.source_digest")
    plan = load(EVOLUTION_PLAN)
    require_equal(plan.get("source_digest"), canonical_digest(plan), "evolution.source_digest")
    module = inventory_module()
    expected = module.build()
    module.check_outputs(expected)
    checkpoint = expected.get("current_checkpoint")
    require(isinstance(checkpoint, dict), "inventory.current_checkpoint missing")
    require_equal(checkpoint.get("status"), auth.get("status"), "inventory.current_checkpoint.status")
    require_equal(expected["evidence_sets"]["bitcoin_inscriptions"]["count"], 8, "inventory.bitcoin.count")
    require_equal(expected["evidence_sets"]["ethereum_non_nft"]["count"], 12, "inventory.ethereum.count")
    require_equal(expected["evidence_sets"]["ethereum_chronicle_nft"]["asset_count"], 175, "inventory.nft.count")


def validate_relationship_topology() -> None:
    graph = load(RELATIONSHIP_MAP)
    node_ids = {item.get("id") for item in graph.get("nodes", []) if isinstance(item, dict)}
    required = {
        "final_evidence_inventory",
        "historical_final_evidence_freeze_v3",
        "current_live_evidence_state",
        "bitcoin_inscription_proof_annex",
        "ethereum_non_nft_proof_annex",
        "chronicle_nft_proof_annex",
        "core_repository_zenodo_series",
    }
    require(required <= node_ids, f"relationship map missing nodes: {sorted(required - node_ids)}")
    require_equal(node(graph, "final_evidence_inventory").get("scope", {}).get("ethereum_non_nft"), 12, "relationship.inventory.ethereum")
    entrypoints = load(EVIDENCE_MANIFEST).get("evidence_system_entrypoints")
    require(isinstance(entrypoints, dict), "evidence manifest lacks evidence-system entrypoints")
    require_equal(entrypoints.get("final_inventory"), "/api/final-evidence-inventory.v1.json", "entrypoints.inventory")
    require_equal(entrypoints.get("recovery_index"), "/api/recovery-index.json", "entrypoints.recovery")


def validate_pending(auth: dict[str, Any], state: dict[str, Any], index: dict[str, Any]) -> None:
    require_equal(auth.get("status"), "pending", "authorization.status")
    require_equal(state.get("publication_status"), "published_and_publicly_restored", "state.publication_status")
    require_equal(state.get("latest_doi"), PREVIOUS_DOI, "state.latest_doi")
    require_equal(state.get("latest_record_id"), PREVIOUS_RECORD_ID, "state.latest_record_id")
    require_equal(state.get("latest_git_commit_sha"), PREVIOUS_SOURCE, "state.latest_source")
    require_equal(state.get("latest_package_identity_sha256"), PREVIOUS_PACKAGE, "state.latest_package")
    pending = index.get("pending_evidence_checkpoint")
    require(isinstance(pending, dict), "recovery pending_evidence_checkpoint missing")
    require_equal(pending.get("sequence"), 4, "recovery.pending.sequence")
    require_equal(pending.get("status"), "owner_authorized_pending_publication", "recovery.pending.status")
    current = load(EVIDENCE_MANIFEST)["current_cryptographic_proof_state"]
    require_equal(current["ethereum_non_nft"].get("anchor_count"), 12, "manifest.ethereum.count")
    preservation = current["repository_preservation"]
    require_equal(preservation.get("current_checkpoint_status"), "owner_authorized_pending_publication", "manifest.checkpoint.status")
    require_equal(preservation.get("latest_published_version_doi"), PREVIOUS_DOI, "manifest.latest_doi")
    catalog = load(RECOVERY_CATALOG)["core_repository"].get("current_evidence_checkpoint")
    require(isinstance(catalog, dict), "recovery catalog current checkpoint missing")
    require_equal(catalog.get("status"), "owner_authorized_pending_publication", "catalog.checkpoint.status")
    plan = load(EVOLUTION_PLAN).get("pending_checkpoint_v4")
    require(isinstance(plan, dict), "evolution pending checkpoint missing")
    require_equal(plan.get("status"), "owner_authorized_pending_publication", "evolution.pending.status")
    boundary = load(ADDRESS_SCOPE).get("freeze_boundary", {})
    require_equal(boundary.get("new_doi_publication_status"), "owner_authorized_pending_publication_v4", "address_scope.doi_status")


def validate_prepared(auth: dict[str, Any], state: dict[str, Any], index: dict[str, Any]) -> dict[str, Any]:
    require_equal(auth.get("status"), "prepared", "authorization.status")
    prepared = load(PREPARED)
    require_equal(prepared.get("schema"), "trinityaccord.current-baseline-publication-prepared.v4", "prepared.schema")
    require_equal(prepared.get("sequence"), 4, "prepared.sequence")
    require_equal(prepared.get("status"), "prepared", "prepared.status")
    require_equal(prepared.get("base_commit_sha"), auth.get("prepared_base_commit_sha"), "prepared.base_commit")
    require_equal(prepared.get("previous_version_doi"), PREVIOUS_DOI, "prepared.previous_doi")
    require_equal(prepared.get("required_evidence_checkpoint_commit_sha"), REQUIRED_CHECKPOINT, "prepared.required_checkpoint")
    require_equal(state.get("publication_status"), "prepared_for_evidence_checkpoint_publication_v4", "state.publication_status")
    require_equal(state.get("latest_doi"), PREVIOUS_DOI, "state.latest_doi_during_prepare")
    refresh = index.get("publication_refresh")
    require(isinstance(refresh, dict), "prepared recovery publication_refresh missing")
    require_equal(refresh.get("sequence"), 4, "prepared recovery sequence")
    require_equal(refresh.get("status"), "prepared_for_evidence_checkpoint_publication", "prepared recovery status")
    pending = index.get("pending_evidence_checkpoint")
    require(isinstance(pending, dict), "prepared pending checkpoint missing")
    require_equal(pending.get("status"), "prepared", "prepared pending status")
    preservation = load(EVIDENCE_MANIFEST)["current_cryptographic_proof_state"]["repository_preservation"]
    require_equal(preservation.get("current_checkpoint_status"), "prepared", "manifest.checkpoint.status")
    require_equal(load(ADDRESS_SCOPE).get("freeze_boundary", {}).get("new_doi_publication_status"), "prepared_for_publication_v4", "address_scope.doi_status")
    return prepared


def validate_consumed(auth: dict[str, Any], state: dict[str, Any], index: dict[str, Any]) -> None:
    require_equal(auth.get("status"), "consumed", "authorization.status")
    source = auth.get("published_source_baseline_commit_sha")
    doi = auth.get("published_doi")
    record_id = auth.get("published_record_id")
    package = auth.get("published_package_identity_sha256")
    require(isinstance(source, str) and COMMIT_RE.fullmatch(source) is not None, "invalid checkpoint source")
    match = DOI_RE.fullmatch(str(doi))
    require(match is not None and doi != PREVIOUS_DOI, "invalid or non-new checkpoint DOI")
    require(isinstance(record_id, int) and int(match.group(1)) == record_id, "checkpoint DOI/record mismatch")
    require(isinstance(package, str) and SHA256_RE.fullmatch(package) is not None, "invalid checkpoint package identity")
    require_equal(state.get("publication_status"), "published_and_publicly_restored", "state.publication_status")
    require_equal(state.get("latest_git_commit_sha"), source, "state.latest_source")
    require_equal(state.get("latest_doi"), doi, "state.latest_doi")
    require_equal(state.get("latest_record_id"), record_id, "state.latest_record_id")
    require_equal(state.get("latest_package_identity_sha256"), package, "state.latest_package")
    require_equal(state.get("concept_doi"), CONCEPT_DOI, "state.concept_doi")
    require_equal(state.get("public_metadata_verification"), "passed", "state.public_metadata")
    require_equal(state.get("public_cold_restore"), "passed", "state.public_restore")
    require_equal(state.get("live_main_equivalence_claimed"), False, "state.live_main_equivalence")
    checkpoint = state.get("current_evidence_checkpoint")
    require(isinstance(checkpoint, dict), "state current_evidence_checkpoint missing")
    require_equal(checkpoint.get("status"), "published_verified_and_consumed", "state.checkpoint.status")
    require_equal(checkpoint.get("evidence_scope"), EXPECTED_SCOPE, "state.checkpoint.scope")
    require_equal(checkpoint.get("intended_as_final_evidence_freeze"), False, "state.checkpoint.final")
    versions = state.get("versions")
    require(isinstance(versions, list), "state.versions missing")
    by_doi = {item.get("doi"): item for item in versions if isinstance(item, dict)}
    require(PREVIOUS_DOI in by_doi and doi in by_doi, "state versions lack predecessor or checkpoint DOI")
    prepared = load(PREPARED)
    observation = load(OBSERVATION)
    require_equal(prepared.get("status"), "published_verified", "prepared.status")
    require_equal(prepared.get("source_git_commit_sha"), source, "prepared.source")
    require_equal(prepared.get("version_doi"), doi, "prepared.doi")
    require_equal(observation.get("status"), "passed", "observation.status")
    require_equal(observation.get("source_git_commit_sha"), source, "observation.source")
    require_equal(observation.get("version_doi"), doi, "observation.doi")
    require_equal(observation.get("public_cold_restore"), "passed", "observation.restore")
    require_equal(observation.get("arweave_snapshot_refreshed"), False, "observation.arweave")
    refresh = index.get("publication_refresh")
    require(isinstance(refresh, dict), "checkpoint recovery publication_refresh missing")
    require_equal(refresh.get("sequence"), 4, "checkpoint recovery sequence")
    require_equal(refresh.get("status"), "published_verified_and_consumed", "checkpoint recovery status")
    require("pending_evidence_checkpoint" not in index, "consumed index retains pending checkpoint")
    additions = index.get("latest_trusted_release", {}).get("repository_additions_after_published_baseline")
    require_equal(additions, {}, "checkpoint repository additions")
    latest = index.get("latest_trusted_release", {}).get("repository_preservation", {})
    require_equal(latest.get("doi"), doi, "recovery.latest.doi")
    require_equal(latest.get("git_commit_sha"), source, "recovery.latest.source")
    preservation = load(EVIDENCE_MANIFEST)["current_cryptographic_proof_state"]["repository_preservation"]
    require_equal(preservation.get("latest_published_version_doi"), doi, "manifest.latest_doi")
    require_equal(preservation.get("current_checkpoint_status"), "published_verified_and_consumed", "manifest.checkpoint.status")
    require_equal(preservation.get("current_checkpoint_source_baseline_commit_sha"), source, "manifest.checkpoint.source")
    external = load(EXTERNAL_STATE)
    require_equal(external.get("current_core_repository_latest_version_doi"), doi, "external.current_core_doi")
    catalog = load(RECOVERY_CATALOG).get("core_repository", {})
    require_equal(catalog.get("current_verified_version_doi"), doi, "catalog.current_doi")
    require_equal(catalog.get("current_verified_source_git_commit_sha"), source, "catalog.current_source")
    require_equal(catalog.get("current_evidence_checkpoint", {}).get("status"), "published_verified_and_consumed", "catalog.checkpoint.status")
    plan = load(EVOLUTION_PLAN)
    require_equal(plan.get("current_checkpoint", {}).get("core_version_doi"), doi, "evolution.current.doi")
    require_equal(plan.get("pending_checkpoint_v4"), None, "evolution.pending")
    graph = load(RELATIONSHIP_MAP)
    require_equal(node(graph, "core_repository_zenodo_series").get("latest_version_doi"), doi, "relationship.core.doi")
    boundary = load(ADDRESS_SCOPE).get("freeze_boundary", {})
    require_equal(boundary.get("current_checkpoint_v4_version_doi"), doi, "address_scope.checkpoint.doi")
    require_equal(boundary.get("current_checkpoint_v4_includes_post_freeze_additions"), True, "address_scope.checkpoint.includes_delta")


def validate() -> None:
    auth = load(AUTH)
    state = load(STATE)
    index = load(INDEX)
    validate_static_auth(auth)
    validate_sequence3_history(state)
    validate_relationship_topology()
    status = auth.get("status")
    if status == "pending":
        validate_pending(auth, state, index)
    elif status == "prepared":
        validate_prepared(auth, state, index)
    elif status == "consumed":
        validate_consumed(auth, state, index)
    else:
        raise SystemExit(f"invalid sequence-4 authorization status: {status!r}")
    validate_generated(auth, index)
    print(f"Current evidence checkpoint publication v4 state valid: {status}")


def initialize_pending() -> None:
    auth = load(AUTH)
    state = load(STATE)
    index = load(INDEX)
    evidence = load(EVIDENCE_MANIFEST)
    catalog = load(RECOVERY_CATALOG)
    plan = load(EVOLUTION_PLAN)
    graph = load(RELATIONSHIP_MAP)
    address_scope = load(ADDRESS_SCOPE)
    validate_static_auth(auth)
    require_equal(auth.get("status"), "pending", "authorization.status")
    validate_sequence3_history(state)
    require_equal(state.get("latest_doi"), PREVIOUS_DOI, "state.latest_doi")

    index["pending_evidence_checkpoint"] = {
        "schema": auth["schema"],
        "sequence": 4,
        "status": "owner_authorized_pending_publication",
        "authorization": "preservation/current-baseline-publication-authorization-v4.json",
        "previous_version_doi": PREVIOUS_DOI,
        "core_concept_doi": CONCEPT_DOI,
        "required_evidence_checkpoint_commit_sha": REQUIRED_CHECKPOINT,
        "evidence_scope": EXPECTED_SCOPE,
        "arweave_snapshot_requested": False,
        "intended_as_final_evidence_freeze": False,
        "future_material_versions_allowed": True,
        "non_amending_boundary": True,
    }
    required_files = index.setdefault("required_recovery_files", [])
    for relative in (
        "preservation/current-baseline-publication-authorization-v4.json",
        "scripts/current_baseline_publication_v4.py",
        "scripts/run_current_baseline_publication_v4_ci.sh",
    ):
        if relative not in required_files:
            required_files.append(relative)
    additions = index.setdefault("latest_trusted_release", {}).setdefault(
        "repository_additions_after_published_baseline", {}
    )
    for addition in additions.values():
        if isinstance(addition, dict):
            addition["new_doi_publication"] = "owner_authorized_pending_publication_v4"
            addition["future_checkpoint_scope"] = "8_bitcoin_12_ethereum_175_nft"
    limitations = index.get("limitations", [])
    if isinstance(limitations, list):
        for position, item in enumerate(limitations):
            if isinstance(item, str) and item.startswith("Current GitHub adds two offline-verified Ethereum"):
                limitations[position] = (
                    "Current GitHub adds two offline-verified Ethereum authority/signature anchors after DOI v3. "
                    "Sequence 4 is owner-authorized to freeze the complete 8 + 12 + 175 checkpoint; until it is "
                    "consumed, the two-anchor delta still requires a named verified Git commit."
                )
    update_digest(index)

    current = evidence["current_cryptographic_proof_state"]
    eth = current["ethereum_non_nft"]
    eth["next_checkpoint_v4_anchor_count"] = 12
    eth["next_checkpoint_v4_status"] = "owner_authorized_pending_publication"
    preservation = current["repository_preservation"]
    preservation.update(
        {
            "current_checkpoint_authorization": "preservation/current-baseline-publication-authorization-v4.json",
            "current_checkpoint_status": "owner_authorized_pending_publication",
            "current_checkpoint_required_evidence_commit_sha": REQUIRED_CHECKPOINT,
            "current_checkpoint_intended_as_permanent_final": False,
            "current_checkpoint_future_material_versions_allowed": True,
            "current_checkpoint_scope": EXPECTED_SCOPE,
            "current_checkpoint_arweave_upload_requested": False,
        }
    )
    preservation["live_repository_delta"]["new_doi_publication"] = "owner_authorized_pending_publication_v4"
    update_digest(evidence)

    boundary = address_scope["freeze_boundary"]
    boundary.update(
        {
            "new_doi_publication_status": "owner_authorized_pending_publication_v4",
            "new_arweave_upload_status": "intentionally_deferred_not_authorized",
            "current_checkpoint_v4_includes_post_freeze_additions": False,
            "current_checkpoint_v4_authorization": "preservation/current-baseline-publication-authorization-v4.json",
        }
    )
    update_digest(address_scope)

    catalog["core_repository"]["current_evidence_checkpoint"] = {
        "sequence": 4,
        "status": "owner_authorized_pending_publication",
        "authorization": "preservation/current-baseline-publication-authorization-v4.json",
        "previous_version_doi": PREVIOUS_DOI,
        "core_concept_doi": CONCEPT_DOI,
        "evidence_scope": EXPECTED_SCOPE,
        "arweave_snapshot_requested": False,
        "future_material_versions_allowed": True,
    }

    plan["pending_checkpoint_v4"] = {
        "status": "owner_authorized_pending_publication",
        "authorization": "preservation/current-baseline-publication-authorization-v4.json",
        "core_concept_doi": CONCEPT_DOI,
        "previous_version_doi": PREVIOUS_DOI,
        "evidence_scope": EXPECTED_SCOPE,
        "arweave_upload_authorized": False,
        "intended_as_permanent_final": False,
        "future_material_versions_allowed": True,
    }
    plan["live_repository_checkpoint"]["new_doi_publication_status"] = "owner_authorized_pending_publication_v4"
    plan["live_repository_checkpoint"]["new_arweave_upload_status"] = "intentionally_deferred_not_authorized"
    plan["authorization_boundary"]["latest_zenodo_authorization"] = (
        "sequence_4_checkpoint_authorized_pending_publication"
    )
    plan["future_agent_start_sequence"][0] = (
        "Read api/final-evidence-inventory.v1.json as the current 8 + 12 + 175 checkpoint inventory; "
        "read its historical final_freeze object for immutable DOI v3 and current_checkpoint for sequence 4."
    )
    plan["future_agent_start_sequence"][5] = (
        "While sequence 4 is pending, compare current GitHub main against DOI v3 source baseline "
        f"{PREVIOUS_SOURCE} and preserve the explicit two-anchor delta boundary."
    )
    update_digest(plan)

    inventory_node = node(graph, "final_evidence_inventory")
    inventory_node["scope"] = {
        "bitcoin_inscriptions": 8,
        "ethereum_non_nft": 12,
        "chronicle_nft": 175,
    }
    inventory_node["freeze_role"] = "current checkpoint v4 inventory; publication pending"
    inventory_node["role"] = (
        "Indexes the current 8 + 12 + 175 verified evidence checkpoint while preserving DOI v3 as immutable history."
    )
    core_node = node(graph, "core_repository_zenodo_series")
    core_node["latest_version_doi"] = PREVIOUS_DOI
    core_node["pending_checkpoint_v4"] = {
        "status": "owner_authorized_pending_publication",
        "authorization": "preservation/current-baseline-publication-authorization-v4.json",
        "scope": inventory_node["scope"],
        "arweave_upload_requested": False,
    }
    if not any(
        isinstance(item, dict) and item.get("id") == "historical_final_evidence_freeze_v3"
        for item in graph.get("nodes", [])
    ):
        graph.setdefault("nodes", []).append(
            {
                "id": "historical_final_evidence_freeze_v3",
                "type": "immutable_historical_evidence_freeze",
                "version_doi": PREVIOUS_DOI,
                "source_baseline_commit_sha": PREVIOUS_SOURCE,
                "scope": {
                    "bitcoin_inscriptions": 8,
                    "ethereum_non_nft": 10,
                    "chronicle_nft": 175,
                },
                "role": "Preserves the immutable sequence-3 snapshot without claiming it contains the later two Ethereum anchors.",
            }
        )
        graph.setdefault("edges", []).append(
            {
                "from": "final_evidence_inventory",
                "to": "historical_final_evidence_freeze_v3",
                "relationship": "extends_without_mutating",
            }
        )

    write(INDEX, index)
    write(EVIDENCE_MANIFEST, evidence)
    write(ADDRESS_SCOPE, address_scope)
    write(RECOVERY_CATALOG, catalog)
    write(EVOLUTION_PLAN, plan)
    write(RELATIONSHIP_MAP, graph)
    refresh_inventory()


def prepare(base_commit: str) -> None:
    auth = load(AUTH)
    state = load(STATE)
    index = load(INDEX)
    evidence = load(EVIDENCE_MANIFEST)
    catalog = load(RECOVERY_CATALOG)
    plan = load(EVOLUTION_PLAN)
    graph = load(RELATIONSHIP_MAP)
    address_scope = load(ADDRESS_SCOPE)
    validate_static_auth(auth)
    validate_pending(auth, state, index)
    require(COMMIT_RE.fullmatch(base_commit) is not None, "base commit must be a full Git SHA")

    previous = {
        "doi": state.get("latest_doi"),
        "record_id": state.get("latest_record_id"),
        "git_commit_sha": state.get("latest_git_commit_sha"),
        "git_tree_oid": state.get("latest_git_tree_oid"),
        "package_identity_sha256": state.get("latest_package_identity_sha256"),
    }
    auth.update({"status": "prepared", "prepared_base_commit_sha": base_commit})
    state.update(
        {
            "publication_status": "prepared_for_evidence_checkpoint_publication_v4",
            "prepared_base_commit_sha": base_commit,
            "previous_verified_version": previous,
            "planned_homepage_arweave_snapshot": False,
            "live_main_equivalence_claimed": False,
            "current_evidence_checkpoint": {
                "status": "prepared",
                "sequence": 4,
                "evidence_scope": EXPECTED_SCOPE,
                "intended_as_final_evidence_freeze": False,
                "future_material_versions_allowed": True,
                "arweave_snapshot_refreshed": False,
            },
        }
    )
    index["publication_refresh"] = {
        "schema": auth["schema"],
        "sequence": 4,
        "status": "prepared_for_evidence_checkpoint_publication",
        "authorized_base_commit_sha": base_commit,
        "required_evidence_checkpoint_commit_sha": REQUIRED_CHECKPOINT,
        "previous_version_doi": PREVIOUS_DOI,
        "core_concept_doi": CONCEPT_DOI,
        "arweave_snapshot_refreshed": False,
        "intended_as_final_evidence_freeze": False,
        "future_material_versions_allowed": True,
        "non_amending_boundary": True,
    }
    index["pending_evidence_checkpoint"].update(
        {"status": "prepared", "authorized_base_commit_sha": base_commit}
    )
    update_digest(index)
    preservation = evidence["current_cryptographic_proof_state"]["repository_preservation"]
    preservation.update(
        {
            "current_checkpoint_status": "prepared",
            "current_checkpoint_authorized_base_commit_sha": base_commit,
            "published_baseline_boundary": (
                "DOI v3 remains the latest public immutable baseline while the owner-authorized "
                "8 + 12 + 175 checkpoint is prepared and not yet published."
            ),
        }
    )
    update_digest(evidence)
    address_scope["freeze_boundary"]["new_doi_publication_status"] = "prepared_for_publication_v4"
    update_digest(address_scope)
    catalog["core_repository"]["current_evidence_checkpoint"].update(
        {"status": "prepared", "authorized_base_commit_sha": base_commit}
    )
    plan["pending_checkpoint_v4"].update(
        {"status": "prepared", "authorized_base_commit_sha": base_commit}
    )
    update_digest(plan)
    node(graph, "core_repository_zenodo_series")["pending_checkpoint_v4"].update(
        {"status": "prepared", "authorized_base_commit_sha": base_commit}
    )
    prepared = {
        "schema": "trinityaccord.current-baseline-publication-prepared.v4",
        "sequence": 4,
        "status": "prepared",
        "base_commit_sha": base_commit,
        "required_evidence_checkpoint_commit_sha": REQUIRED_CHECKPOINT,
        "previous_version_doi": PREVIOUS_DOI,
        "core_concept_doi": CONCEPT_DOI,
        "publication_scope": "full_git_tracked_current_evidence_checkpoint",
        "checkpoint_evidence_scope": EXPECTED_SCOPE,
        "arweave_snapshot_refreshed": False,
        "intended_as_final_evidence_freeze": False,
        "future_material_versions_allowed": True,
        "boundary": {
            "non_amending": True,
            "bitcoin_originals_prevail": True,
            "repository_doi_is_exact_baseline_not_live_main": True,
        },
    }
    write(AUTH, auth)
    write(STATE, state)
    write(INDEX, index)
    write(EVIDENCE_MANIFEST, evidence)
    write(ADDRESS_SCOPE, address_scope)
    write(RECOVERY_CATALOG, catalog)
    write(EVOLUTION_PLAN, plan)
    write(RELATIONSHIP_MAP, graph)
    write(PREPARED, prepared)
    refresh_inventory()


def seal(
    source_commit: str,
    published_state_path: Path,
    recovery_report_path: Path,
    metadata_report_path: Path,
) -> None:
    auth = load(AUTH)
    state = load(STATE)
    index = load(INDEX)
    evidence = load(EVIDENCE_MANIFEST)
    external = load(EXTERNAL_STATE)
    catalog = load(RECOVERY_CATALOG)
    plan = load(EVOLUTION_PLAN)
    graph = load(RELATIONSHIP_MAP)
    address_scope = load(ADDRESS_SCOPE)
    validate_static_auth(auth)
    prepared = validate_prepared(auth, state, index)
    published = load(published_state_path)
    recovery = load(recovery_report_path)
    metadata = load(metadata_report_path)
    require(COMMIT_RE.fullmatch(source_commit) is not None, "seal requires an exact source commit")
    require_equal(published.get("latest_git_commit_sha"), source_commit, "published.latest_source")
    require_equal(published.get("concept_doi"), CONCEPT_DOI, "published.concept_doi")
    new_doi = published.get("latest_doi")
    match = DOI_RE.fullmatch(str(new_doi))
    require(match is not None and new_doi != PREVIOUS_DOI, "publisher did not create/reconcile a new checkpoint DOI")
    record_id = published.get("latest_record_id")
    require(isinstance(record_id, int) and int(match.group(1)) == record_id, "publisher DOI/record mismatch")
    package = published.get("latest_package_identity_sha256")
    require(isinstance(package, str) and SHA256_RE.fullmatch(package) is not None, "invalid publisher package identity")
    require_equal(recovery.get("result"), "pass", "public_recovery.result")
    require_equal(recovery.get("source_git_commit_sha"), source_commit, "public_recovery.source")
    require_equal(metadata.get("status"), "passed", "public_metadata.status")
    require_equal(metadata.get("git_commit_sha"), source_commit, "public_metadata.source")
    require_equal(metadata.get("doi"), new_doi, "public_metadata.doi")
    require_equal(metadata.get("package_identity_sha256"), package, "public_metadata.package")

    previous_verified = state.get("previous_verified_version")
    final = dict(state)
    final.update(published)
    final.update(
        {
            "schema": "trinityaccord.repository-preservation-zenodo-state.v2",
            "publication_status": "published_and_publicly_restored",
            "source_baseline_commit_sha": source_commit,
            "public_download_verification": "passed",
            "public_metadata_verification": "passed",
            "public_cold_restore": "passed",
            "public_cold_restore_report": recovery,
            "public_metadata_report": metadata,
            "previous_verified_version": previous_verified,
            "github_required_for_discovery": False,
            "github_required_for_repository_recovery": False,
            "live_main_equivalence_claimed": False,
            "coverage_scope": "exact Git-tracked current evidence checkpoint named by latest_git_commit_sha",
            "current_evidence_checkpoint": {
                "status": "published_verified_and_consumed",
                "sequence": 4,
                "version_doi": new_doi,
                "source_baseline_commit_sha": source_commit,
                "package_identity_sha256": package,
                "evidence_scope": EXPECTED_SCOPE,
                "intended_as_final_evidence_freeze": False,
                "future_material_versions_allowed": True,
                "arweave_snapshot_refreshed": False,
                "non_amending_boundary": True,
            },
            "homepage_snapshot_refresh": {
                "status": "not_requested_sequence_4",
                "boundary": "Existing transaction-addressed Arweave mirrors remain historical named-payload mirrors.",
            },
        }
    )
    auth.update(
        {
            "status": "consumed",
            "published_source_baseline_commit_sha": source_commit,
            "published_record_id": record_id,
            "published_doi": new_doi,
            "published_package_identity_sha256": package,
        }
    )
    prepared.update(
        {
            "status": "published_verified",
            "source_git_commit_sha": source_commit,
            "version_doi": new_doi,
            "zenodo_record_id": record_id,
            "zenodo_package_identity_sha256": package,
        }
    )
    observation = {
        "schema": "trinityaccord.current-baseline-publication-observation.v4",
        "sequence": 4,
        "status": "passed",
        "source_git_commit_sha": source_commit,
        "version_doi": new_doi,
        "concept_doi": CONCEPT_DOI,
        "zenodo_record_id": record_id,
        "zenodo_package_identity_sha256": package,
        "public_metadata_and_byte_verification": "passed",
        "public_cold_restore": "passed",
        "checkpoint_evidence_scope": EXPECTED_SCOPE,
        "intended_as_final_evidence_freeze": False,
        "future_material_versions_allowed": True,
        "arweave_snapshot_refreshed": False,
        "boundary": {
            "non_amending": True,
            "bitcoin_originals_prevail": True,
            "repository_doi_is_exact_baseline_not_live_main": True,
            "arweave_mirrors_remain_historical_named_payloads": True,
        },
    }
    trusted = index.setdefault("latest_trusted_release", {})
    latest = trusted.setdefault("repository_preservation", {})
    latest.update(
        {
            "doi": new_doi,
            "record_id": record_id,
            "concept_doi": CONCEPT_DOI,
            "git_commit_sha": source_commit,
            "git_tree_oid": published.get("latest_git_tree_oid"),
            "package_identity_sha256": package,
            "github_required_for_recovery": False,
            "github_required_for_discovery": False,
            "public_metadata_verification": "passed",
            "public_cold_restore": "passed",
            "coverage_status": "exact_current_evidence_checkpoint",
            "live_main_equivalence_claimed": False,
            "recovery_catalog": "preservation/recovery-catalog.json",
            "current_state": "preservation/repository-preservation-state-v2.json",
        }
    )
    trusted["repository_additions_after_published_baseline"] = {}
    limitations = index.get("limitations", [])
    if isinstance(limitations, list):
        for position, item in enumerate(limitations):
            if isinstance(item, str) and item.startswith("Current GitHub adds two offline-verified Ethereum"):
                limitations[position] = (
                    f"Checkpoint v4 ({new_doi}) incorporates the two Ethereum authority/signature anchors. "
                    "Any later GitHub additions must again be separated from this immutable baseline."
                )
    index["publication_refresh"] = {
        "schema": auth["schema"],
        "sequence": 4,
        "status": "published_verified_and_consumed",
        "source_git_commit_sha": source_commit,
        "version_doi": new_doi,
        "record_id": record_id,
        "core_concept_doi": CONCEPT_DOI,
        "previous_version_doi": PREVIOUS_DOI,
        "required_evidence_checkpoint_commit_sha": REQUIRED_CHECKPOINT,
        "arweave_snapshot_refreshed": False,
        "intended_as_final_evidence_freeze": False,
        "future_material_versions_allowed": True,
        "non_amending_boundary": True,
    }
    index.pop("pending_evidence_checkpoint", None)
    update_digest(index)

    current = evidence["current_cryptographic_proof_state"]
    current["status"] = "offline_verifiable_and_immutable_checkpoint_v4"
    eth = current["ethereum_non_nft"]
    eth.update(
        {
            "published_current_checkpoint_v4_anchor_count": 12,
            "post_freeze_live_delta_anchor_count": 0,
            "post_freeze_live_delta_tx_hashes": [],
            "next_checkpoint_v4_anchor_count": 12,
            "next_checkpoint_v4_status": "published_verified_and_consumed",
            "doi_boundary": (
                f"The immutable checkpoint DOI {new_doi} contains all 12 current non-NFT Ethereum anchors, "
                "including the authority-manifest digest and EIP-712 signature records."
            ),
        }
    )
    preservation = current["repository_preservation"]
    preservation.update(
        {
            "latest_published_version_doi": new_doi,
            "status": "checkpoint_published_and_publicly_restored",
            "latest_observation": "preservation/current-baseline-publication-observation-v4.json",
            "cold_restore": "PASS",
            "published_baseline_boundary": (
                "This DOI is the exact owner-authorized 8 Bitcoin + 12 Ethereum + 175 NFT current evidence "
                "checkpoint. It is immutable, is not moving GitHub main, and is not declared permanently final."
            ),
            "live_repository_delta": {
                "status": "incorporated_into_published_checkpoint_v4",
                "ethereum_non_nft_additions": 0,
                "new_doi_publication": "published_verified_and_consumed",
                "new_arweave_upload": "intentionally_deferred_not_attempted",
                "recovery_boundary": "The named v4 DOI restores the complete 8 + 12 + 175 checkpoint without GitHub.",
            },
            "current_checkpoint_status": "published_verified_and_consumed",
            "current_checkpoint_version_doi": new_doi,
            "current_checkpoint_source_baseline_commit_sha": source_commit,
            "current_checkpoint_package_identity_sha256": package,
            "current_checkpoint_intended_as_permanent_final": False,
            "current_checkpoint_future_material_versions_allowed": True,
        }
    )
    update_digest(evidence)

    address_scope["freeze_boundary"].update(
        {
            "new_doi_publication_status": "published_verified_and_consumed",
            "new_arweave_upload_status": "intentionally_deferred_not_attempted",
            "current_checkpoint_v4_includes_post_freeze_additions": True,
            "current_checkpoint_v4_version_doi": new_doi,
            "current_checkpoint_v4_source_baseline_commit_sha": source_commit,
        }
    )
    update_digest(address_scope)

    external["current_core_repository_latest_version_doi"] = new_doi
    external["core_repository_reference_note"] = (
        "10.5281/zenodo.21739344 is a historical version reference, not the current Concept DOI. "
        f"The Concept DOI is {CONCEPT_DOI}; the current verified checkpoint version is {new_doi}."
    )
    core = catalog["core_repository"]
    core.update(
        {
            "previous_verified_version_doi": PREVIOUS_DOI,
            "current_verified_version_doi": new_doi,
            "current_verified_source_git_commit_sha": source_commit,
        }
    )
    core["current_evidence_checkpoint"].update(
        {
            "status": "published_verified_and_consumed",
            "version_doi": new_doi,
            "source_baseline_commit_sha": source_commit,
            "package_identity_sha256": package,
        }
    )

    plan["current_checkpoint"] = {
        "checkpoint_kind": "immutable_published_checkpoint_not_live_main",
        "scope_label": "2026 current evidence checkpoint v4",
        "core_concept_doi": CONCEPT_DOI,
        "core_version_doi": new_doi,
        "frozen_source_baseline_commit_sha": source_commit,
        "package_identity_sha256": package,
        "public_metadata_and_byte_verification": "passed",
        "public_doi_only_cold_restore": "passed",
        "evidence_scope": EXPECTED_SCOPE,
        "intended_as_permanent_final": False,
        "future_material_versions_allowed": True,
    }
    plan.pop("pending_checkpoint_v4", None)
    live = plan["live_repository_checkpoint"]
    live.update(
        {
            "checkpoint_kind": "incorporated_into_immutable_checkpoint_v4",
            "published_checkpoint_v4_includes_this_delta": True,
            "new_doi_publication_status": "published_verified_and_consumed",
            "new_arweave_upload_status": "intentionally_deferred_not_attempted",
            "recovery_boundary": f"Version DOI {new_doi} restores the complete 12-anchor state without GitHub.",
        }
    )
    plan["versioning_semantics"].update(
        {
            "current_checkpoint_is_permanent_final": False,
            "future_material_improvements_use_a_new_version": True,
            "concept_doi_may_resolve_a_later_verified_version": True,
        }
    )
    plan["maintenance_checkpoint_2026_08_09"]["external_write_record"].update(
        {
            "new_zenodo_version_published": True,
            "zenodo_checkpoint_sequence": 4,
            "zenodo_version_doi": new_doi,
            "arweave_upload_performed": False,
            "owner_zenodo_authorization_consumed": True,
        }
    )
    plan["maintenance_checkpoint_2026_08_09"]["continuation_note"] = (
        f"Checkpoint v4 at {new_doi} freezes 8 + 12 + 175. Future material improvements require a new "
        "owner-authorized version; no new Arweave upload was performed."
    )
    plan["authorization_boundary"]["latest_zenodo_authorization"] = (
        "sequence_4_checkpoint_published_verified_and_consumed"
    )
    plan["future_agent_start_sequence"][0] = (
        "Read api/final-evidence-inventory.v1.json as the immutable DOI v4 checkpoint inventory, "
        "then read api/evidence-manifest.json for any explicitly separated later GitHub delta."
    )
    plan["future_agent_start_sequence"][5] = (
        f"Compare current GitHub main against checkpoint v4 source baseline {source_commit} and produce an explicit delta report."
    )
    update_digest(plan)

    inventory_node = node(graph, "final_evidence_inventory")
    inventory_node["freeze_role"] = f"immutable checkpoint v4 snapshot at source commit {source_commit}"
    inventory_node["role"] = f"Preserves the 8 + 12 + 175 inventory frozen in version DOI {new_doi}."
    live_node = node(graph, "current_live_evidence_state")
    live_node["published_checkpoint_v4_scope"] = inventory_node["scope"]
    live_node["role"] = "Exposes the same verified 8 + 12 + 175 evidence scope frozen by checkpoint v4, plus any later explicitly separated Git delta."
    core_node = node(graph, "core_repository_zenodo_series")
    core_node.pop("pending_checkpoint_v4", None)
    core_node.update(
        {
            "latest_version_doi": new_doi,
            "current_checkpoint_authorization": "preservation/current-baseline-publication-authorization-v4.json",
            "current_checkpoint_scope": inventory_node["scope"],
            "current_checkpoint_source_baseline_commit_sha": source_commit,
            "current_checkpoint_public_cold_restore": "passed",
            "current_live_two_anchor_ethereum_delta_included": True,
        }
    )

    write(STATE, final)
    write(AUTH, auth)
    write(PREPARED, prepared)
    write(OBSERVATION, observation)
    write(INDEX, index)
    write(EVIDENCE_MANIFEST, evidence)
    write(ADDRESS_SCOPE, address_scope)
    write(EXTERNAL_STATE, external)
    write(RECOVERY_CATALOG, catalog)
    write(EVOLUTION_PLAN, plan)
    write(RELATIONSHIP_MAP, graph)
    refresh_inventory()
    if published_state_path.is_file() and published_state_path.parent == ROOT / "preservation":
        published_state_path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("initialize")
    sub.add_parser("validate")
    prepare_parser = sub.add_parser("prepare")
    prepare_parser.add_argument("--base-commit", required=True)
    seal_parser = sub.add_parser("seal")
    seal_parser.add_argument("--source-commit", required=True)
    seal_parser.add_argument("--published-state", required=True)
    seal_parser.add_argument("--recovery-report", required=True)
    seal_parser.add_argument("--metadata-report", required=True)
    args = parser.parse_args()
    if args.command == "initialize":
        initialize_pending()
        validate()
    elif args.command == "validate":
        validate()
    elif args.command == "prepare":
        prepare(args.base_commit)
        validate()
    elif args.command == "seal":
        seal(
            args.source_commit,
            (ROOT / args.published_state).resolve(),
            Path(args.recovery_report).resolve(),
            Path(args.metadata_report).resolve(),
        )
        validate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
