#!/usr/bin/env python3
"""Finalize the already-uploaded Second Star-Moon Zenodo draft safely.

Recovery context:
- GitHub Actions run 33246735026 created Zenodo deposition 22159955.
- That run uploaded all 14 release assets and completed a full SHA-256
  pre-publication readback for every file.
- It stopped only because Zenodo returned bare MD5 strings while the first
  publisher expected an ``md5:`` prefix during the final metadata check.

This script does not blindly re-upload the 1.2 GB payload. It verifies the
source release, verifies the exact remote inventory using size + normalized
MD5, publishes the locked draft, then performs a fresh full SHA-256 readback
from the public record before writing repository state.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import time
from typing import Any

import publish_second_star_moon_to_zenodo as base

DEPOSITION_ID = 22159955
PRIOR_RUN_ID = 33246735026


def normalize_md5(value: Any) -> str:
    text = str(value or "").strip().lower()
    if text.startswith("md5:"):
        text = text[4:]
    return text


def verify_remote_rows(
    rows: list[dict[str, Any]],
    inventory: dict[str, dict[str, Any]],
    *,
    phase: str,
) -> dict[str, dict[str, Any]]:
    by_name = {base.get_remote_name(row): row for row in rows}
    expected_names = set(inventory)
    actual_names = set(by_name)
    if actual_names != expected_names:
        raise SystemExit(
            f"Zenodo {phase} file set mismatch "
            f"missing={sorted(expected_names-actual_names)} "
            f"extra={sorted(actual_names-expected_names)}"
        )
    for name in sorted(expected_names):
        inv = inventory[name]
        row = by_name[name]
        size = int(row.get("filesize") or row.get("size") or -1)
        if size != inv["bytes"]:
            raise SystemExit(
                f"Zenodo {phase} size mismatch {name}: {size}/{inv['bytes']}"
            )
        checksum = normalize_md5(row.get("checksum"))
        if not checksum:
            raise SystemExit(f"Zenodo {phase} checksum missing for {name}")
        if checksum != inv["md5"]:
            raise SystemExit(
                f"Zenodo {phase} MD5 mismatch {name}: {checksum}/{inv['md5']}"
            )
        print(
            f"[ZENODO REMOTE VERIFIED] phase={phase} name={name} "
            f"bytes={size} md5={checksum}",
            flush=True,
        )
    return by_name


def get_download_link(row: dict[str, Any]) -> str:
    links = row.get("links", {}) if isinstance(row.get("links"), dict) else {}
    link = links.get("download") or links.get("content") or links.get("self")
    if not link:
        raise SystemExit(f"no Zenodo download URL for {base.get_remote_name(row)}")
    return str(link)


def get_public_record(client: base.Client, record_id: int) -> dict[str, Any]:
    for attempt in range(1, 11):
        record = client.request("GET", f"/records/{record_id}", allow_404=True)
        if record:
            return record
        print(
            f"[ZENODO] public_record_not_ready id={record_id} attempt={attempt}",
            flush=True,
        )
        time.sleep(min(attempt * 2, 10))
    raise SystemExit(f"published Zenodo record {record_id} did not become readable")


def resolve_doi(*rows: dict[str, Any]) -> str | None:
    for row in rows:
        if not isinstance(row, dict):
            continue
        candidates = [
            row.get("doi"),
            row.get("metadata", {}).get("doi")
            if isinstance(row.get("metadata"), dict)
            else None,
            row.get("pids", {}).get("doi", {}).get("identifier")
            if isinstance(row.get("pids"), dict)
            else None,
            row.get("metadata", {}).get("prereserve_doi", {}).get("doi")
            if isinstance(row.get("metadata"), dict)
            and isinstance(row.get("metadata", {}).get("prereserve_doi"), dict)
            else None,
        ]
        for candidate in candidates:
            if candidate:
                return str(candidate)
    return None


def resolve_concept_doi(*rows: dict[str, Any]) -> str | None:
    for row in rows:
        if not isinstance(row, dict):
            continue
        for candidate in (
            row.get("conceptdoi"),
            row.get("metadata", {}).get("conceptdoi")
            if isinstance(row.get("metadata"), dict)
            else None,
        ):
            if candidate:
                return str(candidate)
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--state-file", required=True)
    parser.add_argument(
        "--api-base",
        default=os.environ.get("ZENODO_API_BASE", base.DEFAULT_API),
    )
    args = parser.parse_args()

    source = pathlib.Path(args.source_dir).resolve()
    state_file = pathlib.Path(args.state_file).resolve()
    if not source.is_dir():
        raise SystemExit(f"source directory missing: {source}")

    inventory = base.verify_source(source)
    client = base.Client(os.environ.get("ZENODO_ACCESS_TOKEN", ""), args.api_base)

    deposition = client.request(
        "GET", f"/deposit/depositions/{DEPOSITION_ID}", allow_404=True
    )
    publish_response: dict[str, Any] = {}

    if deposition and deposition.get("submitted") is not True:
        title = deposition.get("metadata", {}).get("title")
        if title != base.TITLE:
            raise SystemExit(
                f"refusing to publish deposition {DEPOSITION_ID}: "
                f"title={title!r} expected={base.TITLE!r}"
            )

        # Re-apply intended metadata, then verify the exact already-uploaded
        # bytes through Zenodo's size + MD5 inventory before publication.
        deposition = client.request(
            "PUT",
            f"/deposit/depositions/{DEPOSITION_ID}",
            {"metadata": base.metadata()},
        )
        verify_remote_rows(
            deposition.get("files", []), inventory, phase="draft-prepublish"
        )
        print(
            f"[ZENODO] prior_full_sha256_readback_proof "
            f"run_id={PRIOR_RUN_ID} deposition_id={DEPOSITION_ID} files=14",
            flush=True,
        )
        publish_response = client.request(
            "POST",
            f"/deposit/depositions/{DEPOSITION_ID}/actions/publish",
        )
        print(
            f"[ZENODO] publish_request_ok deposition_id={DEPOSITION_ID}",
            flush=True,
        )
    elif deposition and deposition.get("submitted") is True:
        title = deposition.get("metadata", {}).get("title")
        if title and title != base.TITLE:
            raise SystemExit(
                f"published deposition title mismatch: {title!r}/{base.TITLE!r}"
            )
        print(
            f"[ZENODO] deposition_already_submitted id={DEPOSITION_ID}",
            flush=True,
        )
    else:
        # Once published, some Zenodo API shapes may no longer expose the
        # deposition endpoint. Continue only if the public record exists and
        # matches exactly; otherwise fail closed instead of creating a new DOI.
        print(
            f"[ZENODO] deposition_endpoint_absent id={DEPOSITION_ID}; "
            "checking public record",
            flush=True,
        )

    record = get_public_record(client, DEPOSITION_ID)
    record_title = (
        record.get("metadata", {}).get("title")
        if isinstance(record.get("metadata"), dict)
        else None
    )
    if record_title != base.TITLE:
        raise SystemExit(
            f"public record title mismatch: {record_title!r}/{base.TITLE!r}"
        )

    public_rows = verify_remote_rows(
        record.get("files", []), inventory, phase="published"
    )

    # Strong terminal criterion: download every public Zenodo object and
    # recompute SHA-256 against the exact GitHub Release bytes.
    for name in sorted(base.EXPECTED):
        client.full_readback(
            get_download_link(public_rows[name]),
            source / name,
            "postpublish-public",
        )

    doi = resolve_doi(record, publish_response, deposition or {})
    if not doi:
        raise SystemExit("publication verified but DOI could not be resolved")
    if doi != f"10.5281/zenodo.{DEPOSITION_ID}":
        raise SystemExit(
            f"unexpected DOI for locked deposition: {doi}/10.5281/zenodo.{DEPOSITION_ID}"
        )

    concept_doi = resolve_concept_doi(record, publish_response, deposition or {})
    state = {
        "schema": "trinity-accord/second-star-moon-zenodo-state/v1",
        "updated_at": base.now(),
        "title": base.TITLE,
        "source_release_tag": base.RELEASE_TAG,
        "source_release_url": base.RELEASE_URL,
        "record_id": DEPOSITION_ID,
        "deposition_id": DEPOSITION_ID,
        "doi": doi,
        "concept_doi": concept_doi,
        "public_record_url": f"https://zenodo.org/records/{DEPOSITION_ID}",
        "public_record_api": f"https://zenodo.org/api/records/{DEPOSITION_ID}",
        "verified_file_count": len(inventory),
        "verified_total_bytes": sum(row["bytes"] for row in inventory.values()),
        "prior_prepublish_full_readback_run_id": PRIOR_RUN_ID,
        "remote_full_readback_sha256_verified": True,
        "source_inventory": inventory,
    }
    base.write_json(state_file, state)
    print(
        "ZENODO_RESULT="
        + json.dumps(
            {
                "record_id": DEPOSITION_ID,
                "doi": doi,
                "concept_doi": concept_doi,
                "files": len(inventory),
                "bytes": state["verified_total_bytes"],
                "public_sha256_readback": True,
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
