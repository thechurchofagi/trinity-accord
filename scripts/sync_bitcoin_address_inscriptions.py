#!/usr/bin/env python3
"""Mirror every inscription currently held by the Trinity Bitcoin address.

This archive preserves, independently:
1. exact inscription content bytes from /content/<INSCRIPTION_ID>;
2. exact tag-5 CBOR metadata bytes from /r/metadata/<INSCRIPTION_ID>, when present.

The /r/inscription/<ID> JSON is descriptive index data. It is preserved too, but
it is not the same object as the inscription's CBOR metadata field.

This is archival only. The three Bitcoin Originals remain the canonical body.
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
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

AUTHORITY_ADDRESS = "bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf"
DEFAULT_BASE_URL = "https://ordinals.com"
DEFAULT_OUTPUT = Path("bitcoin-inscription-mirrors/address-wide")
ID_RE = re.compile(r"^[0-9a-f]{64}i(?:0|[1-9][0-9]*)$")
HEX_RE = re.compile(r"^(?:[0-9a-fA-F]{2})*$")
USER_AGENT = "trinity-accord-address-inscription-sync/1.4"


class FetchError(RuntimeError):
    """A fetch failure that preserves the HTTP status for narrow fallbacks."""

    def __init__(self, url: str, cause: Exception | None, status: int | None = None):
        super().__init__(f"failed to fetch {url}: {cause}")
        self.url = url
        self.status = status


class AddressInscriptionHTMLParser(HTMLParser):
    """Extract inscription links only from ord's address thumbnail container."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.invalid_ids: list[str] = []
        self.thumbnail_sections = 0
        self.in_thumbnails = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "dd" and "thumbnails" in (attributes.get("class") or "").split():
            self.thumbnail_sections += 1
            self.in_thumbnails = True
            return
        if tag != "a" or not self.in_thumbnails:
            return
        href = attributes.get("href") or ""
        prefix = "/inscription/"
        if not href.startswith(prefix):
            return
        inscription_id = href[len(prefix) :]
        if ID_RE.fullmatch(inscription_id):
            self.ids.append(inscription_id)
        else:
            self.invalid_ids.append(inscription_id)

    def handle_endtag(self, tag: str) -> None:
        if tag == "dd" and self.in_thumbnails:
            self.in_thumbnails = False


class _Break:
    pass


BREAK = _Break()


class CborReader:
    """Minimal deterministic CBOR decoder for non-authoritative readable derivatives."""

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

        # Major type 7 uses the additional-information bytes as the value itself,
        # so handle it before the generic length/integer argument decoder.
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
                return {"$cbor_simple": self.read(1)[0]}
            if additional == 25:
                return struct.unpack(">e", self.read(2))[0]
            if additional == 26:
                return struct.unpack(">f", self.read(4))[0]
            if additional == 27:
                return struct.unpack(">d", self.read(8))[0]
            if additional == 31:
                return BREAK
            raise ValueError("reserved CBOR simple/float value")

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
            return raw if major == 2 else raw.decode("utf-8")
        if major == 4:
            values: list[Any] = []
            if arg is None:
                while True:
                    value = self.item()
                    if value is BREAK:
                        break
                    values.append(value)
            else:
                for _ in range(arg):
                    value = self.item()
                    if value is BREAK:
                        raise ValueError("unexpected CBOR break in definite array")
                    values.append(value)
            return values
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


def fetch_bytes(
    url: str,
    *,
    accept: str | None = None,
    attempts: int = 4,
    absent_statuses: frozenset[int] = frozenset(),
) -> bytes | None:
    """Fetch bytes with fail-closed retry semantics.

    Explicitly allowed absent HTTP statuses (currently used only for optional
    inscription metadata) return None immediately. Other 4xx responses fail
    immediately; transient transport errors and 5xx responses are retried.
    """
    headers = {"User-Agent": USER_AGENT}
    if accept:
        headers["Accept"] = accept

    last: Exception | None = None
    last_status: int | None = None
    for attempt in range(1, attempts + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=45) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            if exc.code in absent_statuses:
                return None
            last = exc
            last_status = exc.code
            if 400 <= exc.code < 500:
                break
        except (urllib.error.URLError, TimeoutError) as exc:
            last = exc
            last_status = None

        if attempt == attempts:
            break
        time.sleep(attempt * 2)

    raise FetchError(url, last, last_status)


def fetch_json(url: str, *, negotiate: bool = True) -> dict:
    raw = fetch_bytes(url, accept="application/json" if negotiate else None)
    if raw is None:
        raise RuntimeError(f"unexpected absent response from {url}")
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object from {url}")
    return value


def fetch_inscription_metadata_cbor(base_url: str, inscription_id: str) -> bytes:
    """Fetch exact tag-5 CBOR bytes; 404 means this inscription has no metadata."""
    url = f"{base_url.rstrip('/')}/r/metadata/{inscription_id}"
    raw = fetch_bytes(url, absent_statuses=frozenset({404}))
    if raw is None:
        return b""

    value = json.loads(raw)
    if value is None or value == "":
        return b""
    if not isinstance(value, str) or not HEX_RE.fullmatch(value):
        raise RuntimeError(f"invalid hex-encoded CBOR metadata from {url}")
    return bytes.fromhex(value)


def validate_discovered_ids(ids: Any, source: str) -> list[str]:
    if not isinstance(ids, list):
        raise RuntimeError(f"{source} has no inscriptions array")
    if any(not isinstance(item, str) or not ID_RE.fullmatch(item) for item in ids):
        raise RuntimeError(f"{source} contains an invalid inscription id")
    if len(ids) != len(set(ids)):
        raise RuntimeError(f"{source} contains duplicate inscription ids")
    return sorted(ids)


def discover_ids_from_html(raw: bytes, url: str) -> list[str]:
    try:
        html = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RuntimeError(f"ord address HTML is not UTF-8: {url}") from exc
    parser = AddressInscriptionHTMLParser()
    parser.feed(html)
    parser.close()
    if parser.thumbnail_sections != 1 or parser.in_thumbnails:
        raise RuntimeError("ord address HTML has no single complete thumbnails section")
    if parser.invalid_ids:
        raise RuntimeError("ord address HTML contains an invalid inscription id")
    return validate_discovered_ids(parser.ids, "ord address HTML")


def discover_ids(base_url: str, address: str) -> list[str]:
    url = f"{base_url.rstrip('/')}/address/{address}"
    try:
        payload = fetch_json(url)
    except FetchError as exc:
        if exc.status != 406:
            raise
        # ordinals.com may expose this documented address view as HTML while
        # refusing JSON content negotiation. The HTML view contains the same
        # complete address inscription set. Object-level address checks below
        # still fail closed for every discovered ID.
        raw = fetch_bytes(url, accept="text/html")
        if raw is None:
            raise RuntimeError(f"unexpected absent response from {url}")
        print("ord address JSON returned HTTP 406; using validated HTML view", flush=True)
        return discover_ids_from_html(raw, url)
    return validate_discovered_ids(payload.get("inscriptions"), "ord address JSON")


def write_object(base_url: str, address: str, inscription_id: str, root: Path) -> dict:
    obj_dir = root / "objects" / inscription_id
    obj_dir.mkdir(parents=True, exist_ok=True)

    info = fetch_json(
        f"{base_url.rstrip('/')}/r/inscription/{inscription_id}", negotiate=False
    )
    if info.get("id") != inscription_id:
        raise RuntimeError(f"inscription info id mismatch for {inscription_id}")
    if info.get("address") != address:
        raise RuntimeError(f"inscription info address mismatch for {inscription_id}")

    content = fetch_bytes(f"{base_url.rstrip('/')}/content/{inscription_id}")
    if content is None:
        raise RuntimeError(f"unexpected absent content for {inscription_id}")
    metadata_cbor = fetch_inscription_metadata_cbor(base_url, inscription_id)

    declared = info.get("content_length")
    if declared is not None and int(declared) != len(content):
        raise RuntimeError(
            f"content length mismatch for {inscription_id}: "
            f"declared={declared} actual={len(content)}"
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

    decoded_content = base64.b64decode(
        (obj_dir / "content.b64").read_text(encoding="ascii").strip(), validate=True
    )
    if (
        decoded_content != content
        or hashlib.sha256(decoded_content).hexdigest() != content_sha256
    ):
        raise RuntimeError(f"local content round-trip verification failed for {inscription_id}")

    decoded_metadata_cbor = base64.b64decode(
        (obj_dir / "inscription-metadata.cbor.b64")
        .read_text(encoding="ascii")
        .strip(),
        validate=True,
    )
    if (
        decoded_metadata_cbor != metadata_cbor
        or hashlib.sha256(decoded_metadata_cbor).hexdigest() != metadata_sha256
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
            "semantics": (
                "stable complete current set returned by the ord address endpoint; "
                "validated HTML is used only when JSON negotiation returns HTTP 406"
            ),
        },
        "archive": {
            "objects_are_cumulative": True,
            "content_encoding": "base64 of exact inscription body bytes",
            "content_hash": "sha256 of decoded exact inscription body bytes",
            "inscription_metadata_encoding": (
                "base64 and hex of exact tag-5 CBOR metadata bytes"
            ),
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
    for index, inscription_id in enumerate(start_ids, start=1):
        print(f"[{index}/{len(start_ids)}] mirroring {inscription_id}", flush=True)
        objects.append(write_object(base_url, address, inscription_id, output))

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
        "The documented JSON address representation is preferred; when the server "
        "returns HTTP 406 for JSON negotiation, the same address page's inscription "
        "thumbnail links are parsed and strictly validated instead. "
        "Objects are cumulative, so previously observed inscriptions remain preserved "
        "if they later leave the address.\n\n"
        "For every inscription, the archive preserves the inscription body returned by "
        "`/content/<ID>` and the independent tag-5 CBOR metadata returned by "
        "`/r/metadata/<ID>` when present. HTTP 404 from that optional metadata endpoint "
        "is recorded as absence, not as a synchronization failure. A human-readable "
        "decoded metadata JSON is only a derivative; the exact CBOR bytes and SHA-256 "
        "remain the preserved verification source.\n\n"
        "This is an archival/discovery mirror only. The three Bitcoin Originals remain "
        "the canonical body.\n",
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
