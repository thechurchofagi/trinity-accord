#!/usr/bin/env python3
"""Verify Builder receipt-boundary fields stay synchronized across CI surfaces.

This check intentionally fails with a clear message instead of editing files in CI.
It protects the Builder, submission schema, Phase 5C regression allowlist, and
builder bundle manifest from drifting out of sync after receipt-boundary changes.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RECEIPT_BOUNDARY_FIELDS = [
    "receipt_is_not_final_inclusion",
    "receipt_is_intake_only",
    "later_records_may_reclassify_or_correct_this_record",
]

BASE_BOUNDARY_FIELDS = [
    "not_authority",
    "not_governance",
    "not_attestation",
    "not_successor_reception",
    "not_amendment",
    "bitcoin_originals_prevail",
]

REQUIRED_SUBMISSION_BOUNDARY_FIELDS = BASE_BOUNDARY_FIELDS + RECEIPT_BOUNDARY_FIELDS


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def load_json(relative_path: str) -> dict:
    path = ROOT / relative_path
    if not path.exists():
        fail(f"missing {relative_path}")
    return json.loads(path.read_text(encoding="utf-8"))


def require_text(relative_path: str, needles: list[str]) -> str:
    path = ROOT / relative_path
    if not path.exists():
        fail(f"missing {relative_path}")
    text = path.read_text(encoding="utf-8")
    for needle in needles:
        if needle not in text:
            fail(f"{relative_path} missing synchronized text: {needle}")
    return text


def check_submission_schema() -> None:
    schema = load_json("api/record-chain-submission-schema.v1.json")
    boundary = schema.get("properties", {}).get("submission_boundary")
    if not isinstance(boundary, dict):
        fail("schema properties.submission_boundary is missing or not an object")

    required = boundary.get("required")
    if required != REQUIRED_SUBMISSION_BOUNDARY_FIELDS:
        fail(f"submission_boundary.required drifted: {required!r}")

    properties = boundary.get("properties", {})
    for field in REQUIRED_SUBMISSION_BOUNDARY_FIELDS:
        if properties.get(field) != {"const": True}:
            fail(f"submission_boundary.properties.{field} must be {{'const': True}}")

    extra = sorted(set(properties) - set(REQUIRED_SUBMISSION_BOUNDARY_FIELDS))
    if extra:
        fail(f"submission_boundary has schema-invalid extra properties: {extra}")

    if boundary.get("additionalProperties") is not False:
        fail("submission_boundary.additionalProperties must be false")


def check_builder_source() -> None:
    require_text(
        "downloads/record-chain-builder.mjs",
        [f"{field}: true" for field in RECEIPT_BOUNDARY_FIELDS],
    )


def check_phase5_allowlist() -> None:
    require_text(
        "scripts/test_phase_5c_hotfix.py",
        [f'"{field}"' for field in REQUIRED_SUBMISSION_BOUNDARY_FIELDS],
    )


def check_builder_manifest_hash() -> None:
    builder_path = ROOT / "downloads/record-chain-builder.mjs"
    manifest = load_json("api/record-chain-builder-bundles.v1.json")
    canonical_builder = manifest.get("canonical_builder", {})
    builder_bytes = builder_path.read_bytes()
    expected_sha = hashlib.sha256(builder_bytes).hexdigest()
    expected_size = len(builder_bytes)
    if canonical_builder.get("sha256") != expected_sha:
        fail("api/record-chain-builder-bundles.v1.json canonical_builder.sha256 is stale")
    if canonical_builder.get("size_bytes") != expected_size:
        fail("api/record-chain-builder-bundles.v1.json canonical_builder.size_bytes is stale")


def main() -> int:
    check_submission_schema()
    check_builder_source()
    check_phase5_allowlist()
    check_builder_manifest_hash()
    print("PASS: Builder receipt-boundary fields are synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
