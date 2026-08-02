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


def normalized_public_record(record: dict[str, Any]) -> dict[str, Any]:
    """Merge direct-record top-level metadata into the metadata validation view.

    Zenodo's direct `/api/records/{id}` response currently exposes the custom
    license at top level while the corresponding search/deposition metadata and
    uploaded metadata file use `metadata.license`. Values are copied only when
    absent from `metadata`; conflicting values remain visible and fail normal
    equality checks rather than being overwritten.
    """
    normalized = copy.deepcopy(record)
    metadata_value = normalized.get("metadata")
    metadata = dict(metadata_value) if isinstance(metadata_value, dict) else {}
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
