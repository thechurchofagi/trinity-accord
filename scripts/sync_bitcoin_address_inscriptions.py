#!/usr/bin/env python3
"""Mirror every inscription currently held by the Trinity Bitcoin address.

This is an archival mirror only. It never changes the authority boundary: the
three Bitcoin Originals remain the canonical body.

Each inscription is archived as two independent Ordinals payload classes when
present:
1. content bytes returned by /content/<INSCRIPTION_ID>;
2. CBOR metadata bytes returned by /r/metadata/<INSCRIPTION_ID>.

The recursive inscription-information JSON from /r/inscription/<ID> is also
preserved, but it is descriptive index data rather than the inscription's CBOR
metadata field.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import re
import struct
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

AUTHORITY_ADDRESS = "bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf"
DEFAULT_BASE_URL = "https://ordinals.com"
DEFAULT_OUTPUT = Path("bitcoin-inscription-mirrors/address-wide")
ID_RE = re.compile(r"^[0-9a-f]{64}i(?:0|[1-9][0-9]*)$")
HEX_RE = re.compile(r"^(?:[0-9a-fA-F]{2})*$")
USER_AGENT = "trinity-accord-address-inscription-sync/1.2"


class _Break:
    pass


BREAK = _Break()


class CborReader:
    """Small deterministic CBOR decoder for human-readable archive derivatives.

    The raw CBOR bytes are always preserved and hashed independently. Decoding
    is only a convenience derivative and is not the authority source.
    """

    def __init__(self, data: bytes):
        self.data = data
        self.offset = 0

    def read(self, size: int) -> bytes:
        if size < 0 or self.offset + size > len(self.data):
            raise ValueError("truncated CBOR")
        out = self.data[self.offset : self.offset + size]
        self.offset += size
        return out

    def argument(self, additional: int) -> int | None:
        if additional < 24:
            return additional
        if additional == 24:
            return int.from_bytes(self.read(1), "big")
        if additional == 25:
            return int.from_bytes(self.read(2), "big")
        if additional == 26:
            return int.from_bytes(self.read(4), "big")
        if additional == 27:
            return int.from_bytes(self.read(8), "big")
        if additional == 31:
            return None
        raise ValueError("reserved CBOR additional-information value")

    def item(self) -> Any:
        initial = self.read(1)[0]
        major = initial >> 5
        additional = initial & 0x1F

        if major == 7 and additional == 31:
            return BREAK

        arg = self.argument(additional)

        if major == 0:
            if arg is None:
                raise ValueError("indefinite unsigned integer")
            return arg
        if major == 1:
            if arg is None:
                raise ValueError("indefinite negative integer")
            return -1 - arg
        if major in (2, 3):
            if arg is None:
                chunks: list[bytes] = []
                while True:
                    part_initial = self.read(1)[0]
                    if part_initial == 0xFF:
                        break
                    part_major = part_initial >> 5
                    part_additional = part_initial & 0x1F
                    if part_major != major:
                        raise ValueError("mixed CBOR indefinite string chunks")
                    part_len = self.argument(part_additional)
                    if part_len is None:
                        raise ValueError("nested indefinite CBOR string chunk")
                    chunks.append(self.read(part_len))
                raw = b"".join(chunks)
            else:
                raw = self.read(arg)
            if major == 2:
                return raw
            return raw.decode("utf-8")
        if major == 4:
            items: list[Any] = []
            if arg is None:
                while True:
                    value = self.item()
                    if value is BREAK:
                        break
                    items.append(value)
            else:
                for _ in range(arg):
                    value = self.item()
                    if value is BREAK:
                        raise ValueError("unexpected CBOR break in definite array")
                    items.append(value)
            return items
        if major == 5:
            pairs: list[tuple[Any, Any]] = []
            if arg is None:
                while True:
                    key = self.item()
                    if key is BREAK:
                        break
                    value = self.item()
                    if value is BREAK:
                        raise ValueError("unexpected CBOR break as map value")
                    pairs.append((key, value))
            else:
                for _ in range(arg):
                    key = self.item()
                    value = self.item()
                    if key is BREAK or value is BREAK:
                        raise ValueError("unexpected CBOR break in definite map")
                    pairs.append((key, value))
            if all(isinstance(key, (str, int)) for key, _ in pairs):
                result: dict[Any, Any] = {}
                for key, value in pairs:
                    if key in result:
                        raise ValueError("duplicate CBOR map key")
                    result[key] = value
                return result
            return {"$cbor_map": [[key, value] for key, value in pairs]}
        if major == 6:
            if arg is None:
                raise ValueError("indefinite CBOR tag")
            value = self.item()
            if value is BREAK:
                raise ValueError("unexpected CBOR break after tag")
            return {"$cbor_tag": arg, "value": value}
        if major == 7:
            if additional < 20:
                return {"$cbor_simple": additional}
            if additional == 20:
                return False
            if additional == 21:
                return True
            if additional == 22:
                return None
            if additional == 23:
                return {"$cbor_undefined": True}
            if additional == 24:
                assert arg is not None
                return {"$cbor_simple": arg}
            if additional == 25:
                return struct.unpack(">e", self.read(2))[0]
            if additional == 26:
                return struct.unpack(">f", self.read(4))[0]
            if additional == 27:
                return struct.unpack(">d", self.read(8))[0]
            raise ValueError("unsupported CBOR simple value")
        raise ValueError("unsupported CBOR major type")


def json_compatible(value: Any) -> Any:
    if isinstance(value, bytes):
        return {"$bytes_hex": value.hex()}
    if isinstance(value, float) and not math.isfinite(value):
        return {"$float": repr(value)}
    if isinstance(value, list):
        return [json_compatible(item) for item in value]
    if isinstance(value, dict):
        if "$cbor_map" in value and len(value) == 1:
            return {
                "$cbor_map": [
                    [json_compatible(key), json_compatible(item)]
                    for key, item in value["$cbor_map"]
                ]
            }
        return {str(key): json_compatible(item) for key, item in value.items()}
    return value


def decode_cbor(data: bytes) -> Any:
    reader = CborReader(data)
    value = reader.item()
    if value is BREAK:
        raise ValueError("top-level CBOR break")
    if reader.offset != len(data):
        raise ValueError("trailing bytes after top-level CBOR value")
    return json_compatible(value)


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


def fetch_json(url: str, *, negotiate: bool = True) -> dict:
    raw = fetch_bytes(url, accept="application/json" if negotiate else None)
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object from {url}")
    return value


def fetch_inscription_metadata_cbor(base_url: str, inscription_id: str) -> bytes:
    """Fetch exact inscription CBOR metadata bytes from ord's recursive endpoint."""
    url = f"{base_url.rstrip('/')}/r/metadata/{inscription_id}"
    raw = fetch_bytes(url)
    value = json.loads(raw)
    if value is None or value == "":
        return b""
    if not isinstance(value, str) or not HEX_RE.fullmatch(value):
        raise RuntimeError(f"invalid hex-encoded CBOR metadata from {url}")
    return bytes.fromhex(value)


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

    # /r/inscription is descriptive recursive index data.
    info = fetch_json(
        f"{base_url.rstrip('/')}/r/inscription/{inscription_id}", negotiate=False
    )
    if info.get("id") != inscription_id:
        raise RuntimeError(f"inscription info id mismatch for {inscription_id}")
    if info.get("address") != address:
        raise RuntimeError(f"inscription info address mismatch for {inscription_id}")

    # The inscription body and CBOR metadata are distinct on-chain payloads.
    content = fetch_bytes(f"{base_url.rstrip('/')}/content/{inscription_id}")
    metadata_cbor = fetch_inscription_metadata_cbor(base_url, inscription_id)

    declared = info.get("content_length")
    if declared is not None and int(declared) != len(content):
        raise RuntimeError(
            f"content length mismatch for {inscription_id}: declared={declared} actual={len(content)}"
        )

    content_sha256 = hashlib.sha256(content).hexdigest()
    metadata_sha256 = hashlib.sha256(metadata_cbor).hexdigest()

    (obj_dir / "metadata.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (obj_dir / "content.b64").write_text(
        base64.b64encode(content).decode("ascii") + "\n", encoding="ascii"
    )
    (obj_dir / "CONTENT_SHA256").write_text(
        f"{content_sha256}  decoded-content\n", encoding="ascii"
    )
    (obj_dir / "CONTENT_LENGTH").write_text(f"{len(content)}\n", encoding="ascii")

    # Preserve exact CBOR metadata bytes even when the content is a binary image.
    (obj_dir / "inscription-metadata.cbor.b64").write_text(
        base64.b64encode(metadata_cbor).decode("ascii") + "\n", encoding="ascii"
    )
    (obj_dir / "inscription-metadata.cbor.hex").write_text(
        metadata_cbor.hex() + "\n", encoding="ascii"
    )
    (obj_dir / "INSCRIPTION_METADATA_SHA256").write_text(
        f"{metadata_sha256}  decoded-inscription-metadata-cbor\n", encoding="ascii"
    )
    (obj_dir / "INSCRIPTION_METADATA_LENGTH").write_text(
        f"{len(metadata_cbor)}\n", encoding="ascii"
    )
    decoded_metadata = {
        "present": bool(metadata_cbor),
        "source": "ord inscription field tag 5 (CBOR metadata)",
        "derived_not_authority": True,
        "decoded": decode_cbor(metadata_cbor) if metadata_cbor else None,
    }
    (obj_dir / "inscription-metadata.decoded.json").write_text(
        json.dumps(
            decoded_metadata,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )

    encoded = (obj_dir / "content.b64").read_text(encoding="ascii").strip()
    decoded = base64.b64decode(encoded, validate=True)
    if decoded != content or hashlib.sha256(decoded).hexdigest() != content_sha256:
        raise RuntimeError(f"local content round-trip verification failed for {inscription_id}")

    metadata_encoded = (
        obj_dir / "inscription-metadata.cbor.b64"
    ).read_text(encoding="ascii").strip()
    metadata_decoded = base64.b64decode(metadata_encoded, validate=True)
    if (
        metadata_decoded != metadata_cbor
        or hashlib.sha256(metadata_decoded).hexdigest() != metadata_sha256
    ):
        raise RuntimeError(
            f"local inscription metadata round-trip verification failed for {inscription_id}"
        )

    return {
        "id": inscription_id,
        "content_length": len(content),
        "content_sha256": content_sha256,
        "content_type": info.get("content_type"),
        "inscription_metadata_present": bool(metadata_cbor),
        "inscription_metadata_length": len(metadata_cbor),
        "inscription_metadata_sha256": metadata_sha256,
    }


def build_manifest(address: str, current_ids: list[str], objects: list[dict]) -> dict:
    return {
        "schema": "trinityaccord.bitcoin-address-inscription-mirror.v2",
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
            "content_encoding": "base64 of exact inscription body bytes",
            "content_hash": "sha256 of decoded exact inscription body bytes",
            "inscription_metadata_encoding": "base64 and hex of exact tag-5 CBOR metadata bytes",
            "inscription_metadata_hash": "sha256 of decoded exact CBOR metadata bytes",
            "decoded_metadata_is_derivative": True,
        },
        "authority_boundary": {
            "archive_only": True,
            "same_address_does_not_imply_canonical": True,
            "three_bitcoin_originals_remain_canonical": True,
        },
    }


def sync(base_url: str, address: str, output: Path) -> dict:
    start_ids = discover_ids(base_url, address)
    print(f"discovered {len(start_ids)} inscriptions for {address}", flush=True)
    output.mkdir(parents=True, exist_ok=True)

    objects: list[dict] = []
    for index, item in enumerate(start_ids, start=1):
        print(f"[{index}/{len(start_ids)}] mirroring {item}", flush=True)
        objects.append(write_object(base_url, address, item, output))

    # Fail closed if ownership changed during collection; never publish a mixed snapshot.
    end_ids = discover_ids(base_url, address)
    if start_ids != end_ids:
        raise RuntimeError("address inscription set changed during synchronization")

    manifest = build_manifest(address, start_ids, objects)
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output / "current-ids.txt").write_text(
        "".join(f"{item}\n" for item in start_ids), encoding="ascii"
    )
    (output / "README.md").write_text(
        "# Address-wide Bitcoin inscription mirror\n\n"
        f"Authority address: `{address}`.\n\n"
        "The current set is discovered at runtime; no inscription count is hard-coded. "
        "Objects are cumulative, so previously observed inscriptions remain preserved if they later leave the address.\n\n"
        "For every inscription, the archive preserves the inscription body returned by `/content/<ID>` and the "
        "independent tag-5 CBOR metadata returned by `/r/metadata/<ID>`. A human-readable decoded metadata JSON is "
        "stored only as a derivative; the exact CBOR bytes and SHA-256 remain the source preserved for verification.\n\n"
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
