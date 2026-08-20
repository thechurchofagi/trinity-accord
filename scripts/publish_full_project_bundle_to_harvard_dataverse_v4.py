#!/usr/bin/env python3
"""Harvard publisher v4: authenticate Dataverse multipart control calls.

Inherits verifier compatibility and empty-draft resume logic from v3. Harvard's
current deployment requires X-Dataverse-key on the returned multipart complete
(and abort) Dataverse URIs, even though older generic examples omit it.
"""
from __future__ import annotations

import json
import urllib.parse
from typing import Iterable

import publish_full_project_bundle_to_harvard_dataverse_v3 as v3

impl = v3.impl


def direct_upload_archive(client, token, pid, archive, sha256, progress) -> bool:
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
                headers={"Content-Length": str(size), "User-Agent": impl.USER_AGENT},
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
                    impl.log(f"multipart_part PASS part={number} bytes={len(chunk)} progress={progress.done}/{size}")
            complete = data.get("complete")
            if not complete:
                raise impl.PublishError("multipart direct-upload response has no complete URL")
            complete_url = urllib.parse.urljoin(impl.SERVER + "/", str(complete).lstrip("/"))
            finished = client.put(
                complete_url,
                headers=impl.hd_headers(token),
                json=etags,
                timeout=120,
            )
            impl.require_status(finished, range(200, 300), "Harvard multipart completion")
            impl.log(f"multipart_complete PASS parts={len(etags)}")
        else:
            return False
    except Exception:
        abort = data.get("abort")
        if abort:
            try:
                abort_url = urllib.parse.urljoin(impl.SERVER + "/", str(abort).lstrip("/"))
                aborted = client.delete(abort_url, headers=impl.hd_headers(token), timeout=30)
                impl.log(f"multipart_abort attempted HTTP={aborted.status_code}")
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


impl.direct_upload_archive = direct_upload_archive


if __name__ == "__main__":
    try:
        raise SystemExit(impl.main())
    except Exception as exc:
        impl.log(f"FAIL {type(exc).__name__}: {exc}")
        raise
