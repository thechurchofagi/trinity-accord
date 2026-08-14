#!/usr/bin/env python3
"""Mirror every inscription currently held by the Trinity Accord Bitcoin address.

The address inventory is discovered at run time from ord's JSON address endpoint.
No expected inscription count is hard-coded.  Inscription bodies are treated as
untrusted bytes and stored as inert base64 together with exact SHA-256/length
metadata.  Previously observed object directories are retained if an inscription
later leaves the address; current-ids.txt and manifest.json describe the stable
current snapshot.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ADDRESS = "bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf"
DEFAULT_BASE_URL = "https://ordinals.com"
ARCHIVE_DIR = ROOT / "bitcoin-inscription-mirrors" / "address-wide"
OBJECTS_DIR = ARCHIVE_DIR / "objects"
ID_RE = re.compile(r"^[0-9a-f]{64}i(?:0|[1-9][0-9]*)$")
USER_AGENT = "trinity-accord-address-inscription-mirror/1.0"
MAX_ATTEMPTS = 4


class SyncError(RuntimeError):
    pass


def request_bytes(url: str, *, accept: str | None = None) -> bytes:
    headers = {"User-Agent": USER_AGENT}
    if accept:
        headers["Accept"] = accept
    last_error: BaseException | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.read()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            last_error = exc
            if attempt == MAX_ATTEMPTS:
                break
            time.sleep(attempt * 2)
    raise SyncError(f"failed to fetch {url}: {last_error}")


def request_json(url: str) -> dict[str, Any]:
    raw = request_bytes(url, accept="application/json")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SyncError(f"non-JSON response from {url}: {exc}") from exc
    if not isinstance(value, dict):
        raise SyncError(f"expected JSON object from {url}")
    return value


def discover_ids(base_url: str) -> list[str]:
    payload = request_json(f"{base_url}/address/{ADDRESS}")
    ids = payload.get("inscriptions")
    if not isinstance(ids, list):
        raise SyncError("address endpoint did not return an inscriptions array")
    if not ids:
        raise SyncError("address endpoint returned zero inscriptions; refusing to replace a known non-empty snapshot")
    normalized: list[str] = []
    for value in ids:
        if not isinstance(value, str) or not ID_RE.fullmatch(value):
            raise SyncError(f"invalid inscription id from address endpoint: {value!r}")
        normalized.append(value)
    if len(set(normalized)) != len(normalized):
        raise SyncError("address endpoint returned duplicate inscription ids")
    return sorted(normalized)


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


def write_if_changed(path: Path, data: bytes) -> bool:
    if path.exists() and path.read_bytes() == data:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_bytes(data)
    temp.replace(path)
    return True


def mirror_one(base_url: str, inscription_id: str) -> dict[str, Any]:
    metadata = request_json(f"{base_url}/inscription/{inscription_id}")
    if metadata.get("id") != inscription_id:
        raise SyncError(f"{inscription_id}: metadata id mismatch")
    if metadata.get("address") != ADDRESS:
        raise SyncError(
            f"{inscription_id}: metadata address mismatch: {metadata.get('address')!r}"
        )

    content = request_bytes(f"{base_url}/content/{inscription_id}")
    declared_length = metadata.get("content_length")
    if declared_length is not None:
        try:
            declared_length_int = int(declared_length)
        except (TypeError, ValueError) as exc:
            raise SyncError(f"{inscription_id}: invalid content_length {declared_length!r}") from exc
        if declared_length_int != len(content):
            raise SyncError(
                f"{inscription_id}: content length mismatch "
                f"(metadata={declared_length_int}, downloaded={len(content)})"
            )

    sha256 = hashlib.sha256(content).hexdigest()
    encoded = base64.b64encode(content).decode("ascii")
    wrapped = "\n".join(encoded[i : i + 76] for i in range(0, len(encoded), 76)) + "\n"

    target = OBJECTS_DIR / inscription_id
    write_if_changed(target / "metadata.json", canonical_json_bytes(metadata))
    write_if_changed(target / "content.b64", wrapped.encode("ascii"))
    write_if_changed(
        target / "CONTENT_SHA256",
        f"{sha256}  decoded-content\n".encode("ascii"),
    )
    write_if_changed(target / "CONTENT_LENGTH", f"{len(content)}\n".encode("ascii"))

    decoded = base64.b64decode((target / "content.b64").read_bytes(), validate=False)
    if decoded != content:
        raise SyncError(f"{inscription_id}: local base64 round-trip mismatch")

    return {
        "id": inscription_id,
        "number": metadata.get("number"),
        "content_type": metadata.get("content_type"),
        "content_length": len(content),
        "content_sha256": sha256,
        "metadata_path": str((target / "metadata.json").relative_to(ROOT)),
        "content_base64_path": str((target / "content.b64").relative_to(ROOT)),
    }


def build_readme() -> bytes:
    text = f"""# Address-wide Bitcoin inscription mirror

This directory is a runtime-discovered archival mirror of every inscription
currently reported for `{ADDRESS}` by the configured ord server.

It is **not capped at eight inscriptions or any other fixed count**.

- `current-ids.txt` is the stable current address set from the most recent successful sync.
- `manifest.json` binds the current set to exact decoded-content SHA-256 values and lengths.
- `objects/<INSCRIPTION_ID>/metadata.json` preserves ord metadata.
- `objects/<INSCRIPTION_ID>/content.b64` stores the exact inscription bytes as inert base64.
- `CONTENT_SHA256` hashes the decoded original bytes.
- `CONTENT_LENGTH` records the decoded byte length.

The `objects/` directory is cumulative: once an inscription has been observed,
its archived object is retained even if it later leaves the address.

## Authority boundary

This is a discovery/preservation mirror only. The three Bitcoin Originals
remain the only canonical body. Other same-address inscriptions do not amend,
replace, supersede, or interpret the Originals merely by appearing here.
"""
    return text.encode("utf-8")


def verify_archive(current_ids: list[str]) -> None:
    for inscription_id in current_ids:
        target = OBJECTS_DIR / inscription_id
        for name in ("metadata.json", "content.b64", "CONTENT_SHA256", "CONTENT_LENGTH"):
            if not (target / name).is_file():
                raise SyncError(f"{inscription_id}: missing archived file {name}")
        decoded = base64.b64decode((target / "content.b64").read_bytes(), validate=False)
        expected_hash = (target / "CONTENT_SHA256").read_text("ascii").split()[0]
        expected_length = int((target / "CONTENT_LENGTH").read_text("ascii").strip())
        if hashlib.sha256(decoded).hexdigest() != expected_hash:
            raise SyncError(f"{inscription_id}: archived SHA-256 mismatch")
        if len(decoded) != expected_length:
            raise SyncError(f"{inscription_id}: archived length mismatch")


def sync(base_url: str) -> int:
    base_url = base_url.rstrip("/")
    start_ids = discover_ids(base_url)
    print(f"Discovered {len(start_ids)} inscription(s) for {ADDRESS}.")

    OBJECTS_DIR.mkdir(parents=True, exist_ok=True)
    items = []
    for index, inscription_id in enumerate(start_ids, 1):
        print(f"[{index}/{len(start_ids)}] Mirroring {inscription_id}")
        items.append(mirror_one(base_url, inscription_id))

    # Fail closed if address membership changed during collection.
    end_ids = discover_ids(base_url)
    if start_ids != end_ids:
        added = sorted(set(end_ids) - set(start_ids))
        removed = sorted(set(start_ids) - set(end_ids))
        raise SyncError(
            "address inscription set changed during sync; refusing mixed snapshot "
            f"(added={added}, removed={removed})"
        )

    verify_archive(start_ids)

    manifest = {
        "schema": "trinityaccord.bitcoin-authority-address-mirror.v1",
        "address": ADDRESS,
        "authority_boundary": {
            "archive_is_non_canonical": True,
            "bitcoin_originals_prevail": True,
            "same_address_does_not_imply_amendment": True,
        },
        "discovery": {
            "base_url": base_url,
            "endpoint": f"/address/{ADDRESS}",
            "fixed_expected_count": None,
        },
        "count": len(start_ids),
        "ids": start_ids,
        "items": sorted(items, key=lambda item: item["id"]),
    }

    write_if_changed(
        ARCHIVE_DIR / "current-ids.txt",
        ("".join(f"{value}\n" for value in start_ids)).encode("ascii"),
    )
    write_if_changed(ARCHIVE_DIR / "manifest.json", canonical_json_bytes(manifest))
    write_if_changed(ARCHIVE_DIR / "README.md", build_readme())
    print(f"PASS: stable complete current snapshot contains {len(start_ids)} inscription(s).")
    return 0


def check() -> int:
    manifest_path = ARCHIVE_DIR / "manifest.json"
    ids_path = ARCHIVE_DIR / "current-ids.txt"
    if not manifest_path.is_file() or not ids_path.is_file():
        raise SyncError("address-wide mirror has not been generated yet")
    manifest = json.loads(manifest_path.read_text("utf-8"))
    ids = [line.strip() for line in ids_path.read_text("ascii").splitlines() if line.strip()]
    if manifest.get("address") != ADDRESS:
        raise SyncError("manifest address mismatch")
    if manifest.get("ids") != ids or manifest.get("count") != len(ids):
        raise SyncError("manifest/current-ids mismatch")
    verify_archive(ids)
    print(f"PASS: verified {len(ids)} archived current inscription object(s).")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--sync", action="store_true", help="discover and mirror the stable current address set")
    mode.add_argument("--check", action="store_true", help="verify the checked-in address-wide mirror offline")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args()
    try:
        if args.check:
            return check()
        return sync(args.base_url)
    except SyncError as exc:
        print(f"FAIL: {exc}", flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
