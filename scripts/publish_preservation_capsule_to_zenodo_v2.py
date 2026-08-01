#!/usr/bin/env python3
"""Publish the repository capsule with draft-safe Zenodo byte readback.

The original publisher validates every uploaded byte before irreversible publication,
but Zenodo draft objects can expose a public ``download`` link that returns 404 until
the deposition is published. This compatibility layer keeps the original publisher's
state/reconciliation logic and replaces only remote byte verification:

* unpublished drafts are read back from their authenticated upload bucket first;
* alternate authenticated file links are tried without weakening size/hash checks;
* published records receive bounded retries for short post-publication 404 windows;
* the workflow still performs an independent, unauthenticated DOI-only cold restore.
"""
from __future__ import annotations

import hashlib
import sys
import time
import urllib.parse
from pathlib import Path
from typing import Any, Callable, Iterable

import publish_preservation_capsule_to_zenodo as publisher


def _deduplicate(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value and value not in seen:
            result.append(value)
            seen.add(value)
    return result


def remote_download_candidates(
    record: dict[str, Any], item: dict[str, Any], name: str
) -> list[str]:
    """Return authenticated byte endpoints in state-appropriate order."""
    item_links = item.get("links")
    links = item_links if isinstance(item_links, dict) else {}
    record_links = record.get("links")
    deposition_links = record_links if isinstance(record_links, dict) else {}
    bucket = deposition_links.get("bucket")
    bucket_object = (
        str(bucket).rstrip("/") + "/" + urllib.parse.quote(name)
        if isinstance(bucket, str) and bucket
        else ""
    )

    self_link = str(links.get("self") or "")
    version_link = str(links.get("version") or "")
    content_link = str(links.get("content") or "")
    download_link = str(links.get("download") or "")

    if publisher.is_published(record):
        candidates = [download_link, content_link, self_link, version_link, bucket_object]
    else:
        # A draft's public download URL can legitimately be 404 before publish.
        candidates = [bucket_object, self_link, version_link, content_link, download_link]
    return _deduplicate(candidates)


def download_verified_bytes(
    client: publisher.ZenodoClient,
    candidates: Iterable[str],
    *,
    expected_size: int,
    expected_sha256: str,
    name: str,
    attempts: int,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> bytes:
    """Read one exact file from the first working endpoint, with bounded retries."""
    urls = _deduplicate(candidates)
    if not urls:
        raise SystemExit(f"Zenodo remote byte URL is missing: {name}")

    diagnostics: list[str] = []
    for attempt in range(1, attempts + 1):
        for url in urls:
            try:
                raw = client.request_bytes(url)
            except SystemExit as exc:
                diagnostics.append(f"{url}: {exc}")
                continue
            if len(raw) != expected_size:
                diagnostics.append(
                    f"{url}: downloaded {len(raw)} bytes, expected {expected_size}"
                )
                continue
            digest = hashlib.sha256(raw).hexdigest()
            if digest != expected_sha256:
                diagnostics.append(
                    f"{url}: sha256 {digest}, expected {expected_sha256}"
                )
                continue
            return raw
        if attempt < attempts:
            sleep_fn(float(min(2 * attempt, 10)))

    detail = " | ".join(diagnostics[-12:])
    raise SystemExit(
        f"Zenodo exact byte readback failed after {attempts} attempt(s): {name}: {detail}"
    )


def verify_remote_files(
    client: publisher.ZenodoClient,
    record: dict[str, Any],
    capsule_dir: Path,
) -> dict[str, dict[str, Any]]:
    """Verify the exact remote set, metadata checksums, and downloaded bytes."""
    local = publisher.file_inventory(capsule_dir)
    remote_files = record.get("files")
    if not isinstance(remote_files, list):
        raise SystemExit("Zenodo record files list is missing")
    remote = {
        publisher.remote_name(item): item
        for item in remote_files
        if isinstance(item, dict) and publisher.remote_name(item)
    }
    expected_names = set(publisher.PUBLISHED_FILE_NAMES)
    if set(remote) != expected_names:
        raise SystemExit(
            "Zenodo preservation file set mismatch: "
            f"missing={sorted(expected_names - set(remote))} "
            f"unexpected={sorted(set(remote) - expected_names)}"
        )

    published = publisher.is_published(record)
    for name in publisher.PUBLISHED_FILE_NAMES:
        item = remote[name]
        if publisher.remote_size(item) != local[name]["bytes"]:
            raise SystemExit(f"Zenodo remote size mismatch: {name}")
        checksum = str(item.get("checksum") or "")
        if checksum.split(":", 1)[-1].lower() != local[name]["md5"]:
            raise SystemExit(f"Zenodo remote checksum mismatch: {name}")
        download_verified_bytes(
            client,
            remote_download_candidates(record, item, name),
            expected_size=local[name]["bytes"],
            expected_sha256=local[name]["sha256"],
            name=name,
            attempts=8 if published else 3,
        )
    return local


def main() -> int:
    publisher.verify_remote_files = verify_remote_files
    return publisher.main()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        raise SystemExit(130)
