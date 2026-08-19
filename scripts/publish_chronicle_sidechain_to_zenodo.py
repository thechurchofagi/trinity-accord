#!/usr/bin/env python3
"""Publish/reconcile a Chronicle sidechain cold-recovery deposit on Zenodo.

Fail-closed guarantees:
- exact versioned mixed-rights acknowledgement is mandatory;
- local SHA256SUMS and package identity are verified before any network write;
- one bounded series draft is reconciled rather than duplicated;
- uploads are streamed from disk with Content-Length, bounded retries, and
  post-error remote reconciliation so large files are not buffered in memory;
- already-correct draft files are retained across retries, while mismatches and
  unexpected files are removed before publication;
- every uploaded file is size/MD5 checked and fully streamed back for SHA-256
  verification before publish and after publish;
- all API operations are logged to DEBUG.jsonl without exposing bearer tokens.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import http.client
import json
import os
import pathlib
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
TITLE = "Trinity Accord Chronicle Polygon and Base NFT Evidence v2"
RIGHTS_ACK = "TRINITY_SIDECHAIN_EVIDENCE_MIXED_RIGHTS_V1_APPROVED"
DEFAULT_API = "https://zenodo.org/api"
DEFAULT_STATE = ROOT / "archive" / "chronicle-sidechain-zenodo-state.json"
CHUNK_BYTES = 8 * 1024 * 1024
PROGRESS_BYTES = 64 * 1024 * 1024
TRANSIENT_HTTP = {408, 425, 429, 500, 502, 503, 504}


def read_json(path: pathlib.Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return data


def write_json(path: pathlib.Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_inventory(path: pathlib.Path) -> dict[str, Any]:
    sha = hashlib.sha256()
    md5 = hashlib.md5(usedforsecurity=False)
    total = 0
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(CHUNK_BYTES)
            if not chunk:
                break
            total += len(chunk)
            sha.update(chunk)
            md5.update(chunk)
    return {"bytes": total, "sha256": sha.hexdigest(), "md5": md5.hexdigest()}


class UploadError(RuntimeError):
    def __init__(self, message: str, *, retryable: bool, status: int | None = None):
        super().__init__(message)
        self.retryable = retryable
        self.status = status


class Client:
    def __init__(
        self,
        token: str,
        api_base: str,
        debug_path: pathlib.Path,
        *,
        upload_timeout: int,
        download_timeout: int,
        upload_retries: int,
        download_retries: int,
    ):
        if not token:
            raise SystemExit("ZENODO_ACCESS_TOKEN is required")
        if upload_timeout < 60 or download_timeout < 60:
            raise SystemExit("Zenodo upload/download timeouts must be >= 60 seconds")
        if upload_retries < 1 or download_retries < 1:
            raise SystemExit("Zenodo retry counts must be >= 1")
        self.token = token
        self.base = api_base.rstrip("/")
        self.debug_path = debug_path
        self.upload_timeout = upload_timeout
        self.download_timeout = download_timeout
        self.upload_retries = upload_retries
        self.download_retries = download_retries
        debug_path.parent.mkdir(parents=True, exist_ok=True)
        if debug_path.exists():
            debug_path.unlink()

    def log(self, event: str, **fields: Any) -> None:
        row = {
            "ts": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
            "event": event,
            **fields,
        }
        with self.debug_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        print(
            "[ZENODO] "
            + event
            + (" " if fields else "")
            + " ".join(f"{key}={value}" for key, value in fields.items()),
            flush=True,
        )

    def url(self, value: str) -> str:
        return self.base + value if value.startswith("/") else value

    def headers(self, content_type: str | None = None) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "User-Agent": "trinity-sidechain-zenodo/1.1",
        }
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    def request(
        self,
        method: str,
        url: str,
        *,
        payload: Any | None = None,
        data: bytes | None = None,
        content_type: str = "application/json",
    ) -> Any:
        body = data
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode()
        target = self.url(url)
        started = dt.datetime.now(dt.timezone.utc)
        self.log(
            "request_start",
            method=method,
            url_path=urllib.parse.urlparse(target).path,
            body_bytes=len(body) if body is not None else 0,
        )
        request = urllib.request.Request(
            target,
            data=body,
            method=method,
            headers=self.headers(content_type if body is not None else None),
        )
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                raw = response.read()
                status = getattr(response, "status", 200)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            self.log(
                "request_http_error",
                method=method,
                url_path=urllib.parse.urlparse(target).path,
                status=exc.code,
                detail_sha256=sha256_bytes(detail.encode()),
            )
            raise SystemExit(
                f"Zenodo {method} HTTP {exc.code}: {detail[:1600]}"
            ) from exc
        except OSError as exc:
            self.log(
                "request_network_error",
                method=method,
                url_path=urllib.parse.urlparse(target).path,
                error=repr(exc),
            )
            raise SystemExit(f"Zenodo {method} failed: {exc}") from exc
        elapsed = int(
            (dt.datetime.now(dt.timezone.utc) - started).total_seconds() * 1000
        )
        self.log(
            "request_ok",
            method=method,
            url_path=urllib.parse.urlparse(target).path,
            status=status,
            response_bytes=len(raw),
            response_sha256=sha256_bytes(raw),
            elapsed_ms=elapsed,
        )
        if not raw:
            return {}
        try:
            return json.loads(raw.decode())
        except Exception as exc:
            raise SystemExit("Zenodo API returned non-JSON response") from exc

    def put_file(
        self,
        url: str,
        path: pathlib.Path,
        expect: dict[str, Any],
        *,
        attempt: int,
    ) -> None:
        target = self.url(url)
        parsed = urllib.parse.urlparse(target)
        if parsed.scheme not in {"https", "http"} or not parsed.hostname:
            raise UploadError(
                f"unsupported Zenodo bucket URL: {target}",
                retryable=False,
            )
        current_size = path.stat().st_size
        if current_size != int(expect["bytes"]):
            raise UploadError(
                f"local file size changed before upload: {path.name}",
                retryable=False,
            )
        request_path = parsed.path or "/"
        if parsed.query:
            request_path += "?" + parsed.query
        conn_cls = (
            http.client.HTTPSConnection
            if parsed.scheme == "https"
            else http.client.HTTPConnection
        )
        conn = conn_cls(
            parsed.hostname,
            parsed.port,
            timeout=self.upload_timeout,
        )
        started = dt.datetime.now(dt.timezone.utc)
        sent = 0
        next_progress = PROGRESS_BYTES
        sha = hashlib.sha256()
        md5 = hashlib.md5(usedforsecurity=False)
        self.log(
            "upload_stream_start",
            name=path.name,
            bytes=current_size,
            sha256=expect["sha256"],
            attempt=attempt,
            timeout_seconds=self.upload_timeout,
            chunk_bytes=CHUNK_BYTES,
        )
        try:
            conn.putrequest("PUT", request_path)
            headers = self.headers("application/octet-stream")
            headers["Content-Length"] = str(current_size)
            for key, value in headers.items():
                conn.putheader(key, value)
            conn.endheaders()
            with path.open("rb") as handle:
                while True:
                    chunk = handle.read(CHUNK_BYTES)
                    if not chunk:
                        break
                    conn.send(chunk)
                    sent += len(chunk)
                    sha.update(chunk)
                    md5.update(chunk)
                    if sent >= next_progress or sent == current_size:
                        self.log(
                            "upload_stream_progress",
                            name=path.name,
                            attempt=attempt,
                            sent_bytes=sent,
                            total_bytes=current_size,
                            percent=round((sent / current_size) * 100, 2)
                            if current_size
                            else 100.0,
                        )
                        while next_progress <= sent:
                            next_progress += PROGRESS_BYTES
            if sent != current_size:
                raise UploadError(
                    f"streamed byte count mismatch for {path.name}: {sent} != {current_size}",
                    retryable=False,
                )
            if sha.hexdigest() != expect["sha256"] or md5.hexdigest() != expect["md5"]:
                raise UploadError(
                    f"local file changed while streaming upload: {path.name}",
                    retryable=False,
                )
            response = conn.getresponse()
            raw = response.read()
            status = int(response.status)
            elapsed = int(
                (dt.datetime.now(dt.timezone.utc) - started).total_seconds() * 1000
            )
            if not 200 <= status < 300:
                detail = raw.decode("utf-8", errors="replace")
                self.log(
                    "upload_stream_http_error",
                    name=path.name,
                    attempt=attempt,
                    status=status,
                    elapsed_ms=elapsed,
                    response_sha256=sha256_bytes(raw),
                )
                raise UploadError(
                    f"Zenodo PUT HTTP {status}: {detail[:1600]}",
                    retryable=status in TRANSIENT_HTTP,
                    status=status,
                )
            self.log(
                "upload_stream_ok",
                name=path.name,
                attempt=attempt,
                status=status,
                sent_bytes=sent,
                elapsed_ms=elapsed,
                response_bytes=len(raw),
                response_sha256=sha256_bytes(raw),
            )
        except UploadError:
            raise
        except (TimeoutError, socket.timeout, OSError, http.client.HTTPException) as exc:
            elapsed = int(
                (dt.datetime.now(dt.timezone.utc) - started).total_seconds() * 1000
            )
            self.log(
                "upload_stream_network_error",
                name=path.name,
                attempt=attempt,
                sent_bytes=sent,
                elapsed_ms=elapsed,
                error=repr(exc),
            )
            raise UploadError(
                f"Zenodo streaming PUT failed for {path.name}: {exc}",
                retryable=True,
            ) from exc
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def verify_download(
        self,
        url: str,
        *,
        name: str,
        expect: dict[str, Any],
        phase: str,
    ) -> None:
        target = self.url(url)
        for attempt in range(1, self.download_retries + 1):
            started = dt.datetime.now(dt.timezone.utc)
            total = 0
            next_progress = PROGRESS_BYTES
            sha = hashlib.sha256()
            self.log(
                "download_verify_start",
                name=name,
                phase=phase,
                attempt=attempt,
                expected_bytes=expect["bytes"],
                expected_sha256=expect["sha256"],
                timeout_seconds=self.download_timeout,
            )
            request = urllib.request.Request(
                target,
                method="GET",
                headers=self.headers(),
            )
            try:
                with urllib.request.urlopen(
                    request, timeout=self.download_timeout
                ) as response:
                    while True:
                        chunk = response.read(CHUNK_BYTES)
                        if not chunk:
                            break
                        total += len(chunk)
                        sha.update(chunk)
                        if total >= next_progress:
                            self.log(
                                "download_verify_progress",
                                name=name,
                                phase=phase,
                                attempt=attempt,
                                bytes=total,
                            )
                            while next_progress <= total:
                                next_progress += PROGRESS_BYTES
                digest = sha.hexdigest()
                elapsed = int(
                    (dt.datetime.now(dt.timezone.utc) - started).total_seconds()
                    * 1000
                )
                if total != int(expect["bytes"]) or digest != expect["sha256"]:
                    raise SystemExit(
                        f"Zenodo downloaded bytes mismatch {name}: "
                        f"bytes={total}/{expect['bytes']} sha256={digest}/{expect['sha256']}"
                    )
                self.log(
                    "download_verify_ok",
                    name=name,
                    phase=phase,
                    attempt=attempt,
                    bytes=total,
                    sha256=digest,
                    elapsed_ms=elapsed,
                )
                return
            except SystemExit:
                raise
            except Exception as exc:
                elapsed = int(
                    (dt.datetime.now(dt.timezone.utc) - started).total_seconds()
                    * 1000
                )
                self.log(
                    "download_verify_error",
                    name=name,
                    phase=phase,
                    attempt=attempt,
                    bytes=total,
                    elapsed_ms=elapsed,
                    error=repr(exc),
                )
                if attempt >= self.download_retries:
                    raise SystemExit(
                        f"Zenodo full readback failed for {name} after "
                        f"{self.download_retries} attempts: {exc}"
                    ) from exc
                time.sleep(min(5 * attempt, 20))


def verify_local(deposit: pathlib.Path) -> dict[str, Any]:
    package = read_json(deposit / "SIDECHAIN-ZENODO-DEPOSIT.json")
    if package.get("schema") != "trinity-accord/chronicle-sidechain-zenodo-deposit/v1":
        raise SystemExit("unexpected deposit schema")
    if package.get("metadata", {}).get("title") != TITLE:
        raise SystemExit("unexpected deposit title")
    sums: dict[str, str] = {}
    for line in (deposit / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, name = line.split(None, 1)
        name = name.strip().lstrip("*")
        if len(digest) != 64:
            raise SystemExit(f"invalid SHA256SUMS digest for {name}")
        sums[name] = digest
    expected_names = {
        row["name"]
        for row in package.get("inventory", [])
        if isinstance(row, dict)
    } | {"SHA256SUMS", "SIDECHAIN-ZENODO-DEPOSIT.json"}
    actual_names = {
        path.name
        for path in deposit.iterdir()
        if path.is_file() and path.name != "DEBUG.jsonl"
    }
    if actual_names != expected_names:
        raise SystemExit(
            f"local deposit file set mismatch "
            f"missing={sorted(expected_names - actual_names)} "
            f"unexpected={sorted(actual_names - expected_names)}"
        )
    inventory: dict[str, dict[str, Any]] = {}
    for path in sorted(
        item for item in deposit.iterdir() if item.is_file() and item.name != "DEBUG.jsonl"
    ):
        inventory[path.name] = file_inventory(path)
        if (
            path.name != "SHA256SUMS"
            and sums.get(path.name) != inventory[path.name]["sha256"]
        ):
            raise SystemExit(f"SHA256SUMS mismatch: {path.name}")
    return {"package": package, "inventory": inventory}


def dep_id(rec: dict[str, Any]) -> int:
    try:
        return int(rec["id"])
    except Exception as exc:
        raise SystemExit("Zenodo response missing deposition id") from exc


def meta(rec: dict[str, Any]) -> dict[str, Any]:
    return rec.get("metadata") if isinstance(rec.get("metadata"), dict) else {}


def is_published(rec: dict[str, Any]) -> bool:
    return (
        rec.get("submitted") is True
        or str(rec.get("state") or "").lower() == "done"
        or bool(rec.get("doi") or meta(rec).get("doi"))
    )


def version(rec: dict[str, Any]) -> str:
    return str(meta(rec).get("version") or "")


def doi(rec: dict[str, Any]) -> str:
    return str(rec.get("doi") or meta(rec).get("doi") or "")


def concept_doi(rec: dict[str, Any]) -> str:
    return str(rec.get("conceptdoi") or meta(rec).get("conceptdoi") or "")


def list_series(client: Client) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for page in range(1, 21):
        query = urllib.parse.urlencode(
            {"size": 100, "page": page, "sort": "mostrecent"}
        )
        rows = client.request("GET", f"/deposit/depositions?{query}")
        if not isinstance(rows, list):
            raise SystemExit("Zenodo deposition list is not a list")
        page_rows = [row for row in rows if isinstance(row, dict)]
        out.extend(row for row in page_rows if meta(row).get("title") == TITLE)
        if len(page_rows) < 100:
            break
    return sorted(out, key=dep_id)


def refresh(client: Client, rec: dict[str, Any]) -> dict[str, Any]:
    out = client.request("GET", f"/deposit/depositions/{dep_id(rec)}")
    if not isinstance(out, dict):
        raise SystemExit("Zenodo deposition readback invalid")
    return out


def remote_files(rec: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = rec.get("files")
    if not isinstance(rows, list):
        raise SystemExit("Zenodo files missing")
    result: dict[str, dict[str, Any]] = {}
    for item in rows:
        if not isinstance(item, dict):
            continue
        name = str(item.get("filename") or item.get("key") or "")
        if name:
            result[name] = item
    return result


def remote_metadata_matches(
    item: dict[str, Any], expect: dict[str, Any]
) -> bool:
    try:
        size = int(item.get("filesize", item.get("size")))
    except (TypeError, ValueError):
        return False
    checksum = str(item.get("checksum") or "").split(":", 1)[-1].lower()
    return size == int(expect["bytes"]) and checksum == expect["md5"]


def delete_remote_file(client: Client, item: dict[str, Any], *, name: str) -> None:
    links = item.get("links") if isinstance(item.get("links"), dict) else {}
    url = links.get("self")
    if not url:
        raise SystemExit(f"Zenodo file delete link missing: {name}")
    client.log("remote_file_delete", name=name)
    client.request("DELETE", str(url))


def cleanup_unexpected_files(
    client: Client,
    draft: dict[str, Any],
    local: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    draft = refresh(client, draft)
    remote = remote_files(draft)
    unexpected = sorted(set(remote) - set(local))
    if not unexpected:
        return draft
    for name in unexpected:
        delete_remote_file(client, remote[name], name=name)
    draft = refresh(client, draft)
    client.log("unexpected_files_removed", names=unexpected)
    return draft


def upload_one(
    client: Client,
    draft: dict[str, Any],
    *,
    bucket: str,
    deposit: pathlib.Path,
    name: str,
    expect: dict[str, Any],
) -> dict[str, Any]:
    path = deposit / name
    upload_url = str(bucket).rstrip("/") + "/" + urllib.parse.quote(name)
    for attempt in range(1, client.upload_retries + 1):
        draft = refresh(client, draft)
        existing = remote_files(draft).get(name)
        if existing is not None:
            if remote_metadata_matches(existing, expect):
                client.log(
                    "upload_reconciled_existing",
                    name=name,
                    attempt=attempt,
                    bytes=expect["bytes"],
                    md5=expect["md5"],
                )
                return draft
            client.log(
                "upload_existing_mismatch",
                name=name,
                attempt=attempt,
                remote_size=existing.get("filesize", existing.get("size")),
                remote_checksum=existing.get("checksum"),
                expected_size=expect["bytes"],
                expected_md5=expect["md5"],
            )
            delete_remote_file(client, existing, name=name)
            draft = refresh(client, draft)
        try:
            client.put_file(upload_url, path, expect, attempt=attempt)
        except UploadError as exc:
            client.log(
                "upload_attempt_failed",
                name=name,
                attempt=attempt,
                retryable=exc.retryable,
                status=exc.status,
                error=str(exc),
            )
            if not exc.retryable:
                raise SystemExit(str(exc)) from exc
            time.sleep(min(5 * attempt, 20))
            draft = refresh(client, draft)
            landed = remote_files(draft).get(name)
            if landed is not None and remote_metadata_matches(landed, expect):
                client.log(
                    "upload_reconciled_after_error",
                    name=name,
                    attempt=attempt,
                    bytes=expect["bytes"],
                    md5=expect["md5"],
                )
                return draft
            if attempt >= client.upload_retries:
                raise SystemExit(
                    f"Zenodo upload failed for {name} after "
                    f"{client.upload_retries} attempts: {exc}"
                ) from exc
            continue
        draft = refresh(client, draft)
        landed = remote_files(draft).get(name)
        if landed is not None and remote_metadata_matches(landed, expect):
            client.log(
                "upload_verified_metadata",
                name=name,
                attempt=attempt,
                bytes=expect["bytes"],
                md5=expect["md5"],
            )
            return draft
        if landed is not None:
            client.log(
                "upload_post_success_mismatch",
                name=name,
                attempt=attempt,
                remote_size=landed.get("filesize", landed.get("size")),
                remote_checksum=landed.get("checksum"),
            )
            delete_remote_file(client, landed, name=name)
        if attempt >= client.upload_retries:
            raise SystemExit(
                f"Zenodo upload returned success but metadata did not reconcile: {name}"
            )
        time.sleep(min(5 * attempt, 20))
    raise SystemExit(f"unreachable upload failure: {name}")


def verify_remote(
    client: Client,
    rec: dict[str, Any],
    local: dict[str, dict[str, Any]],
    *,
    phase: str,
) -> None:
    remote = remote_files(rec)
    if set(remote) != set(local):
        raise SystemExit(
            f"Zenodo remote file set mismatch "
            f"missing={sorted(set(local) - set(remote))} "
            f"unexpected={sorted(set(remote) - set(local))}"
        )
    client.log(
        "remote_manifest_verify_start",
        phase=phase,
        files=len(local),
        bytes=sum(int(row["bytes"]) for row in local.values()),
    )
    for name, expect in local.items():
        item = remote[name]
        if not remote_metadata_matches(item, expect):
            raise SystemExit(
                f"Zenodo metadata mismatch {name}: "
                f"remote_size={item.get('filesize', item.get('size'))} "
                f"remote_checksum={item.get('checksum')} "
                f"expected_size={expect['bytes']} expected_md5={expect['md5']}"
            )
        links = item.get("links") if isinstance(item.get("links"), dict) else {}
        download = str(links.get("download") or links.get("content") or "")
        if not download:
            raise SystemExit(f"Zenodo download link missing {name}")
        client.verify_download(download, name=name, expect=expect, phase=phase)
        client.log(
            "remote_file_verified",
            phase=phase,
            name=name,
            bytes=expect["bytes"],
            sha256=expect["sha256"],
        )
    client.log("remote_manifest_verify_ok", phase=phase, files=len(local))


def create_draft(
    client: Client,
    latest: dict[str, Any] | None,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    if latest is None:
        out = client.request("POST", "/deposit/depositions", payload={"metadata": metadata})
        if not isinstance(out, dict):
            raise SystemExit("new deposition response invalid")
        return out
    response = client.request(
        "POST",
        f"/deposit/depositions/{dep_id(latest)}/actions/newversion",
        payload={},
    )
    links = (
        response.get("links")
        if isinstance(response, dict) and isinstance(response.get("links"), dict)
        else {}
    )
    draft_url = links.get("latest_draft")
    if not draft_url:
        raise SystemExit("new version response missing latest_draft")
    draft = client.request("GET", str(draft_url))
    if not isinstance(draft, dict):
        raise SystemExit("latest draft invalid")
    return draft


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--deposit-dir", required=True)
    parser.add_argument(
        "--state",
        default=str(DEFAULT_STATE.relative_to(ROOT)),
    )
    parser.add_argument(
        "--api-base",
        default=os.getenv("ZENODO_API_BASE", DEFAULT_API),
    )
    parser.add_argument(
        "--rights-boundary-ack",
        default=os.getenv("CHRONICLE_SIDECHAIN_ZENODO_RIGHTS_ACK", ""),
    )
    parser.add_argument(
        "--upload-timeout",
        type=int,
        default=int(os.getenv("ZENODO_UPLOAD_TIMEOUT_SECONDS", "1200")),
    )
    parser.add_argument(
        "--download-timeout",
        type=int,
        default=int(os.getenv("ZENODO_DOWNLOAD_TIMEOUT_SECONDS", "1200")),
    )
    parser.add_argument(
        "--upload-retries",
        type=int,
        default=int(os.getenv("ZENODO_UPLOAD_RETRIES", "3")),
    )
    parser.add_argument(
        "--download-retries",
        type=int,
        default=int(os.getenv("ZENODO_DOWNLOAD_RETRIES", "3")),
    )
    args = parser.parse_args()

    deposit = (ROOT / args.deposit_dir).resolve()
    if ROOT not in deposit.parents or not deposit.is_dir():
        raise SystemExit("deposit directory must exist inside repository")
    local = verify_local(deposit)
    package = local["package"]
    version_id = str(package.get("version") or "")
    if args.rights_boundary_ack != RIGHTS_ACK:
        raise SystemExit(
            "sidechain Zenodo publication disabled until mixed-rights "
            "acknowledgement is explicitly approved"
        )
    state_path = (ROOT / args.state).resolve()
    if ROOT not in state_path.parents:
        raise SystemExit("state path must be inside repository")

    token = os.getenv("ZENODO_ACCESS_TOKEN", "").strip()
    client = Client(
        token,
        args.api_base,
        deposit / "DEBUG.jsonl",
        upload_timeout=args.upload_timeout,
        download_timeout=args.download_timeout,
        upload_retries=args.upload_retries,
        download_retries=args.download_retries,
    )
    client.log(
        "publication_config",
        version=version_id,
        upload_timeout_seconds=args.upload_timeout,
        download_timeout_seconds=args.download_timeout,
        upload_retries=args.upload_retries,
        download_retries=args.download_retries,
        chunk_bytes=CHUNK_BYTES,
    )

    series = list_series(client)
    same = [row for row in series if version(row) == version_id]
    published_same = [row for row in same if is_published(row)]
    drafts = [row for row in same if not is_published(row)]
    if len(published_same) > 1 or len(drafts) > 1:
        raise SystemExit(f"duplicate Zenodo records for version {version_id}")

    if published_same:
        record = refresh(client, published_same[0])
        verify_remote(
            client,
            record,
            local["inventory"],
            phase="published-reconcile",
        )
        client.log(
            "reconciled_existing",
            version=version_id,
            deposition_id=dep_id(record),
            doi=doi(record),
        )
    else:
        if drafts:
            draft = refresh(client, drafts[0])
            client.log(
                "reuse_existing_draft",
                version=version_id,
                deposition_id=dep_id(draft),
            )
        else:
            other_drafts = [row for row in series if not is_published(row)]
            if other_drafts:
                raise SystemExit(
                    "unfinished sidechain Zenodo draft for another version "
                    "requires reconciliation"
                )
            published = [row for row in series if is_published(row)]
            draft = create_draft(
                client,
                published[-1] if published else None,
                package["metadata"],
            )
            client.log(
                "created_draft",
                version=version_id,
                deposition_id=dep_id(draft),
            )

        deposition_id = dep_id(draft)
        updated = client.request(
            "PUT",
            f"/deposit/depositions/{deposition_id}",
            payload={"metadata": package["metadata"]},
        )
        draft = refresh(client, updated if isinstance(updated, dict) else draft)
        draft = cleanup_unexpected_files(client, draft, local["inventory"])
        links = draft.get("links") if isinstance(draft.get("links"), dict) else {}
        bucket = links.get("bucket")
        if not bucket:
            raise SystemExit("Zenodo draft missing bucket")

        client.log(
            "upload_reconcile_start",
            deposition_id=deposition_id,
            files=len(local["inventory"]),
            total_bytes=sum(
                int(row["bytes"]) for row in local["inventory"].values()
            ),
        )
        for name in sorted(local["inventory"]):
            draft = upload_one(
                client,
                draft,
                bucket=str(bucket),
                deposit=deposit,
                name=name,
                expect=local["inventory"][name],
            )

        draft = refresh(client, draft)
        verify_remote(
            client,
            draft,
            local["inventory"],
            phase="pre-publish",
        )
        record = client.request(
            "POST",
            f"/deposit/depositions/{dep_id(draft)}/actions/publish",
            payload={},
        )
        if not isinstance(record, dict):
            raise SystemExit("Zenodo publish response invalid")
        record = refresh(client, record)
        verify_remote(
            client,
            record,
            local["inventory"],
            phase="post-publish",
        )
        client.log(
            "published_verified",
            version=version_id,
            deposition_id=dep_id(record),
            doi=doi(record),
        )

    if not doi(record):
        raise SystemExit("published Zenodo record missing DOI")
    state = {
        "schema": "trinity-accord/chronicle-sidechain-zenodo-state/v1",
        "updated_at": dt.datetime.now(dt.timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "latest_version": version_id,
        "source_release_tag": package["source_release_tag"],
        "source_commit_sha": package["source_commit_sha"],
        "package_identity_sha256": package["package_identity_sha256"],
        "deposition_id": dep_id(record),
        "record_id": record.get("record_id") or dep_id(record),
        "doi": doi(record),
        "concept_doi": concept_doi(record),
        "api_base": args.api_base,
        "remote_full_readback_sha256_verified": True,
    }
    write_json(state_path, state)
    print(json.dumps(state, indent=2, sort_keys=True))
    output = os.getenv("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(
                f"doi={state['doi']}\nconcept_doi={state['concept_doi']}\n"
            )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
