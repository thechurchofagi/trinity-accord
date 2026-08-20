#!/usr/bin/env python3
"""Harvard publisher v3: resume the created draft and honor returned presigned URLs.

Fixes two fail-closed integration findings:
1. verifier report compatibility is inherited from v2 (`result: pass`);
2. Harvard's returned multipart presigned URLs reject an unsiged x-amz-tagging header.

The existing draft PID can be supplied with HARVARD_RESUME_PID.  It is reused
only when it is still a DRAFT and contains no files, preventing duplicate
Dataset creation after a pre-upload failure.
"""
from __future__ import annotations

import json
import os
import urllib.parse
from typing import Any, Iterable

import publish_full_project_bundle_to_harvard_dataverse_v2 as v2

impl = v2.impl
_orig_create_dataset = impl.create_dataset


def create_dataset(client, token: str, metadata: dict[str, Any]) -> tuple[int, str]:
    pid = os.environ.get("HARVARD_RESUME_PID", "").strip()
    if not pid:
        return _orig_create_dataset(client, token, metadata)

    response = client.get(
        f"{impl.SERVER}/api/datasets/:persistentId/",
        headers=impl.hd_headers(token),
        params={"persistentId": pid},
    )
    payload = impl.json_response(response, (200,), "Harvard resume Dataset lookup")
    data = payload.get("data", {})
    latest = data.get("latestVersion", {})
    state = latest.get("versionState")
    files = latest.get("files", [])
    if state != "DRAFT":
        raise impl.PublishError(f"resume Dataset {pid} is not DRAFT: {state!r}")
    if files:
        raise impl.PublishError(
            f"resume Dataset {pid} unexpectedly already contains {len(files)} file(s)"
        )
    dataset_id = data.get("id")
    if dataset_id is None:
        raise impl.PublishError(f"resume Dataset {pid} response has no dataset id")
    impl.log(f"dataset_resume PASS dataset_id={dataset_id} persistent_id={pid} files=0")
    return int(dataset_id), pid


def direct_upload_archive(
    client,
    token: str,
    pid: str,
    archive,
    sha256: str,
    progress,
) -> bool:
    size = archive.stat().st_size
    response = client.get(
        f"{impl.SERVER}/api/datasets/:persistentId/uploadurls",
        headers=impl.hd_headers(token),
        params={"persistentId": pid, "size": size},
    )
    if response.status_code != 200:
        impl.log(f"direct upload unavailable HTTP={response.status_code}; falling back to Native API")
        return False
    payload = response.json()
    data = payload.get("data", {}) if isinstance(payload, dict) else {}
    storage = data.get("storageIdentifier")
    if not storage:
        impl.log("direct upload response lacks storageIdentifier; falling back to Native API")
        return False

    progress.stage = "harvard_direct_upload"
    progress.done = 0
    progress.total = size
    progress.detail = f"dataset={pid}"
    try:
        if data.get("url"):
            def body() -> Iterable[bytes]:
                with archive.open("rb") as fh:
                    while True:
                        chunk = fh.read(impl.CHUNK)
                        if not chunk:
                            break
                        progress.done += len(chunk)
                        yield chunk

            uploaded = client.put(
                str(data["url"]),
                headers={
                    "Content-Length": str(size),
                    "User-Agent": impl.USER_AGENT,
                },
                content=body(),
                timeout=300,
            )
            impl.require_status(uploaded, range(200, 300), "Harvard S3 direct upload")
        elif data.get("urls"):
            part_size = int(data["partSize"])
            etags: dict[str, str] = {}
            with archive.open("rb") as fh:
                for number, part_url in sorted(data["urls"].items(), key=lambda kv: int(kv[0])):
                    chunk = fh.read(part_size)
                    if not chunk:
                        raise impl.PublishError(f"multipart upload ran out of bytes at part {number}")
                    uploaded = client.put(
                        str(part_url),
                        headers={"User-Agent": impl.USER_AGENT},
                        content=chunk,
                        timeout=300,
                    )
                    impl.require_status(uploaded, range(200, 300), f"Harvard multipart part {number}")
                    etag = uploaded.headers.get("ETag")
                    if not etag:
                        raise impl.PublishError(f"multipart part {number} returned no ETag")
                    etags[str(number)] = etag
                    progress.done += len(chunk)
                    impl.log(
                        f"multipart_part PASS part={number} bytes={len(chunk)} "
                        f"progress={progress.done}/{size}"
                    )
            complete = data.get("complete")
            if not complete:
                raise impl.PublishError("multipart direct-upload response has no complete URL")
            complete_url = urllib.parse.urljoin(impl.SERVER + "/", str(complete).lstrip("/"))
            finished = client.put(complete_url, json=etags, timeout=120)
            impl.require_status(finished, range(200, 300), "Harvard multipart completion")
            impl.log(f"multipart_complete PASS parts={len(etags)}")
        else:
            return False
    except Exception:
        abort = data.get("abort")
        if abort:
            try:
                abort_url = urllib.parse.urljoin(impl.SERVER + "/", str(abort).lstrip("/"))
                client.delete(abort_url, timeout=30)
                impl.log("multipart_abort attempted after upload failure")
            except Exception:
                pass
        raise

    file_meta = {
        "description": "Exact opaque GitHub Actions artifact bytes for the full Trinity Accord preservation bundle.",
        "categories": ["Data"],
        "restrict": "false",
        "storageIdentifier": storage,
        "fileName": impl.ARCHIVE_NAME,
        "mimeType": "application/octet-stream",
        "fileSize": size,
        "checksum": {"@type": "SHA-256", "@value": sha256},
    }
    registered = client.post(
        f"{impl.SERVER}/api/datasets/:persistentId/add",
        headers=impl.hd_headers(token),
        params={"persistentId": pid},
        files={"jsonData": (None, json.dumps(file_meta, separators=(",", ":")))},
    )
    impl.json_response(registered, (200, 201), "Harvard register direct-upload file")
    return True


impl.create_dataset = create_dataset
impl.direct_upload_archive = direct_upload_archive


if __name__ == "__main__":
    try:
        raise SystemExit(impl.main())
    except Exception as exc:
        impl.log(f"FAIL {type(exc).__name__}: {exc}")
        raise
