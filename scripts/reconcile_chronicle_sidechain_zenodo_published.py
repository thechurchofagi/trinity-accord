#!/usr/bin/env python3
"""Reconcile an already-published Chronicle sidechain Zenodo version via Records API.

This is a fail-closed recovery path for the publish transition. It never creates,
updates, uploads to, edits, or republishes a Zenodo deposition. It:
- deterministically re-verifies the local DOI-ready deposit;
- locates exactly one already-published owner deposition for the package version;
- waits for Zenodo's public Records API to expose that record;
- verifies the exact public file set, size/MD5 metadata, and full SHA-256 readback;
- writes the repository DOI state only after every public byte has been verified.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from publish_chronicle_sidechain_to_zenodo import TITLE, verify_local

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_API = "https://zenodo.org/api"
DEFAULT_STATE = ROOT / "archive" / "chronicle-sidechain-zenodo-state.json"
CHUNK_BYTES = 8 * 1024 * 1024
PROGRESS_BYTES = 64 * 1024 * 1024
TRANSIENT_HTTP = {408, 425, 429, 500, 502, 503, 504}


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def write_json(path: pathlib.Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def meta(rec: dict[str, Any]) -> dict[str, Any]:
    return rec.get("metadata") if isinstance(rec.get("metadata"), dict) else {}


def version(rec: dict[str, Any]) -> str:
    return str(meta(rec).get("version") or "")


def doi(rec: dict[str, Any]) -> str:
    return str(rec.get("doi") or meta(rec).get("doi") or "")


def concept_doi(rec: dict[str, Any]) -> str:
    return str(rec.get("conceptdoi") or meta(rec).get("conceptdoi") or "")


def is_published(rec: dict[str, Any]) -> bool:
    return (
        rec.get("submitted") is True
        or str(rec.get("state") or "").lower() == "done"
        or bool(doi(rec))
    )


class Reconciler:
    def __init__(self, *, token: str, api_base: str, debug_path: pathlib.Path, request_attempts: int, download_attempts: int, request_delay: int, timeout: int):
        if not token:
            raise SystemExit("ZENODO_ACCESS_TOKEN is required for owner-deposition discovery")
        if request_attempts < 1 or download_attempts < 1:
            raise SystemExit("retry counts must be positive")
        self.token = token
        self.base = api_base.rstrip("/")
        self.debug_path = debug_path
        self.request_attempts = request_attempts
        self.download_attempts = download_attempts
        self.request_delay = max(1, request_delay)
        self.timeout = max(60, timeout)
        debug_path.parent.mkdir(parents=True, exist_ok=True)
        if debug_path.exists():
            debug_path.unlink()

    def log(self, event: str, **fields: Any) -> None:
        row = {"ts": now(), "event": event, **fields}
        with self.debug_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        print("[ZENODO PUBLIC] " + event + (" " if fields else "") + " ".join(f"{k}={v}" for k, v in fields.items()), flush=True)

    def _headers(self, *, authenticated: bool) -> dict[str, str]:
        headers = {"Accept": "application/json", "User-Agent": "trinity-sidechain-zenodo-public-reconcile/1.0"}
        if authenticated:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def get_json(self, url: str, *, authenticated: bool, retry_404: bool, label: str) -> dict[str, Any] | list[Any]:
        target = self.base + url if url.startswith("/") else url
        last_error = "unknown"
        for attempt in range(1, self.request_attempts + 1):
            self.log("json_request_start", label=label, attempt=attempt, path=urllib.parse.urlparse(target).path, authenticated=authenticated)
            request = urllib.request.Request(target, method="GET", headers=self._headers(authenticated=authenticated))
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    raw = response.read()
                    status = int(getattr(response, "status", 200))
                data = json.loads(raw.decode("utf-8"))
                if not isinstance(data, (dict, list)):
                    raise ValueError("JSON root is not object/list")
                self.log("json_request_ok", label=label, attempt=attempt, status=status, bytes=len(raw))
                return data
            except urllib.error.HTTPError as exc:
                last_error = f"HTTP {exc.code}"
                retryable = exc.code in TRANSIENT_HTTP or (retry_404 and exc.code == 404)
                self.log("json_request_http_error", label=label, attempt=attempt, status=exc.code, retryable=retryable)
                if not retryable or attempt >= self.request_attempts:
                    raise SystemExit(f"Zenodo {label} failed after {attempt} attempt(s): HTTP {exc.code}") from exc
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                last_error = repr(exc)
                self.log("json_request_error", label=label, attempt=attempt, error=last_error)
                if attempt >= self.request_attempts:
                    raise SystemExit(f"Zenodo {label} failed after {attempt} attempts: {exc}") from exc
            time.sleep(min(self.request_delay * attempt, 30))
        raise SystemExit(f"Zenodo {label} failed: {last_error}")

    def list_version_depositions(self, version_id: str) -> list[dict[str, Any]]:
        matches: list[dict[str, Any]] = []
        for page in range(1, 21):
            query = urllib.parse.urlencode({"size": 100, "page": page, "sort": "mostrecent", "all_versions": "true"})
            data = self.get_json(f"/deposit/depositions?{query}", authenticated=True, retry_404=False, label=f"owner-depositions-page-{page}")
            if not isinstance(data, list):
                raise SystemExit("Zenodo deposition list is not an array")
            rows = [row for row in data if isinstance(row, dict)]
            for row in rows:
                if meta(row).get("title") == TITLE and version(row) == version_id:
                    matches.append(row)
            if len(rows) < 100:
                break
        return matches

    def public_record(self, deposition: dict[str, Any]) -> dict[str, Any]:
        record_id = deposition.get("record_id") or deposition.get("recid") or deposition.get("id")
        try:
            record_id = int(record_id)
        except Exception as exc:
            raise SystemExit("published deposition lacks numeric record_id") from exc
        record = self.get_json(f"/records/{record_id}", authenticated=False, retry_404=True, label="public-record")
        if not isinstance(record, dict):
            raise SystemExit("Zenodo public record response is not an object")
        self.log("public_record_visible", record_id=record_id, doi=doi(record) or doi(deposition))
        return record

    @staticmethod
    def public_files(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
        rows = record.get("files")
        if not isinstance(rows, list):
            raise SystemExit("Zenodo public record has no files array")
        result: dict[str, dict[str, Any]] = {}
        for item in rows:
            if not isinstance(item, dict):
                continue
            name = str(item.get("key") or item.get("filename") or item.get("name") or "")
            if name:
                result[name] = item
        return result

    @staticmethod
    def remote_size(item: dict[str, Any]) -> int | None:
        for key in ("size", "filesize"):
            try:
                if item.get(key) is not None:
                    return int(item[key])
            except (TypeError, ValueError):
                pass
        return None

    @staticmethod
    def remote_md5(item: dict[str, Any]) -> str:
        checksum = str(item.get("checksum") or "").lower()
        return checksum.split(":", 1)[-1] if checksum else ""

    def candidate_download_urls(self, record_id: int, name: str, item: dict[str, Any]) -> list[str]:
        links = item.get("links") if isinstance(item.get("links"), dict) else {}
        candidates: list[str] = []
        for key in ("content", "download", "self"):
            value = links.get(key)
            if value:
                candidates.append(str(value))
        quoted = urllib.parse.quote(name, safe="")
        candidates.append(f"{self.base}/records/{record_id}/files/{quoted}/content")
        parsed = urllib.parse.urlparse(self.base)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        candidates.append(f"{origin}/records/{record_id}/files/{quoted}?download=1")
        out: list[str] = []
        for value in candidates:
            if value not in out:
                out.append(value)
        return out

    def verify_public_file(self, *, record_id: int, name: str, item: dict[str, Any], expect: dict[str, Any]) -> str:
        size = self.remote_size(item)
        md5 = self.remote_md5(item)
        if size != int(expect["bytes"]) or md5 != str(expect["md5"]).lower():
            raise SystemExit(
                f"Zenodo public metadata mismatch {name}: size={size}/{expect['bytes']} md5={md5}/{expect['md5']}"
            )
        failures: list[str] = []
        for candidate_index, url in enumerate(self.candidate_download_urls(record_id, name, item), 1):
            for attempt in range(1, self.download_attempts + 1):
                started = time.monotonic()
                total = 0
                sha = hashlib.sha256()
                next_progress = PROGRESS_BYTES
                self.log("public_download_start", name=name, candidate=candidate_index, attempt=attempt, path=urllib.parse.urlparse(url).path)
                request = urllib.request.Request(url, method="GET", headers={"User-Agent": "trinity-sidechain-zenodo-public-reconcile/1.0"})
                try:
                    with urllib.request.urlopen(request, timeout=self.timeout) as response:
                        while True:
                            chunk = response.read(CHUNK_BYTES)
                            if not chunk:
                                break
                            total += len(chunk)
                            sha.update(chunk)
                            if total >= next_progress:
                                self.log("public_download_progress", name=name, candidate=candidate_index, attempt=attempt, bytes=total)
                                while next_progress <= total:
                                    next_progress += PROGRESS_BYTES
                    digest = sha.hexdigest()
                    elapsed_ms = int((time.monotonic() - started) * 1000)
                    if total == int(expect["bytes"]) and digest == expect["sha256"]:
                        self.log("public_download_verified", name=name, candidate=candidate_index, attempt=attempt, bytes=total, sha256=digest, elapsed_ms=elapsed_ms)
                        return url
                    mismatch = f"candidate={candidate_index} bytes={total}/{expect['bytes']} sha256={digest}/{expect['sha256']}"
                    failures.append(mismatch)
                    self.log("public_download_mismatch", name=name, candidate=candidate_index, attempt=attempt, bytes=total, sha256=digest)
                    break
                except urllib.error.HTTPError as exc:
                    retryable = exc.code in TRANSIENT_HTTP or exc.code == 404
                    failures.append(f"candidate={candidate_index} attempt={attempt} HTTP {exc.code}")
                    self.log("public_download_http_error", name=name, candidate=candidate_index, attempt=attempt, status=exc.code, retryable=retryable)
                    if not retryable:
                        break
                except OSError as exc:
                    failures.append(f"candidate={candidate_index} attempt={attempt} {exc!r}")
                    self.log("public_download_error", name=name, candidate=candidate_index, attempt=attempt, error=repr(exc))
                if attempt < self.download_attempts:
                    time.sleep(min(self.request_delay * attempt, 20))
        raise SystemExit(f"Zenodo public full readback failed for {name}: {'; '.join(failures[-8:])}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--deposit-dir", required=True)
    parser.add_argument("--state", default=str(DEFAULT_STATE.relative_to(ROOT)))
    parser.add_argument("--api-base", default=os.getenv("ZENODO_API_BASE", DEFAULT_API))
    parser.add_argument("--request-attempts", type=int, default=int(os.getenv("ZENODO_PUBLIC_RECORD_ATTEMPTS", "18")))
    parser.add_argument("--download-attempts", type=int, default=int(os.getenv("ZENODO_PUBLIC_DOWNLOAD_ATTEMPTS", "3")))
    parser.add_argument("--request-delay", type=int, default=int(os.getenv("ZENODO_PUBLIC_RETRY_DELAY_SECONDS", "10")))
    parser.add_argument("--timeout", type=int, default=int(os.getenv("ZENODO_PUBLIC_TIMEOUT_SECONDS", "1200")))
    args = parser.parse_args()

    deposit = (ROOT / args.deposit_dir).resolve()
    if ROOT not in deposit.parents or not deposit.is_dir():
        raise SystemExit("deposit directory must exist inside repository")
    local = verify_local(deposit)
    package = local["package"]
    inventory = local["inventory"]
    version_id = str(package.get("version") or "")
    if not version_id:
        raise SystemExit("deposit package missing version")

    state_path = (ROOT / args.state).resolve()
    if ROOT not in state_path.parents:
        raise SystemExit("state path must be inside repository")

    reconciler = Reconciler(
        token=os.getenv("ZENODO_ACCESS_TOKEN", "").strip(),
        api_base=args.api_base,
        debug_path=deposit / "DEBUG-PUBLISHED-RECONCILE.jsonl",
        request_attempts=args.request_attempts,
        download_attempts=args.download_attempts,
        request_delay=args.request_delay,
        timeout=args.timeout,
    )
    reconciler.log("reconcile_start", version=version_id, files=len(inventory), bytes=sum(int(v["bytes"]) for v in inventory.values()))

    matches = reconciler.list_version_depositions(version_id)
    if len(matches) != 1:
        raise SystemExit(f"expected exactly one Zenodo deposition for version {version_id}, found {len(matches)}")
    deposition = matches[0]
    if not is_published(deposition):
        raise SystemExit(f"Zenodo deposition for version {version_id} is not published")
    if not doi(deposition):
        raise SystemExit("published Zenodo deposition is missing DOI")

    record = reconciler.public_record(deposition)
    if meta(record).get("title") != TITLE:
        raise SystemExit("public Zenodo record title mismatch")
    public_version = version(record)
    if public_version and public_version != version_id:
        raise SystemExit(f"public Zenodo record version mismatch {public_version} != {version_id}")
    record_doi = doi(record) or doi(deposition)
    if record_doi != doi(deposition):
        raise SystemExit(f"public/deposition DOI mismatch {record_doi} != {doi(deposition)}")

    try:
        record_id = int(deposition.get("record_id") or deposition.get("recid") or deposition.get("id"))
    except Exception as exc:
        raise SystemExit("published deposition lacks numeric record id") from exc
    remote = reconciler.public_files(record)
    if set(remote) != set(inventory):
        raise SystemExit(
            f"Zenodo public file set mismatch missing={sorted(set(inventory)-set(remote))} unexpected={sorted(set(remote)-set(inventory))}"
        )

    verified_urls: dict[str, str] = {}
    for name in sorted(inventory):
        verified_urls[name] = reconciler.verify_public_file(record_id=record_id, name=name, item=remote[name], expect=inventory[name])
    reconciler.log("public_manifest_verified", record_id=record_id, doi=record_doi, files=len(inventory))

    state = {
        "schema": "trinity-accord/chronicle-sidechain-zenodo-state/v1",
        "updated_at": now(),
        "latest_version": version_id,
        "source_release_tag": package["source_release_tag"],
        "source_commit_sha": package["source_commit_sha"],
        "package_identity_sha256": package["package_identity_sha256"],
        "deposition_id": int(deposition.get("id")),
        "record_id": record_id,
        "doi": record_doi,
        "concept_doi": concept_doi(record) or concept_doi(deposition),
        "api_base": args.api_base,
        "remote_full_readback_sha256_verified": True,
        "remote_readback_surface": "public_records_api",
        "public_record_api": f"{args.api_base.rstrip('/')}/records/{record_id}",
        "published_reconcile": True,
        "verified_file_count": len(verified_urls),
    }
    write_json(state_path, state)
    print(json.dumps(state, indent=2, sort_keys=True))
    output = os.getenv("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"doi={state['doi']}\nconcept_doi={state['concept_doi']}\nrecord_id={record_id}\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
