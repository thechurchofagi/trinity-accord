#!/usr/bin/env python3
"""Sequence-2 one-shot repository baseline publication state machine.

This lifecycle publishes no new authority and performs no Arweave write. It
advances the existing repository-preservation Concept DOI by exactly one
proof-hardened Zenodo version, while preserving sequence-1 DOI/Arweave history.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "preservation/current-baseline-publication-authorization-v2.json"
PREPARED = ROOT / "preservation/current-baseline-publication-prepared-v2.json"
OBSERVATION = ROOT / "preservation/current-baseline-publication-observation-v2.json"
STATE = ROOT / "preservation/repository-preservation-state-v2.json"
INDEX = ROOT / "api/recovery-index.json"
SEQ1_AUTH = ROOT / "preservation/current-baseline-publication-authorization-v1.json"
SEQ3_AUTH = ROOT / "preservation/current-baseline-publication-authorization-v3.json"

CONCEPT_DOI = "10.5281/zenodo.21739343"
PREVIOUS_DOI = "10.5281/zenodo.21831412"
PREVIOUS_SOURCE = "3e013bbb44a741546db68013c4034c2121017f33"
PREVIOUS_PACKAGE = "1630e44bdec257c0c3278c79ab2eb4a6787cc7ac861e34e8dc470b63cf091b54"
PREVIOUS_ARWEAVE_TX = "-lAi9yvTzgfDTx32n8nzNRKAGOegO_croyzNHX3y7IM"
PREVIOUS_ARWEAVE_SHA = "361f0a1479e48fc5b194f19a65929a1dad53c1264a593e163eb24b3cacc8be63"
REQUIRED_HARDENING = "0cdba0d13b97f242908f150b634ae7a481be9ee3"
RIGHTS_ACK = "TRINITY_PRESERVATION_CAPSULE_RIGHTS_V1_APPROVED"
CONFIRMATION = "PUBLISH_TRINITY_CURRENT_BASELINE_V2"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path.relative_to(ROOT)}")
    return value


def write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_index_digest(index: dict[str, Any]) -> None:
    canonical = dict(index)
    canonical.pop("source_digest", None)
    raw = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    index["source_digest"] = hashlib.sha256(raw).hexdigest()[:16]


def require_equal(observed: Any, expected: Any, label: str) -> None:
    if observed != expected:
        raise SystemExit(f"{label} mismatch: observed={observed!r} expected={expected!r}")


def validate_static_auth(auth: dict[str, Any]) -> None:
    expected = {
        "schema": "trinityaccord.current-baseline-publication-authorization.v2",
        "sequence": 2,
        "authorized_by": "thechurchofagi",
        "core_concept_doi": CONCEPT_DOI,
        "previous_core_version_doi": PREVIOUS_DOI,
        "zenodo_rights_acknowledgement": RIGHTS_ACK,
        "publication_confirmation": CONFIRMATION,
        "include_full_repository_doi": True,
        "include_homepage_arweave_snapshot": False,
        "non_amending_boundary": True,
        "live_main_equivalence_claimed": False,
        "required_proof_hardening_commit_sha": REQUIRED_HARDENING,
    }
    for key, expected_value in expected.items():
        require_equal(auth.get(key), expected_value, f"authorization.{key}")
    previous = auth.get("previous_publication")
    if not isinstance(previous, dict):
        raise SystemExit("authorization.previous_publication missing")
    for key, expected_value in {
        "sequence": 1,
        "source_baseline_commit_sha": PREVIOUS_SOURCE,
        "doi": PREVIOUS_DOI,
        "package_identity_sha256": PREVIOUS_PACKAGE,
        "homepage_snapshot_arweave_txid": PREVIOUS_ARWEAVE_TX,
        "homepage_snapshot_sha256": PREVIOUS_ARWEAVE_SHA,
    }.items():
        require_equal(previous.get(key), expected_value, f"authorization.previous_publication.{key}")


def validate_sequence1_history() -> None:
    seq1 = load(SEQ1_AUTH)
    require_equal(seq1.get("status"), "consumed", "sequence1.status")
    require_equal(seq1.get("published_source_baseline_commit_sha"), PREVIOUS_SOURCE, "sequence1.source")
    require_equal(seq1.get("published_doi"), PREVIOUS_DOI, "sequence1.doi")
    require_equal(seq1.get("published_package_identity_sha256"), PREVIOUS_PACKAGE, "sequence1.package")
    require_equal(seq1.get("homepage_snapshot_arweave_txid"), PREVIOUS_ARWEAVE_TX, "sequence1.arweave_txid")
    require_equal(seq1.get("homepage_snapshot_sha256"), PREVIOUS_ARWEAVE_SHA, "sequence1.arweave_sha256")


def validate_pending(auth: dict[str, Any], state: dict[str, Any]) -> None:
    require_equal(auth.get("status"), "pending", "authorization.status")
    require_equal(state.get("latest_doi"), PREVIOUS_DOI, "state.latest_doi")
    require_equal(state.get("latest_git_commit_sha"), PREVIOUS_SOURCE, "state.latest_git_commit_sha")
    require_equal(state.get("latest_package_identity_sha256"), PREVIOUS_PACKAGE, "state.latest_package_identity_sha256")
    require_equal(state.get("concept_doi"), CONCEPT_DOI, "state.concept_doi")


def validate_prepared(auth: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    require_equal(auth.get("status"), "prepared", "authorization.status")
    prepared = load(PREPARED)
    require_equal(prepared.get("schema"), "trinityaccord.current-baseline-publication-prepared.v2", "prepared.schema")
    require_equal(prepared.get("sequence"), 2, "prepared.sequence")
    require_equal(prepared.get("status"), "prepared", "prepared.status")
    require_equal(prepared.get("base_commit_sha"), auth.get("prepared_base_commit_sha"), "prepared.base_commit_sha")
    require_equal(prepared.get("previous_version_doi"), PREVIOUS_DOI, "prepared.previous_version_doi")
    require_equal(prepared.get("required_proof_hardening_commit_sha"), REQUIRED_HARDENING, "prepared.required_hardening")
    require_equal(state.get("publication_status"), "prepared_for_current_baseline_publication_v2", "state.publication_status")
    require_equal(state.get("latest_doi"), PREVIOUS_DOI, "state.latest_doi_during_prepare")
    require_equal(state.get("latest_git_commit_sha"), PREVIOUS_SOURCE, "state.latest_source_during_prepare")
    return prepared


def validate_consumed(auth: dict[str, Any], state: dict[str, Any], index: dict[str, Any]) -> None:
    require_equal(auth.get("status"), "consumed", "authorization.status")
    source = auth.get("published_source_baseline_commit_sha")
    doi = auth.get("published_doi")
    record_id = auth.get("published_record_id")
    package = auth.get("published_package_identity_sha256")
    if not isinstance(source, str) or len(source) != 40:
        raise SystemExit("consumed authorization has invalid source commit")
    if not isinstance(doi, str) or not doi.startswith("10.5281/zenodo.") or doi == PREVIOUS_DOI:
        raise SystemExit("consumed authorization has invalid/new DOI")
    if not isinstance(record_id, int) or record_id <= 0:
        raise SystemExit("consumed authorization has invalid record id")
    if not isinstance(package, str) or len(package) != 64:
        raise SystemExit("consumed authorization has invalid package identity")

    # Sequence 2 remains immutable publication history after the explicitly
    # authorized sequence-3 final evidence freeze starts.  Validate its own
    # prepared/observation records and the successor lineage, but do not require
    # sequence 2 to keep owning the moving latest-state pointers.
    if SEQ3_AUTH.is_file():
        successor = load(SEQ3_AUTH)
        successor_status = successor.get("status")
        if successor_status in {"prepared", "consumed"}:
            require_equal(successor.get("sequence"), 3, "sequence3.sequence")
            require_equal(successor.get("core_concept_doi"), CONCEPT_DOI, "sequence3.concept_doi")
            require_equal(successor.get("previous_core_version_doi"), doi, "sequence3.previous_doi")
            previous = successor.get("previous_publication")
            if not isinstance(previous, dict):
                raise SystemExit("sequence3.previous_publication missing")
            require_equal(previous.get("source_baseline_commit_sha"), source, "sequence3.previous_source")
            require_equal(previous.get("doi"), doi, "sequence3.previous_publication.doi")
            require_equal(previous.get("package_identity_sha256"), package, "sequence3.previous_package")
            versions = state.get("versions")
            if not isinstance(versions, list) or doi not in {
                item.get("doi") for item in versions if isinstance(item, dict)
            }:
                raise SystemExit("preservation history no longer contains sequence-2 DOI")
            prepared_v2 = load(PREPARED)
            require_equal(prepared_v2.get("status"), "published_verified", "prepared.status")
            require_equal(prepared_v2.get("source_git_commit_sha"), source, "prepared.source")
            require_equal(prepared_v2.get("version_doi"), doi, "prepared.version_doi")
            observation_v2 = load(OBSERVATION)
            require_equal(observation_v2.get("status"), "passed", "observation.status")
            require_equal(observation_v2.get("source_git_commit_sha"), source, "observation.source")
            require_equal(observation_v2.get("version_doi"), doi, "observation.version_doi")
            if successor_status == "prepared":
                require_equal(state.get("latest_doi"), doi, "prepared sequence3 predecessor DOI")
                require_equal(
                    state.get("publication_status"),
                    "prepared_for_final_evidence_baseline_publication_v3",
                    "prepared sequence3 state",
                )
            else:
                require_equal(state.get("latest_doi"), successor.get("published_doi"), "sequence3 latest DOI")
                require_equal(state.get("publication_status"), "published_and_publicly_restored", "sequence3 state")
                refresh = index.get("publication_refresh")
                if not isinstance(refresh, dict):
                    raise SystemExit("sequence3 recovery publication_refresh missing")
                require_equal(refresh.get("sequence"), 3, "sequence3 recovery sequence")
                require_equal(refresh.get("status"), "published_verified_and_consumed", "sequence3 recovery status")
            validate_sequence1_history()
            return

    require_equal(state.get("publication_status"), "published_and_publicly_restored", "state.publication_status")
    require_equal(state.get("latest_git_commit_sha"), source, "state.latest_git_commit_sha")
    require_equal(state.get("latest_doi"), doi, "state.latest_doi")
    require_equal(state.get("latest_record_id"), record_id, "state.latest_record_id")
    require_equal(state.get("latest_package_identity_sha256"), package, "state.latest_package_identity_sha256")
    require_equal(state.get("concept_doi"), CONCEPT_DOI, "state.concept_doi")
    require_equal(state.get("public_cold_restore"), "passed", "state.public_cold_restore")
    require_equal(state.get("public_metadata_verification"), "passed", "state.public_metadata_verification")
    require_equal(state.get("live_main_equivalence_claimed"), False, "state.live_main_equivalence_claimed")

    versions = state.get("versions")
    if not isinstance(versions, list):
        raise SystemExit("state.versions missing")
    by_doi = {item.get("doi"): item for item in versions if isinstance(item, dict)}
    if PREVIOUS_DOI not in by_doi or doi not in by_doi:
        raise SystemExit("preservation version history does not contain both sequence-1 and sequence-2 DOI records")

    prepared = load(PREPARED)
    require_equal(prepared.get("status"), "published_verified", "prepared.status")
    require_equal(prepared.get("source_git_commit_sha"), source, "prepared.source")
    require_equal(prepared.get("version_doi"), doi, "prepared.version_doi")
    observation = load(OBSERVATION)
    require_equal(observation.get("status"), "passed", "observation.status")
    require_equal(observation.get("source_git_commit_sha"), source, "observation.source")
    require_equal(observation.get("version_doi"), doi, "observation.version_doi")
    require_equal(observation.get("public_cold_restore"), "passed", "observation.public_cold_restore")
    require_equal(observation.get("arweave_snapshot_refreshed"), False, "observation.arweave_snapshot_refreshed")

    refresh = index.get("publication_refresh")
    if not isinstance(refresh, dict):
        raise SystemExit("recovery index publication_refresh missing")
    require_equal(refresh.get("sequence"), 2, "recovery.publication_refresh.sequence")
    require_equal(refresh.get("status"), "published_verified_and_consumed", "recovery.publication_refresh.status")
    require_equal(refresh.get("source_git_commit_sha"), source, "recovery.publication_refresh.source")
    require_equal(refresh.get("version_doi"), doi, "recovery.publication_refresh.doi")
    require_equal(refresh.get("arweave_snapshot_refreshed"), False, "recovery.publication_refresh.arweave_snapshot_refreshed")
    latest = index.get("latest_trusted_release", {}).get("repository_preservation", {})
    require_equal(latest.get("doi"), doi, "recovery.latest_trusted_release.doi")
    require_equal(latest.get("git_commit_sha"), source, "recovery.latest_trusted_release.source")
    require_equal(latest.get("package_identity_sha256"), package, "recovery.latest_trusted_release.package")
    validate_sequence1_history()


def validate() -> None:
    auth = load(AUTH)
    state = load(STATE)
    index = load(INDEX)
    validate_static_auth(auth)
    status = auth.get("status")
    if status == "pending":
        validate_pending(auth, state)
    elif status == "prepared":
        validate_prepared(auth, state)
    elif status == "consumed":
        validate_consumed(auth, state, index)
    else:
        raise SystemExit(f"invalid sequence-2 authorization status: {status!r}")
    print(f"Current baseline publication v2 state valid: {status}")


def prepare(base_commit: str) -> None:
    auth = load(AUTH)
    state = load(STATE)
    index = load(INDEX)
    validate_static_auth(auth)
    validate_pending(auth, state)
    validate_sequence1_history()
    if len(base_commit) != 40:
        raise SystemExit("base commit must be a full 40-character Git SHA")

    previous = {
        "doi": state.get("latest_doi"),
        "record_id": state.get("latest_record_id"),
        "git_commit_sha": state.get("latest_git_commit_sha"),
        "git_tree_oid": state.get("latest_git_tree_oid"),
        "package_identity_sha256": state.get("latest_package_identity_sha256"),
    }
    auth["status"] = "prepared"
    auth["prepared_base_commit_sha"] = base_commit
    state.update(
        {
            "publication_status": "prepared_for_current_baseline_publication_v2",
            "prepared_base_commit_sha": base_commit,
            "previous_verified_version": previous,
            "planned_homepage_arweave_snapshot": False,
            "live_main_equivalence_claimed": False,
        }
    )
    index["publication_refresh"] = {
        "schema": auth["schema"],
        "sequence": 2,
        "status": "prepared_for_current_baseline_publication",
        "authorized_base_commit_sha": base_commit,
        "required_proof_hardening_commit_sha": REQUIRED_HARDENING,
        "previous_version_doi": PREVIOUS_DOI,
        "core_concept_doi": CONCEPT_DOI,
        "arweave_snapshot_refreshed": False,
        "previous_sequence_1_arweave_txid": PREVIOUS_ARWEAVE_TX,
        "non_amending_boundary": True,
    }
    update_index_digest(index)
    prepared = {
        "schema": "trinityaccord.current-baseline-publication-prepared.v2",
        "sequence": 2,
        "status": "prepared",
        "base_commit_sha": base_commit,
        "required_proof_hardening_commit_sha": REQUIRED_HARDENING,
        "previous_version_doi": PREVIOUS_DOI,
        "core_concept_doi": CONCEPT_DOI,
        "publication_scope": "full_git_tracked_repository_exact_baseline",
        "arweave_snapshot_refreshed": False,
        "boundary": {
            "non_amending": True,
            "bitcoin_originals_prevail": True,
            "live_main_equivalence_claimed": False,
        },
    }
    write(AUTH, auth)
    write(STATE, state)
    write(INDEX, index)
    write(PREPARED, prepared)


def seal(source_commit: str, published_state_path: Path, recovery_report_path: Path) -> None:
    auth = load(AUTH)
    state = load(STATE)
    index = load(INDEX)
    validate_static_auth(auth)
    prepared = validate_prepared(auth, state)
    published = load(published_state_path)
    recovery = load(recovery_report_path)

    require_equal(published.get("latest_git_commit_sha"), source_commit, "published.latest_git_commit_sha")
    require_equal(published.get("concept_doi"), CONCEPT_DOI, "published.concept_doi")
    new_doi = published.get("latest_doi")
    if not isinstance(new_doi, str) or new_doi == PREVIOUS_DOI or not new_doi.startswith("10.5281/zenodo."):
        raise SystemExit("publisher did not create/reconcile a distinct sequence-2 DOI")
    new_record_id = published.get("latest_record_id")
    if not isinstance(new_record_id, int) or new_record_id <= 0:
        raise SystemExit("publisher did not record a valid Zenodo record id")
    package = published.get("latest_package_identity_sha256")
    if not isinstance(package, str) or len(package) != 64:
        raise SystemExit("publisher did not record a valid package identity")
    require_equal(recovery.get("result"), "pass", "public_recovery.result")
    require_equal(recovery.get("source_git_commit_sha"), source_commit, "public_recovery.source")

    previous_verified = state.get("previous_verified_version")
    final = dict(state)
    final.update(published)
    # The prepared state inherited sequence 1's report.  It is bound to the
    # predecessor record and must not be presented as sequence 2 metadata.
    final.pop("public_metadata_report", None)
    final.update(
        {
            "schema": "trinityaccord.repository-preservation-zenodo-state.v2",
            "publication_status": "published_and_publicly_restored",
            "source_baseline_commit_sha": source_commit,
            "public_download_verification": "passed",
            "public_metadata_verification": "passed",
            "public_cold_restore": "passed",
            "public_cold_restore_report": recovery,
            "previous_verified_version": previous_verified,
            "github_required_for_discovery": False,
            "github_required_for_repository_recovery": False,
            "live_main_equivalence_claimed": False,
            "coverage_scope": "exact Git-tracked publication baseline named by latest_git_commit_sha",
            "homepage_snapshot_refresh": {
                "status": "not_requested_sequence_2",
                "sequence_1_arweave_txid": PREVIOUS_ARWEAVE_TX,
                "sequence_1_payload_sha256": PREVIOUS_ARWEAVE_SHA,
                "sequence_1_source_commit_sha": PREVIOUS_SOURCE,
            },
        }
    )

    auth.update(
        {
            "status": "consumed",
            "published_source_baseline_commit_sha": source_commit,
            "published_record_id": new_record_id,
            "published_doi": new_doi,
            "published_package_identity_sha256": package,
        }
    )
    prepared.update(
        {
            "status": "published_verified",
            "source_git_commit_sha": source_commit,
            "version_doi": new_doi,
            "zenodo_record_id": new_record_id,
            "zenodo_package_identity_sha256": package,
        }
    )
    observation = {
        "schema": "trinityaccord.current-baseline-publication-observation.v2",
        "sequence": 2,
        "status": "passed",
        "source_git_commit_sha": source_commit,
        "version_doi": new_doi,
        "concept_doi": CONCEPT_DOI,
        "zenodo_record_id": new_record_id,
        "zenodo_package_identity_sha256": package,
        "public_metadata_and_byte_verification": "passed_by_v3_publisher",
        "public_cold_restore": "passed",
        "arweave_snapshot_refreshed": False,
        "previous_sequence_1_arweave_txid": PREVIOUS_ARWEAVE_TX,
        "boundary": {
            "non_amending": True,
            "bitcoin_originals_prevail": True,
            "repository_doi_is_exact_baseline_not_live_main": True,
            "sequence_1_arweave_snapshot_remains_historical_mirror_only": True,
        },
    }

    latest_release = index.setdefault("latest_trusted_release", {}).setdefault("repository_preservation", {})
    latest_release.update(
        {
            "doi": new_doi,
            "record_id": new_record_id,
            "concept_doi": CONCEPT_DOI,
            "git_commit_sha": source_commit,
            "git_tree_oid": published.get("latest_git_tree_oid"),
            "package_identity_sha256": package,
            "github_required_for_recovery": False,
            "github_required_for_discovery": False,
            "public_metadata_verification": "passed",
            "public_cold_restore": "passed",
            "coverage_status": "exact_published_baseline",
            "live_main_equivalence_claimed": False,
        }
    )
    index["publication_refresh"] = {
        "schema": auth["schema"],
        "sequence": 2,
        "status": "published_verified_and_consumed",
        "source_git_commit_sha": source_commit,
        "version_doi": new_doi,
        "core_concept_doi": CONCEPT_DOI,
        "previous_version_doi": PREVIOUS_DOI,
        "required_proof_hardening_commit_sha": REQUIRED_HARDENING,
        "arweave_snapshot_refreshed": False,
        "previous_sequence_1_arweave_txid": PREVIOUS_ARWEAVE_TX,
        "previous_sequence_1_arweave_payload_sha256": PREVIOUS_ARWEAVE_SHA,
        "non_amending_boundary": True,
    }
    update_index_digest(index)

    write(STATE, final)
    write(AUTH, auth)
    write(PREPARED, prepared)
    write(OBSERVATION, observation)
    write(INDEX, index)
    if published_state_path.exists() and published_state_path.is_file() and published_state_path.parent == ROOT / "preservation":
        published_state_path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    prep = sub.add_parser("prepare")
    prep.add_argument("--base-commit", required=True)
    sealing = sub.add_parser("seal")
    sealing.add_argument("--source-commit", required=True)
    sealing.add_argument("--published-state", required=True)
    sealing.add_argument("--recovery-report", required=True)
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
        )
        validate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
