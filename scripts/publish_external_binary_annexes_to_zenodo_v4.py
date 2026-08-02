#!/usr/bin/env python3
"""Publish final immutable V4 annexes with normalized Zenodo metadata views."""
from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
from typing import Any

import external_binary_annex_v2 as builder_implementation
from external_binary_annex_v4 import FINAL_ANNEX_IDS

builder_implementation.V2_ANNEX_IDS = dict(FINAL_ANNEX_IDS)

import publish_external_binary_annexes_to_zenodo_v2 as publisher  # noqa: E402

_original_validate_public_metadata = publisher.validate_public_metadata

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


def reconcile_immutable_evidence_v4(package_dir: Path) -> dict[str, Any]:
    """Recreate the exact already-published Evidence V4 package identity.

    Evidence V4 became immutable when source commit ``8942c1c3...`` was
    published. Later retries rebuild the same release bytes from newer workflow
    sources; only the manifest provenance field and its derived checksums differ.
    Rebinding that single field must reproduce all three known public identities
    exactly or publication stops before NFT V4 is created.
    """
    manifest_path = package_dir / "annex-manifest.json"
    manifest = publisher.package_module.strict_json(manifest_path)
    if manifest.get("annex_type") != "evidence":
        raise SystemExit("immutable Evidence V4 reconciliation received wrong annex type")
    if manifest.get("annex_id") != FINAL_ANNEX_IDS["evidence"]:
        raise SystemExit("immutable Evidence V4 reconciliation received wrong annex id")
    builder_implementation._valid_commit_sha(
        str(manifest.get("source_commit_sha") or "")
    )
    if publisher.package_module.hash_file(package_dir / "payload.tar") != (
        EVIDENCE_V4_PAYLOAD_TAR_SHA256
    ):
        raise SystemExit("Evidence V4 payload differs from the immutable public record")

    manifest["source_commit_sha"] = EVIDENCE_V4_SOURCE_SHA
    manifest["package_identity_sha256"] = None
    manifest["package_identity_sha256"] = publisher.package_module.manifest_identity(
        manifest
    )
    publisher.package_module.write_json(manifest_path, manifest)
    (package_dir / "checksums.sha256").write_text(
        "".join(
            f"{publisher.package_module.hash_file(package_dir / name)}  {name}\n"
            for name in publisher.package_module.CHECKSUM_TARGET_NAMES
        ),
        encoding="utf-8",
    )
    verified = publisher.package_module.verify_local_package(package_dir)
    if verified["package_identity_sha256"] != EVIDENCE_V4_PACKAGE_IDENTITY_SHA256:
        raise SystemExit("Evidence V4 package identity differs from the immutable record")
    if publisher.package_module.hash_file(manifest_path) != EVIDENCE_V4_MANIFEST_SHA256:
        raise SystemExit("Evidence V4 manifest differs from the immutable public record")
    return verified


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
    reconcile_immutable_evidence_v4(evidence_dir)

    token = os.environ.get("ZENODO_ACCESS_TOKEN", "").strip()
    client = publisher.ZenodoClient(token, args.api_base)
    evidence = publisher.publish_one_v2(
        client, token, evidence_dir, args.api_base
    )
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
        "core_repository_preservation_doi": "10.5281/zenodo.21739344",
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
