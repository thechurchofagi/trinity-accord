#!/usr/bin/env python3
"""Publish a reproducible capsule with fail-closed Zenodo draft replacement.

This compatibility layer addresses two deposition behaviors without weakening
publication verification:

* deleting draft files and immediately uploading replacements can expose stale
  file metadata for a short interval;
* draft file bytes are reliably readable from the authenticated upload bucket,
  while public record links are authoritative only after publication.

The workflow therefore waits for an empty draft, verifies every PUT response
when fields are available, reads every uploaded object back from the bucket by
exact SHA-256, tolerates metadata lag only while the deposition is unpublished,
and requires exact published metadata plus public byte recovery before state is
recorded as ``published``.
"""
from __future__ import annotations

import sys
import time
import urllib.parse
from pathlib import Path
from typing import Any

import publish_preservation_capsule_to_zenodo as publisher
from publish_preservation_capsule_to_zenodo_v2 import (
    download_verified_bytes,
    remote_download_candidates,
)


ORIGINAL_CLEAR_FILES = publisher.clear_files


def remote_map(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    files = record.get("files")
    if not isinstance(files, list):
        raise SystemExit("Zenodo record files list is missing")
    result = {
        publisher.remote_name(item): item
        for item in files
        if isinstance(item, dict) and publisher.remote_name(item)
    }
    expected = set(publisher.PUBLISHED_FILE_NAMES)
    if set(result) != expected:
        raise SystemExit(
            "Zenodo preservation file set mismatch: "
            f"missing={sorted(expected - set(result))} "
            f"unexpected={sorted(set(result) - expected)}"
        )
    return result


def metadata_errors(
    remote: dict[str, dict[str, Any]], local: dict[str, dict[str, Any]]
) -> list[str]:
    errors: list[str] = []
    for name in publisher.PUBLISHED_FILE_NAMES:
        item = remote[name]
        observed_size = publisher.remote_size(item)
        expected_size = int(local[name]["bytes"])
        if observed_size != expected_size:
            errors.append(f"{name}:size={observed_size},expected={expected_size}")
        checksum = str(item.get("checksum") or "")
        observed_md5 = checksum.split(":", 1)[-1].lower() if checksum else ""
        expected_md5 = str(local[name]["md5"])
        if observed_md5 != expected_md5:
            errors.append(
                f"{name}:md5={observed_md5 or 'missing'},expected={expected_md5}"
            )
    return errors


def verify_exact_remote_bytes(
    client: publisher.ZenodoClient,
    record: dict[str, Any],
    remote: dict[str, dict[str, Any]],
    local: dict[str, dict[str, Any]],
) -> None:
    published = publisher.is_published(record)
    for name in publisher.PUBLISHED_FILE_NAMES:
        download_verified_bytes(
            client,
            remote_download_candidates(record, remote[name], name),
            expected_size=int(local[name]["bytes"]),
            expected_sha256=str(local[name]["sha256"]),
            name=name,
            attempts=10 if published else 4,
        )


def clear_files(client: publisher.ZenodoClient, draft: dict[str, Any]) -> None:
    """Delete the old set and wait until the deposition reports an empty bucket."""
    ORIGINAL_CLEAR_FILES(client, draft)
    current = draft
    for attempt in range(1, 16):
        current = publisher.refresh(client, current)
        files = current.get("files")
        if isinstance(files, list) and not files:
            return
        if attempt < 15:
            time.sleep(float(min(attempt, 3)))
    remaining = current.get("files")
    count = len(remaining) if isinstance(remaining, list) else "unknown"
    raise SystemExit(f"Zenodo draft did not become empty after deletion: remaining={count}")


def upload_files(
    client: publisher.ZenodoClient, draft: dict[str, Any], capsule_dir: Path
) -> None:
    """Upload each file and authenticate its exact bucket bytes immediately."""
    links = draft.get("links")
    bucket = links.get("bucket") if isinstance(links, dict) else None
    if not isinstance(bucket, str) or not bucket:
        raise SystemExit("Zenodo draft is missing upload bucket")

    local = publisher.file_inventory(capsule_dir)
    for name in publisher.PUBLISHED_FILE_NAMES:
        url = bucket.rstrip("/") + "/" + urllib.parse.quote(name)
        response = client.request(
            "PUT",
            url,
            data=(capsule_dir / name).read_bytes(),
            content_type="application/octet-stream",
        )
        if isinstance(response, dict):
            response_size = publisher.remote_size(response)
            if response_size is not None and response_size != local[name]["bytes"]:
                raise SystemExit(
                    f"Zenodo upload response size mismatch: {name}: "
                    f"observed={response_size} expected={local[name]['bytes']}"
                )
            response_checksum = str(response.get("checksum") or "")
            if response_checksum:
                observed_md5 = response_checksum.split(":", 1)[-1].lower()
                if observed_md5 != local[name]["md5"]:
                    raise SystemExit(f"Zenodo upload response checksum mismatch: {name}")
        download_verified_bytes(
            client,
            [url],
            expected_size=int(local[name]["bytes"]),
            expected_sha256=str(local[name]["sha256"]),
            name=name,
            attempts=5,
        )

    current = draft
    for attempt in range(1, 16):
        current = publisher.refresh(client, current)
        files = current.get("files")
        names = (
            {
                publisher.remote_name(item)
                for item in files
                if isinstance(item, dict) and publisher.remote_name(item)
            }
            if isinstance(files, list)
            else set()
        )
        if names == set(publisher.PUBLISHED_FILE_NAMES):
            return
        if attempt < 15:
            time.sleep(float(min(attempt, 3)))
    raise SystemExit("Zenodo draft did not expose the complete uploaded file set")


def verify_remote_files(
    client: publisher.ZenodoClient,
    record: dict[str, Any],
    capsule_dir: Path,
) -> dict[str, dict[str, Any]]:
    """Require exact bytes always and exact metadata after publication."""
    local = publisher.file_inventory(capsule_dir)
    current = record
    remote = remote_map(current)
    verify_exact_remote_bytes(client, current, remote, local)

    errors = metadata_errors(remote, local)
    if not errors:
        return local

    if not publisher.is_published(current):
        for attempt in range(1, 6):
            if attempt > 1:
                time.sleep(float(min(attempt, 3)))
            current = publisher.refresh(client, current)
            remote = remote_map(current)
            errors = metadata_errors(remote, local)
            if not errors:
                return local
        print(
            "Zenodo draft metadata is lagging exact authenticated bucket bytes: "
            + " | ".join(errors),
            file=sys.stderr,
        )
        return local

    for attempt in range(1, 16):
        if attempt > 1:
            time.sleep(float(min(attempt, 5)))
        current = publisher.refresh(client, current)
        remote = remote_map(current)
        errors = metadata_errors(remote, local)
        if not errors:
            verify_exact_remote_bytes(client, current, remote, local)
            return local
    raise SystemExit(
        "Zenodo published metadata did not converge to exact file identities: "
        + " | ".join(errors)
    )


def main() -> int:
    publisher.clear_files = clear_files
    publisher.upload_files = upload_files
    publisher.verify_remote_files = verify_remote_files
    return publisher.main()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        raise SystemExit(130)
