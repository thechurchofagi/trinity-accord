#!/usr/bin/env python3
"""Seal an already-published current-baseline DOI and Arweave snapshot.

This script performs no network or external write. Its inputs must have been
independently verified by the reconciliation workflow before invocation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUTH_PATH = ROOT / "preservation/current-baseline-publication-authorization-v1.json"
PREPARED_PATH = ROOT / "preservation/current-baseline-publication-prepared-v1.json"
STATE_PATH = ROOT / "preservation/repository-preservation-state-v2.json"
INDEX_PATH = ROOT / "api/recovery-index.json"
OBSERVATION_PATH = ROOT / "preservation/current-baseline-publication-observation-v1.json"
RECONCILIATION_PATH = ROOT / "preservation/current-baseline-publication-reconciliation-v1.json"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def canonical_index_digest(index: dict[str, Any]) -> str:
    canonical = dict(index)
    canonical.pop("source_digest", None)
    raw = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-state", required=True)
    parser.add_argument("--public-recovery-report", required=True)
    parser.add_argument("--public-metadata-report", required=True)
    parser.add_argument("--arweave-receipt", required=True)
    args = parser.parse_args()

    published = read_json(Path(args.work_state))
    recovery = read_json(Path(args.public_recovery_report))
    metadata = read_json(Path(args.public_metadata_report))
    arweave = read_json(Path(args.arweave_receipt))
    reconciliation = read_json(RECONCILIATION_PATH)
    auth = read_json(AUTH_PATH)
    prepared = read_json(PREPARED_PATH)
    old_state = read_json(STATE_PATH)
    index = read_json(INDEX_PATH)

    require(reconciliation.get("status") == "pending", "reconciliation is not pending")
    require(reconciliation.get("external_writes_already_complete") is True, "reconciliation must identify completed external writes")
    require(reconciliation.get("allow_zenodo_write") is False, "reconciliation must forbid Zenodo writes")
    require(reconciliation.get("allow_arweave_post") is False, "reconciliation must forbid Arweave posts")
    source = reconciliation.get("source_git_commit_sha")
    doi = reconciliation.get("version_doi")
    concept = reconciliation.get("concept_doi")
    package = reconciliation.get("package_identity_sha256")
    txid = reconciliation.get("arweave_txid")
    payload_sha = reconciliation.get("arweave_payload_sha256")
    record_id = reconciliation.get("zenodo_record_id")

    require(auth.get("status") == "prepared", "owner authorization is not prepared")
    require(auth.get("previous_core_version_doi") == old_state.get("latest_doi"), "previous verified DOI changed before reconciliation")
    require(published.get("publication_status") == "published", "published work state is not published")
    require(published.get("latest_git_commit_sha") == source, "published source mismatch")
    require(published.get("latest_doi") == doi, "published DOI mismatch")
    require(published.get("latest_record_id") == record_id, "published record id mismatch")
    require((published.get("concept_doi") or published.get("core_concept_doi")) == concept, "published concept DOI mismatch")
    require(published.get("latest_package_identity_sha256") == package, "published package identity mismatch")

    require(recovery.get("result") == "pass", "public DOI recovery did not pass")
    require(recovery.get("source_git_commit_sha") == source, "public DOI recovery source mismatch")
    require(recovery.get("package_identity_sha256") == package, "public DOI recovery package mismatch")
    require(metadata.get("status") == "passed", "public metadata verification did not pass")
    require(metadata.get("record_id") == record_id, "public metadata record id mismatch")
    require(metadata.get("doi") == doi, "public metadata DOI mismatch")
    require(metadata.get("concept_doi") == concept, "public metadata concept DOI mismatch")
    require(metadata.get("git_commit_sha") == source, "public metadata source mismatch")
    require(metadata.get("package_identity_sha256") == package, "public metadata package mismatch")
    require(metadata.get("observed_without_zenodo_credentials") is True, "public metadata verification used credentials")

    require(arweave.get("result") == "uploaded" and arweave.get("hash_match") is True, "Arweave readback did not pass")
    require((arweave.get("txid") or arweave.get("tx_id")) == txid, "Arweave transaction mismatch")
    require(arweave.get("source_git_commit_sha") == source, "Arweave source mismatch")
    require(arweave.get("repository_version_doi") == doi, "Arweave DOI binding mismatch")
    require(arweave.get("payload_sha256") == payload_sha, "Arweave payload mismatch")
    require(arweave.get("readback_sha256") == payload_sha, "Arweave readback mismatch")

    published["public_download_verification"] = "passed"
    published["public_metadata_verification"] = "passed"
    published["public_cold_restore"] = "passed"
    published["public_cold_restore_report"] = recovery
    published["public_metadata_report"] = metadata

    previous = {
        "doi": old_state.get("latest_doi"),
        "record_id": old_state.get("latest_record_id"),
        "git_commit_sha": old_state.get("latest_git_commit_sha"),
        "package_identity_sha256": old_state.get("latest_package_identity_sha256"),
    }
    final_state = dict(old_state)
    final_state.update(published)
    final_state.update({
        "schema": "trinityaccord.repository-preservation-zenodo-state.v2",
        "publication_status": "published_and_publicly_restored",
        "source_baseline_commit_sha": source,
        "public_download_verification": "passed",
        "public_metadata_verification": "passed",
        "public_cold_restore": "passed",
        "public_cold_restore_report": recovery,
        "public_metadata_report": metadata,
        "homepage_machine_snapshot_arweave": arweave,
        "previous_verified_version": previous,
        "github_required_for_discovery": False,
        "github_required_for_repository_recovery": False,
        "live_main_equivalence_claimed": False,
        "coverage_scope": "exact Git-tracked publication baseline named by latest_git_commit_sha",
    })
    final_state.pop("prepared_base_commit_sha", None)
    final_state.pop("planned_homepage_arweave_snapshot", None)

    auth.update({
        "status": "consumed",
        "published_source_baseline_commit_sha": source,
        "published_record_id": record_id,
        "published_doi": doi,
        "published_package_identity_sha256": package,
        "homepage_snapshot_arweave_txid": txid,
        "homepage_snapshot_sha256": payload_sha,
    })
    prepared.update({
        "status": "published_verified",
        "source_git_commit_sha": source,
        "version_doi": doi,
        "arweave_txid": txid,
    })
    observation = {
        "schema": "trinityaccord.current-baseline-publication-observation.v1",
        "status": "passed",
        "source_git_commit_sha": source,
        "version_doi": doi,
        "concept_doi": concept,
        "zenodo_record_id": record_id,
        "zenodo_package_identity_sha256": package,
        "public_metadata_verification": "passed",
        "public_cold_restore": "passed",
        "arweave_txid": txid,
        "arweave_payload_sha256": payload_sha,
        "arweave_readback_sha256": payload_sha,
        "reconciled_from_failed_run_id": reconciliation.get("failed_workflow_run_id"),
        "boundary": {
            "non_amending": True,
            "bitcoin_originals_prevail": True,
            "repository_doi_is_exact_baseline_not_live_main": True,
            "homepage_arweave_snapshot_is_mirror_only": True,
            "reconciliation_performed_no_external_write": True,
        },
    }
    reconciliation.update({
        "status": "consumed",
        "public_metadata_verification": "passed",
        "public_cold_restore": "passed",
        "arweave_public_readback": "passed",
    })
    index["publication_refresh"] = {
        "schema": auth["schema"],
        "sequence": 1,
        "status": "published_verified_and_consumed",
        "source_git_commit_sha": source,
        "version_doi": doi,
        "core_concept_doi": concept,
        "arweave_txid": txid,
        "arweave_payload_sha256": payload_sha,
        "non_amending_boundary": True,
    }
    trusted = index.setdefault("latest_trusted_release", {})
    require(isinstance(trusted, dict), "latest trusted release is invalid")
    trusted["status"] = "published_and_publicly_restored"
    trusted["repository_preservation"] = {
        "doi": doi,
        "record_id": record_id,
        "concept_doi": concept,
        "git_commit_sha": source,
        "git_tree_oid": published.get("latest_git_tree_oid"),
        "package_identity_sha256": package,
        "github_required_for_recovery": False,
        "github_required_for_discovery": False,
        "public_metadata_verification": "passed",
        "public_cold_restore": "passed",
        "coverage_status": "exact_published_baseline",
        "live_main_equivalence_claimed": False,
        "recovery_catalog": "preservation/recovery-catalog.json",
        "current_state": "preservation/repository-preservation-state-v2.json",
    }
    index["source_digest"] = canonical_index_digest(index)

    write_json(STATE_PATH, final_state)
    write_json(AUTH_PATH, auth)
    write_json(PREPARED_PATH, prepared)
    write_json(OBSERVATION_PATH, observation)
    write_json(RECONCILIATION_PATH, reconciliation)
    write_json(INDEX_PATH, index)
    print(f"Sealed current baseline publication: doi={doi} arweave_txid={txid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
