#!/usr/bin/env python3
"""Fail-closed, resumable Harvard Dataverse uploader for Preservation Epoch II.

This program is deliberately pinned to the one authorized Epoch II draft.  It
never creates a Dataset, edits metadata, deletes files, publishes a version, or
touches Preservation Epoch I.  Upload commands are permitted only while the
target is DRAFT.  The final command submits once, only after exact file and
readback receipts prove the frozen 419-file layout.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
from dataclasses import dataclass
from typing import Any, Iterable, Iterator

import httpx


SERVER = "https://dataverse.harvard.edu"
PID = "doi:10.7910/DVN/W9Y3IV"
DATASET_ID = 14229992
TITLE = "Trinity Accord — Research Corpus and Preservation Mirror · Preservation Epoch II"
SOURCE_SHA = "3bdf9121fb9e98cd9ba9de62a2466367d0968e4e"
OLD_PID = "doi:10.7910/DVN/YUCG12"
MANIFEST_SHA256 = "24212072367bdcdd5d550c379433b10bdefe0366f9bec3ddc10ea81e6fadbcad"
SUMS_SHA256 = "fbf5a3cc784683a595c6bb4d2869b209d786029dee184d19be56e0df7039f705"
CANDIDATE_ID = "cd0bd263f548d23060422021408ab1705e8c48c1c1028f1a440eb89d1e88d7e8"
LAYOUT_ID = "938c6d9f3df75853e31821a1fc8b23f0f06ec235ff6408a104ebd91e6e4381e4"
PLANNED_FILES = 419
PLANNED_PAYLOAD_BYTES = 23_107_006_729
CHUNK = 8 * 1024 * 1024
USER_AGENT = "trinity-accord-epoch-ii-uploader/1.0"
HEX64 = set("0123456789abcdef")


class UploadError(RuntimeError):
    pass


def log(message: str) -> None:
    print(f"[harvard-epoch-ii] {message}", flush=True)


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def headers(token: str) -> dict[str, str]:
    return {"X-Dataverse-key": token, "User-Agent": USER_AGENT}


def require_status(response: httpx.Response, expected: Iterable[int], label: str) -> None:
    if response.status_code not in set(expected):
        raise UploadError(f"{label}: HTTP {response.status_code}: {response.text[:4000]}")


def json_response(response: httpx.Response, expected: Iterable[int], label: str) -> dict[str, Any]:
    require_status(response, expected, label)
    try:
        value = response.json()
    except ValueError as exc:
        raise UploadError(f"{label}: non-JSON response") from exc
    if not isinstance(value, dict) or value.get("status") == "ERROR":
        raise UploadError(f"{label}: invalid/error response: {value}")
    return value


def request_retry(client: httpx.Client, method: str, url: str, *, label: str,
                  attempts: int = 5, **kwargs: Any) -> httpx.Response:
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            response = client.request(method, url, **kwargs)
            if response.status_code not in {408, 425, 429, 500, 502, 503, 504}:
                return response
            last = UploadError(f"{label}: transient HTTP {response.status_code}")
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            last = exc
        if attempt < attempts:
            delay = min(2 ** attempt, 20)
            log(f"retry label={label!r} attempt={attempt}/{attempts} delay={delay}s error={last}")
            time.sleep(delay)
    raise UploadError(f"{label}: exhausted retries: {last}")


def s3_upload_headers(url: str, content_length: int) -> dict[str, str]:
    """Return exactly the headers covered by Harvard's S3 signature.

    Harvard currently signs ``x-amz-tagging`` and the Dataverse direct-upload
    contract requires ``dv-state=temp`` in that case.  Other installations can
    disable tagging, so the header must be derived from SignedHeaders rather
    than sent unconditionally.
    """
    query = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    signed = ";".join(query.get("X-Amz-SignedHeaders", query.get("x-amz-signedheaders", []))).lower()
    result = {"Content-Length": str(content_length), "User-Agent": USER_AGENT}
    if "x-amz-tagging" in signed.split(";"):
        result["x-amz-tagging"] = "dv-state=temp"
    return result


def dataset_snapshot(client: httpx.Client, token: str) -> tuple[dict[str, Any], dict[str, Any]]:
    response = request_retry(
        client, "GET", f"{SERVER}/api/datasets/:persistentId/",
        label="Dataset lookup", headers=headers(token), params={"persistentId": PID}, timeout=120,
    )
    data = json_response(response, (200,), "Dataset lookup").get("data", {})
    if int(data.get("id") or -1) != DATASET_ID:
        raise UploadError(f"target Dataset ID drift: {data.get('id')!r}")
    if str(data.get("persistentUrl") or "").rstrip("/").split("doi.org/")[-1] not in {PID, PID.removeprefix("doi:")}:
        persistent_id = str(data.get("protocol") or "") + ":" + str(data.get("authority") or "") + "/" + str(data.get("identifier") or "")
        if persistent_id != PID:
            raise UploadError(f"target PID drift: {persistent_id!r}")
    latest = data.get("latestVersion") or {}
    citation_fields = latest.get("metadataBlocks", {}).get("citation", {}).get("fields", [])
    title = next(
        (str(field.get("value") or "") for field in citation_fields if field.get("typeName") == "title"),
        "",
    )
    if title and title != TITLE:
        raise UploadError(f"target title drift: {title!r}")
    return data, latest


def state_of(latest: dict[str, Any]) -> str:
    return str(latest.get("versionState") or "")


def dataset_locks(client: httpx.Client, token: str) -> list[dict[str, Any]]:
    response = request_retry(
        client,
        "GET",
        f"{SERVER}/api/datasets/{DATASET_ID}/locks",
        label="Dataset locks lookup",
        headers=headers(token),
        timeout=120,
    )
    value = json_response(response, (200,), "Dataset locks lookup").get("data") or []
    if not isinstance(value, list):
        raise UploadError("Dataset locks response is not a list")
    return value


def effective_state(client: httpx.Client, token: str, latest: dict[str, Any]) -> str:
    version_state = state_of(latest)
    if version_state == "RELEASED":
        return version_state
    if any(str(lock.get("lockType") or "") == "InReview" for lock in dataset_locks(client, token)):
        return "InReview"
    return version_state


def normalize_checksum(value: Any) -> tuple[str, str]:
    if not isinstance(value, dict):
        return "", ""
    kind = str(value.get("type") or value.get("@type") or "").upper().replace("_", "-")
    digest = str(value.get("value") or value.get("@value") or "").lower()
    return kind, digest


def file_key(directory: str, filename: str) -> str:
    return f"{directory}/{filename}" if directory else filename


def dataverse_files(latest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in latest.get("files") or []:
        data_file = item.get("dataFile") or {}
        key = file_key(str(item.get("directoryLabel") or ""), str(data_file.get("filename") or ""))
        if not key or key in result:
            raise UploadError(f"empty or duplicate Dataverse logical path: {key!r}")
        result[key] = item
    return result


def validate_manifest(manifest_path: pathlib.Path, sums_path: pathlib.Path) -> dict[str, Any]:
    if sha256_file(manifest_path) != MANIFEST_SHA256:
        raise UploadError("frozen DATASET-MANIFEST.json digest drift")
    if sha256_file(sums_path) != SUMS_SHA256:
        raise UploadError("frozen Harvard SHA256SUMS digest drift")
    manifest = load_json(manifest_path)
    checks = {
        "source_git_commit_sha": SOURCE_SHA,
        "candidate_identity_sha256": CANDIDATE_ID,
        "layout_identity_sha256": LAYOUT_ID,
        "old_harvard_doi_unchanged": OLD_PID.removeprefix("doi:"),
        "file_count": 417,
        "planned_harvard_file_count": PLANNED_FILES,
        "total_bytes": PLANNED_PAYLOAD_BYTES,
    }
    for key, expected in checks.items():
        if manifest.get(key) != expected:
            raise UploadError(f"manifest contract drift {key}: {manifest.get(key)!r} != {expected!r}")
    rows = manifest.get("files") or []
    if len(rows) != 417:
        raise UploadError(f"manifest row count drift: {len(rows)}")
    keys: set[str] = set()
    for row in rows:
        key = file_key(str(row["directory_label"]), str(row["filename"]))
        digest = str(row.get("sha256") or "").lower()
        if key in keys or len(digest) != 64 or any(ch not in HEX64 for ch in digest):
            raise UploadError(f"invalid or duplicate manifest row: {key}")
        keys.add(key)
    parsed_sums: dict[str, str] = {}
    for line in sums_path.read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        parsed_sums[name] = digest
    if parsed_sums != {file_key(str(r["directory_label"]), str(r["filename"])): str(r["sha256"]) for r in rows}:
        raise UploadError("frozen manifest and SHA256SUMS disagree")
    return manifest


def control_rows(manifest_path: pathlib.Path, sums_path: pathlib.Path) -> list[dict[str, Any]]:
    return [
        {"directory_label": "00-start-here", "filename": "DATASET-MANIFEST.json",
         "bytes": manifest_path.stat().st_size, "sha256": MANIFEST_SHA256,
         "source_kind": "control", "source_locator": str(manifest_path)},
        {"directory_label": "00-start-here", "filename": "SHA256SUMS",
         "bytes": sums_path.stat().st_size, "sha256": SUMS_SHA256,
         "source_kind": "control", "source_locator": str(sums_path)},
    ]


def verify_local(path: pathlib.Path, row: dict[str, Any]) -> None:
    actual_size = path.stat().st_size
    if actual_size != int(row["bytes"]):
        raise UploadError(f"source size mismatch {path}: {actual_size} != {row['bytes']}")
    actual_sha = sha256_file(path)
    if actual_sha != str(row["sha256"]):
        raise UploadError(f"source SHA-256 mismatch {path}: {actual_sha} != {row['sha256']}")


def materialize_repository_row(source_repo: pathlib.Path, row: dict[str, Any], target: pathlib.Path) -> None:
    source = str(row["source_locator"])
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as output:
        result = subprocess.run(
            ["git", "-C", str(source_repo), "show", f"{SOURCE_SHA}:{source}"],
            stdout=output, stderr=subprocess.PIPE,
        )
    if result.returncode:
        raise UploadError(f"git show failed for {source}: {result.stderr.decode(errors='replace')}")


def download_release(client: httpx.Client, row: dict[str, Any], target: pathlib.Path) -> None:
    url = str(row["source_locator"])
    if not url.startswith("https://github.com/thechurchofagi/trinity-accord/releases/download/"):
        raise UploadError(f"unapproved Release URL: {url}")
    target.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(1, 6):
        digest = hashlib.sha256()
        size = 0
        try:
            with client.stream("GET", url, follow_redirects=True, timeout=900, headers={"User-Agent": USER_AGENT}) as response:
                require_status(response, (200,), f"download {row['filename']}")
                host = urllib.parse.urlparse(str(response.url)).hostname or ""
                if host not in {"github.com", "release-assets.githubusercontent.com"}:
                    raise UploadError(f"unexpected Release redirect host: {host}")
                with target.open("wb") as output:
                    for chunk in response.iter_bytes(CHUNK):
                        output.write(chunk)
                        digest.update(chunk)
                        size += len(chunk)
                        if size > int(row["bytes"]):
                            raise UploadError(f"download exceeded declared size: {row['filename']}")
            if size != int(row["bytes"]) or digest.hexdigest() != str(row["sha256"]):
                raise UploadError(f"download identity mismatch: {row['filename']} bytes={size} sha256={digest.hexdigest()}")
            return
        except (httpx.HTTPError, OSError, UploadError) as exc:
            target.unlink(missing_ok=True)
            if attempt == 5:
                raise UploadError(f"Release download failed after 5 attempts: {exc}") from exc
            time.sleep(min(2 ** attempt, 20))


def extract_datafile_id(value: Any) -> int | None:
    if isinstance(value, dict):
        if "dataFile" in value:
            found = extract_datafile_id(value["dataFile"])
            if found is not None:
                return found
        if "id" in value and any(k in value for k in ("filename", "filesize", "checksum", "storageIdentifier")):
            try:
                return int(value["id"])
            except (TypeError, ValueError):
                pass
        for child in value.values():
            found = extract_datafile_id(child)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = extract_datafile_id(child)
            if found is not None:
                return found
    return None


def direct_upload(client: httpx.Client, token: str, path: pathlib.Path, row: dict[str, Any]) -> int:
    size = int(row["bytes"])
    lookup = request_retry(
        client, "GET", f"{SERVER}/api/datasets/:persistentId/uploadurls",
        label=f"allocate {row['filename']}", headers=headers(token),
        params={"persistentId": PID, "size": size}, timeout=120,
    )
    payload = json_response(lookup, (200,), "direct-upload allocation")
    data = payload.get("data") or {}
    storage = str(data.get("storageIdentifier") or "")
    if not storage:
        raise UploadError("Harvard direct-upload response lacks storageIdentifier")
    try:
        if data.get("url"):
            def body() -> Iterator[bytes]:
                with path.open("rb") as handle:
                    for chunk in iter(lambda: handle.read(CHUNK), b""):
                        yield chunk
            last: Exception | None = None
            for attempt in range(1, 5):
                try:
                    response = client.put(
                        str(data["url"]),
                        headers=s3_upload_headers(str(data["url"]), size),
                        content=body(),
                        timeout=900,
                    )
                    require_status(response, range(200, 300), "single-part direct upload")
                    break
                except (httpx.HTTPError, UploadError) as exc:
                    last = exc
                    if attempt == 4:
                        raise UploadError(f"single-part upload exhausted retries: {last}") from exc
                    time.sleep(min(2 ** attempt, 20))
        elif data.get("urls"):
            etags: dict[str, str] = {}
            part_size = int(data["partSize"])
            bytes_sent = 0
            with path.open("rb") as handle:
                for number, url in sorted(data["urls"].items(), key=lambda pair: int(pair[0])):
                    chunk = handle.read(part_size)
                    if not chunk:
                        raise UploadError(f"multipart source ended before part {number}")
                    response = request_retry(
                        client, "PUT", str(url), label=f"upload {row['filename']} part {number}", attempts=4,
                        headers=s3_upload_headers(str(url), len(chunk)), content=chunk, timeout=900,
                    )
                    require_status(response, range(200, 300), f"multipart part {number}")
                    etag = response.headers.get("ETag")
                    if not etag:
                        raise UploadError(f"multipart part {number} returned no ETag")
                    etags[str(number)] = etag
                    bytes_sent += len(chunk)
            if bytes_sent != size:
                raise UploadError(f"multipart source byte count mismatch: {bytes_sent} != {size}")
            complete_value = str(data.get("complete") or "")
            if not complete_value:
                raise UploadError("multipart allocation lacks complete URL")
            complete = urllib.parse.urljoin(SERVER + "/", complete_value.lstrip("/"))
            response = request_retry(
                client, "PUT", complete, label=f"complete {row['filename']}", attempts=3,
                headers=headers(token), json=etags, timeout=180,
            )
            require_status(response, range(200, 300), "multipart completion")
        else:
            raise UploadError("Harvard direct-upload response has neither url nor urls")
    except Exception:
        abort = str(data.get("abort") or "")
        if abort:
            try:
                client.delete(urllib.parse.urljoin(SERVER + "/", abort.lstrip("/")), headers=headers(token), timeout=60)
            except Exception:
                pass
        raise

    # Preserve every object as opaque bytes.  In particular, declaring ZIP
    # media types can cause Dataverse to unpack them and destroy the frozen
    # one-file/one-digest layout.
    mime = "application/octet-stream"
    meta = {
        "description": (
            "Exact public Preservation Epoch II byte object. "
            f"SHA-256: {row['sha256']}. Source kind: {row['source_kind']}."
        ),
        "categories": ["Data"],
        "restrict": "false",
        "directoryLabel": str(row["directory_label"]),
        "storageIdentifier": storage,
        "fileName": str(row["filename"]),
        "mimeType": mime,
        "fileSize": size,
        "checksum": {"@type": "SHA-256", "@value": str(row["sha256"])},
    }
    try:
        response = client.post(
            f"{SERVER}/api/datasets/:persistentId/add", headers=headers(token),
            params={"persistentId": PID},
            files={"jsonData": (None, json.dumps(meta, ensure_ascii=False, separators=(",", ":")))},
            timeout=180,
        )
        payload = json_response(response, (200, 201), f"register {row['filename']}")
        datafile_id = extract_datafile_id(payload.get("data"))
    except (httpx.HTTPError, UploadError) as exc:
        # Registration is deliberately never retried blindly.  Resolve an
        # ambiguous response from the Dataset itself so duplicates cannot form.
        log(f"registration response ambiguous for {row['filename']}: {exc}; resolving from Dataset")
        _, latest = dataset_snapshot(client, token)
        item = dataverse_files(latest).get(file_key(str(row["directory_label"]), str(row["filename"])))
        datafile_id = int((item or {}).get("dataFile", {}).get("id") or 0) or None
        if datafile_id is None:
            raise
    if datafile_id is None:
        _, latest = dataset_snapshot(client, token)
        item = dataverse_files(latest).get(file_key(str(row["directory_label"]), str(row["filename"])))
        datafile_id = int((item or {}).get("dataFile", {}).get("id") or 0) or None
    if datafile_id is None:
        raise UploadError(f"registered file has no dataFile id: {row['filename']}")
    return datafile_id


def readback(client: httpx.Client, token: str, datafile_id: int, row: dict[str, Any]) -> None:
    digest = hashlib.sha256()
    size = 0
    url = f"{SERVER}/api/access/datafile/{datafile_id}"
    last: Exception | None = None
    for attempt in range(1, 6):
        digest = hashlib.sha256()
        size = 0
        try:
            with client.stream("GET", url, headers=headers(token), params={"format": "original"},
                               follow_redirects=True, timeout=900) as response:
                require_status(response, (200,), f"readback {row['filename']}")
                for chunk in response.iter_bytes(CHUNK):
                    digest.update(chunk)
                    size += len(chunk)
                    if size > int(row["bytes"]):
                        raise UploadError(f"readback exceeded expected size: {row['filename']}")
            if size == int(row["bytes"]) and digest.hexdigest() == str(row["sha256"]):
                return
            raise UploadError(f"readback identity mismatch {row['filename']}: bytes={size} sha256={digest.hexdigest()}")
        except (httpx.HTTPError, OSError, UploadError) as exc:
            last = exc
            if attempt < 5:
                time.sleep(min(2 ** attempt, 20))
    raise UploadError(f"readback failed after 5 attempts: {last}")


def verify_existing(item: dict[str, Any], row: dict[str, Any]) -> int:
    data_file = item.get("dataFile") or {}
    if int(data_file.get("filesize") or -1) != int(row["bytes"]):
        raise UploadError(f"existing size mismatch: {row['filename']}")
    kind, digest = normalize_checksum(data_file.get("checksum"))
    if kind not in {"SHA-256", "SHA256"} or digest != str(row["sha256"]):
        raise UploadError(f"existing SHA-256 mismatch: {row['filename']} kind={kind} digest={digest}")
    if bool(item.get("restricted")):
        raise UploadError(f"existing file is restricted: {row['filename']}")
    return int(data_file["id"])


@dataclass
class ReceiptRow:
    path: str
    bytes: int
    sha256: str
    datafile_id: int
    action: str
    public: bool = True
    full_readback_sha256_verified: bool = True


def upload_rows(client: httpx.Client, token: str, rows: list[dict[str, Any]],
                materializer: Any, work: pathlib.Path, receipt_path: pathlib.Path,
                receipt_kind: str) -> None:
    _, latest = dataset_snapshot(client, token)
    state = effective_state(client, token, latest)
    if state != "DRAFT":
        raise UploadError(f"uploads forbidden while Dataset state is {state!r}")
    existing = dataverse_files(latest)
    receipts: list[ReceiptRow] = []
    for index, row in enumerate(rows, 1):
        key = file_key(str(row["directory_label"]), str(row["filename"]))
        log(f"file {index}/{len(rows)} begin path={key} bytes={row['bytes']}")
        old = existing.get(key)
        if old is not None:
            datafile_id = verify_existing(old, row)
            action = "existing_exact_dataverse_checksum"
            # A successful prior upload receipt is represented by the immutable
            # registered SHA-256; no source re-download or duplicate upload.
            readback(client, token, datafile_id, row)
        else:
            path = work / f"item-{index:04d}.bin"
            materializer(row, path)
            verify_local(path, row)
            datafile_id = direct_upload(client, token, path, row)
            readback(client, token, datafile_id, row)
            path.unlink(missing_ok=True)
            action = "uploaded_and_full_readback_verified"
        receipts.append(ReceiptRow(key, int(row["bytes"]), str(row["sha256"]), datafile_id, action))
        write_json(receipt_path, {
            "schema": "trinityaccord.harvard-epoch-ii-upload-receipt.v1",
            "persistent_id": PID, "dataset_id": DATASET_ID, "kind": receipt_kind,
            "status": "in_progress", "files_verified": len(receipts),
            "bytes_verified": sum(item.bytes for item in receipts),
            "rows": [item.__dict__ for item in receipts],
        })
        log(f"file {index}/{len(rows)} PASS path={key} datafile_id={datafile_id}")
    value = load_json(receipt_path)
    value["status"] = "pass"
    write_json(receipt_path, value)


def command_upload(args: argparse.Namespace, manifest: dict[str, Any], token: str) -> int:
    rows = list(manifest["files"])
    work = args.work_dir.resolve()
    work.mkdir(parents=True, exist_ok=True)
    with httpx.Client(follow_redirects=True) as client:
        if args.group == "repository":
            selected = [row for row in rows if row["source_kind"] == "repository_file"]
            selected += control_rows(args.manifest, args.sums)
            source_repo = args.source_repo.resolve()
            def materializer(row: dict[str, Any], target: pathlib.Path) -> None:
                if row["source_kind"] == "repository_file":
                    materialize_repository_row(source_repo, row, target)
                else:
                    source = args.manifest if row["filename"] == "DATASET-MANIFEST.json" else args.sums
                    target.write_bytes(source.read_bytes())
            upload_rows(client, token, selected, materializer, work, args.receipt, "repository_and_controls")
        elif args.group == "release":
            all_release = sorted(
                [row for row in rows if row["source_kind"] == "public_github_release_asset"],
                key=lambda row: file_key(str(row["directory_label"]), str(row["filename"])),
            )
            selected = [row for index, row in enumerate(all_release) if index % args.shard_count == args.shard_index]
            upload_rows(client, token, selected, lambda row, target: download_release(client, row, target),
                        work, args.receipt, f"release_shard_{args.shard_index}_of_{args.shard_count}")
        elif args.group == "candidate":
            selected = [row for row in rows if row["source_kind"] == "verified_candidate_file"]
            candidate = args.candidate_dir.resolve()
            upload_rows(client, token, selected,
                        lambda row, target: shutil.copyfile(candidate / str(row["source_locator"]), target),
                        work, args.receipt, "verified_candidate")
        else:
            raise UploadError(f"unknown group: {args.group}")
    return 0


def receipt_rows(receipt_dir: pathlib.Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(receipt_dir.rglob("*.json")):
        value = load_json(path)
        if value.get("schema") != "trinityaccord.harvard-epoch-ii-upload-receipt.v1":
            continue
        if value.get("status") != "pass":
            raise UploadError(f"non-PASS upload receipt: {path}")
        rows.extend(value.get("rows") or [])
    return rows


def command_finalize(args: argparse.Namespace, manifest: dict[str, Any], token: str) -> int:
    expected_rows = list(manifest["files"]) + control_rows(args.manifest, args.sums)
    expected = {file_key(str(row["directory_label"]), str(row["filename"])): row for row in expected_rows}
    receipts = receipt_rows(args.receipt_dir)
    receipt_map: dict[str, dict[str, Any]] = {}
    for row in receipts:
        key = str(row["path"])
        if key in receipt_map:
            raise UploadError(f"duplicate receipt path: {key}")
        receipt_map[key] = row
    if set(receipt_map) != set(expected):
        raise UploadError(f"receipt coverage mismatch missing={sorted(set(expected)-set(receipt_map))[:20]} extra={sorted(set(receipt_map)-set(expected))[:20]}")
    for key, row in expected.items():
        receipt = receipt_map[key]
        if (int(receipt.get("bytes") or -1), str(receipt.get("sha256") or ""),
            receipt.get("full_readback_sha256_verified"), receipt.get("public")) != (
                int(row["bytes"]), str(row["sha256"]), True, True):
            raise UploadError(f"receipt identity/readback mismatch: {key}")

    cold = load_json(args.cold_receipt)
    if str(cold.get("result") or "").lower() != "pass":
        raise UploadError("clean candidate cold recovery is not PASS")
    with httpx.Client(follow_redirects=True) as client:
        _, latest = dataset_snapshot(client, token)
        state = effective_state(client, token, latest)
        if state in {"InReview", "RELEASED"}:
            log(f"finalize idempotent PASS state={state}; submitForReview not called")
            return 0
        if state != "DRAFT":
            raise UploadError(f"unexpected pre-submit state: {state!r}")
        actual = dataverse_files(latest)
        if set(actual) != set(expected):
            raise UploadError(f"Dataverse file-set mismatch files={len(actual)} expected={len(expected)}")
        for key, row in expected.items():
            verify_existing(actual[key], row)
        if len(actual) != PLANNED_FILES:
            raise UploadError(f"Dataverse count mismatch: {len(actual)}")
        # Exactly one request, with no generic retry wrapper.  If the response is
        # ambiguous, the state is read once and no second submission is issued.
        log("all gates PASS; issuing the sole submitForReview request")
        try:
            response = client.post(
                f"{SERVER}/api/datasets/:persistentId/submitForReview",
                headers=headers(token), params={"persistentId": PID}, timeout=180,
            )
            require_status(response, (200,), "submitForReview")
        except (httpx.HTTPError, UploadError) as exc:
            log(f"submitForReview response ambiguous/error: {exc}; checking state without resubmission")
        _, after = dataset_snapshot(client, token)
        final_state = effective_state(client, token, after)
        if final_state not in {"InReview", "RELEASED"}:
            raise UploadError(f"single submitForReview did not produce InReview/RELEASED: {final_state!r}; no retry issued")
        final = {
            "schema": "trinityaccord.harvard-epoch-ii-final-submission-receipt.v1",
            "persistent_id": PID, "dataset_id": DATASET_ID,
            "planned_files": PLANNED_FILES, "payload_and_support_bytes": PLANNED_PAYLOAD_BYTES,
            "control_files": 2, "manifest_sha256": MANIFEST_SHA256,
            "candidate_identity_sha256": CANDIDATE_ID, "layout_identity_sha256": LAYOUT_ID,
            "all_files_public": True, "all_sizes_and_sha256_match": True,
            "per_file_full_readback_receipts": len(receipt_map),
            "clean_cold_recovery": "pass", "submit_for_review_calls_this_execution": 1,
            "final_state": final_state,
        }
        write_json(args.final_receipt, final)
        log(f"FINAL PASS files={PLANNED_FILES} state={final_state}")
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--manifest", type=pathlib.Path, required=True)
    result.add_argument("--sums", type=pathlib.Path, required=True)
    sub = result.add_subparsers(dest="command", required=True)
    upload = sub.add_parser("upload")
    upload.add_argument("--group", choices=("repository", "release", "candidate"), required=True)
    upload.add_argument("--source-repo", type=pathlib.Path)
    upload.add_argument("--candidate-dir", type=pathlib.Path)
    upload.add_argument("--shard-index", type=int, default=0)
    upload.add_argument("--shard-count", type=int, default=1)
    upload.add_argument("--work-dir", type=pathlib.Path, required=True)
    upload.add_argument("--receipt", type=pathlib.Path, required=True)
    final = sub.add_parser("finalize")
    final.add_argument("--receipt-dir", type=pathlib.Path, required=True)
    final.add_argument("--cold-receipt", type=pathlib.Path, required=True)
    final.add_argument("--final-receipt", type=pathlib.Path, required=True)
    return result


def main() -> int:
    args = parser().parse_args()
    token = os.environ.get("HD_API_TOKEN", "").strip()
    if not token:
        raise UploadError("HD_API_TOKEN is required")
    manifest = validate_manifest(args.manifest.resolve(), args.sums.resolve())
    if args.command == "upload":
        if args.group == "repository" and not args.source_repo:
            raise UploadError("--source-repo is required for repository group")
        if args.group == "candidate" and not args.candidate_dir:
            raise UploadError("--candidate-dir is required for candidate group")
        if args.group == "release" and not (0 <= args.shard_index < args.shard_count <= 32):
            raise UploadError("invalid release shard selection")
        return command_upload(args, manifest, token)
    return command_finalize(args, manifest, token)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        log(f"FAIL {type(exc).__name__}: {exc}")
        raise
