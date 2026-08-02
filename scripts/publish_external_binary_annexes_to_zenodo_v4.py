#!/usr/bin/env python3
"""Publish final immutable V4 annexes with normalized Zenodo metadata views."""
from __future__ import annotations

import copy
from typing import Any

import external_binary_annex_v2 as builder_implementation
from external_binary_annex_v4 import FINAL_ANNEX_IDS

builder_implementation.V2_ANNEX_IDS = dict(FINAL_ANNEX_IDS)

import publish_external_binary_annexes_to_zenodo_v2 as publisher  # noqa: E402

_original_validate_public_metadata = publisher.validate_public_metadata


def _canonical_related_identifier(identifier: Any, scheme: Any = "") -> str:
    """Normalize only representation-equivalent DOI identifiers.

    Zenodo stores a depositor DOI URL as a bare DOI plus ``scheme=doi`` in its
    public record. Non-DOI URLs remain exact strings so unrelated identifiers
    cannot become equivalent accidentally.
    """
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


# Public validation and duplicate-field conflict checks must use the same exact
# canonicalization rules. This changes representation handling only; it does not
# weaken relation or resource-type validation.
publisher._related_pairs = _related_pairs_v4


def _canonical_duplicate_value(key: str, value: Any) -> Any:
    """Canonicalize equivalent legacy/current Zenodo field representations."""
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
    """Reject contradictory top-level and nested public metadata representations."""
    top_license_ids = publisher._license_ids(
        {
            "license": record.get("license"),
            "rights": record.get("rights"),
        }
    )
    metadata_license_ids = publisher._license_ids(metadata)
    if (
        top_license_ids
        and metadata_license_ids
        and top_license_ids != metadata_license_ids
    ):
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
    """Merge non-conflicting direct-record fields into the metadata validation view.

    Zenodo's direct ``/api/records/{id}`` response can expose fields such as the
    custom license at top level while search/deposition responses and the
    uploaded metadata file expose them below ``metadata``. Equivalent legacy and
    current representations are accepted. Contradictory duplicate values are
    rejected before any missing value is copied, so a top-level public value can
    never be hidden by a matching nested value.
    """
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


def main() -> int:
    builder_implementation.V2_ANNEX_IDS = dict(FINAL_ANNEX_IDS)
    return publisher.main()


if __name__ == "__main__":
    raise SystemExit(main())
