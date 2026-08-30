#!/usr/bin/env python3
"""Mirror the complete First Star-Moon Witness GitHub Release to Zenodo.

The workflow downloads the release assets first. This publisher then:
- verifies the exact expected release inventory (name, byte length, SHA-256);
- reconciles at most one Zenodo draft with this exact title;
- uploads every asset with streaming progress logs;
- verifies Zenodo's remote file metadata and full read-back SHA-256;
- publishes the record and writes a machine-readable state file.

No secret values are ever logged.
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
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

TITLE = "The First Star-Moon Witness: A Computationally Delayed Human-Witness Archive"
RELEASE_TAG = "first-star-moon-witness-encrypted-archive-v1"
RELEASE_URL = (
    "https://github.com/thechurchofagi/trinity-accord/releases/tag/"
    + RELEASE_TAG
)
DEFAULT_API = "https://zenodo.org/api"
CHUNK = 8 * 1024 * 1024
PROGRESS = 64 * 1024 * 1024
TRANSIENT = {408, 425, 429, 500, 502, 503, 504}

EXPECTED: dict[str, tuple[int, str]] = {
    "ARCHIVE-README.md": (1441, "f72c0aa719572b284bfeb42f87fe91dfcf76f0e532fef6504a5a3418715ea6af"),
    "ATTACK-COST-BENCHMARK.json": (1060, "2e2d47547e783f2d5340a606824b708cc3d6431872e0fe05c79635890efcf8a2"),
    "DECRYPTION-VERIFICATION.json": (280, "d7e8586dfca91f6219350da5928f4fe0fa1bdc9655860a1c9b14dc66f86bb5ca"),
    "ENCRYPTION-REPORT.json": (1763, "8747f5d31bb81798c40f80783ebb4f0419d53e76ad58726ed46c56618c7f853a"),
    "FIRST-STAR-MOON-ENCRYPTED-MANIFEST.json": (3789, "850d8f0e539a713b2d65bfef089f1be9e2e135560da4ea01ff4ddaf88d7d36ff"),
    "FORMAT-AND-RECOVERY.md": (1809, "bb1aee3ea1f944e3f3bd95e765b713ab0dd266bb85de2a8f7df324fba3b9f3cd"),
    "JOIN-VERIFICATION.json": (343, "d334660094bc7bf0b7a774618abfadf7860ba61aee2c255c7dfa02370e1fcb2a"),
    "PLAINTEXT-DELETION-RECEIPT.json": (282, "9837426dfac1b481987d8df0368c97f30161f48b544fc878bbc354872cc34692"),
    "PUBLIC-ARCHIVE-CHECKSUMS.sha256": (1609, "7608c11c182d1bfc41945b2c50eafe8dea8206326db1ee3720c51666a57bc31e"),
    "SECRET-DESTRUCTION-RECEIPT.json": (322, "87439a99f121d7cbae06059930407a83d30cf9626ad0dd06edcce25a58970dd0"),
    "SOURCE-INTEGRITY.json": (1800, "6462d0e65d0c3dc1614c3d6b79a0c5cb740d242b26db206533632906ca76710a"),
    "SPLIT-REPORT.json": (811, "7872d2ec05c737c831e7905ae5fa020465bf9751520c55ad8432f8323bd537bc"),
    "TAMPER-REJECTION.json": (192, "ba6e902c60d9bda905607eadd9069677e542111c876a0a9c6e360dfc2d5907ee"),
    "first-star-moon-witness.v1.pqtime.enc.part001": (419430400, "89dfbdd5f620e2d3aa7033b8ca9f30b327d475fb8937a7b85751189ff4b855d0"),
    "first-star-moon-witness.v1.pqtime.enc.part002": (419430400, "911d22e79905a2c686782b506f1d2f36348ca76ba58475882c0a984bef3963e7"),
    "first-star-moon-witness.v1.pqtime.enc.part003": (394320845, "86776c9fbbbb1cd1e01c10d5e82f4973e15a26eaff02069b496e5a000b8aff67"),
    "requirements.txt": (41, "4d338366992581573f37b5d34b83d50d6754513be20ddf7ef52b4cc268a0b856"),
    "ta_pqtime_container.py": (17788, "a2938bdb4687d0f39a6728ae970c5e6325c1b21e7293a470176d68722a76fd70"),
}


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(CHUNK):
            h.update(chunk)
    return h.hexdigest()


def md5_file(path: pathlib.Path) -> str:
    h = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as f:
        while chunk := f.read(CHUNK):
            h.update(chunk)
    return h.hexdigest()


def normalize_md5(value: Any) -> str:
    """Normalize Zenodo checksum metadata across legacy and current API shapes."""
    checksum = str(value or "").strip().lower()
    if checksum.startswith("md5:"):
        checksum = checksum[4:]
    return checksum


def write_json(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


class Client:
    def __init__(self, token: str, base: str):
        if not token:
            raise SystemExit("ZENODO_ACCESS_TOKEN is required")
        self.token = token
        self.base = base.rstrip("/")

    def headers(self, content_type: str | None = None) -> dict[str, str]:
        out = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "User-Agent": "trinity-first-star-moon-zenodo/1.0",
        }
        if content_type:
            out["Content-Type"] = content_type
        return out

    def url(self, value: str) -> str:
        return self.base + value if value.startswith("/") else value

    def request(
        self,
        method: str,
        value: str,
        payload: Any | None = None,
        *,
        allow_404: bool = False,
    ) -> Any:
        target = self.url(value)
        data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        print(
            f"[ZENODO] request method={method} path={urllib.parse.urlparse(target).path}",
            flush=True,
        )
        req = urllib.request.Request(
            target,
            data=data,
            method=method,
            headers=self.headers("application/json" if data is not None else None),
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                raw = r.read()
        except urllib.error.HTTPError as exc:
            if allow_404 and exc.code == 404:
                return None
            detail = exc.read().decode("utf-8", errors="replace")
            raise SystemExit(f"Zenodo {method} HTTP {exc.code}: {detail[:1600]}") from exc
        except OSError as exc:
            raise SystemExit(f"Zenodo {method} failed: {exc}") from exc
        return json.loads(raw.decode("utf-8")) if raw else {}

    def put_file(self, bucket: str, path: pathlib.Path) -> None:
        target = bucket.rstrip("/") + "/" + urllib.parse.quote(path.name)
        parsed = urllib.parse.urlparse(target)
        if parsed.scheme != "https" or not parsed.hostname:
            raise SystemExit(f"unexpected Zenodo bucket URL: {target}")
        size = path.stat().st_size
        expected_sha = sha256_file(path)
        expected_md5 = md5_file(path)
        for attempt in range(1, 5):
            sent = 0
            next_progress = PROGRESS
            sha = hashlib.sha256()
            md5 = hashlib.md5(usedforsecurity=False)
            conn = http.client.HTTPSConnection(parsed.hostname, parsed.port, timeout=900)
            request_path = parsed.path + (("?" + parsed.query) if parsed.query else "")
            print(
                f"[ZENODO] upload_start name={path.name} bytes={size} attempt={attempt}",
                flush=True,
            )
            try:
                conn.putrequest("PUT", request_path)
                headers = self.headers("application/octet-stream")
                headers["Content-Length"] = str(size)
                for key, value in headers.items():
                    conn.putheader(key, value)
                conn.endheaders()
                with path.open("rb") as f:
                    while chunk := f.read(CHUNK):
                        conn.send(chunk)
                        sent += len(chunk)
                        sha.update(chunk)
                        md5.update(chunk)
                        if sent >= next_progress or sent == size:
                            print(
                                f"[ZENODO] upload_progress name={path.name} bytes={sent}/{size} percent={sent*100/size:.2f}",
                                flush=True,
                            )
                            while next_progress <= sent:
                                next_progress += PROGRESS
                response = conn.getresponse()
                raw = response.read()
                if (
                    200 <= response.status < 300
                    and sent == size
                    and sha.hexdigest() == expected_sha
                    and md5.hexdigest() == expected_md5
                ):
                    print(
                        f"[ZENODO] upload_ok name={path.name} status={response.status}",
                        flush=True,
                    )
                    return
                detail = raw.decode("utf-8", errors="replace")
                if response.status not in TRANSIENT:
                    raise SystemExit(
                        f"Zenodo PUT HTTP {response.status} for {path.name}: {detail[:1000]}"
                    )
            except (socket.timeout, TimeoutError, OSError, http.client.HTTPException) as exc:
                if attempt >= 4:
                    raise SystemExit(f"Zenodo upload failed for {path.name}: {exc}") from exc
            finally:
                conn.close()
            time.sleep(min(10 * attempt, 30))
        raise SystemExit(f"Zenodo upload retries exhausted: {path.name}")

    def full_readback(self, url: str, path: pathlib.Path, phase: str) -> None:
        expected_size = path.stat().st_size
        expected_sha = sha256_file(path)
        for attempt in range(1, 4):
            total = 0
            next_progress = PROGRESS
            h = hashlib.sha256()
            req = urllib.request.Request(url, method="GET", headers=self.headers())
            print(
                f"[ZENODO] readback_start phase={phase} name={path.name} attempt={attempt}",
                flush=True,
            )
            try:
                with urllib.request.urlopen(req, timeout=900) as r:
                    while chunk := r.read(CHUNK):
                        total += len(chunk)
                        h.update(chunk)
                        if total >= next_progress:
                            print(
                                f"[ZENODO] readback_progress phase={phase} name={path.name} bytes={total}",
                                flush=True,
                            )
                            while next_progress <= total:
                                next_progress += PROGRESS
                if total != expected_size or h.hexdigest() != expected_sha:
                    raise SystemExit(
                        f"Zenodo readback mismatch {path.name}: bytes={total}/{expected_size} sha256={h.hexdigest()}/{expected_sha}"
                    )
                print(
                    f"[ZENODO] readback_ok phase={phase} name={path.name} sha256={expected_sha}",
                    flush=True,
                )
                return
            except SystemExit:
                raise
            except Exception as exc:
                if attempt >= 3:
                    raise SystemExit(f"Zenodo readback failed for {path.name}: {exc}") from exc
                time.sleep(10 * attempt)


def verify_source(root: pathlib.Path) -> dict[str, dict[str, Any]]:
    actual = {p.name for p in root.iterdir() if p.is_file()}
    expected = set(EXPECTED)
    if actual != expected:
        raise SystemExit(
            f"release asset set mismatch missing={sorted(expected-actual)} extra={sorted(actual-expected)}"
        )
    inventory: dict[str, dict[str, Any]] = {}
    for name in sorted(EXPECTED):
        path = root / name
        expected_size, expected_sha = EXPECTED[name]
        size = path.stat().st_size
        digest = sha256_file(path)
        if size != expected_size or digest != expected_sha:
            raise SystemExit(
                f"source verification failed {name}: bytes={size}/{expected_size} sha256={digest}/{expected_sha}"
            )
        inventory[name] = {
            "bytes": size,
            "sha256": digest,
            "md5": md5_file(path),
        }
        print(
            f"[SOURCE VERIFIED] name={name} bytes={size} sha256={digest}",
            flush=True,
        )
    return inventory


def metadata() -> dict[str, Any]:
    return {
        "title": TITLE,
        "upload_type": "dataset",
        "description": (
            "Independent, non-amending preservation mirror of the complete GitHub Release for the First Star-Moon Witness. "
            "The principal payload is intentionally encrypted/computationally delayed and is preserved as ciphertext bytes rather than as presently readable media. "
            "The unlock secret is not retained by the depositor or by Zenodo. The archival purpose is long-term bit preservation, provenance, and future verifiability. "
            "The record includes the complete public recovery package: ciphertext parts, checksums, manifest, format/recovery documentation, verification reports, benchmark data, requirements, and recovery code. "
            "Any future successful recovery should reconstruct and verify the ciphertext against PUBLIC-ARCHIVE-CHECKSUMS.sha256 and the release manifest before interpreting recovered content. "
            "AI-assisted tooling contributed to packaging, metadata preparation, integrity checking, and archival automation; publication authorization and archival responsibility remain with the human operator."
        ),
        "creators": [{"name": "Trinity Accord"}],
        "version": "1.0",
        "publication_date": "2026-08-30",
        "keywords": [
            "Trinity Accord",
            "First Star-Moon Witness",
            "encrypted archive",
            "computational delay",
            "digital preservation",
            "cryptographic provenance",
            "human witness archive",
        ],
        "notes": (
            "This record is a non-amending preservation mirror created after Canon closure. "
            "It does not revise the canonical Trinity Accord. The GitHub Release remains the source distribution surface; Zenodo is an independent institutional preservation and citation layer."
        ),
        "related_identifiers": [
            {
                "identifier": RELEASE_URL,
                "relation": "isSupplementTo",
                "scheme": "url",
            }
        ],
    }


def get_remote_name(row: dict[str, Any]) -> str:
    return str(row.get("filename") or row.get("key") or "")


def find_or_create(client: Client) -> dict[str, Any]:
    rows = client.request("GET", "/deposit/depositions?size=100")
    matches = [
        r
        for r in rows
        if isinstance(r, dict) and r.get("metadata", {}).get("title") == TITLE
    ]
    if len(matches) > 1:
        raise SystemExit(
            f"multiple Zenodo deposits with exact target title: {[r.get('id') for r in matches]}"
        )
    if matches:
        dep = matches[0]
        print(
            f"[ZENODO] reuse_deposition id={dep.get('id')} submitted={dep.get('submitted')}",
            flush=True,
        )
        return dep
    dep = client.request("POST", "/deposit/depositions", {})
    dep_id = dep.get("id")
    if not dep_id:
        raise SystemExit("Zenodo did not return deposition id")
    dep = client.request(
        "PUT",
        f"/deposit/depositions/{dep_id}",
        {"metadata": metadata()},
    )
    print(
        f"[ZENODO] deposition_created id={dep_id} reserved_doi={dep.get('metadata',{}).get('prereserve_doi',{}).get('doi')}",
        flush=True,
    )
    return dep


def verify_remote_rows(
    rows: list[dict[str, Any]],
    inventory: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    by_name = {get_remote_name(r): r for r in rows}
    if set(by_name) != set(inventory):
        raise SystemExit(
            f"Zenodo remote file set mismatch missing={sorted(set(inventory)-set(by_name))} extra={sorted(set(by_name)-set(inventory))}"
        )
    for name, inv in inventory.items():
        row = by_name[name]
        size = int(row.get("filesize") or row.get("size") or -1)
        checksum = str(row.get("checksum") or "")
        if size != inv["bytes"]:
            raise SystemExit(
                f"Zenodo remote size mismatch {name}: {size}/{inv['bytes']}"
            )
        if checksum and normalize_md5(checksum) != inv["md5"]:
            raise SystemExit(
                f"Zenodo remote MD5 mismatch {name}: {checksum}/{inv['md5']}"
            )
    return by_name


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-dir", required=True)
    ap.add_argument("--state-file", required=True)
    ap.add_argument(
        "--api-base",
        default=os.environ.get("ZENODO_API_BASE", DEFAULT_API),
    )
    args = ap.parse_args()
    source = pathlib.Path(args.source_dir).resolve()
    state_path = pathlib.Path(args.state_file).resolve()
    if not source.is_dir():
        raise SystemExit(f"source directory missing: {source}")
    inventory = verify_source(source)
    client = Client(os.environ.get("ZENODO_ACCESS_TOKEN", ""), args.api_base)
    dep = find_or_create(client)
    dep_id = int(dep["id"])
    publish_payload: dict[str, Any] = {}

    if dep.get("submitted") is True:
        record = client.request("GET", f"/records/{dep_id}", allow_404=True)
        if not record:
            record = client.request("GET", f"/deposit/depositions/{dep_id}")
        rows = record.get("files", [])
        by_name = verify_remote_rows(rows, inventory)
        for name in sorted(EXPECTED):
            link = (
                by_name[name].get("links", {}).get("download")
                or by_name[name].get("links", {}).get("self")
            )
            if not link:
                raise SystemExit(f"no readback URL for published file {name}")
            client.full_readback(str(link), source / name, "published-reconcile")
        final = record
    else:
        dep = client.request(
            "PUT",
            f"/deposit/depositions/{dep_id}",
            {"metadata": metadata()},
        )
        bucket = str(dep.get("links", {}).get("bucket") or "")
        if not bucket:
            raise SystemExit("Zenodo draft did not return bucket URL")
        remote_rows = dep.get("files", [])
        remote_by_name = {get_remote_name(r): r for r in remote_rows}
        unexpected = set(remote_by_name) - set(EXPECTED)
        if unexpected:
            raise SystemExit(
                f"unexpected files in existing Zenodo draft: {sorted(unexpected)}"
            )
        for name in sorted(EXPECTED):
            path = source / name
            row = remote_by_name.get(name)
            inv = inventory[name]
            correct = False
            if row:
                size = int(row.get("filesize") or row.get("size") or -1)
                checksum = str(row.get("checksum") or "")
                correct = size == inv["bytes"] and (
                    not checksum or normalize_md5(checksum) == inv["md5"]
                )
            if correct:
                print(f"[ZENODO] upload_skip_existing name={name}", flush=True)
            else:
                if row:
                    delete_url = row.get("links", {}).get("self")
                    if not delete_url:
                        file_id = row.get("id")
                        delete_url = (
                            f"/deposit/depositions/{dep_id}/files/{file_id}"
                        )
                    client.request("DELETE", str(delete_url))
                client.put_file(bucket, path)
            dep = client.request("GET", f"/deposit/depositions/{dep_id}")
            row = {
                get_remote_name(r): r for r in dep.get("files", [])
            }.get(name)
            if not row:
                raise SystemExit(f"Zenodo file absent after upload: {name}")
            link = (
                row.get("links", {}).get("download")
                or row.get("links", {}).get("self")
            )
            if not link:
                raise SystemExit(f"no draft readback URL for {name}")
            client.full_readback(str(link), path, "prepublish")

        dep = client.request("GET", f"/deposit/depositions/{dep_id}")
        verify_remote_rows(dep.get("files", []), inventory)
        publish_payload = client.request(
            "POST",
            f"/deposit/depositions/{dep_id}/actions/publish",
        )
        print(
            f"[ZENODO] published id={dep_id} doi={publish_payload.get('doi') or publish_payload.get('metadata',{}).get('doi') or publish_payload.get('metadata',{}).get('prereserve_doi',{}).get('doi')}",
            flush=True,
        )
        record = (
            client.request("GET", f"/records/{dep_id}", allow_404=True)
            or publish_payload
        )
        by_name = verify_remote_rows(record.get("files", []), inventory)
        for name in sorted(EXPECTED):
            link = (
                by_name[name].get("links", {}).get("download")
                or by_name[name].get("links", {}).get("self")
            )
            if not link:
                raise SystemExit(f"no published readback URL for {name}")
            client.full_readback(str(link), source / name, "postpublish")
        final = record

    doi = (
        final.get("doi")
        or final.get("metadata", {}).get("doi")
        or final.get("pids", {}).get("doi", {}).get("identifier")
        or publish_payload.get("doi")
        or publish_payload.get("metadata", {}).get("doi")
        or publish_payload.get("metadata", {})
        .get("prereserve_doi", {})
        .get("doi")
        or dep.get("doi")
        or dep.get("metadata", {}).get("doi")
        or dep.get("metadata", {}).get("prereserve_doi", {}).get("doi")
    )
    concept_doi = (
        final.get("conceptdoi")
        or final.get("metadata", {}).get("conceptdoi")
        or publish_payload.get("conceptdoi")
        or publish_payload.get("metadata", {}).get("conceptdoi")
        or dep.get("conceptdoi")
    )
    record_id = int(final.get("id") or dep_id)
    state = {
        "schema": "trinity-accord/first-star-moon-zenodo-state/v1",
        "updated_at": now(),
        "title": TITLE,
        "source_release_tag": RELEASE_TAG,
        "source_release_url": RELEASE_URL,
        "record_id": record_id,
        "deposition_id": dep_id,
        "doi": doi,
        "concept_doi": concept_doi,
        "public_record_url": f"https://zenodo.org/records/{record_id}",
        "public_record_api": f"https://zenodo.org/api/records/{record_id}",
        "verified_file_count": len(inventory),
        "verified_total_bytes": sum(x["bytes"] for x in inventory.values()),
        "remote_full_readback_sha256_verified": True,
        "source_inventory": inventory,
    }
    if not doi:
        raise SystemExit("publication completed but DOI was not resolved")
    write_json(state_path, state)
    print(
        "ZENODO_RESULT="
        + json.dumps(
            {
                "record_id": record_id,
                "doi": doi,
                "concept_doi": concept_doi,
                "files": len(inventory),
                "bytes": state["verified_total_bytes"],
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
