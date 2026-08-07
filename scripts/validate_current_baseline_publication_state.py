#!/usr/bin/env python3
"""Validate the one-shot current-baseline DOI and Arweave publication lifecycle."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUTH_PATH = ROOT / "preservation/current-baseline-publication-authorization-v1.json"
PREPARED_PATH = ROOT / "preservation/current-baseline-publication-prepared-v1.json"
OBSERVATION_PATH = ROOT / "preservation/current-baseline-publication-observation-v1.json"
STATE_PATH = ROOT / "preservation/repository-preservation-state-v2.json"
INDEX_PATH = ROOT / "api/recovery-index.json"

AUTH_SCHEMA = "trinityaccord.current-baseline-publication-authorization.v1"
PREPARED_SCHEMA = "trinityaccord.current-baseline-publication-prepared.v1"
OBSERVATION_SCHEMA = "trinityaccord.current-baseline-publication-observation.v1"
CONCEPT_DOI = "10.5281/zenodo.21739343"
PREVIOUS_DOI = "10.5281/zenodo.21755827"
ZENODO_ACK = "TRINITY_PRESERVATION_CAPSULE_RIGHTS_V1_APPROVED"
ARWEAVE_ACK = "TRINITY_HOMEPAGE_SNAPSHOT_ARWEAVE_V1_APPROVED"
CONFIRMATION = "PUBLISH_TRINITY_CURRENT_BASELINE_V1"
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
DOI_RE = re.compile(r"^10\.5281/zenodo\.\d+$")


def strict_json(path: Path) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in items:
            if key in value:
                raise SystemExit(f"duplicate JSON key {key!r}: {path}")
            value[key] = item
        return value

    try:
        parsed = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"non-finite number {token}")
            ),
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise SystemExit(f"invalid strict JSON: {path}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return parsed


def require(value: bool, message: str) -> None:
    if not value:
        raise SystemExit(message)


def canonical_index_digest(index: dict[str, Any]) -> str:
    canonical = dict(index)
    canonical.pop("source_digest", None)
    raw = json.dumps(
        canonical,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def validate_authorization() -> dict[str, Any]:
    auth = strict_json(AUTH_PATH)
    expected = {
        "schema": AUTH_SCHEMA,
        "sequence": 1,
        "authorized_by": "thechurchofagi",
        "core_concept_doi": CONCEPT_DOI,
        "previous_core_version_doi": PREVIOUS_DOI,
        "zenodo_rights_acknowledgement": ZENODO_ACK,
        "arweave_rights_acknowledgement": ARWEAVE_ACK,
        "publication_confirmation": CONFIRMATION,
        "include_full_repository_doi": True,
        "include_homepage_arweave_snapshot": True,
        "non_amending_boundary": True,
        "live_main_equivalence_claimed": False,
    }
    for key, value in expected.items():
        require(auth.get(key) == value, f"current-baseline authorization mismatch: {key}")
    require(auth.get("status") in {"pending", "prepared", "consumed"}, "invalid current-baseline authorization status")
    return auth


def validate_prepared(auth: dict[str, Any], state: dict[str, Any], index: dict[str, Any]) -> None:
    base = auth.get("prepared_base_commit_sha")
    require(isinstance(base, str) and COMMIT_RE.fullmatch(base) is not None, "prepared authorization lacks exact base commit")
    prepared = strict_json(PREPARED_PATH)
    require(prepared.get("schema") == PREPARED_SCHEMA, "prepared record schema mismatch")
    require(prepared.get("sequence") == 1 and prepared.get("status") == "prepared", "prepared record status mismatch")
    require(prepared.get("base_commit_sha") == base, "prepared record base commit mismatch")
    require(prepared.get("previous_version_doi") == PREVIOUS_DOI, "prepared record previous DOI mismatch")
    require(prepared.get("core_concept_doi") == CONCEPT_DOI, "prepared record concept DOI mismatch")
    boundary = prepared.get("boundary")
    require(isinstance(boundary, dict), "prepared record boundary is missing")
    require(boundary.get("non_amending") is True, "prepared record must be non-amending")
    require(boundary.get("bitcoin_originals_prevail") is True, "prepared record must preserve Bitcoin authority")
    require(boundary.get("live_main_equivalence_claimed") is False, "prepared record overclaims live-main equivalence")

    require(state.get("publication_status") == "prepared_for_current_baseline_publication", "prepared lifecycle state mismatch")
    require(state.get("prepared_base_commit_sha") == base, "prepared state base commit mismatch")
    require(state.get("latest_doi") == PREVIOUS_DOI, "prepared state must retain the last verified DOI")
    require(state.get("core_concept_doi") == CONCEPT_DOI, "prepared state concept DOI mismatch")
    require(state.get("planned_homepage_arweave_snapshot") is True, "prepared state lacks planned Arweave snapshot")
    previous = state.get("previous_verified_version")
    require(isinstance(previous, dict) and previous.get("doi") == PREVIOUS_DOI, "prepared state previous-version identity mismatch")

    refresh = index.get("publication_refresh")
    require(isinstance(refresh, dict), "prepared recovery index refresh is missing")
    require(refresh.get("schema") == AUTH_SCHEMA and refresh.get("sequence") == 1, "prepared recovery index schema mismatch")
    require(refresh.get("status") == "prepared_for_current_baseline_publication", "prepared recovery index status mismatch")
    require(refresh.get("authorized_base_commit_sha") == base, "prepared recovery index base mismatch")
    require(refresh.get("previous_version_doi") == PREVIOUS_DOI, "prepared recovery index previous DOI mismatch")
    require(refresh.get("core_concept_doi") == CONCEPT_DOI, "prepared recovery index concept DOI mismatch")
    require(refresh.get("homepage_arweave_snapshot_planned") is True, "prepared recovery index lacks Arweave intent")
    require(refresh.get("non_amending_boundary") is True, "prepared recovery index lacks non-amending boundary")

    trusted = index.get("latest_trusted_release")
    require(isinstance(trusted, dict), "prepared state lacks latest trusted release")
    repository = trusted.get("repository_preservation")
    require(isinstance(repository, dict) and repository.get("doi") == PREVIOUS_DOI, "prepared transition displaced the last trusted DOI")


def validate_consumed(auth: dict[str, Any], state: dict[str, Any], index: dict[str, Any]) -> None:
    source = auth.get("published_source_baseline_commit_sha")
    doi = auth.get("published_doi")
    package = auth.get("published_package_identity_sha256")
    txid = auth.get("homepage_snapshot_arweave_txid")
    payload_sha = auth.get("homepage_snapshot_sha256")
    require(isinstance(source, str) and COMMIT_RE.fullmatch(source) is not None, "consumed authorization lacks exact source commit")
    require(isinstance(doi, str) and DOI_RE.fullmatch(doi) is not None and doi != PREVIOUS_DOI, "consumed authorization lacks a new version DOI")
    require(isinstance(package, str) and SHA256_RE.fullmatch(package) is not None, "consumed authorization lacks package identity")
    require(isinstance(txid, str) and txid, "consumed authorization lacks Arweave transaction")
    require(isinstance(payload_sha, str) and SHA256_RE.fullmatch(payload_sha) is not None, "consumed authorization lacks Arweave payload digest")

    prepared = strict_json(PREPARED_PATH)
    require(prepared.get("schema") == PREPARED_SCHEMA and prepared.get("sequence") == 1, "published prepared-record schema mismatch")
    require(prepared.get("status") == "published_verified", "prepared record was not finalized")
    require(prepared.get("source_git_commit_sha") == source, "prepared record source mismatch")
    require(prepared.get("version_doi") == doi, "prepared record DOI mismatch")
    require(prepared.get("arweave_txid") == txid, "prepared record Arweave transaction mismatch")

    require(state.get("publication_status") == "published_and_publicly_restored", "consumed lifecycle lacks final published state")
    require(state.get("latest_doi") == doi, "final state DOI mismatch")
    require(state.get("latest_git_commit_sha") == source, "final state source commit mismatch")
    require(state.get("source_baseline_commit_sha") == source, "final state baseline commit mismatch")
    require(state.get("latest_package_identity_sha256") == package, "final state package identity mismatch")
    require(state.get("concept_doi") == CONCEPT_DOI or state.get("core_concept_doi") == CONCEPT_DOI, "final state concept DOI mismatch")
    require(state.get("public_download_verification") == "passed", "final state lacks public download verification")
    require(state.get("public_metadata_verification") == "passed", "final state lacks public metadata verification")
    require(state.get("public_cold_restore") == "passed", "final state lacks public cold restore")
    require(state.get("live_main_equivalence_claimed") is False, "final state overclaims live-main equivalence")

    arweave = state.get("homepage_machine_snapshot_arweave")
    require(isinstance(arweave, dict), "final state lacks homepage Arweave receipt")
    require(arweave.get("result") == "uploaded" and arweave.get("hash_match") is True, "homepage Arweave readback did not pass")
    require(arweave.get("txid") == txid or arweave.get("tx_id") == txid, "homepage Arweave transaction mismatch")
    require(arweave.get("payload_sha256") == payload_sha, "homepage Arweave payload digest mismatch")
    require(arweave.get("readback_sha256") == payload_sha, "homepage Arweave readback digest mismatch")
    require(arweave.get("source_git_commit_sha") == source, "homepage Arweave source mismatch")
    require(arweave.get("repository_version_doi") == doi, "homepage Arweave DOI binding mismatch")
    boundary = arweave.get("boundary")
    require(isinstance(boundary, dict) and boundary.get("arweave_snapshot_is_not_amendment") is True, "homepage Arweave boundary mismatch")
    require(boundary.get("bitcoin_originals_prevail") is True, "homepage Arweave authority boundary mismatch")

    observation = strict_json(OBSERVATION_PATH)
    require(observation.get("schema") == OBSERVATION_SCHEMA and observation.get("status") == "passed", "current-baseline observation did not pass")
    require(observation.get("source_git_commit_sha") == source, "observation source mismatch")
    require(observation.get("version_doi") == doi, "observation DOI mismatch")
    require(observation.get("zenodo_package_identity_sha256") == package, "observation package mismatch")
    require(observation.get("public_cold_restore") == "passed", "observation lacks public cold restore")
    require(observation.get("arweave_txid") == txid, "observation Arweave transaction mismatch")
    require(observation.get("arweave_payload_sha256") == payload_sha, "observation Arweave payload mismatch")
    require(observation.get("arweave_readback_sha256") == payload_sha, "observation Arweave readback mismatch")

    refresh = index.get("publication_refresh")
    require(isinstance(refresh, dict), "final recovery index refresh is missing")
    require(refresh.get("schema") == AUTH_SCHEMA and refresh.get("sequence") == 1, "final recovery index schema mismatch")
    require(refresh.get("status") == "published_verified_and_consumed", "final recovery index status mismatch")
    require(refresh.get("source_git_commit_sha") == source, "final recovery index source mismatch")
    require(refresh.get("version_doi") == doi, "final recovery index DOI mismatch")
    require(refresh.get("core_concept_doi") == CONCEPT_DOI, "final recovery index concept DOI mismatch")
    require(refresh.get("arweave_txid") == txid, "final recovery index Arweave transaction mismatch")
    require(refresh.get("arweave_payload_sha256") == payload_sha, "final recovery index Arweave digest mismatch")
    require(refresh.get("non_amending_boundary") is True, "final recovery index lacks non-amending boundary")

    trusted = index.get("latest_trusted_release")
    require(isinstance(trusted, dict) and trusted.get("status") == "published_and_publicly_restored", "final latest-trusted status mismatch")
    repository = trusted.get("repository_preservation")
    require(isinstance(repository, dict), "final latest-trusted repository entry is missing")
    require(repository.get("doi") == doi, "final latest-trusted DOI mismatch")
    require(repository.get("git_commit_sha") == source, "final latest-trusted source mismatch")
    require(repository.get("package_identity_sha256") == package, "final latest-trusted package mismatch")
    require(repository.get("public_cold_restore") == "passed", "final latest-trusted release lacks cold restore")


def validate() -> str:
    auth = validate_authorization()
    state = strict_json(STATE_PATH)
    index = strict_json(INDEX_PATH)
    require(index.get("source_digest") == canonical_index_digest(index), "recovery index source digest mismatch")
    require(state.get("live_main_equivalence_claimed") is False, "current state overclaims live-main equivalence")
    status = str(auth["status"])
    if status == "pending":
        require(state.get("publication_status") == "published_and_publicly_restored", "pending authorization disturbed the published state")
        require(state.get("latest_doi") == PREVIOUS_DOI, "pending authorization previous DOI mismatch")
    elif status == "prepared":
        validate_prepared(auth, state, index)
    elif status == "consumed":
        validate_consumed(auth, state, index)
    else:  # guarded above; retained for fail-closed readability
        raise SystemExit("unsupported current-baseline lifecycle state")
    print(f"Current baseline publication state valid: {status}")
    return status


def main() -> int:
    validate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
