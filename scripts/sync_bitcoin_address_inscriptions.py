#!/usr/bin/env python3
"""Mirror every inscription currently held by the Trinity Bitcoin address.

This is an archival mirror only. It never changes the authority boundary: the
three Bitcoin Originals remain the canonical body.
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

AUTHORITY_ADDRESS = "bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf"
DEFAULT_BASE_URL = "https://ordinals.com"
DEFAULT_OUTPUT = Path("bitcoin-inscription-mirrors/address-wide")
ID_RE = re.compile(r"^[0-9a-f]{64}i(?:0|[1-9][0-9]*)$")
USER_AGENT = "trinity-accord-address-inscription-sync/1.0"


def fetch_bytes(url: str, *, accept: str | None = None, attempts: int = 4) -> bytes:
    headers = {"User-Agent": USER_AGENT}
    if accept:
        headers["Accept"] = accept
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=45) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            last = exc
            if attempt == attempts:
                break
            time.sleep(attempt * 2)
    raise RuntimeError(f"failed to fetch {url}: {last}")


def fetch_json(url: str) -> dict:
    value = json.loads(fetch_bytes(url, accept="application/json"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object from {url}")
    return value


def discover_ids(base_url: str, address: str) -> list[str]:
    payload = fetch_json(f"{base_url.rstrip('/')}/address/{address}")
    ids = payload.get("inscriptions")
    if not isinstance(ids, list):
        raise RuntimeError("ord address response has no inscriptions array")
    if any(not isinstance(item, str) or not ID_RE.fullmatch(item) for item in ids):
        raise RuntimeError("ord address response contains an invalid inscription id")
    if len(ids) != len(set(ids)):
        raise RuntimeError("ord address response contains duplicate inscription ids")
    return sorted(ids)


def write_object(base_url: str, address: str, inscription_id: str, root: Path) -> dict:
    obj_dir = root / "objects" / inscription_id
    obj_dir.mkdir(parents=True, exist_ok=True)

    metadata = fetch_json(f"{base_url.rstrip('/')}/inscription/{inscription_id}")
    if metadata.get("id") != inscription_id:
        raise RuntimeError(f"metadata id mismatch for {inscription_id}")
    if metadata.get("address") != address:
        raise RuntimeError(f"metadata address mismatch for {inscription_id}")

    content = fetch_bytes(f"{base_url.rstrip('/')}/content/{inscription_id}")
    declared = metadata.get("content_length")
    if declared is not None and int(declared) != len(content):
        raise RuntimeError(
            f"content length mismatch for {inscription_id}: declared={declared} actual={len(content)}"
        )

    sha256 = hashlib.sha256(content).hexdigest()
    (obj_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (obj_dir / "content.b64").write_text(
        base64.b64encode(content).decode("ascii") + "\n", encoding="ascii"
    )
    (obj_dir / "CONTENT_SHA256").write_text(f"{sha256}  decoded-content\n", encoding="ascii")
    (obj_dir / "CONTENT_LENGTH").write_text(f"{len(content)}\n", encoding="ascii")

    # Immediate local round-trip verification.
    encoded = (obj_dir / "content.b64").read_text(encoding="ascii").strip()
    decoded = base64.b64decode(encoded, validate=True)
    if decoded != content or hashlib.sha256(decoded).hexdigest() != sha256:
        raise RuntimeError(f"local round-trip verification failed for {inscription_id}")

    return {
        "id": inscription_id,
        "content_length": len(content),
        "content_sha256": sha256,
        "content_type": metadata.get("content_type"),
    }


def build_manifest(address: str, current_ids: list[str], objects: list[dict]) -> dict:
    return {
        "schema": "trinityaccord.bitcoin-address-inscription-mirror.v1",
        "address": address,
        "count": len(current_ids),
        "ids": current_ids,
        "objects": objects,
        "discovery": {
            "fixed_count": False,
            "semantics": "stable complete current set returned by the ord address endpoint",
        },
        "archive": {
            "objects_are_cumulative": True,
            "content_encoding": "base64 of exact inscription bytes",
            "content_hash": "sha256 of decoded exact inscription bytes",
        },
        "authority_boundary": {
            "archive_only": True,
            "same_address_does_not_imply_canonical": True,
            "three_bitcoin_originals_remain_canonical": True,
        },
    }


def sync(base_url: str, address: str, output: Path) -> dict:
    start_ids = discover_ids(base_url, address)
    output.mkdir(parents=True, exist_ok=True)

    objects = [write_object(base_url, address, item, output) for item in start_ids]

    # Fail closed if ownership changed during collection; never publish a mixed snapshot.
    end_ids = discover_ids(base_url, address)
    if start_ids != end_ids:
        raise RuntimeError("address inscription set changed during synchronization")

    manifest = build_manifest(address, start_ids, objects)
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output / "current-ids.txt").write_text("".join(f"{item}\n" for item in start_ids), encoding="ascii")
    (output / "README.md").write_text(
        "# Address-wide Bitcoin inscription mirror\n\n"
        f"Authority address: `{address}`.\n\n"
        "The current set is discovered at runtime; no inscription count is hard-coded. "
        "Objects are cumulative, so previously observed inscriptions remain preserved if they later leave the address.\n\n"
        "This is an archival/discovery mirror only. The three Bitcoin Originals remain the canonical body.\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--address", default=AUTHORITY_ADDRESS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = sync(args.base_url, args.address, args.output)
    print(f"synced {manifest['count']} inscriptions for {manifest['address']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
