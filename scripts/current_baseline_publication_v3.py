#!/usr/bin/env python3
"""Sequence-3 one-shot final evidence-baseline publication state machine.

This lifecycle advances the existing core repository Concept DOI by exactly one
owner-authorized version.  It freezes the complete Bitcoin, Ethereum and NFT
proof topology, performs no Arweave write, and remains non-amending.
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
AUTH = ROOT / "preservation/current-baseline-publication-authorization-v3.json"
PREPARED = ROOT / "preservation/current-baseline-publication-prepared-v3.json"
OBSERVATION = ROOT / "preservation/current-baseline-publication-observation-v3.json"
STATE = ROOT / "preservation/repository-preservation-state-v2.json"
INDEX = ROOT / "api/recovery-index.json"
EVIDENCE_MANIFEST = ROOT / "api/evidence-manifest.json"
EXTERNAL_STATE = ROOT / "preservation/external-binary-annex-state.json"
RECOVERY_CATALOG = ROOT / "preservation/recovery-catalog.json"
SEQ2_AUTH = ROOT / "preservation/current-baseline-publication-authorization-v2.json"

CONCEPT_DOI = "10.5281/zenodo.21739343"
PREVIOUS_DOI = "10.5281/zenodo.21846249"
PREVIOUS_RECORD_ID = 21846249
PREVIOUS_SOURCE = "22f0abf2e93124845f750e6b2c1569e9d1d26b03"
PREVIOUS_PACKAGE = "afdc93dd20f64ab6bd36b98410ef0d72a10b2f5cf5d722634d5c3ada4d924823"
REQUIRED_FREEZE = "5fdc53605d1a3e3782a9257b12cf2fc9b5fa2162"
RIGHTS_ACK = "TRINITY_PRESERVATION_CAPSULE_RIGHTS_V1_APPROVED"
CONFIRMATION = "PUBLISH_TRINITY_FINAL_EVIDENCE_BASELINE_V3"
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DOI_RE = re.compile(r"^10\.5281/zenodo\.([0-9]+)$")

EXPECTED_SCOPE = {
    "bitcoin_inscriptions": 8,
    "bitcoin_canonical_originals": 3,
    "bitcoin_non_amending_ancillary": 5,
    "ethereum_non_nft_anchors": 10,
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


def inventory_module():
    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import build_final_evidence_inventory  # type: ignore

    return build_final_evidence_inventory


def refresh_inventory() -> None:
    module = inventory_module()
    module.write_outputs(module.build())


def validate_generated(auth: dict[str, Any], index: dict[str, Any]) -> None:
    require_equal(index.get("source_digest"), canonical_digest(index), "recovery.source_digest")
    evidence = load(EVIDENCE_MANIFEST)
    require_equal(
        evidence.get("source_digest"),
        canonical_digest(evidence),
        "evidence_manifest.source_digest",
    )
    module = inventory_module()
    expected = module.build()
    module.check_outputs(expected)
    require_equal(expected["final_freeze"]["status"], auth.get("status"), "inventory.final_freeze.status")
    require_equal(
        expected["evidence_sets"]["bitcoin_inscriptions"]["count"],
        8,
        "inventory.bitcoin.count",
    )
    require_equal(expected["evidence_sets"]["ethereum_non_nft"]["count"], 10, "inventory.ethereum.count")
    require_equal(
        expected["evidence_sets"]["ethereum_chronicle_nft"]["asset_count"],
        175,
        "inventory.nft.count",
    )


def validate_static_auth(auth: dict[str, Any]) -> None:
    expected = {
        "schema": "trinityaccord.current-baseline-publication-authorization.v3",
        "sequence": 3,
        "authorized_by": "thechurchofagi",
        "core_concept_doi": CONCEPT_DOI,
        "previous_core_version_doi": PREVIOUS_DOI,
        "zenodo_rights_acknowledgement": RIGHTS_ACK,
        "publication_confirmation": CONFIRMATION,
        "include_full_repository_doi": True,
        "include_homepage_arweave_snapshot": False,
        "intended_as_final_evidence_freeze": True,
        "non_amending_boundary": True,
        "live_main_equivalence_claimed": False,
        "required_evidence_freeze_commit_sha": REQUIRED_FREEZE,
        "frozen_evidence_scope": EXPECTED_SCOPE,
    }
    for key, expected_value in expected.items():
        require_equal(auth.get(key), expected_value, f"authorization.{key}")
    previous = auth.get("previous_publication")
    require(isinstance(previous, dict), "authorization.previous_publication missing")
    for key, expected_value in {
        "sequence": 2,
        "source_baseline_commit_sha": PREVIOUS_SOURCE,
        "doi": PREVIOUS_DOI,
        "package_identity_sha256": PREVIOUS_PACKAGE,
    }.items():
        require_equal(previous.get(key), expected_value, f"authorization.previous_publication.{key}")


def validate_sequence2_history() -> None:
    seq2 = load(SEQ2_AUTH)
    require_equal(seq2.get("status"), "consumed", "sequence2.status")
    require_equal(seq2.get("published_source_baseline_commit_sha"), PREVIOUS_SOURCE, "sequence2.source")
    require_equal(seq2.get("published_doi"), PREVIOUS_DOI, "sequence2.doi")
    require_equal(seq2.get("published_record_id"), PREVIOUS_RECORD_ID, "sequence2.record_id")
    require_equal(seq2.get("published_package_identity_sha256"), PREVIOUS_PACKAGE, "sequence2.package")


def validate_relationship_topology() -> None:
    graph = load(ROOT / "api/evidence-relationship-map.v1.json")
    node_ids = {item.get("id") for item in graph.get("nodes", []) if isinstance(item, dict)}
    required_nodes = {
        "final_evidence_inventory",
        "evidence_evolution_handoff",
        "bitcoin_inscription_proof_annex",
        "ethereum_non_nft_proof_annex",
        "chronicle_nft_proof_annex",
        "github_repository_and_pages",
        "arweave_mirrors",
        "core_repository_zenodo_series",
        "external_evidence_zenodo_annex",
        "nft_media_zenodo_annex",
    }
    require(required_nodes <= node_ids, f"relationship map missing nodes: {sorted(required_nodes - node_ids)}")
    entrypoints = load(EVIDENCE_MANIFEST).get("evidence_system_entrypoints")
    require(isinstance(entrypoints, dict), "evidence manifest lacks evidence-system entrypoints")
    require_equal(entrypoints.get("final_inventory"), "/api/final-evidence-inventory.v1.json", "entrypoints.inventory")
    require_equal(entrypoints.get("recovery_index"), "/api/recovery-index.json", "entrypoints.recovery")
    require_equal(
        entrypoints.get("machine_evolution_plan"),
        "/api/evidence-evolution-plan.v1.json",
        "entrypoints.evolution",
    )


def validate_pending(auth: dict[str, Any], state: dict[str, Any], index: dict[str, Any]) -> None:
    require_equal(auth.get("status"), "pending", "authorization.status")
    require_equal(state.get("publication_status"), "published_and_publicly_restored", "state.publication_status")
    require_equal(state.get("latest_doi"), PREVIOUS_DOI, "state.latest_doi")
    require_equal(state.get("latest_record_id"), PREVIOUS_RECORD_ID, "state.latest_record_id")
    require_equal(state.get("latest_git_commit_sha"), PREVIOUS_SOURCE, "state.latest_git_commit_sha")
    require_equal(state.get("latest_package_identity_sha256"), PREVIOUS_PACKAGE, "state.latest_package")
    require_equal(state.get("concept_doi"), CONCEPT_DOI, "state.concept_doi")
    refresh = index.get("publication_refresh")
    require(isinstance(refresh, dict), "recovery publication_refresh missing")
    require_equal(refresh.get("sequence"), 2, "recovery.publication_refresh.sequence")
    pending = index.get("pending_final_freeze")
    require(isinstance(pending, dict), "recovery pending_final_freeze missing")
    require_equal(pending.get("sequence"), 3, "recovery.pending_final_freeze.sequence")
    require_equal(pending.get("status"), "owner_authorized_pending_publication", "recovery.pending_final_freeze.status")
    preservation = load(EVIDENCE_MANIFEST)["current_cryptographic_proof_state"]["repository_preservation"]
    require_equal(preservation.get("latest_published_version_doi"), PREVIOUS_DOI, "manifest.latest_doi")
    require_equal(preservation.get("final_freeze_status"), "owner_authorized_pending_publication", "manifest.final_freeze_status")


def validate_prepared(auth: dict[str, Any], state: dict[str, Any], index: dict[str, Any]) -> dict[str, Any]:
    require_equal(auth.get("status"), "prepared", "authorization.status")
    prepared = load(PREPARED)
    require_equal(prepared.get("schema"), "trinityaccord.current-baseline-publication-prepared.v3", "prepared.schema")
    require_equal(prepared.get("sequence"), 3, "prepared.sequence")
    require_equal(prepared.get("status"), "prepared", "prepared.status")
    require_equal(prepared.get("base_commit_sha"), auth.get("prepared_base_commit_sha"), "prepared.base_commit")
    require_equal(prepared.get("previous_version_doi"), PREVIOUS_DOI, "prepared.previous_doi")
    require_equal(prepared.get("required_evidence_freeze_commit_sha"), REQUIRED_FREEZE, "prepared.required_freeze")
    require_equal(
        state.get("publication_status"),
        "prepared_for_final_evidence_baseline_publication_v3",
        "state.publication_status",
    )
    require_equal(state.get("latest_doi"), PREVIOUS_DOI, "state.latest_doi_during_prepare")
    refresh = index.get("publication_refresh")
    require(isinstance(refresh, dict), "prepared recovery publication_refresh missing")
    require_equal(refresh.get("sequence"), 3, "prepared recovery sequence")
    require_equal(refresh.get("status"), "prepared_for_final_evidence_baseline_publication", "prepared recovery status")
    pending = index.get("pending_final_freeze")
    require(isinstance(pending, dict), "prepared recovery pending_final_freeze missing")
    require_equal(pending.get("status"), "prepared", "prepared pending_final_freeze.status")
    preservation = load(EVIDENCE_MANIFEST)["current_cryptographic_proof_state"]["repository_preservation"]
    require_equal(preservation.get("final_freeze_status"), "prepared", "manifest.final_freeze_status")
    return prepared


def validate_consumed(auth: dict[str, Any], state: dict[str, Any], index: dict[str, Any]) -> None:
    require_equal(auth.get("status"), "consumed", "authorization.status")
    source = auth.get("published_source_baseline_commit_sha")
    doi = auth.get("published_doi")
    record_id = auth.get("published_record_id")
    package = auth.get("published_package_identity_sha256")
    require(isinstance(source, str) and COMMIT_RE.fullmatch(source) is not None, "invalid final source commit")
    match = DOI_RE.fullmatch(str(doi))
    require(match is not None and doi != PREVIOUS_DOI, "invalid or non-new final DOI")
    require(isinstance(record_id, int) and int(match.group(1)) == record_id, "final DOI/record mismatch")
    require(isinstance(package, str) and SHA256_RE.fullmatch(package) is not None, "invalid final package identity")
    require_equal(state.get("publication_status"), "published_and_publicly_restored", "state.publication_status")
    require_equal(state.get("latest_git_commit_sha"), source, "state.latest_source")
    require_equal(state.get("latest_doi"), doi, "state.latest_doi")
    require_equal(state.get("latest_record_id"), record_id, "state.latest_record_id")
    require_equal(state.get("latest_package_identity_sha256"), package, "state.latest_package")
    require_equal(state.get("concept_doi"), CONCEPT_DOI, "state.concept_doi")
    require_equal(state.get("public_metadata_verification"), "passed", "state.public_metadata")
    require_equal(state.get("public_cold_restore"), "passed", "state.public_restore")
    require_equal(state.get("live_main_equivalence_claimed"), False, "state.live_main_equivalence")
    freeze = state.get("final_evidence_freeze")
    require(isinstance(freeze, dict), "state final_evidence_freeze missing")
    require_equal(freeze.get("status"), "published_verified_and_consumed", "state.final_freeze.status")
    require_equal(freeze.get("evidence_scope"), EXPECTED_SCOPE, "state.final_freeze.scope")
    versions = state.get("versions")
    require(isinstance(versions, list), "state.versions missing")
    by_doi = {item.get("doi"): item for item in versions if isinstance(item, dict)}
    require(PREVIOUS_DOI in by_doi and doi in by_doi, "state versions lack predecessor or final DOI")
    prepared = load(PREPARED)
    require_equal(prepared.get("status"), "published_verified", "prepared.status")
    require_equal(prepared.get("source_git_commit_sha"), source, "prepared.source")
    require_equal(prepared.get("version_doi"), doi, "prepared.doi")
    observation = load(OBSERVATION)
    require_equal(observation.get("status"), "passed", "observation.status")
    require_equal(observation.get("source_git_commit_sha"), source, "observation.source")
    require_equal(observation.get("version_doi"), doi, "observation.doi")
    require_equal(observation.get("zenodo_record_id"), record_id, "observation.record_id")
    require_equal(
        observation.get("zenodo_package_identity_sha256"),
        package,
        "observation.package_identity",
    )
    require_equal(observation.get("public_cold_restore"), "passed", "observation.restore")
    require_equal(observation.get("arweave_snapshot_refreshed"), False, "observation.arweave")
    refresh = index.get("publication_refresh")
    require(isinstance(refresh, dict), "final recovery publication_refresh missing")
    require_equal(refresh.get("sequence"), 3, "final recovery sequence")
    require_equal(refresh.get("status"), "published_verified_and_consumed", "final recovery status")
    require_equal(refresh.get("source_git_commit_sha"), source, "final recovery source")
    require_equal(refresh.get("version_doi"), doi, "final recovery doi")
    require("pending_final_freeze" not in index, "consumed recovery index retains pending_final_freeze")
    additions = index.get("latest_trusted_release", {}).get("repository_additions_after_published_baseline")
    require_equal(additions, {}, "final repository additions")
    latest = index.get("latest_trusted_release", {}).get("repository_preservation", {})
    require_equal(latest.get("doi"), doi, "recovery.latest.doi")
    require_equal(latest.get("git_commit_sha"), source, "recovery.latest.source")
    require_equal(latest.get("package_identity_sha256"), package, "recovery.latest.package")
    preservation = load(EVIDENCE_MANIFEST)["current_cryptographic_proof_state"]["repository_preservation"]
    require_equal(preservation.get("latest_published_version_doi"), doi, "manifest.latest_doi")
    require_equal(preservation.get("final_freeze_status"), "published_verified_and_consumed", "manifest.final_status")
    require_equal(preservation.get("final_freeze_source_baseline_commit_sha"), source, "manifest.final_source")
    external = load(EXTERNAL_STATE)
    require_equal(external.get("current_core_repository_latest_version_doi"), doi, "external.current_core_doi")
    catalog = load(RECOVERY_CATALOG).get("core_repository", {})
    require_equal(catalog.get("current_verified_version_doi"), doi, "catalog.current_doi")
    require_equal(catalog.get("current_verified_source_git_commit_sha"), source, "catalog.current_source")


def validate() -> None:
    auth = load(AUTH)
    state = load(STATE)
    index = load(INDEX)
    validate_static_auth(auth)
    validate_sequence2_history()
    validate_relationship_topology()
    status = auth.get("status")
    if status == "pending":
        validate_pending(auth, state, index)
    elif status == "prepared":
        validate_prepared(auth, state, index)
    elif status == "consumed":
        validate_consumed(auth, state, index)
    else:
        raise SystemExit(f"invalid sequence-3 authorization status: {status!r}")
    validate_generated(auth, index)
    print(f"Final evidence baseline publication v3 state valid: {status}")


def prepare(base_commit: str) -> None:
    auth = load(AUTH)
    state = load(STATE)
    index = load(INDEX)
    evidence = load(EVIDENCE_MANIFEST)
    catalog = load(RECOVERY_CATALOG)
    validate_static_auth(auth)
    validate_sequence2_history()
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
            "publication_status": "prepared_for_final_evidence_baseline_publication_v3",
            "prepared_base_commit_sha": base_commit,
            "previous_verified_version": previous,
            "planned_homepage_arweave_snapshot": False,
            "live_main_equivalence_claimed": False,
        }
    )
    index["publication_refresh"] = {
        "schema": auth["schema"],
        "sequence": 3,
        "status": "prepared_for_final_evidence_baseline_publication",
        "authorized_base_commit_sha": base_commit,
        "required_evidence_freeze_commit_sha": REQUIRED_FREEZE,
        "previous_version_doi": PREVIOUS_DOI,
        "core_concept_doi": CONCEPT_DOI,
        "arweave_snapshot_refreshed": False,
        "intended_as_final_evidence_freeze": True,
        "non_amending_boundary": True,
    }
    index["pending_final_freeze"].update(
        {"status": "prepared", "authorized_base_commit_sha": base_commit}
    )
    update_digest(index)
    preservation = evidence["current_cryptographic_proof_state"]["repository_preservation"]
    preservation.update(
        {
            "final_freeze_status": "prepared",
            "final_freeze_authorized_base_commit_sha": base_commit,
            "published_baseline_boundary": (
                "The latest public DOI remains the exact sequence-2 baseline while the "
                "owner-authorized final evidence baseline is prepared and not yet published."
            ),
        }
    )
    update_digest(evidence)
    catalog["core_repository"]["final_evidence_freeze"].update(
        {"status": "prepared", "authorized_base_commit_sha": base_commit}
    )
    prepared = {
        "schema": "trinityaccord.current-baseline-publication-prepared.v3",
        "sequence": 3,
        "status": "prepared",
        "base_commit_sha": base_commit,
        "required_evidence_freeze_commit_sha": REQUIRED_FREEZE,
        "previous_version_doi": PREVIOUS_DOI,
        "core_concept_doi": CONCEPT_DOI,
        "publication_scope": "full_git_tracked_final_evidence_baseline",
        "frozen_evidence_scope": EXPECTED_SCOPE,
        "arweave_snapshot_refreshed": False,
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
    write(RECOVERY_CATALOG, catalog)
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
    require(match is not None and new_doi != PREVIOUS_DOI, "publisher did not create/reconcile a new final DOI")
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
            "coverage_scope": "exact Git-tracked final evidence baseline named by latest_git_commit_sha",
            "final_evidence_freeze": {
                "status": "published_verified_and_consumed",
                "sequence": 3,
                "version_doi": new_doi,
                "source_baseline_commit_sha": source_commit,
                "package_identity_sha256": package,
                "evidence_scope": EXPECTED_SCOPE,
                "intended_as_final_evidence_freeze": True,
                "arweave_snapshot_refreshed": False,
                "non_amending_boundary": True,
            },
            "homepage_snapshot_refresh": {
                "status": "not_requested_sequence_3",
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
        "schema": "trinityaccord.current-baseline-publication-observation.v3",
        "sequence": 3,
        "status": "passed",
        "source_git_commit_sha": source_commit,
        "version_doi": new_doi,
        "concept_doi": CONCEPT_DOI,
        "zenodo_record_id": record_id,
        "zenodo_package_identity_sha256": package,
        "public_metadata_and_byte_verification": "passed",
        "public_cold_restore": "passed",
        "frozen_evidence_scope": EXPECTED_SCOPE,
        "intended_as_final_evidence_freeze": True,
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
            "coverage_status": "exact_final_evidence_baseline",
            "live_main_equivalence_claimed": False,
            "recovery_catalog": "preservation/recovery-catalog.json",
            "current_state": "preservation/repository-preservation-state-v2.json",
        }
    )
    trusted["repository_additions_after_published_baseline"] = {}
    index["publication_refresh"] = {
        "schema": auth["schema"],
        "sequence": 3,
        "status": "published_verified_and_consumed",
        "source_git_commit_sha": source_commit,
        "version_doi": new_doi,
        "record_id": record_id,
        "core_concept_doi": CONCEPT_DOI,
        "previous_version_doi": PREVIOUS_DOI,
        "required_evidence_freeze_commit_sha": REQUIRED_FREEZE,
        "arweave_snapshot_refreshed": False,
        "intended_as_final_evidence_freeze": True,
        "non_amending_boundary": True,
    }
    index.pop("pending_final_freeze", None)
    update_digest(index)
    preservation = evidence["current_cryptographic_proof_state"]["repository_preservation"]
    preservation.update(
        {
            "latest_published_version_doi": new_doi,
            "status": "final_frozen_and_publicly_restored",
            "latest_observation": "preservation/current-baseline-publication-observation-v3.json",
            "cold_restore": "PASS",
            "published_baseline_boundary": (
                "This DOI is the exact owner-authorized final evidence baseline containing the "
                "Bitcoin, Ethereum and NFT proof annexes plus the unified inventory; it is not a moving GitHub main."
            ),
            "final_freeze_status": "published_verified_and_consumed",
            "final_freeze_version_doi": new_doi,
            "final_freeze_source_baseline_commit_sha": source_commit,
            "final_freeze_package_identity_sha256": package,
        }
    )
    preservation.pop("bitcoin_annex_next_capsule_status", None)
    update_digest(evidence)
    external["current_core_repository_latest_version_doi"] = new_doi
    external["core_repository_reference_note"] = (
        "10.5281/zenodo.21739344 is a historical version reference, not the current Concept DOI. "
        f"The Concept DOI is {CONCEPT_DOI}; the final verified repository version is {new_doi}."
    )
    core = catalog["core_repository"]
    core.update(
        {
            "previous_verified_version_doi": PREVIOUS_DOI,
            "current_verified_version_doi": new_doi,
            "current_verified_source_git_commit_sha": source_commit,
        }
    )
    core["final_evidence_freeze"].update(
        {
            "status": "published_verified_and_consumed",
            "version_doi": new_doi,
            "source_baseline_commit_sha": source_commit,
            "package_identity_sha256": package,
        }
    )
    write(STATE, final)
    write(AUTH, auth)
    write(PREPARED, prepared)
    write(OBSERVATION, observation)
    write(INDEX, index)
    write(EVIDENCE_MANIFEST, evidence)
    write(EXTERNAL_STATE, external)
    write(RECOVERY_CATALOG, catalog)
    refresh_inventory()
    if published_state_path.is_file() and published_state_path.parent == ROOT / "preservation":
        published_state_path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    prepare_parser = sub.add_parser("prepare")
    prepare_parser.add_argument("--base-commit", required=True)
    seal_parser = sub.add_parser("seal")
    seal_parser.add_argument("--source-commit", required=True)
    seal_parser.add_argument("--published-state", required=True)
    seal_parser.add_argument("--recovery-report", required=True)
    seal_parser.add_argument("--metadata-report", required=True)
    args = parser.parse_args()
    if args.command == "validate":
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
