#!/usr/bin/env python3
"""Publish final immutable V4 annexes and reconcile public Evidence V4 safely."""
from __future__ import annotations

import argparse
import copy
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import external_binary_annex_v2 as builder_implementation
from external_binary_annex_v4 import FINAL_ANNEX_IDS

builder_implementation.V2_ANNEX_IDS = dict(FINAL_ANNEX_IDS)

import publish_external_binary_annexes_to_zenodo_v2 as publisher  # noqa: E402
from publish_preservation_capsule_to_zenodo import (  # noqa: E402
    deposition_id,
    is_published,
    list_depositions,
)

_original_validate_public_metadata = publisher.validate_public_metadata

EVIDENCE_V4_RECORD_ID = 21753937
EVIDENCE_V4_DOI = "10.5281/zenodo.21753937"
EVIDENCE_V4_CONCEPT_RECORD_ID = 21753253
EVIDENCE_V4_SOURCE_SHA = "8942c1c3bf52a09b038eccf8f5cf9377f0732244"
EVIDENCE_V4_PACKAGE_IDENTITY_SHA256 = (
    "830eaa1b2ee8a0c6c961cf2ab5f369147a59c9df0b05304102da17b897d44bbf"
)
EVIDENCE_V4_MANIFEST_SHA256 = (
    "650c71b8f51b70b11abab0953e53c2293ae52c56ba8131b3b3687a4534a28e51"
)
EVIDENCE_V4_PAYLOAD_TAR_SHA256 = (
    "86c8b34f267f21615a78f3804c5886ae6985a764d6a77a653d7009d0091a8bee"
)
EXACT_STABLE_EVIDENCE_FILES = (
    "payload.tar",
    "README.txt",
    "restore-trinity-annex.py",
    "zenodo-metadata.json",
)


def current_core_repository_reference() -> dict[str, str]:
    state_path = publisher.ROOT / "preservation/repository-preservation-state-v2.json"
    value = json.loads(state_path.read_text(encoding="utf-8"))
    external_state_path = publisher.ROOT / "preservation/external-binary-annex-state.json"
    external_state = json.loads(external_state_path.read_text(encoding="utf-8"))
    concept = str(value.get("concept_doi") or "")
    latest = str(value.get("latest_doi") or "")
    if concept != "10.5281/zenodo.21739343":
        raise SystemExit("unexpected current core repository Concept DOI")
    if not latest.startswith("10.5281/zenodo."):
        raise SystemExit("current core repository version DOI is missing")
    historical = "10.5281/zenodo.21739344"
    expected = {
        "core_repository_preservation_doi": historical,
        "core_repository_preservation_doi_role": "historical_version_reference",
        "current_core_repository_concept_doi": concept,
        "current_core_repository_latest_version_doi": latest,
    }
    for field, wanted in expected.items():
        if external_state.get(field) != wanted:
            raise SystemExit(f"external annex state has a stale DOI role: {field}")
    note = external_state.get("core_repository_reference_note")
    if not isinstance(note, str) or historical not in note or concept not in note or latest not in note:
        raise SystemExit("external annex state has an incomplete core repository DOI note")
    return {**expected, "core_repository_reference_note": note}


def _canonical_related_identifier(identifier: Any, scheme: Any = "") -> str:
    """Normalize only representation-equivalent DOI identifiers."""
    value = str(identifier or "").strip()
    lowered = value.lower()
    for prefix in (
        "https://doi.org/",
        "http://doi.org/",
        "https://dx.doi.org/",
        "http://dx.doi.org/",
        "doi:",
    ):
        if lowered.startswith(prefix):
            value = value[len(prefix) :]
            lowered = value.lower()
            break
    scheme_id = publisher._relation_id(scheme)
    if scheme_id == "doi" or lowered.startswith("10."):
        return "doi:" + lowered
    return value


def _related_pairs_v4(value: Any) -> set[tuple[str, str, str]]:
    """Return canonical identifier/relation/resource triples for Zenodo shapes."""
    result: set[tuple[str, str, str]] = set()
    if not isinstance(value, list):
        return result
    for item in value:
        if not isinstance(item, dict):
            continue
        identifier = _canonical_related_identifier(
            item.get("identifier"), item.get("scheme")
        )
        relation_value = (
            item.get("relation")
            if item.get("relation") not in (None, "")
            else item.get("relation_type")
        )
        relation = publisher._relation_id(relation_value)
        resource_type = publisher._relation_id(item.get("resource_type"))
        if identifier and relation:
            result.add((identifier, relation, resource_type))
    return result


publisher._related_pairs = _related_pairs_v4


def _canonical_duplicate_value(key: str, value: Any) -> Any:
    if key == "license":
        return publisher._license_ids({"license": value})
    if key == "rights":
        return publisher._license_ids({"rights": value})
    if key == "creators":
        return publisher._creator_names(value)
    if key == "related_identifiers":
        return publisher._related_pairs(value)
    if key == "keywords":
        return tuple(str(item) for item in value) if isinstance(value, list) else ()
    if isinstance(value, (str, int, float, bool)) or value is None:
        return str(value or "")
    return value


def _reject_conflicting_duplicate_fields(
    record: dict[str, Any], metadata: dict[str, Any]
) -> None:
    top_license_ids = publisher._license_ids(
        {"license": record.get("license"), "rights": record.get("rights")}
    )
    metadata_license_ids = publisher._license_ids(metadata)
    if top_license_ids and metadata_license_ids and top_license_ids != metadata_license_ids:
        raise SystemExit("Zenodo public metadata conflict: license/rights")
    for key in (
        "creators",
        "related_identifiers",
        "keywords",
        "title",
        "version",
        "publication_date",
        "description",
        "notes",
        "access_right",
    ):
        if key not in record or key not in metadata:
            continue
        if _canonical_duplicate_value(key, record[key]) != _canonical_duplicate_value(
            key, metadata[key]
        ):
            raise SystemExit(f"Zenodo public metadata conflict: {key}")


def normalized_public_record(record: dict[str, Any]) -> dict[str, Any]:
    """Merge only non-conflicting direct-record fields into metadata."""
    normalized = copy.deepcopy(record)
    metadata_value = normalized.get("metadata")
    metadata = dict(metadata_value) if isinstance(metadata_value, dict) else {}
    _reject_conflicting_duplicate_fields(normalized, metadata)
    for key in (
        "license",
        "rights",
        "creators",
        "related_identifiers",
        "keywords",
        "title",
        "version",
        "publication_date",
        "description",
        "notes",
        "access_right",
    ):
        if key not in metadata and key in normalized:
            metadata[key] = copy.deepcopy(normalized[key])
    normalized["metadata"] = metadata
    return normalized


def validate_public_metadata_v4(
    record: dict[str, Any], expected: dict[str, Any]
) -> None:
    _original_validate_public_metadata(normalized_public_record(record), expected)


publisher.validate_public_metadata = validate_public_metadata_v4


def _stable_manifest_view(manifest: dict[str, Any]) -> dict[str, Any]:
    """Remove only non-content observations that legitimately change over time."""
    stable = copy.deepcopy(manifest)
    stable.pop("source_commit_sha", None)
    stable.pop("package_identity_sha256", None)
    assets = stable.get("assets")
    if not isinstance(assets, list):
        raise SystemExit("Evidence V4 manifest lacks assets list")
    for item in assets:
        if not isinstance(item, dict):
            raise SystemExit("Evidence V4 manifest contains a non-object asset")
        item.pop("download_count_at_capture", None)
    return stable


def _verify_public_file_metadata(
    name: str,
    item: dict[str, Any],
    downloaded: Path,
) -> None:
    size = item.get("size", item.get("filesize"))
    if int(size or -1) != downloaded.stat().st_size:
        raise SystemExit(f"Evidence V4 public file size mismatch: {name}")
    checksum = publisher._item_checksum(item)
    if not checksum:
        return
    algorithm, _, expected = checksum.partition(":")
    if algorithm == "md5":
        observed = publisher.package_module.md5_file(downloaded)
    elif algorithm == "sha256":
        observed = publisher.package_module.hash_file(downloaded)
    else:
        return
    if observed != expected:
        raise SystemExit(f"Evidence V4 public file checksum mismatch: {name}")


def verify_existing_evidence_v4(
    client: publisher.ZenodoClient,
    current_package_dir: Path,
    api_base: str,
) -> dict[str, Any]:
    """Verify the immutable public Evidence V4 package against stable source content.

    The public six-file package is the source of truth for its own immutable
    source SHA, manifest and package identity. A current rebuild is used only to
    prove that every stable release/content/right/boundary field still matches.
    Download counters and the coordination workflow source are observations, not
    content, and are the only excluded fields.
    """
    current = publisher.package_module.verify_local_package(current_package_dir)
    current_manifest = current["manifest"]
    if current["annex_type"] != "evidence":
        raise SystemExit("Evidence V4 verifier received wrong annex type")
    if current["annex_id"] != FINAL_ANNEX_IDS["evidence"]:
        raise SystemExit("Evidence V4 verifier received wrong annex id")
    if publisher.package_module.hash_file(current_package_dir / "payload.tar") != (
        EVIDENCE_V4_PAYLOAD_TAR_SHA256
    ):
        raise SystemExit("Evidence V4 current payload differs from public payload")

    title = str(current["metadata"]["title"])
    records = publisher.legacy.series_records(list_depositions(client), title)
    same = [
        item
        for item in records
        if publisher.legacy.version(item) == FINAL_ANNEX_IDS["evidence"]
        and is_published(item)
    ]
    if len(same) != 1:
        raise SystemExit("Evidence V4 must have exactly one published deposition")
    authenticated_record_id = int(
        same[0].get("record_id") or deposition_id(same[0])
    )
    if authenticated_record_id != EVIDENCE_V4_RECORD_ID:
        raise SystemExit("unexpected published Evidence V4 record id")

    record = publisher.legacy.public_record(EVIDENCE_V4_RECORD_ID)
    if publisher._record_doi(record) != EVIDENCE_V4_DOI:
        raise SystemExit("unexpected published Evidence V4 DOI")
    if publisher._concept_record_id(record) != EVIDENCE_V4_CONCEPT_RECORD_ID:
        raise SystemExit("unexpected Evidence V4 concept record id")
    remote = publisher._public_file_items(record)
    expected_names = set(publisher.package_module.PUBLISHED_FILE_NAMES)
    if set(remote) != expected_names:
        raise SystemExit(
            "Evidence V4 public file set mismatch: "
            f"missing={sorted(expected_names-set(remote))} "
            f"unexpected={sorted(set(remote)-expected_names)}"
        )

    with tempfile.TemporaryDirectory(
        prefix="trinity-evidence-v4-public-package-"
    ) as temp_name:
        public_dir = Path(temp_name)
        for name in publisher.package_module.PUBLISHED_FILE_NAMES:
            url = publisher._public_url(remote[name])
            if not url:
                raise SystemExit(f"Evidence V4 public URL missing: {name}")
            target = public_dir / name
            publisher.legacy.curl_download(url, target)
            _verify_public_file_metadata(name, remote[name], target)

        public = publisher.package_module.verify_local_package(public_dir)
        public_manifest = public["manifest"]
        if public["annex_type"] != "evidence":
            raise SystemExit("public Evidence V4 package has wrong annex type")
        if public["annex_id"] != FINAL_ANNEX_IDS["evidence"]:
            raise SystemExit("public Evidence V4 package has wrong annex id")
        if public_manifest.get("source_commit_sha") != EVIDENCE_V4_SOURCE_SHA:
            raise SystemExit("public Evidence V4 source commit mismatch")
        if public["package_identity_sha256"] != EVIDENCE_V4_PACKAGE_IDENTITY_SHA256:
            raise SystemExit("public Evidence V4 package identity mismatch")
        if publisher.package_module.hash_file(public_dir / "annex-manifest.json") != (
            EVIDENCE_V4_MANIFEST_SHA256
        ):
            raise SystemExit("public Evidence V4 manifest hash mismatch")
        if publisher.package_module.hash_file(public_dir / "payload.tar") != (
            EVIDENCE_V4_PAYLOAD_TAR_SHA256
        ):
            raise SystemExit("public Evidence V4 payload hash mismatch")
        if int(public["asset_count"]) != 28 or int(public["payload_bytes"]) != 204595967:
            raise SystemExit("public Evidence V4 inventory totals mismatch")

        validate_public_metadata_v4(record, current["metadata"])
        if _stable_manifest_view(public_manifest) != _stable_manifest_view(
            current_manifest
        ):
            raise SystemExit("Evidence V4 stable manifest content differs")
        for name in EXACT_STABLE_EVIDENCE_FILES:
            if publisher.package_module.hash_file(public_dir / name) != (
                publisher.package_module.hash_file(current_package_dir / name)
            ):
                raise SystemExit(f"Evidence V4 stable file differs: {name}")

        entry = publisher._state_entry_v2(record, public, api_base)
        entry["source_commit_sha"] = EVIDENCE_V4_SOURCE_SHA
        entry["public_metadata_verification"] = "passed"
        entry["stable_source_content_verification"] = "passed"
        return entry


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-package-dir", required=True)
    parser.add_argument("--nft-package-dir", required=True)
    parser.add_argument(
        "--state", default="preservation/external-binary-annex-state.json"
    )
    parser.add_argument(
        "--api-base",
        default=os.environ.get("ZENODO_API_BASE", publisher.DEFAULT_API),
    )
    parser.add_argument(
        "--rights-boundary-ack",
        default=os.environ.get("EXTERNAL_BINARY_ANNEX_RIGHTS_ACK", ""),
    )
    parser.add_argument(
        "--source-commit",
        default=os.environ.get("TRINITY_PUBLICATION_SOURCE_SHA", ""),
    )
    args = parser.parse_args()
    if args.rights_boundary_ack != publisher.RIGHTS_ACKNOWLEDGEMENT:
        raise SystemExit(
            "external binary annex publication requires the exact rights acknowledgement"
        )

    workflow_source = builder_implementation._valid_commit_sha(args.source_commit)
    builder_implementation.V2_ANNEX_IDS = dict(FINAL_ANNEX_IDS)
    builder_implementation.activate_v2_specs()

    evidence_dir = Path(args.evidence_package_dir).resolve()
    nft_dir = Path(args.nft_package_dir).resolve()
    token = os.environ.get("ZENODO_ACCESS_TOKEN", "").strip()
    client = publisher.ZenodoClient(token, args.api_base)

    evidence = verify_existing_evidence_v4(client, evidence_dir, args.api_base)
    nft = publisher.publish_one_v2(client, token, nft_dir, args.api_base)
    expected_sources = {
        "evidence": EVIDENCE_V4_SOURCE_SHA,
        "nft": workflow_source,
    }
    for annex_type, entry in (("evidence", evidence), ("nft", nft)):
        if entry["source_commit_sha"] != expected_sources[annex_type]:
            raise SystemExit(f"annex source commit mismatch: {annex_type}")

    state = {
        "schema": publisher.package_module.STATE_SCHEMA,
        "publication_status": "published_pending_public_cold_restore",
        "source_commit_sha": workflow_source,
        "publication_workflow_source_commit_sha": workflow_source,
        "annex_source_commits": expected_sources,
        **current_core_repository_reference(),
        "rights_boundary_schema": "trinityaccord.external-binary-annex-rights.v1",
        "annexes": {"evidence": evidence, "nft": nft},
        "all_named_release_assets_embedded": True,
        "release_asset_pagination_complete": True,
        "public_metadata_verification": "passed",
        "deprecated_failed_nft_attempts_embedded": False,
        "external_binary_payload_recovery_requires_github": False,
    }
    state_path = (publisher.ROOT / args.state).resolve()
    if publisher.ROOT not in state_path.parents:
        raise SystemExit("annex state path must remain inside the repository")
    publisher.package_module.write_json(state_path, state)
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"evidence_record_id={evidence['record_id']}\n")
            handle.write(f"evidence_doi={evidence['doi']}\n")
            handle.write(f"nft_record_id={nft['record_id']}\n")
            handle.write(f"nft_doi={nft['doi']}\n")
    print(json.dumps(state, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
